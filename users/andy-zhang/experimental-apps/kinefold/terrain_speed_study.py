"""Run a bounded same-spatial-terrain speed study with a configurable hip belt.

Run app Python: python terrain_speed_study.py --write-config .preview/speed.json
then python terrain_speed_study.py --config .preview/speed.json --output .preview/speed
Inputs: explicit kg/mm/deg/s, shaft Nm/Nm s/kg m2 assumptions and two exact
catalogue motors with one gearbox. Outputs source-guarded JSON/CSV with exact
requests, weighted metrics and raw ODrive captures only, inside this app.
At most 20 runs: four speeds, two motors, two independent engines, plus ODrive
jump/landing. No catalogue search or live-design writes. Ideal lossless added
belt; finite-gain heave feedback, not full-vehicle stability or hardware proof.
Metric interpolation never changes physics or animation frames. Estimated
rotor/gear inertia, approximate torque-speed envelopes and drag remain assumptions.
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
import workflow_example as example
from actuator_comparison import candidate_hardware, validate_assumptions
from contact_cases import terrain_spec, validate_contact_request

ROOT = Path(__file__).resolve().parent
MOTORS = {'flipsky-80100': 'motor-flipsky-80100-130kv',
          'odrive-8325': 'motor-odrive-m8325s-100kv'}
GEARBOX = 'gear-ab90-g10-d19-r155'
KINDS = ('terrain-stability', 'jump', 'landing')
SHARED = tuple(k for k in example.SHARED_KEYS if k not in
    ('noLoadRpm', 'peakDurationS', 'terrainDurationS', 'terrainSpeedMmS',
     'terrainDelayS', 'evaluationStartS'))


def default_config():
    base = example.default_config()
    return dict(schema='kinefold/terrain-speed-study-v1',
        candidateIds=list(MOTORS), speedsMps=[.4, 1., 2., 3.], hipBeltRatio=2.,
        shared={k: base[k] for k in SHARED}, terrain=copy.deepcopy(base['terrain']),
        noLoadRpm={'flipsky-80100': 6240., 'odrive-8325': 4800.},
        peakDurationS={'flipsky-80100': 2., 'odrive-8325': 3.},
        reverseEfficiency=.9, leadDistanceMm=200., totalDistanceMm=1800.,
        evaluationStartDistanceMm=600., retainCandidateId='odrive-8325',
        assumptionNotice='Extra belt is ideal/rigid/lossless with no added hardware inertia; base gearbox10 times belt2 gives total20. ODrive source Kt .083 Nm/A phase amplitude times80A peak (3s) gives6.64Nm and40A free-air gives3.32Nm. No-load envelopes are ideal Kv times48V (4800/6240rpm), not measured loaded curves; gearbox input limit still applies. Gear-input J, Coulomb/cogging and viscous drag are editable placeholders; rotorJ is a sheet geometry estimate. Same spatial terrain and lead at every speed, shorter time for fast cases. Wheel starts at zero spin; finite-gain controller and rigid contacts are experimental quarter-heave models, not full-body stability.')


def positive(value, name, lo=0., hi=1e7, inclusive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not (lo <= value <= hi if inclusive else lo < value <= hi):
        raise ValueError(name+' is outside its finite range.')


def common_config(c, speed=None):
    result = study.default_config()
    result.update(c['shared'])
    result.update(terrains=[copy.deepcopy(c['terrain'])],
        noLoadRpm=c['noLoadRpm']['odrive-8325'], peakDurationS=3.,
        frictionSmoothingRadS=c['shared']['frictionSmoothingRadS'])
    velocity = (speed if speed is not None else c['speedsMps'][0])*1000
    result.update(terrainSpeedMmS=velocity,
        terrainDelayS=c['leadDistanceMm']/velocity,
        terrainDurationS=c['totalDistanceMm']/velocity,
        evaluationStartS=c['evaluationStartDistanceMm']/velocity)
    return study.validate_config(result)


def validate_config(raw):
    default = default_config()
    if not isinstance(raw, dict) or set(raw) != set(default):
        raise ValueError('Use exactly the --write-config fields.')
    c = copy.deepcopy(raw)
    if c['schema'] != default['schema'] or not isinstance(c['assumptionNotice'], str) or not c['assumptionNotice'].strip():
        raise ValueError('Schema and explicit assumption notice are required.')
    ids = c['candidateIds']
    if not isinstance(ids, list) or not 1 <= len(ids) <= 2 or any(not isinstance(k, str) for k in ids) or len(set(ids)) != len(ids) or set(ids)-set(MOTORS):
        raise ValueError('Choose one or two unique predefined motors.')
    if c['retainCandidateId'] not in ids:
        raise ValueError('The one retained candidate must be selected.')
    speeds = c['speedsMps']
    if not isinstance(speeds, list) or not 1 <= len(speeds) <= 4:
        raise ValueError('Choose at most four speeds.')
    for speed in speeds: positive(speed, 'speedMps', .2, 5., inclusive=True)
    if len(set(speeds)) != len(speeds): raise ValueError('Duplicate speed.')
    positive(c['hipBeltRatio'], 'hipBeltRatio', 1., 3., inclusive=True)
    positive(c['reverseEfficiency'], 'reverseEfficiency', .01, 1., inclusive=True)
    for key in ('leadDistanceMm', 'totalDistanceMm', 'evaluationStartDistanceMm'):
        positive(c[key], key, 0., 4000.)
    if not c['leadDistanceMm'] < c['evaluationStartDistanceMm'] < c['totalDistanceMm']:
        raise ValueError('Lead < evaluation start < total distance is required.')
    if not isinstance(c['shared'], dict) or set(c['shared']) != set(SHARED):
        raise ValueError('Shared assumptions differ from template.')
    for key in ('noLoadRpm', 'peakDurationS'):
        if not isinstance(c[key], dict) or set(c[key]) != set(MOTORS): raise ValueError(key+' needs both motor entries.')
        for value in c[key].values(): positive(value, key)
    for speed in speeds: common_config(c, speed)
    return c


def selected_hardware(c, catalog, candidate_id):
    motor = next(x for x in catalog['motors'] if x['id'] == MOTORS[candidate_id])
    gear = next(x for x in catalog['gearboxes'] if x['id'] == GEARBOX)
    s = c['shared']
    assumptions = validate_assumptions(dict(hipBeltRatio=c['hipBeltRatio'],
        unknownGearboxInputInertiaKgM2=s['gearboxInputInertiaKgM2'],
        noLoadRpm=c['noLoadRpm'][candidate_id], reverseEfficiency=c['reverseEfficiency'],
        motoringPowerW=s['motoringPowerW'], brakingPowerW=s['brakingPowerW'],
        regenPowerW=s['brakingPowerW'], regenEnergyJ=s['regenEnergyJ'],
        peakDurationS=c['peakDurationS'][candidate_id], minClearanceMm=s['minimumClearanceMm'],
        undersideOffsetMm=s['undersideOffsetMm'], rideKpNPerM=s['rideKpNPerM'],
        rideKdNsPerM=s['rideKdNsPerM']))
    hardware = candidate_hardware(motor, gear, assumptions)
    total = gear['ratio']*c['hipBeltRatio']
    hardware['outputCoulombNm'] = total*s['shaftCoulombNm']
    hardware['outputViscousNms'] = total**2*s['shaftViscousNms']
    hardware['assumptionFlags'].append('Common shaft Coulomb/cogging and viscous placeholders override percentage drag; forward efficiency plus explicit drag may overlap')
    return dict(id=candidate_id, motorId=motor['id'], gearboxId=gear['id'],
        name=motor['name']+' / '+gear['name'], gearRatio=gear['ratio'],
        hipBeltRatio=c['hipBeltRatio'], totalReduction=total, hardware=hardware,
        source=dict(catalogRevision=catalog['revision'], motorUrl=motor['sourceUrl'],
            gearboxUrl=gear.get('detailSourceUrl') or gear['sourceUrl'],
            peakShaftNm=motor['peakTorqueNm'], continuousShaftNm=motor.get('continuousTorqueNm'),
            rotorJStatus=motor['rotorInertiaStatus'], gearboxInputJStatus=gear['inertiaStatus'],
            noLoadRpmAssumption=c['noLoadRpm'][candidate_id],
            peakDurationS=c['peakDurationS'][candidate_id],
            peakDurationProvenance='ODrive documentation3s' if candidate_id=='odrive-8325' else 'editable placeholder'))


def make_payload(c, candidate, kind, engine, speed=None):
    common = common_config(c, speed)
    hw = candidate['hardware']; actuator = hw['actuatorConfig']
    request = study.make_payload(common, kind, candidate['gearRatio'], 'losses', engine,
        c['terrain'] if kind == 'terrain-stability' else None)
    request['motorConfig'].update(hipBeltRatio=c['hipBeltRatio'],
        rotorInertiaKgM2=hw['rotorInertiaKgM2'], gearboxInputInertiaKgM2=hw['gearboxInputInertiaKgM2'])
    request['actuatorConfig'] = copy.deepcopy(actuator)
    hip_cap = actuator['gearboxPeakNm']*c['hipBeltRatio']
    request['caseConfig'].update(jumpTorqueNm=hip_cap, landingBrakeTorqueNm=hip_cap, landingBrakeLimitNm=hip_cap)
    request['runConfig']['hipRotorInertiaKgM2'] = hw['gearboxOutputInertiaKgM2']
    validate_contact_request(request)
    return request


def clipped_segments(rows, start, end):
    """Yield saved-row intervals clipped to a metric window, never modify rows."""
    if end <= start: raise ValueError('Empty metric window.')
    for a, b in zip(rows, rows[1:]):
        if b['t'] <= a['t']: raise ValueError('Saved row times must strictly increase.')
        left, right = max(start, a['t']), min(end, b['t'])
        if right > left:
            dt = b['t']-a['t']
            yield a, b, (left-a['t'])/dt, (right-a['t'])/dt, right-left


def weighted_moments(rows, start, end, field):
    total = first = second = 0.; values = []
    for a, b, u, v, dt in clipped_segments(rows, start, end):
        x, y = field(a), field(b)
        lo, hi = x+(y-x)*u, x+(y-x)*v
        if not all(math.isfinite(z) for z in (lo, hi)): raise ValueError('Nonfinite metric value.')
        total += dt; first += dt*(lo+hi)/2; second += dt*(lo*lo+lo*hi+hi*hi)/3
        values.extend((lo, hi))
    if total == 0: return None
    mean = first/total; variance = max(0., second/total-mean*mean)
    return dict(mean=mean, variance=variance, std=math.sqrt(variance),
        rms=math.sqrt(max(0., second/total)), peakToPeak=max(values)-min(values),
        maximumAbsolute=max(abs(v) for v in values), observedSeconds=total,
        method='Exact integral of piecewise-linear saved samples; not engine substep extrema')


def weighted_fraction(rows, start, end, predicate):
    """Left-held sampled Boolean fraction; no claim of exact contact transition."""
    total = positive_time = 0.
    for a, _b, _u, _v, dt in clipped_segments(rows, start, end):
        total += dt; positive_time += dt*bool(predicate(a))
    return positive_time/total if total else None


def terrain_signature(terrain):
    """Only spatial geometry/seed/phase; velocity/time metadata intentionally varies."""
    stats = terrain['statistics']
    return dict(contourMm=terrain['contourMm'], baseSegmentMm=terrain['baseSegmentMm'],
        profile=terrain['profile'], cellCount=stats['cellCount'], startCycle=stats['startCycle'],
        seed=terrain['seed'], variationPercent=terrain['variationPercent'],
        referenceWheelWorldXMm=terrain['referenceWheelWorldXMm'])


def assert_same_spatial_input(left, right):
    def compare(a, b):
        if isinstance(a, dict):
            if not isinstance(b, dict) or set(a) != set(b): raise ValueError('Terrain spatial keys differ.')
            for key in a: compare(a[key], b[key])
        elif isinstance(a, list):
            if not isinstance(b, list) or len(a) != len(b): raise ValueError('Terrain contour lengths differ.')
            for x, y in zip(a, b): compare(x, y)
        elif isinstance(a, (int, float)) and not isinstance(a, bool):
            if not isinstance(b, (int, float)) or not math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-9):
                raise ValueError('Terrain spatial values differ.')
        elif a != b: raise ValueError('Terrain seed/phase differs.')
    compare(left, right)


def summarize(request, result, c, speed=None):
    common = common_config(c, speed)
    metrics = study.summarize(request, result, common)
    metrics['maxConstraintPositionErrorMm']=result['diagnostics'].get('maxConstraintPositionErrorMm')
    metrics['maxPenetrationMm']=result['diagnostics'].get('maxPenetrationMm')
    metrics['minimumTravelReserveDeg']=min(min(r['theta2']-request['params']['te'],request['params']['tc']-r['theta2']) for r in result['rows'])
    if request['caseConfig']['kind'] != 'terrain-stability': return metrics
    rows = result['rows']; start = common['evaluationStartS']; end = common['terrainDurationS']
    complete = bool(rows and rows[0]['t'] <= start+1e-10 and rows[-1]['t'] >= end-1e-9)
    selected = [r for r in rows if start-1e-10 <= r['t'] <= end+1e-10]
    old = metrics['terrainMetrics']; numerical = metrics['numericallyResolved']
    # Include the whole run's stop events, including a pre-window failure.
    physical = any(e['type'] in ('compression-stop', 'underside-contact', 'extension-stop') for e in result['events'])
    minimum = min((r['chassisClearanceMm'] for r in selected), default=None)
    physical = physical or (minimum is not None and minimum < c['shared']['minimumClearanceMm'])
    speed_mm_s = speed*1000
    contact = weighted_fraction(rows, start, end, lambda r:r['contactNormalForceN'] > 1e-6)
    metrics['terrainMetrics'] = dict(evaluationStartS=start, evaluationEndS=end,
        evaluationStartDistanceMm=c['evaluationStartDistanceMm'], evaluationEndDistanceMm=c['totalDistanceMm'],
        speedMps=speed, encounterPeriodS=c['terrain']['periodMm']/speed_mm_s,
        halfCycleResponseTimeS=c['terrain']['periodMm']/(2*speed_mm_s),
        sampleCount=len(selected), fullWindowObserved=complete, usableComparison=complete and numerical,
        heaveTestPassed=complete and numerical and not physical,
        status='numerical-failure' if not numerical else 'incomplete-window' if not complete else 'physical-limit' if physical else 'completed-window',
        heightMm=weighted_moments(rows,start,end,lambda r:r['chassisZMm']),
        desiredHeightMm=weighted_moments(rows,start,end,lambda r:r['rideTargetHeightMm']),
        trackingErrorMm=weighted_moments(rows,start,end,lambda r:r['chassisZMm']-r['rideTargetHeightMm']),
        hipSpeedDegS=weighted_moments(rows,start,end,lambda r:r['velocityDegS']),
        motorRpm=weighted_moments(rows,start,end,lambda r:r.get('shaftRpm',0)),
        motorTorqueNm=weighted_moments(rows,start,end,lambda r:r['motorTorqueNm']),
        contactFraction=contact, contactLossFraction=1-contact if contact is not None else None,
        saturationFraction=weighted_fraction(rows,start,end,lambda r:bool(r['actuatorLimited'])),
        booleanMetricMethod='Time-weighted left-held saved samples; transitions resolved only to output interval',
        minClearanceMm=minimum, minimumTravelReserveDeg=min((min(r['theta2']-request['params']['te'],request['params']['tc']-r['theta2']) for r in selected),default=None),
        scope='Same spatial strip, seed and lead; fast runs have less elapsed settling time. Finite-gain hardware-limited quarter heave, not roll/pitch or tipping stability. Unresolved/incomplete/stopped runs cannot establish successful stability.')
    return metrics


def fingerprints():
    names = (*study.SOURCE_FILES, 'workflow_example.py', 'actuator_comparison.py',
        'motor-gearbox-catalog.json', 'terrain_speed_study.py')
    return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, allow_nan=False, separators=(',', ':')), encoding='utf-8')


def app_local(path):
    resolved = path.resolve()
    if ROOT not in resolved.parents: raise ValueError('Output must stay inside this app.')
    return resolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-config', type=Path); parser.add_argument('--config', type=Path)
    parser.add_argument('--output', type=Path); parser.add_argument('--dt', type=float)
    parser.add_argument('--candidate', choices=tuple(MOTORS), action='append')
    parser.add_argument('--case', choices=KINDS, action='append')
    parser.add_argument('--speed', type=float, action='append')
    parser.add_argument('--engine', choices=tuple(study.ENGINES), action='append')
    args = parser.parse_args()
    if args.write_config:
        target=app_local(args.write_config)
        if target.exists(): raise ValueError('Refusing to overwrite an existing editable config.')
        write(target, default_config())
        if args.output is None: return
    if args.output is None: parser.error('--output is required to execute.')
    c = json.loads(args.config.read_text(encoding='utf-8')) if args.config else default_config()
    if args.dt is not None: c['shared']['dt']=args.dt
    c=validate_config(c)
    if args.speed and any(s not in c['speedsMps'] for s in args.speed): raise ValueError('Speed filter must select configured speeds.')
    catalog=json.loads((ROOT/'motor-gearbox-catalog.json').read_text(encoding='utf-8'))
    candidates=[selected_hardware(c,catalog,k) for k in c['candidateIds'] if not args.candidate or k in args.candidate]
    if not candidates: raise ValueError('Candidate filter selects no runs.')
    hashes=fingerprints();output=app_local(args.output)
    filters={key:getattr(args,key) for key in ('candidate','case','speed','engine')}
    settings=dict(schema='kinefold/terrain-speed-capture-v1', config=c,
        sourceSHA256=hashes, candidates=candidates, filters=filters)
    guard=output/'settings.json'
    if guard.exists() and json.loads(guard.read_text(encoding='utf-8')) != settings:
        raise ValueError('Source/config/filter identity differs; use a fresh folder.')
    write(guard,settings)
    summary_path=output/'summary.json'
    records=json.loads(summary_path.read_text(encoding='utf-8')).get('records',[]) if summary_path.exists() else []
    reference_spatial=None;started=time.monotonic()
    for candidate in candidates:
        kinds=KINDS if candidate['id']=='odrive-8325' else ('terrain-stability',)
        for kind in kinds:
            if args.case and kind not in args.case: continue
            speeds=[s for s in c['speedsMps'] if not args.speed or s in args.speed] if kind=='terrain-stability' else [None]
            for speed in speeds:
                for engine,sim in study.ENGINES.items():
                    if args.engine and engine not in args.engine: continue
                    request=make_payload(c,candidate,kind,engine,speed)
                    if kind=='terrain-stability':
                        model=validate_contact_request(request)
                        spatial=terrain_signature(terrain_spec(model,request['caseConfig'])['terrain'])
                        if reference_spatial is None: reference_spatial=spatial
                        else: assert_same_spatial_input(reference_spatial,spatial)
                    key=(candidate['id'],kind,speed,engine)
                    old=next((r for r in records if (r['candidateId'],r['case'],r['speedMps'],r['engine'])==key),None)
                    if old:
                        if old['payload'] != request: raise ValueError('Cached exact request changed.')
                        continue
                    tick=time.monotonic();result=sim(request,stop_at_assessment=kind!='terrain-stability')
                    if kind=='terrain-stability': assert_same_spatial_input(reference_spatial,terrain_signature(result['terrain']))
                    tag=f"{candidate['id']}-{kind}"+(f'-v{speed:g}' if speed is not None else '')+'-'+engine
                    capture_name=tag+'-capture.json' if candidate['id']==c['retainCandidateId'] else None
                    if capture_name: write(output/capture_name,dict(payload=request,result=result,sourceSHA256=hashes))
                    record=dict(candidateId=candidate['id'],case=kind,speedMps=speed,engine=engine,
                        payload=request,capture=capture_name,runWallSeconds=time.monotonic()-tick,
                        metrics=summarize(request,result,c,speed),warnings=result.get('warnings',[]))
                    records.append(record)
                    write(summary_path,dict(schema='kinefold/terrain-speed-result-v1',settings=settings,
                        records=records,python=platform.python_version(),elapsedWallSeconds=time.monotonic()-started,
                        sameSpatialInputVerified=True,storage='Exact requests/metrics for20runs maximum; rawframes for one selected motor only. Failed cases retained; no global ranking.'))
                    print(json.dumps({k:record[k] for k in ('candidateId','case','speedMps','engine','runWallSeconds')}|
                        dict(termination=record['metrics']['termination'],resolved=record['metrics']['numericallyResolved'],
                            terrainStatus=record['metrics'].get('terrainMetrics',{}).get('status'))),flush=True)
    fields=('candidateId','case','speedMps','engine','numericallyResolved','termination','terrainStatus',
        'trackingRmsMm','trackingVarianceMm2','contactLossFraction','saturationFraction',
        'minimumTravelReserveDeg','motorPeakRpm','hipPeakDegS','jumpCOMRiseMm','landingSuccessAboveClearance','minClearanceMm')
    with (output/'summary.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for r in records:
            m=r['metrics'];t=m.get('terrainMetrics',{});error=t.get('trackingErrorMm') or {}
            writer.writerow({k:r[k] if k in r else m.get(k) for k in fields}|dict(
                terrainStatus=t.get('status'),trackingRmsMm=error.get('rms'),trackingVarianceMm2=error.get('variance'),
                contactLossFraction=t.get('contactLossFraction'),saturationFraction=t.get('saturationFraction'),
                minimumTravelReserveDeg=t.get('minimumTravelReserveDeg'),
                motorPeakRpm=(t.get('motorRpm') or {}).get('maximumAbsolute'),
                hipPeakDegS=(t.get('hipSpeedDegS') or {}).get('maximumAbsolute')))
    print('SUMMARY '+str(summary_path),flush=True)


if __name__ == '__main__': main()
