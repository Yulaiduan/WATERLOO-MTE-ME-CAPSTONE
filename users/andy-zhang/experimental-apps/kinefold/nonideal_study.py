"""Capture matched finite-link jump, landing and terrain motor-loss experiments.

Run app Python: python nonideal_study.py --write-config .preview/nonideal.json
then python nonideal_study.py --config .preview/nonideal.json --output .preview/run
Inputs: explicit editable study JSON (kg, mm, deg, s, shaft Nm/Nm s/rad/kg m2).
Outputs: exact replayable requests, actual engine rows/frames and JSON/CSV metrics
inside the app. No live design writes. This is a vertical-heave quarter model,
not full-vehicle stability or measured hardware; ideal noiseless finite-gain
feedback is bounded by torque/speed/power and physical inertia, not perfect
tracking. Coulomb includes the user's constant cogging-drag approximation;
periodic conservative cogging is zero. Numerical residuals are not absorption.
"""
import argparse
import copy
import csv
import hashlib
import json
import math
import platform
import statistics
import time
from pathlib import Path

from actuation_limits import ACTUATOR_DEFAULTS
from analytical_contact import simulate_contact as analytical
from contact_dynamics import simulate_contact as pymunk
from contact_cases import CASE_DEFAULTS, validate_contact_request
from motor_model import DEFAULTS as MOTOR_DEFAULTS
from terrain_profiles import CATALOG

ROOT = Path(__file__).resolve().parent
ENGINES = {'analytical': analytical, 'pymunk': pymunk}
EFFECTS = ('reference', 'inertia', 'losses')
SOURCE_FILES = ('nonideal_study.py', 'motor_model.py', 'actuation_limits.py',
    'dynamic_model.py', 'finite_contact_model.py', 'contact_cases.py',
    'analytical_contact.py', 'contact_dynamics.py', 'finite_pymunk_contact.py',
    'motor_rotor_constraint.py', 'torque_targets.py', 'terrain_profiles.py', 'terrain-catalog.json',
    'saved-configurations/vsl-v45-nominal-alpha0.json')


def default_config():
    """Return explicit unmeasured comparison assumptions, never source ratings."""
    return dict(schema='kinefold/nonideal-study-v1',
        chassisKg=45., upperLinkKg=1., lowerLinkKg=1., wheelKg=.5,
        alphaDeg=20., dropMm=2000., jumpTargetMm=2000.,
        minimumClearanceMm=50., undersideOffsetMm=50.,
        ratios=[10., 20., 40.], terrainRatios=[20.],
        effects=list(EFFECTS), terrainEffects=['reference', 'losses'],
        rotorInertiaKgM2=.000825, gearboxInputInertiaKgM2=.0001,
        shaftCoulombNm=.05, shaftViscousNms=.0008, frictionSmoothingRadS=10.,
        shaftPeakNm=17., noLoadRpm=6000., gearboxOutputPeakNm=250.,
        motoringPowerW=5000., brakingPowerW=5000., regenEnergyJ=5000.,
        peakDurationS=2., forwardEfficiency=1., reverseEfficiency=1.,
        rideKpNPerM=5000., rideKdNsPerM=350.,
        dt=.00025, outputHz=200., iterations=120,
        jumpDurationS=2., landingDurationS=1.5, terrainDurationS=4.5,
        terrainSpeedMmS=400., terrainDelayS=.5, evaluationStartS=1.5,
        terrains=[
            dict(id='flat',heightMm=0.,rmsMm=0.,representation='obstacles',periodMm=600.,variationPercent=0.,gradePercent=0.,seed=481),
            dict(id='smooth-bumps',heightMm=50.,rmsMm=0.,representation='obstacles',periodMm=600.,variationPercent=0.,gradePercent=0.,seed=481),
            dict(id='seeded-rough',heightMm=50.,rmsMm=15.,representation='roughness',periodMm=600.,variationPercent=25.,gradePercent=0.,seed=481),
            dict(id='rough-5pct-grade',heightMm=50.,rmsMm=15.,representation='roughness',periodMm=600.,variationPercent=25.,gradePercent=5.,seed=481)],
        assumptionNotice='All drive inertia, Coulomb/cogging drag, viscous loss, speed, power and gearbox limits are editable illustrative placeholders, not measured ratings. Shaft peak17Nm is an example, not a selected motor. Efficiency1 isolates explicit drag, avoiding duplicated efficiency loss. Synthetic terrain amplitudes override the catalogue envelope; profile ID only selects the common contour generator. V4 support force/preload scale by chassis mass and cos(alpha), with unchanged local route; not exact gravity cancellation.')


def validate_config(raw):
    template=default_config()
    if not isinstance(raw,dict) or set(raw)!=set(template):
        raise ValueError('Study requires exactly the keys in --write-config output.')
    c=copy.deepcopy(raw)
    if c['schema']!=template['schema'] or not isinstance(c['assumptionNotice'],str) or not c['assumptionNotice'].strip():
        raise ValueError('Study schema and nonempty assumption notice are required.')
    for k,v in c.items():
        if isinstance(template[k],(int,float)):
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:
                raise ValueError(k+' must be finite/nonnegative.')
    for k in ('chassisKg','upperLinkKg','lowerLinkKg','wheelKg','shaftPeakNm','noLoadRpm','gearboxOutputPeakNm','dt','outputHz','frictionSmoothingRadS','terrainSpeedMmS'):
        if c[k]<=0:raise ValueError(k+' must be positive.')
    if not 0<=c['alphaDeg']<=45 or not 0<c['dt']<=.01 or not 10<=c['outputHz']<=1000:
        raise ValueError('Bound alpha0..45, dt0...01 and outputHz10..1000.')
    if c['dropMm']>5000 or c['jumpTargetMm']>5000 or not 0<=c['evaluationStartS']<c['terrainDurationS']:
        raise ValueError('Invalid target or evaluation window.')
    for k in ('forwardEfficiency','reverseEfficiency'):
        if not .01<=c[k]<=1:raise ValueError(k+' requires .01..1.')
    for k in ('ratios','terrainRatios'):
        if not isinstance(c[k],list) or not 1<=len(c[k])<=6 or len(set(c[k]))!=len(c[k]):raise ValueError(k+' requires1..6 unique values.')
        if any(isinstance(n,bool) or not isinstance(n,(int,float)) or not math.isfinite(n) or not 1<=n<=100 for n in c[k]):raise ValueError('Study gear ratios require1..100.')
    for k in ('effects','terrainEffects'):
        if not isinstance(c[k],list) or not c[k] or len(set(c[k]))!=len(c[k]) or set(c[k])-set(EFFECTS):raise ValueError(k+' has unknown/duplicate effects.')
    if not isinstance(c['terrains'],list) or not 1<=len(c['terrains'])<=6:raise ValueError('Choose1..6 explicit synthetic terrain inputs.')
    ids=set()
    for terrain in c['terrains']:
        if not isinstance(terrain,dict) or set(terrain)!=set(template['terrains'][0]):raise ValueError('Terrain requires exactly the template fields.')
        if not isinstance(terrain['id'],str) or not terrain['id'] or any(x not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for x in terrain['id']) or terrain['id'] in ids:raise ValueError('Terrain IDs require unique lowercase slugs.')
        ids.add(terrain['id'])
        from terrain_profiles import validate_terrain
        validate_terrain(terrain_config(terrain))
    # Model's own validators additionally enforce integration/collision bounds.
    return c


def terrain_config(t):
    return dict(schema='kinefold/terrain-v2',catalogRevision=CATALOG['revision'],
        profileId='maintained-natural-trail',severity='typical',
        **{k:v for k,v in t.items() if k!='id'})


def make_payload(c,kind,ratio,effect,engine,terrain=None):
    base=json.loads((ROOT/'saved-configurations/vsl-v45-nominal-alpha0.json').read_text(encoding='utf-8'))
    p=base['params'];original_mass=p['m1']
    p.update(m1=c['chassisKg']/4,m2=c['upperLinkKg'],m3=c['lowerLinkKg'],m5=0.,m6=c['wheelKg'],
        alpha=c['alphaDeg'],theta2=135.,te=100.,tc=165.,loadMode='weight',Fx=0.,Ft=0.,beta=0.,Tab0=0.,Tcd0=0.,Tef0=0.)
    p['Fn']=p['Fz']=(p['m1']+p['m2']+p['m3']+p['m6'])*p['g']
    scale=p['m1']/original_mass*math.cos(math.radians(c['alphaDeg']))
    p['springK']*=scale;p['p0']*=scale
    duration=c[{'jump':'jumpDurationS','landing':'landingDurationS','terrain-stability':'terrainDurationS'}[kind]]
    run={**base['solverConfig'],'duration':duration,'dt':c['dt'],'outputHz':c['outputHz'],
        'iterations':c['iterations'],'initialVelocityDegS':0.,'hipTorqueNm':0.,'dampingNms':0.,
        'hipRotorInertiaKgM2':0.,'inputRiseMm':0.,'inputHeightMm':0.,
        'inputSpeedMmS':c['terrainSpeedMmS'],'inputDelayS':c['terrainDelayS']}
    jmotor=c['rotorInertiaKgM2'] if effect!='reference' else 0.
    jgear=c['gearboxInputInertiaKgM2'] if effect!='reference' else 0.
    motor={**MOTOR_DEFAULTS,'enabled':True,'gearRatio':ratio,'rotorInertiaKgM2':jmotor,
        'coggingAmplitudeNm':0.,'coulombFrictionNm':c['shaftCoulombNm'] if effect=='losses' else 0.,
        'viscousFrictionNms':c['shaftViscousNms'] if effect=='losses' else 0.,
        'frictionVelocityScaleRadS':c['frictionSmoothingRadS'],'commandBasis':'joint'}
    if 'gearboxInputInertiaKgM2' in MOTOR_DEFAULTS:motor['gearboxInputInertiaKgM2']=jgear
    elif jgear:
        raise ValueError('This study needs the updated motor model with explicit gearboxInputInertiaKgM2; do not fold it into the shaft rotor value.')
    actuator={**ACTUATOR_DEFAULTS,'ratio':ratio,'peakShaftNm':c['shaftPeakNm'],
        'noLoadRpm':c['noLoadRpm'],'gearboxPeakNm':c['gearboxOutputPeakNm'],
        'motoringPowerW':c['motoringPowerW'],'brakingPowerW':c['brakingPowerW'],
        'regenPowerW':c['brakingPowerW'],'regenEnergyJ':c['regenEnergyJ'],
        'peakDurationS':c['peakDurationS'],'forwardEfficiency':c['forwardEfficiency'],
        'reverseEfficiency':c['reverseEfficiency'],'minClearanceMm':c['minimumClearanceMm'],
        'undersideOffsetMm':c['undersideOffsetMm'],'rideKpNPerM':c['rideKpNPerM'],'rideKdNsPerM':c['rideKdNsPerM']}
    request=dict(engine=engine,params=p,runConfig=run,motorConfig=motor,actuatorConfig=actuator,
        contactConfig=dict(mode='terrain-contact',drive='free',friction=.8,restitution=0.),
        caseConfig={**CASE_DEFAULTS,'kind':kind,'jumpTorqueNm':c['gearboxOutputPeakNm'],
            'landingDropMm':c['dropMm'],'landingOpenFraction':1.,
            'landingBrakeTorqueNm':c['gearboxOutputPeakNm'],'landingBrakeLimitNm':c['gearboxOutputPeakNm'],
            'brakeStrategy':'entered','undersideOffsetMm':c['undersideOffsetMm']})
    if terrain is not None:request['terrainConfig']=terrain_config(terrain)
    validate_contact_request(request)
    return request


def moments(values):
    return dict(mean=statistics.fmean(values),variance=statistics.pvariance(values),
        std=statistics.pstdev(values),rms=math.sqrt(statistics.fmean(v*v for v in values)),
        peakToPeak=max(values)-min(values),maximumAbsolute=max(abs(v) for v in values))


def summarize(request,result,c):
    rows=result['rows'];first,last=rows[0],rows[-1];d=result['diagnostics'];cm=result['caseMetrics'];obs=result.get('targetObservations',{})
    termination=d['termination'];numerical=termination in ('duration','assessment-outcome','underside-contact') and d.get('maxPenetrationMm',0)<=1 and d.get('maxConstraintPositionErrorMm',0)<=1
    kind=request['caseConfig']['kind'];landing=bool(cm.get('landingSuccess')) and numerical and cm['minimumUndersideClearanceMm']>=c['minimumClearanceMm']
    jump=obs.get('jumpComRiseMm');jump_observed=bool(obs.get('genuineFirstFlight')) and jump is not None
    ev=[e['type'] for e in result['events']]
    summary=dict(termination=termination,numericallyResolved=numerical,elapsedSeconds=last['t'],
        finiteLinkDynamics=bool(d.get('finiteLinkDynamics')),totalMassKg=sum(request['params']['m'+k] for k in ('1','2','3','5','6')),
        grossFourCornerMassKg=4*sum(request['params']['m'+k] for k in ('1','2','3','5','6')),
        reflectedDriveInertiaKgM2=d['reflectedHipInertiaKgM2'],
        outcome=cm.get('outcome'),landingSuccessAboveClearance=landing if kind=='landing' else None,
        jumpCOMRiseMm=jump if jump_observed else None,jumpChassisRiseMm=(obs.get('firstFlightApex',{}).get('chassisZMm',0)-obs.get('takeoff',{}).get('chassisZMm',0)) if jump_observed and obs.get('firstFlightApex') else None,
        jumpObserved=jump_observed if kind=='jump' else None,jumpTargetReached=bool(jump_observed and jump>=c['jumpTargetMm']) if kind=='jump' else None,
        minClearanceMm=cm.get('minimumUndersideClearanceMm'),firstArrestTimeS=cm.get('firstArrestTimeS'),
        impactTimeS=cm.get('impactTimeS'),takeoffTimeS=cm.get('takeoffTimeS'),
        motorWorkJ=last['motorWorkJ'],motorDissipatedJ=last['motorDissipatedJ'],
        springStoredJ=last['springEnergyJ']-first['springEnergyJ'],gravityReleasedJ=first['gravityEnergyJ']-last['gravityEnergyJ'],
        remainingDriveKineticJ=last['rotorKineticJ'],maxDriveKineticJ=max(r['rotorKineticJ'] for r in rows),
        energyResidualJ=d['energyBalanceResidualJ'],peakDeliveredTorqueNm=max(abs(r['motorTorqueNm']) for r in rows),
        peakShaftRpm=max(abs(r.get('shaftRpm',0)) for r in rows),eventTypes=ev,
        sampledPeakJointAccelerationDegS2=max((abs(b['velocityDegS']-a['velocityDegS'])/(b['t']-a['t']) for a,b in zip(rows,rows[1:]) if b['t']>a['t']+1e-12),default=0.),
        sampledPeakChassisAccelerationMmS2=max((abs(b['chassisVelocityMmS']-a['chassisVelocityMmS'])/(b['t']-a['t']) for a,b in zip(rows,rows[1:]) if b['t']>a['t']+1e-12),default=0.),
        accelerationMeaning='Differences between saved output velocities; rigid impacts/stops are impulses, not physical finite peak accelerations.')
    if kind=='terrain-stability':
        start=c['evaluationStartS'];end=c['terrainDurationS'];selected=[r for r in rows if start-1e-9<=r['t']<=end+1e-9]
        complete=bool(selected and selected[0]['t']<=start+1/c['outputHz']+1e-9 and selected[-1]['t']>=end-1/c['outputHz']-1e-9)
        minimum=min((r['chassisClearanceMm'] for r in selected),default=None)
        physical_failure='compression-stop' in ev or 'underside-contact' in ev or (minimum is not None and minimum<c['minimumClearanceMm'])
        summary['terrainMetrics']=dict(evaluationStartS=start,evaluationEndS=end,sampleCount=len(selected),
            fullWindowObserved=complete,usableComparison=complete and numerical,
            heaveTestPassed=complete and numerical and not physical_failure,
            status='numerical-failure' if not numerical else 'incomplete-window' if not complete else 'physical-limit' if physical_failure else 'completed-window',
            heightMm=moments([r['chassisZMm'] for r in selected]) if selected else None,
            desiredHeightMm=moments([r['rideTargetHeightMm'] for r in selected]) if selected else None,
            trackingErrorMm=moments([r['chassisZMm']-r['rideTargetHeightMm'] for r in selected]) if selected else None,
            contactFraction=statistics.fmean(r['contactNormalForceN']>1e-6 for r in selected) if selected else None,
            saturationFraction=statistics.fmean(bool(r['actuatorLimited']) for r in selected) if selected else None,
            minClearanceMm=minimum,
            scope='Noiseless finite-gain hardware-limited heave feedback; not pitch/roll stability. Raw world height includes intended grade rise; tracking error subtracts the captured grade-following target.')
    return summary


def source_hashes():
    return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,allow_nan=False,separators=(',',':')),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-config',type=Path)
    parser.add_argument('--config',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--dt',type=float)
    parser.add_argument('--case',choices=('jump','landing','terrain-stability'),action='append')
    parser.add_argument('--ratio',type=float,action='append')
    parser.add_argument('--effect',choices=EFFECTS,action='append')
    parser.add_argument('--terrain',action='append')
    parser.add_argument('--engine',choices=tuple(ENGINES),action='append')
    args=parser.parse_args()
    if args.write_config:
        dest=args.write_config.resolve()
        if ROOT not in dest.parents:raise ValueError('Config output stays inside app.')
        write(dest,default_config());print('CONFIG '+str(dest),flush=True)
        if not args.output:return
    if args.output is None:parser.error('--output is required for execution.')
    output=args.output.resolve()
    if ROOT not in output.parents:raise ValueError('Study output stays inside Kinefold.')
    c=validate_config(json.loads(args.config.read_text(encoding='utf-8')) if args.config else default_config())
    if args.dt is not None:c['dt']=args.dt;c=validate_config(c)
    output.mkdir(parents=True,exist_ok=True);hashes=source_hashes()
    settings=dict(config=c,sourceSHA256=hashes,filters={k:getattr(args,k) for k in ('case','ratio','effect','terrain','engine')})
    guard=output/'settings.json'
    if guard.exists() and json.loads(guard.read_text(encoding='utf-8'))!=settings:raise ValueError('Output source/config/filter identity differs; use a new folder.')
    write(guard,settings);write(output/'README.json',dict(purpose=__doc__,settings='settings.json',summary='summary.json',captures='*-capture.json'))
    records=[];started=time.monotonic()
    for kind in ('jump','landing','terrain-stability'):
        if args.case and kind not in args.case:continue
        ratios=c['terrainRatios'] if kind=='terrain-stability' else c['ratios']
        effects=c['terrainEffects'] if kind=='terrain-stability' else c['effects']
        for ratio in ratios:
            if args.ratio and ratio not in args.ratio:continue
            for effect in effects:
                if args.effect and effect not in args.effect:continue
                for terrain in c['terrains'] if kind=='terrain-stability' else [None]:
                    if terrain and args.terrain and terrain['id'] not in args.terrain:continue
                    for engine,sim in ENGINES.items():
                        if args.engine and engine not in args.engine:continue
                        request=make_payload(c,kind,ratio,effect,engine,terrain)
                        tag=f'{kind}-n{ratio:g}-{effect}-{terrain["id"] if terrain else "flat"}-{engine}'
                        capture=output/(tag+'-capture.json');tick=time.monotonic()
                        if capture.exists():
                            saved=json.loads(capture.read_text(encoding='utf-8'))
                            if saved['payload']!=request or saved['sourceSHA256']!=hashes:raise ValueError('Cached capture identity differs.')
                            result=saved['result']
                        else:
                            result=sim(request,stop_at_assessment=kind!='terrain-stability')
                            write(capture,dict(payload=request,result=result,sourceSHA256=hashes))
                        item=dict(case=kind,ratio=ratio,effect=effect,terrain=terrain['id'] if terrain else None,engine=engine,
                            capture=capture.name,runWallSeconds=time.monotonic()-tick,metrics=summarize(request,result,c))
                        records.append(item);report=dict(schema='kinefold/nonideal-study-result-v1',settings=settings,records=records,
                            python=platform.python_version(),elapsedWallSeconds=time.monotonic()-started)
                        write(output/'summary.json',report)
                        print(json.dumps({k:item[k] for k in ('case','ratio','effect','terrain','engine','runWallSeconds')}|dict(outcome=item['metrics']['outcome'],termination=item['metrics']['termination']),allow_nan=False),flush=True)
    if not records:raise ValueError('Filters selected no runs.')
    fields=('case','ratio','effect','terrain','engine','termination','jumpCOMRiseMm','landingSuccessAboveClearance','motorWorkJ','motorDissipatedJ','remainingDriveKineticJ','peakDeliveredTorqueNm','energyResidualJ','heightVarianceMm2','trackingVarianceMm2','trackingRmsMm','saturationFraction','terrainStatus')
    with (output/'summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in records:
            m=r['metrics'];t=m.get('terrainMetrics',{})
            writer.writerow({k:r[k] if k in r else m.get(k) for k in fields}|dict(
                heightVarianceMm2=(t.get('heightMm') or {}).get('variance'),trackingVarianceMm2=(t.get('trackingErrorMm') or {}).get('variance'),
                trackingRmsMm=(t.get('trackingErrorMm') or {}).get('rms'),saturationFraction=t.get('saturationFraction'),terrainStatus=t.get('status')))
    print('SUMMARY '+str(output/'summary.json'),flush=True)


if __name__=='__main__':main()
