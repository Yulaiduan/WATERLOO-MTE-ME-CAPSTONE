"""Check canonical mass/limits, finite dynamics and CPU repeatability.

Run: python simulation/experiments/verify_backend.py [--steps 200]
Inputs: assets/manifest.json and hashed MJCF assets; SI units (kg, m, rad, s).
Outputs: JSON check evidence on stdout; exit 0 on success, 1 on failure.
No files or viewers are created. CPU timing is diagnostic, not GPU validation.
"""

import argparse
import hashlib
import json
import math
import platform
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]


class ValidationError(ValueError):
    """The supplied assets or observed simulation fail the validation contract."""


def asset_path(assets, relative):
    if not isinstance(relative, str) or not relative:
        raise ValidationError("Asset paths must be nonempty strings.")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts or "\\" in relative or ":" in relative:
        raise ValidationError(f"Unsafe asset path: {relative}")
    candidate = assets / relative
    if candidate.resolve() != assets.resolve() / relative or not candidate.is_file():
        raise ValidationError(f"Missing asset or symlink: {relative}")
    return candidate


def load_manifest(root=ROOT):
    assets = root / "assets"
    manifest = json.loads((assets / "manifest.json").read_text())
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValidationError("Unsupported assets manifest schema.")
    models = manifest.get("models")
    if not isinstance(models, list) or not models:
        raise ValidationError("BLOCKED: no canonical robot in assets/manifest.json. Supply a reviewed model and physical baseline.")
    hashes = manifest.get("files")
    if not isinstance(hashes, dict) or not hashes:
        raise ValidationError("Manifest must hash all model files and dependencies in 'files'.")
    payloads = {p.relative_to(assets).as_posix() for p in assets.rglob("*")
                if p.is_file() and p.name not in {"README.md", "manifest.json", ".gitkeep"}}
    if payloads != set(hashes):
        raise ValidationError("Manifest hashes must cover exactly all asset payload files.")
    for relative, expected in hashes.items():
        path = asset_path(assets, relative)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected:
            raise ValidationError(f"Asset checksum mismatch: {relative}")
        if path.suffix.lower() in {".xml", ".urdf"}:
            for element in ET.parse(path).iter():
                for key in ("file", "meshdir", "texturedir", "assetdir"):
                    value = element.get(key)
                    if value and (PurePosixPath(value).is_absolute() or ".." in PurePosixPath(value).parts
                                  or "\\" in value or ":" in value):
                        raise ValidationError(f"External asset references are forbidden: {relative}: {value}")
    seen = set()
    for spec in models:
        if not isinstance(spec, dict) or not isinstance(spec.get("path"), str):
            raise ValidationError("Each canonical model needs a path and physical baseline.")
        relative = spec["path"]
        if relative in seen or relative not in hashes or not relative.endswith(".xml"):
            raise ValidationError(f"Duplicate, unhashed or unsupported canonical MJCF: {relative}")
        asset_path(assets, relative)
        seen.add(relative)
    return manifest


def dependencies():
    try:
        import mujoco
        import numpy as np
    except ImportError as exc:
        raise ValidationError("Install simulation/requirements.txt in the active Python environment.") from exc
    return mujoco, np


def validate_model(model, spec, mujoco, np):
    if not math.isfinite(model.opt.timestep) or model.opt.timestep <= 0:
        raise ValidationError("Timestep must be finite and positive.")
    if not np.isfinite(model.body_mass).all() or np.any(model.body_mass < 0):
        raise ValidationError("Body masses must be finite and nonnegative.")
    if np.any(model.body_mass[model.body_dofnum > 0] <= 0):
        raise ValidationError("Moving bodies require positive mass.")
    expected_masses = spec.get("body_masses_kg")
    actual_masses = {}
    for index in range(1, model.nbody):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, index)
        if not name:
            raise ValidationError("Every non-world body must have a stable name.")
        actual_masses[name] = float(model.body_mass[index])
    if not actual_masses or not isinstance(expected_masses, dict) or actual_masses.keys() != expected_masses.keys():
        raise ValidationError("Canonical body names do not match the mass baseline.")
    for name, actual in actual_masses.items():
        expected = expected_masses[name]
        if not isinstance(expected, (int, float)) or not math.isfinite(expected) or not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-12):
            raise ValidationError(f"Canonical mass mismatch: {name}")
    expected_joints = spec.get("joints")
    actual_joints = {}
    types = {int(mujoco.mjtJoint.mjJNT_FREE): "free", int(mujoco.mjtJoint.mjJNT_BALL): "ball",
             int(mujoco.mjtJoint.mjJNT_SLIDE): "slide", int(mujoco.mjtJoint.mjJNT_HINGE): "hinge"}
    for index in range(model.njnt):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, index)
        if not name:
            raise ValidationError("Every joint must have a stable name.")
        actual_joints[name] = {"type": types[int(model.jnt_type[index])],
                              "limited": bool(model.jnt_limited[index]),
                              "range": model.jnt_range[index].tolist()}
    if not isinstance(expected_joints, dict) or actual_joints.keys() != expected_joints.keys():
        raise ValidationError("Canonical joint names do not match the baseline.")
    for name, actual in actual_joints.items():
        expected = expected_joints[name]
        if (not isinstance(expected, dict) or actual["type"] != expected.get("type")
                or type(expected.get("limited")) is not bool or actual["limited"] != expected["limited"]):
            raise ValidationError(f"Canonical joint type/limit mismatch: {name}")
        limits = np.asarray(expected.get("range"), dtype=float)
        if limits.shape != (2,) or not np.isfinite(limits).all() or not np.allclose(actual["range"], limits, rtol=0, atol=1e-12):
            raise ValidationError(f"Canonical joint range mismatch: {name}")
        if actual["limited"] and limits[0] >= limits[1]:
            raise ValidationError(f"Invalid joint range: {name}")
    return {"body_count": len(actual_masses), "joint_count": len(actual_joints),
            "total_mass_kg": sum(actual_masses.values()), "timestep_s": model.opt.timestep}


def rollout(model, steps, mujoco, np):
    data = mujoco.MjData(model)
    state_type = mujoco.mjtState.mjSTATE_INTEGRATION
    trajectory = np.empty((steps, mujoco.mj_stateSize(model, state_type)))
    start = time.perf_counter()
    for step in range(steps):
        mujoco.mj_step(model, data)
        mujoco.mj_getState(model, data, trajectory[step], state_type)
        if not np.isfinite(trajectory[step]).all() or not np.isfinite(data.qacc).all():
            raise ValidationError(f"Non-finite simulation state at step {step}.")
        if np.any(data.warning.number):
            raise ValidationError(f"MuJoCo warning at step {step}: {data.warning.number.tolist()}")
        if not math.isclose(data.time, (step + 1) * model.opt.timestep, rel_tol=1e-10, abs_tol=1e-12):
            raise ValidationError("Simulation time reset or failed to advance.")
    return trajectory, time.perf_counter() - start


def check(root=ROOT, steps=200, repeat=True):
    if not 1 <= steps <= 10000:
        raise ValidationError("Steps must be between 1 and 10000.")
    manifest = load_manifest(root)
    mujoco, np = dependencies()
    report = {"backend": "mujoco-cpu", "mujoco": mujoco.__version__, "numpy": np.__version__,
              "python": platform.python_version(), "platform": platform.platform(),
              "steps": steps, "accelerated_backend": "not configured or validated", "models": []}
    for spec in manifest["models"]:
        path = asset_path(root / "assets", spec["path"])
        model = mujoco.MjModel.from_xml_path(str(path))
        result = {"path": spec["path"], **validate_model(model, spec, mujoco, np)}
        first, elapsed = rollout(model, steps, mujoco, np)
        result.update(wall_seconds=elapsed, simulated_seconds=steps * model.opt.timestep,
                      simulated_seconds_per_wall_second=steps * model.opt.timestep / max(elapsed, 1e-12))
        if repeat:
            fresh_model = mujoco.MjModel.from_xml_path(str(path))
            second, _ = rollout(fresh_model, steps, mujoco, np)
            if not np.array_equal(first, second):
                raise ValidationError(f"Determinism drift for {spec['path']}: {np.max(np.abs(first - second))}")
            result["max_absolute_drift"] = 0.0
        report["models"].append(result)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=200)
    args = parser.parse_args()
    try:
        print(json.dumps(check(steps=args.steps), indent=2))
        return 0
    except (ValueError, RuntimeError, OSError, ET.ParseError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
