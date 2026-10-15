"""Render the equal/upper-long/reverse RMS comparison as offline HTML and PDF.

Run from app: .venv/Scripts/python.exe scripts/build_rms_report.py
Inputs: retained docs/rms-link-results.json/checks.json; mm/deg/N/Nm and unit
time. Outputs rms-link-comparison.html and docs/rms-link-report.pdf with vector
plots and embedded evidence. Uses existing ReportLab/pypdf and chart helpers.
Limits: bounded ideal static RMS screening, no dynamic motor, clearance,
spring, impact or thermal certification. Renderer never runs the search.
"""
from pathlib import Path
import hashlib
import html
import json
from reportlab.lib import colors
from build_design_report import Report,GRAY
from build_inversion_report import table,PALETTE
from build_curved_report import get,lines,figure_svg

APP=Path(__file__).resolve().parents[1]
FAMILIES=['equal','upper125','lower125']
NAMES={'equal':'Equal','upper125':'Upper 1.25x','lower125':'Lower 1.25x'}


def sections(d,v,e):
    p=lambda text:dict(kind='p',text=text)
    t=lambda h,rows,w,height=30:dict(kind='table',headers=h,rows=rows,widths=w,rowheight=height)
    f=lambda title,ls,x,y,h=185:dict(kind='figure',title=title,lines=ls,xlabel=x,ylabel=y,height=h)
    ss=[]
    def sec(id,title,sub,blocks):ss.append(dict(id=id,title=title,subtitle=sub,blocks=blocks))
    fixed=[get(d,k) for k in d['groups']['fixed450_50']]
    e,u,l=fixed
    ratio=lambda c:f"{c['config']['L2']:g}/{c['config']['L3']:g}"
    sec('matched','Reverse lengths can lower hip RMS','Matched 450 mm total link length, exactly +50 mm sideways movement and 325/285 mm height.',[
        p('<b>Lower link=1.25 x upper</b> is the requested reverse orientation. '
          'At the same total size and starting angle, it gives lower hip-equivalent '
          'RMS after retuning the guide to the same lateral movement. It is not a universal '
          'motor benefit: equivalent relative-knee torque gives a different ordering.'),
        t(['Upper/lower mm','Guide ratio','Hip RMS Nm','Knee RMS Nm','Hip peak Nm'],[
          [ratio(c),f"{c['config']['qab']:.6f}",f"{c['rms_quad_hip_Nm']:.3f}",
           f"{c['rms_quad_relative_knee_Nm']:.3f}",f"{c['force']['peak_45kg_hip_Nm']:.3f}"] for c in fixed],
          [115,91,98,98,97],34),
        f('Individual direct-hip holding torque over the useful stroke',lines(fixed,'force','height_mm','torque_45kg_Nm'),
          'Useful vertical travel (mm)','Hip holding magnitude (Nm)',205),
        p(f"Reverse 200/250 gives <b>{100*(1-l['rms_quad_hip_Nm']/e['rms_quad_hip_Nm']):.2f}% less hip RMS</b> "
          f"than equal 225/225 and {100*(1-l['rms_quad_hip_Nm']/u['rms_quad_hip_Nm']):.2f}% less than upper-long 250/200. "
          'Both endpoints are solved for the same 325 mm vertical task; the normal end angles differ '
          '(165.613 /164.802 /167.577 degrees). Guide ratio changes are part of this design comparison.'),
        p('All use alpha=phase=0, start100 degrees, 20+20 mm assumed reserves and '
          '110.3625 N vertical per leg (45 kg shared over four corners). Moving links are massless; '
          'no spring, inertia or loss is included. RMS here is uniform useful height, equivalent '
          'to constant vertical speed without dwell. These are not motor ratings.')])
    rows=[]
    for cap in [165,170,175]:
      for family in FAMILIES:
        c=get(d,f'{family}_{cap}_50');q=c['config']
        rows.append([str(cap),NAMES[family],f"{q['L2']:.1f}/{q['L3']:.1f}",f"{q['qab']:.2f}",f"{c['rms_quad_hip_Nm']:.3f}"])
    chart=[]
    for i,family in enumerate(FAMILIES):
        chart.append(dict(x=[25,50,75,100],y=[get(d,f'{family}_175_{n}')['rms_quad_hip_Nm'] for n in [25,50,75,100]],
          label=NAMES[family],color=colors.HexColor(PALETTE[i]),html_color=PALETTE[i]))
    sec('compact','Compare compact designs fairly','Bounded RMS grid leaders for approximately 50 mm sideways movement; equal links remain eligible.',[
        t(['Angle cap deg','Family','Upper/lower mm','Guide','Hip RMS Nm'],rows,[75,109,150,65,100],24),
        f('175-degree cap: best retained grid hip RMS in each lateral band',chart,
          'Nominal sideways target (mm)','Hip RMS (Nm)',145),
        p('At 175 degrees the lower-long 175.6/219.4 mm, r1.70 gives 30.262 Nm, versus '
          '30.952 Nm for equal190/190,r1.79: about2.23% lower. However, its largest link '
          'is15.5% longer and combined length3.95% larger. These leaders occupy different '
          '+/-2.5 mm lateral bands (48.06 versus52.36 mm), so use the exact50 mm fixed-size '
          'comparison on page1 to isolate a common lateral task.'),
        p('The reverse family has the lowest retained hip RMS in the50 mm band at each cap. '
          'It does not win every case: equal links slightly beat reverse at25 mm and cap175. '
          'Results depend on path, guide, size limits and operating range; grid leaders are not '
          'global continuous optima.')])
    r2=[get(d,k) for k in d['groups']['fixed450_r2']]
    sec('meaning','RMS depends on the actuator and duty','Static load screening must distinguish hip, relative knee and the motor shaft.',[
        p('At guide2:1, fixed S=L2+L3 gives Jz=S cos(q-pi), independent of length difference. '
          '<b>Equal, upper-long and lower-long links therefore have identical vertical-load '
          'RMS, peak, ROM and height history.</b> Their sideways movement differs.'),
        t(['Upper/lower mm, r2','Hip RMS Nm','Knee RMS Nm','Signed lateral mm'],[
          [ratio(c),f"{c['rms_quad_hip_Nm']:.3f}",f"{c['rms_quad_relative_knee_Nm']:.3f}",
           f"{c['normal']['signed_drift_mm']:.3f}"] for c in r2],[151,110,110,128],30),
        f('Same smooth quintic height motion: static hip holding torque only',
          lines(fixed,'timed','time_fraction','torque_45kg_Nm'),'Normalized lift time (no dwell)','Hip holding magnitude (Nm)',170),
        p('For page1 cases, static RMS over the common smooth quintic lift is '
          '34.734 /36.497 /32.856 Nm (equal /upper-long /lower-long); the reverse advantage '
          'persists for this assumed height history. No acceleration torque is included. '
          'Uniform height RMS is not the same weighting as uniform joint angle or smooth time.'),
        p('<b>Coordinate mapping:</b> tau_knee=-tau_hip/r; knee speed=-r times hip speed. '
          'For page1, knee RMS is19.408 /19.008 /19.578 Nm. Reverse is about0.88% higher '
          'than equal in that coordinate. A separate motor gearbox changes torque and speed '
          'again. Compare the actual actuator location, gearing, inertia and duty before choosing.'),
        p('Ideal useful lift work remains31.453 J. RMS helps estimate copper-loss heating '
          'only for a declared motor/gear/duty; it does not establish energy efficiency. '
          'Spring compensation, moving masses, side loads and dwell can change all rankings.')])
    rounded=[get(d,k) for k in d['groups']['rounded_reverse']]
    sec('limits','Useful reverse examples to examine','Both keep lower/upper=1.25, alpha=phase=0 and the existing mathematical height inverse.',[
        t(['Upper/lower mm','Guide','Sideways mm','Hip RMS Nm','End angle deg'],[
          [ratio(c),f"{c['config']['qab']:.5f}",f"{c['normal']['signed_drift_mm']:.2f}",
           f"{c['rms_quad_hip_Nm']:.3f}",f"{c['config']['tc']:.3f}"] for c in rounded],
          [117,88,98,98,98],34),
        p('180/225 mm with17:10 is a rounded compact reverse example:49.10 mm sideways '
          'travel,30.835 Nm hip RMS and36.814 Nm peak. It slightly improves on the earlier '
          'equal190/190,r1.8 example (31.078 Nm RMS), but uses a longer individual link '
          'and25 mm more combined length. 200/250 with12:7 is a larger rational-guide '
          'example, not a lower-torque upgrade to the compact case.'),
        p('<b>Physical inversion remains unresolved.</b> At the reverse fold, C lies beyond '
          'A by L3-L2 while the lower link passes through A in side projection. A45-50 mm '
          'offset does not clear a200 mm wheel or prove the belt/chassis layout. The screen '
          'only assumes rb60 mm and10 mm pitch-circle surplus; outer hardware, axial '
          'stack, tire, fork, chassis and structural dimensions are unknown.'),
        p('Search:582,471 combinations; S350-600 by5 mm, L2/L3=1/1.25/0.8, '
          'guide1.2-2.6 by0.01, starts100-140 by5 degrees, separate caps165/170/175, '
          '325 mm height,20+20 reserves, lateral25/50/75/100 +/-2.5 mm, monotone normal '
          'sideways motion and full100-260 height inverse with Jz>=5 mm/rad. '
          '36 selected grid leaders are checked continuously for extrema after sampled screening. '
          'Only hip RMS is optimized; knee and quintic values are evaluations, not separate optima.'),
        p(f"Validation: {v['cases']} analytical cases; {v['scalar_comparisons']:,} independent originalV2/Andy "
          f"comparisons pass. Height RMS error {v['max_height_RMS_error_Nm']:.2e} Nm; "
          f"quintic RMS error {v['max_quintic_RMS_error_Nm']:.2e} Nm. Independent adaptive "
          'quadrature and doubled time resolution also pass. Three actual positive-mass '
          'Pymunk full100-260 degree sweeps pass at2/1/0.5/0.25 ms and converge; finest '
          'path errors0.00755/0.00847/0.00736 mm. Zero gravity/forces/collision shapes: '
          'geometry only. No loaded Pymunk, spring, '
          'impact, contact, clearance, hardware or thermal validation is claimed.'),
        p('Keep all earlier reports, model decisions and the dual-rope IMPOSSIBLE/rejected '
          'status. Refit springs and actual motor dynamics only after selecting geometry, '
          'physical packaging and duty. Source c92880d; isolated workspace; canonical physics '
          'NOT APPLICABLE. Reproduction commands and evidence are in the adjacent design record.')])
    return ss


class RmsReport(Report):
    def section(self,*args):
        super().section(*args);self.c.setFillColor(colors.white);self.c.rect(46,24,450,21,fill=1,stroke=0)
        self.text(48,37,'2026-10-15 | Equal and reverse link RMS | Source c92880d | Experimental',7,GRAY)


def main():
    d=json.loads((APP/'docs/rms-link-results.json').read_text());v=json.loads((APP/'docs/rms-link-checks.json').read_text())
    assert v['passed'] and v['sources']['docs/rms-link-results.json']==hashlib.sha256((APP/'docs/rms-link-results.json').read_bytes()).hexdigest()
    e=json.loads((APP/'docs/rms-link-engine-checks.json').read_text());assert e['all_passed']
    assert all(hashlib.sha256((APP/p).read_bytes()).hexdigest()==h for p,h in e['sources'].items())
    ss=sections(d,v,e);r=RmsReport(APP/'docs/rms-link-report.pdf',d);r.c.setTitle('CAMEL | Equal and reverse link RMS comparison');bodies=[]
    for i,s in enumerate(ss):
        r.section(f'{i+1:02} / RMS COMPARISON',s['title'],s['subtitle']);y=665;body=[]
        for b in s['blocks']:
            if b['kind']=='p':y=r.text(48,y,b['text'],9)-11;body.append('<p>'+b['text']+'</p>')
            elif b['kind']=='table':
                y=r.table(48,y,b['widths'],b['headers'],b['rows'],7.6,b['rowheight'])-15;body.append(table(b['headers'],b['rows']))
            else:
                y-=15;r.text(48,y+14,b['title'],8.2,GRAY);y-=15;r.chart(48,y,499,b['height'],b['lines'],b['xlabel'],b['ylabel']);y-=b['height']+15
                body.append('<figure><figcaption>'+html.escape(b['title'])+'</figcaption>'+figure_svg(b)+'</figure>')
        if y<49:raise ValueError(f'Page{i+1} ends at{y}; repair layout')
        bodies.append(f'<section id="{s["id"]}"><p class="eyebrow">{i+1:02} / RMS COMPARISON</p><h2>{s["title"]}</h2><p class="lead">{s["subtitle"]}</p>'+''.join(body)+'</section>')
    r.c.save()
    css='*{box-sizing:border-box}body{margin:0;background:#f7f7f0;color:#193b3c;font:17px/1.65 system-ui,sans-serif}header{padding:18px 5%;border-bottom:1px solid #cedbd3;display:flex;justify-content:space-between;gap:15px}a{color:#087e76}button{padding:9px 15px;border:0;background:#193b3c;color:white}main{max-width:1050px;margin:auto;padding:28px}h1{font-size:clamp(34px,5vw,64px);line-height:1.1}h2{font-size:29px;line-height:1.25}.eyebrow{color:#087e76;letter-spacing:.14em;font-size:12px;font-weight:bold}.lead{color:#527171}section{margin:36px 0;padding:28px;background:white;border-top:3px solid #087e76}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:12px 9px;vertical-align:top;overflow-wrap:anywhere}th{background:#193b3c;color:white}tr:nth-child(even){background:#eef4f3}figure{margin:25px 0}figcaption{font-weight:600;font-size:14px}svg{width:100%;height:auto}nav{display:flex;flex-wrap:wrap;gap:18px}footer{padding:30px;font-size:13px}@media(max-width:600px){header{flex-direction:column}main{padding:12px}section{padding:14px}table{font-size:11px}th,td{padding:8px 4px}}@media print{body{background:white;font-size:12px}header,nav,.links{display:none}main{max-width:none;padding:0}section{page-break-before:always;padding:0;border:0}section:first-of-type{page-break-before:avoid}h1{font-size:30px}}'
    out='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'"><title>CAMEL | Equal and reverse link RMS</title><style>'+css+'</style></head><body>'
    out+='<header><b>CAMEL / OFFLINE RMS STUDY</b><div><a id="pdf-link" href="docs/rms-link-report.pdf">PDF report</a> <button id="print-report">Print</button></div></header><main><p class="eyebrow">EQUAL / UPPER-LONG / LOWER-LONG 1.25x</p><h1>Which lengths<br>reduce RMS torque?</h1><p>Matched controls, a bounded RMS sweep and actuator-coordinate comparisons.</p><nav>'+''.join(f'<a href="#{s["id"]}">{s["title"]}</a>' for s in ss)+'</nav>'+''.join(bodies)
    out+='<div class="links"><a href="docs/rms-link-study.md">Design record</a> | <a href="docs/rms-link-results.json">Numerical evidence</a> | <a href="design-sweep-brief.html">Earlier design brief</a></div></main><footer>Ideal static screening; physical packaging, stiffness, dynamics and actual motor duty remain unresolved.</footer><script id="report-evidence" type="application/json">'+json.dumps(d,separators=(',',':')).replace('<','\\u003c')+'</script><script>document.getElementById("print-report").addEventListener("click",()=>window.print())</script></body></html>'
    (APP/'rms-link-comparison.html').write_bytes(out.encode())
    from pypdf import PdfReader
    print(json.dumps(dict(pages=len(PdfReader(APP/'docs/rms-link-report.pdf').pages),html_bytes=len(out.encode()),pdf_bytes=(APP/'docs/rms-link-report.pdf').stat().st_size)))


if __name__=='__main__':main()
