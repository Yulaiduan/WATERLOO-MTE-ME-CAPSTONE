"""Launch the local torque explorer in a browser with a hidden persistent server.

Run python launcher.py [--no-browser]. Inputs: adjacent app files, localhost 8772.
Outputs: HTTP app, default-browser window, temporary diagnostic log on startup.
Uses installed Python and its standard library; no installation or robot control.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent
URL = 'http://127.0.0.1:8772/'
LOG = Path(tempfile.gettempdir()) / 'torque-coupling-server.log'


def running():
    try:
        with urllib.request.urlopen(URL + 'api/health', timeout=0.5) as response:
            data = json.load(response)
    except (OSError, ValueError, urllib.error.URLError):
        return False
    if data.get('app') != 'torque-coupling':
        raise RuntimeError('Port 8772 belongs to another app. Close it and retry.')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    if not running():
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        with LOG.open('a', encoding='utf-8') as log:
            process = subprocess.Popen(
                [sys.executable, '-B', str(ROOT / 'server.py')], cwd=ROOT,
                stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                creationflags=flags, start_new_session=os.name != 'nt',
            )
        deadline = time.monotonic() + 8
        while not running():
            if process.poll() is not None or time.monotonic() >= deadline:
                raise RuntimeError(f'The app could not start. See {LOG}')
            time.sleep(0.1)
    print('Torque Coupling is ready at ' + URL)
    if not args.no_browser:
        if os.name == 'nt':
            os.startfile(URL)
        elif not webbrowser.open(URL):
            raise RuntimeError('Open this address in your browser: ' + URL)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Unable to open Torque Coupling: {error}', file=sys.stderr)
        raise SystemExit(1)
