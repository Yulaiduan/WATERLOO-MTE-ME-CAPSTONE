"""Search ratio-generated curved leg paths with explicit lateral travel bands.

Run from app: .venv/Scripts/python.exe curved_path_search.py
Inputs: alpha=phi0=0, Rw200mm,325mm total vertical stroke,20mm end reserves,
25/50/75/100mm normal lateral excursion targets +/-2.5mm, declared grid below.
Outputs: docs/curved-path-results.json with geometry/force/control metrics and
source hashes. Uses pinned NumPy/SciPy. Limits: 1DOF allowed motion, not measured
compliance, collision-free inversion, spring choice or hardware/motor rating.
R2 and a fixed-line corridor are not objectives or acceptance conditions.
"""
from pathlib import Path
import hashlib
import json
import math
import platform
import time
import numpy as np
from scipy.optimize import brentq
from inversion_search import curve, inverse_height, R
from force_travel_search import force_metrics, json_scalar, F45

APP=Path(__file__).resolve().parent
TARGETS=[25.,50.,75.,100.]
TOTAL=325.;TOL=2.5


def extrema(fn, lo, hi):
    qs=np.linspace(lo,hi,129);v=fn(qs);points=[lo,hi]
    if np.max(abs(v))<1e-10:return np.array([lo,hi])
    for a,b,fa,fb in zip(qs[:-1],qs[1:],v[:-1],v[1:]):
        if abs(fa)<1e-10:points.append(float(a))
        if fa*fb<0:points.append(brentq(lambda q:float(fn(q)),a,b,xtol=1e-13))
    return np.unique(points)


def second(q,a,b,r):
    t=q-math.pi;k=r-1
    return -a*np.cos(t)+k*k*b*np.cos(k*t),-a*np.sin(t)-k*k*b*np.sin(k*t)


def path_metrics(a,b,r,start,end):
    """Continuous extrema plus dense integrals, mm/rad units; no line-fit score."""
    lo,hi=start*R,end*R
    fn=lambda q:curve(q,a,b,r)
    qx=extrema(lambda q:fn(q)[2],lo,hi);xx=fn(qx)[0]
    qr=extrema(lambda q:fn(q)[0]*fn(q)[2]+fn(q)[1]*fn(q)[3],lo,hi)
    xr,zr=fn(qr)[:2]
    qj=extrema(lambda q:second(q,a,b,r)[1],lo,hi)
    jz=fn(qj)[3]
    qh=extrema(lambda q:second(q,a,b,r)[0],lo,hi)
    jx=fn(qh)[2]
    qslope=extrema(lambda q:second(q,a,b,r)[0]*fn(q)[3]-fn(q)[2]*second(q,a,b,r)[1],lo,hi)
    slope=fn(qslope)[2]/fn(qslope)[3]
    q=np.linspace(lo,hi,2001);x,z,dx,dz=fn(q)
    x0,z0=float(x[0]),float(z[0]);xe,ze=float(x[-1]),float(z[-1])
    turns=[float(t/R) for t in qx if lo+1e-8<t<hi-1e-8]
    return dict(vertical_mm=ze-z0,signed_drift_mm=xe-x0,lateral_excursion_mm=float(np.ptp(xx)),
       max_from_start_mm=float(np.max(abs(xx-x0))),lateral_variation_mm=float(np.sum(abs(np.diff(xx)))),
       turning_q_deg=turns,monotone_lateral=len(turns)==0,
       x_bounds_mm=[float(np.min(xx)),float(np.max(xx))],z_bounds_mm=[z0,ze],
       min_hip_distance_mm=float(np.min(np.hypot(xr,zr))),
       min_Jz_mm_rad=float(np.min(jz)),max_Jz_mm_rad=float(np.max(jz)),
       max_abs_Jx_mm_rad=float(np.max(abs(jx))),
       slope_range=[float(np.min(slope)),float(np.max(slope))],
       tangent_range_deg=[float(np.degrees(np.arctan(np.min(slope)))),float(np.degrees(np.arctan(np.max(slope))))],
       arc_length_mm=float(np.trapezoid(np.hypot(dx,dz),q)),
       samples=[dict(q_deg=float(q[i]/R),x_mm=float(x[i]),z_mm=float(z[i]),
          Jx_mm_rad=float(dx[i]),Jz_mm_rad=float(dz[i])) for i in np.linspace(0,2000,31).astype(int)])


def candidate(name,a,b,r,start):
    z0=float(curve(start*R,a,b,r)[1]);end=inverse_height(z0+TOTAL,a,b,r,0,(start,175))/R
    normal=path_metrics(a,b,r,start,end)
    full_bounds=[min(100.,start),max(260.,360-start)]
    full=path_metrics(a,b,r,*full_bounds)
    f=force_metrics(a,b,r,start,end);lo,hi=f['usable_angle_bounds_deg']
    useful=path_metrics(a,b,r,lo,hi)
    f['max_Jz_m_rad']=useful['max_Jz_mm_rad']/1000
    f['min_Jz_m_rad']=useful['min_Jz_mm_rad']/1000
    f['peak_45kg_hip_Nm']=F45*f['max_Jz_m_rad']
    f['min_force_per_hip_N_Nm']=1/f['max_Jz_m_rad']
    f['constant_vertical_speed_0p25m_s_peak_hip_rad_s']=.25/f['min_Jz_m_rad']
    f['side_load_peak_Nm']={}
    for mu in [-.3,0,.3]:
        q=extrema(lambda q:second(q,a,b,r)[1]+mu*second(q,a,b,r)[0],lo*R,hi*R)
        _,_,jx,jz=curve(q,a,b,r)
        f['side_load_peak_Nm'][str(mu)]=float(F45*np.max(abs(jz+mu*jx))/1000)
    # Exact robust sign-unknown bound max(|Jz|+0.3|Jx|), partitioning at Jx zeros.
    split=extrema(lambda q:curve(q,a,b,r)[2],lo*R,hi*R)
    robust=[]
    for left,right in zip(split[:-1],split[1:]):
        sign=float(np.sign(curve((left+right)/2,a,b,r)[2]))
        q=extrema(lambda q:second(q,a,b,r)[1]+.3*sign*second(q,a,b,r)[0],left,right)
        _,_,jx,jz=curve(q,a,b,r);robust.extend((abs(jz)+.3*abs(jx)).tolist())
    f['robust_abs_Fx_over_Fz_0p3_peak_Nm']=F45*max(robust)/1000
    f['samples']=f['samples'][::2]
    return dict(id=name,config=dict(L2=a,L3=b,qab=r,ra=60*r,rb=60,rw=200,alpha=0,phi0=0,
       qcd=1,qef=1,te=start,tc=end),normal=normal,useful=useful,full=full,force=f,
       link_sum_mm=a+b,link_mismatch=abs(a/b-1),guide_pitch_pass=a>60*(r+1),
       normal_coplanar220_pass=normal['min_hip_distance_mm']>=220-1e-7,
       full_coplanar220_pass=full['min_hip_distance_mm']>=220-1e-7,
       full_ideal_inverse=full['min_Jz_mm_rad']>=5-1e-7,
       fold_guard_deg=180-end,full_bounds_deg=full_bounds,
       scope='Ideal wheel-centre path; no actual stiffness or physical inversion claim')


def grid():
    guides=np.unique(np.r_[np.round(np.arange(1.3,2.60001,.005),8),5/3,1.75,1.8,2])
    ratios=np.round(np.arange(.85,1.15001,.025),8)
    scales=np.arange(150.,400.01,5);starts=np.arange(100.,140.01,2.5)
    gg,rr=np.meshgrid(guides,ratios,indexing='ij');g,lr=gg.ravel(),rr.ravel()
    pools={};counts=dict(enumerated=0,height_pitch_inverse=0,monotone_lateral=0,
       normal220=0,target_pass={str(int(t)):0 for t in TARGETS})
    def save(key, ids, score, a,b,start,ends):
        if not len(ids):return
        ids=ids[np.argsort(score[ids],kind='stable')[:6]]
        pools.setdefault(key,[]).extend([dict(a=float(a[i]),b=float(b),r=float(g[i]),start=float(start),
          score=float(score[i])) for i in ids])
        pools[key]=sorted(pools[key],key=lambda x:(x['score'],x['a']+x['b']))[:10]
    for b in scales:
        a=lr*b;pitch=a>60*(g+1)
        fullq=np.linspace(100*R,260*R,33)[None,:]
        fullj=curve(fullq,a[:,None],b,g[:,None])[3].min(axis=1)
        for start in starts:
            counts['enumerated']+=len(g)
            q0=np.full(len(g),start*R);xs,zs,_,_=curve(q0,a,b,g)
            cap=curve(np.full(len(g),175*R),a,b,g)[1]
            ids=np.flatnonzero(pitch&(fullj>=5)&(cap-zs>=TOTAL))
            counts['height_pitch_inverse']+=len(ids)
            if not len(ids):continue
            lo=q0[ids].copy();hi=np.full(len(ids),175*R)
            for _ in range(33):
                mid=(lo+hi)/2;low=curve(mid,a[ids],b,g[ids])[1]<zs[ids]+TOTAL
                lo=np.where(low,mid,lo);hi=np.where(low,hi,mid)
            ends=q0.copy();ends[ids]=(lo+hi)/2
            q=q0[ids,None]+np.linspace(0,1,33)[None,:]*(ends[ids,None]-q0[ids,None])
            x,z,jx,jz=curve(q,a[ids,None],b,g[ids,None]);exc=np.ptp(x,axis=1)
            mono=(jx.min(axis=1)>=-1e-7)|(jx.max(axis=1)<=1e-7)
            clear=np.hypot(x,z).min(axis=1)>=220
            counts['monotone_lateral']+=int(np.sum(mono));counts['normal220']+=int(np.sum(mono&clear))
            # Jz increases on normal phase-zero100..175 for this positive-ratio domain.
            left=q0[ids].copy();right=ends[ids].copy()
            for _ in range(30):
                mid=(left+right)/2;low=curve(mid,a[ids],b,g[ids])[1]<zs[ids]+TOTAL-20
                left=np.where(low,mid,left);right=np.where(low,right,mid)
            peak=np.full(len(g),np.inf);peak[ids]=curve((left+right)/2,a[ids],b,g[ids])[3]
            for target in TARGETS:
                match=mono&(abs(exc-target)<=TOL)
                counts['target_pass'][str(int(target))]+=int(np.sum(match))
                for tier,tiermask in [('equal',abs(lr[ids]-1)<1e-8),('near5',abs(lr[ids]-1)<=.05+1e-8)]:
                    for package,pmask in [('geometry',np.ones(len(ids),bool)),('normal220',clear)]:
                        chosen=ids[match&tiermask&pmask]
                        for objective,score in [('force',peak),('short',a+b)]:
                            save(f'w{int(target)}_{tier}_{package}_{objective}',chosen,score,a,b,start,ends)
    domains=dict(L3_mm=scales.tolist(),L2_over_L3=ratios.tolist(),guide_ratio=guides.tolist(),
       starts_deg=starts.tolist(),normal_cap_deg=175,full_bounds_deg=[100,260],rb_mm=60,
       coarse_poses=33,target_tolerance_mm=TOL)
    return pools,counts,domains


def main():
    t=time.perf_counter();pools,counts,domains=grid();cache={};leaders=[]
    for key,rows in sorted(pools.items()):
        candidates=[];target=float(key.split('_')[0][1:])
        for p in rows:
            signature=(p['a'],p['b'],p['r'],p['start'])
            if signature not in cache:cache[signature]=candidate('pending',*signature)
            c=cache[signature]
            if abs(c['normal']['lateral_excursion_mm']-target)>TOL+1e-6:continue
            if not (c['normal']['monotone_lateral'] and c['full_ideal_inverse'] and c['guide_pitch_pass']):continue
            if 'normal220' in key and not c['normal_coplanar220_pass']:continue
            candidates.append(c)
        if not candidates:continue
        winner=min(candidates,key=lambda c:((c['force']['max_Jz_m_rad'],c['link_sum_mm']) if key.endswith('force')
                                            else (c['link_sum_mm'],c['force']['max_Jz_m_rad'])))
        leaders.append(dict(bucket=key,case=winner))
    selected=[]
    for target in TARGETS:
        for suffix in ['equal_geometry_force','near5_geometry_force','equal_normal220_force','equal_geometry_short']:
            key=f'w{int(target)}_{suffix}'
            row=next((r for r in leaders if r['bucket']==key),None)
            if row:
                c=dict(row['case']);c['id']=key;selected.append(c)
    # Simple identical-link references isolate guide ratio without changing size or start.
    for r in [1.5,5/3,1.75,1.8,1.9,2,2.2]:
        try:selected.append(candidate(f'ratio300_{r:.6g}',300.,300.,r,100.))
        except ValueError:pass
    for target,a,r in [(25,185,1.9),(50,190,1.8),(75,200,1.7),(100,205,1.6)]:
        selected.append(candidate(f'example{target}',float(a),float(a),r,100.))
    for a,r,start in [(180,1.9,95),(185,1.8,95),(190,1.7,95),(195,1.6,95),(185,1.8,90)]:
        try:selected.append(candidate(f'ROM_sensitivity_{a}_{r}_{start}',float(a),float(a),r,float(start)))
        except ValueError:pass
    for row in leaders:
        c=row['case']
        compact={k:v for k,v in c.items() if k not in ['normal','useful','full','force']}
        compact['normal']={k:c['normal'][k] for k in ['lateral_excursion_mm','signed_drift_mm','min_hip_distance_mm']}
        compact['force']={k:c['force'][k] for k in ['max_Jz_m_rad','peak_45kg_hip_Nm','hip_ROM_deg']}
        row['case']=compact
    sources=['curved_path_search.py','inversion_search.py','force_travel_search.py']
    data=dict(schema='camel/curved-lateral-path/v1',date='2026-10-14',base_revision='93fed9fa90759fd6762d1b78f6fce8c6c92920a4',
      owner_inputs=dict(total_vertical_mm=325,lateral_targets_mm=TARGETS,wheel_radius_mm=200,
         cancelled_method='R2 and fixed15-degree corridor cancelled before publication'),
      assumptions=dict(buffers_mm=[20,20],usable_vertical_mm=285,alpha=0,phi0=0,
         lateral_target='Peak-to-peak x excursion over NORMAL325mm stroke, +/-2.5mm band; monotone lateral normal path',
         direction='Either signed lateral direction retained; full phase-zero endpoints have zero net drift',
         packaging='Normal220mm exclusion separate; all near-equal full coplanar sweeps fail',
         compliance='Allowed coupled movement only; actual stiffness requires spring/controller/contact and geometric stiffness',
         objective='Hard travel/inverse/pitch/lateral-band/monotonicity/tier/package filters; separate peak-force and size leaders; no weighted score'),
      search=dict(counts=counts,domains=domains,final_candidates=len(cache),elapsed_s=time.perf_counter()-t),
      selected=selected,leaders=leaders,provenance=dict(python=platform.python_version(),numpy=np.__version__,
         sources={p:hashlib.sha256((APP/p).read_bytes()).hexdigest() for p in sources}))
    (APP/'docs/curved-path-results.json').write_bytes((json.dumps(data,separators=(',',':'),default=json_scalar)+'\n').encode())
    print(json.dumps(dict(counts=counts,selected=len(selected),leaders=len(leaders),elapsed_s=data['search']['elapsed_s']),indent=2))
    for c in selected:print(c['id'],c['config']['L2'],c['config']['L3'],c['config']['qab'],c['normal']['lateral_excursion_mm'],c['force']['peak_45kg_hip_Nm'])


if __name__=='__main__':main()
