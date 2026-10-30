"""Serve exact saved analytical/Pymunk comparison cases and bounded missing pairs.

Imported by ComparisonService; inputs are safe local comparison/replay IDs and
landing/jump/terrain selections, builder mm/deg/kg and captured SI controls.
Outputs validated immutable replay bundles and owned subprocess job status under
the app's ignored .preview directory. No physics imports at server startup,
arbitrary paths, active-design writes, GUI or hardware-validity claims.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import threading
import time
import uuid

from actuator_comparison import canonical,digest

MAX_JSON=16*1024*1024
KINDS=('landing','jump','terrain')
ENGINES=('analytical','pymunk')
TERMINAL={'complete','failed','cancelled','timed-out'}
CONFIG_KEYS=('params','runConfig','contactConfig','caseConfig','motorConfig','actuatorConfig','terrainConfig')


def reject_nonfinite(value):
    raise ValueError('Nonfinite replay JSON number: '+value)


def read_json(path):
    if path.stat().st_size>MAX_JSON:raise ValueError('Replay JSON exceeds 16 MiB; reduce output in a new capture.')
    return json.loads(path.read_text(encoding='utf-8'),parse_constant=reject_nonfinite)


def atomic_json(path,value):
    data=canonical(value)
    if len(data.encode('utf-8'))>MAX_JSON:raise ValueError('Replay JSON exceeds 16 MiB; original capture is untouched.')
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:temporary.write_text(data,encoding='utf-8');temporary.replace(path)
    finally:temporary.unlink(missing_ok=True)


def valid_id(value,label='replay'):
    if not isinstance(value,str) or len(value)!=32 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('Invalid '+label+' job ID.')
    return value


def settings(payload):
    if not isinstance(payload,dict) or set(payload)-{'engine',*CONFIG_KEYS} or not {'engine','params','runConfig','contactConfig','caseConfig','motorConfig','actuatorConfig'}<=set(payload):
        raise ValueError('Saved replay requires a complete captured contact payload.')
    if payload.get('engine') not in ENGINES:raise ValueError('Invalid saved replay engine.')
    canonical(payload)
    return {key:copy.deepcopy(value) for key,value in payload.items() if key!='engine'}


def assert_generator_sources(source_root,identity,review=None):
    """Unrun cases may use defaults only from the original captured generator."""
    hashes=dict(identity.get('sourceSHA256',{}));review=review or {}
    if review.get('assessmentSourceSHA256'):hashes['actuator_comparison.py']=review['assessmentSourceSHA256']
    for name in ('actuator_comparison.py','contact_cases.py','motor_model.py'):
        path=Path(source_root)/name
        if not hashes.get(name) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=hashes[name]:
            raise ValueError('Cannot regenerate an unrun case: '+name+' differs from or lacks the original captured source hash. Existing frames remain replayable; create a new study for current defaults.')


def finite_number(value):
    return not isinstance(value,bool) and isinstance(value,(int,float)) and math.isfinite(value)


def validate_record(record,candidate_id,kind,engine,project=None,candidate=None):
    if not isinstance(record,dict) or record.get('candidateId')!=candidate_id or record.get('kind')!=kind or record.get('engine')!=engine:
        raise ValueError('Saved replay candidate, case or engine identity mismatch.')
    payload=record.get('payload');cfg=settings(payload)
    if payload['engine']!=engine:raise ValueError('Saved payload engine mismatch.')
    if cfg['caseConfig'].get('kind')!=('terrain-stability' if kind=='terrain' else kind):
        raise ValueError('Saved replay case configuration mismatch.')
    if project is not None and canonical(payload['params'])!=canonical(project.get('params')):
        raise ValueError('Saved replay geometry does not match the captured mechanism.')
    if candidate is not None:
        hw=candidate.get('hardware')
        if not isinstance(hw,dict) or canonical(cfg['actuatorConfig'])!=canonical(hw.get('actuatorConfig')):
            raise ValueError('Saved replay actuator does not match the selected exact candidate.')
        motor=cfg['motorConfig']
        if motor.get('gearRatio')!=cfg['actuatorConfig'].get('ratio') or motor.get('rotorInertiaKgM2')!=hw.get('rotorInertiaKgM2'):
            raise ValueError('Saved replay gearing or rotor inertia mismatch.')
    result=record.get('result')
    if not isinstance(result,dict) or result.get('engine')!=engine or result.get('schema')!='kinefold/contact-v2':
        raise ValueError('Saved replay result is not a captured contact trajectory for this engine.')
    for key in CONFIG_KEYS:
        if key in cfg and canonical(result.get(key))!=canonical(cfg[key]):
            raise ValueError('Saved replay result '+key+' differs from its exact payload.')
        if key not in cfg and key in result:raise ValueError('Saved replay result has unexpected '+key+'.')
    snap=result.get('snapshot')
    if isinstance(snap,dict):
        for key in CONFIG_KEYS:
            name='solverConfig' if key=='runConfig' else key
            if key in cfg and name in snap and canonical(snap[name])!=canonical(cfg[key]):
                raise ValueError('Saved replay snapshot '+name+' differs from its payload.')
    rows=result.get('rows');frames=result.get('frames')
    if not isinstance(rows,list) or not rows or len(rows)>20001 or not isinstance(frames,list) or len(frames)!=len(rows):
        raise ValueError('Saved replay needs nonempty aligned rows and frames.')
    previous=-1.
    for row,frame in zip(rows,frames):
        if not isinstance(row,dict) or not isinstance(frame,dict):raise ValueError('Malformed replay frame.')
        t=row.get('t');ft=frame.get('t')
        if not finite_number(t) or not finite_number(ft) or t<0 or t+1e-10<previous or abs(t-ft)>1e-8:
            raise ValueError('Saved replay has invalid/nonmonotonic frame times.')
        for key in ('theta2','chassisZMm','wheelZMm'):
            if not finite_number(row.get(key)):raise ValueError('Saved replay row is missing finite '+key+'.')
        for key in ('theta2','theta4','theta5','theta6','wheelAngle'):
            if not finite_number(frame.get(key)):raise ValueError('Saved replay frame is missing finite '+key+'.')
        for key in ('A','B','C','terrainOffsetMm'):
            point=frame.get(key)
            if not isinstance(point,list) or len(point)!=3 or not all(finite_number(v) for v in point):
                raise ValueError('Saved replay frame has invalid '+key+' coordinates.')
        if abs(frame['theta2']-row['theta2'])>1e-7:raise ValueError('Saved replay row/frame pose mismatch.')
        previous=t
    if abs(rows[0]['t'])>1e-8:raise ValueError('Saved replay must retain its initial state.')
    canonical(result)
    return record


def make_bundle(original_job_id,candidate,kind,project,runs,identity=None,warnings=None,source='saved-comparison'):
    if kind not in KINDS or not isinstance(candidate,dict) or not isinstance(candidate.get('id'),str):raise ValueError('Invalid replay selection.')
    valid_id(original_job_id,'comparison')
    if set(runs)!=set(ENGINES):raise ValueError('Both exact saved engines are required for paired replay.')
    for engine in ENGINES:validate_record(runs[engine],candidate['id'],kind,engine,project,candidate)
    a=settings(runs['analytical']['payload']);b=settings(runs['pymunk']['payload'])
    if canonical(a)!=canonical(b):raise ValueError('Analytical and Pymunk saved settings differ; mixed captures cannot be replayed together.')
    ah=runs['analytical']['result'].get('designHash');ph=runs['pymunk']['result'].get('designHash')
    if ah and ph and ah!=ph:raise ValueError('Saved engine design hashes differ.')
    bundle=dict(schema='kinefold/comparison-replay-v1',originalJobId=original_job_id,
        candidateId=candidate['id'],candidate=copy.deepcopy(candidate),kind=kind,
        project=copy.deepcopy(project),settingsHash=digest(a),runs=copy.deepcopy(runs),
        identity=copy.deepcopy(identity or {}),source=source,warnings=list(warnings or []))
    if len(canonical(bundle).encode('utf-8'))>MAX_JSON:raise ValueError('Paired replay exceeds 16 MiB; reduce output in a new capture.')
    return bundle


class ComparisonReplayService:
    """Read saved cases; own only newly requested paired-case workers."""
    def __init__(self,root,python_executable,shared_lock=None,main_busy=None,worker_script=None):
        self.root=Path(root).resolve();self.python=Path(python_executable)
        self.comparisons=self.root/'.preview'/'actuator-comparisons'
        self.jobs=self.root/'.preview'/'actuator-replays'
        self.worker_script=Path(worker_script) if worker_script else self.root/'comparison_replay_worker.py'
        self.shared_lock=shared_lock;self.main_busy=main_busy or (lambda:False)
        self.lock=threading.RLock();self.process=None;self.current=None;self.closed=False;self._lock_owned=False
        if self.jobs.exists():
            for directory in self.jobs.iterdir():
                try:
                    if not directory.is_dir():continue
                    valid_id(directory.name);path=directory/'status.json'
                    if path.is_file():
                        state=read_json(path)
                        if isinstance(state,dict) and state.get('state')=='running':
                            state.update(state='failed',message='Replay interrupted before server restart; captured inputs and partial records retained. No old PID was trusted.')
                            atomic_json(path,state)
                except (ValueError,OSError):continue

    @property
    def busy(self):
        with self.lock:return self.process is not None and self.process.poll() is None

    def _selection(self,payload):
        job_id=valid_id(payload.get('jobId'),'comparison');kind=payload.get('kind');cid=payload.get('candidateId')
        if kind not in KINDS or not isinstance(cid,str) or not 1<=len(cid)<=400:raise ValueError('Choose one known exact candidate and landing, jump or terrain.')
        directory=self.comparisons/job_id
        if not (directory/'result.json').is_file():raise ValueError('Comparison has no captured candidate results yet.')
        result=read_json(directory/'result.json')
        if not isinstance(result,dict) or result.get('schema')!='kinefold/automatic-actuator-comparison-v1' or not isinstance(result.get('candidates'),list):
            raise ValueError('Stored comparison result schema/candidate list is invalid.')
        candidate=next((c for c in result['candidates'] if isinstance(c,dict) and c.get('id')==cid),None)
        if candidate is None:raise ValueError('Candidate is not part of this captured comparison.')
        project=result.get('project');identity=result.get('identity',{})
        if not isinstance(project,dict) or project.get('schema')!='kinefold/project-v3' or not isinstance(project.get('params'),dict):raise ValueError('Comparison does not retain a complete captured project.')
        if not isinstance(identity,dict) or not isinstance(result.get('assumptions'),dict):raise ValueError('Stored comparison identity/assumptions are invalid.')
        if identity.get('projectHash') and digest(project)!=identity['projectHash']:raise ValueError('Captured project hash mismatch.')
        if identity.get('assumptionsHash') and digest(result.get('assumptions'))!=identity['assumptionsHash']:raise ValueError('Captured assumption hash mismatch.')
        return directory,result,candidate,kind

    def _original_records(self,directory,parent,candidate,kind):
        runs={}
        for engine in ENGINES:
            path=directory/(digest(candidate['id'])[:20]+'-'+engine+'-'+kind+'.json')
            if path.is_file():
                record=read_json(path)
                validate_record(record,candidate['id'],kind,engine,parent['project'],candidate)
                runs[engine]=record
        if len(runs)==2 and canonical(settings(runs['analytical']['payload']))!=canonical(settings(runs['pymunk']['payload'])):
            raise ValueError('Saved engine payloads differ; refusing mixed replay settings.')
        return runs

    def _index(self):
        path=self.jobs/'index.json'
        value=read_json(path) if path.is_file() else {}
        if not isinstance(value,dict):raise ValueError('Saved replay index is invalid.')
        return value

    def _key(self,job_id,candidate_id,kind):return digest(dict(jobId=job_id,candidateId=candidate_id,kind=kind))

    def _job(self,replay_id=None):
        rid=replay_id or self.current
        if not rid and (self.jobs/'latest-job.json').is_file():rid=read_json(self.jobs/'latest-job.json').get('replayId')
        rid=valid_id(rid);directory=self.jobs/rid
        if not (directory/'status.json').is_file():raise ValueError('Unknown replay job.')
        state=read_json(directory/'status.json');progress=directory/'progress.json'
        if not isinstance(state,dict) or state.get('id')!=rid or state.get('state') not in TERMINAL|{'running'}:
            raise ValueError('Stored replay status identity/state is invalid.')
        if progress.is_file():
            update=read_json(progress);update.pop('state',None);state.update(update)
        return directory,state

    def cached(self,payload):
        directory,parent,candidate,kind=self._selection(payload);job_id=payload['jobId']
        index=self._index();rid=index.get(self._key(job_id,candidate['id'],kind))
        if rid:
            replay_dir,state=self._job(rid)
            if any(state.get(k)!=v for k,v in (('originalJobId',job_id),('candidateId',candidate['id']),('kind',kind))):
                raise ValueError('Stored replay job selection mismatch.')
            if state['state']=='running':
                return dict(ok=True,ready=False,replayJob=state,missing=list(ENGINES))
            if state['state']=='complete' and (replay_dir/'bundle.json').is_file():
                bundle=read_json(replay_dir/'bundle.json')
                if bundle.get('originalJobId')!=job_id or bundle.get('candidateId')!=candidate['id'] or bundle.get('kind')!=kind:
                    raise ValueError('Stored replay index identity mismatch.')
                checked=make_bundle(job_id,candidate,kind,parent['project'],bundle.get('runs',{}),bundle.get('identity'),bundle.get('warnings'),bundle.get('source','saved-replay'))
                if bundle.get('settingsHash')!=checked['settingsHash']:raise ValueError('Stored replay settings hash mismatch.')
                return dict(ok=True,ready=True,bundle=checked,replayJob=state)
        runs=self._original_records(directory,parent,candidate,kind)
        if len(runs)==2:
            identity=copy.deepcopy(parent.get('identity',{}))
            if parent.get('review'):identity['documentedReview']=copy.deepcopy(parent['review'])
            bundle=make_bundle(job_id,candidate,kind,parent['project'],runs,identity,
                ['Exact captured settings and stored frames; active Studio inputs are not used.'],source='saved-comparison')
            return dict(ok=True,ready=True,bundle=bundle)
        return dict(ok=True,ready=False,originalJobId=job_id,candidateId=candidate['id'],kind=kind,
            missing=[engine for engine in ENGINES if engine not in runs],available=list(runs))

    def _release(self):
        if self._lock_owned:self.shared_lock.release();self._lock_owned=False

    def _start(self,payload):
        if self.closed:raise ValueError('Replay service is closed.')
        directory,parent,candidate,kind=self._selection(payload)
        cached=self.cached(payload)
        if cached['ready'] and not payload.get('force',False):return cached
        if cached.get('replayJob',{}).get('state')=='running' and not payload.get('force',False):return cached
        if self.busy or self.main_busy():raise ValueError('Another comparison/replay is running; wait or cancel it first.')
        if not self.python.is_file() or not self.worker_script.is_file():raise ValueError('Set up the app numerical environment before running a saved case.')
        if not isinstance(candidate.get('hardware'),dict):raise ValueError('This candidate has unresolved hardware. Create a new comparison with explicit missing-data assumptions first.')
        original=self._original_records(directory,parent,candidate,kind)
        base_payload=copy.deepcopy(next(iter(original.values()))['payload']) if original else None
        if base_payload is None:
            catalog_path=self.root/'motor-gearbox-catalog.json'
            if not catalog_path.is_file() or digest(read_json(catalog_path))!=parent.get('identity',{}).get('catalogHash'):
                raise ValueError('Catalog has changed or its captured hash is unavailable. Existing frames remain replayable; create a new comparison to simulate an unrun candidate.')
            assert_generator_sources(self.worker_script.parent,parent.get('identity',{}),parent.get('review'))
        if self.shared_lock is not None:
            if not self.shared_lock.acquire(blocking=False):raise ValueError('Another physics run is active; retry when it completes.')
            self._lock_owned=True
        rid=uuid.uuid4().hex;target=self.jobs/rid
        capture=dict(schema='kinefold/comparison-replay-request-v1',originalJobId=payload['jobId'],
            candidate=copy.deepcopy(candidate),kind=kind,project=copy.deepcopy(parent['project']),
            assumptions=copy.deepcopy(parent['assumptions']),originalIdentity=copy.deepcopy(parent.get('identity',{})),
            originalReview=copy.deepcopy(parent.get('review')),basePayload=base_payload,
            originalPayloadHash=digest(settings(base_payload)) if base_payload else None)
        budget=parent.get('budget',{})
        requested_seconds=budget.get('maxSeconds',180) if isinstance(budget,dict) else None
        if not finite_number(requested_seconds) or not 1<=requested_seconds<=600:
            self._release();raise ValueError('Stored comparison wall-time budget is invalid.')
        seconds=min(300,max(30,requested_seconds))
        capture['maxSeconds']=seconds
        state=dict(id=rid,state='running',originalJobId=payload['jobId'],candidateId=candidate['id'],kind=kind,
            createdAt=time.time(),progress=0.,stage='captured',message='Captured exact selected-case settings; both engines will run independently.')
        try:
            target.mkdir(parents=True,exist_ok=False);atomic_json(target/'request.json',capture);atomic_json(target/'status.json',state)
            log=(target/'worker.log').open('wb')
            try:
                self.process=subprocess.Popen([str(self.python),str(self.worker_script),'--request',str(target/'request.json'),'--output',str(target)],
                    cwd=self.root,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            finally:log.close()
            self.current=rid
            index=self._index();index[self._key(payload['jobId'],candidate['id'],kind)]=rid;atomic_json(self.jobs/'index.json',index)
            atomic_json(self.jobs/'latest-job.json',dict(schema='kinefold/replay-job-pointer-v1',replayId=rid))
            threading.Thread(target=self._monitor,args=(rid,self.process,seconds),daemon=True).start()
            return dict(ok=True,ready=False,replayJob=state)
        except Exception:
            try:
                if self.process is not None and self.process.poll() is None:
                    self.process.terminate()
                    try:self.process.wait(timeout=3)
                    except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=3)
            finally:self.process=None;self._release()
            raise

    def _monitor(self,rid,process,seconds):
        try:
            try:process.wait(timeout=seconds+5)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:process.wait(timeout=3)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=3)
                with self.lock:
                    directory,state=self._job(rid)
                    if state['state'] not in TERMINAL:
                        state.update(state='timed-out',message='Owned replay exceeded its bounded time limit; captured settings retained.');atomic_json(directory/'status.json',state)
            with self.lock:
                directory,state=self._job(rid)
                if state['state'] not in TERMINAL:
                    error=read_json(directory/'error.json').get('error') if (directory/'error.json').is_file() else None
                    complete=process.returncode==0 and (directory/'bundle.json').is_file()
                    state.update(state='complete' if complete else 'failed',finishedAt=time.time(),
                        message='Both saved-case engine trajectories are ready.' if complete else error or 'Saved-case worker failed; app-local log retained.')
                    atomic_json(directory/'status.json',state)
        finally:
            with self.lock:
                if self.process is process:self.process=None
                self._release()

    def handle(self,payload):
        if not isinstance(payload,dict) or not isinstance(payload.get('action'),str):raise ValueError('Replay action is required.')
        action=payload.get('action')
        with self.lock:
            if action in ('replay','run-replay'):
                allowed={'action','jobId','candidateId','kind'}|({'force'} if action=='run-replay' else set())
                if set(payload)-allowed or not {'jobId','candidateId','kind'}<=set(payload):raise ValueError('Replay requires only comparison jobId, candidateId and kind.')
                if 'force' in payload and type(payload['force']) is not bool:raise ValueError('force must be boolean.')
                return self.cached(payload) if action=='replay' else self._start(payload)
            if action not in ('replay-status','replay-cancel','replay-result'):raise ValueError('Unknown replay action.')
            if set(payload)-{'action','replayId'}:raise ValueError('Replay status/result/cancel accepts only replayId.')
            directory,state=self._job(payload.get('replayId'))
            if action=='replay-cancel' and state['state'] not in TERMINAL:
                if state['id']!=self.current or self.process is None:raise ValueError('Cannot cancel a replay not owned by this service.')
                self.process.terminate();state.update(state='cancelled',message='Cancelled owned selected-case worker; captured inputs retained.');atomic_json(directory/'status.json',state)
            if action=='replay-result':
                bundle=read_json(directory/'bundle.json') if state['state']=='complete' and (directory/'bundle.json').is_file() else None
                if bundle is not None:
                    checked=make_bundle(bundle['originalJobId'],bundle['candidate'],bundle['kind'],bundle['project'],bundle['runs'],bundle.get('identity'),bundle.get('warnings'),bundle.get('source'))
                    if checked['settingsHash']!=bundle.get('settingsHash'):raise ValueError('Stored replay settings hash mismatch.')
                    bundle=checked
                return dict(ok=True,ready=bundle is not None,replayJob=state,bundle=bundle)
            return dict(ok=True,replayJob=state)

    def close(self):
        with self.lock:
            self.closed=True
            if self.process is not None and self.process.poll() is None:
                self.process.terminate();directory,state=self._job(self.current)
                state.update(state='cancelled',message='Server shutdown stopped its owned selected-case worker.');atomic_json(directory/'status.json',state)
                try:self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=3)
            self._release()
