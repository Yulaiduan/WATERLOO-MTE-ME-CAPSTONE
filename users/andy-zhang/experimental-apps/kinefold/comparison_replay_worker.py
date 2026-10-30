"""Compute one captured motor/gearbox case with both independent contact engines.

Run app Python comparison_replay_worker.py --request FILE --output DIRECTORY;
the local replay service supplies owned paths, immutable builder mm/deg/kg,
SI controller/motor settings and a bounded deadline. Writes progress, each exact
engine payload/result, and a validated paired replay bundle. No GUI, live profile
write, catalog re-optimization or hardware acceptance is performed.
"""
import argparse
import copy
import hashlib
import platform
from importlib.metadata import version,PackageNotFoundError
from pathlib import Path
import time

import actuator_comparison as ac
from comparison_replay_service import (ENGINES,KINDS,atomic_json,make_bundle,
    read_json,settings,valid_id,validate_record,assert_generator_sources)

ROOT=Path(__file__).resolve().parent


def model_identity():
    files=('comparison_replay_worker.py','actuator_comparison.py','actuation_limits.py',
        'dynamic_model.py','motor_model.py','contact_cases.py','analytical_contact.py',
        'contact_dynamics.py','finite_contact_model.py','finite_pymunk_contact.py','terrain_profiles.py')
    values={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files if (ROOT/name).is_file()}
    packages={}
    for name in ('numpy','scipy','pymunk'):
        try:packages[name]=version(name)
        except PackageNotFoundError:packages[name]=None
    return dict(pythonVersion=platform.python_version(),packageVersions=packages,sourceSHA256=values)


def run_replay(capture,output,simulators=None):
    required={'schema','originalJobId','candidate','kind','project','assumptions','originalIdentity',
        'originalReview','basePayload','originalPayloadHash','maxSeconds'}
    if not isinstance(capture,dict) or set(capture)!=required or capture['schema']!='kinefold/comparison-replay-request-v1':
        raise ValueError('Replay worker requires its complete immutable captured request.')
    job_id=valid_id(capture['originalJobId'],'comparison');kind=capture['kind']
    if kind not in KINDS:raise ValueError('Unknown selected replay case.')
    candidate=capture['candidate'];project=capture['project']
    if not isinstance(candidate,dict) or not isinstance(candidate.get('hardware'),dict):raise ValueError('Captured replay hardware is unresolved.')
    if not isinstance(project,dict) or project.get('schema')!='kinefold/project-v3':raise ValueError('Captured replay project is invalid.')
    seconds=capture['maxSeconds']
    if isinstance(seconds,bool) or not isinstance(seconds,(int,float)) or not 1<=seconds<=300:raise ValueError('Replay deadline must be bounded.')
    original=capture['originalIdentity']
    if original.get('projectHash') and ac.digest(project)!=original['projectHash']:raise ValueError('Captured replay project hash differs.')
    if original.get('assumptionsHash') and ac.digest(capture['assumptions'])!=original['assumptionsHash']:raise ValueError('Captured replay assumptions hash differs.')
    base=capture['basePayload']
    if base is not None:
        cfg=settings(base)
        if ac.digest(cfg)!=capture['originalPayloadHash']:raise ValueError('Saved selected-case payload hash differs.')
        if ac.canonical(cfg['params'])!=ac.canonical(project['params']):raise ValueError('Saved selected-case geometry differs from capture.')
        if cfg['caseConfig'].get('kind')!=('terrain-stability' if kind=='terrain' else kind):raise ValueError('Saved selected-case kind differs.')
        if ac.canonical(cfg['actuatorConfig'])!=ac.canonical(candidate['hardware'].get('actuatorConfig')):raise ValueError('Saved selected actuator differs from candidate.')
    else:
        assert_generator_sources(ROOT,original,capture.get('originalReview'))
        catalog=ac.load_catalog()
        if ac.digest(catalog)!=original.get('catalogHash'):raise ValueError('Catalog changed after the original comparison capture.')
        base=ac.contact_payload(project,candidate['hardware'],capture['assumptions'],kind,'analytical')
        settings(base)
    payloads={engine:{**copy.deepcopy(base),'engine':engine} for engine in ENGINES}
    if ac.canonical(settings(payloads['analytical']))!=ac.canonical(settings(payloads['pymunk'])):
        raise ValueError('Replay worker generated unequal engine settings.')
    output=Path(output);output.mkdir(parents=True,exist_ok=True);start=time.monotonic()
    current=model_identity();identity=dict(originalIdentity=copy.deepcopy(original),originalReview=copy.deepcopy(capture['originalReview']),
        replayModel=current,settingsHash=ac.digest(settings(base)),settingsSource='exact-saved-case-payload' if capture['basePayload'] is not None else 'original-frozen-project-assumptions-hardware')
    old=dict(original.get('sourceSHA256',{}));review=capture.get('originalReview') or {}
    if review.get('nativeEngineSHA256'):old['contact_dynamics.py']=review['nativeEngineSHA256']
    changed=[name for name,h in current['sourceSHA256'].items() if name in old and h!=old[name]]
    warnings=['Exact saved numerical settings were used for both engines; the active Studio design was not read.']
    if changed:warnings.append('Recomputed with current sources; changed since original capture: '+', '.join(changed)+'. Original and current hashes are retained.')
    if simulators is None:
        from analytical_contact import simulate_contact as analytical
        from contact_dynamics import simulate_contact as pymunk
        simulators=dict(analytical=analytical,pymunk=pymunk)
    runs={}
    for index,engine in enumerate(ENGINES):
        if time.monotonic()-start>=seconds:raise TimeoutError('Selected-case replay exceeded its bounded deadline.')
        atomic_json(output/'progress.json',dict(stage=engine,progress=index/2,message='Running '+engine+' with the exact captured '+kind+' settings.',elapsedSeconds=time.monotonic()-start))
        payload=payloads[engine];result=simulators[engine](payload)
        record=dict(candidateId=candidate['id'],engine=engine,kind=kind,payload=payload,result=result,
            assessment=ac.dynamic_metrics(result,capture['assumptions'],kind),provenance=current)
        validate_record(record,candidate['id'],kind,engine,project,candidate)
        atomic_json(output/(engine+'.json'),record);runs[engine]=record
    bundle=make_bundle(job_id,candidate,kind,project,runs,identity,warnings,source='computed-replay')
    atomic_json(output/'bundle.json',bundle)
    atomic_json(output/'progress.json',dict(stage='complete',progress=1.,message='Both exact captured case trajectories are ready for synced replay.',elapsedSeconds=time.monotonic()-start))
    return bundle


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--request',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:run_replay(read_json(args.request),args.output)
    except Exception as error:
        args.output.mkdir(parents=True,exist_ok=True);atomic_json(args.output/'error.json',dict(error=str(error)[:2000]));raise


if __name__=='__main__':main()
