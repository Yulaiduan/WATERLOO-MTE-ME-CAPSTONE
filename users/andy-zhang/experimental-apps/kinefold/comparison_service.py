"""Standard-library local comparison job API, isolated from physics imports.

Preview server imports ComparisonService(app_root, python_executable=None,
shared_lock=None), calls handle(JSON), and close() on shutdown. Requests capture
project-v3 and mm/SI assumptions; results/details/exports stay inside the app.
One owned bounded subprocess runs at once, sharing the existing dynamics lock.
No shell, arbitrary executable/request paths, Downloads or live design writes.
"""
import copy
import json
from pathlib import Path
import subprocess
import threading
import time
import uuid

from actuator_comparison import (ASSUMPTIONS,BUDGET,canonical,digest,
    validate_assumptions,validate_budget)
from comparison_replay_service import ComparisonReplayService

MAX_JSON=16*1024*1024
TERMINAL={'complete','failed','cancelled','timed-out'}


def read_json(path):
    if path.stat().st_size>MAX_JSON:raise ValueError('Comparison JSON exceeds 16 MiB.')
    return json.loads(path.read_text(encoding='utf-8'))


def atomic_write(path,value):
    data=canonical(value)
    if len(data.encode())>MAX_JSON:raise ValueError('Comparison JSON exceeds 16 MiB.')
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:temporary.write_text(data,encoding='utf-8');temporary.replace(path)
    finally:
        if temporary.exists():temporary.unlink()


class ComparisonService:
    """Own one process and immutable per-job capture; standard-library only."""
    def __init__(self,root,python_executable=None,shared_lock=None):
        self.root=Path(root).resolve();self.jobs=self.root/'.preview'/'actuator-comparisons'
        self.python=Path(python_executable).resolve() if python_executable else self.root/'.venv'/('Scripts/python.exe' if __import__('os').name=='nt' else 'bin/python')
        self.shared_lock=shared_lock;self.lock=threading.RLock();self.current=None;self.process=None
        self.closed=False;self._lock_owned=False
        self.replays=ComparisonReplayService(self.root,self.python,shared_lock,
            main_busy=lambda:self.process is not None and self.process.poll() is None)
        # No PID is trusted after restart. Captures survive, but an old running
        # label cannot imply that a new server owns or can terminate its worker.
        if self.jobs.exists():
            for directory in self.jobs.iterdir():
                if not directory.is_dir() or len(directory.name)!=32 or any(c not in '0123456789abcdef' for c in directory.name):continue
                path=directory/'status.json'
                if path.exists():
                    try:
                        job=read_json(path)
                        if job.get('state')=='running':
                            job.update(state='failed',message='Interrupted before server restart; partial results retained. No old PID was trusted.')
                            atomic_write(path,job)
                    except (ValueError,OSError):continue

    @property
    def busy(self):
        with self.lock:return (self.process is not None and self.process.poll() is None) or self.replays.busy

    def _job_path(self,job_id):
        if not isinstance(job_id,str) or len(job_id)!=32 or any(c not in '0123456789abcdef' for c in job_id):raise ValueError('Invalid comparison job ID.')
        return self.jobs/job_id

    def _job(self,job_id=None):
        job_id=job_id or self.current
        if not job_id and (self.jobs/'latest-job.json').is_file():
            job_id=read_json(self.jobs/'latest-job.json').get('jobId')
        if not job_id:raise ValueError('No comparison job has been captured.')
        directory=self._job_path(job_id);status=directory/'status.json'
        if not status.exists():raise ValueError('Unknown comparison job.')
        job=read_json(status)
        progress=directory/'progress.json'
        if progress.exists():job.update(read_json(progress))
        # State is process-owned, progress is algorithm-owned.
        state=read_json(status)['state'];job['state']=state
        return directory,job

    def _settings(self):
        path=self.root/'profiles'/'actuator-comparison.json'
        if not path.exists():return dict(assumptions=dict(ASSUMPTIONS),budget=dict(BUDGET))
        saved=read_json(path)
        if not isinstance(saved,dict) or set(saved)!={'schema','assumptions','budget'} or saved['schema']!='kinefold/comparison-settings-v1':raise ValueError('Stored comparison settings are invalid; file left untouched.')
        return dict(assumptions=validate_assumptions(saved['assumptions']),budget=validate_budget(saved['budget']))

    def _start(self,payload):
        allowed={'action','project','assumptions','budget','selection'}
        if set(payload)-allowed:raise ValueError('Unknown comparison start fields.')
        if self.closed:raise ValueError('Comparison service is closed.')
        if self.busy:raise ValueError('A comparison job is already running; cancel or wait.')
        if not self.python.is_file():raise ValueError('Set up the app numerical environment before a finite comparison.')
        project=payload.get('project')
        if project is not None and (not isinstance(project,dict) or project.get('schema')!='kinefold/project-v3'):raise ValueError('Comparison requires a captured project-v3 design.')
        assumptions=validate_assumptions(payload.get('assumptions'));budget=validate_budget(payload.get('budget'))
        selection=payload.get('selection') or {}
        if not isinstance(selection,dict) or set(selection)-{'motorIds','gearboxIds'}:raise ValueError('Invalid exact catalog selection.')
        for ids in selection.values():
            if not isinstance(ids,list) or len(ids)>200 or any(not isinstance(x,str) or len(x)>200 for x in ids):raise ValueError('Invalid exact catalog selection IDs.')
        if self.shared_lock is not None:
            if not self.shared_lock.acquire(blocking=False):raise ValueError('Another physics run is active; retry after it completes.')
            self._lock_owned=True
        job_id=uuid.uuid4().hex;directory=self._job_path(job_id)
        try:
            directory.mkdir(parents=True,exist_ok=False)
            capture=dict(project=copy.deepcopy(project),assumptions=assumptions,budget=budget,selection=selection)
            atomic_write(directory/'request.json',capture)
            status=dict(id=job_id,state='running',createdAt=time.time(),progress=0.,stage='starting',message='Captured immutable comparison inputs.')
            atomic_write(directory/'status.json',status)
            log=(directory/'worker.log').open('wb')
            try:
                self.process=subprocess.Popen([str(self.python),str(self.root/'actuator_comparison.py'),
                    '--request',str(directory/'request.json'),'--output',str(directory)],cwd=self.root,
                    stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            finally:log.close()
            self.current=job_id
            atomic_write(self.jobs/'latest-job.json',dict(schema='kinefold/comparison-job-pointer-v1',jobId=job_id))
            threading.Thread(target=self._monitor,args=(job_id,self.process,budget['maxSeconds']),daemon=True).start()
            return dict(ok=True,job=status)
        except Exception:
            self._release();raise

    def _release(self):
        if self._lock_owned:self.shared_lock.release();self._lock_owned=False

    def _monitor(self,job_id,process,seconds):
        try:
            try:process.wait(timeout=seconds+15)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:process.wait(timeout=3)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=3)
                with self.lock:
                    directory,job=self._job(job_id)
                    if job['state'] not in TERMINAL:job.update(state='timed-out',message='Owned worker exceeded the bounded wall-time limit. Partial results retained.');atomic_write(directory/'status.json',job)
            with self.lock:
                directory,job=self._job(job_id)
                if job['state'] not in TERMINAL:
                    error=read_json(directory/'error.json').get('error') if (directory/'error.json').exists() else None
                    job.update(state='complete' if process.returncode==0 else 'failed',finishedAt=time.time(),
                        message='Comparison finished.' if process.returncode==0 else error or 'Comparison worker failed; inspect app-local worker.log.')
                    atomic_write(directory/'status.json',job)
        finally:
            with self.lock:
                if self.process is process:self.process=None
                self._release()

    def handle(self,payload):
        if not isinstance(payload,dict) or not isinstance(payload.get('action'),str):raise ValueError('Comparison action required.')
        action=payload['action']
        with self.lock:
            if action in ('replay','run-replay','replay-status','replay-cancel','replay-result'):
                return self.replays.handle(payload)
            if action in ('defaults','load'):
                if set(payload)!={'action'}:raise ValueError('Unexpected settings-load fields.')
                settings=dict(assumptions=dict(ASSUMPTIONS),budget=dict(BUDGET)) if action=='defaults' else self._settings()
                return dict(ok=True,**settings)
            if action=='save':
                if set(payload)-{'action','assumptions','budget'}:raise ValueError('Unexpected settings-save fields.')
                settings=dict(assumptions=validate_assumptions(payload.get('assumptions')),budget=validate_budget(payload.get('budget')))
                atomic_write(self.root/'profiles'/'actuator-comparison.json',dict(schema='kinefold/comparison-settings-v1',**settings))
                return dict(ok=True,**settings,savedPath='profiles/actuator-comparison.json')
            if action=='start':return self._start(payload)
            if action not in ('status','cancel','results','detail','export'):raise ValueError('Unknown comparison action.')
            if set(payload)-{'action','jobId','candidateId'}:raise ValueError('Unknown comparison job fields.')
            directory,job=self._job(payload.get('jobId'))
            if action=='status':return dict(ok=True,job=job)
            if action=='cancel':
                if job['state'] not in TERMINAL:
                    if job['id']!=self.current or not self.process:raise ValueError('Cannot cancel a process not owned by this service.')
                    self.process.terminate();job.update(state='cancelled',message='Cancelled owned worker; partial results retained.');atomic_write(directory/'status.json',job)
                return dict(ok=True,job=job)
            if not (directory/'result.json').exists():return dict(ok=True,job=job,result=None)
            result=read_json(directory/'result.json')
            if action=='results':return dict(ok=True,job=job,result=result)
            if action=='export':
                export=self.root/'exports'/('actuator-comparison-'+job['id']+'.json')
                atomic_write(export,result);return dict(ok=True,job=job,savedPath=export.relative_to(self.root).as_posix(),bytes=export.stat().st_size)
            candidate_id=payload.get('candidateId')
            candidate=next((r for r in result['candidates'] if r['id']==candidate_id),None)
            if not candidate:raise ValueError('Candidate is not part of this immutable job.')
            runs={engine:{} for engine in ('analytical','pymunk')}
            for engine in runs:
                for kind in ('landing','jump','terrain'):
                    path=directory/(digest(candidate_id)[:20]+'-'+engine+'-'+kind+'.json')
                    if path.exists():runs[engine][kind]=read_json(path)['result']
            response=dict(ok=True,job=job,candidate=candidate,runs=runs)
            if len(canonical(response).encode('utf-8'))>MAX_JSON:
                raise ValueError('Combined detail exceeds 16 MiB. Reduce output rate or duration for a new study; existing local case files are retained.')
            return response

    def close(self):
        with self.lock:
            self.closed=True
            self.replays.close()
            if self.process is not None and self.process.poll() is None:
                self.process.terminate()
                directory,job=self._job(self.current);job.update(state='cancelled',message='Server shutdown stopped its owned worker.');atomic_write(directory/'status.json',job)
                try:self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=3)
            self._release()
