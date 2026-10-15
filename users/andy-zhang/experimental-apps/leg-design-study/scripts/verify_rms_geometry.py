"""Check three new lower-long RMS candidates with actual Pymunk constraints.

Run from app: .venv/Scripts/python.exe scripts/verify_rms_geometry.py
Inputs: retained mm/deg candidates, existing positive mass allocation, ideal
prescribed hip motion100..260 degrees; zero gravity/forces/collision shapes.
Outputs docs/rms-link-engine-checks.json with 2/1/0.5/0.25 ms refinement and
source hashes. Uses existing Pymunk/NumPy. Limits: geometry agreement only,
not RMS load, contact, clearance, spring/motor, impact or hardware validation.
"""
from pathlib import Path
import hashlib
import json
import sys

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
import generalized_leg as g
from verify_inversion_geometry import engine_run


def main():
    d=json.loads((APP/'docs/rms-link-results.json').read_text());rows=[]
    for name in ['reverse180_225','fixed450_lower125_50','lower125_175_50']:
        c=next(c for c in d['selected'] if c['id']==name);p=c['config']
        cfg=g.physical_allocation(g.config(dict(L2=p['L2'],L3=p['L3'],ra=p['ra'],rb=60,
          alpha=0,phi0=0,te=100,tc=260,g=0,Fy=0,Fz=0)))
        runs=[engine_run(cfg,100,260,dt) for dt in [.002,.001,.0005,.00025]]
        passed=all(r['passed'] for r in runs[-2:]) and runs[-1]['max_path_error_mm']<.8*runs[0]['max_path_error_mm']
        for r in runs:r.pop('trace')
        row=dict(id=name,passed=passed,resolved_config=cfg,refinement=runs);rows.append(row)
        print(json.dumps(row),flush=True)
    sources=['scripts/verify_rms_geometry.py','scripts/verify_inversion_geometry.py','generalized_leg.py','docs/rms-link-results.json']
    out=dict(all_passed=all(r['passed'] for r in rows),cases=rows,
      acceptance='0.5/0.25ms path/pin<0.1mm, guide<1e-4rad, tracking<0.01rad; finest path<0.8coarse; all coarse results retained.',
      scope='Actual motor/pivot/gear stepping with positive masses, zero gravity/forces/collision shapes; no loaded RMS or physical clearance proof.',
      sources={p:hashlib.sha256((APP/p).read_bytes()).hexdigest() for p in sources})
    (APP/'docs/rms-link-engine-checks.json').write_bytes((json.dumps(out,separators=(',',':'))+'\n').encode())
    return 0 if out['all_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
