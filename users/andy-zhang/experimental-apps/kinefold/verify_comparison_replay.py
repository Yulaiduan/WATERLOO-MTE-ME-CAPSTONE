"""Verify exact paired replay persistence, validation, lifecycle and actual engines.

Run app Python verify_comparison_replay.py [--real]. Inputs are temporary saved
comparison fixtures in builder mm/deg/kg and SI controls; --real uses this app's
installed SciPy/Pymunk through an owned worker. Reports unittest checks only.
Does not open a GUI/server or change real profiles/jobs. Numerical replay tests
do not certify hardware, canonical robot physics or live browser presentation.
"""
import argparse
import hashlib
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

import actuator_comparison as ac
from comparison_service import ComparisonService
from comparison_replay_service import (ComparisonReplayService,MAX_JSON,atomic_json,
    make_bundle,read_json,settings,validate_record)
from comparison_replay_worker import run_replay

APP=Path(__file__).resolve().parent
JOB='a'*32
REAL=False


def base_fixture(duration=.1):
    project=json.loads((APP/'saved-configurations/vsl-v45-nominal-alpha0.json').read_text(encoding='utf-8'))
    assumptions={**ac.ASSUMPTIONS,'dynamicDurationS':duration,'dynamicDt':.00025,'dynamicOutputHz':50.,'dropHeightMm':20.}
    catalog=ac.load_catalog();motor=catalog['motors'][0];gear=catalog['gearboxes'][0]
    hardware=ac.candidate_hardware(motor,gear,assumptions)
    candidate=dict(id=motor['id']+'__'+gear['id'],motorId=motor['id'],gearboxId=gear['id'],
        motorName=motor['name'],gearboxName=gear['name'],ratio=gear['ratio'],hardware=hardware,
        analytical={k:dict(status='not-run') for k in ('landing','jump','terrain')},
        pymunk={k:dict(status='not-run') for k in ('landing','jump','terrain')})
    parent=dict(schema='kinefold/automatic-actuator-comparison-v1',project=project,assumptions=assumptions,
        budget=dict(maxSeconds=60),candidates=[candidate],identity=dict(projectHash=ac.digest(project),
            assumptionsHash=ac.digest(assumptions),catalogHash=ac.digest(catalog),catalogRevision=catalog['revision'],
            sourceSHA256={name:hashlib.sha256((APP/name).read_bytes()).hexdigest() for name in ('actuator_comparison.py','contact_cases.py','motor_model.py')}))
    return parent,candidate,catalog


def synthetic_record(parent,candidate,kind,engine):
    payload=ac.contact_payload(parent['project'],candidate['hardware'],parent['assumptions'],kind,engine)
    rows=[];frames=[]
    for t,z in ((0.,700.),(.05,690.),(.1,680.)):
        rows.append(dict(t=t,theta2=135.,chassisZMm=z,wheelZMm=200.,chassisVelocityMmS=-200.,
            chassisAccelerationMmS2=0.,chassisClearanceMm=z-50,contactCount=1,motorTorqueNm=0.,shaftCommandNm=0.,energyBalanceResidualJ=0.))
        frames.append(dict(t=t,theta2=135.,theta4=0.,theta5=0.,theta6=0.,wheelAngle=t*100,
            A=[0,0,z],B=[-200,0,z-200],C=[0,0,200],terrainOffsetMm=[-t*100,0,0],indexAnglesDeg=dict(a=0,b=0,c=0,d=0,e=0,f=0)))
    result=dict(schema='kinefold/contact-v2',engine=engine,rows=rows,frames=frames,events=[],
        diagnostics=dict(termination='duration',finiteLinkDynamics=True),caseMetrics=dict(minimumUndersideClearanceMm=630),
        designHash=ac.digest(settings(payload)),snapshot={('solverConfig' if k=='runConfig' else k):copy.deepcopy(v) for k,v in payload.items() if k!='engine'},
        **settings(payload))
    return dict(candidateId=candidate['id'],kind=kind,engine=engine,payload=payload,result=result,assessment=dict(status='unknown'))


def install_parent(root,parent,candidate,catalog,engines=(),kind='landing'):
    directory=root/'.preview'/'actuator-comparisons'/JOB
    atomic_json(directory/'result.json',parent);atomic_json(directory/'status.json',dict(id=JOB,state='complete'))
    atomic_json(directory.parent/'latest-job.json',dict(jobId=JOB))
    (root/'motor-gearbox-catalog.json').write_text(json.dumps(catalog),encoding='utf-8')
    atomic_json(root/'profiles'/'library.json',dict(sentinel='active design must remain untouched'))
    for engine in engines:
        atomic_json(directory/(ac.digest(candidate['id'])[:20]+'-'+engine+'-'+kind+'.json'),synthetic_record(parent,candidate,kind,engine))
    return directory


class Validation(unittest.TestCase):
    def setUp(self):
        self.parent,self.candidate,_=base_fixture()
        self.runs={e:synthetic_record(self.parent,self.candidate,'landing',e) for e in ('analytical','pymunk')}
    def test_complete_bundle_preserves_payloads_and_all_frames(self):
        before=ac.canonical(self.runs)
        bundle=make_bundle(JOB,self.candidate,'landing',self.parent['project'],self.runs)
        self.assertEqual(before,ac.canonical(bundle['runs']));self.assertEqual(before,ac.canonical(self.runs))
        self.assertEqual(bundle['settingsHash'],ac.digest(settings(self.runs['analytical']['payload'])))
    def test_rejects_config_engine_candidate_and_case_mix(self):
        edits=[lambda r:r['pymunk']['payload']['runConfig'].update(dt=.001),
            lambda r:r['pymunk']['result']['params'].update(alpha=20),
            lambda r:r['pymunk'].update(engine='analytical'),lambda r:r['pymunk'].update(kind='jump'),
            lambda r:r['pymunk'].update(candidateId='other'),lambda r:r['pymunk']['payload']['actuatorConfig'].update(ratio=7)]
        for edit in edits:
            runs=copy.deepcopy(self.runs);edit(runs)
            with self.assertRaises(ValueError):make_bundle(JOB,self.candidate,'landing',self.parent['project'],runs)
    def test_rejects_malformed_frame_clock_geometry_and_nonfinite(self):
        edits=[lambda r:r['frames'].pop(),lambda r:r['frames'][1].update(t=.051),
            lambda r:r['rows'][2].update(t=-1),lambda r:r['frames'][1].update(A=[0,0,float('nan')]),
            lambda r:r['frames'][1].update(theta2=137),lambda r:r['rows'][0].update(t=.01),
            lambda r:r['frames'][1].update(C=None),lambda r:r['rows'][1].update(theta2=True)]
        for edit in edits:
            record=copy.deepcopy(self.runs['analytical']);edit(record['result'])
            with self.assertRaises(ValueError):validate_record(record,self.candidate['id'],'landing','analytical',self.parent['project'],self.candidate)
    def test_no_silent_pair_of_unequal_settings(self):
        runs=copy.deepcopy(self.runs);p=runs['pymunk']['payload'];p['runConfig']['dt']=.001
        runs['pymunk']['result']['runConfig']=copy.deepcopy(p['runConfig']);runs['pymunk']['result']['snapshot']['solverConfig']=copy.deepcopy(p['runConfig'])
        with self.assertRaises(ValueError):make_bundle(JOB,self.candidate,'landing',self.parent['project'],runs)


class Service(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.parent,self.candidate,self.catalog=base_fixture()
        self.directory=install_parent(self.root,self.parent,self.candidate,self.catalog,engines=('analytical','pymunk'))
        self.lock=threading.Lock();self.service=ComparisonService(self.root,sys.executable,self.lock)
        self.request=dict(jobId=JOB,candidateId=self.candidate['id'],kind='landing')
        self.library=(self.root/'profiles/library.json').read_bytes();self.pointer=(self.directory.parent/'latest-job.json').read_bytes()
    def tearDown(self):
        self.service.close();self.assertEqual((self.root/'profiles/library.json').read_bytes(),self.library)
        self.assertEqual((self.directory.parent/'latest-job.json').read_bytes(),self.pointer);self.temp.cleanup()
    def call(self,action,**kwargs):return self.service.handle({'action':action,**self.request,**kwargs})
    def test_cached_exact_pair_is_read_only_and_needs_no_runtime(self):
        self.service.replays.python=Path('missing-runtime')
        response=self.call('replay');self.assertTrue(response['ready']);self.assertEqual(response['bundle']['kind'],'landing')
        self.assertEqual(self.call('run-replay')['bundle'],response['bundle'])
        self.assertFalse(self.lock.locked());self.assertFalse(self.service.busy)
    def test_missing_case_and_partial_engine_are_explicit(self):
        self.assertEqual(self.call('replay',kind='jump')['missing'],['analytical','pymunk'])
        (self.directory/(ac.digest(self.candidate['id'])[:20]+'-pymunk-landing.json')).unlink()
        response=self.call('replay');self.assertFalse(response['ready']);self.assertEqual(response['missing'],['pymunk'])
    def test_bad_ids_fields_hashes_and_source_record_rejected(self):
        for kwargs in (dict(jobId='../escape'),dict(kind='other'),dict(candidateId='other'),dict(path='outside')):
            with self.assertRaises(ValueError):self.call('replay',**kwargs)
        raw=read_json(self.directory/'result.json');raw['project']['params']['m2']=9;atomic_json(self.directory/'result.json',raw)
        with self.assertRaises(ValueError):self.call('replay')
    def test_cached_replay_survives_catalog_update_but_new_unknown_case_does_not(self):
        (self.root/'motor-gearbox-catalog.json').write_text('{}')
        self.assertTrue(self.call('replay')['ready'])
        with self.assertRaises(ValueError):self.call('run-replay',kind='jump')
    def test_unrun_case_cannot_silently_use_changed_default_sources(self):
        raw=read_json(self.directory/'result.json')
        raw['identity']['sourceSHA256']['contact_cases.py']='0'*64
        atomic_json(self.directory/'result.json',raw)
        self.assertTrue(self.call('replay')['ready'])
        self.service.replays.worker_script=APP/'comparison_replay_worker.py'
        with self.assertRaisesRegex(ValueError,'contact_cases.py'):
            self.call('run-replay',kind='jump')
    def fake_worker(self,delay=.15,fail=False):
        bundle=self.call('replay')['bundle'];atomic_json(self.root/'fixture-bundle.json',bundle)
        script=self.root/'comparison_replay_worker.py'
        script.write_text("import argparse,json,pathlib,time\np=argparse.ArgumentParser();p.add_argument('--request');p.add_argument('--output');a=p.parse_args();d=pathlib.Path(a.output)\ntime.sleep("+repr(delay)+")\n"+("(d/'error.json').write_text(json.dumps({'error':'test worker failure'}));raise SystemExit(2)\n" if fail else "(d/'bundle.json').write_bytes(pathlib.Path('fixture-bundle.json').read_bytes())\n"),encoding='utf-8')
    def wait(self,rid,deadline=4):
        end=time.monotonic()+deadline
        while time.monotonic()<end:
            state=self.service.handle(dict(action='replay-status',replayId=rid))['replayJob']
            if state['state']!='running':return state
            time.sleep(.02)
        self.fail('Replay worker did not finish within test deadline')
    def test_job_lifecycle_freezes_settings_and_reuses_persisted_replay(self):
        self.fake_worker();response=self.call('run-replay',force=True);rid=response['replayJob']['id']
        self.assertTrue(self.lock.locked());self.assertTrue(self.service.busy)
        resumed=self.call('replay');self.assertFalse(resumed['ready']);self.assertEqual(resumed['replayJob']['id'],rid)
        with self.assertRaises(ValueError):self.service.handle(dict(action='start'))
        with self.assertRaises(ValueError):self.call('run-replay',force=True)
        state=self.wait(rid);self.assertEqual(state['state'],'complete')
        result=self.service.handle(dict(action='replay-result',replayId=rid));self.assertTrue(result['ready'])
        capture=read_json(self.root/'.preview/actuator-replays'/rid/'request.json')
        self.assertEqual(capture['originalPayloadHash'],result['bundle']['settingsHash'])
        self.assertEqual(capture['project'],self.parent['project'])
        self.service.close();self.service=ComparisonService(self.root,sys.executable,self.lock)
        self.assertEqual(self.call('replay')['replayJob']['id'],rid);self.assertFalse(self.lock.locked())
    def test_cancel_shutdown_and_held_external_lock(self):
        self.fake_worker(delay=3)
        self.lock.acquire()
        try:
            with self.assertRaises(ValueError):self.call('run-replay',force=True)
        finally:self.lock.release()
        rid=self.call('run-replay',force=True)['replayJob']['id']
        self.service.handle(dict(action='replay-cancel',replayId=rid));self.service.close()
        self.assertFalse(self.lock.locked());self.assertFalse(self.service.busy)
        self.assertEqual(self.service.handle(dict(action='replay-status',replayId=rid))['replayJob']['state'],'cancelled')
        self.assertFalse(self.service.handle(dict(action='replay-result',replayId=rid))['ready'])
    def test_failure_and_deadline_are_not_completed_pairs(self):
        self.fake_worker(fail=True);rid=self.call('run-replay',force=True)['replayJob']['id']
        self.assertEqual(self.wait(rid)['state'],'failed')
        self.assertFalse(self.service.handle(dict(action='replay-result',replayId=rid))['ready'])
        self.fake_worker(delay=3);monitor=self.service.replays._monitor
        self.service.replays._monitor=lambda i,p,s:monitor(i,p,-4.8)
        rid=self.call('run-replay',force=True)['replayJob']['id'];self.assertEqual(self.wait(rid)['state'],'timed-out')
        self.assertFalse(self.lock.locked())
    def test_restart_does_not_trust_orphan_pid(self):
        path=self.root/'.preview/actuator-replays'/('b'*32)/'status.json'
        atomic_json(path,dict(id='b'*32,state='running',pid=1))
        another=ComparisonReplayService(self.root,sys.executable)
        try:self.assertEqual(another.handle(dict(action='replay-status',replayId='b'*32))['replayJob']['state'],'failed')
        finally:another.close()
    def test_oversized_and_nonfinite_json_rejected_without_live_writes(self):
        path=self.root/'oversized.json'
        with path.open('wb') as f:f.truncate(MAX_JSON+1)
        with self.assertRaises(ValueError):read_json(path)
        path.write_text('{"bad":NaN}')
        with self.assertRaises(ValueError):read_json(path)
        with self.assertRaises(ValueError):atomic_json(path,dict(bad=float('inf')))
    def test_server_startup_imports_no_physics_packages(self):
        code="import sys;import comparison_service;assert not any(x in sys.modules for x in ('scipy','numpy','pymunk'))"
        subprocess.run([sys.executable,'-c',code],cwd=APP,check=True,capture_output=True)


class RealEngines(unittest.TestCase):
    def test_all_three_actual_cases_through_owned_worker(self):
        if not REAL:self.skipTest('use --real with installed app Python for actual engine cases')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);parent,candidate,catalog=base_fixture(duration=.12)
            install_parent(root,parent,candidate,catalog)
            service=ComparisonService(root,sys.executable,threading.Lock())
            service.replays.worker_script=APP/'comparison_replay_worker.py'
            try:
                for kind in ('landing','jump','terrain'):
                    response=service.handle(dict(action='run-replay',jobId=JOB,candidateId=candidate['id'],kind=kind));rid=response['replayJob']['id']
                    end=time.monotonic()+30
                    while time.monotonic()<end:
                        state=service.handle(dict(action='replay-status',replayId=rid))['replayJob']
                        if state['state']!='running':break
                        time.sleep(.03)
                    self.assertEqual(state['state'],'complete',state)
                    bundle=service.handle(dict(action='replay-result',replayId=rid))['bundle']
                    self.assertEqual(bundle['kind'],kind)
                    self.assertEqual(settings(bundle['runs']['analytical']['payload']),settings(bundle['runs']['pymunk']['payload']))
                    for engine in ('analytical','pymunk'):
                        run=bundle['runs'][engine]['result'];self.assertGreater(len(run['frames']),2)
                        self.assertTrue(run['diagnostics']['finiteLinkDynamics'])
                        self.assertNotEqual(run['frames'][0]['A'],run['frames'][-1]['A'])
                        self.assertIn('linkKineticJ',run['rows'][-1]);self.assertIn('actuatorConfig',run)
                    self.assertTrue(service.handle(dict(action='replay',jobId=JOB,candidateId=candidate['id'],kind=kind))['ready'])
            finally:service.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--real',action='store_true');args,rest=parser.parse_known_args();REAL=args.real
    unittest.main(argv=[sys.argv[0],*rest],verbosity=2)
