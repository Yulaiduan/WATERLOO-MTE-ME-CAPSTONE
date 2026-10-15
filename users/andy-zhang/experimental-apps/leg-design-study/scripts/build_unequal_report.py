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
            xx,yy=tr(*pt);out.append(('text',xx+({'A':-9,'B':12,'C':-8}[name]),yy+({'A':-12,'B':-12,'C':20}[name]),name,'#153247'))
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
    sec('options','Upper-long links within 1.25x','Owner correction: longer /shorter <=1.25; alpha=phase=0; wheel R200 mm.',[
        p('Yes, the upper link can be longer. These four rounded examples obey the new length '
          'constraint and provide <b>325 mm total vertical travel, including assumed 20+20 mm '
          'reserves: 285 mm useful.</b> Their ideal height maps stay invertible through the fold. '
          'The earlier 160/475 mm proposal is outside this constraint and is superseded.'),
        t(['Upper /lower mm','Length ratio','Guide r','Sideways mm','Hip peak Nm'],[
            [f"{c['config']['L2']:g} /{c['config']['L3']:g}",f"{c['projection']['length_ratio']:.3f}",
             f"{c['config']['qab']:g}",f"{c['normal']['signed_drift_mm']:.2f}",
             f"{c['force']['peak_45kg_hip_Nm']:.2f}"] for c in picks],
          [121,91,83,102,102],id='shortlist',rowheight=30),
        f('Normal paths aligned at their start; equal physical axis scales',lines(picks,relative=True),
          'Sideways movement from start (mm)','Vertical movement from start (mm)',equal=True,height=232),
        p('<b>Balanced study seed: 200/175 mm, guide 15:8 (1.875).</b> This gives 49.77 mm sideways '
          'movement with a 1.143 length ratio. The 205/185 mm, 7:4 alternative gives 76.31 mm '
          'and slightly lower static torque. All require axial wheel/link separation at the fold; '
          'none is a collision-free coplanar mechanism.')])
    sec('inversion','Curved paths through the fold','Full ideal q=100-260 deg; the 325 mm normal stroke is only part of this envelope.',[
        f('Full wheel-centre paths in hip coordinates; equal physical scales',lines(picks,'full'),
          'Global C_y (mm)','Global C_z (mm)',equal=True,height=240),
        t(['Upper /lower mm','Full height mm','Min Jz mm/rad','Useful hip ROM deg'],[
            [f"{c['config']['L2']:g} /{c['config']['L3']:g}",f"{c['full']['vertical_mm']:.1f}",
             f"{c['full']['min_Jz_mm_rad']:.2f}",f"{c['force']['hip_ROM_deg']:.2f}"] for c in picks],
          [135,117,122,125],rowheight=29),
        p('With a=L2,b=L3,t=q-pi,k=r-1: '
          '<font name="Courier">x=a cos(t)-b cos(kt); z=a sin(t)+b sin(kt)</font>. '
          'Jz is positive over the full envelope, so each height has one q through 180 degrees. '
          'The fold tangent is vertical; full endpoint sideways drift is zero by symmetry, '
          'despite nonzero lateral excursion.'),
        p('<b>At r=2 with unequal links, x=(a-b)cos(t), z=(a+b)sin(t): an ellipse.</b> '
          'A 2:1 guide therefore remains a useful curved-path option. It becomes a vertical '
          'line only when a=b. Four labelled six-second offline GIFs below show actual wheel '
          'radius and the projected overlaps; they do not simulate rolling or collision.'),
        dict(kind='gallery',cases=picks)])
    sec('clearance','Axial separation is necessary','Near-equal upper-long paths invert ideally; projected wheel and rod interference remains.',[
        p('At the fold, B=(a,0), C=(a-b,0). For a>b, <b>0&lt;a-b&lt;a</b>, so the wheel centre '
          'lies <b>inside the upper segment AB</b>. Its projected distance to that segment '
          'is zero at any scale. A flat coplanar wheel/upper-link layout cannot pass through '
          'this fold, even if hip-centre clearance alone looks acceptable.'),
        dict(kind='mechanism',title='200/175 mm, guide 15:8: wheel and guide pitch circles; blue upper /orange lower',case=picks[1],height=188),
        t(['Upper /lower mm','Fold hip distance mm','Wheel /upper gap mm','Guide pitch surplus mm'],[
            [f"{c['config']['L2']:g} /{c['config']['L3']:g}",f"{c['projection']['wheel_hip_min_mm']:.1f}",
             f"{c['projection']['wheel_rim_to_upper_segment_min_mm']:.1f}",
             f"{c['projection']['guide_pitch_surplus_mm']:.1f}"] for c in picks],
          [121,126,126,126],rowheight=29),
        p('A negative wheel/upper gap means projected overlap. All rows pass the assumed '
          '10 mm guide pitch-centre surplus a-60(r+1), with rb 60 and ra=60r; that guide '
          'check does not establish wheel, flange, shaft, belt or chassis clearance.'),
        p('For a lower-long alternative, minimum wheel/hip and wheel/thin-upper-segment '
          'distance is b-a. Under the 1.25x limit, merely reaching 220 mm requires shorter '
          'link>=880 mm and longer>=1100 mm. Adding hip pitch radius requires still more. '
          'That is outside this compact 150-400 mm search. No searched candidate passes '
          'the full coplanar wheel clearance screen.'),
        p('<b>Proposed packaging direction:</b> place wheel and links in separate axial '
          'planes, using an appropriate fork/offset/shaft arrangement. Rods also overlap in '
          'projection at the fold. Actual axial stack, tire width, chassis and outer hardware '
          'must be measured in CAD; physical full inversion remains unvalidated.')])
    sec('force','Force and control tradeoffs','Pure vertical equivalent corner load 110.3625 N =45 kg x9.81/4; no spring or moving-link inertia.',[
        f('Individual direct-hip holding torque magnitudes over 285 mm useful travel',
          lines(picks,'force','height_mm','torque_45kg_Nm'),'Useful vertical travel (mm)','Direct hip holding magnitude (Nm)',height=215),
        t(['Upper /lower mm','Peak /RMS Nm','Hip speed rad/s','Side-load peak Nm'],[
            [f"{c['config']['L2']:g} /{c['config']['L3']:g}",
             f"{c['force']['peak_45kg_hip_Nm']:.2f} /{c['force']['rms_45kg_hip_uniform_height_Nm']:.2f}",
             f"{c['force']['constant_vertical_speed_0p25m_s_peak_hip_rad_s']:.3f}",
             f"{c['force']['robust_abs_Fx_over_Fz_0p3_peak_Nm']:.2f}"] for c in picks],
          [135,117,122,125],rowheight=29),
        p('Holding magnitude is Fz Jz for the upward-load case; the signed balancing '
          'hip torque is -Fz Jz. Reducing maximum Jz improves worst vertical force per hip '
          'Nm. A smaller Jz at a given pose needs greater joint speed for the same vertical '
          'speed; peak speed depends on minimum Jz. Speed assumes constant vertical 0.25 m/s; '
          'side-load peak is a both-sign |Fx/Fz|<=0.3 assumed sensitivity.'),
        p('Relative-knee torque is <b>-tau_hip/r</b>; relative-knee speed is '
          '<b>-r times hip speed</b>. Half-torque applies only at r2. Motor gearing is '
          'another mapping. Height-RMS equals time-weighted torque RMS at constant vertical '
          'speed without dwell; heating still needs motor/gear losses and actual duty.'),
        p('Ideal useful lift work remains 31.453 J per leg in every case. Lower torque is '
          'mechanical advantage, not free energy. Total supported loads 3g and 4g multiply '
          'the static load term by 3 and 4; they do not predict impacts. Permitted sideways '
          'movement is not measured compliance: stiffness, contact, rolling and inertia '
          'are unresolved. No new spring or motor rating is selected.')])
    rom=lines([picks[1],picks[3]],'normal','q_deg','z_mm')
    for l,c in zip(rom,[picks[1],picks[3]]):l['y']=[y-c['normal']['samples'][0]['z_mm'] for y in l['y']]
    compare=[get(d,k) for k in ['w50_upper_long_force','upper50','w50_upper_long_short','w50_lower_long_force']]
    sec('search','Hard length limit, separate objectives',f"{d['search']['counts']['enumerated']:,} bounded geometry/window combinations; no weighted score or R2 method.",[
        p('L2 and L3=150-400 mm in 5 mm steps; max/min<=1.25 and |L2-L3|>=5 mm. '
          'Guide 1.2-2.6 in 0.005 steps plus exact 5/3. Normal q start 100-140 in 5 degree '
          'steps; end solves 325 mm height and must be<=175. Full 100-260 requires '
          'Jz>=5 mm/rad. Sideways excursion 25/50/75/100 +/-2.5 mm, without reversal.'),
        p('Upper-long and lower-long families are ranked separately. Hard constraints '
          'come first; minimize useful peak Jz and total link sum as separate objectives. '
          'Coarse 33 poses retain eight candidates per bucket; finalists get continuous '
          'derivative-extrema checks and 2001-pose integrals. Finite grid and retained pool '
          'do not prove a global or manufacturing optimum.'),
        t(['50 mm comparison','Upper /lower, r','Hip peak Nm','Length ratio'],[
            [name,f"{c['config']['L2']:g}/{c['config']['L3']:g}, {c['config']['qab']:g}",
             f"{c['force']['peak_45kg_hip_Nm']:.2f}",f"{c['projection']['length_ratio']:.3f}"]
            for name,c in zip(['Upper-long force leader','Rounded 15:8 example','Upper-long size leader','Lower-long force leader'],compare)],
          [151,143,103,102],rowheight=30),
        f('Height reserves trim the angular control window',rom,'Hip angle q (degrees)','Height from normal start (mm)',height=173),
        p(f"Useful ROM uses height roots z^-1(zstart+20) and z^-1(zend-20). For 200/175,15:8, "
          f"total q=100-{picks[1]['config']['tc']:.3f} deg; useful hip ROM "
          f"{picks[1]['force']['hip_ROM_deg']:.3f} deg. Do not subtract 20 degrees for 20 mm. "
          'Rounded ratios balance readable parameters, compactness and lateral target; '
          'their somewhat higher torque than the grid force leaders is reported explicitly.')])
    sec('evidence','Checks and next design decision','Ideal inverse verified; collision-free axial packaging and loaded dynamics remain open.',[
        p(f"<b>23 numerical tests pass</b>, including seven unequal-link tests. "
          f"{v['scalar_comparisons']:,} original Jonathan V2/Andy 2D scalar comparisons across "
          f"{v['selected_cases']} cases agree, maximum {v['max_error_mm_Nm']:.3e} mm/Nm. "
          'The 1.25x constraint and upper-long fold overlap have explicit regression checks. '
          'Independent read-only review confirms the four rounded examples and ellipse relation.'),
        t(['Actual Pymunk case','2 ms mm','1 ms mm','0.5 ms mm','0.25 ms mm'],[
            [c['id'],*[f'{a["max_path_error_mm"]:.5f}' for a in c['refinement']]] for c in e['cases']],
          [119,95,95,95,95],rowheight=30),
        p('Actual positive-mass motor/pivot/gear constraints generate the three angular sweeps; '
          'only initial poses are assigned. The compact evidence retains every timestep and '
          'unchanged tolerance result, including coarse failures if present. Zero gravity/forces '
          'and no collision shapes mean geometry evidence, not validated loaded torque, '
          'contact, compliance, impact or physical inversion.'),
        p('<b>Start CAD with 200/175 mm, guide 15:8</b> for approximately 50 mm sideways movement, '
          'or 205/185 mm, 7:4 for about 75 mm. Both fit the required length relation. Their '
          'normal strokes approach the assumed 175 degree guard; inspect actual stop and '
          'buffer tolerances rather than treating these limits as measured hardware.'),
        p('The earlier broad search recommended 160/475 mm before the owner clarified the '
          '1.25x limit. That recommendation is superseded; its historical evidence remains '
          'in the preceding local revision and contribution log. This report now applies '
          'the constraint to every retained case. Existing Motion Lab models, earlier '
          'reports/spring cases and historical dual-rope <b>IMPOSSIBLE /rejected</b> stay intact.'),
        p('Reproduction commands, source hashes, exact assumptions and validation history are '
          'in docs/unequal-inversion-study.md and docs/validation.md. The manual launcher '
          'opens this static file with adjacent GIFs; no server or new Motion Lab control '
          'is needed. Source base aaed324; workspace scope; canonical physics NOT APPLICABLE.')])
    return rows


class UnequalReport(Report):
    def section(self,*args):
        super().section(*args)
        self.c.setFillColor(colors.white);self.c.rect(46,24,450,21,fill=1,stroke=0)
        self.text(48,37,'2026-10-15 | Unequal-link inversion | Source aaed324 | Experimental',7,GRAY)


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
    out+='<div class="hero"><div><p class="eyebrow">ALPHA ZERO · CURVED PATHS · FULL IDEAL INVERSION</p><h1>Upper link longer.<br>Within 1.25x.</h1><p>Four upper-long examples within the required length limit, with full inversion animations and explicit packaging limits.</p></div><div class="hero-box"><b>Offline design report</b><span>325 mm total /285 mm useful</span><span>6,601,338 windows searched</span></div></div>'
    out+='<main class="reader"><nav class="toc">'+toc+'<small>Static offline evidence.<br>No server or network needed.</small></nav><article class="report">'+''.join(bodies)
    out+='<div class="links"><a href="docs/unequal-inversion-study.md">Detailed design record</a><a href="docs/unequal-inversion-results.json">Numerical evidence</a><a href="docs/unequal-animations/manifest.json">GIF manifest</a><a href="docs/revisions.md">Revision map</a><a href="curved-paths.html">Earlier curved paths</a></div></article></main>'
    out+='<footer class="footer">Ideal height inversion · wheel/link axial separation needed · axial packaging unresolved · historical IMPOSSIBLE decisions retained</footer><script type="application/json" id="report-evidence">'+payload+'</script><script>document.getElementById("print-report").addEventListener("click",()=>window.print());</script></body></html>'
    (APP/'unequal-inversion.html').write_bytes(out.encode())


def main():
    d,e,v=[json.loads((APP/'docs'/f'unequal-inversion-{name}.json').read_text()) for name in ['results','engine-checks','math-checks']]
    assert e['all_passed'] and v['passed'];ss=sections(d,e,v);pdf=build_pdf(d,ss);build_html(d,ss)
    from pypdf import PdfReader
    print(json.dumps(dict(pages=len(PdfReader(pdf).pages),pdf_bytes=pdf.stat().st_size,html_bytes=(APP/'unequal-inversion.html').stat().st_size)))


if __name__=='__main__':main()
