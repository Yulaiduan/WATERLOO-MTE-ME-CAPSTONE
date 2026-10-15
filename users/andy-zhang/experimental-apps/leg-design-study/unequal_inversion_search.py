"""Find unequal guided-leg paths with a regular inverse through inversion.

Run from app: .venv/Scripts/python.exe unequal_inversion_search.py
Inputs: original alpha=phi0=0 model; mm/deg/N/Nm units;325mm total height,
20mm end reserves; R200 wheel; declared unequal link/guide/start grid below.
Outputs: docs/unequal-inversion-results.json, compact leaders and selected
continuous geometry/force evidence. NumPy/SciPy and existing audited helpers.
Limits: projected wheel/segment/pitch-circle screens, not 3D packaging,
collision-free rods, contact, dynamic motor rating or measured compliance.
"""
from pathlib import Path
import hashlib
import json
import math
import platform
import time
import numpy as np
from curved_path_search import candidate,curve,R,TOTAL,json_scalar

APP=Path(__file__).resolve().parent
TARGETS=[25.,50.,75.,100.]
BASE='aaed324' # Owner 1.25x correction follows the initial broad report.


def wheel_segment_distance(q,a,b,r):
    t=np.asarray(q)-math.pi;x,z=curve(q,a,b,r)[:2]
    projection=np.clip(x*np.cos(t)+z*np.sin(t),0,a)
    return np.hypot(x-projection*np.cos(t),z-projection*np.sin(t))


def evaluate(name,a,b,r,start):
    c=candidate(name,a,b,r,start)
    c['legacy_full_hip_point_pass']=c.pop('full_coplanar220_pass')
    c['normal_hip_point_pass']=c.pop('normal_coplanar220_pass')
    q=np.linspace(100*R,260*R,4001)
    exact=max(b-a,0.)
    numeric=float(np.min(wheel_segment_distance(q,a,b,r)))
    if abs(numeric-exact)>1e-7:raise ValueError('Fold clearance proof and sampled segment disagree')
    c['projection']=dict(wheel_upper_segment_min_mm=exact,
      wheel_hip_min_mm=abs(a-b),wheel_knee_distance_mm=b,
      wheel_rim_to_upper_segment_min_mm=exact-200,
      wheel_to_hip_pitch_circle_gap_mm=abs(a-b)-200-60*r,
      wheel_to_knee_pitch_circle_gap_mm=b-200-60,
      guide_pitch_surplus_mm=a-60*(r+1),
      lower_long=b>a,point_segment_clear=exact>=220-1e-7,
      hip_pitch_circle_clear=(b-a)>=220+60*r-1e-7,
      knee_pitch_circle_clear=b>=280-1e-7,
      recommended_guide_surplus=a>=60*(r+1)+10-1e-7,
      length_ratio=max(a,b)/min(a,b),owner_length_ratio_pass=max(a,b)/min(a,b)<=1.25+1e-9,
      rods_overlap_at_fold=True,
      physical_full_inversion_validated=False)
    return c


def grid():
    uppers=np.arange(150.,400.01,5);lowers=np.arange(150.,400.01,5)
    guides=np.unique(np.r_[np.round(np.arange(1.2,2.60001,.005),8),5/3])
    starts=np.arange(100.,140.01,5)
    aa,rr=np.meshgrid(uppers,guides,indexing='ij');a,g=aa.ravel(),rr.ravel()
    pools={};counts=dict(enumerated=0,height_pitch_inverse=0,unequal_monotone=0,
       point_segment_candidates=0,hip_pitch_candidates=0)
    def retain(key,ids,score,b,start):
        if not len(ids):return
        ids=ids[np.argsort(score[ids],kind='stable')[:4]]
        pools.setdefault(key,[]).extend(dict(a=float(a[i]),b=float(b),r=float(g[i]),start=float(start),score=float(score[i])) for i in ids)
        pools[key]=sorted(pools[key],key=lambda p:(p['score'],p['a']+p['b']))[:8]
    for b in lowers:
        pitch=a>=60*(g+1)+10
        inverse=curve(np.full(len(a),100*R),a,b,g)[3]>=5
        unequal=(abs(a-b)>=5)&(np.maximum(a,b)/np.minimum(a,b)<=1.25+1e-9)
        for start in starts:
            counts['enumerated']+=len(a)
            q0=np.full(len(a),start*R);z0=curve(q0,a,b,g)[1]
            capacity=curve(np.full(len(a),175*R),a,b,g)[1]-z0
            ids=np.flatnonzero(pitch&inverse&unequal&(capacity>=TOTAL))
            counts['height_pitch_inverse']+=len(ids)
            if not len(ids):continue
            lo=q0[ids].copy();hi=np.full(len(ids),175*R)
            for _ in range(32):
                mid=(lo+hi)/2;low=curve(mid,a[ids],b,g[ids])[1]<z0[ids]+TOTAL
                lo=np.where(low,mid,lo);hi=np.where(low,hi,mid)
            ends=(lo+hi)/2
            q=q0[ids,None]+np.linspace(0,1,33)[None,:]*(ends[:,None]-q0[ids,None])
            x,z,jx,jz=curve(q,a[ids,None],b,g[ids,None])
            excursion=np.ptp(x,axis=1);monotone=(jx.min(axis=1)>=-1e-7)|(jx.max(axis=1)<=1e-7)
            counts['unequal_monotone']+=int(np.sum(monotone))
            segment=(b-a[ids])>=220;pulley=(b-a[ids])>=220+60*g[ids]
            counts['point_segment_candidates']+=int(np.sum(monotone&segment))
            counts['hip_pitch_candidates']+=int(np.sum(monotone&pulley))
            lo=q0[ids].copy();hi=ends.copy()
            for _ in range(30):
                mid=(lo+hi)/2;low=curve(mid,a[ids],b,g[ids])[1]<z0[ids]+TOTAL-20
                lo=np.where(low,mid,lo);hi=np.where(low,hi,mid)
            score=np.full(len(a),np.inf);score[ids]=curve((lo+hi)/2,a[ids],b,g[ids])[3]
            for target in TARGETS:
                match=monotone&(abs(excursion-target)<=2.5)
                for family,mask in [('geometry',np.ones(len(ids),bool)),('upper_long',a[ids]>b),('lower_long',a[ids]<b)]:
                    chosen=ids[match&mask]
                    for objective,objective_score in [('force',score),('short',a+b)]:
                        retain(f'w{int(target)}_{family}_{objective}',chosen,objective_score,b,start)
    return pools,counts,dict(L2_mm=uppers.tolist(),L3_mm=lowers.tolist(),guide_ratios=guides.tolist(),
      start_deg=starts.tolist(),end_cap_deg=175,full_bounds_deg=[100,260],
      alpha=0,phi0=0,guide_rb_mm=60,minimum_link_difference_mm=5,maximum_length_ratio=1.25,
      target_lateral_excursion_mm=TARGETS,target_half_band_mm=2.5,
      minimum_guide_pitch_surplus_mm=10,coarse_poses=33)


def main():
    tick=time.perf_counter();pools,counts,domains=grid();cache={};leaders=[]
    for key,rows in sorted(pools.items()):
        viable=[];target=float(key.split('_')[0][1:])
        for row in rows:
            signature=(row['a'],row['b'],row['r'],row['start'])
            if signature not in cache:cache[signature]=evaluate('pending',*signature)
            c=cache[signature];p=c['projection']
            if not(c['full_ideal_inverse'] and c['normal']['monotone_lateral'] and p['recommended_guide_surplus']):continue
            if abs(c['normal']['lateral_excursion_mm']-target)>2.5+1e-6:continue
            if 'segment220' in key and not p['point_segment_clear']:continue
            if 'pitch_circle' in key and not(p['hip_pitch_circle_clear'] and p['knee_pitch_circle_clear']):continue
            viable.append(c)
        if viable:
            metric=(lambda c:(c['force']['max_Jz_m_rad'],c['link_sum_mm'])) if key.endswith('force') else (lambda c:(c['link_sum_mm'],c['force']['max_Jz_m_rad']))
            c=dict(min(viable,key=metric));c['id']=key;leaders.append(c)
    selected=[c for c in leaders if ('upper_long' in c['id'] or 'lower_long' in c['id'])]
    for n,a,b,r in [(25,200,170,2.),(50,200,175,1.875),(75,205,185,1.75),(100,215,175,1.7)]:
        selected.append(evaluate(f'upper{n}',float(a),float(b),r,100.))
    compact=[]
    for c in leaders:
        compact.append(dict(id=c['id'],config=c['config'],projection=c['projection'],
          normal_excursion_mm=c['normal']['lateral_excursion_mm'],normal_drift_mm=c['normal']['signed_drift_mm'],
          hip_peak_Nm=c['force']['peak_45kg_hip_Nm'],hip_ROM_deg=c['force']['hip_ROM_deg'],link_sum_mm=c['link_sum_mm']))
    sources=['unequal_inversion_search.py','curved_path_search.py','inversion_search.py','force_travel_search.py']
    out=dict(schema='camel/unequal-inversion/v2',date='2026-10-14',base_revision=BASE,
       owner_inputs=dict(wheel_radius_mm=200,total_vertical_mm=325,buffers_mm=[20,20],usable_mm=285,
         alpha=0,phi0=0,maximum_length_ratio=1.25,request='Upper may be longer; max/min length <=1.25; curved invertible height paths; no R2 objective'),
       assumptions=dict(full_sweep_deg=[100,260],projection_gap_mm=20,hip_pulley_radius='ra=60r pitch radius only',
          recommended_guide_pitch_surplus_mm=10,normal_excursion_bands='25/50/75/100 +/-2.5 mm; either direction, no normal reversal',
          force_model='110.3625 N vertical equivalent corner load; massless moving links, no spring/inertia',
          physical_scope='Rods overlap in side view at fold; axial staggering/offsets, chassis/outer pulley sizes, structure/contact remain unresolved'),
       search=dict(counts=counts,domains=domains,final_candidates=len(cache),elapsed_s=time.perf_counter()-tick),
       recommended_ids=['upper25','upper50','upper75','upper100'],
       selected=selected,leaders=compact,provenance=dict(python=platform.python_version(),numpy=np.__version__,
          sources={s:hashlib.sha256((APP/s).read_bytes()).hexdigest() for s in sources}))
    path=APP/'docs/unequal-inversion-results.json';path.write_bytes((json.dumps(out,separators=(',',':'),default=json_scalar)+'\n').encode())
    print(json.dumps(dict(counts=counts,selected=len(selected),leaders=len(leaders),bytes=path.stat().st_size,elapsed_s=out['search']['elapsed_s']),indent=2))
    for c in selected:
        print(c['id'],c['config']['L2'],c['config']['L3'],c['config']['qab'],
          c['normal']['signed_drift_mm'],c['force']['peak_45kg_hip_Nm'],c['projection']['wheel_to_hip_pitch_circle_gap_mm'])


if __name__=='__main__':main()
