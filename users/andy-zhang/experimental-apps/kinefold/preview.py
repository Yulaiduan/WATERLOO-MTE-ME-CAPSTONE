"""Serve/restart the Kinefold browser app using installed Python standard library.

Invocation: python preview.py start [--no-browser] | stop | serve
Inputs: adjacent app assets, fixed http://127.0.0.1:4191/ (no physical units).
Outputs: detached loopback server, readable .preview/server.log and health state.
Limitations: local single-user preview; no hosting, login service or simulation.
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
          "reference-v4.js", "conventions.js", "reference.json", "preview-geometry.js", "solvers.js"}


SOLVER_LOCK = threading.Lock()
LAB = ROOT.parent / "wheel-leg-lab"

def start_solvers():
    """Start/reuse the verified sibling bench through its durable launcher."""
    with SOLVER_LOCK:
        launcher = LAB / "Start-Pymunk.ps1"
        if not launcher.exists():
            raise RuntimeError("Restore the sibling wheel-leg-lab folder first.")
        result = subprocess.run(["powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(launcher), "-NoBrowser"], capture_output=True, text=True, timeout=50, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        if result.returncode:
            raise RuntimeError(result.stdout.strip() or result.stderr.strip() or "Run Setup Motion Lab.cmd first.")
        with urlopen("http://127.0.0.1:4186/api/health", timeout=3) as response:
            state=json.load(response)
        if state.get("app") != "capstone-wheel-leg-lab" or Path(state.get("root", "")).resolve() != LAB.resolve():
            raise RuntimeError("Port 4186 did not identify the expected Motion Lab checkout.")
        return {"ready": True, "origin": "http://127.0.0.1:4186"}


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
            if self.path == "/__kinefold_solvers":
                if self.headers.get("Origin") != URL.rstrip("/") or self.headers.get("X-Kinefold-Request") != "solver-tabs":
                    self.send_error(403)
                    return
                try:
                    result, status = start_solvers(), 200
                except Exception as error:
                    result, status = {"error": str(error)}, 503
                payload = json.dumps(result).encode()
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
