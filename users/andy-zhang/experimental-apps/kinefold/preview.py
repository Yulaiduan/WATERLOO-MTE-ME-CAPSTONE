"""Serve/restart the Kinefold browser app using installed Python standard library.

Invocation: python preview.py start [--no-browser] | stop | serve
Inputs: adjacent app assets, fixed http://127.0.0.1:4191/ (no physical units).
Outputs: detached loopback server, readable .preview/server.log and health state.
Limitations: local single-user preview; experimental dynamics run in an app venv.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError
from urllib.request import Request, urlopen
import webbrowser

ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:4191/"
IDENTITY = hashlib.sha256(str(ROOT).casefold().encode()).hexdigest()[:20]
STATE = ROOT / ".preview"
ASSETS = {"index.html", "style.css", "app.js", "model.js", "variables.js",
          "reference-v4.js", "conventions.js", "reference.json", "preview-geometry.js",
          "solvers.js", "solver-style.css", "project-store.js", "designs.js"}


DYNAMICS_LOCK = threading.Lock()
MAX_REQUEST_BYTES = 128 * 1024
MAX_RESULT_BYTES = 16 * 1024 * 1024


def reject_nonfinite(value):
    """JSON input and engine output must contain finite numbers only."""
    raise ValueError("Nonfinite JSON number: " + value)


def run_dynamics(request):
    """Integrate one bounded request in this app's installed physics environment."""
    if not isinstance(request, dict) or set(request) != {"engine", "params", "runConfig"}:
        return {"error": "Expected engine, params and runConfig only."}, 400
    if not isinstance(request["engine"], str) or request["engine"] not in {"analytical", "pymunk"}:
        return {"error": "Choose analytical or pymunk."}, 400
    if not isinstance(request["params"], dict) or not isinstance(request["runConfig"], dict):
        return {"error": "params and runConfig must be objects."}, 400
    python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file():
        return {"error": "Dynamics dependencies are not installed. Run Setup Kinefold.cmd in this app folder, then retry. The builder and static solver remain available."}, 503
    if not DYNAMICS_LOCK.acquire(blocking=False):
        return {"error": "A dynamics run is already in progress. Wait for it to finish, then retry."}, 409
    try:
        result = subprocess.run(
            [str(python), str(ROOT / "dynamics.py"), "--request-stdin"],
            input=json.dumps(request, allow_nan=False), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=90, cwd=ROOT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if len(result.stdout.encode("utf-8")) > MAX_RESULT_BYTES:
            return {"error": "Result exceeded the local preview limit. Reduce duration or output sample rate."}, 422
        try:
            data = json.loads(result.stdout, parse_constant=reject_nonfinite)
        except ValueError:
            return {"error": "Dynamics engine did not return a valid result. Run Setup Kinefold.cmd to verify its environment. " + result.stderr.strip()[-1500:]}, 502
        if not isinstance(data, dict):
            return {"error": "Dynamics engine returned an unexpected response."}, 502
        if result.returncode or "error" in data:
            return {"error": str(data.get("error", "Dynamics integration failed."))}, 422
        return data, 200
    except subprocess.TimeoutExpired:
        return {"error": "Dynamics run exceeded 90 seconds and was stopped. Reduce duration, relax the step or check the design."}, 504
    except (OSError, ValueError) as error:
        return {"error": str(error)}, 503
    finally:
        DYNAMICS_LOCK.release()


def health():
    try:
        with urlopen(URL + "__kinefold_health", timeout=1) as response:
            return json.load(response)
    except (URLError, ValueError, OSError):
        return None


def is_ours(value):
    return isinstance(value, dict) and value.get("app") == "kinefold-v1" and value.get("root") == IDENTITY


def serve():
    token = secrets.token_urlsafe(32)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)

        def do_GET(self):
            route = self.path.split("?", 1)[0]
            if route == "/__kinefold_health":
                data = json.dumps({"app": "kinefold-v1", "root": IDENTITY}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            elif route == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
            elif route == "/" or route.removeprefix("/") in ASSETS:
                super().do_GET()
            else:
                self.send_error(404)

        def do_HEAD(self):
            route = self.path.split("?", 1)[0]
            if route == "/" or route.removeprefix("/") in ASSETS:
                super().do_HEAD()
            else:
                self.send_error(404)

        def do_POST(self):
            if self.path == "/api/dynamics":
                if self.headers.get("Origin") != URL.rstrip("/") or self.headers.get("X-Kinefold-Request") != "coupled-dynamics":
                    payload = b'{"error":"Dynamics requests must come from this Kinefold page."}'
                    self.send_response(403)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                    return
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if not 0 < length <= MAX_REQUEST_BYTES:
                        result, status = {"error": "Request body must be between 1 and 131072 bytes."}, 413
                    elif self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json":
                        result, status = {"error": "Send an application/json request."}, 415
                    else:
                        self.connection.settimeout(10)
                        raw = self.rfile.read(length)
                        if len(raw) != length:
                            raise ValueError("Incomplete request body.")
                        request = json.loads(raw, parse_constant=reject_nonfinite)
                        result, status = run_dynamics(request)
                except (ValueError, OSError) as error:
                    result, status = {"error": str(error)}, 400
                payload = json.dumps(result, allow_nan=False).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            if self.path != "/__kinefold_stop" or self.headers.get("X-Kinefold-Token") != token:
                self.send_error(403)
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Kinefold stopping")
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            super().end_headers()

    with ThreadingHTTPServer(("127.0.0.1", 4191), Handler) as server:
        STATE.mkdir(exist_ok=True)
        (STATE / "server.json").write_text(json.dumps({"root": IDENTITY, "token": token}), encoding="utf-8")
        print(f"Kinefold ready at {URL}", flush=True)
        server.serve_forever(poll_interval=.15)


def start(open_browser=True):
    current = health()
    if is_ours(current):
        print(f"Kinefold already running. Ready: {URL}")
    else:
        STATE.mkdir(exist_ok=True)
        options = {}
        if os.name == "nt":
            options["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        else:
            options["start_new_session"] = True
        with (STATE / "server.log").open("ab") as log:
            process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "serve"],
                                       cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=log, **options)
        for _ in range(60):
            if is_ours(health()):
                break
            if process.poll() is not None:
                raise RuntimeError(f"Could not start Kinefold on port 4191. Another app may own it. Read {STATE / 'server.log'}")
            time.sleep(.15)
        else:
            process.terminate()
            raise RuntimeError(f"Startup timed out. Read {STATE / 'server.log'}")
        print(f"Kinefold ready: {URL}")
    print(f"Project: {ROOT}\nTo stop: double-click Stop Kinefold.cmd")
    if open_browser:
        webbrowser.open(URL)


def stop():
    current = health()
    if not is_ours(current):
        if current:
            raise RuntimeError("The service at port 4191 is not this Kinefold app. It was left untouched.")
        print("This Kinefold server is not running.")
        return
    state = json.loads((STATE / "server.json").read_text(encoding="utf-8"))
    if state.get("root") != IDENTITY:
        raise RuntimeError("Server identity differs; no process was stopped.")
    request = Request(URL + "__kinefold_stop", data=b"", headers={"X-Kinefold-Token": state["token"]})
    with urlopen(request, timeout=3):
        pass
    for _ in range(30):
        if not is_ours(health()):
            print("Kinefold stopped.")
            return
        time.sleep(.1)
    raise RuntimeError("Stop request sent but server is still responding. Read .preview/server.log.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["start", "stop", "serve"])
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "serve":
            serve()
        elif args.command == "stop":
            stop()
        else:
            start(not args.no_browser)
    except Exception as error:
        print(f"Kinefold error: {error}", file=sys.stderr)
        sys.exit(1)
