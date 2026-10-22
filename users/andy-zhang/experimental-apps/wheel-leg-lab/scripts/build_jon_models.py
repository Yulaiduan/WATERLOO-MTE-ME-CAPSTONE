"""Expose Jonathan's exact math as reference functions in the original bench UI.

Run: python scripts/build_jon_models.py, also called by npm run build.
Inputs: repository v2 HTML model scripts, mm/deg/kg/N/Nm; no UI is copied.
Outputs: ignored web/jon-models.js with original scripts and SHA-256 provenance.
Standard library only. No source snippet is executed during this build.
Limits: reference statics are fixed-A; existing suspension dynamics stay separate.
"""
from pathlib import Path
import hashlib
import json
import re

def main():
    root=Path(__file__).resolve().parents[1]
    source=root.parents[2]/'jonathan-xie/experimental-apps/vsl-solver/v2/v2-quasi-static.html'
    raw=source.read_bytes();text=raw.decode('utf-8');scripts=dict(re.findall(r'<script id="([^"]+)">(.*?)</script>',text,re.S))
    names=('solver-model','statics-model','global-maxima-model')
    if any(name not in scripts for name in names):raise ValueError('Jonathan v2 reference models missing.')
    metadata={'source':'users/jonathan-xie/experimental-apps/vsl-solver/v2/v2-quasi-static.html','sha256':hashlib.sha256(raw).hexdigest(),'models':{name:hashlib.sha256(scripts[name].encode()).hexdigest() for name in names}}
    output='\n'.join(scripts[name] for name in names)+'\nwindow.JonReference={VSL,VSLStatic,VSLPeaks,source:'+json.dumps(metadata)+'};\n'
    (root/'web/jon-models.js').write_text(output,encoding='utf-8',newline='\n')
    print('Built original Jonathan math reference functions; no copied editor.')

if __name__=='__main__':main()
