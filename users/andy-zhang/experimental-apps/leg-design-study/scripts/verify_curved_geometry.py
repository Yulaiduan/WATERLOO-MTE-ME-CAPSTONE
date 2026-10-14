"""Step actual Pymunk constraints for short ratio-generated curved paths.

Run from app: .venv/Scripts/python.exe scripts/verify_curved_geometry.py
Inputs: retained mm/degree examples, positive existing physical masses, full
angular sweep, zero gravity/contact and no collision shapes. Outputs compact
docs/curved-path-engine-checks.json with 2/1/0.5ms refinement and source hashes.
Only initial poses assigned; real motor/pivot/gear constraints generate motion.
Limits: geometry evidence, not measured compliance, force, impact or hardware.
"""
from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import generalized_leg as g
from verify_inversion_geometry import engine_run


def main():
    app=Path(__file__).resolve().parents[1]
    data=json.loads((app/'docs/curved-path-results.json').read_text());rows=[]
    for name in ['example25','example50','example100']:
        case=next(c for c in data['selected'] if c['id']==name);p=case['config'];a,b=case['full_bounds_deg']
        cfg=g.physical_allocation(g.config(dict(L2=p['L2'],L3=p['L3'],ra=p['ra'],rb=60,
               alpha=0,phi0=0,te=a,tc=b,g=0,Fy=0,Fz=0)))
        runs=[engine_run(cfg,a,b,dt) for dt in [.002,.001,.0005]]
        passed=all(r['passed'] for r in runs[1:]) and runs[-1]['max_path_error_mm']<.8*runs[0]['max_path_error_mm']
        for r in runs:r.pop('trace')
        rows.append(dict(id=name,passed=passed,resolved_config=cfg,refinement=runs));print(json.dumps(rows[-1]),flush=True)
    evidence=dict(all_passed=all(c['passed'] for c in rows),cases=rows,
        scope='Actual ideal full angular geometry, positive masses, no forces/gravity/collision shapes; no compliance/force/contact proof.',
        acceptance='1/0.5ms path/pin<0.1mm, guide<1e-4rad, tracking<0.01rad; fine path error<0.8coarse. Coarse results retained.',
        sources={p:hashlib.sha256((app/p).read_bytes()).hexdigest() for p in ['scripts/verify_curved_geometry.py',
             'scripts/verify_inversion_geometry.py','generalized_leg.py','docs/curved-path-results.json']})
    (app/'docs/curved-path-engine-checks.json').write_bytes((json.dumps(evidence,separators=(',',':'))+'\n').encode())
    return 0 if evidence['all_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
