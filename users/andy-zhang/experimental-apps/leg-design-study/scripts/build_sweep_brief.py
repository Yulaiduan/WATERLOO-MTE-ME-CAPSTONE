"""Render equal/unequal comparisons and a proposed next-sweep specification.

Run from app: .venv/Scripts/python.exe scripts/build_sweep_brief.py
Inputs: docs/equal-link-comparison.json, explicit mm/deg/N/Nm assumptions.
Outputs: design-sweep-brief.html and docs/design-sweep-brief.pdf; ReportLab,
pypdf and existing local chart helpers. No search/network/simulation at render.
Limits: selected ideal comparisons and proposed ranges, not a new optimization,
physical clearance, selected springs/motors or validated thermal/contact model.
"""
from pathlib import Path
import html
import json
import hashlib
from reportlab.lib import colors
from build_design_report import Report,GRAY
from build_inversion_report import table
from build_curved_report import get,label,lines,figure_svg

APP=Path(__file__).resolve().parents[1]


def sections(d):
    v=json.loads((APP/'docs/equal-link-comparison-checks.json').read_text())
    assert v['passed'] and v['sources']['docs/equal-link-comparison.json']==hashlib.sha256((APP/'docs/equal-link-comparison.json').read_bytes()).hexdigest()
    p=lambda text:dict(kind='p',text=text)
    t=lambda h,rows,w,**kw:dict(kind='table',headers=h,rows=rows,widths=w,**kw)
    f=lambda title,series,x,y,h:dict(kind='figure',title=title,lines=series,xlabel=x,ylabel=y,height=h)
    out=[]
    def sec(id,title,subtitle,blocks):out.append(dict(id=id,title=title,subtitle=subtitle,blocks=blocks))
    comparisons=[]
    for pair in d['pairs']:
        e,u=[get(d,pair[k]) for k in ['equal','unequal']]
        short=lambda c:f"{c['config']['L2']:g}/{c['config']['L3']:g}; r{c['config']['qab']:g}"
        comparisons.append([str(pair['target_mm']),short(e),short(u),
            f"{e['force']['peak_45kg_hip_Nm']:.2f} /{u['force']['peak_45kg_hip_Nm']:.2f}",
            f"{pair['link_sum_saved_mm']:g}"])
    sec('comparison','Another path-shaping variable','Slightly unequal links do not automatically improve vertical force or motor torque.',[
        p('The current upper-long examples trade <b>0-4.9% less combined link length</b> for '
          '<b>1.1-5.0% more peak vertical-load hip torque</b> and slightly less useful angular ROM '
          'than the similar rounded equal-link examples. Combined length is only a size proxy: '
          'the longest individual link actually grows by 5-15 mm in these comparisons.'),
        t(['Sideways target mm','Equal links mm; guide','Upper-long mm; guide','Hip peak E /U Nm','Total length saved mm'],comparisons,
          [71,123,123,99,83],rowheight=34,id='comparison-table'),
        f('Approximately 50 mm sideways cases: individual holding torque curves',
          lines([get(d,'equal50'),get(d,'upper50')],'force','height_mm','torque_45kg_Nm'),
          'Useful vertical travel (mm)','Direct hip holding magnitude (Nm)',205),
        p('Both families have 325 mm total/285 mm useful height and approximately matched '
          'sideways bands. Guide ratios and total sizes also differ, so this table compares '
          'practical candidates; it does not isolate link mismatch alone. Load is 110.3625 N '
          'vertical per leg, representing 45 kg equally shared over four corners, with '
          'massless moving links and no spring/inertia. These are not motor ratings.'),
        p('<b>Use equal 190/190 mm, r1.8 as the 50 mm baseline.</b> Upper 200/175 mm,15:8 remains '
          'a useful geometry/guide-packaging option. It has not demonstrated a force advantage. '
          'Only optimizing equal and unequal families under identical constraints can compare '
          'their best achievable results.')])
    control=[get(d,k) for k in ['r2_equal','r2_upper']]
    path=lines(control,'normal','z_mm','x_mm',relative=True)
    sec('geometry','Separate vertical and sideways motion','At guide 2:1, total length controls vertical kinematics and length difference controls sideways motion.',[
        p('Let S=L2+L3, D=L2-L3 and t=q-pi. At guide r=2 exactly:<br/>'
          '<font name="Courier">x=D cos(t); z=S sin(t)<br/>'
          'Jx=-D sin(t); Jz=S cos(t)</font><br/>'
          'At fixed S, changing D adds sideways movement without changing vertical height, '
          'vertical-load torque or useful ROM. Equal links give D=0 and a vertical line; '
          'unequal links give an ellipse. Horizontal loads add a different Jx torque term.'),
        f('Sideways displacement versus vertical travel; independent axis ranges',path,
          'Normal vertical travel from start (mm)','Sideways movement from start (mm)',193),
        t(['Fixed S=380 mm, r2','Sideways mm','Hip peak Nm','Guide pitch surplus mm'],[
            [f"{c['config']['L2']:g}/{c['config']['L3']:g}",f"{c['normal']['signed_drift_mm']:.3f}",
             f"{c['force']['peak_45kg_hip_Nm']:.3f}",f"{c['comparison_guide_pitch_surplus_mm']:.1f}"] for c in control],
          [148,105,110,136],rowheight=30),
        p('A fixed 375 mm,15:8 comparison also illustrates the adjustment: equal 187.5/187.5 '
          'gives 31.34 mm sideways travel and 38.361 Nm peak; upper 200/175 gives 49.77 mm '
          'and 38.523 Nm. Both pass the assumed 10 mm guide pitch surplus. This is more '
          'sideways movement for about 0.4% more vertical-load peak at this particular ratio.'),
        p('The equal 195/195,r1.7 fixed-size control reaches 324.800 mm by 175 degrees, just '
          '0.200 mm below the numerical 325 mm threshold. It is retained as a failure rather '
          'than clipping stroke; that tiny threshold difference is not a robust practical '
          'advantage. The separate 185/185,r2 control has only 5 mm guide surplus, below '
          'the assumed 10 mm; it is an analytical control, not a fully feasible candidate.')])
    sec('requirements','Your current design brief','Confirmed owner choices, historical requests and declared study assumptions remain distinct.',[
        t(['Topic','Current state'],[
            ['Mechanism','Jonathan variables/conventions; coupled 1DOF leg; compare equal, upper-long and lower-long links'],
            ['Wheel /links','R200 mm; longer/shorter<=1.25; link-length ratio is separate from guide pulley ratio'],
            ['Stroke /buffers','Approximately 325 mm total including buffers; 20+20 mm split is assumed, giving 285 mm useful'],
            ['Path /inversion','alpha=phi0=0; curved sideways 25/50/75/100 mm; ideal height inverse through full fold'],
            ['Cancelled method','No R2 or fixed 15-degree straight-line/corridor ranking; 10-15 degree line was an earlier preference'],
            ['Loads /motors','Robot 40-45 kg; 3g/4g held-load sensitivity; peak/RMS torque, speed and acceleration requested'],
            ['Springs /checks','Refit existing spring topologies on finalists; compare Jonathan V2, Andy 2D and actual Pymunk'],
            ['Delivery /history','Offline HTML/PDF, labelled plots/GIFs, app MD and revision history; keep reports separate from Motion Lab tooling']],
          [117,382],rowheight=39),
        p('The screenshot originally showed q100-165 degrees. Recent compact examples '
          'extend normal motion to almost 175, with a 5 degree fold guard. Those are study '
          'choices, not established hardware stops. Full ideal inversion is checked on '
          '100-260; any newly lowered normal start must also expand the full domain consistently. '
          'For example, 190/190 mm,r1.8 supplies only 269.21 mm over 100-165 degrees. '
          'The compact 325 mm result relies on the larger angular window.'),
        p('Unequal links shift the fold wheel-centre position by L2-L3, but do not solve '
          'R200 wheel/link overlap. Upper-long folds put C inside upper AB; equal folds put '
          'C at A. Both need actual axial/chassis/hub/tire packaging. Permitted sideways '
          'movement is not measured compliance. Prior spring/motor cases use other geometries; '
          'do not transfer their ratings. Dual-rope remains IMPOSSIBLE /rejected.')])
    sec('next-sweep','A fair next optimization sweep','Proposed ranges and method only; this brief does not run a new large grid.',[
        t(['Variable /scenario','Proposed starting study'],[
            ['Total /imbalance','S350-600 mm; d=(L2-L3)/S in[-1/9,+1/9], including exact d0; record actual individual bounds'],
            ['Guide ratio','r1.2-2.6; compare sensible rational/tooth realizations afterwards; rb60 mm is an assumption'],
            ['Operating window','Normal start 100-140; caps 165/170/175 as separate scenarios; optional 95-degree start sensitivity'],
            ['Height /lateral','325 mm total,20+20 mm reserves; 25/50/75/100 +/-2.5 mm lateral bands, both directions labelled'],
            ['Fixed architecture','alpha=phase=0; R200; original source conventions; equal/upper-long/lower-long families'],
            ['Later physical stage','Measured axial layout, pulley outer sizes, moving mass/inertia, spring route/preload and motor gearing']],
          [117,382],rowheight=36),
        p('<b>Hard filters:</b> owner length bound, exact total stroke and reserves, '
          'positive full-domain Jz with declared5 mm/rad conditioning threshold, no normal '
          'sideways reversal, guide pitch allowance and real clearances when supplied. '
          'Do not invent missing axial dimensions. Classify geometry-only results separately.'),
        p('<b>Keep separate objectives:</b> peak hip torque, RMS torque for the same motion/duty, '
          'maximum link and actual swept envelope, useful ROM, joint speed/acceleration and '
          'side-load robustness. Use a Pareto set: retain designs not beaten in every '
          'chosen objective. No arbitrary blended weights; H/peak torque duplicates peak '
          'ranking when every candidate has the same H.'),
        p('Sweep broadly, retain equal controls in every scenario, then refine selected '
          'tradeoffs continuously and round guide hardware. Recheck tolerances and active '
          'bounds; verify original2D math and actual Pymunk geometry. Finally refit springs '
          'and evaluate a common smooth lift time with moving masses and gearing. '
          'Impact simulation needs actual event/stroke/contact inputs; 3g/4g snapshots '
          'do not specify impact acceleration or damping.'),
        p('Torque is not energy efficiency: ideal lift work is 31.453 J per leg for the '
          'common 285 mm/110.3625 N case. Relative-knee torque=-tau_hip/r and speed=-r times '
          'hip speed; half torque applies only at r2. Actual motor losses, thermal duty '
          'and compliance require their physical inputs. Source 14f53f1; workspace scope; '
          'canonical physics NOT APPLICABLE. Reproduce with compare_link_lengths.py and '
          'verify_sweep_brief.cjs; detailed Markdown retains the copyable next-sweep prompt.'),
        p(f"{v['cases']} analytical cases and {v['scalar_comparisons']:,} independent originalV2/Andy 2D "
          f"scalar comparisons pass; maximum error {v['max_error_mm_Nm']:.3e} mm/Nm. "
          'No new Pymunk, loaded contact, spring or hardware test is claimed by this brief.')])
    return out


class BriefReport(Report):
    def section(self,*args):
        super().section(*args);self.c.setFillColor(colors.white);self.c.rect(46,24,450,21,fill=1,stroke=0)
        self.text(48,37,'2026-10-15 | Equal/unequal comparison and sweep brief | Source 14f53f1 | Experimental',7,GRAY)


def main():
    d=json.loads((APP/'docs/equal-link-comparison.json').read_text());ss=sections(d)
    pdf=APP/'docs/design-sweep-brief.pdf';r=BriefReport(pdf,d);r.c.setTitle('CAMEL | Equal versus unequal links and next sweep')
    bodies=[]
    for i,s in enumerate(ss):
        r.section(f'{i+1:02} / DESIGN SWEEP BRIEF',s['title'],s['subtitle']);y=665;bs=[]
        for b in s['blocks']:
            if b['kind']=='p':y=r.text(48,y,b['text'],9)-11;bs.append('<p>'+b['text'].replace('<font name="Courier">','<code>').replace('</font>','</code>')+'</p>')
            elif b['kind']=='table':
                y=r.table(48,y,b['widths'],b['headers'],b['rows'],7.6,b['rowheight'])-15
                bs.append(table(b['headers'],b['rows'],b.get('id','')))
            else:
                y-=15;r.text(48,y+14,b['title'],8.2,GRAY);y-=15
                r.chart(48,y,499,b['height'],b['lines'],b['xlabel'],b['ylabel']);y-=b['height']+15
                bs.append('<figure><figcaption>'+html.escape(b['title'])+'</figcaption>'+figure_svg(b)+'</figure>')
        if y<49:raise ValueError(f'Page{i+1} content ends at{y:.1f}; repair layout')
        bodies.append(f'<section id="{s["id"]}"><p class="eyebrow">{i+1:02} / DESIGN SWEEP BRIEF</p><h2>{s["title"]}</h2><p class="lead">{s["subtitle"]}</p>'+''.join(bs)+'</section>')
    r.c.save()
    css='*{box-sizing:border-box}body{margin:0;background:#f7f7f0;color:#193b3c;font:17px/1.65 system-ui,sans-serif}header{padding:18px 5%;border-bottom:1px solid #cedbd3;display:flex;justify-content:space-between;gap:15px}a{color:#087e76}button{padding:9px 15px;border:0;background:#193b3c;color:white;border-radius:4px}main{max-width:1050px;margin:auto;padding:28px}h1{font-size:clamp(34px,5vw,64px);line-height:1.1}h2{font-size:29px;line-height:1.25}.eyebrow{color:#087e76;letter-spacing:.14em;font-size:12px;font-weight:bold}.lead{color:#527171}section{margin:36px 0;padding:28px;background:white;border-top:3px solid #087e76}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:12px 9px;vertical-align:top;overflow-wrap:anywhere}th{background:#193b3c;color:white}tr:nth-child(even){background:#eef4f3}figure{margin:25px 0}figcaption{font-weight:600;font-size:14px}svg{width:100%;height:auto}nav{display:flex;flex-wrap:wrap;gap:18px}code{font-size:14px}footer{padding:30px;font-size:13px}@media(max-width:600px){header{flex-direction:column}main{padding:12px}section{padding:14px}table{font-size:11px}th,td{padding:8px 4px}}@media print{body{background:white;font-size:12px}header,nav,.links{display:none}main{max-width:none;padding:0}section{page-break-before:always;padding:0;border:0}section:first-of-type{page-break-before:avoid}h1{font-size:30px}}'
    payload=json.dumps(d,separators=(',',':')).replace('<','\\u003c')
    out='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'"><title>CAMEL | Equal and unequal link design brief</title><style>'+css+'</style></head><body>'
    out+='<header><b>CAMEL / OFFLINE DESIGN BRIEF</b><div><a id="pdf-link" href="docs/design-sweep-brief.pdf">PDF report</a> <button id="print-report">Print</button></div></header><main><p class="eyebrow">EQUAL CONTROLS / UNEQUAL GEOMETRY / NEXT SWEEP</p><h1>What do different<br>link lengths buy?</h1><p>Selected comparisons, your current design requirements, and a proposed optimization study.</p><nav>'+''.join(f'<a href="#{s["id"]}">{s["title"]}</a>' for s in ss)+'</nav>'+''.join(bodies)
    out+='<div class="links"><a href="docs/next-sweep-brief.md">Detailed brief and next-sweep prompt</a> | <a href="docs/equal-link-comparison.json">Numerical evidence</a> | <a href="unequal-inversion.html">Upper-long report and GIFs</a> | <a href="curved-paths.html">Equal-link curved paths</a></div></main><footer>Experimental geometry and static equivalent loads; actual axial packaging, stiffness, motor duty and impacts remain unresolved.</footer><script id="report-evidence" type="application/json">'+payload+'</script><script>document.getElementById("print-report").addEventListener("click",()=>window.print())</script></body></html>'
    (APP/'design-sweep-brief.html').write_bytes(out.encode())
    from pypdf import PdfReader
    print(json.dumps(dict(pages=len(PdfReader(pdf).pages),pdf_bytes=pdf.stat().st_size,html_bytes=len(out.encode()))))


if __name__=='__main__':main()
