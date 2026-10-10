"""Serve the isolated wheel-leg toolkit on loopback.

Run: python server.py --port 4186 (or legacy geometry port 4175).
Inputs: local HTTP JSON configuration in documented SI units and static pages.
Outputs: simulation JSON and local web assets; logs go to the launcher capture.
Requires pinned Pymunk; not a public deployment or authenticated multi-user service.
"""
import argparse
import gzip
import json
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from physics import DEFAULTS, simulate
from math_model import simulate_math
import pymunk

ROOT=Path(__file__).resolve().parent
RUN_LOCK=threading.Lock()
MATH_LOCK=threading.Lock()

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT/'web'),**kwargs)
    def json(self,data,status=200):
        payload=json.dumps(data,separators=(',',':'),allow_nan=False).encode()
        compress='gzip' in self.headers.get('Accept-Encoding','') and len(payload)>3000
        if compress: payload=gzip.compress(payload)
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        if compress: self.send_header('Content-Encoding','gzip')
        self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
    def do_GET(self):
        if self.path.split('?',1)[0] in ['/','/index.html']:
            self.path='/index.html'
        if self.path=='/api/health':
            return self.json({'app':'capstone-wheel-leg-lab','root':str(ROOT),'engine':pymunk.version})
        if self.path=='/api/defaults': return self.json(DEFAULTS)
        if self.path=='/math/wheel_leg_ode45.m':
            payload=(ROOT/'math/wheel_leg_ode45.m').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type','text/plain; charset=utf-8')
            self.send_header('Content-Disposition','attachment; filename="wheel_leg_ode45.m"')
            self.send_header('Content-Length',str(len(payload)))
            self.end_headers();self.wfile.write(payload);return
        super().do_GET()
    def do_POST(self):
        if self.path not in ['/api/simulate','/api/pymunk/simulate','/api/math/simulate']:
            return self.json({'error':'Unknown endpoint.'},404)
        try:
            count=int(self.headers.get('Content-Length','0'))
            if count<=0 or count>50000: return self.json({'error':'Invalid request size.'},413)
            value=json.loads(self.rfile.read(count))
            lock=MATH_LOCK if self.path=='/api/math/simulate' else RUN_LOCK
            if not lock.acquire(blocking=False): return self.json({'error':'This solver is already running. Retry when it finishes.'},409)
            try:
                result=simulate_math(value) if self.path=='/api/math/simulate' else simulate(value)
                result.setdefault('backend','pymunk')
            finally: lock.release()
            self.json(result)
        except (ValueError,TypeError,KeyError) as error:
            self.json({'error':str(error)},400)
        except (BrokenPipeError,ConnectionResetError): pass
        except Exception as error:
            print('SIMULATION ERROR:',repr(error),flush=True)
            self.json({'error':'Simulation failed. Inspect .preview/server.stderr.log.'},500)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=4186,choices=[4186,4175]);args=parser.parse_args()
    print(f'Wheel Leg Lab ready at http://127.0.0.1:{args.port}/',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
