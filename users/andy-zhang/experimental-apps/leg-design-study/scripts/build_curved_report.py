"""Render the ratio-generated curved-path study as static HTML and vector PDF.

Run from app: .venv/Scripts/python.exe scripts/build_curved_report.py
Inputs: retained curved-path results/math/engine JSON; mm/deg/N/Nm/rad units.
Outputs: curved-paths.html and docs/curved-path-report.pdf. Uses pinned
ReportLab and existing report helpers. No search, simulation or network during
rendering. Limits: kinematic lateral mobility, not actual stiffness, physical
inversion, selected springs/motors or canonical robot validation. No R2 ranking.
"""
from pathlib import Path
import html
import json
import math
import re
from reportlab.lib import colors
from build_design_report import Report, GRAY
from build_inversion_report import svg_chart as base_svg, table, pdf_paths, PALETTE

APP=Path(__file__).resolve().parents[1]


def get(d,key):return next(c for c in d['selected'] if c['id']==key)


def label(c):
    p=c['config'];return f"{p['L2']:g}/{p['L3']:g} mm, r {p['qab']:.4g}"


def lines(cases,side='normal',x='x_mm',y='z_mm',relative=False):
    output=[]
    for i,c in enumerate(cases):
        rows=c[side]['samples'];xs=[p[x] for p in rows];ys=[p[y] for p in rows]
        if relative:xs=[v-xs[0] for v in xs];ys=[v-ys[0] for v in ys]
        output.append(dict(x=xs,y=ys,label=label(c),color=colors.HexColor(PALETTE[i%5]),html_color=PALETTE[i%5]))
    return output


def figure_svg(block):
    out=base_svg(block['lines'],block['xlabel'],block['ylabel'],equal=block.get('equal',False),disk=block.get('disk',False))
    index=0
    def dash(m):
        nonlocal index
        tag=m.group(0)
        if block['lines'][index].get('dash'):tag=tag.replace('<polyline ','<polyline stroke-dasharray="5 4" ')
        index+=1;return tag
    return re.sub(r'<polyline\s[^>]*>',dash,out)


def content(d,e,v):
    picks=[get(d,f'example{n}') for n in [25,50,75,100]]
    clear=[get(d,f'w{n}_equal_normal220_force') for n in [25,50,75,100]]
    sections=[]
    p=lambda text:dict(kind='p',text=text)
    t=lambda headers,rows,**kw:dict(kind='table',headers=headers,rows=rows,**kw)
    f=lambda title,series,x,y,**kw:dict(kind='figure',title=title,lines=series,xlabel=x,ylabel=y,**kw)
    def sec(id,title,subtitle,blocks):sections.append(dict(id=id,title=title,subtitle=subtitle,blocks=blocks))
    sec('options','Curved paths from ratio changes',
        '325 mm total vertical travel, including two assumed 20 mm reserves; 285 mm useful.',[
        p('This study searches useful curved '
          'wheel-centre paths with 25, 50, 75 or 100 mm of sideways excursion. All leading examples '
          'retain <b>alpha=0 and original assembly phase phi0=0</b>. Changing the guide ratio produces '
          'the curve; no mounting tilt or indexing is introduced.'),
        t(['Target mm','Equal links mm','Guide ratio','Actual lateral mm','Hip peak Nm'],[
            [str(n),f"{c['config']['L2']:g}",f"{c['config']['qab']:g}",f"{c['normal']['lateral_excursion_mm']:.2f}",
             f"{c['force']['peak_45kg_hip_Nm']:.2f}"] for n,c in zip([25,50,75,100],picks)],id='shortlist',widths=[73,102,91,124,109]),
        f('Normal strokes aligned at their extended start; equal physical axis scales',lines(picks,relative=True),
          'Sideways movement from start (mm)','Vertical movement from start (mm)',equal=True,height=242),
        p('<b>Balanced geometric seed: 190/190 mm with guide 9:5.</b> It provides 49.98 mm lateral '
          'excursion and 325/285 mm total/useful height. These compact examples fail the assumed '
          'normal 220 mm coplanar wheel/hip exclusion. Larger clearance-filtered alternatives are '
          'shown separately; actual physical packaging remains unresolved.')])
    same=[get(d,k) for k in ['ratio300_1.5','ratio300_1.66667','ratio300_1.8','ratio300_2','ratio300_2.2']]
    sec('ratios','The ratio bends the path',
        'Same 300/300 mm links, same q start=100 degrees, same 325 mm vertical stroke.',[
        p('With t=q-pi and k=r-1, the original phase-zero model is '
          '<font name="Courier">x=L2 cos(t)-L3 cos(k t); z=L2 sin(t)+L3 sin(k t)</font>. '
          'Equal links at r=2 move vertically. Reducing r below 2 allows sideways motion as the leg '
          'compresses; increasing r above 2 bends the normal path the other way.'),
        f('Ratio sensitivity isolated from changes in link length',lines(same,relative=True),
          'Relative horizontal wheel-centre position (mm)','Relative vertical wheel-centre position (mm)',equal=True,height=250),
        t(['Guide r','Normal sideways mm','Useful hip ROM deg','45 kg hip peak Nm'],[
            [f"{c['config']['qab']:.4g}",f"{c['normal']['lateral_excursion_mm']:.2f}",
             f"{c['force']['hip_ROM_deg']:.2f}",f"{c['force']['peak_45kg_hip_Nm']:.2f}"] for c in same],
          widths=[84,143,135,137],rowheight=27),
        p('The guide ratio is ra/rb. With rb=60 mm, the four compact examples have ra=114/108/102/96 mm. '
          'These are pitch-radius relations, not selected pulley tooth counts, belt pitches or strength ratings. '
          'The 2:1 zero-excursion case is a baseline, not a curved-path winner.')])
    torques=lines(picks,'force','height_mm','torque_45kg_Nm')
    sec('force','Force, speed and sideways loading',
        'Pure vertical equivalent load: 45 kg robot /4 corners =110.3625 N per leg; massless moving links.',[
        f('Individual direct-hip holding torque curves over useful travel',torques,'Useful vertical height (mm)',
          'Unassisted direct hip holding torque (Nm)',height=238),
        t(['L mm /r','Peak /RMS Nm','Hip ROM deg','Speed rad/s','Side-load peak Nm'],[
            [f"{c['config']['L2']:g} /{c['config']['qab']:g}",
             f"{c['force']['peak_45kg_hip_Nm']:.2f} /{c['force']['rms_45kg_hip_uniform_height_Nm']:.2f}",
             f"{c['force']['hip_ROM_deg']:.2f}",f"{c['force']['constant_vertical_speed_0p25m_s_peak_hip_rad_s']:.3f}",
             f"{c['force']['robust_abs_Fx_over_Fz_0p3_peak_Nm']:.2f}"] for c in picks],
          widths=[88,108,97,95,111],rowheight=31),
        p('Speed assumes 0.25 m/s constant vertical movement. Side-load peak is a robust envelope '
          'for either sign of Fx with |Fx/Fz|<=0.3, an explicitly assumed sensitivity. '
          '<font name="Courier">|tau_hip|=|Fx Jx+Fz Jz|</font>. '
          'A curve changes both force projection and required joint speed; it does not provide free energy.'),
        p('For the relative knee coordinate, <b>tau_knee=-tau_hip/r</b> and '
          '<b>knee speed=-r hip speed</b>. The factor one-half applies only at r=2. Any motor gearbox '
          'is a separate mapping. Height-RMS corresponds to constant vertical speed; real thermal duty '
          'needs time weighting. Ideal useful lift work is 31.453 J per leg in every case. '
          '3/4g are held-load multiples, not impact predictions or motor ratings.')])
    slopes=[]
    for i,c in enumerate(picks):
        rows=c['force']['samples'];slopes.append(dict(x=[r['height_mm'] for r in rows],
            y=[r['Jx_m_rad']/r['Jz_m_rad'] for r in rows],label=label(c),
            color=colors.HexColor(PALETTE[i]),html_color=PALETTE[i]))
    sec('compliance','Allowed movement is not stiffness',
        'A single guided joint permits coupled horizontal and vertical motion along the local tangent.',[
        p('The slope Jx/Jz measures horizontal movement per unit vertical movement. Larger lateral '
          'excursion allows the wheel centre to move sideways as the leg compresses, but does not '
          'establish a softer suspension. A locked actuator can remain stiff despite a curved path.'),
        f('Horizontal-to-vertical movement ratio through each useful stroke',slopes,'Useful vertical height (mm)',
          'Local sideways /vertical motion Jx/Jz',height=245),
        p('<font name="Courier">J=[Jx,Jz] (metres/radian)<br/>'
          'C = J J^T / K_eff<br/>Cxx=Jx^2/K_eff; Cxz=Jx Jz/K_eff; Czz=Jz^2/K_eff</font>'),
        p('This local one-DOF compliance matrix applies only for a stable effective joint stiffness '
          'K_eff in Nm/rad, with the permitted coupled motion free to occur. It has rank one. '
          'K_eff must include spring/controller stiffness and load-dependent geometric stiffness. '
          'Without those inputs, an absolute horizontal stiffness or spring constant would be invented.'),
        p('If vertical motion is blocked by rigid contact or another constraint, the coupled sideways '
          'motion can also be blocked. Ground contact, traction, tire deformation and wheel rotation '
          'decide whether the path is helpful compliance, rolling movement or scrub. Existing wheel-spin '
          'cancellation is not a rolling constraint. At the phase-zero fold Jx=0, so the permitted '
          'sideways motion vanishes locally even though vertical inversion remains regular.')])
    full=lines(picks,'full')
    sec('inversion','Inversion and wheel packaging',
        'Full ideal envelope q=100-260 degrees; a 325 mm normal working stroke is only part of it.',[
        f('Full paths and the assumed 220 mm projected wheel-centre exclusion around hip A',full,
          'Global horizontal C_y (mm), equal scale','Global vertical C_z (mm)',equal=True,disk=True,height=254),
        t(['Target mm','Compact L mm','Normal hip distance mm','220-filter L mm','220-filter ratio'],[
            [str(n),f"{c['config']['L2']:g}",f"{c['normal']['min_hip_distance_mm']:.2f}",
             f"{cc['config']['L2']:g}",f"{cc['config']['qab']:g}"] for n,c,cc in zip([25,50,75,100],picks,clear)],
          widths=[76,89,135,104,95],rowheight=31),
        p('Strict phase-zero symmetry gives x(-t)=x(t), z(-t)=-z(t). The full path moves sideways '
          'toward the fold and returns on the other branch, so <b>full endpoint horizontal drift is '
          'zero despite a substantial lateral excursion</b>. Lateral excursion, signed drift and '
          'turning points are therefore reported separately.'),
        p('All compact examples pass the ideal height-inverse check through inversion, but every '
          'near-equal coplanar full sweep fails clearance: at the fold |C|=|L2-L3|. The larger '
          '280/285/295/300 mm alternatives clear the normal branch only. Measured axial wheel/chassis '
          'and belt geometry is still required. Historical dual-rope remains <b>IMPOSSIBLE /rejected</b>.')])
    c=picks[1];cc=clear[1]
    rom=lines([c,cc],'normal','q_deg','z_mm')
    for l,case in zip(rom,[c,cc]):l['y']=[v-case['normal']['z_bounds_mm'][0] for v in l['y']]
    sec('search','Search priorities and effective ROM',
        '2,953,002 windows enumerated; hard constraints first, separate force and size leaders.',[
        t(['Variable /filter','Policy'],[
            ['Links /guide','L3 150-400 step5 mm; L2/L3 .85-1.15 step.025; r1.3-2.6 step.005 plus exact5/3'],
            ['Angle /height','q start100-140 step2.5 deg; end solved for325 mm, <=175; full100-260'],
            ['Path target','Normal lateral excursion25/50/75/100 +/-2.5 mm; monotone sideways normal motion'],
            ['Feasibility','Jz>=5 mm/rad across full envelope; L2>60(r+1) pitch separation; 5 deg fold guard'],
            ['Scenarios /ranking','Equal or within5%; geometry-only vs normal220; minimize peakJz or link sum separately'],
            ['Verification','33 coarse poses; retained continuous derivative extrema +2001-pose force/integrals']],
          widths=[117,382],rowheight=29),
        f('The same height reserves trim different angular intervals',rom,'Hip-input angle q (degrees)',
          'Vertical height from normal start (mm)',height=192),
        p(f'Effective ROM solves height roots: qlow=z^-1(zstart+20), qhigh=z^-1(zend-20). '
          f'The 190 mm, 9:5 case has total q=100-{c["config"]["tc"]:.3f} deg and useful '
          f'q={c["force"]["usable_angle_bounds_deg"][0]:.3f}-{c["force"]["usable_angle_bounds_deg"][1]:.3f} deg, '
          f'giving {c["force"]["hip_ROM_deg"]:.3f} deg hip ROM. The 100/175 degree limits are '
          'study assumptions, not hardware stops. Separate 90/95 degree start sensitivities expand '
          'the full envelope consistently and can permit still shorter links.'),
        p('No weighted blended score is used. Force leaders sometimes sit near '
          'a lateral tolerance edge; rounded-ratio examples are chosen for understandable comparisons. '
          'Finite grid and pool retention do not prove global or manufacturing optima.')])
    sec('evidence','Validation and next design choice',
        'Independent original models, numerical tests and actual constrained Pymunk geometry.',[
        p(f'{v["scalar_comparisons"]:,} scalar comparisons against original Jonathan V2 geometry/statics '
          f'and Andy 2D statics pass; maximum discrepancy {v["max_error_mm_Nm"]:.3e} mm/Nm. '
          'Six new tests plus five force and five inversion tests pass. Independent review checks '
          'the new excursion, inverse, force and compliance interpretation.'),
        t(['Actual Pymunk case','2 ms path error mm','1 ms mm','0.5 ms mm'],[
            [label(get(d,c['id'])),*[f'{a["max_path_error_mm"]:.5f}' for a in c['refinement']]] for c in e['cases']],
          widths=[181,112,103,103],rowheight=31),
        p('All three fixtures pass at 2/1/0.5 ms and converge. Real motor/pivot/gear constraints '
          'generate motion with positive body masses; only initial poses are assigned. Zero '
          'gravity/forces and absent collision shapes make this a geometry check, not measured '
          'compliance, force, contact or impact validation. Earlier failures remain in their earlier reports.'),
        p('<b>Start with 190/190 mm and guide 9:5 for the 50 mm case</b> if compact geometry '
          'and unresolved axial packaging are acceptable study assumptions. Use the 285 mm, r=1.85 '
          'normal-clearance alternative if a coplanar wheel/hip layout is mandatory. Compare the '
          '100 mm case only if more lateral sweep is worth its added rolling/scrub and side-load coupling.'),
        p('Next specify actual axial/chassis clearances, spring route, controller stiffness, contact '
          'conditions and motor inertia/duty before selecting stiffness or motor ratings. Previous '
          'spring/motor calculations are separate geometries. No new Motion Lab controls or services '
          'are added; existing models, examples/GIFs and rejected decisions stay intact.'),
        p('Reproduction: curved_path_search.py; test_curved_paths; scripts/verify_curved_geometry.py; '
          'scripts/verify_curved_report.cjs --math-only; scripts/build_curved_report.py; then the full '
          'browser verifier. Detailed commands, source hashes, decisions and revision map are adjacent. '
          'Source base 93fed9f; workspace scope; canonical robot physics NOT APPLICABLE.')])
    return sections


class CurvedReport(Report):
    def section(self,*args):
        super().section(*args)
        self.c.setFillColor(colors.white);self.c.rect(46,24,450,21,fill=1,stroke=0)
        self.text(48,37,'2026-10-14 | Curved lateral paths | Source 93fed9f | Experimental',7,GRAY)


def build_pdf(d,sections):
    target=APP/'docs/curved-path-report.pdf';r=CurvedReport(target,d)
    r.c.setTitle('CAMEL | Curved paths for lateral wheel movement')
    for i,s in enumerate(sections):
        r.section(f'{i+1:02} / CURVED PATH STUDY',s['title'],s['subtitle']);y=665
        for b in s['blocks']:
            if b['kind']=='p':
                y=r.text(48,y,b['text'],9.1)-12
            elif b['kind']=='table':
                y=r.table(48,y,b['widths'],b['headers'],b['rows'],7.6,b.get('rowheight',29))-16
            else:
                y-=15;r.text(48,y+14,b['title'],8.4,GRAY)
                height=b['height'];y-=15
                if b.get('equal'):pdf_paths(r,b['lines'],y=y,h=height,disk=b.get('disk',False))
                else:r.chart(48,y,499,height,b['lines'],b['xlabel'],b['ylabel'])
                y-=height+17
        if y<49:raise ValueError(f'Page {i+1} content ends at {y:.1f}; repair layout')
    r.c.save();return target


def build_html(d,sections):
    css=re.search(r'<style>([\s\S]*?)</style>',(APP/'inversion-paths.html').read_text(encoding='utf-8')).group(1)
    css+='td,th{overflow-wrap:anywhere}.report section{scroll-margin-top:70px}svg{height:auto;max-width:100%}'
    bodies=[]
    for i,s in enumerate(sections):
        blocks=[]
        for b in s['blocks']:
            if b['kind']=='p':blocks.append('<p>'+re.sub(r'</?font[^>]*>','',b['text'])+'</p>')
            elif b['kind']=='table':blocks.append(table(b['headers'],b['rows'],b.get('id','')))
            else:blocks.append('<figure><figcaption>'+html.escape(b['title'])+'</figcaption>'+figure_svg(b)+'</figure>')
        bodies.append(f'<section id="{s["id"]}"><p class="eyebrow">{i+1:02} / CURVED LATERAL PATH STUDY</p><h2>{s["title"]}</h2><p class="lead">{s["subtitle"]}</p>'+''.join(blocks)+'</section>')
    toc=''.join(f'<a href="#{s["id"]}">{i+1:02} {s["title"]}</a>' for i,s in enumerate(sections))
    payload=json.dumps(d,separators=(',',':'),ensure_ascii=False).replace('<','\\u003c')
    out='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    out+='<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'"><title>CAMEL · Curved paths and lateral movement</title><style>'+css+'</style></head><body>'
    out+='<header class="top"><div class="brand">CAMEL <small>Curved path report / October 2026</small></div><div class="top-actions"><a id="pdf-link" href="docs/curved-path-report.pdf">PDF report ↗</a><button class="print-button" id="print-report">Print report</button></div></header>'
    out+='<div class="hero"><div><p class="eyebrow">RATIO CHANGES · ORIGINAL PHASE ZERO</p><h1>Curved paths.<br>Room to move sideways.</h1><p>Compare 25, 50, 75 and 100 mm of lateral travel, with explicit force, control and packaging tradeoffs.</p></div><div class="hero-box"><b>Offline design report</b><span>325 mm total /285 mm useful</span><span>2,953,002 windows searched</span></div></div>'
    out+='<main class="reader"><nav class="toc">'+toc+'<small>Static figures and evidence.<br>No server or network needed.</small></nav><article class="report">'+''.join(bodies)
    out+='<div class="links"><a href="docs/curved-path-study.md">Detailed design record</a><a href="docs/curved-path-results.json">Numerical evidence</a><a href="docs/revisions.md">Revision map</a><a href="force-travel.html">Earlier force report</a><a href="inversion-paths.html">Earlier inversion report</a></div></article></main>'
    out+='<footer class="footer">Experimental allowed motion · actual stiffness and physical inversion unresolved · historical IMPOSSIBLE decisions retained</footer><script type="application/json" id="report-evidence">'+payload+'</script><script>document.getElementById("print-report").addEventListener("click",()=>window.print());</script></body></html>'
    (APP/'curved-paths.html').write_bytes(out.encode())


def main():
    load=lambda name:json.loads((APP/'docs'/name).read_text())
    d,e,v=[load(name) for name in ['curved-path-results.json','curved-path-engine-checks.json','curved-path-math-checks.json']]
    assert e['all_passed'] and v['passed'];sections=content(d,e,v)
    pdf=build_pdf(d,sections);build_html(d,sections)
    from pypdf import PdfReader
    print(json.dumps(dict(pages=len(PdfReader(pdf).pages),pdf_bytes=pdf.stat().st_size,
                         html_bytes=(APP/'curved-paths.html').stat().st_size)))


if __name__=='__main__':main()
