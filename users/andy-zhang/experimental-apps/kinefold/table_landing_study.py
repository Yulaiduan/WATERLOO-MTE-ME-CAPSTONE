"""Compare the supplied 45 kg / full-65-degree landing table in both engines.

Run from Kinefold with its app Python:
  python table_landing_study.py --output .preview/table-landing --dt .000125
Inputs: screenshot cases (45 kg chassis, four equal corners, 1/1.5 m wheel-bottom
drop, alpha 0/20 deg), retained V4 geometry, explicit wheel kg/friction and SI
integration controls below. Writes captured requests, actual trajectories, local
passing torque brackets, interval AB inverse-dynamics loads and JSON/CSV summary
to the chosen app-local output folder. Never changes the live library or source
apps. Ideal unlimited joint actuator, massless bars and free wheel; two labelled
spring assumptions. Rigid impact force peaks and physical belt preload/compliance
are unknown. Reconstructed interval tension is not a native belt-force sensor,
hardware rating, global torque optimum or proof of four-leg load sharing.
"""
import argparse
import copy
import csv
import hashlib
import json
import math
import platform
import time
from pathlib import Path

from analytical_contact import simulate_contact as analytical
from contact_dynamics import simulate_contact as pymunk
from contact_cases import CASE_DEFAULTS,validate_contact_request,initial_conditions

ROOT=Path(__file__).resolve().parent
CASES=(('1a',1000,20,97,5.2),('1b',1500,20,146,7.4),
       ('2a',1000,0,97,3.1),('2b',1500,0,146,4.06))
ENGINES={'analytical':analytical,'pymunk':pymunk}


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,allow_nan=False,separators=(',',':')),encoding='utf-8')


def payload(base,case,engine,spring,dt,output_hz,wheel_mass,friction,duration):
    label,height,alpha,torque,_=case
    p=copy.deepcopy(base['params'])
    p.update(m1=45/4,m2=0,m3=0,m5=0,m6=wheel_mass,alpha=alpha,
             theta2=100,te=100,tc=165,loadMode='weight',Fx=0,Tab0=0,Tcd0=0,Tef0=0)
    p.update(Fn=(p['m1']+wheel_mass)*p['g'],Fz=(p['m1']+wheel_mass)*p['g'],Ft=0,beta=0)
    p['springEnabled']=spring!='off'
    if spring=='gcomp':
        # Scale the existing V4 chassis support law, not a new impact soft stop.
        # Both k and reference preload scale equally, preserving the route.
        scale=(p['m1']/base['params']['m1'])*math.cos(math.radians(alpha))
        p['springK']*=scale;p['p0']*=scale
    run={**base['solverConfig'],'dt':dt,'duration':duration,'outputHz':output_hz,
         'initialVelocityDegS':0,'hipTorqueNm':0,'dampingNms':0,
         'hipRotorInertiaKgM2':0,'inputRiseMm':0,'iterations':160}
    result=dict(engine=engine,params=p,runConfig=run,
        contactConfig=dict(mode='terrain-contact',drive='free',friction=friction,restitution=0),
        caseConfig={**CASE_DEFAULTS,'kind':'landing','landingDropMm':height,
                    'landingOpenFraction':1.,'landingBrakeTorqueNm':torque,
                    'landingBrakeLimitNm':1000.,'undersideOffsetMm':50.,'brakeStrategy':'entered'})
    m=validate_contact_request(result);q,*_=initial_conditions(m,result['caseConfig'])
    assert abs(math.degrees(q)-100)<1e-10
    assert abs(math.degrees(m.hi-q)-65)<1e-10
    return result


def belt_intervals(request,result):
    """Massless lower-link moment balance using actual interval wheel momentum.

    F_w = F_contact + W_wheel - m_wheel*Delta(v_wheel)/Delta(t), source x/z SI.
    DeltaT_AB = -cross(r_BC,F_w)/r_b. Lever arm is the interval endpoint mean.
    With zero entered preload, tight span = abs(DeltaT); slack span = 0 in the
    ideal source convention. Impacts/stops are labelled, never finite peak claims.
    """
    m=validate_contact_request(request);p=m.p;rows=result['rows'];frames=result['frames']
    assert p['m2']==p['m3']==p['m5']==0
    impact=next((e['t'] for e in result['events'] if e['type']=='first-contact'),None)
    arrest=next((e['t'] for e in result['events'] if e['type']=='chassis-arrest'),None)
    stops=[e['t'] for e in result['events'] if e['type'] in ('compression-stop','extension-stop')]
    intervals=[]
    for i in range(1,len(rows)):
        a,b=rows[i-1],rows[i];dt=b['t']-a['t']
        if dt<1e-10:continue
        acx=-(b['wheelVelocityXMmS']-a['wheelVelocityXMmS'])/(1000*dt)
        acz=(b['wheelVelocityZMmS']-a['wheelVelocityZMmS'])/(1000*dt)
        force=(-b['contactForceXN']-p['m6']*acx,
               b['contactForceZN']-p['m6']*p['g']-p['m6']*acz)
        arms=[]
        for f in (frames[i-1],frames[i]):
            arms.append((-(f['C'][0]-f['B'][0])/1000,(f['C'][2]-f['B'][2])/1000))
        arm=tuple(sum(v[k] for v in arms)/2 for k in (0,1))
        differential=-(arm[0]*force[1]-arm[1]*force[0])/(p['rb']/1000)
        event_window=lambda t:t is not None and a['t']-2*request['runConfig']['dt']<=t<=b['t']+2*request['runConfig']['dt']
        phase='flight' if impact is None or b['t']<impact else 'braking'
        if event_window(impact):phase='impact-interval'
        if any(event_window(t) for t in stops):phase='stop-interval'
        if arrest is not None and a['t']>=arrest:phase='after-arrest'
        residual=force[1]-p['m1']*(p['g']+(b['chassisVelocityMmS']-a['chassisVelocityMmS'])/(1000*dt))
        intervals.append(dict(t=b['t'],startS=a['t'],durationS=dt,theta2Deg=(a['theta2']+b['theta2'])/2,
            phase=phase,deltaTabN=differential,upperN=p['Tab0']+max(0,differential),
            lowerN=p['Tab0']+max(0,-differential),tightN=p['Tab0']+abs(differential),
            wheelToLinkForceSourceN=force,verticalMomentumResidualN=residual))
    return intervals


def summarize(request,result,include_belts=True):
    intervals=belt_intervals(request,result) if include_belts else []
    smooth=[r for r in intervals if r['phase']=='braking']
    all_peak=max(intervals,key=lambda r:r['tightN']) if intervals else None
    peak=max(smooth,key=lambda r:r['tightN']) if smooth else None
    c=result['caseMetrics'];diag=result['diagnostics']
    numerical=(diag.get('maxPenetrationMm',0)<=1 and diag.get('maxConstraintPositionErrorMm',0)<=1
               and diag['termination'] not in ('penetration-limit','constraint-limit','jam'))
    first=result['rows'][0];last=result['rows'][-1]
    return dict(enteredJointNm=request['caseConfig']['landingBrakeTorqueNm'],outputHz=request['runConfig']['outputHz'],
        success=bool(c['landingSuccess']) and numerical,numericallyResolved=numerical,
        outcome=c['outcome'],termination=diag['termination'],impactTimeS=c['impactTimeS'],
        arrestTimeS=c['firstArrestTimeS'],maxCompressionDeg=c['maxCompressionDeg'],
        usedTravelDeg=c['maxCompressionDeg']-first['theta2'],
        minimumClearanceMm=c['minimumUndersideClearanceMm'],
        peakDeliveredBrakeNm=max(abs(r['brakeTorqueNm']) for r in result['rows']),
        smoothBrakingTabPeakN=peak['tightN'] if peak else None,
        smoothBrakingTabPeak=peak,allIntervalsTabPeak=all_peak,
        maxVerticalMomentumResidualN=max(abs(r['verticalMomentumResidualN']) for r in smooth) if smooth else None,
        motorWorkJ=last['motorWorkJ'],springStoredJ=last['springEnergyJ']-first['springEnergyJ'],
        gravityReleasedJ=first['gravityEnergyJ']-last['gravityEnergyJ'],
        remainingKineticJ=last['kineticJ'],energyResidualJ=diag['energyBalanceResidualJ'],
        penetrationMm=diag['maxPenetrationMm'],constraintMm=diag['maxConstraintPositionErrorMm'])


def run(request,include_belts=True):
    result=ENGINES[request['engine']](request,stop_at_assessment=True)
    return summarize(request,result,include_belts),result


def search(request,iterations):
    """Local lowest-passing bracket under this controller, not a global optimum."""
    trials=[];best=None
    def trial(torque):
        nonlocal best
        r=copy.deepcopy(request);r['caseConfig']['landingBrakeTorqueNm']=torque
        # Sampling is not used for step-resolved arrest/stop decisions. Avoid
        # rebuilding thousands of drawing/energy rows in exploratory trials.
        r['runConfig']['outputHz']=min(100.,request['runConfig']['outputHz'])
        summary,result=run(r,include_belts=False);trials.append(summary)
        if not summary['numericallyResolved']:raise ValueError('Numerical failure during torque search; not classified as physical failure.')
        if summary['success'] and (best is None or torque<best[0]['caseConfig']['landingBrakeTorqueNm']):best=(r,result,summary)
        return summary['success']
    m=validate_contact_request(request);q,*_=initial_conditions(m,request['caseConfig'])
    compression=m.sites(m.hi)['6'][0][1]-m.sites(q)['6'][0][1]
    work=m.p['m1']*m.p['g']*(request['caseConfig']['landingDropMm']/1000+compression)
    work-=m.spring(m.hi)['energy']-m.spring(q)['energy']
    estimate=max(0,work/(m.hi-q))
    values=sorted(set([0.,request['caseConfig']['landingBrakeTorqueNm'],estimate,max(estimate*1.3+10,220.)]))
    hi=None;lo=0.
    for torque in values:
        if trial(torque):hi=torque;break
        lo=torque
    if hi is None:return dict(feasible=False,trials=trials,endpointWorkEstimateNm=estimate),None
    for _ in range(iterations):
        mid=(lo+hi)/2
        if trial(mid):hi=mid
        else:lo=mid
    # Validate both ends at the requested display interval. Float-step boundaries
    # and rigid impacts can move a zero-reserve threshold; keep actual evidence.
    def final(torque):
        r=copy.deepcopy(request);r['caseConfig']['landingBrakeTorqueNm']=torque
        summary,result=run(r);trials.append(summary)
        if not summary['numericallyResolved']:raise ValueError('Numerical failure at final torque bracket.')
        return r,result,summary
    lower=final(lo);upper=final(hi)
    if lower[2]['success']:
        # Preserve a known failing end from the same full-output configuration.
        lo=0.;lower=final(lo)
        if lower[2]['success']:return dict(feasible=True,lowerFailingNm=None,upperPassingNm=0.,bracketWidthNm=None,endpointWorkEstimateNm=estimate,trials=trials,best=lower[2]),lower
        for _ in range(iterations):
            mid=(lo+hi)/2;tested=final(mid)
            if tested[2]['success']:hi=mid;upper=tested
            else:lo=mid;lower=tested
    for _ in range(5):
        if upper[2]['success']:break
        lo=hi;lower=upper;hi+=max(.25,hi*.005);upper=final(hi)
    if not upper[2]['success']:return dict(feasible=False,endpointWorkEstimateNm=estimate,trials=trials,reason='Full-output verification did not establish a passing upper bound.'),None
    return dict(feasible=True,lowerFailingNm=lo,upperPassingNm=hi,bracketWidthNm=hi-lo,
        endpointWorkEstimateNm=estimate,trials=trials,best=upper[2]),upper


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--dt',type=float,default=.000125)
    parser.add_argument('--output-hz',type=float,default=1000)
    parser.add_argument('--wheel-mass',type=float,default=.5)
    parser.add_argument('--friction',type=float,default=.8)
    parser.add_argument('--duration',type=float,default=1.5)
    parser.add_argument('--search-iterations',type=int,default=8)
    parser.add_argument('--spring',choices=('off','gcomp','both'),default='both')
    parser.add_argument('--engine',choices=('analytical','pymunk','both'),default='both')
    parser.add_argument('--case',choices=tuple(c[0] for c in CASES))
    parser.add_argument('--skip-search',action='store_true')
    args=parser.parse_args();output=args.output.resolve()
    if ROOT not in output.parents:raise ValueError('Study output must stay inside Kinefold.')
    if not 0<=args.search_iterations<=12:raise ValueError('Bound the search to 0..12 iterations.')
    base=json.loads((ROOT/'saved-configurations/vsl-v4-nominal-alpha0.json').read_text())
    library=ROOT/'profiles/library.json';before=hashlib.sha256(library.read_bytes()).hexdigest() if library.exists() else None
    output.mkdir(parents=True,exist_ok=True)
    names=('table_landing_study.py','contact_cases.py','analytical_contact.py','contact_dynamics.py','dynamic_model.py','reference-v4.js',
           'motor_model.py','terrain_profiles.py','finite_contact_model.py','finite_pymunk_contact.py','actuation_limits.py','torque_targets.py')
    identity={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
    # Cached trajectories may be summarized by an updated reporting script, but
    # their physical engine/dependency sources must match this run exactly.
    physics={name:value for name,value in identity.items() if name!='table_landing_study.py'}
    manifest_path=output/'physics-identity.json'
    if manifest_path.exists():
        if json.loads(manifest_path.read_text())!=physics:raise ValueError('Physics sources changed; use a fresh study output folder.')
    elif any(output.glob('case-*.json')):
        raise ValueError('Legacy cache has no source identity; use a fresh output folder.')
    else:write(manifest_path,physics)
    settings=dict(dt=args.dt,outputHz=args.output_hz,wheelMassKg=args.wheel_mass,friction=args.friction,
        durationS=args.duration,searchIterations=args.search_iterations,chassisKgPerCorner=11.25,
        fullChassisKg=45,upperLinkKg=0,lowerLinkKg=0,stopReserveDeg=0,brakingTravelDeg=65,
        motor='ideal unlimited joint torque, no rotor/gear inertia or drag',wheel='free uniform disc',
        gcomp='Existing V4 k and p0 scaled by (11.25/8.75)*cos(alpha), route unchanged; approximate chassis support, no added soft stop',
        belt='Zero-preload minimum tight strand from interval wheel momentum and massless lower-link moment balance; not elastic/impulsive physical peak')
    records=[];start=time.monotonic()
    springs=('off','gcomp') if args.spring=='both' else (args.spring,)
    for case in CASES:
        if args.case and case[0]!=args.case:continue
        for spring in springs:
            for engine in ENGINES:
                if args.engine!='both' and engine!=args.engine:continue
                tag=f'case-{case[0]}-{spring}-{engine}'
                request=payload(base,case,engine,spring,args.dt,args.output_hz,args.wheel_mass,args.friction,args.duration)
                cache=output/(tag+'-table.json')
                if cache.exists():
                    capture=json.loads(cache.read_text());assert capture['payload']==request
                    result=capture['result'];summary=summarize(request,result)
                else:
                    summary,result=run(request);write(cache,dict(payload=request,result=result,beltIntervals=belt_intervals(request,result)))
                item=dict(case=case[0],dropMm=case[1],alphaDeg=case[2],tableJointNm=case[3],tableTabKN=case[4],
                    engine=engine,spring=spring,appliedTableTorque=summary)
                if not args.skip_search:
                    search_path=output/(tag+'-search.json')
                    if search_path.exists():
                        saved=json.loads(search_path.read_text());assert saved['basePayload']==request
                        item['search']=saved['search']
                    else:
                        found,best=search(request,args.search_iterations);item['search']=found
                        write(search_path,dict(basePayload=request,search=found))
                        if best:
                            r,s,_=best;write(output/(tag+'-passing.json'),dict(payload=r,result=s,beltIntervals=belt_intervals(r,s)))
                records.append(item);write(output/'progress.json',dict(settings=settings,records=records,elapsedSeconds=time.monotonic()-start))
                s=item.get('search',{})
                print(json.dumps(dict(case=case[0],engine=engine,spring=spring,tableOutcome=summary['outcome'],
                    requiredBracketNm=[s.get('lowerFailingNm'),s.get('upperPassingNm')],tableRunSmoothTabKN=(summary['smoothBrakingTabPeakN'] or 0)/1000,
                    elapsedSeconds=round(time.monotonic()-start,1))),flush=True)
    after=hashlib.sha256(library.read_bytes()).hexdigest() if library.exists() else None
    assert before==after,'Live profile library changed during a read-only study.'
    report=dict(schema='kinefold/table-landing-study-v1',sourceCommit='9fca28d plus full-open input validation',
        python=platform.python_version(),sourceSHA256=identity,settings=settings,records=records,
        profileLibrarySHA256=before,elapsedSeconds=time.monotonic()-start,
        limitations=['Four equal corner shares imposed; full vehicle pitch/roll not simulated.',
            'Screenshot lacks moving mass, spring tuning, wheel friction and belt preload; selected assumptions are explicit.',
            'Ideal rigid collision intervals do not determine physical impact force/belt peaks.',
            'Passing torque is an observed local bracket with zero stop reserve, not certified minimum or hardware survival.'])
    write(output/'summary.json',report)
    fields=['case','dropMm','alphaDeg','spring','engine','tableJointNm','tableTabKN','outcome','requiredLowerNm','requiredUpperNm','tableRunTabKN','passingRunTabKN','passingUsedTravelDeg','residualJ']
    with (output/'summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in records:
            s=r.get('search',{});b=s.get('best',{})
            writer.writerow({**{k:r[k] for k in fields if k in r},'outcome':r['appliedTableTorque']['outcome'],
                'requiredLowerNm':s.get('lowerFailingNm'),'requiredUpperNm':s.get('upperPassingNm'),
                'tableRunTabKN':(r['appliedTableTorque']['smoothBrakingTabPeakN'] or 0)/1000,
                'passingRunTabKN':None if b.get('smoothBrakingTabPeakN') is None else b['smoothBrakingTabPeakN']/1000,
                'passingUsedTravelDeg':b.get('usedTravelDeg'),'residualJ':b.get('energyResidualJ')})
    print('SUMMARY '+str(output/'summary.json'),flush=True)


if __name__=='__main__':main()
