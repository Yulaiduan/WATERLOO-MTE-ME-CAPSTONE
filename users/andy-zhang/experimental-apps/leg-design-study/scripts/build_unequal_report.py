"""Publish unequal-link inversion examples as offline HTML and vector PDF.

Run from app: .venv/Scripts/python.exe scripts/build_unequal_report.py
Inputs: retained unequal-inversion result/math/engine JSON; mm, deg, N, Nm.
Outputs: unequal-inversion.html and docs/unequal-inversion-report.pdf, using
ReportLab and shared local rendering helpers. No search/network/sim at render.
Limits: ideal height inverse and projected pitch-circle screening only;
overlapping rods still require axial packaging. No motor/hardware certification.
"""
from pathlib import Path
import html
import json
import math
import re
from reportlab.lib import colors
from build_design_report import Report,GRAY
from build_inversion_report import table,pdf_paths,PALETTE
from build_curved_report import get,label,lines,figure_svg

APP=Path(__file__).resolve().parents[1]


def mechanism(c):
    """Return a scale-correct static mechanism figure in SVG and PDF primitives."""
    p=c['config'];a,b,r=p['L2'],p['L3'],p['qab'];out=[]
    for i,q in enumerate([100,180,260]):
        t=math.radians(q-180);bx,bz=a*math.cos(t),a*math.sin(t)
        x=a*math.cos(t)-b*math.cos((r-1)*t);z=a*math.sin(t)+b*math.sin((r-1)*t)
        # Each panel uses the same isotropic scale and bounds.
        s=.155;tr=lambda x,z:(i*230+115+x*s,140-z*s)
        out.append(('text',i*230+115,23,f'q = {q} deg','#153247'))
        for px,pz,rr,col in [(x,z,200,'#087e76'),(0,0,60*r,'#80679b'),(bx,bz,60,'#80679b')]:
            cx,cy=tr(px,pz);out.append(('circle',cx,cy,rr*s,col))
        for (u,v),col,w in [(((bx,bz),(x,z)),'#bc7b2b',6),(((0,0),(bx,bz)),'#416fa8',3)]:
            out.append(('line',*tr(*u),*tr(*v),col,w))
        for name,pt in [('A',(0,0)),('B',(bx,bz)),('C',(x,z))]:
            xx,yy=tr(*pt);out.append(('text',xx+8,yy-7,name,'#153247'))
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 690 260" role="img" aria-label="Three equal-scale poses showing projected rod overlap at the fold">'
    for v in out:
        if v[0]=='text':svg+=f'<text x="{v[1]:.3f}" y="{v[2]:.3f}" fill="{v[4]}" font-size="12" text-anchor="middle">{v[3]}</text>'
        elif v[0]=='circle':svg+=f'<circle cx="{v[1]:.3f}" cy="{v[2]:.3f}" r="{v[3]:.3f}" fill="none" stroke="{v[4]}" stroke-width="1.5"/>'
        else:svg+=f'<line x1="{v[1]:.3f}" y1="{v[2]:.3f}" x2="{v[3]:.3f}" y2="{v[4]:.3f}" stroke="{v[5]}" stroke-width="{v[6]}"/>'
    return svg+'</svg>',out


def sections(d,e,v):
    picks=[get(d,k) for k in d['recommended_ids']];rows=[]
    p=lambda s:dict(kind='p',text=s)
    t=lambda h,r,w,**kw:dict(kind='table',headers=h,rows=r,widths=w,**kw)
    f=lambda title,ls,x,y,**kw:dict(kind='figure',title=title,lines=ls,xlabel=x,ylabel=y,**kw)
    def sec(id,title,sub,blocks):rows.append(dict(id=id,title=title,subtitle=sub,blocks=blocks))
    sec('options','Unequal links that invert','Original alpha=0 and assembly phase=0; wheel radius 200 mm.',[
        p('A shorter upper link and longer lower link can keep the wheel away from the hip while the '
          'height coordinate remains invertible through the fold. These four rounded study examples '
          'provide <b>325 mm total vertical travel, including 20+20 mm assumed reserves: 285 mm useful.</b>'),
        t(['Upper /lower mm','Guide r','Sideways mm','Hip peak Nm','Hip pitch gap mm'],[
            [f"{c['config']['L2']:g} /{c['config']['L3']:g}",f"{c['config']['qab']:g}",
             f"{c['normal']['signed_drift_mm']:.2f}",f"{c['force']['peak_45kg_hip_Nm']:.2f}",
             f"{c['projection']['wheel_to_hip_pitch_circle_gap_mm']:.1f}"] for c in picks],
          [115,68,102,101,113],id='shortlist',rowheight=29),
        f('Normal paths aligned at their start; axes use equal physical scales',lines(picks,relative=True),
          'Sideways movement from start (mm)','Vertical movement from start (mm)',equal=True,height=235),
        p('<b>Start with 160/475 mm, r 1.42 for about 50 mm sideways travel.</b> The 160/480 mm, r 1.35 '
          'alternative gives about75 mm and lower vertical-load torque. All four pass the assumed '
          'wheel/thin-upper-link and wheel/guide-pitch-circle screens. Rod overlap, actual pulley '
          'outer size and chassis interference still prevent a claim of physically proven inversion.')])
    sec('inversion','Through the fold and back','Full ideal q=100-260 deg; the 325 mm normal stroke occupies only part of this envelope.',[
        f('Full wheel-centre paths in hip coordinates; equal axis scales',lines(picks,'full'),
          'Global C_y (mm)','Global C_z (mm)',equal=True,height=245),
        t(['Upper /lower mm','Full height mm','Min Jz mm/rad','Useful hip ROM deg'],[
            [f"{c['config']['L2']:g} /{c['config']['L3']:g}",f"{c['full']['vertical_mm']:.1f}",
             f"{c['full']['min_Jz_mm_rad']:.2f}",f"{c['force']['hip_ROM_deg']:.2f}"] for c in picks],
          [135,117,122,125],rowheight=29),
        p('Jz stays positive across the entire 100-260 degree envelope, so each height has one q '
          'and an unambiguous branch through 180 degrees. Fold tangent is vertical. Symmetry gives '
          'x(-t)=x(t), z(-t)=-z(t): full endpoint sideways drift is zero, although the path bows sideways.'),
        p('The offline HTML includes four labelled six-second GIFs. Each sweeps 100 to260 degrees '
          'and back, shows actual wheel radius and guide pitch circles, and explicitly marks the '
          'overlapping fold. They illustrate equations; they do not simulate collision or rolling.'),
        dict(kind='gallery',cases=picks)])
    sec('clearance','Why the longer lower link helps','Pitch circles improve the screen; they do not establish outer pulley or chassis clearance.',[
        p('Let a=L2, b=L3, r=ra/rb, t=q-pi and k=r-1. Jonathan conventions give '
          '<font name="Courier">x=a cos(t)-b cos(kt); z=a sin(t)+b sin(kt)</font>. '
          'Exactly, <b>|C|²=a²+b²-2ab cos(rt)</b>, hence minimum wheel-centre/hip distance is |a-b|.'),
        p('For b>=a the wheel-centre distance to the thin upper segment AB is always at least b-a, '
          'with equality at the fold. First screen: b-a>=220 mm (R200 plus 20 assumed gap). '
          'With rb 60, the stronger wheel/hip pitch-circle screen is <b>b-a>=220+60r</b>. '
          'Also require b>=280 for wheel/knee pitch-circle separation and a-60(r+1)>=10 for '
          'an assumed 10 mm guide pitch-centre surplus.'),
        dict(kind='mechanism',title='160/475 mm, r 1.42: wheel and pitch circles; blue upper /orange lower',case=picks[1],height=188),
        t(['Case','Thin upper gap mm','Hip pitch gap mm','Interpretation'],[
            ['160 /475, r 1.42','115.0','29.8','Pass assumed 20 mm screens'],
            ['150 /375, r1.45','25.0','-62.0','Wheel overlaps hip pitch circle'],
            ['400 /175, r1.50','-200.0','-65.0','Upper-long wheel overlaps upper rod']],
          [112,114,112,161],rowheight=33),
        p('<b>All rods overlap in side view at the fold.</b> For b>a, C lies on the opposite side of A '
          'from B and the lower link passes through the hip. Axial staggering, forked links or '
          'offset hardware is necessary. The quoted gaps exclude flange/shaft/belt/chassis sizes, '
          'rod thickness, tire deformation and tolerances; no candidate is certified collision-free.')])
    sec('force','Force and control tradeoffs','Pure vertical equivalent corner load 110.3625 N =45 kg  x 9.81/4; no spring or moving-link inertia.',[
        f('Individual direct-hip holding torque curves through 285 mm useful travel',
          lines(picks,'force','height_mm','torque_45kg_Nm'),'Useful vertical travel (mm)','Direct hip holding torque (Nm)',height=220),
        t(['Upper /lower mm','Peak /RMS Nm','Hip speed rad/s','Side-load peak Nm'],[
            [f"{c['config']['L2']:g} /{c['config']['L3']:g}",
             f"{c['force']['peak_45kg_hip_Nm']:.2f} /{c['force']['rms_45kg_hip_uniform_height_Nm']:.2f}",
             f"{c['force']['constant_vertical_speed_0p25m_s_peak_hip_rad_s']:.3f}",
             f"{c['force']['robust_abs_Fx_over_Fz_0p3_peak_Nm']:.2f}"] for c in picks],
          [135,117,122,125],rowheight=29),
        p('Holding torque magnitude is Fz Jz for the plotted upward-load case; reducing its maximum improves worst force per hip Nm, but a smaller '
          'Jacobian needs more joint speed. Speed assumes constant vertical 0.25 m/s. Side-load '
          'column is the worst either-sign |Fx/Fz|<=0.3 envelope, an assumed sensitivity. '
          'For total supported loads of 3g and 4g, multiply the static load term by 3 and 4 respectively. This is not an impact prediction.'),
        p('Relative-knee torque is <b>-tau_hip/r</b>; relative-knee speed is <b>-r times hip speed</b>. '
          'One-half applies only to r2. Motor gearing is another mapping. Height-RMS equals '
          'time-weighted torque RMS for constant vertical speed without dwell. Motor heating '
          'still needs shaft/gearing, losses and real duty.'),
        p('Ideal useful lift work is 31.453 J per leg in every case. Lower torque is therefore '
          'mechanical advantage, not improved energy efficiency. Permitted lateral travel also '
          'does not establish compliance: local C=J J^T/K_eff needs actual spring/controller and '
          'geometric stiffness, contact and rolling conditions. No new motor or spring is selected.')])
    compare=[get(d,k) for k in ['w50_pitch_circle_force','clear50','w100_pitch_circle_short','w100_pitch_circle_force']]
    rom=lines([picks[1],picks[3]],'normal','q_deg','z_mm')
    for l,c in zip(rom,[picks[1],picks[3]]):l['y']=[y-c['normal']['samples'][0]['z_mm'] for y in l['y']]
    sec('search','Search priorities and useful ROM','11,535,210 bounded geometry/window combinations; no weighted score or R² method.',[
        p('L2=130-350 and L3=150-650 mm in 5 mm steps; guide 1.2-2.6 in 0.005 steps plus exact 5/3; '
          'q start 100-140 in 5 deg steps. End angle solves 325 mm height and must be<=175. '
          'Full 100-260 must have Jz>=5 mm/rad. Unequal means |L2-L3|>=10 mm. '
          'Normal sideways excursion must be 25/50/75/100 +/-2.5 mm without sideways reversal.'),
        p('Hard constraints first; geometry-only, thin-segment 220 and hip-pitch-circle families '
          'remain separate. Within each, rank minimum useful peak Jz and minimum link sum '
          'separately. Coarse 33 poses retain eight candidates per bucket; finalists get continuous '
          'derivative-extrema checks and 2001-pose force integrals. Finite grid/pool retention '
          'cannot prove a global or manufacturing optimum.'),
        t(['Comparison','L2 /L3, r','Hip peak Nm','Hip pitch gap mm'],[
            [name,f"{c['config']['L2']:g} /{c['config']['L3']:g}, {c['config']['qab']:g}",
             f"{c['force']['peak_45kg_hip_Nm']:.2f}",f"{c['projection']['wheel_to_hip_pitch_circle_gap_mm']:.1f}"]
            for name,c in zip(['50 mm grid force leader','50 mm rounded example','100 mm grid size leader','100 mm grid force leader'],compare)],
          [145,135,102,117],rowheight=31),
        f('Height reserves trim different angular windows',rom,'Hip angle q (degrees)','Height from normal start (mm)',height=173),
        p('Useful ROM uses exact height roots qlow=z^-1(zstart+20), qhigh=z^-1(zend-20), '
          'rather than subtracting fixed degrees. For 160/475,r 1.42, totalq=100-164.692 deg; '
          'useful ROM 55.806 deg. Rounded examples trade a little peak torque for larger '
          'assumed pitch-circle gaps. Starting angles and all margins are study assumptions.')])
    sec('evidence','Checks and next design decision','Numerical agreement supports the equations; physical inversion still needs a packaged design.',[
        p(f'<b>22 numerical tests pass</b>, including six new unequal-link tests. '
          f'{v["scalar_comparisons"]:,} scalar comparisons across 22 cases agree with original '
          f'Jonathan V2 and Andy 2D statics, maximum error {v["max_error_mm_Nm"]:.3e} mm/Nm. '
          'The first test run misclassified diagnostic wide_reverse as a grid ID; the harness '
          'classifier was fixed and all 22 tests rerun. Numerical acceptance criteria were unchanged.'),
        t(['Actual Pymunk case','2 ms mm','1 ms mm','0.5 ms mm','0.25 ms mm'],[
            [c['id'],*[f'{a["max_path_error_mm"]:.5f}' for a in c['refinement']]] for c in e['cases']],
          [119,95,95,95,95],rowheight=30),
        p('All three fixtures pass path/pin/guide/tracking tolerances at all four timesteps and '
          'converge. Real motor, pivot and gear constraints move positive-mass bodies; only the '
          'initial pose is assigned. Zero gravity/forces and no collision shapes make this a '
          'geometry test. It does not validate loaded torque, ground contact, impacts or packaging.'),
        p('<b>Recommended next CAD seed: 160/475 mm, guide1.42.</b> It provides 50.165 mm normal '
          'sideways travel, 38.552 Nm equivalent 45 kg hip peak and 29.8 mm minimum wheel-to-hip '
          'pitch-circle gap. Use 160/480,r 1.35 if 74.451 mm sideways travel is desirable: 35.633 Nm '
          'peak and 39 mm pitch gap. Both require an explicit axial layout at the fold.'),
        p('Next measure pulley outer radii, rod/fork thickness, axial stack, chassis envelope '
          'and actual contact conditions. Then size springs/motors using that geometry and '
          'measured mass/inertia/duty. Prior spring cases remain separate. Historical dual-rope '
          'stays <b>IMPOSSIBLE /rejected</b>; no Motion Lab controls or services change.'),
        p('Rebuild using unequal_inversion_search.py, test_unequal_inversion, '
          'scripts/verify_unequal_geometry.py, scripts/verify_unequal_report.cjs --math-only, '
          'scripts/build_unequal_visuals.py and scripts/build_unequal_report.py. Then run the '
          'full browser verifier. Adjacent design record retains commands, source hashes and '
          'decisions. Source base 1a3fb7e; workspace scope; canonical physics NOT APPLICABLE.')])
    return rows


class UnequalReport(Report):
    def section(self,*args):
        super().section(*args)
        self.c.setFillColor(colors.white);self.c.rect(46,24,450,21,fill=1,stroke=0)
        self.text(48,37,'2026-10-14 | Unequal-link inversion | Source 1a3fb7e | Experimental',7,GRAY)


def build_pdf(d,ss):
    target=APP/'docs/unequal-inversion-report.pdf';r=UnequalReport(target,d)
    r.c.setTitle('CAMEL | Unequal-link invertible curved paths')
    for i,s in enumerate(ss):
        r.section(f'{i+1:02} / UNEQUAL LINK STUDY',s['title'],s['subtitle']);y=665
        for b in s['blocks']:
            if b['kind']=='gallery':continue
            if b['kind']=='p':y=r.text(48,y,b['text'],9)-11
            elif b['kind']=='table':y=r.table(48,y,b['widths'],b['headers'],b['rows'],7.5,b.get('rowheight',29))-15
            elif b['kind']=='mechanism':
                y-=15;r.text(48,y+14,b['title'],8.1,GRAY);y-=10
                _,items=mechanism(b['case']);scale=499/690
                for v in items:
                    r.c.setStrokeColor(colors.HexColor(v[-1] if v[0]!='line' else v[-2]))
                    if v[0]=='text':r.text(48+v[1]*scale-13,y-v[2]*scale+6,v[3],7,width=100)
                    elif v[0]=='circle':r.c.setLineWidth(1);r.c.circle(48+v[1]*scale,y-v[2]*scale,v[3]*scale,stroke=1,fill=0)
                    else:r.c.setLineWidth(v[-1]*scale);r.c.line(48+v[1]*scale,y-v[2]*scale,48+v[3]*scale,y-v[4]*scale)
                y-=b['height']+12
            else:
                y-=15;r.text(48,y+14,b['title'],8.1,GRAY);y-=15;h=b['height']
                if b.get('equal'):pdf_paths(r,b['lines'],y=y,h=h)
                else:r.chart(48,y,499,h,b['lines'],b['xlabel'],b['ylabel'])
                y-=h+15
        if y<49:raise ValueError(f'Page{i+1} ends at{y:.1f}; repair layout')
    r.c.save();return target


def build_html(d,ss):
    css=re.search(r'<style>([\s\S]*?)</style>',(APP/'inversion-paths.html').read_text(encoding='utf-8')).group(1)
    css+='td,th{overflow-wrap:anywhere}svg,img{height:auto;max-width:100%}.gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.gallery figure{margin:0}.report section{scroll-margin-top:70px}@media(max-width:750px){.gallery{grid-template-columns:1fr}}@media print{.gallery{display:none}}'
    bodies=[]
    for i,s in enumerate(ss):
        bs=[]
        for b in s['blocks']:
            if b['kind']=='p':bs.append('<p>'+re.sub(r'</?font[^>]*>','',b['text'])+'</p>')
            elif b['kind']=='table':bs.append(table(b['headers'],b['rows'],b.get('id','')))
            elif b['kind']=='gallery':
                bs.append('<div class="gallery">'+''.join(f'<figure><figcaption>{html.escape(label(c))}</figcaption><img src="docs/unequal-animations/{c["id"]}.gif" width="800" height="640" alt="Labelled {html.escape(label(c))} full inversion with projected fold overlap"></figure>' for c in b['cases'])+'</div>')
            elif b['kind']=='mechanism':bs.append('<figure><figcaption>'+b['title']+'</figcaption>'+mechanism(b['case'])[0]+'</figure>')
            else:bs.append('<figure><figcaption>'+html.escape(b['title'])+'</figcaption>'+figure_svg(b)+'</figure>')
        bodies.append(f'<section id="{s["id"]}"><p class="eyebrow">{i+1:02} / UNEQUAL LINK STUDY</p><h2>{s["title"]}</h2><p class="lead">{s["subtitle"]}</p>'+''.join(bs)+'</section>')
    toc=''.join(f'<a href="#{s["id"]}">{i+1:02} {s["title"]}</a>' for i,s in enumerate(ss))
    payload=json.dumps(d,separators=(',',':'),ensure_ascii=False).replace('<','\\u003c')
    out='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    out+='<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src file: data:; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'"><title>CAMEL · Unequal links through inversion</title><style>'+css+'</style></head><body>'
    out+='<header class="top"><div class="brand">CAMEL <small>Unequal-link report / October 2026</small></div><div class="top-actions"><a id="pdf-link" href="docs/unequal-inversion-report.pdf">PDF report ↗</a><button class="print-button" id="print-report">Print report</button></div></header>'
    out+='<div class="hero"><div><p class="eyebrow">ALPHA ZERO · CURVED PATHS · FULL IDEAL INVERSION</p><h1>Unequal links.<br>Room around the hip.</h1><p>Four labelled examples, with full-path animations and explicit force, control and packaging screens.</p></div><div class="hero-box"><b>Offline design report</b><span>325 mm total /285 mm useful</span><span>11,535,210 windows searched</span></div></div>'
    out+='<main class="reader"><nav class="toc">'+toc+'<small>Static offline evidence.<br>No server or network needed.</small></nav><article class="report">'+''.join(bodies)
    out+='<div class="links"><a href="docs/unequal-inversion-study.md">Detailed design record</a><a href="docs/unequal-inversion-results.json">Numerical evidence</a><a href="docs/unequal-animations/manifest.json">GIF manifest</a><a href="docs/revisions.md">Revision map</a><a href="curved-paths.html">Earlier curved paths</a></div></article></main>'
    out+='<footer class="footer">Ideal height inversion · projected pitch-circle screens · axial packaging unresolved · historical IMPOSSIBLE decisions retained</footer><script type="application/json" id="report-evidence">'+payload+'</script><script>document.getElementById("print-report").addEventListener("click",()=>window.print());</script></body></html>'
    (APP/'unequal-inversion.html').write_bytes(out.encode())


def main():
    d,e,v=[json.loads((APP/'docs'/f'unequal-inversion-{name}.json').read_text()) for name in ['results','engine-checks','math-checks']]
    assert e['all_passed'] and v['passed'];ss=sections(d,e,v);pdf=build_pdf(d,ss);build_html(d,ss)
    from pypdf import PdfReader
    print(json.dumps(dict(pages=len(PdfReader(pdf).pages),pdf_bytes=pdf.stat().st_size,html_bytes=(APP/'unequal-inversion.html').stat().st_size)))


if __name__=='__main__':main()
