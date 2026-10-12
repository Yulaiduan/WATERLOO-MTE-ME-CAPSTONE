"""Verify actual owned native inversion windows and graceful diagnostic exit.

Run .venv/Scripts/python.exe scripts/verify_inversion_native.py from app root.
Inputs SI dual-rope/bellcrank presets; outputs ignored PNG/config/state/log
evidence. Opens its own Pygame windows; --quit-at-end closes only those windows.
No hardware proof or unrelated desktop interaction; installed display required.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from inversion import config

def main():
    out=ROOT/'artifacts/inversion-native-live';out.mkdir(parents=True,exist_ok=True)
    for preset in ('dual_rope','knee_bellcrank'):
        case=out/(preset+'.json');state=out/(preset+'-state.json');image=out/(preset+'.png')
        case.write_text(json.dumps({'config':config({'preset':preset})}),encoding='utf-8')
        result=subprocess.run([sys.executable,str(ROOT/'debug_inversion_gui.py'),'--config',str(case),'--run','--quit-at-end','--state-file',str(state),'--snapshot-file',str(image)],cwd=ROOT,capture_output=True,text=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        (out/(preset+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
        data=json.loads(state.read_text(encoding='utf-8'))
        assert result.returncode==0,result.stderr
        assert data['solver_steps']>=4000 and data['status']=='closed'
        if os.name=='nt':assert data['window_id']
        assert image.is_file()
        print('PASS actual native:',preset,'steps',data['solver_steps'],'shapes',data['shape_count'],'constraints',data['constraint_count'])

if __name__=='__main__':main()
