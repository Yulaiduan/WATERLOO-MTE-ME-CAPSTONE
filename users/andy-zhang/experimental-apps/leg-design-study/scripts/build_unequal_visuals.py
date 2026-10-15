"""Draw labelled offline GIFs for four unequal-link full inversion examples.

Run from app: .venv/Scripts/python.exe scripts/build_unequal_visuals.py
Inputs: retained unequal-inversion-results.json; original mm/degree geometry.
Outputs: four curated GIFs and a small manifest in docs/unequal-animations/.
Uses pinned Pillow/NumPy and installed Windows fonts with a portable fallback.
Limits: kinematic illustration, fixed wheel orientation/no rolling contact;
projected rod overlaps intentionally visible, not a collision simulation.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from inversion_search import curve,R

APP=Path(__file__).resolve().parents[1]
BG='#f5f8fa';INK='#153247';TEAL='#087e76';GOLD='#bc7b2b';RED='#b74e59';BLUE='#416fa8'


def font(size,bold=False):
    for p in [Path('C:/Windows/Fonts')/('arialbd.ttf' if bold else 'arial.ttf'),
              Path('/usr/share/fonts/truetype/dejavu')/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')]:
        if p.exists():return ImageFont.truetype(str(p),size)
    return ImageFont.load_default(size=size)


def frame(case,q,index=0):
    p=case['config'];a,b,r=p['L2'],p['L3'],p['qab']
    im=Image.new('RGB',(800,640),BG);d=ImageDraw.Draw(im)
    d.text((28,18),f"Unequal links {a:g} / {b:g} mm | guide {r:g}",font=font(23,True),fill=INK)
    d.text((28,51),f"alpha = phase = 0 | q = {q:.1f} deg | normal 325 / useful 285 mm",font=font(15),fill=INK)
    full=case['full']['samples'];xs=[s['x_mm'] for s in full];zs=[s['z_mm'] for s in full]
    xmin,xmax=min(xs)-220,max(a,60*r)+35;zmin,zmax=min(zs)-220,max(zs)+220
    scale=min(700/(xmax-xmin),440/(zmax-zmin))
    xc,zc=(xmin+xmax)/2,(zmin+zmax)/2
    tr=lambda x,z:(400+(x-xc)*scale,325-(z-zc)*scale)
    def disk(x,z,radius,outline,fill=None,width=2):
        cx,cy=tr(x,z);rr=radius*scale;d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=outline,fill=fill,width=width)
    d.line((tr(xmin,0),tr(xmax,0)),fill='#d5dee5',width=1)
    d.line([tr(s['x_mm'],s['z_mm']) for s in full],fill='#a8bbc7',width=2)
    normal=case['normal']['samples'];d.line([tr(s['x_mm'],s['z_mm']) for s in normal],fill=TEAL,width=4)
    x,z=curve(q*R,a,b,r)[:2];bx,bz=a*math.cos(q*R-math.pi),a*math.sin(q*R-math.pi)
    disk(float(x),float(z),200,TEAL,'#dceee9',3)
    for angle in range(0,360,60):
        d.line((tr(float(x),float(z)),tr(float(x)+190*math.cos(angle*R),float(z)+190*math.sin(angle*R))),fill='#aac9c3',width=1)
    # Separate colours reveal the projected overlap, which requires axial packaging.
    d.line((tr(bx,bz),tr(float(x),float(z))),fill=GOLD,width=10)
    d.line((tr(0,0),tr(bx,bz)),fill=BLUE,width=5)
    disk(0,0,60*r,'#80679b',None,2);disk(bx,bz,60,'#80679b',None,2)
    for name,(px,pz) in [('A',(0,0)),('B',(bx,bz)),('C',(float(x),float(z)))]:
        cx,cy=tr(px,pz);d.ellipse((cx-4,cy-4,cx+4,cy+4),fill=INK)
        dx,dy={'A':(-19,-25),'B':(10,-20),'C':(-8,12)}[name]
        d.text((cx+dx,cy+dy),name,font=font(16,True),fill=INK)
    gap=case['projection']['wheel_to_hip_pitch_circle_gap_mm']
    d.text((28,551),f"Wheel R200 | projected hip pitch gap {gap:.1f} mm (overlap)",font=font(16,True),fill=RED)
    d.text((28,578),'Wheel and links overlap in projection: axial separation required.',font=font(15),fill=RED)
    d.text((28,603),'Ideal geometry only; wheel orientation held; no contact or rolling constraint.',font=font(14),fill=INK)
    if abs(q-180)<1e-8:d.text((28,93),'FOLD: rods overlap in side view',font=font(19,True),fill=RED)
    return im


def main():
    source=APP/'docs/unequal-inversion-results.json';data=json.loads(source.read_text())
    output=APP/'docs/unequal-animations';output.mkdir(exist_ok=True)
    rows=[]
    for name in data['recommended_ids']:
        c=next(c for c in data['selected'] if c['id']==name)
        qs=100+80*(1-np.cos(2*np.pi*np.arange(80)/80))
        palette=frame(c,100).quantize(colors=64)
        frames=[frame(c,float(q),i).quantize(palette=palette,dither=Image.Dither.NONE) for i,q in enumerate(qs)]
        target=output/f'{name}.gif'
        # GIF delays are integer centiseconds: alternate70/80 ms for exactly6 s.
        frames[0].save(target,save_all=True,append_images=frames[1:],duration=[70,80]*40,loop=0,optimize=True,disposal=1)
        if target.stat().st_size>1024*1024:raise ValueError('Curated GIF exceeds repository limit')
        rows.append(dict(id=name,file=target.name,frames=80,duration_ms=6000,width=800,height=640,
          config=c['config'],bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    manifest=dict(schema='camel/unequal-inversion-gifs/v1',cases=rows,
       scope='Analytical angular illustrations; not physical simulation; projected rod overlap remains explicit.',
       source_sha256={'docs/unequal-inversion-results.json':hashlib.sha256(source.read_bytes()).hexdigest(),
                      'scripts/build_unequal_visuals.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    (output/'manifest.json').write_bytes((json.dumps(manifest,separators=(',',':'))+'\n').encode())
    print(json.dumps(rows,indent=2))


if __name__=='__main__':main()
