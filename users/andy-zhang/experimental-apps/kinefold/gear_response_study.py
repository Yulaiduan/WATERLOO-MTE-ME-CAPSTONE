"""Compare three ODrive gearbox designs with real wheel contact and free spin.

Run app Python: python gear_response_study.py --write-config .preview/gear.json
then python gear_response_study.py --config .preview/gear.json --output .preview/gear-run
Inputs: editable kg/mm/deg/s/Nm assumptions, three exact catalogue gearboxes,
floating terrain speeds, one pinned-chassis terrain speed and a desired-height
step. Outputs source-guarded summary JSON/CSV with exact requests, weighted
metrics and at most eight selected raw captures, inside this app. Maximum36
base runs; filters support bounded pilots/refinements. Wheel contact is never
prescribed. Pin reaction is a force diagnostic; height-step metrics describe the
whole closed-loop quarter assembly, not intrinsic motor latency. Highest passing
tested speed is not a certified maximum. Rigid contacts, estimated inertia,
assumed drag/limits and finite observation windows cannot certify hardware.
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

import nonideal_study as study
import terrain_speed_study as speed_study
from actuator_comparison import candidate_hardware, validate_assumptions
from actuation_limits import torque_limit
from contact_cases import terrain_spec, validate_contact_request

ROOT=Path(__file__).resolve().parent
MOTOR='motor-odrive-m8325s-100kv'
GEARBOXES={'gear-5':'gear-ab90-g5-d19-r156',
           'gear-10':'gear-ab90-g10-d19-r155',
           'gear-20':'gear-aep90-g20-d19-r154'}
CASES=('floating-terrain','pinned-terrain','height-step')
SHARED=('chassisKg','upperLinkKg','lowerLinkKg','wheelKg','alphaDeg',
        'minimumClearanceMm','undersideOffsetMm','shaftCoulombNm',
        'shaftViscousNms','frictionSmoothingRadS','gearboxInputInertiaKgM2',
        'motoringPowerW','brakingPowerW','regenEnergyJ','rideKpNPerM',
        'rideKdNsPerM','dt','outputHz','iterations')


def default_config():
    base=speed_study.default_config()
    return dict(schema='kinefold/gear-response-study-v1',candidateIds=list(GEARBOXES),
        speedsMps=[1.,3.,4.,6.],pinnedSpeedMps=3.,hipBeltRatio=2.,
        shared={k:(500. if k=='outputHz' else base['shared'][k]) for k in SHARED},
        terrain=copy.deepcopy(base['terrain']),noLoadRpm=4800.,peakDurationS=3.,
        reverseEfficiency=.9,leadDistanceMm=200.,totalDistanceMm=1800.,
        evaluationStartDistanceMm=600.,heightStepMm=25.,heightStepTimeS=.1,
        stepDurationS=2.,settlingBandFraction=.02,settlingMinimumHoldS=.2,
        thresholds=dict(maxTrackingRmsMm=5.,minContactFraction=.99,
            minTravelReserveDeg=2.,minClearanceMm=50.),retainCandidateId='gear-10',
        retainFloatingSpeedsMps=[3.,6.],
        assumptionNotice='Three exact gearbox SKUs with the same ODrive motor and ideal extra B2 belt; listed gearbox efficiencies differ. RotorJ is a sheet geometry estimate and missing gearbox-inputJ uses the explicit common assumption. Shaft Coulomb/cogging is constant resisting drag; periodic cogging0. Finite-gain noiseless controller and physical unilateral wheel contact remain active; no wheel-to-ground pin. Pinned chassis force is interval-averaged and cannot be integrated as the floating trajectory. Height-step response is whole-assembly closed-loop motion. Highest passing tested speed depends on editable thresholds and is not a safe hardware speed or a global optimum.')


def finite(value,name,lo,hi):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not lo<=value<=hi:
        raise ValueError(name+' must be finite within '+str((lo,hi)))


def common_config(c,velocity=None):
    base=study.default_config();base.update(c['shared'])
    velocity=c['speedsMps'][0] if velocity is None else velocity
    mm_s=1000*velocity
    base.update(noLoadRpm=c['noLoadRpm'],peakDurationS=c['peakDurationS'],
        reverseEfficiency=c['reverseEfficiency'],terrains=[copy.deepcopy(c['terrain'])],
        terrainSpeedMmS=mm_s,terrainDelayS=c['leadDistanceMm']/mm_s,
        terrainDurationS=c['totalDistanceMm']/mm_s,
        evaluationStartS=c['evaluationStartDistanceMm']/mm_s)
    return study.validate_config(base)


def validate_config(raw):
    template=default_config()
    if not isinstance(raw,dict) or set(raw)!=set(template):raise ValueError('Use exactly the generated configuration fields.')
    c=copy.deepcopy(raw)
    if c['schema']!=template['schema'] or not isinstance(c['assumptionNotice'],str) or not c['assumptionNotice'].strip():raise ValueError('Schema and assumption notice are required.')
    ids=c['candidateIds']
    if not isinstance(ids,list) or not 1<=len(ids)<=3 or any(not isinstance(k,str) for k in ids) or len(set(ids))!=len(ids) or set(ids)-set(GEARBOXES):raise ValueError('Choose1..3 unique predefined gearboxes.')
    if c['retainCandidateId'] not in ids:raise ValueError('The retained candidate must be selected.')
    if not isinstance(c['shared'],dict) or set(c['shared'])!=set(SHARED):raise ValueError('Shared fields differ from template.')
    velocities=c['speedsMps']
    if not isinstance(velocities,list) or not 1<=len(velocities)<=4:raise ValueError('Choose at most four speeds.')
    for v in velocities:finite(v,'speedMps',.2,10.)
    if len(set(velocities))!=len(velocities):raise ValueError('Duplicate speed.')
    finite(c['pinnedSpeedMps'],'pinnedSpeedMps',.2,10.)
    finite(c['hipBeltRatio'],'hipBeltRatio',1.,3.)
    finite(c['noLoadRpm'],'noLoadRpm',1.,1e7)
    finite(c['peakDurationS'],'peakDurationS',.01,100.)
    finite(c['reverseEfficiency'],'reverseEfficiency',.01,1.)
    for k in ('leadDistanceMm','totalDistanceMm','evaluationStartDistanceMm'):finite(c[k],k,1.,4000.)
    if not c['leadDistanceMm']<c['evaluationStartDistanceMm']<c['totalDistanceMm']:raise ValueError('Require lead < evaluation start < total distance.')
    finite(c['heightStepMm'],'heightStepMm',1.,100.)
    finite(c['heightStepTimeS'],'heightStepTimeS',.05,1.)
    finite(c['stepDurationS'],'stepDurationS',.3,4.)
    finite(c['settlingBandFraction'],'settlingBandFraction',.001,.2)
    finite(c['settlingMinimumHoldS'],'settlingMinimumHoldS',.05,1.)
    if c['heightStepTimeS']+c['settlingMinimumHoldS']>=c['stepDurationS']:raise ValueError('Step horizon must contain the required settling hold.')
    t=c['thresholds']
    if not isinstance(t,dict) or set(t)!=set(template['thresholds']):raise ValueError('Threshold keys differ from template.')
    for k in t:finite(t[k],k,0.,1. if k=='minContactFraction' else 1000.)
    retain=c['retainFloatingSpeedsMps']
    if not isinstance(retain,list) or len(retain)>2 or len(set(retain))!=len(retain) or any(v not in velocities for v in retain):raise ValueError('Retain at most two selected floating speeds.')
    for v in set(velocities+[c['pinnedSpeedMps']]):common_config(c,v)
    return c


def selected_hardware(c,catalog,candidate_id):
    motor=next(x for x in catalog['motors'] if x['id']==MOTOR)
    gear=next(x for x in catalog['gearboxes'] if x['id']==GEARBOXES[candidate_id])
    s=c['shared'];a=validate_assumptions(dict(hipBeltRatio=c['hipBeltRatio'],
        unknownGearboxInputInertiaKgM2=s['gearboxInputInertiaKgM2'],noLoadRpm=c['noLoadRpm'],
        peakDurationS=c['peakDurationS'],reverseEfficiency=c['reverseEfficiency'],
        motoringPowerW=s['motoringPowerW'],brakingPowerW=s['brakingPowerW'],
        regenPowerW=s['brakingPowerW'],regenEnergyJ=s['regenEnergyJ'],
        minClearanceMm=s['minimumClearanceMm'],undersideOffsetMm=s['undersideOffsetMm'],
        rideKpNPerM=s['rideKpNPerM'],rideKdNsPerM=s['rideKdNsPerM']))
    hw=candidate_hardware(motor,gear,a);N=gear['ratio']*c['hipBeltRatio'];cfg=hw['actuatorConfig']
    hw['outputCoulombNm']=N*s['shaftCoulombNm'];hw['outputViscousNms']=N*N*s['shaftViscousNms']
    hw['assumptionFlags'].append('Common shaft drag overrides percentage drag; listed efficiency plus explicit drag can overlap')
    speed_cap=c['noLoadRpm']/N
    if cfg['maxInputRpm'] is not None:speed_cap=min(speed_cap,cfg['maxInputRpm']/N)
    if cfg['maxOutputRpm'] is not None:speed_cap=min(speed_cap,cfg['maxOutputRpm']/c['hipBeltRatio'])
    return dict(id=candidate_id,name=motor['name']+' / '+gear['name'],motorId=MOTOR,
        gearboxId=gear['id'],gearRatio=gear['ratio'],hipBeltRatio=c['hipBeltRatio'],totalReduction=N,
        hardware=hw,capability=dict(peakMotoringHipNm=torque_limit(cfg,0.,1e8)['actuatorAvailableNm'],
            peakBrakingHipNmAtPoint1RadS=torque_limit(cfg,.1,-1e8)['actuatorAvailableNm'],
            continuousMotoringHipNm=torque_limit(cfg,0.,1e8,peak_elapsed_s=cfg['peakDurationS']+1)['actuatorAvailableNm'],
            modeledNoLoadHipRpm=speed_cap,modeledNoLoadHipDegS=speed_cap*6,
            reflectedDriveInertiaKgM2=hw['reflectedInertiaKgM2'],forwardEfficiency=cfg['forwardEfficiency']),
        source=dict(catalogRevision=catalog['revision'],motorUrl=motor['sourceUrl'],
            gearboxUrl=gear.get('detailSourceUrl') or gear['sourceUrl'],
            rotorJStatus=motor['rotorInertiaStatus'],gearboxJStatus=gear['inertiaStatus'],
            speedMeaning='Assumed48V no-load envelope plus known gearbox speed caps; not measured loaded speed',
            peakDurationProvenance='ODrive source3s, editable in this study'))


def make_payload(c,candidate,case,engine,velocity=None):
    common=common_config(c,velocity)
    terrain=c['terrain'] if case!='height-step' else dict(c['terrain'],heightMm=0.,rmsMm=0.,variationPercent=0.,gradePercent=0.)
    request=study.make_payload(common,'terrain-stability',candidate['gearRatio'],'losses',engine,terrain)
    hw=candidate['hardware'];request['motorConfig'].update(hipBeltRatio=c['hipBeltRatio'],
        rotorInertiaKgM2=hw['rotorInertiaKgM2'],gearboxInputInertiaKgM2=hw['gearboxInputInertiaKgM2'])
    request['actuatorConfig']=copy.deepcopy(hw['actuatorConfig'])
    request['actuatorConfig'].update(rideTargetStepMm=c['heightStepMm'] if case=='height-step' else 0.,rideTargetStepTimeS=c['heightStepTimeS'])
    request['runConfig']['hipRotorInertiaKgM2']=hw['gearboxOutputInertiaKgM2']
    request['runConfig']['fixture']='pinned-chassis' if case=='pinned-terrain' else 'floating-chassis'
    if case=='height-step':request['runConfig'].update(inputSpeedMmS=0.,duration=c['stepDurationS'],inputDelayS=0.)
    validate_contact_request(request)
    return request


def signed_moments(rows,start,end,field):
    result=speed_study.weighted_moments(rows,start,end,field)
    if result is None:return None
    values=[]
    for a,b,u,v,_dt in speed_study.clipped_segments(rows,start,end):
        x,y=field(a),field(b);values.extend((x+(y-x)*u,x+(y-x)*v))
    result.update(minimum=min(values),maximum=max(values))
    return result


def crossing(rows,time0,level,field):
    for a,b in zip(rows,rows[1:]):
        if b['t']<time0:continue
        left=max(a['t'],time0);fraction=(left-a['t'])/(b['t']-a['t'])
        x=field(a)+(field(b)-field(a))*fraction;y=field(b)
        if x>=level:return left
        if y>=level and y>x:return left+(b['t']-left)*(level-x)/(y-x)
    return None


def step_metrics(rows,c,resolved=True):
    """Actual chassis motion; metrics-only crossings interpolate saved samples."""
    t0=c['heightStepTimeS'];end=c['stepDurationS'];step=c['heightStepMm']
    base=rows[0]['rideTargetHeightMm'];target=base+step;band=step*c['settlingBandFraction']
    full=rows[0]['t']<=t0+1e-10 and rows[-1]['t']>=end-1e-9
    observed=[r for r in rows if r['t']>=t0-1e-10]
    contact=speed_study.weighted_fraction(rows,t0,end,lambda r:r['contactNormalForceN']>1e-6)
    y=lambda r:(r['chassisZMm']-base)/step
    t10=crossing(rows,t0,.1,y);t90=crossing(rows,t0,.9,y)
    enter=None
    bad=[i for i,r in enumerate(rows) if r['t']>=t0-1e-10 and abs(r['chassisZMm']-target)>band]
    if bad and bad[-1]<len(rows)-1:
        a,b=rows[bad[-1]],rows[bad[-1]+1];boundary=target+math.copysign(band,a['chassisZMm']-target)
        enter=a['t']+(b['t']-a['t'])*(boundary-a['chassisZMm'])/(b['chassisZMm']-a['chassisZMm'])
    elif not bad and observed:enter=t0
    hold=(rows[-1]['t']-enter) if enter is not None else 0.
    applied=any(abs(r['rideTargetHeightMm']-target)<1e-8 for r in observed)
    valid=bool(full and resolved and applied and contact is not None and contact>=1-1e-9)
    settled=valid and enter is not None and hold>=c['settlingMinimumHoldS']-1e-10
    reached=t90 is not None
    return dict(commandStepMm=step,commandTimeS=t0,initialTargetHeightMm=base,targetHeightMm=target,
        fullWindowObserved=full,contactFraction=contact,commandStepApplied=applied,validResponseComparison=valid,
        status='numerical-failure' if not resolved else 'incomplete-window' if not full else 'step-command-not-applied' if not applied else 'contact-loss' if not valid else 'target-not-reached' if not reached else 'settled' if settled else 'not-settled-within-observation',
        delayTo10PercentS=t10-t0 if valid and t10 is not None else None,
        riseTime10To90S=t90-t10 if valid and t10 is not None and reached else None,
        timeTo90PercentS=t90-t0 if valid and reached else None,
        overshootPercent=max(0.,max((y(r) for r in observed),default=0.)-1)*100 if valid else None,
        settlingTimeS=enter-t0 if settled else None,settlingObserved=settled,
        settlingBandMm=band,settlingMinimumHoldS=c['settlingMinimumHoldS'],
        finalTrackingErrorMm=rows[-1]['chassisZMm']-target,
        observedCrossings=dict(time10S=t10,time90S=t90,tailBandEntryS=enter,tailHoldS=hold),
        scope='Closed-loop chassis ride-height response of the coupled quarter assembly; not intrinsic motor delay. Crossings interpolate metrics only, never physics frames. Unresolved/incomplete/contact-losing tests have no qualified rise/settling metric.')


def summarize(request,result,c,case,velocity=None):
    common=common_config(c,velocity)
    rows=result['rows'];d=result['diagnostics'];base=study.summarize(request,result,common)
    start=c['heightStepTimeS'] if case=='height-step' else c['evaluationStartDistanceMm']/(velocity*1000)
    end=request['runConfig']['duration'];full=rows[0]['t']<=start+1e-10 and rows[-1]['t']>=end-1e-9
    selected=[r for r in rows if start-1e-10<=r['t']<=end+1e-10]
    contact=speed_study.weighted_fraction(rows,start,end,lambda r:r['contactNormalForceN']>1e-6)
    reserve=min((min(r['theta2']-request['params']['te'],request['params']['tc']-r['theta2']) for r in selected),default=None)
    clearance=min((r['chassisClearanceMm'] for r in selected),default=None)
    error=signed_moments(rows,start,end,lambda r:r['chassisZMm']-r['rideTargetHeightMm'])
    limits=c['thresholds'];reasons=[]
    if not base['numericallyResolved']:reasons.append('numerical-failure')
    if not full:reasons.append('incomplete-window')
    if contact is None or contact<limits['minContactFraction']:reasons.append('contact-fraction')
    if reserve is None or reserve<limits['minTravelReserveDeg']:reasons.append('travel-reserve')
    if clearance is None or clearance<limits['minClearanceMm']:reasons.append('clearance')
    if any(e['type'] in ('extension-stop','compression-stop','underside-contact') for e in result['events']):reasons.append('physical-stop')
    if case=='floating-terrain' and (error is None or error['rms']>limits['maxTrackingRmsMm']):reasons.append('tracking-rms')
    stats=dict(evaluationStartS=start,evaluationEndS=end,fullWindowObserved=full,
        trackingErrorMm=error,contactFraction=contact,contactLossFraction=1-contact if contact is not None else None,
        saturationFraction=speed_study.weighted_fraction(rows,start,end,lambda r:bool(r['actuatorLimited'])),
        jointTorqueNm=signed_moments(rows,start,end,lambda r:r['motorTorqueNm']),
        shaftTorqueNm=signed_moments(rows,start,end,lambda r:r['shaftCommandNm']),
        hipSpeedDegS=signed_moments(rows,start,end,lambda r:r['velocityDegS']),
        shaftRpm=signed_moments(rows,start,end,lambda r:r['shaftRpm']),
        minimumTravelReserveDeg=reserve,minClearanceMm=clearance,passes=not reasons,failureReasons=reasons,
        speedMps=velocity,forcingFrequencyHz=velocity*1000/c['terrain']['periodMm'] if velocity else None,
        scope='Physical wheel contact and free spin; time-weighted saved samples, not substep impact peaks. Saturation alone does not fail a case if all editable tracking/contact/travel/clearance limits pass.')
    base.update(responseMetrics=stats,maxConstraintPositionErrorMm=d.get('maxConstraintPositionErrorMm'),maxPenetrationMm=d.get('maxPenetrationMm'))
    base.pop('terrainMetrics',None)
    if case=='height-step':base['stepMetrics']=step_metrics(rows,c,base['numericallyResolved'])
    if case=='pinned-terrain':
        finite_rows=[r for r in rows if r.get('pinForceZN') is not None]
        delay=request['runConfig']['inputDelayS'];baseline=signed_moments(finite_rows,.2*delay,.8*delay,lambda r:r['pinForceZN'])
        mean=baseline['mean'] if baseline else None
        force=signed_moments(finite_rows,start,end,lambda r:r['pinForceZN'])
        available=bool(force and baseline and force['observedSeconds']>=end-start-1e-9 and baseline['observedSeconds']>=.6*delay-1e-9)
        if not available:stats['passes']=False;stats['failureReasons'].append('pin-data-unavailable')
        base['pinMetrics']=dict(pinDataAvailable=available,pinForceZN=force,
            preTerrainBaselineForceZN=mean,baselineWindowS=[.2*delay,.8*delay],
            baselineSubtractedForceZN=signed_moments(finite_rows,start,end,lambda r:r['pinForceZN']-mean) if mean is not None else None,
            maximumChassisMotionMm=max(abs(r['chassisZMm']-rows[0]['chassisZMm']) for r in rows),
            sign='Positive pinForceZN is upward fixture force: insufficient suspension support. Negative is fixture hold-down: excess upward support.',
            scope='Interval-averaged pin reaction; baseline measured before terrain, not the first spin-up impulse. Absolute support error is retained. Not a floating acceleration prediction or a hardware impact peak.')
    return base


def rank_tested_speeds(records,c):
    results=[]
    for candidate in c['candidateIds']:
        statuses=[]
        for velocity in sorted(c['speedsMps']):
            pair=[r for r in records if r['candidateId']==candidate and r['case']=='floating-terrain' and r['speedMps']==velocity]
            complete=len(pair)==2 and {r['engine'] for r in pair}==set(study.ENGINES)
            passed=complete and all(r['metrics'].get('responseMetrics',{}).get('passes',False) for r in pair)
            status='not-run' if not pair else 'incomplete-pair' if not complete else 'pass' if passed else 'numerical-failure' if not all(r['metrics'].get('numericallyResolved',False) for r in pair) else 'fail'
            statuses.append(dict(speedMps=velocity,bothEnginesPresent=complete,status=status,passes=passed,
                engineStatuses={r['engine']:r['metrics'].get('responseMetrics',{}).get('failureReasons',['engine-error']) for r in pair}))
        passing=[r['speedMps'] for r in statuses if r['passes']];highest=max(passing) if passing else None
        holes=[r['speedMps'] for r in statuses if r['bothEnginesPresent'] and not r['passes'] and highest is not None and r['speedMps']<highest]
        higher=[r['speedMps'] for r in statuses if r['status']=='fail' and highest is not None and r['speedMps']>highest]
        results.append(dict(candidateId=candidate,highestPassingTestedSpeedMps=highest,
            nextHigherNonpassingTestedSpeedMps=min(higher) if higher else None,
            unresolvedOrIncompleteSpeedsMps=[r['speedMps'] for r in statuses if r['status'] in ('numerical-failure','incomplete-pair')],
            notRunSpeedsMps=[r['speedMps'] for r in statuses if r['status']=='not-run'],
            nonpassingTestedSpeedsBelowHighestPass=holes,tested=statuses,
            scope='Both engines must pass editable limits. Not a continuous speed boundary, certified safe maximum, endurance result or globally optimal hardware. Nonmonotone holes forbid inferring an uninterrupted passing range.'))
    return results


def fingerprints():
    result=speed_study.fingerprints();result['gear_response_study.py']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return result


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,allow_nan=False,separators=(',',':')),encoding='utf-8')


def app_local(path):
    resolved=path.resolve()
    if ROOT not in resolved.parents:raise ValueError('Output must stay inside this app.')
    return resolved


def jobs(c,candidates,args):
    for candidate in candidates:
        for case in CASES:
            if args.case and case not in args.case:continue
            velocities=c['speedsMps'] if case=='floating-terrain' else [c['pinnedSpeedMps']] if case=='pinned-terrain' else [None]
            for velocity in velocities:
                if args.speed and velocity is not None and velocity not in args.speed:continue
                for engine in study.ENGINES:
                    if not args.engine or engine in args.engine:yield candidate,case,velocity,engine


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-config',type=Path);parser.add_argument('--config',type=Path);parser.add_argument('--output',type=Path)
    parser.add_argument('--candidate',choices=tuple(GEARBOXES),action='append');parser.add_argument('--case',choices=CASES,action='append')
    parser.add_argument('--speed',type=float,action='append');parser.add_argument('--engine',choices=tuple(study.ENGINES),action='append');parser.add_argument('--dt',type=float)
    args=parser.parse_args()
    if args.write_config:
        target=app_local(args.write_config)
        if target.exists():raise ValueError('Refusing to overwrite settings.')
        write(target,default_config())
        if args.output is None:return
    if args.output is None:parser.error('--output is required to execute.')
    c=json.loads(args.config.read_text(encoding='utf-8')) if args.config else default_config()
    if args.dt is not None:c['shared']['dt']=args.dt
    c=validate_config(c)
    if args.speed and any(v not in set(c['speedsMps']+[c['pinnedSpeedMps']]) for v in args.speed):raise ValueError('Speed filter must select configured speeds.')
    catalog=json.loads((ROOT/'motor-gearbox-catalog.json').read_text(encoding='utf-8'))
    candidates=[selected_hardware(c,catalog,k) for k in c['candidateIds'] if not args.candidate or k in args.candidate]
    if not candidates:raise ValueError('Candidate filter selects no runs.')
    plan=list(jobs(c,candidates,args));prepared=[];reference=None
    for candidate,case,velocity,engine in plan:
        request=make_payload(c,candidate,case,engine,velocity)
        if case!='height-step':
            m=validate_contact_request(request);spatial=speed_study.terrain_signature(terrain_spec(m,request['caseConfig'])['terrain'])
            if reference is None:reference=spatial
            else:speed_study.assert_same_spatial_input(reference,spatial)
        prepared.append((candidate,case,velocity,engine,request))
    if not prepared:raise ValueError('Filters select no runs.')
    hashes=fingerprints();output=app_local(args.output)
    settings=dict(schema='kinefold/gear-response-capture-v1',config=c,candidates=candidates,sourceSHA256=hashes,
        filters={k:getattr(args,k) for k in ('candidate','case','speed','engine')})
    guard=output/'settings.json'
    if guard.exists() and json.loads(guard.read_text())!=settings:raise ValueError('Source/config/filter identity differs; use a fresh folder.')
    write(guard,settings);path=output/'summary.json';records=json.loads(path.read_text()).get('records',[]) if path.exists() else []
    started=time.monotonic()
    for candidate,case,velocity,engine,request in prepared:
        key=(candidate['id'],case,velocity,engine)
        old=next((r for r in records if (r['candidateId'],r['case'],r['speedMps'],r['engine'])==key),None)
        if old:
            if old['payload']!=request:raise ValueError('Cached exact request differs.')
            continue
        tick=time.monotonic();result=None;error=None
        try:result=study.ENGINES[engine](request,stop_at_assessment=False)
        except (ValueError,ArithmeticError,RuntimeError) as exc:error=str(exc)
        tag=f"{candidate['id']}-{case}"+(f'-v{velocity:g}' if velocity is not None else '')+'-'+engine
        retain=candidate['id']==c['retainCandidateId'] and (case!='floating-terrain' or velocity in c['retainFloatingSpeedsMps'])
        capture=tag+'-capture.json' if retain and result is not None else None
        if result is not None:
            if case!='height-step':speed_study.assert_same_spatial_input(reference,speed_study.terrain_signature(result['terrain']))
            metrics=summarize(request,result,c,case,velocity)
            if capture:write(output/capture,dict(payload=request,result=result,sourceSHA256=hashes))
        else:metrics=dict(numericallyResolved=False,termination='engine-error',error=error)
        record=dict(candidateId=candidate['id'],case=case,speedMps=velocity,engine=engine,payload=request,capture=capture,
            runWallSeconds=time.monotonic()-tick,metrics=metrics,warnings=result.get('warnings',[]) if result else [],error=error)
        records.append(record)
        write(path,dict(schema='kinefold/gear-response-result-v1',settings=settings,records=records,
            tradeoff=rank_tested_speeds(records,c),python=platform.python_version(),elapsedWallSeconds=time.monotonic()-started,
            sameSpatialInputVerified=reference is not None,storage='At most36 base runs; exact requests/metrics retained, raw captures only one candidate selected cases. No wheel-to-ground binding. Failures retained.'))
        print(json.dumps({k:record[k] for k in ('candidateId','case','speedMps','engine','runWallSeconds')}|
            dict(resolved=metrics['numericallyResolved'],termination=metrics['termination'],
                passes=metrics.get('responseMetrics',{}).get('passes'),stepStatus=metrics.get('stepMetrics',{}).get('status'))),flush=True)
    columns=('candidateId','case','speedMps','engine','numericallyResolved','termination','passes',
        'trackingRmsMm','contactFraction','saturationFraction','minimumTravelReserveDeg','minClearanceMm',
        'jointPeakTorqueNm','shaftPeakTorqueNm','shaftPeakRpm','delayTo10PercentS','riseTime10To90S',
        'settlingTimeS','overshootPercent','pinRmsZN','pinBaselineZN','pinBaselineSubtractedRmsZN')
    with (output/'summary.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader()
        for record in records:
            m=record['metrics'];r=m.get('responseMetrics',{});s=m.get('stepMetrics',{});p=m.get('pinMetrics',{})
            writer.writerow(dict({k:record.get(k,m.get(k,r.get(k,s.get(k)))) for k in columns},
                trackingRmsMm=(r.get('trackingErrorMm') or {}).get('rms'),
                jointPeakTorqueNm=(r.get('jointTorqueNm') or {}).get('maximumAbsolute'),
                shaftPeakTorqueNm=(r.get('shaftTorqueNm') or {}).get('maximumAbsolute'),
                shaftPeakRpm=(r.get('shaftRpm') or {}).get('maximumAbsolute'),
                pinRmsZN=(p.get('pinForceZN') or {}).get('rms'),pinBaselineZN=p.get('preTerrainBaselineForceZN'),
                pinBaselineSubtractedRmsZN=(p.get('baselineSubtractedForceZN') or {}).get('rms')))
    print('SUMMARY '+str(path),flush=True)


if __name__=='__main__':main()
