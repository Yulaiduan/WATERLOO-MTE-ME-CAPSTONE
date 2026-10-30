"""Run a small three-combination example of the saved-design comparison workflow.

Run app Python: python workflow_example.py --write-config .preview/example.json
then python workflow_example.py --config .preview/example.json --output .preview/example
Inputs: explicit shared kg/mm/deg/s and shaft SI loss assumptions; three exact
catalogue IDs only. Outputs summary JSON/CSV with exact requests and fingerprints;
actual rows/frames are retained only for one named worked combination. At most
18 runs, no catalogue search, live profile changes or GUI. Leaders are conditional
on this quarter-heave model and these three examples, not verified hardware or
global optima. Constant cogging is lumped into Coulomb drag. Thermal, mounting,
real torque-speed maps and shock strength remain unassessed.
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
from actuator_comparison import candidate_hardware, validate_assumptions
from contact_cases import validate_contact_request

ROOT=Path(__file__).resolve().parent
COMBINATIONS={
    'light-10':('motor-flipsky-6384-170kv-battle-hardened','gear-ab90-g10-d19-r155'),
    'strong-10':('motor-flipsky-80100-130kv','gear-ab90-g10-d19-r155'),
    'strong-20':('motor-flipsky-80100-130kv','gear-aep90-g20-d19-r154')}
SHARED_KEYS=('chassisKg','upperLinkKg','lowerLinkKg','wheelKg','alphaDeg','dropMm',
    'jumpTargetMm','minimumClearanceMm','undersideOffsetMm','shaftCoulombNm',
    'shaftViscousNms','frictionSmoothingRadS','gearboxInputInertiaKgM2','noLoadRpm',
    'motoringPowerW','brakingPowerW','regenEnergyJ','peakDurationS','rideKpNPerM',
    'rideKdNsPerM','dt','outputHz','iterations','jumpDurationS','landingDurationS',
    'terrainDurationS','terrainSpeedMmS','terrainDelayS','evaluationStartS')
KINDS=('jump','landing','terrain-stability')


def default_config():
    original=study.default_config()
    return dict(schema='kinefold/workflow-example-v1',
        candidateIds=list(COMBINATIONS),exampleCandidateId='strong-10',
        **{k:(.5 if k=='frictionSmoothingRadS' else original[k]) for k in SHARED_KEYS},
        reverseEfficiency=.9,jumpTieMm=20.,terrainTieRmsMm=.1,landingTieClearanceMm=10.,
        terrain=copy.deepcopy(original['terrains'][2]))


def shared_config(c):
    base=study.default_config();base.update({k:c[k] for k in SHARED_KEYS})
    base['terrains']=[copy.deepcopy(c['terrain'])]
    return study.validate_config(base)


def validate_config(raw):
    template=default_config()
    if not isinstance(raw,dict) or set(raw)!=set(template):
        raise ValueError('Use exactly the fields in --write-config output.')
    c=copy.deepcopy(raw)
    if c['schema']!=template['schema']:raise ValueError('Unknown workflow example schema.')
    ids=c['candidateIds']
    if not isinstance(ids,list) or not 1<=len(ids)<=3 or any(not isinstance(x,str) for x in ids) or len(set(ids))!=len(ids) or set(ids)-set(COMBINATIONS):
        raise ValueError('Select one to three unique predefined example combinations.')
    if c['exampleCandidateId'] not in ids:raise ValueError('The single retained worked combination must be selected.')
    for key in ('reverseEfficiency','jumpTieMm','terrainTieRmsMm','landingTieClearanceMm'):
        value=c[key]
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
            raise ValueError(key+' must be finite/nonnegative.')
    if not .01<=c['reverseEfficiency']<=1:raise ValueError('Reverse efficiency requires .01..1.')
    shared_config(c)
    return c


def selected_hardware(c,catalog,candidate_id):
    motor_id,gear_id=COMBINATIONS[candidate_id]
    motor=next(x for x in catalog['motors'] if x['id']==motor_id)
    gear=next(x for x in catalog['gearboxes'] if x['id']==gear_id)
    assumptions=validate_assumptions(dict(unknownGearboxInputInertiaKgM2=c['gearboxInputInertiaKgM2'],
        noLoadRpm=c['noLoadRpm'],reverseEfficiency=c['reverseEfficiency'],
        motoringPowerW=c['motoringPowerW'],brakingPowerW=c['brakingPowerW'],
        regenPowerW=c['brakingPowerW'],regenEnergyJ=c['regenEnergyJ'],peakDurationS=c['peakDurationS'],
        minClearanceMm=c['minimumClearanceMm'],undersideOffsetMm=c['undersideOffsetMm'],
        rideKpNPerM=c['rideKpNPerM'],rideKdNsPerM=c['rideKdNsPerM']))
    hardware=candidate_hardware(motor,gear,assumptions)
    # This example uses common shaft losses rather than candidate_hardware's
    # separate percentage-of-rated-output drag scenario.
    hardware['outputCoulombNm']=gear['ratio']*c['shaftCoulombNm']
    hardware['outputViscousNms']=gear['ratio']**2*c['shaftViscousNms']
    hardware['assumptionFlags'].append('Common shaft Coulomb/cogging and viscous placeholders override percentage drag; listed forward efficiency plus explicit drag may overlap and is not a measured loss map')
    return dict(id=candidate_id,motorId=motor_id,gearboxId=gear_id,
        name=motor['name']+' / '+gear['name'],ratio=gear['ratio'],hardware=hardware,
        source=dict(catalogRevision=catalog['revision'],motorUrl=motor['sourceUrl'],
            gearboxUrl=gear.get('detailSourceUrl') or gear['sourceUrl'],
            shaftPeakNm=motor['peakTorqueNm'],rotorJStatus=motor['rotorInertiaStatus'],
            gearboxInputJStatus=gear['inertiaStatus'],gearboxPeakNm=gear['peakOutputNm'],
            gearboxContinuousNm=gear['continuousOutputNm'],forwardEfficiency=gear['efficiency']))


def make_payload(c,candidate,kind,engine):
    common=shared_config(c);hw=candidate['hardware'];actuator=hw['actuatorConfig'];ratio=candidate['ratio']
    request=study.make_payload(common,kind,ratio,'losses',engine,c['terrain'] if kind=='terrain-stability' else None)
    request['motorConfig'].update(rotorInertiaKgM2=hw['rotorInertiaKgM2'],
        gearboxInputInertiaKgM2=hw['gearboxInputInertiaKgM2'])
    request['actuatorConfig']=copy.deepcopy(actuator)
    request['caseConfig'].update(jumpTorqueNm=actuator['gearboxPeakNm'],
        landingBrakeTorqueNm=actuator['gearboxPeakNm'],landingBrakeLimitNm=actuator['gearboxPeakNm'])
    # Gear train inertia is already in the motor block; no duplicate output J.
    request['runConfig']['hipRotorInertiaKgM2']=hw['gearboxOutputInertiaKgM2']
    validate_contact_request(request)
    return request


def summarize(request,result,c):
    metrics=study.summarize(request,result,shared_config(c));rows=result['rows']
    metrics['maxConstraintPositionErrorMm']=result['diagnostics'].get('maxConstraintPositionErrorMm')
    metrics['maxPenetrationMm']=result['diagnostics'].get('maxPenetrationMm')
    metrics['brakingWorkRemovedJ']=-rows[-1]['motorWorkJ'] if request['caseConfig']['kind']=='landing' else None
    metrics['minimumTravelReserveDeg']=min(min(r['theta2']-request['params']['te'],request['params']['tc']-r['theta2']) for r in rows)
    if 'terrainMetrics' in metrics:
        selected=[r for r in rows if c['evaluationStartS']-1e-9<=r['t']<=c['terrainDurationS']+1e-9]
        metrics['terrainMetrics']['minimumTravelReserveDeg']=min((min(r['theta2']-request['params']['te'],request['params']['tc']-r['theta2']) for r in selected),default=None)
    return metrics


def conditional_leaders(records,c):
    """Use the worse engine; preserve ties and exclude incomplete/failed cases."""
    output={};all_target=[]
    for kind,metric,tolerance,maximize in (
        ('jump','jumpCOMRiseMm',c['jumpTieMm'],True),
        ('landing','minClearanceMm',c['landingTieClearanceMm'],True),
        ('terrain-stability','trackingRmsMm',c['terrainTieRmsMm'],False)):
        eligible=[];excluded=[];target_ids=[]
        for candidate_id in c['candidateIds']:
            pair=[r for r in records if r['candidateId']==candidate_id and r['case']==kind]
            if len(pair)!=2 or {r['engine'] for r in pair}!=set(study.ENGINES):
                excluded.append(dict(candidateId=candidate_id,reason='Matched engine pair not completed'));continue
            mm=[r['metrics'] for r in pair]
            if not all(m['numericallyResolved'] for m in mm):
                excluded.append(dict(candidateId=candidate_id,reason='Numerically unresolved engine result'));continue
            if kind=='jump':
                valid=all(m.get('jumpObserved') and m.get(metric) is not None for m in mm)
                values=[m.get(metric) for m in mm];target=valid and all(m['jumpTargetReached'] for m in mm)
            elif kind=='landing':
                valid=all(m.get('landingSuccessAboveClearance') for m in mm)
                values=[m.get(metric) for m in mm];target=valid
            else:
                valid=all(m.get('terrainMetrics',{}).get('heaveTestPassed') for m in mm)
                values=[m.get('terrainMetrics',{}).get('trackingErrorMm',{}).get('rms') for m in mm];target=valid
            if not valid or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in values):
                excluded.append(dict(candidateId=candidate_id,reason='Required physical observation/pass missing'));continue
            score=min(values) if maximize else max(values)
            eligible.append(dict(candidateId=candidate_id,score=score,targetMet=target))
            if target:target_ids.append(candidate_id)
        ordered=sorted(eligible,key=lambda r:r['score'],reverse=maximize)
        leaders=[r['candidateId'] for r in ordered if abs(r['score']-ordered[0]['score'])<=tolerance] if ordered else []
        output[kind]=dict(status='no-eligible-combination' if not ordered else 'tie-within-resolution-band' if len(leaders)>1 else 'conditional-performance-leader',
            leaderIds=leaders,eligible=ordered,excluded=excluded,targetMetIds=target_ids,
            metric=metric,engineAggregation='Lower engine value' if maximize else 'Higher engine value',
            tieTolerance=tolerance,scope='Only the three predefined examples under captured assumptions; no global optimum or hardware pass')
    for candidate_id in c['candidateIds']:
        if all(candidate_id in output[k]['targetMetIds'] for k in KINDS):all_target.append(candidate_id)
    output['allTargets']=dict(passingIds=all_target,status='conditional-pass' if all_target else 'none-demonstrated',
        scope='Jump target, first-arrest landing clearance and short heave window only; thermal/mechanical compatibility unassessed')
    return output


def fingerprints():
    names=(*study.SOURCE_FILES,'workflow_example.py','actuator_comparison.py','motor-gearbox-catalog.json')
    return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,allow_nan=False,separators=(',',':')),encoding='utf-8')


def app_local(path):
    result=path.resolve()
    if ROOT not in result.parents:raise ValueError('Example output must stay inside the app folder.')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-config',type=Path);parser.add_argument('--config',type=Path)
    parser.add_argument('--output',type=Path);parser.add_argument('--candidate',choices=tuple(COMBINATIONS),action='append')
    parser.add_argument('--case',choices=KINDS,action='append')
    args=parser.parse_args()
    if args.write_config:
        write(app_local(args.write_config),default_config())
        if args.output is None:return
    if args.output is None:parser.error('--output is required to execute.')
    c=validate_config(json.loads(args.config.read_text(encoding='utf-8')) if args.config else default_config())
    catalog=json.loads((ROOT/'motor-gearbox-catalog.json').read_text(encoding='utf-8'))
    candidates=[selected_hardware(c,catalog,k) for k in c['candidateIds'] if not args.candidate or k in args.candidate]
    kinds=[k for k in KINDS if not args.case or k in args.case]
    if not candidates:raise ValueError('Filters select no example combinations.')
    output=app_local(args.output);hashes=fingerprints()
    settings=dict(schema='kinefold/workflow-example-capture-v1',config=c,sourceSHA256=hashes,
        candidates=candidates,filters=dict(candidate=args.candidate,case=args.case),
        workflow=['Capture one mechanism and input','Select three actuator presets','Run jump, landing and one terrain in both engines','Compare task-specific outcomes','Replay and retain one worked combination'])
    guard=output/'settings.json'
    if guard.exists() and json.loads(guard.read_text(encoding='utf-8'))!=settings:
        raise ValueError('Source/config/filter identity changed; use a new app-local folder.')
    write(guard,settings)
    report_path=output/'summary.json';prior=json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
    records=prior.get('records',[]);examples_path=output/'example-captures.json'
    examples=json.loads(examples_path.read_text(encoding='utf-8')) if examples_path.exists() else dict(candidateId=c['exampleCandidateId'],captures=[])
    start=time.monotonic()
    for candidate in candidates:
        for kind in kinds:
            for engine,sim in study.ENGINES.items():
                request=make_payload(c,candidate,kind,engine)
                key=(candidate['id'],kind,engine)
                old=next((r for r in records if (r['candidateId'],r['case'],r['engine'])==key),None)
                if old:
                    if old['payload']!=request:raise ValueError('Cached exact request changed.')
                    continue
                tick=time.monotonic();result=sim(request,stop_at_assessment=kind!='terrain-stability')
                record=dict(candidateId=candidate['id'],case=kind,engine=engine,payload=request,
                    runWallSeconds=time.monotonic()-tick,metrics=summarize(request,result,c),warnings=result.get('warnings',[]))
                records.append(record)
                if candidate['id']==c['exampleCandidateId']:
                    # A crash between raw and summary writes must not duplicate
                    # a case on resume or grow the retained example indefinitely.
                    examples['captures']=[x for x in examples['captures'] if (x['case'],x['engine'])!=(kind,engine)]
                    examples['captures'].append(dict(case=kind,engine=engine,payload=request,result=result))
                    write(examples_path,examples)
                report=dict(schema='kinefold/workflow-example-result-v1',settings=settings,records=records,
                    leaders=conditional_leaders(records,c),python=platform.python_version(),
                    elapsedWallSeconds=time.monotonic()-start,
                    storage='Summary/exact requests for every case; rows/frames only for the named worked combination. No broad catalogue data export.')
                write(report_path,report)
                print(json.dumps(dict(candidate=candidate['id'],case=kind,engine=engine,seconds=record['runWallSeconds'],
                    outcome=record['metrics']['outcome'],resolved=record['metrics']['numericallyResolved'])),flush=True)
    fields=('candidateId','case','engine','numericallyResolved','jumpCOMRiseMm','jumpTargetReached',
        'landingSuccessAboveClearance','minClearanceMm','brakingWorkRemovedJ','trackingRmsMm','trackingVarianceMm2',
        'saturationFraction','minimumTravelReserveDeg','peakDeliveredTorqueNm','energyResidualJ')
    with (output/'summary.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for r in records:
            m=r['metrics'];terrain=m.get('terrainMetrics',{});error=terrain.get('trackingErrorMm') or {}
            writer.writerow({k:r[k] if k in r else m.get(k) for k in fields}|dict(trackingRmsMm=error.get('rms'),
                trackingVarianceMm2=error.get('variance'),saturationFraction=terrain.get('saturationFraction'),
                minimumTravelReserveDeg=terrain.get('minimumTravelReserveDeg',m['minimumTravelReserveDeg'])))
    print('SUMMARY '+str(report_path),flush=True)


if __name__=='__main__':main()
