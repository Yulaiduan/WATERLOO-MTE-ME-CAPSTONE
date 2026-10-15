"""Compare published equal/upper-long paths and fixed-size/guide controls.

Run from app: .venv/Scripts/python.exe scripts/compare_link_lengths.py
Inputs: retained curved/unequal JSON, audited phase-zero geometry; mm/deg/N/Nm.
Outputs: docs/equal-link-comparison.json with recomputed comparisons, controls,
source hashes and exact r2 identity checks. NumPy/SciPy use existing pins.
Limits: selected rounded comparisons, not a new optimum, loaded simulation,
collision clearance, thermal duty or measured compliance. One infeasible
control retains its actual capacity instead of silently changing the stroke.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from curved_path_search import candidate,curve,R,json_scalar

APP=Path(__file__).resolve().parents[1]


def main():
    load=lambda n:json.loads((APP/'docs'/n).read_text())
    equal=load('curved-path-results.json');unequal=load('unequal-inversion-results.json')
    cases=[];pairs=[];controls=[];errors=[]
    for target in [25,50,75,100]:
        pair=[]
        for data,old,new in [(equal,f'example{target}',f'equal{target}'),
                             (unequal,f'upper{target}',f'upper{target}')]:
            ref=next(c for c in data['selected'] if c['id']==old);p=ref['config']
            c=candidate(new,p['L2'],p['L3'],p['qab'],p['te']);cases.append(c);pair.append(c)
            for key in ['peak_45kg_hip_Nm','rms_45kg_hip_uniform_height_Nm','hip_ROM_deg']:
                errors.append(abs(c['force'][key]-ref['force'][key]))
            errors.append(abs(c['normal']['signed_drift_mm']-ref['normal']['signed_drift_mm']))
        a,b=pair;f='peak_45kg_hip_Nm'
        pairs.append(dict(target_mm=target,equal=a['id'],unequal=b['id'],
            hip_peak_increase_percent=100*(b['force'][f]/a['force'][f]-1),
            link_sum_saved_mm=a['link_sum_mm']-b['link_sum_mm'],
            max_link_increase_mm=max(b['config']['L2'],b['config']['L3'])-a['config']['L2']))
        p=b['config'];length=(p['L2']+p['L3'])/2;r=p['qab'];start=p['te']
        capacity=float(curve(175*R,length,length,r)[1]-curve(start*R,length,length,r)[1])
        if capacity<325-1e-9:
            controls.append(dict(id=f'control{target}',reference=b['id'],L2=length,L3=length,qab=r,
                start_deg=start,end_cap_deg=175,capacity_mm=capacity,feasible_325=False,
                reason='Same link sum and guide cannot supply325 mm by175 degrees; stroke not clipped.'))
        else:
            c=candidate(f'control{target}',length,length,r,start);cases.append(c)
            controls.append(dict(id=c['id'],reference=b['id'],feasible_325=True,capacity_mm=capacity))
    assert max(errors)<1e-8
    # A second r2 control pair also meets the assumed10mm guide surplus.
    for name,a,b in [('r2_equal',190.,190.),('r2_upper',205.,175.)]:
        cases.append(candidate(name,a,b,2.,100.))
    for c in cases:
        p=c['config'];gap=p['L2']-60*(p['qab']+1)
        c['comparison_guide_pitch_surplus_mm']=gap
        c['comparison_10mm_guide_pass']=gap>=10-1e-9
    # Independent fixed-r2 identities, not another call to the metric helper.
    q=np.linspace(100*R,260*R,501);t=q-math.pi;S,D=380.,30.
    x,z,jx,jz=curve(q,205,175,2);xe,ze,jxe,jze=curve(q,190,190,2)
    identity=max(float(np.max(abs(a-b))) for a,b in [(x,D*np.cos(t)),(z,S*np.sin(t)),
        (jx,-D*np.sin(t)),(jz,S*np.cos(t)),(z,ze),(jz,jze),(xe,np.zeros_like(q))])
    assert identity<1e-9
    capacity165=float(curve(165*R,190,190,1.8)[1]-curve(100*R,190,190,1.8)[1])
    sources=['scripts/compare_link_lengths.py','curved_path_search.py','force_travel_search.py',
             'inversion_search.py','docs/curved-path-results.json','docs/unequal-inversion-results.json']
    out=dict(schema='camel/equal-link-comparison/v1',date='2026-10-15',base_revision='14f53f1',
       scope='Selected analytical comparisons and next-sweep planning; no new large optimization or physical clearance claim.',
       assumptions=dict(total_mm=325,useful_mm=285,buffers_mm=[20,20],start_deg=100,end_cap_deg=175,
          alpha=0,phi0=0,wheel_radius_mm=200,vertical_force_N=110.3625,
          load='45kg equally shared four corners; massless moving links, no springs/inertia'),
       selected=cases,pairs=pairs,controls=controls,
       rom_sensitivity=dict(case='equal50',normal_bounds_deg=[100,165],capacity_mm=capacity165,
           equal_link_mm_for_325_at_fixed_ratio_and_bounds=190*325/capacity165,
           scope='Capacity only; does not additionally match lateral excursion.'),
       checks=dict(retained_metric_comparisons=len(errors),max_retained_metric_error=max(errors),
          r2_identity_max_error_mm_rad_units=identity,r2_samples=501),
       provenance=dict(sources={p:hashlib.sha256((APP/p).read_bytes()).hexdigest() for p in sources}))
    target=APP/'docs/equal-link-comparison.json'
    target.write_bytes((json.dumps(out,separators=(',',':'),default=json_scalar)+'\n').encode())
    print(json.dumps(dict(cases=len(cases),bytes=target.stat().st_size,pairs=pairs,controls=controls,checks=out['checks']),indent=2))


if __name__=='__main__':main()
