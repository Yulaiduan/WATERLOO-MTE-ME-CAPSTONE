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
from native_viewer import launch as launch_native, status as native_status, show as show_native
from spring_mechanisms import CATALOG, MECHANISM_DEFAULTS
import counterbalance
from suspension_architecture import constant_lift_profile
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
        if self.path=='/api/suspension-architecture/defaults':return self.json(constant_lift_profile())
        if self.path=='/api/counterbalance/defaults':return self.json(counterbalance.DEFAULTS)
        if self.path=='/api/spring-presets': return self.json({'catalog':CATALOG,'defaults':MECHANISM_DEFAULTS})
        if self.path.startswith('/api/native-gui/'):
            try:return self.json(native_status(self.path.rsplit('/',1)[1]))
            except ValueError as error:return self.json({'error':str(error)},404)
        if self.path=='/math/wheel_leg_ode45.m':
            payload=(ROOT/'math/wheel_leg_ode45.m').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type','text/plain; charset=utf-8')
            self.send_header('Content-Disposition','attachment; filename="wheel_leg_ode45.m"')
            self.send_header('Content-Length',str(len(payload)))
            self.end_headers();self.wfile.write(payload);return
        super().do_GET()
    def do_POST(self):
        native_show=self.path.startswith('/api/native-gui/') and self.path.endswith('/show')
        if self.path not in ['/api/simulate','/api/pymunk/simulate','/api/math/simulate','/api/counterbalance/math','/api/counterbalance/pymunk','/api/counterbalance/advance','/api/native-gui'] and not native_show:
            return self.json({'error':'Unknown endpoint.'},404)
        try:
            count=int(self.headers.get('Content-Length','0'))
            if count<=0 or count>50000: return self.json({'error':'Invalid request size.'},413)
            value=json.loads(self.rfile.read(count))
            if self.path=='/api/native-gui' or native_show or self.path=='/api/counterbalance/advance':
                origin=self.headers.get('Origin');allowed={f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}
                if (origin and origin not in allowed) or self.headers.get('Sec-Fetch-Site')=='cross-site':return self.json({'error':'Native launch and live interaction require this local application.'},403)
                if self.path=='/api/counterbalance/advance':return self.json(counterbalance.advance(value))
                if native_show:return self.json(show_native(self.path.split('/')[3]))
                return self.json(launch_native(value),202)
            mathematical=self.path in ('/api/math/simulate','/api/counterbalance/math')
            lock=MATH_LOCK if mathematical else RUN_LOCK
            if not lock.acquire(blocking=False): return self.json({'error':'This solver is already running. Retry when it finishes.'},409)
            try:
                if self.path.startswith('/api/counterbalance/'):
                    result=counterbalance.simulate(value,backend='math' if mathematical else 'pymunk')
                else:result=simulate_math(value) if mathematical else simulate(value)
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
