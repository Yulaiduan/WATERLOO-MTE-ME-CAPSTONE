"""Step actual ideal Pymunk constraints for three new force/travel examples.

Run from app: .venv/Scripts/python.exe scripts/verify_force_geometry.py
Inputs: retained mm/degree cases, positive existing physical mass allocation,
full angular sweep, zero gravity/contact and no collision shapes. Outputs:
docs/force-travel-engine-checks.json with 2/1/0.5ms refinement and source hashes.
Uses pinned Pymunk/NumPy and the existing angular fixture, without pose resets.
Limits: geometry consistency only, not force, impact, collision, hardware or
canonical robot validation; analytical force checks are separate.
"""
from pathlib import Path
import sys
import json
import hashlib
import platform
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import generalized_leg as g
from verify_inversion_geometry import engine_run


def main():
    app=Path(__file__).resolve().parents[1]
    data=json.loads((app/'docs/force-travel-results.json').read_text())
    rows=[]
    for name in ['rounded_equal320_9over5','refined_within5','rounded_indexed_equal300']:
        case=next(c for c in data['selected'] if c['id']==name)
        p=case['config'];a,b=case['full_inversion']['bounds_deg']
        cfg=g.physical_allocation(g.config(dict(L2=p['L2'],L3=p['L3'],ra=p['ra'],rb=60,
            alpha=0,phi0=p['phi0'],te=a,tc=b,g=0,Fy=0,Fz=0)))
        runs=[engine_run(cfg,a,b,dt) for dt in [.002,.001,.0005]]
        passed=all(r['passed'] for r in runs[1:]) and runs[-1]['max_path_error_mm']<.8*runs[0]['max_path_error_mm']
        for r in runs:r.pop('trace')
        rows.append(dict(id=name,passed=passed,resolved_config=cfg,refinement=runs))
        print(json.dumps(rows[-1]),flush=True)
    d=dict(schema='camel/force-travel-geometry/v1',all_passed=all(c['passed'] for c in rows),
      cases=rows,python=platform.python_version(),
      scope='Actual two-second ideal full angular inversion; zero gravity/contact; no collision shapes; force is not inferred from this geometry check.',
      acceptance='Both1ms and0.5ms: path/pin<0.1mm, guide<1e-4rad, tracking<0.01rad; fine path error improves over2ms. Coarse failure retained.',
      sources={p:hashlib.sha256((app/p).read_bytes()).hexdigest() for p in [
          'scripts/verify_force_geometry.py','scripts/verify_inversion_geometry.py','generalized_leg.py','docs/force-travel-results.json']})
    (app/'docs/force-travel-engine-checks.json').write_bytes((json.dumps(d,separators=(',',':'))+'\n').encode())
    return 0 if d['all_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
