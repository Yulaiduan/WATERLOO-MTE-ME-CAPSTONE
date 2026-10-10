"""Launch/monitor the actual local live Pymunk desktop app from the browser.

Imported by loopback server: launch(SI config), status(session_id). Outputs:
owned JSON/log files and a visible Pygame window making live Space.step calls.
No requested script/path is executed; this opens on the simulation host desktop.
Standard library plus the app-local installed Pymunk/Pygame runtime.
"""
import json
import os
from pathlib import Path
import subprocess
import threading
import uuid
from physics import config as validate_config, build
ROOT=Path(__file__).resolve().parent
DIRECTORY=ROOT/'.preview/native-gui'
PROCESSES={}
CASES={}
LOCK=threading.Lock()

def launch(values):
    study=isinstance(values,dict) and values.get('model')=='counterbalance'
    if study:
        if set(values)!={'model','config'}:raise ValueError('Counterbalance native launch needs only model/config fields.')
        import counterbalance
        resolved=counterbalance.config(values['config']);counterbalance.build(resolved)
        program='debug_counterbalance_gui.py'
    else:
        resolved=validate_config(values)
        build(resolved)  # Resolve preload/geometry errors before opening a window.
        program='debug_gui.py'
    with LOCK:
        reusable=next((key for key,process in PROCESSES.items() if process.poll() is None and CASES.get(key)==(program,resolved)),None)
    if reusable:
        existing=show(reusable)
        if existing['status'] in ('starting','ready','running'):
            return {**existing,'reused':True,'message':'Showing the existing live Pymunk desktop window for this profile.'}
    identifier=str(uuid.uuid4())
    DIRECTORY.mkdir(parents=True,exist_ok=True)
    case=DIRECTORY/(identifier+'.config.json');state=DIRECTORY/(identifier+'.state.json');log=DIRECTORY/(identifier+'.log')
    case.write_text(json.dumps({'config':resolved}),encoding='utf-8')
    python=ROOT/'.venv/Scripts/python.exe' if os.name=='nt' else ROOT/'.venv/bin/python'
    if not python.is_file():raise ValueError('Native runtime missing. Run Setup Motion Lab.cmd.')
    with log.open('wb') as output:
        process=subprocess.Popen([str(python),str(ROOT/program),'--config',str(case),'--run','--loop','--state-file',str(state),'--snapshot-file',str(DIRECTORY/(identifier+'.png'))],cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    with LOCK:PROCESSES[identifier]=process;CASES[identifier]=(program,resolved)
    return {'id':identifier,'pid':process.pid,'status':'starting','mode':'native-live','message':'Opening the live Pymunk desktop window on this computer.'}

def status(identifier):
    try:identifier=str(uuid.UUID(identifier))
    except ValueError:raise ValueError('Invalid native viewer ID.')
    with LOCK:process=PROCESSES.get(identifier)
    if process is None:raise ValueError('Native viewer session is not owned by this server.')
    path=DIRECTORY/(identifier+'.state.json');result={'id':identifier,'pid':process.pid,'status':'starting','mode':'native-live'}
    if path.is_file():
        try:result.update(json.loads(path.read_text(encoding='utf-8')))
        except (json.JSONDecodeError,OSError):pass
    code=process.poll()
    if code is not None:
        result['status']='closed' if code==0 else 'failed';result['exit_code']=code
        if code:
            log=DIRECTORY/(identifier+'.log');result['error']=log.read_text(encoding='utf-8',errors='replace')[-2500:] if log.exists() else 'Native window failed to start.'
    return result

def show(identifier):
    """Restore only this server's verified live desktop window."""
    current=status(identifier)
    hwnd=current.get('window_id')
    if os.name=='nt' and hwnd and current['status'] in ('ready','running'):
        import ctypes
        from ctypes import wintypes
        user32=ctypes.WinDLL('user32',use_last_error=True)
        user32.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
        user32.ShowWindow.argtypes=[wintypes.HWND,ctypes.c_int]
        user32.SetForegroundWindow.argtypes=[wintypes.HWND]
        user32.IsWindowVisible.argtypes=[wintypes.HWND]
        owner=wintypes.DWORD();user32.GetWindowThreadProcessId(hwnd,ctypes.byref(owner))
        if owner.value!=current['pid']:raise ValueError('Native window ownership changed; no window restored.')
        user32.ShowWindow(hwnd,9)
        current['foreground_requested']=bool(user32.SetForegroundWindow(hwnd))
        current['window_shown']=bool(user32.IsWindowVisible(hwnd))
    return current
