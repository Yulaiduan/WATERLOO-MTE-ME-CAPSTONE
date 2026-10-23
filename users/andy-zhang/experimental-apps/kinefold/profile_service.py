"""Persist Kinefold profiles and exports inside the app, using standard Python.

Imported by preview.py: ProfileService(app_root).handle(JSON object) returns a
JSON response and HTTP status. Inputs are project-v3 mm/deg/kg/N/SI snapshots
and UTF-8 JSON/CSV artifacts. Outputs are atomic profiles/library.json updates
and unique exports/ files. HTTP origin/header/body guards belong to the caller;
this module validates bounded content, shapes and optimistic storage revisions.
This local experimental store provides no cloud sync or mechanical validation.
"""
from __future__ import annotations

import copy
from datetime import datetime
import json
import math
import os
from pathlib import Path
import re
import tempfile
import threading
import uuid

MAX_BYTES = 32 * 1024 * 1024
MAX_PROJECT_BYTES = 200_000
_LOCK = threading.RLock()


class StorageError(ValueError):
    """A readable validation or conflict failure."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def _encoded(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")


def _json_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise StorageError("Nonfinite JSON number.")
    return number


def _shape(value, allowed, label):
    if not isinstance(value, dict) or set(value) - set(allowed):
        raise StorageError(f"Invalid {label} fields.")


def _finite(value, depth=0):
    if depth > 12:
        raise StorageError("JSON nesting exceeds the storage limit.")
    if isinstance(value, dict):
        if len(value) > 200 or any(not isinstance(k, str) or k in ("__proto__", "prototype", "constructor") for k in value):
            raise StorageError("Unsafe or excessive JSON fields.")
        for child in value.values():
            _finite(child, depth + 1)
    elif isinstance(value, list):
        if len(value) > 200:
            raise StorageError("Too many profile records.")
        for child in value:
            _finite(child, depth + 1)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value) or abs(value) > 1e12:
            raise StorageError("Profile numbers must be finite and bounded.")
    elif isinstance(value, str):
        if len(value) > 2000:
            raise StorageError("Profile string exceeds the storage limit.")
    elif value is not None and not isinstance(value, bool):
        raise StorageError("Unsupported JSON value.")


def _project(value):
    _shape(value, ("schema", "id", "name", "params", "view", "solverConfig", "createdAt", "updatedAt", "legacySolverConfig", "contactConfig", "caseConfig"), "project")
    if value.get("schema") != "kinefold/project-v3":
        raise StorageError("Only validated project-v3 profiles can be saved.")
    if not isinstance(value.get("id"), str) or not re.fullmatch(r"design-[a-zA-Z0-9-]{1,100}", value["id"]):
        raise StorageError("Invalid design identifier.")
    name = value.get("name")
    if not isinstance(name, str) or not name.strip() or len(name) > 80 or any(ord(c) < 32 for c in name):
        raise StorageError("Design name must contain 1–80 readable characters.")
    for key in ("params", "view", "solverConfig"):
        if not isinstance(value.get(key), dict) or not value[key]:
            raise StorageError(f"Missing {key} object.")
    params, config = value["params"], value["solverConfig"]
    numeric_params = "L2 L3 ra rb rc rd re rf rw alpha phi0 te tc m1 m2 m3 m5 m6 g beta Fn Ft Fz Tab0 Tcd0 Tef0 springK hornR Sv rs p0 nu Su Fx theta2".split()
    if set(params) != set(numeric_params + ["loadMode", "springEnabled", "springLaw"]):
        raise StorageError("Unknown or missing design parameters.")
    for key in numeric_params:
        if type(params.get(key)) not in (int, float):
            raise StorageError(f"Missing numeric parameter {key}.")
    if params["loadMode"] not in ("weight", "global", "contact") or params["springLaw"] not in ("v4", "constant") or type(params["springEnabled"]) is not bool:
        raise StorageError("Unknown load or spring convention.")
    if params["L2"] <= 0 or params["L3"] <= 0 or params["g"] < 0 or any(params[k] < 0 for k in ("m1", "m2", "m3", "m5", "m6")) or not params["te"] <= params["theta2"] <= params["tc"]:
        raise StorageError("Invalid geometry, mass or pose bounds.")
    view = value["view"]
    view_flags = "labels dimensions belts path loads axes grid indices beltMarkers".split()
    if set(view) != set(view_flags + ["projection"]) or view["projection"] not in ("side", "iso") or any(type(view[key]) is not bool for key in view_flags):
        raise StorageError("Invalid view settings.")
    _config(config)
    if "legacySolverConfig" in value:
        _config(value["legacySolverConfig"], legacy=True)
    for key in ("createdAt", "updatedAt"):
        if not isinstance(value.get(key), str) or not re.match(r"^\d{4}-\d\d-\d\dT", value[key]):
            raise StorageError(f"Invalid {key}.")
        try:
            datetime.fromisoformat(value[key].replace("Z", "+00:00"))
        except ValueError as error:
            raise StorageError(f"Invalid {key}.") from error
    if "contactConfig" in value:
        contact = value["contactConfig"]
        _shape(contact, ("mode", "friction", "restitution", "drive"), "contact configuration")
        if set(contact) != {"mode", "friction", "restitution", "drive"} or contact.get("mode") not in ("prescribed-height", "terrain-contact") or contact.get("drive") != "free" or type(contact.get("friction")) not in (int, float) or not 0 <= contact["friction"] <= 2 or type(contact.get("restitution")) not in (int, float) or contact["restitution"] != 0:
            raise StorageError("Contact mode requires friction 0–2, zero bounce and a free backdrivable drive.")
    if "caseConfig" in value:
        _case_config(value["caseConfig"])
    _finite(value)
    if len(_encoded(value)) > MAX_PROJECT_BYTES:
        raise StorageError("Design exceeds 200 kB.")
    return copy.deepcopy(value)


def _case_config(value):
    """Validate optional saved studies without importing a physics runtime."""
    limits = {"jumpTorqueNm": (0, 10000), "landingDropMm": (0, 5000),
              "landingOpenFraction": (.01, .99), "landingBrakeTorqueNm": (0, 10000),
              "landingBrakeLimitNm": (0, 10000)}
    allowed = set(limits) | {"kind", "brakeStrategy", "undersideOffsetMm", "energyMethod"}
    _shape(value, allowed, "case configuration")
    if set(value) != allowed or value.get("kind") not in ("terrain-stability", "jump", "landing") or value.get("brakeStrategy") not in ("entered", "energy-sized") or type(value.get("energyMethod")) is not bool:
        raise StorageError("Unknown or missing case settings.")
    for key, (lo, hi) in limits.items():
        if type(value[key]) not in (int, float) or not math.isfinite(value[key]) or not lo <= value[key] <= hi:
            raise StorageError("Invalid case setting " + key + ".")
    offset = value["undersideOffsetMm"]
    if offset is not None and (type(offset) not in (int, float) or not math.isfinite(offset) or not 0 <= offset <= 5000):
        raise StorageError("Underside offset must be null or 0–5000 mm.")


def _config(config, legacy=False):
    limits = {"duration": (.05, 30), "dt": (.0001, .01), "outputHz": (1, 1000), "initialVelocityDegS": (-720, 720), "hipTorqueNm": (-10000, 10000), "dampingNms": (0, 10000), "hipRotorInertiaKgM2": (0, 1000), "I2": (0, 1000), "I3": (0, 1000), "I5": (0, 1000), "I6": (0, 1000), "iterations": (10, 500)}
    if not legacy:
        limits.update(inputHeightMm=(0, 1000), inputPlateauMm=(.1, 10000), inputGapMm=(.1, 10000), inputSpeedMmS=(.1, 10000), inputRiseMm=(0, 1000), inputDelayS=(0, 30))
    if not isinstance(config, dict) or set(config) != set(limits) | {"fixture", "inertiaModel"} or config.get("fixture") != ("fixed-hip" if legacy else "floating-chassis") or config.get("inertiaModel") not in ("uniform-rods-discs", "custom"):
        raise StorageError("Unknown or missing solver settings.")
    for key, (low, high) in limits.items():
        if type(config[key]) not in (int, float) or not math.isfinite(config[key]) or not low <= config[key] <= high:
            raise StorageError(f"Invalid solver setting {key}.")
    if config["iterations"] != int(config["iterations"]) or math.ceil(config["duration"] / config["dt"]) > 100000 or config["outputHz"] > 1 / config["dt"]:
        raise StorageError("Invalid iteration count, integration length or sample rate.")
    if not legacy:
        period = (config["inputPlateauMm"] + config["inputGapMm"]) / config["inputSpeedMmS"]
        if 2 * config["inputRiseMm"] > config["inputPlateauMm"] or 4 * math.ceil(max(0, config["duration"] - config["inputDelayS"]) / period) > 10000:
            raise StorageError("Invalid transition distance or excessive input boundaries.")


class ProfileService:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.profiles = self.root / "profiles"
        self.exports = self.root / "exports"
        self.file = self.profiles / "library.json"

    def _folder(self, path):
        if path.is_symlink() or path.resolve().parent != self.root:
            raise StorageError("Storage folder must remain inside this app.")
        path.mkdir(exist_ok=True)

    def _write(self, path, payload):
        if len(payload) > MAX_BYTES:
            raise StorageError("Stored file would exceed 32 MiB.", 413)
        self._folder(path.parent)
        if path.is_symlink():
            raise StorageError("Storage files cannot be symbolic links.")
        temp = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".write-", delete=False) as stream:
                temp = Path(stream.name)
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if temp and temp.exists():
                temp.unlink()

    def _read(self):
        self._folder(self.profiles)
        if not self.file.exists():
            return {"schema": "kinefold/disk-library-v1", "revision": 0, "designs": [], "working": None, "migrated": False}
        if self.file.is_symlink() or self.file.stat().st_size > MAX_BYTES:
            raise StorageError("Profile library has an unsafe path or exceeds 32 MiB.", 422)
        try:
            state = json.loads(self.file.read_text(encoding="utf-8"))
            _shape(state, ("schema", "revision", "designs", "working", "migrated"), "disk library")
            if state.get("schema") != "kinefold/disk-library-v1" or type(state.get("revision")) is not int or state["revision"] < 0 or type(state.get("migrated")) is not bool:
                raise StorageError("Invalid disk library metadata.")
            self._designs(state.get("designs"))
            if state.get("working") is not None:
                _project(state["working"])
            return state
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise StorageError(f"Profile library could not be read; original file retained: {error}", 422) from error

    def _designs(self, designs):
        if not isinstance(designs, list) or len(designs) > 200:
            raise StorageError("Library limit is 200 designs.")
        for item in designs:
            _project(item)
        if len({item["id"] for item in designs}) != len(designs):
            raise StorageError("Duplicate design identifiers.")

    def handle(self, request):
        try:
            if not isinstance(request, dict) or len(_encoded(request)) > MAX_BYTES:
                raise StorageError("Storage request exceeds 32 MiB or is not an object.", 413)
            with _LOCK:
                return self._handle(request), 200
        except StorageError as error:
            return {"ok": False, "error": str(error)}, error.status
        except RecursionError:
            return {"ok": False, "error": "JSON nesting exceeds the storage limit."}, 400
        except (ValueError, TypeError, OverflowError) as error:
            return {"ok": False, "error": f"Invalid storage request: {error}"}, 400
        except OSError as error:
            return {"ok": False, "error": f"Storage operation failed; existing data retained: {error}"}, 500

    def _handle(self, request):
        action = request.get("action")
        if action == "export":
            _shape(request, ("action", "name", "content", "mime"), "export request")
            name, content, mime = request.get("name"), request.get("content"), request.get("mime")
            if not isinstance(name, str) or not name or len(name) > 180 or any(c in name for c in ("/", "\\", ":")) or any(ord(c) < 32 for c in name):
                raise StorageError("Export name must be a readable filename, without a path.")
            if mime not in ("application/json", "text/csv") or not isinstance(content, str):
                raise StorageError("Exports must contain UTF-8 JSON or CSV text.")
            if mime == "application/json":
                try:
                    json.loads(content, parse_float=_json_float, parse_constant=lambda x: (_ for _ in ()).throw(StorageError("Nonfinite JSON export.")))
                except ValueError as error:
                    raise StorageError(f"Invalid JSON export: {error}") from error
            suffix = ".json" if mime == "application/json" else ".csv"
            stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", Path(name).stem).strip("-")[:100] or "kinefold"
            filename = f"{stem}-{uuid.uuid4().hex}{suffix}"
            self._write(self.exports / filename, content.encode("utf-8"))
            return {"ok": True, "path": "exports/" + filename}
        state = self._read()
        if action in ("list", "read"):
            _shape(request, ("action", "id"), "read request")
            if action == "read":
                found = next((p for p in state["designs"] if p["id"] == request.get("id")), None)
                if found is None:
                    raise StorageError("Saved design was not found.", 404)
                return {"ok": True, "revision": state["revision"], "project": found}
            return {"ok": True, **state}
        allowed = {"save": ("project",), "remove": ("id",), "working": ("project",), "migrate": ("designs", "working", "browserBackup")}
        if action not in allowed:
            raise StorageError("Unknown storage action.")
        _shape(request, ("action", "expectedRevision", *allowed[action]), "storage request")
        if type(request.get("expectedRevision")) is not int or request["expectedRevision"] != state["revision"]:
            raise StorageError("Profiles changed in another tab. Reload before saving; your current edit was not written.", 409)
        if action == "migrate":
            if state["migrated"]:
                return {"ok": True, **state}
            designs = request.get("designs")
            self._designs(designs)
            working = request.get("working")
            if working is not None:
                _project(working)
            backup = request.get("browserBackup")
            known = {"kinefold-library-v3", "kinefold-library-v2", "kinefold-project-v3", "kinefold-project-v2", "kinefold-design-v1"}
            if not isinstance(backup, dict) or set(backup) - known or any(not isinstance(v, str) for v in backup.values()) or len(_encoded(backup)) > 8 * 1024 * 1024:
                raise StorageError("Invalid browser migration backup.")
            backup_file = self.profiles / "browser-backup.json"
            if backup_file.is_symlink():
                raise StorageError("Migration backup cannot be a symbolic link.")
            if not backup_file.exists():
                self._write(backup_file, _encoded({"schema": "kinefold/browser-backup-v1", "keys": backup}))
            state.update(designs=designs, working=working, migrated=True)
        elif action == "save":
            project = _project(request.get("project"))
            state["designs"] = [p for p in state["designs"] if p["id"] != project["id"]] + [project]
            self._designs(state["designs"])
        elif action == "remove":
            if not any(p["id"] == request.get("id") for p in state["designs"]):
                raise StorageError("Design is no longer in this library.", 404)
            state["designs"] = [p for p in state["designs"] if p["id"] != request["id"]]
        else:
            state["working"] = _project(request.get("project"))
        state["revision"] += 1
        self._write(self.file, _encoded(state))
        return {"ok": True, **state}
