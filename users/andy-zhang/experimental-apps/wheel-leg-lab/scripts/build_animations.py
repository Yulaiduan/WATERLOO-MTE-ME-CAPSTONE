"""Export both chats' retained animation fragments as portable standalone pages.

Run: python scripts/build_animations.py from app root (also npm run build).
Inputs: app-local HTML fragments; geometric dimensions/units are labeled in each.
Outputs: ignored web/animations and web/recorded HTML; no simulation is executed.
Dependencies: Python standard library; local viewer CSS, state adapter and D3.
Limitations: exports kinematics/recorded states, not collision or hardware validation.
"""
from pathlib import Path
from html import escape
import re
import shutil
ROOT=Path(__file__).resolve().parents[1]
STUDIES=[
 ('linear-leg','Grounded 2:1 straight-line leg','Equal links, moving belt material and exact vertical wheel-centre path.'),
 ('coaxial-wheel-leg','Independent coaxial wheel drive','A second rotary input at the chassis drives the wheel through two 1:1 stages.'),
 ('tilted-invertible-leg','Tilted invertible line','A timing offset tilts the exact straight path while retaining the ideal inversion.'),
 ('left-tilted-leg','Mirrored 12° left tilt','Mirrored timing and geometry; below-left continues into above-right.'),
 ('two-position-left-leg','Two-position timing study','A 24° hip-pulley reindex switches left-working branches; retained alternative, rejected fixed-pulley assumption.'),
 ('fixed-ratio-left-leg','Fixed 4:1 near-linear working strokes','250 / 168.45 mm links, about 42.35 mm stroke and 0.768 mm path error; large inversion excursion.'),
 ('leg-path-family','Fixed-ratio path family','Compare ratios and unequal links; equal-link 2:1 is the globally straight reference.'),
]

def page(title,fragment):
 fragment=fragment.replace('https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js','/d3.min.js')
 fragment=re.sub(r'https://cdn.jsdelivr.net/npm/plotly.js-dist-min@[^/]+/plotly.min.js','/plotly.min.js',fragment)
 return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
         '<title>'+escape(title)+'</title><link rel="stylesheet" href="/viewer.css"><script src="/theme.js"></script><script src="/viewer-state.js"></script></head><body><main>'
         '<header><h1>'+escape(title)+'</h1><a href="/animations/">All studies</a><a href="/" target="_top">Motion Lab</a></header>'+fragment+'</main></body></html>')

def main():
 runtime=ROOT/'node_modules/plotly.js-dist-min/plotly.min.js'
 if not runtime.exists():raise SystemExit('Plotly runtime missing; run npm ci before building.')
 shutil.copyfile(runtime,ROOT/'web/plotly.min.js')
 for slug,title,_ in STUDIES:
  folder=ROOT/'web/animations'/slug;folder.mkdir(parents=True,exist_ok=True)
  (folder/'index.html').write_text(page(title,(ROOT/'animations'/f'{slug}.html').read_text(encoding='utf-8')),encoding='utf-8')
 folder=ROOT/'web/recorded';folder.mkdir(parents=True,exist_ok=True)
 (folder/'index.html').write_text(page('Recorded Pymunk playback',(ROOT/'animations/pymunk-remote-preview.html').read_text(encoding='utf-8')),encoding='utf-8')
 cards=''.join(f'<a href="/animations/{slug}/"><h2>{escape(title)}</h2><p>{escape(detail)}</p></a>' for slug,title,detail in STUDIES)
 cards+='<a href="/force-plots/"><h2>Wheel / link force calculator</h2><p>Radius, required travel, angles, force and synchronized equal-link animation.</p></a>'
 cards+='<a href="/linkage/"><h2>Detailed linkage bench</h2><p>Two-coordinate drive, spring, impedance, finite actuator response and local analysis.</p></a>'
 cards+='<a href="/physics/"><h2>Pymunk spring bench</h2><p>Actual engine, 50 mm extension spring, joint loads, pulse inputs and native debug view.</p></a>'
 cards+='<a href="/recorded/"><h2>Recorded remote preview</h2><p>Offline playback with moving disturbance profile and force values in N / kgf.</p></a>'
 gallery='<p class="scope">Andy Zhang · experimental studies from both chats · kinematics and fixture dynamics, not a validated CAMEL robot.</p><div class="gallery">'+cards+'</div>'
 (ROOT/'web/animations/index.html').write_text(page('Wheel Leg Lab studies',gallery),encoding='utf-8')
 print('Built seven motion studies, recorded preview and toolkit gallery.')

if __name__=='__main__':main()
