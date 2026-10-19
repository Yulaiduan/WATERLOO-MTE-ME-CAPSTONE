"""Serve Jonathan's unchanged V4 source inside Motion Lab with a narrow UI bridge.

Invocation: imported by server.py, served at /vsl-v4/ on the existing loopback port.
Inputs: tracked sibling V4 HTML/docs/presets (mm, deg, kg, N, Nm); no user file paths.
Outputs: HTML with app-owned theme/bridge references, or explicitly allowed source assets.
Limitations: quasi-static source model; integration does not add dynamics or certify hardware.
"""
from pathlib import Path
import hashlib
import mimetypes

SOURCE = Path(__file__).resolve().parents[3] / 'jonathan-xie/experimental-apps/leg-solver'
FILES = {
    'v4-pulley.html', 'v4-model.md', 'v2-model.md', 'v4-textbook.md',
    'v4-textbook-10mm.json', 'v4-textbook-10mm.png', 'v4-tuning.md',
    'v4-tuning.png', 'v3-model.md', 'v4-sample-13kg-fitted.json',
    'v4-sample-13kg-point-rule.json', 'v4-tuning.json',
}

def resource(route):
    """Return (bytes, MIME) for an explicit app route, or None for an unknown route."""
    if not route.startswith('/vsl-v4/'):
        return None
    name = route[len('/vsl-v4/'):] or 'v4-pulley.html'
    if name not in FILES:
        return None
    raw = (SOURCE / name).read_bytes()
    if name == 'v4-pulley.html':
        sha = hashlib.sha256(raw).hexdigest()
        text = raw.decode('utf-8')
        text = text.replace('</head>', f'<meta name="vsl-source-sha256" content="{sha}">'
                            '<link rel="stylesheet" href="/sizing/vsl-theme.css">'
                            '<script src="/theme.js"></script></head>', 1)
        text = text.replace('</body>', '<script src="/sizing/vsl-bridge.js"></script></body>', 1)
        return text.encode('utf-8'), 'text/html; charset=utf-8'
    return raw, (mimetypes.guess_type(name)[0] or 'application/octet-stream') + ('; charset=utf-8' if name.endswith(('.md', '.json')) else '')
