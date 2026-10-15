"""Compare equal, upper-long and reverse 1:1.25 legs for static torque RMS.

Run from app: .venv/Scripts/python.exe scripts/compare_rms_links.py
Inputs: Jonathan phase-zero geometry in mm/deg, 110.3625 N vertical force,
325 mm total /285 mm useful stroke, 20+20 mm assumed reserves; bounded grid
declared below. Outputs docs/rms-link-results.json with selected cases,
counts, hashes, quadrature checks and height/time-weighted static RMS in Nm.
Requires existing NumPy/SciPy pins. Limits: sampled bounded search, not global
optima, physical clearance, loaded dynamics, thermal ratings or spring sizing.
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from scipy.integrate import quad, simpson
from scipy.optimize import brentq

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
from curved_path_search import candidate, curve, R, json_scalar
from force_travel_search import F45

FAMILIES={'equal':1.,'upper125':1.25,'lower125':.8}


def timed(c,n=2001):
    """Quasi-static torque along common unit-time quintic height; no inertia."""
    p=c['config'];a,b,r=p['L2'],p['L3'],p['qab']
    lo,hi=np.array(c['force']['usable_angle_bounds_deg'])*R
    t=np.linspace(0,1,n);s=10*t**3-15*t**4+6*t**5
    z0=float(curve(lo,a,b,r)[1]);target=z0+285*s
    left=np.full(n,lo);right=np.full(n,hi)
    for _ in range(46):
        mid=(left+right)/2;low=curve(mid,a,b,r)[1]<target
        left=np.where(low,mid,left);right=np.where(low,right,mid)
    q=(left+right)/2;tau=F45*curve(q,a,b,r)[3]/1000
    return dict(quintic_static_rms_hip_Nm=float(np.sqrt(simpson(tau*tau,x=t))),
        samples=[dict(time_fraction=float(t[i]),height_mm=float(285*s[i]),
          q_deg=float(q[i]/R),torque_45kg_Nm=float(tau[i])) for i in np.linspace(0,n-1,61).astype(int)])


def enrich(name,a,b,r,start):
    c=candidate(name,a,b,r,start)
    c['guide_surplus_mm']=a-60*(r+1)
    c['assumed_guide10_pass']=c['guide_surplus_mm']>=10-1e-8
    c['length_ratio']=max(a,b)/min(a,b)
    lo,hi=np.array(c['force']['usable_angle_bounds_deg'])*R
    integrand=lambda q:(float(curve(q,a,b,r)[3])/1000)**3
    exact=F45*np.sqrt(quad(integrand,lo,hi,epsabs=1e-13,epsrel=1e-12)[0]/.285)
    c['rms_quad_hip_Nm']=float(exact)
    c['rms_quad_relative_knee_Nm']=float(exact/r)
    c['rms_trapezoid_error_Nm']=abs(exact-c['force']['rms_45kg_hip_uniform_height_Nm'])
    c['timed']=timed(c)
    c['timed_convergence_error_Nm']=abs(c['timed']['quintic_static_rms_hip_Nm']-timed(c,4001)['quintic_static_rms_hip_Nm'])
    for side in ['normal','useful','full','force']:
        c[side]['samples']=c[side]['samples'][::3]
    c['timed']['samples']=c['timed']['samples'][::5]
    return c


def grid():
    guides=np.round(np.arange(1.2,2.6001,.01),8)
    totals=np.arange(350.,600.1,5.);starts=np.arange(100.,140.1,5.)
    caps=[165.,170.,175.];pools={};counts={'enumerated':0,'height_guide_inverse':0,'lateral_band':0}
    for family,lr in FAMILIES.items():
      for S in totals:
        b=S/(1+lr);a=S-b;r=guides
        fullj=curve(np.linspace(100*R,260*R,65)[None,:],a,b,r[:,None])[3].min(axis=1)
        for start in starts:
          q0=np.full(len(r),start*R);xs,zs,*_=curve(q0,a,b,r)
          for cap in caps:
            counts['enumerated']+=len(r)
            valid=(a-60*(r+1)>=10-1e-8)&(fullj>=5)&(curve(cap*R,a,b,r)[1]-zs>=325)
            ids=np.flatnonzero(valid);counts['height_guide_inverse']+=len(ids)
            if not len(ids):continue
            rr=r[ids];zstart=zs[ids]
            def invert(target):
                left=np.full(len(ids),start*R);right=np.full(len(ids),cap*R)
                for _ in range(36):
                    mid=(left+right)/2;low=curve(mid,a,b,rr)[1]<target
                    left=np.where(low,mid,left);right=np.where(low,right,mid)
                return (left+right)/2
            qe=invert(zstart+325);ql=invert(zstart+20);qh=invert(zstart+305)
            q=q0[ids,None]+np.linspace(0,1,65)*(qe-q0[ids])[:,None]
            x,z,jx,jz=curve(q,a,b,rr[:,None]);exc=np.ptp(x,axis=1)
            mono=(jx.min(axis=1)>=-1e-8)|(jx.max(axis=1)<=1e-8)
            qu=ql[:,None]+np.linspace(0,1,65)*(qh-ql)[:,None]
            ju=curve(qu,a,b,rr[:,None])[3]/1000
            rms=F45*np.sqrt(simpson(ju**3,x=qu,axis=1)/.285)
            for target in [25,50,75,100]:
                chosen=np.flatnonzero(mono&(abs(exc-target)<=2.5))
                counts['lateral_band']+=len(chosen)
                key=f'{family}_{int(cap)}_{target}'
                rows=[dict(score=float(rms[i]),a=float(a),b=float(b),r=float(rr[i]),start=float(start))
                      for i in chosen[np.argsort(rms[chosen],kind='stable')[:8]]]
                pools[key]=sorted(pools.get(key,[])+rows,key=lambda p:(p['score'],p['a']+p['b']))[:12]
    return pools,counts,dict(total_length_mm=[350,600,5],upper_over_lower=FAMILIES,
      guide_ratio=[1.2,2.6,.01],starts_deg=starts.tolist(),caps_deg=caps,
      total_height_mm=325,buffers_mm=[20,20],lateral_targets_mm=[25,50,75,100],tolerance_mm=2.5,
      min_full_Jz_mm_rad=5,full_domain_deg=[100,260],rb_mm=60,guide_surplus_mm=10,
      coarse_poses=65,pool_per_bucket=12,objective='height-weighted static hip RMS; no weighted score')


def main():
    selected=[];groups={};pools,counts,domain=grid();leaders=[];cache={}
    for key,rows in sorted(pools.items()):
        family,cap,target=key.split('_');valid=[]
        for p in rows:
            sig=tuple(p[k] for k in ['a','b','r','start'])
            if sig not in cache:cache[sig]=enrich('pending',*sig)
            c=cache[sig]
            if (c['config']['tc']<=float(cap)+1e-7 and c['assumed_guide10_pass'] and c['full_ideal_inverse']
                and c['normal']['monotone_lateral'] and abs(c['normal']['lateral_excursion_mm']-float(target))<=2.5+1e-7):valid.append(c)
        if valid:
            winner=dict(min(valid,key=lambda c:(c['rms_quad_hip_Nm'],c['link_sum_mm'])))
            winner['id']=key;selected.append(winner);leaders.append(dict(bucket=key,case_id=key))
    groups['grid']=[c['id'] for c in selected]
    # Fixed total length and start; solve the guide for exactly +50 mm lateral.
    groups['fixed450_50']=[];groups['fixed450_r2']=[]
    for family,lr in FAMILIES.items():
        b=450/(1+lr);a=450-b
        def drift(r):return candidate('control',a,b,r,100)['normal']['signed_drift_mm']-50
        r=brentq(drift,1.6,2.1,xtol=1e-13)
        c=enrich(f'fixed450_{family}_50',a,b,r,100);selected.append(c);groups['fixed450_50'].append(c['id'])
        c=enrich(f'fixed450_{family}_r2',a,b,2.,100);selected.append(c);groups['fixed450_r2'].append(c['id'])
    groups['rounded_reverse']=[]
    for name,a,b,r in [('reverse180_225',180.,225.,1.7),('reverse200_250',200.,250.,12/7)]:
        c=enrich(name,a,b,r,100);selected.append(c);groups['rounded_reverse'].append(c['id'])
    old=json.loads((APP/'docs/equal-link-comparison.json').read_text())
    groups['previous_examples']=[]
    for ref in old['selected']:
        if ref['id'] not in [f'{f}{n}' for f in ['equal','upper'] for n in [25,50,75,100]]:continue
        p=ref['config'];c=enrich('previous_'+ref['id'],p['L2'],p['L3'],p['qab'],p['te'])
        selected.append(c);groups['previous_examples'].append(c['id'])
    sources=['scripts/compare_rms_links.py','curved_path_search.py','inversion_search.py','force_travel_search.py','docs/equal-link-comparison.json']
    d=dict(schema='camel/rms-link-comparison/v1',date='2026-10-15',base_revision='c92880d618e778802d4d698128096efa9e568202',
      interpretation='Owner r1=upper L2, r2=lower L3; reverse lower/upper=1.25, unrelated to guide ratio',
      force_N=F45,scope='Massless moving links, ideal static endpoint load; no springs/inertia/losses or physical clearance certification',
      weighting=dict(height='Uniform useful vertical height; equals time RMS at constant vertical speed without dwell',
        quintic='Static torque sampled on common smooth quintic useful height, zero dwell; normalized time; no dynamic inertia',
        actuator='Direct hip equivalent throughout; equivalent knee magnitude is hip/guide; motor gearing separate'),
      search=dict(counts=counts,domain=domain,dense_finalists=len(cache)),selected=selected,groups=groups,leaders=leaders,
      checks=dict(max_height_quadrature_error_Nm=max(c['rms_trapezoid_error_Nm'] for c in selected),
        max_quintic_convergence_error_Nm=max(c['timed_convergence_error_Nm'] for c in selected)),
      provenance=dict(sources={p:hashlib.sha256((APP/p).read_bytes()).hexdigest() for p in sources}))
    assert d['checks']['max_height_quadrature_error_Nm']<1e-4
    assert d['checks']['max_quintic_convergence_error_Nm']<1e-7
    (APP/'docs/rms-link-results.json').write_bytes((json.dumps(d,separators=(',',':'),default=json_scalar)+'\n').encode())
    print(json.dumps(dict(counts=counts,cases=len(selected),checks=d['checks']),indent=2))
    for c in selected:
        if c['id'].endswith('_175_50') or c['id'].startswith('fixed450'):
            print(c['id'],c['config'],c['normal']['signed_drift_mm'],c['rms_quad_hip_Nm'],c['timed']['quintic_static_rms_hip_Nm'],c['force']['peak_45kg_hip_Nm'])


if __name__=='__main__':main()
