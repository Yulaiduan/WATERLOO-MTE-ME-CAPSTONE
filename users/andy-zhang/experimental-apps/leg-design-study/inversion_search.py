"""Search alpha-zero, equal/near-equal guided legs for tilted straight paths.

Run: .venv/Scripts/python.exe inversion_search.py --output docs/inversion-path-results.json
Inputs: documented mm/degree geometry grid, screenshot phase0/alpha0, 200 mm
wheel radius, 300/325/350 mm total vertical windows with 20 mm end reserves.
Outputs: compact selected evidence JSON, search counts and progress on stdout.
Requires NumPy/SciPy. Uses exact V2 geometry over angles beyond the old profile
validator; original model.js/generalized_leg.py remain unchanged.
Limitations: planar kinematic screening, ideal guide, no contact, spring/motor
rating, belt hardware, axial/chassis packaging or canonical robot validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import time
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

APP = Path(__file__).resolve().parent
R = math.pi / 180
BASE = '865b5f14f27e945cebd4fa40ba41f6548e18c2d1'


def curve(q, l2, l3, ratio, phase=0.):
    """V2 wheel-centre coordinates/derivatives, mm and mm/rad; alpha is zero."""
    q = np.asarray(q)
    t = q - math.pi
    k = ratio - 1
    a = phase * R - k * t
    x = l2 * np.cos(t) - l3 * np.cos(a)
    z = l2 * np.sin(t) - l3 * np.sin(a)
    dx = -l2 * np.sin(t) - k * l3 * np.sin(a)
    dz = l2 * np.cos(t) + k * l3 * np.cos(a)
    return x, z, dx, dz


def inverse_height(z, l2, l3, ratio, phase=0., bounds=(100., 260.)):
    return brentq(lambda q: float(curve(q, l2, l3, ratio, phase)[1])-z,
                  bounds[0]*R, bounds[1]*R, xtol=1e-13)


def metrics(l2, l3, ratio, start, end, phase=0., samples=2001):
    q = np.linspace(start*R, end*R, samples)
    if start <= 180 <= end and phase == 0:
        q = np.unique(np.r_[q, math.pi])
    x, z, dx, dz = curve(q, l2, l3, ratio, phase)
    vx, vz = x[-1]-x[0], z[-1]-z[0]
    chord = math.hypot(vx, vz)
    nx, nz = vz/chord, -vx/chord
    error = (x-x[0])*nx+(z-z[0])*nz
    tilt = math.degrees(math.atan2(vx, vz))
    tangents = np.degrees(np.arctan2(dx, dz))
    # TLS is explicitly uniform vertical travel rather than a hidden angle weight.
    heights = np.linspace(z[0], z[-1], samples)
    xx = np.interp(heights, z, x) if np.min(dz)>0 else x
    zz = heights if np.min(dz)>0 else z
    cov = np.cov(xx, zz, bias=True)
    tls = .5*math.atan2(2*cov[0, 1], cov[1, 1]-cov[0, 0])
    tls_error = (xx-np.mean(xx))*math.cos(tls)-(zz-np.mean(zz))*math.sin(tls)
    radius = np.hypot(x, z)
    return dict(vertical_mm=float(vz), lateral_mm=float(vx), chord_mm=chord,
                chord_tilt_deg=tilt, tls_tilt_deg=math.degrees(tls),
                max_chord_error_mm=float(np.max(np.abs(error))),
                chord_error_percent=float(np.max(np.abs(error))/chord*100),
                max_tls_error_mm=float(np.max(np.abs(tls_error))),
                tangent_min_deg=float(np.min(tangents)), tangent_max_deg=float(np.max(tangents)),
                tangent_spread_deg=float(np.ptp(tangents)),
                min_vertical_jacobian_mm_rad=float(np.min(dz)),
                min_full_jacobian_mm_rad=float(np.min(np.hypot(dx, dz))),
                minimum_hip_distance_mm=float(np.min(radius)),
                wheel_hip_margin_mm=float(np.min(radius)-200),
                projected_clearance_pass=bool(np.min(radius)>=220-1e-7),
                crosses_hip_height=bool(z[0]<0<z[-1]),
                below_extent_mm=float(max(0., -z[0])), above_extent_mm=float(max(0., z[-1])),
                endpoint_heights_mm=[float(z[0]), float(z[-1])])


def case(name, l2, l3, ratio, start, end, phase=0., kind='normal_branch'):
    config = dict(L2=float(l2), L3=float(l3), qab=float(ratio), alpha=0., phi0=float(phase),
                  ra=60*float(ratio), rb=60., rc=35., rd=35., re=35., rf=35., rw=200.,
                  qcd=1., qef=1., K=0., beta=13.5, Fy=100., Fz=100.,
                  m1=10., m2=0., m3=0., m5=0., m6=0., g=9.81,r5I=35.,
                  loadMode='yz',Tab0=0.,Tcd0=0.,Tef0=0.,
                  te=float(start), tc=float(end))
    met = metrics(l2, l3, ratio, start, end, phase)
    # Mathematical full inversion means the complete q100..260 envelope, unless
    # phase requires a shifted symmetric range about its fold point.
    fold = 180+phase/2 if abs(ratio-2)<1e-12 else 180.
    envelope = (fold-80, fold+80)
    full = metrics(l2, l3, ratio, *envelope, phase)
    q = np.linspace(start*R, end*R, 61)
    x, z, dx, dz = curve(q, l2, l3, ratio, phase)
    t3 = phase+(math.pi-q)*(ratio-1)/R
    full_q = np.linspace(envelope[0]*R, envelope[1]*R, 81)
    fx, fz, fdx, fdz = curve(full_q, l2, l3, ratio, phase)
    met['usable_mm'] = max(0., met['vertical_mm']-40)
    full['angle_bounds_deg'] = list(envelope)
    rows = [dict(q_deg=float(a/R), x_mm=float(b), z_mm=float(c),
                 tangent_deg=float(math.degrees(math.atan2(d, e))),
                 tau_hip_Nm=float(-(100*d+100*e)/1000),
                 tau_relative_knee_Nm=float((100*d+100*e)/1000/ratio),
                 theta3_deg=float(f)) for a, b, c, d, e, f in zip(q, x, z, dx, dz, t3)]
    return dict(id=name, kind=kind, config=config, metrics=met, full_inversion=full,
                samples=rows, full_samples=[dict(q_deg=float(a/R),x_mm=float(b),z_mm=float(c),
                    tangent_deg=float(math.degrees(math.atan2(d,e))))
                    for a,b,c,d,e in zip(full_q,fx,fz,fdx,fdz)],
                link_difference_mm=abs(l2-l3), link_ratio=l2/l3,
                guide_reduced_ratio=_rational(ratio))


def _rational(value):
    from fractions import Fraction
    f = Fraction(float(value)).limit_denominator(120)
    return dict(numerator=f.numerator, denominator=f.denominator,
                value=float(f), approximation_error=abs(float(f)-value),
                note='Same-pitch ratio illustration only; tooth counts/wrap/strength are not selected.')


def _vector_metrics(l2, l3, r, qs, qe, count=33):
    q = qs[:, None]+(qe-qs)[:, None]*np.linspace(0,1,count)
    x,z,dx,dz = curve(q,l2[:,None],l3,r[:,None])
    vx,vz = x[:,-1]-x[:,0],z[:,-1]-z[:,0]
    chord = np.hypot(vx,vz)
    tilt = np.degrees(np.arctan2(vx,vz))
    errors=((x-x[:,0,None])*vz[:,None]-(z-z[:,0,None])*vx[:,None])/chord[:,None]
    tangent=np.degrees(np.arctan2(dx,dz))
    return dict(tilt=tilt,error=np.max(abs(errors),axis=1),
                relative=np.max(abs(errors),axis=1)/chord*100,
                tangent_spread=np.ptp(tangent,axis=1),
                min_j=np.min(dz,axis=1),min_radius=np.min(np.hypot(x,z),axis=1),
                below=-z[:,0],above=z[:,-1])


def search(quick=False):
    """Vectorized deterministic grid; preserve counts and compact leader pools."""
    guides = np.unique(np.r_[np.round(np.arange(1.4,2.60001,.0025 if not quick else .04),8),5/3,1.75,1.8,2.])
    ratios = np.unique(np.r_[np.round(np.arange(.85,1.15001,.005 if not quick else .025),8),1.])
    scales = np.unique(np.r_[np.arange(200,450.1,10 if not quick else 50),275,325,375,425])
    starts = np.arange(100.,120.1,5.)
    targets = [300.,325.,350.]
    fractions = [.2,.35,.5,.65,.8]
    gg,rr=np.meshgrid(guides,ratios,indexing='ij');g=gg.ravel();lr=rr.ravel()
    pools={};counts=dict(normal_grid=0,inversion_grid=0,normal_geometry_pass=0,
      normal_target_angle=0,normal_clearance_pass=0,normal_quality_pass=0,
      inversion_geometry_pass=0,transition_target_angle=0,transition_quality_pass=0,full_projected_clearance_pass=0)

    def add_pool(key, ids, data, l3, qs, qe, target, family):
        if not len(ids): return
        # Straightness first, then tangent consistency, then physical scale.
        rank=np.lexsort((np.full(len(ids),l3),data['tangent_spread'][ids],data['error'][ids]))[:8]
        for j in ids[rank]:
            item=dict(L2=float(lr[j]*l3),L3=float(l3),ratio=float(g[j]),
                      start=float(qs[j]/R),end=float(qe[j]/R),target=target,family=family,
                      coarse_error=float(data['error'][j]),coarse_spread=float(data['tangent_spread'][j]),
                      coarse_tilt=float(data['tilt'][j]),coarse_radius=float(data['min_radius'][j]))
            pools.setdefault(key,[]).append(item)
        pools[key]=sorted(pools[key],key=lambda a:(a['coarse_error'],a['coarse_spread'],a['L2']+a['L3']))[:32]

    for scale_index,l3 in enumerate(scales):
        l2=lr*l3
        pitch=l2>60*(g+1)
        full_regular=curve(np.full(len(g),100*R),l2,l3,g)[3]>=5
        for start in starts:
            qs=np.full(len(g),start*R)
            xs,zs,_,js=curve(qs,l2,l3,g)
            cap=curve(np.full(len(g),175*R),l2,l3,g)[1]
            for target in targets:
                counts['normal_grid']+=len(g)
                valid=pitch & (js>=5) & ((cap-zs)>=target)
                ids=np.flatnonzero(valid);counts['normal_geometry_pass']+=len(ids)
                if not len(ids):continue
                lo=qs[ids].copy();hi=np.full(len(ids),175*R)
                for _ in range(28):
                    mid=(lo+hi)/2;zm=curve(mid,l2[ids],l3,g[ids])[1]
                    lower=zm<zs[ids]+target;lo=np.where(lower,mid,lo);hi=np.where(lower,hi,mid)
                qe=qs.copy();qe[ids]=(lo+hi)/2
                xe,ze,_,_=curve(qe[ids],l2[ids],l3,g[ids])
                chord_tilt=np.degrees(np.arctan2(xe-xs[ids],ze-zs[ids]))
                ids=ids[(abs(chord_tilt)>=10)&(abs(chord_tilt)<=15)]
                counts['normal_target_angle']+=len(ids)
                if not len(ids):continue
                data0=_vector_metrics(l2[ids],l3,g[ids],qs[ids],qe[ids])
                # Map evaluated arrays back to grid identifiers for leader storage.
                data={k:np.full(len(g),np.nan) for k in data0}
                for k in data: data[k][ids]=data0[k]
                regular=ids[data['min_j'][ids]>=5]
                clear=regular[(data['min_radius'][regular]>=220)&full_regular[regular]]
                quality=clear[(data['relative'][clear]<=2)&(data['tangent_spread'][clear]<=15)]
                counts['normal_clearance_pass']+=len(clear);counts['normal_quality_pass']+=len(quality)
                for tol,label in [(1e-8,'equal'),(.050001,'within5'),(.100001,'within10'),(.150001,'within15')]:
                    selected=clear[abs(lr[clear]-1)<=tol]
                    add_pool(f'{label}_{int(target)}',selected,data,l3,qs,qe,target,'normal_branch')
                add_pool(f'compact_{int(target)}',quality[(l2[quality]+l3)<=700],data,l3,qs,qe,target,'normal_branch')
                add_pool(f'size700_{int(target)}',clear[(l2[clear]+l3)<=700],data,l3,qs,qe,target,'normal_branch')
                if target == 325:
                    for centre,label in [(12.5,'12p5'),(15.,'15')]:
                        band=clear[abs(abs(data['tilt'][clear])-centre)<=.125]
                        add_pool(f'angle{label}_equal_325',band[abs(lr[band]-1)<1e-8],data,l3,qs,qe,target,'normal_branch')
                        add_pool(f'angle{label}_within5_325',band[abs(lr[band]-1)<=.050001],data,l3,qs,qe,target,'normal_branch')
                    if l3 in (250,300,350,400):
                        add_pool(f'scale{int(l3)}_equal_325',clear[abs(lr[clear]-1)<1e-8],data,l3,qs,qe,target,'normal_branch')
                if abs(l3-250)<1e-8: add_pool(f'original_scale_{int(target)}',regular,data,l3,qs,qe,target,'normal_branch')
        # Independent crossing windows: total 300/325/350, both sides at least20%
        # of total vertical capacity. Endpoints solve exact V2 height equations.
        for target in targets:
            for fraction in fractions:
                counts['inversion_grid']+=len(g)
                capacity=curve(np.full(len(g),math.pi+60*R),l2,l3,g)[1]
                possible=pitch & (capacity>=max(fraction,1-fraction)*target)
                counts['inversion_geometry_pass']+=int(np.sum(possible))
                endpoints=[]
                for zgoal in [-(1-fraction)*target,fraction*target]:
                    sign=1 if zgoal>0 else -1;goal=abs(zgoal)
                    lo=np.zeros(len(g));hi=np.full(len(g),60*R)
                    for _ in range(28):
                        mid=(lo+hi)/2;zm=curve(math.pi+mid,l2,l3,g)[1]
                        lower=zm<goal;lo=np.where(lower,mid,lo);hi=np.where(lower,hi,mid)
                    endpoints.append(math.pi+sign*(lo+hi)/2)
                qs,qe=endpoints
                xs,zs,_,_=curve(qs,l2,l3,g);xe,ze,_,_=curve(qe,l2,l3,g)
                tilt=np.degrees(np.arctan2(xe-xs,ze-zs))
                ids=np.flatnonzero(possible&(abs(tilt)>=10)&(abs(tilt)<=15))
                counts['transition_target_angle']+=len(ids)
                if not len(ids):continue
                data0=_vector_metrics(l2[ids],l3,g[ids],qs[ids],qe[ids])
                data={k:np.full(len(g),np.nan) for k in data0}
                for k in data:data[k][ids]=data0[k]
                regular=ids[data['min_j'][ids]>=5]
                quality=regular[(data['relative'][regular]<=2)&(data['tangent_spread'][regular]<=15)]
                counts['transition_quality_pass']+=len(quality)
                for tol,label in [(1e-8,'equal'),(.050001,'within5'),(.150001,'within15')]:
                    selected=regular[abs(lr[regular]-1)<=tol]
                    add_pool(f'transition_{label}_{int(target)}',selected,data,l3,qs,qe,target,'inversion_transition')
        print(json.dumps(dict(progress=f'{scale_index+1}/{len(scales)} scales',counts=counts)),flush=True)
    return dict(domains=dict(L3_mm=[float(x) for x in scales],L2_over_L3=[float(x) for x in ratios],
        guide_ratio=[float(x) for x in guides],normal_start_deg=starts.tolist(),normal_end_cap_deg=175,
                    total_targets_mm=targets,inversion_above_fraction=fractions,
        alpha_deg=0,phase_deg=0,rb_mm=60,coarse_pose_samples=33),counts=counts,pools=pools)


def build_evidence(result):
    chosen={};leaders=[]
    for key,pool in sorted(result['pools'].items()):
        dense=[]
        for row in pool[:16]:
            l2,l3,r=row['L2'],row['L3'],row['ratio']
            start=row['start']
            zs=float(curve(start*R,l2,l3,r)[1])
            end=inverse_height(zs+row['target'],l2,l3,r,bounds=(start, min(260,row['end']+.01))) / R
            c=case(key,l2,l3,r,start,end,kind=row['family'])
            if 10-1e-8<=abs(c['metrics']['chord_tilt_deg'])<=15+1e-8:
                dense.append(c)
        if not dense:continue
        winner=min(dense,key=lambda c:(c['metrics']['max_chord_error_mm'],c['metrics']['tangent_spread_deg'],c['config']['L2']+c['config']['L3']))
        chosen[key]=winner
        leaders.append(dict(bucket=key,config=winner['config'],metrics=winner['metrics']))
    examples=[case('screenshot_250_5over3',250,250,5/3,100,165),
      case('equal250_ratio1p8',250,250,1.8,100,160),
      case('unequal275_250_ratio2',275,250,2,100,260,kind='inversion_transition'),
      case('phase_equal_12p5',250,250,2,160,200,-25,'phase_relaxation'),
      case('phase_near_equal_12p5',275,250,2,160,200,-25,'phase_relaxation')]
    practical=[]
    for length,start in [(350.,115.),(350.,120.),(400.,115.)]:
        ratio=7/4
        end=inverse_height(float(curve(start*R,length,length,ratio)[1])+325,
                           length,length,ratio,bounds=(start,175))/R
        practical.append(case(f'practical_equal{int(length)}_7over4_start{int(start)}',
                              length,length,ratio,start,end))
    guide_sweep=[]
    for ratio in np.linspace(1.4,2.2,81):
        try:
            end=inverse_height(float(curve(115*R,350,350,ratio)[1])+325,
                               350,350,ratio,bounds=(115,175))/R
            guide_sweep.append(dict(qab=float(ratio),tc=end,metrics=metrics(350,350,ratio,115,end)))
        except ValueError:pass
    reference=chosen.get('within5_325') or chosen.get('equal_325')
    selected=[chosen[k] for k in ['equal_300','equal_325','equal_350','within5_325','within10_325','within15_325',
      'angle12p5_equal_325','angle12p5_within5_325','angle15_equal_325','size700_325','compact_325',
      'scale250_equal_325','scale300_equal_325','scale350_equal_325','scale400_equal_325','original_scale_325',
      'transition_equal_325','transition_within15_325'] if k in chosen]
    # Deduplicate the displayed candidate subset, retaining the bucket aliases.
    unique=[]
    for c in selected:
        found=next((v for v in unique if all(abs(v['config'][k]-c['config'][k])<1e-7 for k in ['L2','L3','qab','te','tc'])),None)
        if found:found.setdefault('aliases',[]).append(c['id'])
        else:unique.append(c)
    return dict(schema='camel/alpha-zero-inversion-search/v1',date='2026-10-14',base_revision=BASE,
        assumptions=dict(wheel_radius_mm=200,end_buffers_mm=[20,20],path_offset='10–15 degrees from global vertical',
          near_equal_tiers='exact equal, <=5%, <=10%, <=15% deviation of L2/L3 from1',
          full_inversion='continuous q100..260 ideal guide motion, with C_z negative then positive; monotonic height/Jacobian recorded',
          strict_phase=0,strict_alpha=0,coarse_straightness_acceptance='max chord deviation <=2% chord and tangent spread <=15deg',
          projected_hip_exclusion_mm=220,axial_separation='unknown; no coplanar inversion candidate passes'),
        search=dict(domains=result['domains'],counts=result['counts'],dense_pose_samples=2001,
                    ranking='10–15deg chord, positive vertical Jacobian; branch clearance >=220mm; minimize max chord deviation, then tangent spread, then link sum',
                    total_geometry_window_evaluations=sum(result['counts'][k] for k in ['normal_grid','inversion_grid'])),
        selected=unique,leaders=leaders,examples=examples,practical=practical,guide_sweep=guide_sweep,
        recommended_id='practical_equal350_7over4_start115',best_straightness_id=reference['id'] if reference else None,
        conclusions=dict(strict_same_tilt_full_inversion=False,strict_coplanar_full_inversion=False,
          proof='x(pi+t) even and z(pi+t) odd; atq180 tangent vertical and hip distance |L2−L3|. Equal straight case qab2 is vertical.',
          phase_relaxation='qab2, equal links, phi0=−20..−30deg produces exact10..15deg line atalpha0; changes assembly indexing and retains hip crossing.'),
        provenance=dict(search_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                        model_sha256=hashlib.sha256((APP/'model.js').read_bytes()).hexdigest(),
                        python=platform.python_version(),numpy=np.__version__))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=APP/'docs/inversion-path-results.json')
    parser.add_argument('--quick',action='store_true')
    args=parser.parse_args();begin=time.perf_counter()
    result=search(args.quick);evidence=build_evidence(result)
    evidence['search']['elapsed_seconds']=round(time.perf_counter()-begin,3)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes((json.dumps(evidence,separators=(',',':'),ensure_ascii=False)+'\n').encode())
    print(json.dumps(dict(output=args.output.name,counts=evidence['search']['counts'],
        evaluated=evidence['search']['total_geometry_window_evaluations'],selected=len(evidence['selected']),
        recommended=evidence['recommended_id'],elapsed=evidence['search']['elapsed_seconds'])),flush=True)


if __name__=='__main__':main()
