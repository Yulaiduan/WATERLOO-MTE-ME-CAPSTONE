"""Serve the offline torque-coupling explorer on 127.0.0.1:8772.

Run python server.py [--open]. Inputs: local static app files; no user data.
Outputs: loopback HTTP page and optional browser tab. Python standard library.
Limitations: local single-user viewer, no persistent backend or robot control.
"""
import argparse
import functools
import http.server
import json
from pathlib import Path
import urllib.request
import webbrowser

HOST = '127.0.0.1'
PORT = 8772
ROOT = Path(__file__).resolve().parent
URL = f'http://{HOST}:{PORT}/'


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            body = json.dumps({'app': 'torque-coupling', 'version': 1}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


class Server(http.server.ThreadingHTTPServer):
    allow_reuse_address = False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--open', action='store_true')
    args = parser.parse_args()
    try:
        with urllib.request.urlopen(URL + 'api/health', timeout=1) as response:
            health = json.load(response)
    except Exception:
        health = None
    if health is not None:
        if health.get('app') != 'torque-coupling':
            raise SystemExit(f'Port {PORT} belongs to another application.')
        print('Reusing Torque Coupling at ' + URL)
        if args.open:
            webbrowser.open(URL)
        return
    try:
        server = Server((HOST, PORT), functools.partial(Handler, directory=str(ROOT)))
    except OSError as exc:
        try:
            with urllib.request.urlopen(URL + 'api/health', timeout=2) as response:
                health = json.load(response)
        except Exception:
            raise SystemExit(f'Port {PORT} is occupied. Close its app and retry. {exc}') from exc
        if health.get('app') != 'torque-coupling':
            raise SystemExit(f'Port {PORT} belongs to another application.') from exc
        print('Reusing Torque Coupling at ' + URL)
        if args.open:
            webbrowser.open(URL)
        return
    print('Torque Coupling: ' + URL, flush=True)
    if args.open:
        webbrowser.open(URL)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
