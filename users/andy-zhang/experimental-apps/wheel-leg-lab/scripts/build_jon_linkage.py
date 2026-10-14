"""Build Motion Lab's separate Jonathan v2 linkage from the original member source.

Run: python scripts/build_jon_linkage.py (also called by npm run build).
Inputs: sibling leg-solver v2 HTML, app-local adapter/CSS; mm, deg, kg, N, Nm.
Outputs: ignored web/jon-linkage page/assets and source/model SHA-256 manifest.
Dependencies: Python standard library. No solver or imported snippets are executed.
Limits: preserves the source analytical models; adds no dynamic/contact backend.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parents[2] / 'jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html'
MARKER = 'window.VSLApp={get parameters()'


def main():
    html = SOURCE.read_bytes().decode('utf-8')
    if html.count(MARKER) != 1:
        raise RuntimeError('Jonathan v2 UI interface changed; cross-check the adapter before building.')
    scripts = dict(re.findall(r'<script id="([^"]+)">(.*?)</script>', html, re.S))
    required = ('solver-model', 'statics-model', 'global-maxima-model')
    if any(key not in scripts for key in required):
        raise RuntimeError('Jonathan v2 analytical model scripts are missing.')
    adapter = (ROOT / 'jon-linkage/embedded-api.js').read_text(encoding='utf-8')
    html = html.replace(MARKER, adapter + '\n' + MARKER, 1)
    html = html.replace('</head>', '<link rel="stylesheet" href="/jon-linkage/style.css"></head>', 1)
    html = html.replace('</body>', '<script src="/jon-linkage/bridge.js"></script></body>', 1)
    folder = ROOT / 'web/jon-linkage'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'index.html').write_text(html, encoding='utf-8', newline='\n')
    for name in ('bridge.js', 'style.css'):
        shutil.copyfile(ROOT / 'jon-linkage' / name, folder / name)
    manifest = {
        'source': SOURCE.relative_to(ROOT.parents[3]).as_posix(),
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'models': {key: hashlib.sha256(scripts[key].encode()).hexdigest() for key in required},
        'adapter_sha256': hashlib.sha256(adapter.encode()).hexdigest(),
        'scope': 'Original kinematics, quasi-static equilibrium and bounded maxima; Motion Lab UI bridge only.',
    }
    (folder / 'source.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Built separate Jonathan v2 linkage; all three source model scripts preserved.')


if __name__ == '__main__':
    main()
