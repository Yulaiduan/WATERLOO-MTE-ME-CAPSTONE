"""Step three unequal inversion examples using actual Pymunk constraints.

Run from app: .venv/Scripts/python.exe scripts/verify_unequal_geometry.py
Inputs: selected mm/degree cases, existing positive physical mass allocation,
zero gravity/force/collision shapes, fullq100..260. Outputs compact
docs/unequal-inversion-engine-checks.json with 2/1/.5/.25ms evidence.
Only initial poses assigned; real motor/pivot/gear constraints generate motion.
Limits: geometry, not collision/contact, compliance, motor or hardware proof.
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
    data=json.loads((app/'docs/unequal-inversion-results.json').read_text());rows=[]
    for name in ['clear25','clear50','clear100']:
        c=next(c for c in data['selected'] if c['id']==name);p=c['config']
        cfg=g.physical_allocation(g.config(dict(L2=p['L2'],L3=p['L3'],ra=p['ra'],rb=60,
                     alpha=0,phi0=0,te=100,tc=260,g=0,Fy=0,Fz=0)))
        runs=[engine_run(cfg,100,260,dt) for dt in [.002,.001,.0005,.00025]]
        passed=all(r['passed'] for r in runs[-2:]) and runs[-1]['max_path_error_mm']<.8*runs[0]['max_path_error_mm']
        for r in runs:r.pop('trace')
        row=dict(id=name,passed=passed,resolved_config=cfg,refinement=runs);rows.append(row)
        print(json.dumps(row),flush=True)
    out=dict(all_passed=all(c['passed'] for c in rows),cases=rows,
       acceptance='0.5/0.25ms path/pin<0.1mm, guide<1e-4rad, tracking<0.01rad; fine path<0.8coarse; all coarse results retained.',
       scope='Actual ideal angular constraints, positive masses, no gravity/forces/collision shapes; no physical clearance/force proof.',
       sources={p:hashlib.sha256((app/p).read_bytes()).hexdigest() for p in ['scripts/verify_unequal_geometry.py',
            'scripts/verify_inversion_geometry.py','generalized_leg.py','docs/unequal-inversion-results.json']})
    (app/'docs/unequal-inversion-engine-checks.json').write_bytes((json.dumps(out,separators=(',',':'))+'\n').encode())
    return 0 if out['all_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
