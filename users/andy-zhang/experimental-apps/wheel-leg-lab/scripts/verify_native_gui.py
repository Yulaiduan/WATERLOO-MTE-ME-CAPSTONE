"""Verify browser-triggered live Pymunk desktop solving and owned-window close.

Run: .venv/Scripts/python.exe scripts/verify_native_gui.py with Motion Lab running.
Inputs: loopback 4186, 200 mm wheel fixtures and prescribed/free lever profiles.
Outputs: console evidence and ignored artifacts/native-api-verification.json.
Uses standard Python/Windows APIs; opens a real visible window, then closes only
the verified window whose PID matches this test's API-created session. No files
deleted; Windows-only GUI evidence, not contact or hardware validation.
"""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:4186'

def request(route, values=None, origin=BASE):
    data=None if values is None else json.dumps(values).encode()
    req=Request(BASE+route,data=data,headers={'Content-Type':'application/json','Origin':origin})
    with urlopen(req,timeout=10) as response:return response.status,json.load(response)

def close_owned(state):
    hwnd=state.get('window_id')
    if not hwnd:return
    user32=ctypes.WinDLL('user32',use_last_error=True)
    user32.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
    user32.PostMessageW.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
    owner=wintypes.DWORD();user32.GetWindowThreadProcessId(hwnd,ctypes.byref(owner))
    if owner.value!=state['pid']:raise RuntimeError('Window ownership changed; nothing closed.')
    if not user32.PostMessageW(hwnd,0x0010,0,0):raise ctypes.WinError(ctypes.get_last_error())

def main():
    if os.name!='nt':raise RuntimeError('This verification requires the Windows desktop runtime.')
    for route,values,origin,expected in (
        ('/api/native-gui',{},'https://example.invalid',403),
        ('/api/native-gui',{'spring_topology':'direct_scissor','spring_mode':'extension'},BASE,400),
        ('/api/native-gui/not-a-session',None,BASE,404)):
        try:request(route,values,origin);raise AssertionError('Invalid request was accepted.')
        except HTTPError as error:assert error.code==expected,(error.code,error.read())
    cases=[('knee_capture',{'spring_topology':'knee_capture','radius':.2,'duration':1.2,'start':.3,'position_amplitude':.008},6),
           ('gravity_balance',{'spring_topology':'gravity_balance','radius':.2,'duration':1.2,'start':.3,'position_amplitude':.008},6),
           ('replacement_suspension',{'model':'wheel_leg','config':{**request('/api/suspension-architecture/defaults')[1],'duration':1.2,'start':.3,'position_amplitude':.008},'guide_visualization':{'pretension_N':60.,'show_force_vectors':True,'applied_to_solver':False}},6),
           ('counterbalance_prescribed',{'model':'counterbalance','config':{'duration':1.2,'start':.3,'angle_amplitude_deg':20.}},2),
           ('counterbalance_free',{'model':'counterbalance','config':{'mode':'free','duration':1.2,'initial_speed_deg':10.}},1)]
    evidence=[verify_case(name,values,constraints) for name,values,constraints in cases]
    artifact=ROOT/'artifacts/native-api-verification.json';artifact.parent.mkdir(exist_ok=True)
    artifact.write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    print('PASS: five live fixtures, single replacement suspension with visible guide, owned-window restore/reuse and graceful close.')

def verify_case(name,values,constraints):
    code,session=request('/api/native-gui',values)
    assert code==202
    state={};states=[]
    try:
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            _,state=request('/api/native-gui/'+session['id']);states.append(state)
            assert state['status']!='failed',state
            if state.get('loops',0)>=1 and state.get('solver_steps',0)>1500:break
            time.sleep(.25)
        assert state.get('window_id',0)>0 and state.get('solver_steps',0)>1500,state
        c=values.get('config',values)
        expected_shapes=3+int(c.get('chassis_shape_enabled',False) or c.get('aux_spring_enabled',False))+2*int(c.get('guide_pulleys_visible',False))
        assert state['loops']>=1 and not state['paused'] and state['shape_count']==expected_shapes and state['constraint_count']==constraints,state
        if values.get('model')=='wheel_leg':
            saved=json.loads((ROOT/'.preview/native-gui'/f"{session['id']}.config.json").read_text(encoding='utf-8'))
            assert saved['guide_visualization']=={'pretension_N':60.,'show_force_vectors':True},saved
            assert 'pretension_N' not in saved['config'] and saved['config']['aux_spring_enabled'] is False
        assert any(a.get('solver_steps',0)<b.get('solver_steps',0) for a,b in zip(states,states[1:])),states
        _,shown=request('/api/native-gui/'+session['id']+'/show',{})
        assert shown['pid']==state['pid'] and shown['window_shown'],shown
        _,reused=request('/api/native-gui',values)
        assert reused['id']==session['id'] and reused['reused'] and reused['window_shown'],reused
        print(f"PASS: {name}, real desktop HWND {state['window_id']}, PID {state['pid']}, {state['solver_steps']} live steps, {state['loops']} loop(s).",flush=True)
    finally:close_owned(state)
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        _,closed=request('/api/native-gui/'+session['id'])
        if closed['status']=='closed' and closed.get('exit_code')==0:break
        time.sleep(.1)
    assert closed['status']=='closed' and closed['exit_code']==0,closed
    return {'name':name,'session':session,'states':states,'closed':closed}

if __name__=='__main__':main()
