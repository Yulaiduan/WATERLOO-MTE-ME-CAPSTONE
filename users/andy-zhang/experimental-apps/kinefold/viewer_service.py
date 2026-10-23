"""Own one bounded native Kinefold results-playback child for preview.py.

Use ViewerService(app_root).handle(JSON_object) and .close() on server shutdown.
Public input: open with builder mm/deg/kg/N params, seconds/SI runConfig, optional
terrain-contact contactConfig and display name; status/close have no arguments. Output: JSON and HTTP
status, plus ignored .preview/viewer.log and token-scoped readiness state.
Only the adjacent desktop_viewer.py and app .venv Python may execute. This is a
local single-user experimental playback service, not a remote desktop or engine.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import secrets
import subprocess
import threading
import time

from dynamic_model import Model


class ViewerService:
    """Serialize native opens and retain ownership of exactly one Popen object."""

    START_TIMEOUT = 90
    MAX_REQUEST_BYTES = 128 * 1024

    def __init__(self, root):
        self.root = Path(root).resolve()
        self.state_dir = self.root / '.preview'
        self._lock = threading.RLock()
        self._process = None
        self._token = None
        self._started = 0
        self._name = ''
        self._state = {'state': 'closed'}

    def _runtime(self):
        directory = self.root / '.venv' / ('Scripts' if os.name == 'nt' else 'bin')
        if os.name == 'nt' and (directory / 'pythonw.exe').is_file():
            return directory / 'pythonw.exe'
        return directory / ('python.exe' if os.name == 'nt' else 'python')

    @staticmethod
    def _validate(request):
        if not isinstance(request, dict) or request.get('action') not in ('open', 'status', 'close'):
            raise ValueError('Choose viewer action open, status or close.')
        if request['action'] != 'open':
            if set(request) != {'action'}:
                raise ValueError('status and close accept only action.')
            return None
        if not {'action', 'params', 'runConfig'} <= set(request) or set(request) - {'action', 'params', 'runConfig', 'name', 'contactConfig', 'caseConfig', 'motorConfig'}:
            raise ValueError('open requires action, params and runConfig; optional name and contactConfig only.')
        if 'motorConfig' in request:
            from motor_model import Motor
            if not isinstance(request['motorConfig'],dict):
                raise ValueError('motorConfig must be an object when supplied.')
            Motor.resolve(request['motorConfig'])
        encoded = json.dumps(request, allow_nan=False)
        if len(encoded.encode('utf-8')) > ViewerService.MAX_REQUEST_BYTES:
            raise ValueError('Viewer request exceeds 131072 bytes.')
        name = request.get('name', 'Captured design')
        if not isinstance(name, str) or len(name) > 100 or any(not c.isprintable() for c in name):
            raise ValueError('Viewer name must be at most 100 printable characters.')
        # The mode selects a fixed local engine. Never apply prescribed-input
        # validation to a real finite-mass contact case or accept arbitrary code.
        contact = request.get('contactConfig')
        if 'contactConfig' in request and (not isinstance(contact, dict) or contact.get('mode') not in ('terrain-contact','prescribed-height')):
            raise ValueError('Choose a known interaction mode.')
        if isinstance(contact,dict) and contact.get('mode') == 'terrain-contact':
            from contact_dynamics import validate_contact_request
            validate_contact_request({'engine': 'pymunk', 'params': request['params'],
                                      'runConfig': request['runConfig'], 'contactConfig': contact, **({'caseConfig':request['caseConfig']} if 'caseConfig' in request else {}), **({'motorConfig':request['motorConfig']} if 'motorConfig' in request else {})})
        else:
            Model(request['params'], request['runConfig'], request.get('motorConfig'))
        snapshot = json.loads(encoded)
        snapshot['name'] = name.strip() or 'Captured design'
        return snapshot

    def handle(self, request):
        """Return (JSON, HTTP status); callers enforce HTTP origin/body guards."""
        try:
            snapshot = self._validate(request)
        except (ValueError, TypeError, ArithmeticError, KeyError) as error:
            return {'error': str(error)}, 400
        except ImportError as error:
            return {'error': 'Terrain-contact backend is unavailable: ' + str(error)}, 503
        with self._lock:
            if request['action'] == 'status':
                return self._status(), 200
            if request['action'] == 'close':
                self.close()
                return dict(self._state), 200
            if self._process is not None and self._process.poll() is None:
                return {'error': 'A native playback window is already opening or open. Close it before opening another captured run.', **self._status()}, 409
            runtime = self._runtime()
            script = self.root / 'desktop_viewer.py'
            if not runtime.is_file():
                return {'error': 'Native playback needs the app environment. Run Setup Kinefold.cmd, then retry.'}, 503
            if not script.is_file():
                return {'error': 'desktop_viewer.py is missing from this app folder.'}, 503
            self.state_dir.mkdir(exist_ok=True)
            self._token = secrets.token_urlsafe(24)
            self._started = time.monotonic()
            self._name = snapshot['name']
            mode = 'terrain-contact' if (snapshot.get('contactConfig') or {}).get('mode')=='terrain-contact' else 'prescribed-input'
            self._state = {'state': 'starting', 'name': self._name, 'mode': mode,
                           'message': f'Integrating captured Pymunk {mode} design and opening native playback.'}
            envelope = {'request': snapshot, 'token': self._token, 'parentPid': os.getpid()}
            try:
                with (self.state_dir / 'viewer.log').open('a', encoding='utf-8') as log:
                    self._process = subprocess.Popen(
                        [str(runtime), str(script), '--request-stdin'], cwd=self.root,
                        stdin=subprocess.PIPE, stdout=log, stderr=log,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                    )
                self._process.stdin.write(json.dumps(envelope, allow_nan=False).encode('utf-8'))
                self._process.stdin.close()
                threading.Thread(target=self._watch, args=(self._process, self._token), daemon=True).start()
            except (OSError, ValueError) as error:
                self._terminate_owned()
                self._process = None
                self._token = None
                self._state = {'state': 'error', 'error': 'Cannot start native playback: ' + str(error)}
                return dict(self._state), 503
            return self._status(), 202

    def _status(self):
        process = self._process
        if process is None:
            return dict(self._state)
        try:
            path = self.state_dir / 'viewer-state.json'
            if path.stat().st_size <= 32768:
                data = json.loads(path.read_text(encoding='utf-8'))
                if isinstance(data, dict) and data.get('token') == self._token:
                    self._state = {key: value for key, value in data.items() if key != 'token'}
        except (OSError, ValueError):
            pass  # Atomic replace can briefly be unavailable to Windows readers.
        code = process.poll()
        if code is not None and self._state.get('state') not in ('closed', 'error'):
            if code == 0 and self._state.get('state') == 'ready':
                self._state = {'state': 'closed', 'name': self._name}
            else:
                self._state = {'state': 'error', 'name': self._name,
                               'error': f'Native playback exited before readiness (exit {code}). See .preview/viewer.log; verify Tk and run Setup Kinefold.cmd.'}
        return dict(self._state)

    def _watch(self, process, token):
        while process.poll() is None:
            with self._lock:
                if process is not self._process or token != self._token:
                    return
                state = self._status()
                if state.get('state') == 'starting' and time.monotonic() - self._started > self.START_TIMEOUT:
                    self._terminate_owned()
                    self._process = None
                    self._token = None
                    self._state = {'state': 'error', 'error': 'Native integration/opening exceeded 90 seconds and was stopped. Reduce duration or step count; see .preview/viewer.log.'}
                    return
            time.sleep(.25)

    def _terminate_owned(self):
        process = self._process
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)

    def close(self):
        """Stop this object's child only; never search processes or kill a PID."""
        with self._lock:
            self._terminate_owned()
            self._process = None
            self._token = None
            self._state = {'state': 'closed', 'name': self._name}
