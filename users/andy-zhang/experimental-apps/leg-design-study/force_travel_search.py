"""Rank alpha-zero guided legs for vertical force and buffered travel.

Run from this app: .venv/Scripts/python.exe force_travel_search.py
Inputs: explicit mm/degree domains below, R200 wheel, 20 mm each-end reserves,
300/325/350 mm total height, ideal massless moving links and vertical endpoint
load 98.1/110.3625 N. Outputs: compact docs/force-travel-results.json; numerical
grid/refinement counts and selected profiles. Requires pinned NumPy/SciPy.
Limits: bounded ideal mechanical advantage, not energy efficiency, rated motor,
actual impact/contact, structural strength or physically collision-free inversion.
The old inversion search/model and rejected dual-rope remain unchanged.
"""
from __future__ import annotations
import hashlib
import json
import math
import platform
from pathlib import Path
import time
import numpy as np
from scipy.optimize import minimize
from inversion_search import curve, inverse_height, metrics, R, _vector_metrics

APP = Path(__file__).resolve().parent
BASE = 'd1596e570dad3560a6dc544bfdbc67d158c547ca'
F45 = 45/4*9.81


def json_scalar(value):
    if isinstance(value,np.generic):return value.item()
    raise TypeError(f'Unsupported evidence type: {type(value).__name__}')


def force_metrics(l2, l3, r, start, end, phase=0., samples=2001):
    """Vertical load: J in m/rad, F/T in N/Nm; RMS uniform usable height."""
    zs, ze = [float(curve(q*R,l2,l3,r,phase)[1]) for q in (start,end)]
    usable = ze-zs-40
    if usable <= 0:
        raise ValueError('Total height must exceed the two explicit 20 mm reserves.')
    lo = inverse_height(zs+20,l2,l3,r,phase,(start,end))/R
    hi = inverse_height(ze-20,l2,l3,r,phase,(start,end))/R
    q = np.linspace(lo*R,hi*R,samples)
    x,z,jx,jz = curve(q,l2,l3,r,phase)
    if np.min(jz) <= 0:
        raise ValueError('Height must be strictly monotone on the usable range.')
    j = jz/1000
    peak = float(np.max(j))
    rms = float(np.sqrt(np.trapezoid(j*j,z)/(z[-1]-z[0])))
    angle_mean = float(np.trapezoid(j,q)/(q[-1]-q[0]))
    mean_height = float(np.trapezoid(j,z)/(z[-1]-z[0]))
    window = (hi-lo)*R
    along_peak = float(np.max(np.hypot(jx,jz))/1000)
    rows = []
    for i in np.linspace(0,len(q)-1,61).astype(int):
        rows.append(dict(q_deg=float(q[i]/R),height_mm=float(z[i]-z[0]),
            x_mm=float(x[i]),z_mm=float(z[i]),Jz_m_rad=float(j[i]),
            Jx_m_rad=float(jx[i]/1000),force_per_hip_N_Nm=float(1/j[i]),
            torque_45kg_Nm=float(F45*j[i]),torque_40kg_Nm=float(98.1*j[i]),
            torque_4g_45kg_Nm=float(4*F45*j[i])))
    return dict(usable_mm=usable,usable_angle_bounds_deg=[lo,hi],
        hip_ROM_deg=hi-lo,relative_knee_ROM_deg=r*(hi-lo),
        max_Jz_m_rad=peak,min_Jz_m_rad=float(np.min(j)),
        min_force_per_hip_N_Nm=1/peak,max_force_per_hip_N_Nm=float(1/np.min(j)),
        min_force_per_relative_knee_N_Nm=r/peak,
        rms_Jz_uniform_height_m_rad=rms,mean_Jz_uniform_height_m_rad=mean_height,
        mean_Jz_uniform_angle_m_rad=angle_mean,
        peak_45kg_hip_Nm=F45*peak,rms_45kg_hip_uniform_height_Nm=F45*rms,
        peak_40kg_hip_Nm=98.1*peak,peak_4g_45kg_hip_Nm=4*F45*peak,
        peak_45kg_relative_knee_Nm=F45*peak/r,
        min_force_along_path_per_hip_N_Nm=1/along_peak,
        constant_vertical_speed_0p25m_s_peak_hip_rad_s=.25/float(np.min(j)),
        ideal_lift_work_45kg_J=F45*usable/1000,
        work_integral_45kg_J=float(np.trapezoid(F45*j,q)),
        travel_per_peak_torque_mm_Nm=usable/(F45*peak),
        utilization_H_over_peakJ_ROM=usable/1000/(peak*window),
        horizontal_to_vertical_J_ratio_max=float(np.max(abs(jx/jz))),
        samples=rows)


def evaluate(name,l2,l3,r,start,total,phase=0.,quality=3.):
    fold=180+phase/2 if abs(r-2)<1e-12 else 180.
    cap=fold-5
    z0=float(curve(start*R,l2,l3,r,phase)[1])
    end=inverse_height(z0+total,l2,l3,r,phase,(start,cap))/R
    m=metrics(l2,l3,r,start,end,phase,2001)
    f=force_metrics(l2,l3,r,start,end,phase)
    full=metrics(l2,l3,r,fold-80,fold+80,phase,2001)
    q=np.linspace(start*R,end*R,61)
    x,z,dx,dz=curve(q,l2,l3,r,phase)
    return dict(id=name,family='strict_phase_zero' if phase==0 else 'fixed_indexing_relaxation',
      config=dict(L2=l2,L3=l3,qab=r,alpha=0,phi0=phase,ra=60*r,rb=60,rw=200,
                  te=start,tc=end,qcd=1,qef=1,beta=13.5),
      total_mm=total,link_sum_mm=l2+l3,link_mismatch_fraction=abs(l2/l3-1),
      path=m,force=f,full_inversion=dict(bounds_deg=[fold-80,fold+80],
        min_vertical_J_mm_rad=full['min_vertical_jacobian_mm_rad'],
        ideal_height_invertible=full['min_vertical_jacobian_mm_rad']>=5,
        minimum_hip_distance_mm=full['minimum_hip_distance_mm'],
        coplanar_clearance_pass=full['projected_clearance_pass']),
      acceptance=dict(chord_10to15=10-1e-7<=abs(m['chord_tilt_deg'])<=15+1e-7,
        bow_within_policy=m['chord_error_percent']<=quality+1e-6,
        tangent_span_within15=m['tangent_spread_deg']<=15+1e-6,
        normal_branch_clearance=m['minimum_hip_distance_mm']>=220-1e-6,
        full_ideal_height_invertible=full['min_vertical_jacobian_mm_rad']>=5,
        guide_pitch_clear=l2>60*(r+1)),
      samples=[dict(q_deg=float(a/R),x_mm=float(b),z_mm=float(c),
        tangent_deg=float(math.degrees(math.atan2(d,e)))) for a,b,c,d,e in zip(q,x,z,dx,dz)])


def accepted(c):
    return all(c['acceptance'].values())


def grid():
    guides=np.unique(np.r_[np.round(np.arange(1.4,2.60001,.005),8),5/3,1.75,1.8,2])
    ratios=np.round(np.arange(.85,1.15001,.01),8)
    scales=np.unique(np.r_[np.arange(200,450.1,10),275,325,375,425])
    starts=np.arange(100.,140.01,2.5)
    gg,rr=np.meshgrid(guides,ratios,indexing='ij');g=gg.ravel();lr=rr.ravel()
    pools={};size_pools={};counts=dict(enumerated=0,height_and_pitch=0,
      angle_clearance_full_inversion=0,quality3=0,quality2=0)
    def save(key,ids,l2,l3,qs,qe,total,score,d):
        if not len(ids):return
        ids=ids[np.argsort(score[ids],kind='stable')[:8]]
        rows=[dict(L2=float(l2[i]),L3=float(l3),r=float(g[i]),start=float(qs[i]/R),
          total=float(total),score=float(score[i]),coarse_bow=float(d['relative'][i])) for i in ids]
        pools.setdefault(key,[]).extend(rows)
        pools[key]=sorted(pools[key],key=lambda x:(x['score'],x['L2']+x['L3']))[:16]
    for si,l3 in enumerate(scales):
        l2=lr*l3;pitch=l2>60*(g+1)
        full=curve(np.full(len(g),100*R),l2,l3,g)[3]>=5
        for start in starts:
            qs=np.full(len(g),start*R);xs,zs,_,js=curve(qs,l2,l3,g)
            cap=curve(np.full(len(g),175*R),l2,l3,g)[1]
            for total in (300.,325.,350.):
                counts['enumerated']+=len(g)
                ids=np.flatnonzero(pitch&full&(js>=5)&((cap-zs)>=total))
                counts['height_and_pitch']+=len(ids)
                if not len(ids):continue
                lo=qs[ids].copy();hi=np.full(len(ids),175*R)
                for _ in range(32):
                    mid=(lo+hi)/2;low=curve(mid,l2[ids],l3,g[ids])[1]<zs[ids]+total
                    lo=np.where(low,mid,lo);hi=np.where(low,hi,mid)
                qe=qs.copy();qe[ids]=(lo+hi)/2
                xe,ze,_,_=curve(qe[ids],l2[ids],l3,g[ids])
                angle=np.degrees(np.arctan2(xe-xs[ids],ze-zs[ids]))
                ids=ids[(abs(angle)>=10)&(abs(angle)<=15)]
                if not len(ids):continue
                d0=_vector_metrics(l2[ids],l3,g[ids],qs[ids],qe[ids],51)
                d={k:np.full(len(g),np.nan) for k in d0}
                for k in d:d[k][ids]=d0[k]
                ids=ids[(d['min_radius'][ids]>=220)&(d['min_j'][ids]>=5)]
                counts['angle_clearance_full_inversion']+=len(ids)
                if not len(ids):continue
                # On phase-zero q100..175, Jz increases strictly; its usable peak
                # is exactly at the upper usable end, 20 mm before the total end.
                lo=qs[ids].copy();hi=qe[ids].copy()
                for _ in range(32):
                    mid=(lo+hi)/2;low=curve(mid,l2[ids],l3,g[ids])[1]<zs[ids]+total-20
                    lo=np.where(low,mid,lo);hi=np.where(low,hi,mid)
                score=np.full(len(g),np.inf)
                score[ids]=curve((lo+hi)/2,l2[ids],l3,g[ids])[3]/1000
                for quality in (3.,2.):
                    valid=ids[(d['relative'][ids]<=quality)&(d['tangent_spread'][ids]<=15)]
                    counts['quality'+str(int(quality))]+=len(valid)
                    for tol,tier in [(1e-8,'equal'),(.050001,'within5'),(.100001,'within10'),(.150001,'within15')]:
                        selected=valid[abs(lr[valid]-1)<=tol]
                        save(f'{tier}_{int(total)}_bow{int(quality)}',selected,l2,l3,qs,qe,total,score,d)
                    if total==325 and quality==3:
                        for bucket in np.unique(np.ceil((l2[valid]+l3)/25)*25):
                            selected=valid[np.ceil((l2[valid]+l3)/25)*25==bucket]
                            save(f'size_{int(bucket)}',selected,l2,l3,qs,qe,total,score,d)
        print(json.dumps(dict(scale=f'{si+1}/{len(scales)}',counts=counts)),flush=True)
    return dict(pools=pools,counts=counts,domains=dict(L3_mm=scales.tolist(),
        L2_over_L3=ratios.tolist(),guide_ratio=guides.tolist(),start_deg=starts.tolist(),
        end_cap_deg=175,total_mm=[300,325,350],alpha_deg=0,phase_deg=0,
        reserves_mm=[20,20],coarse_poses=51,dense_finalist_poses=2001))


def refine(seed,equal=False,quality=3.):
    """Local constrained refinement seeded by grid; no global-optimality claim."""
    p=seed['config'];total=seed['total_mm'];phase=p['phi0']
    v0=[p['L3'],p['L2']/p['L3'],p['qab'],p['te']]
    bounds=[(200,450),(1,1) if equal else (.95,1.05),(1.4,2.6),(100,140)]
    def calc(v):
        b,lr,r,start=v;a=b*lr
        z0=float(curve(start*R,a,b,r,phase)[1])
        cap=float(curve(175*R,a,b,r,phase)[1])-z0-total
        if cap<0:return None,cap
        end=inverse_height(z0+total,a,b,r,phase,(start,175))/R
        m=metrics(a,b,r,start,end,phase,401)
        qe=inverse_height(z0+total-20,a,b,r,phase,(start,end))
        score=float(curve(qe,a,b,r,phase)[3])/1000
        tilt=abs(m['chord_tilt_deg'])
        constraints=np.array([cap/100,tilt-10,15-tilt,quality-m['chord_error_percent'],
          15-m['tangent_spread_deg'],(m['minimum_hip_distance_mm']-220)/100,
          (float(curve(100*R,a,b,r,phase)[3])-5)/100,(a-60*(r+1))/100])
        return (score,constraints),cap
    def fun(v):
        val,cap=calc(v);return val[0] if val else 10-cap/100
    def cons(v):
        val,cap=calc(v);return val[1] if val else np.full(8,cap/100)
    result=minimize(fun,v0,method='SLSQP',bounds=bounds,
      constraints=[dict(type='ineq',fun=cons)],options=dict(maxiter=250,ftol=1e-11))
    b,lr,r,start=result.x
    c=evaluate('refined_equal' if equal else 'refined_within5',b*lr,b,r,start,total,phase,quality)
    return dict(method='SLSQP, locally constrained, 401-pose objective constraints; 2001-pose final check',
        solver_success=bool(result.success),message=str(result.message),iterations=int(result.nit),
        objective_m_rad=float(result.fun),dense_accepted=accepted(c),case=c)


def phase_search():
    """Separate alpha-zero fixed -25deg phase/r2 alternative, working clearance required."""
    pools={};enumerated=0;passed=0
    for total in [300.,325.,350.]:
        candidates=[]
        for b in np.arange(250.,450.01,5.):
            for lr in [.95,.975,1.,1.025,1.05]:
                for start in np.arange(87.5,130.01,2.5):
                    enumerated+=1
                    try:c=evaluate('indexed',b*lr,b,2.,start,total,-25,3)
                    except ValueError:continue
                    if not accepted(c):continue
                    passed+=1;candidates.append(c)
        for tol,tier in [(1e-8,'equal'),(.050001,'within5')]:
            eligible=[c for c in candidates if c['link_mismatch_fraction']<=tol]
            if eligible:
                c=min(eligible,key=lambda c:(c['force']['max_Jz_m_rad'],c['link_sum_mm']))
                c['id']=f'indexed_{tier}_{int(total)}';pools[c['id']]=c
        print(json.dumps(dict(indexed_total=total,enumerated=enumerated,passed=passed)),flush=True)
    return dict(enumerated=enumerated,accepted=passed,selected=list(pools.values()),
       domains=dict(L3_mm=[250,450,5],L2_over_L3=[.95,.975,1,1.025,1.05],
       start_deg=[87.5,130,2.5],phase_deg=-25,guide_ratio=2,
       comment='Shifted full inversion87.5..247.5 about fold167.5; lower-link indexing relaxation.'))


def main():
    begin=time.perf_counter();raw=grid();leaders=[];frontier=[]
    for key,pool in sorted(raw['pools'].items()):
        quality=2. if key.endswith('bow2') else 3.
        candidates=[]
        for row in pool:
            c=evaluate(key,row['L2'],row['L3'],row['r'],row['start'],row['total'],quality=quality)
            if accepted(c):candidates.append(c)
        if not candidates:continue
        winner=min(candidates,key=lambda c:(c['force']['max_Jz_m_rad'],c['link_sum_mm']))
        if key.startswith('size_'):frontier.append(winner)
        else:leaders.append(winner)
    equal=next(c for c in leaders if c['id']=='equal_325_bow3')
    near=next(c for c in leaders if c['id']=='within5_325_bow3')
    refined=[refine(equal,True),refine(near)]
    indexed=phase_search()
    old=json.loads((APP/'docs/inversion-path-results.json').read_text(encoding='utf-8'))
    references=[]
    for field,name in [('practical','practical_equal350_7over4_start115'),('selected','equal_325'),
                       ('examples','screenshot_250_5over3')]:
        c=next(c for c in old[field] if c['id']==name or name in c.get('aliases',[]));p=c['config']
        row=evaluate('reference_'+name,p['L2'],p['L3'],p['qab'],p['te'],c['metrics']['vertical_mm'],p['phi0'])
        references.append(row)
    selected=[equal,near]+[c for c in leaders if c['id'] in ['equal_300_bow3','equal_350_bow3','equal_325_bow2','within15_325_bow3']]
    selected += [r['case'] for r in refined if r['dense_accepted']]
    selected += indexed['selected'] + references
    selected += [evaluate('rounded_equal320_9over5',320.,320.,1.8,110.,325.),
                 evaluate('rounded_equal340_7over4',340.,340.,1.75,115.,325.),
                 evaluate('diagnostic_equal330_7over4',330.,330.,1.75,115.,325.),
                 evaluate('rounded_indexed_equal300',300.,300.,2.,87.5,325.,-25.)]
    # Compact Pareto candidates; retain only sizes that improve peakJ over smaller designs.
    pareto=[];best=math.inf
    for c in sorted(frontier,key=lambda c:c['link_sum_mm']):
        if c['force']['max_Jz_m_rad']<best-1e-9:
            best=c['force']['max_Jz_m_rad'];pareto.append(c)
    strip=lambda c:{k:v for k,v in c.items() if k!='samples'} | {'force':{k:v for k,v in c['force'].items() if k!='samples'}}
    data=dict(schema='camel/force-travel-study/v1',date='2026-10-14',base_revision=BASE,
       strict_search=dict(counts=raw['counts'],domains=raw['domains'],
         ranking='minimize peakJz over usable height, then link sum, with chord10..15, bow<=3%(or2), tangent span<=15, total-window |C|>=220, fullJz>=5, guide pitch clearance'),
       indexed_search={k:v for k,v in indexed.items() if k!='selected'},
       assumptions=dict(wheel_radius_mm=200,total_height_mm=[300,325,350],end_buffers_mm=[20,20],
         per_leg_mass_kg=[10,11.25],vertical_load_N=[98.1,F45],moving_links='massless force-transmission comparison; no gravity allocation or sprung-mass double counting',
         forces='Pure vertical endpoint load, Fy=0; horizontal sensitivity separately plotted. Fixed hip, no spring.',
         impact='3g/4g equivalent held loads, not integrated impacts, hardware ratings or dynamic motor torque',
         RMS='Uniform usable height / constant vertical speed, without dwell; no mission thermal RMS',
         invertible='Ideal monotone vertical map below-to-above hip; projected full clearance fails all shortlisted designs',
         straightness='Illustrative3%bow/15deg tangent-span limits; strict2% comparison retained'),
       selected=selected,grid_leaders=[strip(c) for c in leaders],pareto=[strip(c) for c in pareto],
       size_leaders=[strip(c) for c in sorted(frontier,key=lambda c:c['link_sum_mm'])],
       refinement=[{k:v for k,v in r.items() if k!='case'}|{'id':r['case']['id']} for r in refined],
       provenance=dict(python=platform.python_version(),numpy=np.__version__,
         sources={p:hashlib.sha256((APP/p).read_bytes()).hexdigest() for p in ['force_travel_search.py','inversion_search.py','docs/inversion-path-results.json']},
         elapsed_seconds=round(time.perf_counter()-begin,3)))
    target=APP/'docs/force-travel-results.json'
    target.write_bytes((json.dumps(data,separators=(',',':'),ensure_ascii=False,
        allow_nan=False,default=json_scalar)+'\n').encode())
    print(json.dumps(dict(output=target.name,bytes=target.stat().st_size,selected=len(selected),pareto=len(pareto),
       refined=data['refinement'],elapsed=data['provenance']['elapsed_seconds'])),flush=True)


if __name__=='__main__':main()
