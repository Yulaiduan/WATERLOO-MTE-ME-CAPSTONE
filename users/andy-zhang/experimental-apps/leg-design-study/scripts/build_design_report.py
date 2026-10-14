"""Build the generalized leg design report from compact retained computation.

Invocation from app root: python scripts/build_design_report.py
Optional install: python -m pip install -r requirements-report.txt (Python 3.13).
Inputs: docs/generalized-leg-report-data.json; mm/deg/kg/N/Nm/s explicitly labelled.
Outputs: docs/generalized-leg-report.pdf, a vector report using ReportLab.
Requires ReportLab and pypdf; no machine-specific paths or network retrieval.
Limitations: reproduces experimental analytical/rigid-body evidence, not a
hardware/canonical robot certification or rerun of every retained optimization.
Use the source model/test commands in the report to recompute its evidence.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

APP = Path(__file__).resolve().parents[1]
NAVY = colors.HexColor('#122B3E')
TEAL = colors.HexColor('#087F83')
BLUE = colors.HexColor('#3267A5')
GOLD = colors.HexColor('#B57A2D')
RED = colors.HexColor('#BB4D51')
INK = colors.HexColor('#243847')
GRAY = colors.HexColor('#5B6A76')
PALE = colors.HexColor('#EDF3F6')
COLORS = [TEAL, BLUE, GOLD, RED, colors.HexColor('#77629A'), colors.HexColor('#64832A')]
W, H = 595.276, 841.890


def fmt(value, digits=2):
    return f'{float(value):,.{digits}f}' if value is not None else 'not available'


class Report:
    def __init__(self, target, data):
        self.c = canvas.Canvas(str(target), pagesize=(W, H), pageCompression=1, invariant=1)
        self.c.setTitle('CAMEL | Generalized wheel-leg design study')
        self.c.setAuthor('Andy Zhang with Codex | CAMEL member experiment')
        self.data = data
        self.page = 0

    def text(self, x, y, message, size=9, color=INK, width=499, bold=False):
        style = ParagraphStyle('p', fontName='Helvetica-Bold' if bold else 'Helvetica',
                               fontSize=size, leading=size*1.42, textColor=color,
                               spaceAfter=0)
        p = Paragraph(message, style)
        _, height = p.wrap(width, H)
        p.drawOn(self.c, x, y-height)
        return y-height

    def section(self, label, title, subtitle=''):
        if self.page:
            self.c.showPage()
        self.page += 1
        self.c.setFillColor(NAVY)
        self.c.rect(0, H-12, W, 12, fill=1, stroke=0)
        self.text(48, 797, 'CAMEL  /  CONTROLLED ACTIVE-SUSPENSION MOBILITY FOR EXTREME LANDSCAPES', 7.3, TEAL, bold=True)
        self.text(48, 772, label.upper(), 8, GRAY, bold=True)
        self.text(48, 753, title, 23, NAVY, bold=True)
        if subtitle:
            self.text(48, 711, subtitle, 10, GRAY)
        self.c.setStrokeColor(colors.HexColor('#D5E0E6'))
        self.c.line(48, 48, W-48, 48)
        self.text(48, 37, '2026-10-14  |  Experimental member study  |  Base 6c74cfd', 7, GRAY)
        self.c.setFont('Helvetica', 7)
        self.c.setFillColor(GRAY)
        self.c.drawRightString(W-48, 27, str(self.page))

    def box(self, x, y, w, h, label, value, detail=''):
        self.c.setFillColor(PALE)
        self.c.roundRect(x, y-h, w, h, 5, fill=1, stroke=0)
        self.text(x+12, y-11, label.upper(), 7, GRAY, width=w-24, bold=True)
        self.text(x+12, y-29, value, 20, NAVY, width=w-24, bold=True)
        if detail:
            self.text(x+12, y-57, detail, 8, GRAY, width=w-24)

    def table(self, x, y, widths, headers, rows, size=8, row_height=29):
        self.c.setFillColor(NAVY)
        self.c.rect(x, y-row_height, sum(widths), row_height, fill=1, stroke=0)
        xx = x
        for width, head in zip(widths, headers):
            self.text(xx+6, y-6, head, size, colors.white, width=width-12, bold=True)
            xx += width
        y -= row_height
        for index, row in enumerate(rows):
            self.c.setFillColor(PALE if index%2 == 0 else colors.white)
            self.c.rect(x, y-row_height, sum(widths), row_height, fill=1, stroke=0)
            xx = x
            for width, cell in zip(widths, row):
                self.text(xx+6, y-6, str(cell), size, INK, width=width-12)
                xx += width
            y -= row_height
        return y

    def chart(self, x, y, w, h, lines, xlabel, ylabel, title='', xlim=None, ylim=None,
              scatter=False):
        if title:
            self.text(x, y+26, title, 10, NAVY, width=w, bold=True)
        left, right, bottom, top = 47, 9, 37, 20
        xs = [a for line in lines for a in line['x']]
        ys = [a for line in lines for a in line['y']]
        if not xs or not ys:
            return
        xmin, xmax = xlim or (min(xs), max(xs))
        ymin, ymax = ylim or (min(ys), max(ys))
        if xmax == xmin:
            xmax += 1
        if ymax == ymin:
            ymax += 1
        if ylim is None:
            pad=(ymax-ymin)*.08
            ymin-=pad; ymax+=pad
        xx=lambda v:x+left+(v-xmin)/(xmax-xmin)*(w-left-right)
        yy=lambda v:y-h+bottom+(v-ymin)/(ymax-ymin)*(h-bottom-top)
        self.c.setFont('Helvetica', 7)
        for i in range(5):
            v=ymin+(ymax-ymin)*i/4
            self.c.setLineWidth(.6)
            self.c.setStrokeColor(colors.HexColor('#DFE8EC'))
            self.c.line(xx(xmin), yy(v), xx(xmax), yy(v))
            self.c.setFillColor(GRAY)
            self.c.drawRightString(x+left-6, yy(v)-2, f'{v:.1f}')
        for i in range(5):
            v=xmin+(xmax-xmin)*i/4
            self.c.setFillColor(GRAY)
            self.c.drawCentredString(xx(v), y-h+bottom-12, f'{v:.1f}')
        self.c.setStrokeColor(GRAY)
        self.c.setLineWidth(.8)
        self.c.line(xx(xmin), yy(ymin), xx(xmax), yy(ymin))
        self.c.line(xx(xmin), yy(ymin), xx(xmin), yy(ymax))
        for index,line in enumerate(lines):
            color=line.get('color',COLORS[index%len(COLORS)])
            self.c.setStrokeColor(color); self.c.setFillColor(color)
            self.c.setLineWidth(line.get('width',1.8)); self.c.setDash(3,2) if line.get('dash') else self.c.setDash()
            pairs=list(zip(line['x'],line['y']))
            if scatter or line.get('scatter'):
                for a,b in pairs:
                    self.c.circle(xx(a),yy(b),3,fill=1,stroke=0)
            elif pairs:
                path=self.c.beginPath(); path.moveTo(xx(pairs[0][0]),yy(pairs[0][1]))
                for a,b in pairs[1:]:path.lineTo(xx(a),yy(b))
                self.c.drawPath(path)
            self.c.setDash()
        self.text(x+left, y-h+12, xlabel, 8, GRAY, width=w-left)
        self.c.saveState(); self.c.translate(x+11,y-h/2); self.c.rotate(90)
        self.c.setFont('Helvetica',8);self.c.setFillColor(GRAY)
        self.c.drawCentredString(0,0,ylabel);self.c.restoreState()
        # Compact multi-row legend above the plotting area.
        cursor=x+left
        for index,line in enumerate(lines):
            color=line.get('color',COLORS[index%len(COLORS)])
            label=line.get('label','')
            legend_width=min(200,max(95,22+len(label)*4.7))
            if cursor+legend_width>x+w:
                cursor=x+left; top+=12
            self.c.setStrokeColor(color);self.c.setLineWidth(2);self.c.line(cursor,y+8-top+20,cursor+10,y+8-top+20)
            self.text(cursor+14,y+12-top+20,label,7,GRAY,width=legend_width-16)
            cursor+=legend_width

    def arrow(self, a, b, color=INK, width=1.3):
        self.c.setStrokeColor(color); self.c.setFillColor(color);self.c.setLineWidth(width)
        self.c.line(*a,*b)
        ang=math.atan2(b[1]-a[1],b[0]-a[0]);p=self.c.beginPath();p.moveTo(*b)
        p.lineTo(b[0]-7*math.cos(ang-.4),b[1]-7*math.sin(ang-.4))
        p.lineTo(b[0]-7*math.cos(ang+.4),b[1]-7*math.sin(ang+.4));p.close()
        self.c.drawPath(p,fill=1,stroke=0)

    def mechanism(self, case, x=295, y=465, scale=.55):
        s=case['profile']['samples'][len(case['profile']['samples'])//2]
        pts={key:(x+s[key][0]*scale,y+s[key][1]*scale) for key in ['Ag','Bg','Cg','Pg']}
        a,b,c,p=(pts[key] for key in ['Ag','Bg','Cg','Pg'])
        self.c.setStrokeColor(TEAL);self.c.setLineWidth(8);self.c.line(*a,*b)
        self.c.setStrokeColor(GOLD);self.c.line(*b,*c)
        self.c.setStrokeColor(BLUE);self.c.setLineWidth(1.3);self.c.circle(*c,case['config']['rw']*scale,stroke=1,fill=0)
        for label,point in [('A',a),('B',b),('C',c),('P',p)]:
            self.c.setFillColor(NAVY);self.c.circle(*point,3,fill=1,stroke=0)
            self.text(point[0]+8,point[1]+8,label,10,NAVY,width=50,bold=True)
        self.arrow(b,a,BLUE);self.arrow(c,b,TEAL);self.arrow(a,(a[0]+65,a[1]),GRAY)
        self.arrow(a,(a[0],a[1]+65),GRAY)
        self.text(a[0]+65,a[1]+7,'+y',9,GRAY,width=35)
        self.text(a[0]-9,a[1]+80,'+z',9,GRAY,width=35)
        alpha=math.radians(case['config']['alpha'])
        self.arrow(a,(a[0]+90*math.cos(alpha),a[1]-90*math.sin(alpha)),GOLD,.8)
        self.arrow(a,(a[0]+45*math.sin(alpha),a[1]+45*math.cos(alpha)),GOLD,.8)
        self.text(a[0]+91,a[1]-7,'+u',8,GOLD,width=30)
        self.text(a[0]+12,a[1]+54,'+v',8,GOLD,width=30)
        self.arrow(c,(c[0]+80,c[1]),GRAY)
        self.text(c[0]+45,c[1]-8,'global horizontal',7,GRAY,width=95)
        return pts


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=APP/'docs/generalized-leg-report-data.json')
    parser.add_argument('--output',type=Path,default=APP/'docs/generalized-leg-report.pdf')
    args=parser.parse_args()
    data=json.loads(args.data.read_text(encoding='utf-8'))
    report=Report(args.output,data)
    render(report,data)
    report.c.save()
    from pypdf import PdfReader
    reader=PdfReader(args.output)
    print(json.dumps(dict(output=args.output.name,pages=len(reader.pages),bytes=args.output.stat().st_size,
                         text_characters=sum(len(page.extract_text() or '') for page in reader.pages))))


def render(r,d):
    """Lay out the report; every chart uses retained numerical samples."""
    a=d['analytical'];p=d['physics'];cases={x['id']:x for x in a['cases']}
    central=cases['325_peak'];m=central['profile']['metrics'];b=a['baseline'];s=p['selected_spring']
    qrows=p['cycle_trajectory'];cm=p['cycle_metrics']
    names={'legacy_tip':'Legacy tip','hip_pulley':'Hip pulley','knee_pulley':'Knee pulley',
           'direct_scissor':'Direct scissor','hip_bellcrank':'Hip bellcrank','knee_bellcrank':'Knee bellcrank',
           'chassis_direct':'Chassis direct','knee_capture':'Knee capture','gravity_balance':'Gravity balance'}
    def trace(case,key,xkey='usableDz',label=None,color=None):
        rows=case['profile']['samples']
        return dict(x=[x[xkey] for x in rows],y=[x[key] for x in rows],
                    label=label or case.get('id','Reference'),color=color or TEAL)
    def cycle(key,label,color=TEAL):
        return dict(x=[x['time_s'] for x in qrows],y=[x[key] for x in qrows],label=label,color=color)

    # 1 - Decision summary
    r.section('Report / design screening','Generalized wheel-leg study',
              'Jonathan V2 geometry + Andy sizing + independent suspension mechanics')
    r.text(48,666,'A compact, non-2:1 candidate meets the central travel target. Its useful stroke is '
           '285 mm after two geometric reserves. Spring and motor requirements depend on a separate '
           'supported-chassis fixture, actual mass allocation and motion time.',11,NAVY,bold=True)
    for x,label,value,detail in [(48,'Total capacity','325 mm','includes both end reserves'),
                                 (219,'Useful capacity','285 mm','20 mm + 20 mm reserved'),
                                 (390,'Guide ratio','1.775','free variable; not fixed at 2')]:
        r.box(x,586,157,88,label,value,detail)
    r.text(48,468,'Conditional geometry',12,NAVY,bold=True)
    r.text(48,444,'L2 = 180 mm; L3 = 340 mm; ra/rb = 106.5/60 mm; mounting alpha = 4.375 deg. '
           'Physical theta2 = 100 to 159.810888 deg; useful theta2 = 106.429341 to 157.077766 deg. '
           'Wheel radius = 200 mm. Summed links = 520 mm; full lateral excursion = 11.412 mm.',10)
    r.table(48,364,[249,250],['Result / fixture','Computed value'],[
        ('Fixed-A robust static score','46.260 Nm peak / 41.089 Nm time RMS'),
        ('Supported chassis, 10 kg corner','Hip bellcrank, 1 s per direction, zero damping'),
        ('Ideal joint motor demand, full cycle',f'{fmt(cm["torque_peak_abs"],3)} Nm peak / {fmt(cm["torque_rms"],3)} Nm RMS'),
        ('Joint speed / acceleration',f'{fmt(cm["speed_peak_abs"],3)} rad/s / {fmt(cm["accel_peak_abs"],3)} rad/s2'),
        ('Held 4g TOTAL support, 11.25 kg','143.772 Nm joint-output stress envelope')],8,27)
    r.text(48,177,'Decision boundary',11,NAVY,bold=True)
    r.text(48,154,'The geometry is a compact bounded-search example. Extending the tibia domain finds lower '
           'static torque at greater length and drift. No selected motor, manufactured spring, strength '
           'rating, tire-contact feasibility or 3D clearance has been established. Numerical agreement '
           'does not certify a canonical robot.',9.5)
    r.text(48,84,'Report map: 2 reference; 3 coordinates; 4 constraints; 5-8 optimization; '
           '9-10 springs; 11-12 motion; 13-14 impact envelope; 15 verification; 16 reproduction.',8,GRAY)

    # 2 - Full original parameter source, without private screenshots
    r.section('Reference / original solver','Screenshot case reproduced',
              'Rebuilt from entered parameters; no private screenshot is retained in this report.')
    rows=[('Links / wheel','L2 = L3 = 250 mm; rw = 200 mm radius (diameter 400 mm)'),
          ('Guide radii / ratio','ra = 100; rb = 60 mm; qab = 5/3 = 1.666667'),
          ('Drive radii','rc = rd = re = rf = 35 mm; qcd = qef = 1'),
          ('Angles / current pose','te = 100; tc = 165; theta2 = 100.135 deg'),
          ('Mounting / contact','alpha = 0; beta = 13.5 deg; phi0 = 0 assumed'),
          ('Driving loads','Global Fy = Fz = +100 N; Fn/Ft derived'),
          ('Masses / gravity','m1 = 10 kg; m2 = m3 = m5 = m6 = 0; g = 9.81 m/s2'),
          ('Other explicit assumptions','r5I = 35 mm; Tab0 = Tcd0 = Tef0 = 0 N')]
    r.table(48,663,[126,373],['Input family','Original value'],rows,8.4,35)
    bp=b['pose'];r.text(48,337,'At the captured pose',12,NAVY,bold=True)
    r.table(48,313,[125,125,125,124],['theta3 (deg)','tau2 (Nm)','tau4 (Nm)','Tight ab span (N)'],[
        (fmt(bp['theta3'],5),fmt(bp['tau2'],5),fmt(bp['tau4'],5),fmt(bp['Tab'],5)+' / lower')],9,31)
    r.text(48,232,'Current C displacement is (0.265170, 0.337721) mm. Final displacement is '
           '(101.157122, 338.615931) mm. With 20 mm excluded at each end, useful vertical '
           'travel is 298.615931 mm. The lateral motion is a real property of this generalized geometry.',10)
    r.text(48,157,'Original global maxima',11,NAVY,bold=True)
    r.text(48,133,'Across theta2 = 100-165 and beta = 0-90 deg, alpha fixed at 0: '
           '|tau2| = 44.448948 Nm; |tau4| = 20 Nm; tight Tab = 337.983156 N. '
           'These are the original solver\'s attained analytical maxima, separate from this report\'s '
           'fixed-beta robust design objective.',9)
    r.text(48,81,'Phi0 and preloads were not visible in the reference: zero is an explicit demonstration '
           'assumption. Massless moving links are an analytical limit, not an executable physical fixture.',8,GRAY)

    # 3 - Coordinates and equation map
    r.section('Mechanism / conventions','One geometry, clear frames',
              'A = hip; B = knee; C = wheel centre; P = contact patch. V2 names are preserved.')
    r.mechanism(central,x=250,y=612,scale=.50)
    r.text(367,653,'Angle directions',10,NAVY,width=175,bold=True)
    r.text(367,631,'theta2 points B to A.<br/>theta3 points C to B.<br/>Both are CCW from local +u.<br/>'
           'Alpha rotates u/v clockwise relative to y/z.<br/>Beta is clockwise from -z toward -y.',9,width=175)
    r.text(48,354,'Generalized linkage and drive',11,NAVY,bold=True)
    r.text(48,331,'<font name="Courier-Bold">theta3 = phi0 + (180 - theta2)(qab - 1)<br/>'
           'B = -L2 [cos(theta2), sin(theta2)]<br/>C = B - L3 [cos(theta3), sin(theta3)]<br/>'
           'dC/dq = dB/dq + (1-qab)L3 [sin(theta3),-cos(theta3)]<br/>'
           'K = 1-qab + qef(qab-qcd); theta6 = K (theta2-te)</font>',9)
    r.text(48,242,'Actual wheel-centre upward angle',11,NAVY,bold=True)
    r.text(48,219,'Measure the lower-link ray C to B against the <b>global</b> horizontal through C:<br/>'
           '<font name="Courier-Bold">angle = atan2(Bz-Cz, By-Cy) = wrapped(theta3-alpha)</font><br/>'
           'Central useful range: 52.642261 to 13.389732 deg. The expression 180-theta2 applies '
           'only to the equal-link, qab=2, phi0=alpha=0 special case.',9.2)
    r.text(48,125,'Coordinate work conservation',11,NAVY,bold=True)
    r.text(48,102,'Relative knee derivative is -qab. Therefore signed tau_knee = -tau2/qab, '
           'omega_knee = -qab*qdot. A different coordinate can lower torque while increasing speed; '
           'it does not improve ideal work or transmission efficiency.',9)

    # 4 - Buffers and feasibility
    r.section('Requirement / feasibility','Travel includes the reserves',
              'Hard minimum useful stroke 200 mm; preferred about 250 mm; editable total 300-350 mm.')
    for x,total,usable in [(48,300,260),(219,325,285),(390,350,310)]:
        r.box(x,659,157,78,f'{total} mm total',f'{usable} mm','usable; 20 mm reserved each end')
    pathlines=[]
    for key,label,col in [('325_peak','Compact central',TEAL),('expanded_peak','Expanded bound',GOLD)]:
        rows=cases[key]['profile']['physicalSamples'];pathlines.append(dict(x=[s['dy'] for s in rows],y=[s['dz'] for s in rows],label=label,color=col))
    rows=b['profile']['physicalSamples'];pathlines.append(dict(x=[s['dy'] for s in rows],y=[s['dz'] for s in rows],label='Original reference',color=BLUE))
    r.chart(48,519,499,224,pathlines,'Lateral displacement from extension (mm)',
            'Vertical displacement (mm)','Full physical wheel-centre paths')
    r.table(48,267,[250,249],['Constraint / assumption','Central candidate'],[
        ('Useful stops, 20 mm each','106.429341 to 157.077766 deg'),
        ('Minimum useful vertical Jacobian',fmt(m['minJacobian'],3)+' mm/rad (required >= 5)'),
        ('Full lateral excursion',fmt(m['drift'],3)+' mm (limit 150)'),
        ('Flat-ground chassis air gap',fmt(m['minClearance'],3)+' mm (depth 200, gap >= 20)'),
        ('Projected hip-to-wheel rim gap',fmt(m['minHipRimGap'],3)+' mm (assumed >= 20)')],8,26)
    r.text(48,96,'Wheel radius controls gap and contact moment, not automatic travel. The projected hip '
           'exclusion disk is a conservative optional assumption: staggering axial planes may resolve a '
           'projected overlap. The reference remains mathematically valid when that filter rejects it.',8.2,GRAY)

    # 5 - Methods, exact targets, six recorded results
    r.section('Optimization / two methods','Bounded search, exact targets',
              'Loads and masses stay fixed; suspension/drive demand is scored in declared coordinates.')
    r.text(48,666,'<b>Scalar:</b> coarse grid, feasible peak/RMS ranking, four leading seeds, halved coordinate '
           'steps. <b>Pareto:</b> torque/link sum/drift nondominance, then up to twelve frontier seeds. '
           'Both densely recheck finalists with at least 721 samples; exactTarget solves tc for the selected total.',9.3)
    r.text(48,604,'Domains: L2 and L3 180-340 step40 mm; qab 1.4-2.4 step0.25; alpha 0-20 step10 deg; '
           'te 100-110 step10 deg; solved tc constrained to 155-170 deg. Off-grid upper endpoints included. '
           '750 coarse geometries; four refinement passes for this six-row comparison.',8.5,GRAY)
    rows=[]
    for case in a['cases'][:6]:
        cc=case['config'];mm=case['profile']['metrics'];rows.append((f'{cc["targetTotal"]}/{fmt(mm["usableTravel"],0)}',
          cc['objective'],f'{fmt(cc["L2"],1)}/{fmt(cc["L3"],0)}',fmt(cc['ra']/cc['rb'],4),fmt(cc['alpha'],3),
          fmt(mm['peak'],3),fmt(mm['rms'],3),fmt(mm['drift'],2)))
    r.table(48,534,[60,49,77,59,53,69,68,64],['Total/use<br/>mm','Score','L2/L3<br/>mm','qab','alpha<br/>deg','Peak<br/>Nm','RMS<br/>Nm','Drift<br/>mm'],rows,7.6,31)
    r.chart(48,264,499,158,[dict(x=[0,1,2,3,4],y=[50.629180619,46.612880824,46.612880824,46.612880824,46.259849899],label='Peak objective',color=TEAL),
             dict(x=[0,1,2,3,4],y=[42.549838132,39.869076946,39.566271270,39.484833628,39.443351875],label='RMS objective',color=GOLD)],
             'Refinement pass (0 = coarse)','Selected objective (Nm)','Central-case convergence')
    r.text(48,82,'Robust score = worst case over Fy = -100, 0, +100 N at Fz = 100 N and beta = 13.5 deg. '
           'Peak/RMS use sqrt(tau2^2+tau4^2), an equal-weight two-actuator demand score, not one motor rating.',8,GRAY)

    # 6 - Signed, complete parametric torque profiles
    r.section('Profiles / nominal contact','See the whole control window',
              'Signed nominal traces retain horizontal-force assistance and actual drive torque.')
    keys=['300_peak','325_peak','350_peak','expanded_peak']
    styles={'300_peak':('300 mm total',BLUE),'325_peak':('325 mm total',TEAL),
            '350_peak':('350 mm total',RED),'expanded_peak':('Expanded bound',GOLD)}
    lines=[trace(cases[k],'tau2',label=styles[k][0],color=styles[k][1]) for k in keys]
    lines.append(trace(b,'tau2',label='Original reference',color=COLORS[4]))
    r.chart(48,653,499,247,lines,'Useful vertical travel from buffered extension (mm)',
            'Signed suspension tau2 (Nm)','Full suspension output profiles')
    lines=[trace(cases[k],'tau4',label=styles[k][0],color=styles[k][1]) for k in keys]
    r.chart(48,342,499,160,lines,'Useful vertical travel (mm)','Signed drive tau4 (Nm)',
            'Drive holding demand (qcd = qef = 1)')
    r.text(48,156,'All four design cases have K=0 although qab varies. The nominal drive holding torque is '
           '-14.778491 Nm; the robust envelope reaches 24.116306 Nm magnitude under opposite Fy. '
           'These traces show the entered +100/+100 N force, while the search table uses the worst configured case.',9)
    r.text(48,95,'Signed mean is not a sizing minimum. The central nominal |tau2| peak is 43.782204 Nm; '
           'combined nominal peak/RMS is 46.209146/37.041717 Nm. Ideal nominal motor work over useful '
           'compression is -28.291453 J; external prescribed-load work is +28.291460 J.',8.3,GRAY)

    # Torque-normalized travel is a capability score, never physical efficiency.
    r.section('Capability / work and torque','Travel per torque demand',
              'Compare the same loading, actuator coordinates and motion weighting.')
    rows=[]
    for case in a['cases'][:6]:
        cc=case['config'];mm=case['profile']['metrics']
        rows.append((f'{cc["targetTotal"]} / {cc["objective"]}',fmt(mm['usableTravel'],0),
                     fmt(mm['peak'],3),fmt(mm['rms'],3),fmt(mm['usableTravel']/mm['rms'],3),
                     fmt(case['profile']['bounds']['usableTc']-case['profile']['bounds']['usableTe'],3)))
    r.table(48,656,[106,79,78,78,80,78],['Case / search','Useful<br/>stroke mm','Robust<br/>peak Nm','Time<br/>RMS Nm','Stroke/RMS<br/>mm per Nm','Actuator<br/>ROM deg'],rows,7.8,34)
    r.text(48,390,'Peak, mean and RMS answer different questions',12,NAVY,bold=True)
    r.text(48,364,'<b>Peak</b> is the greatest transient magnitude. <b>Mean absolute torque</b> describes typical '
           'demand under a stated weighting. <b>Signed mean</b> can cancel strong positive and negative '
           'loads and therefore cannot size a motor. <b>Time RMS</b> weights high demands quadratically '
           'and can inform copper-loss comparisons for one fixed motor/gearing/duty model. The combined '
           'sqrt(tau2^2+tau4^2) score here describes two output coordinates; it is not one motor\'s heating.',9.5)
    r.text(48,257,'Torque-normalized capability is not efficiency',12,NAVY,bold=True)
    r.text(48,232,f'Central stroke/RMS = {fmt(m["usableTravel"]/m["rms"],3)} mm/Nm. '
           'At fixed useful stroke, maximizing this is equivalent to minimizing the chosen RMS. '
           'It is dimensionful and does not account for angular ROM, speed, current, conversion losses or '
           'regeneration. Changing to a relative-knee coordinate changes torque and speed in opposite '
           'directions without increasing ideal work.',9.5)
    r.text(48,148,'Ideal work and true efficiency',12,NAVY,bold=True)
    r.text(48,123,'Ideal actuator work is W = integral(tau dq), not torque divided by height. '
           'External work includes Fy dy + Fz dz plus the wheel moment contribution Mw dtheta6. '
           'A travel-weighted mean alone hides actuator angular ROM. Physical efficiency would require '
           'useful work divided by electrical energy with measured losses, duty and regenerative behavior; '
           'those inputs are absent.',9.2)

    # Pareto and expanded bound diagnostic
    r.section('Tradeoff / compactness','Torque has a geometry cost',
              'A boundary winner must be challenged before it can inform hardware selection.')
    front=a['pareto'];r.chart(48,646,499,247,[dict(x=[x['metrics']['size'] for x in front],
          y=[x['metrics']['peak'] for x in front],label='Verified DEFAULT-domain Pareto',scatter=True,color=BLUE),
          dict(x=[m['size']],y=[m['peak']],label='Compact scalar example',scatter=True,color=TEAL),
          dict(x=[575],y=[cases['expanded_peak']['profile']['metrics']['peak']],label='Expanded-domain example',scatter=True,color=GOLD)],
          'Summed link length L2 + L3 (mm)','Robust combined peak (Nm)',
          'Evaluated alternatives; dominance also uses full lateral excursion')
    ex=cases['expanded_peak'];em=ex['profile']['metrics']
    r.table(48,369,[153,173,173],['325 mm total / 285 useful','Compact central','Expanded-bound diagnostic'],[
        ('L2 / L3; qab','180 / 340; 1.775','180 / 395; 1.400'),
        ('alpha; tc (deg)','4.375; 159.810888','0; 169.525341'),
        ('Robust peak / RMS Nm',f'{fmt(m["peak"],3)} / {fmt(m["rms"],3)}',f'{fmt(em["peak"],3)} / {fmt(em["rms"],3)}'),
        ('Link sum / lateral drift mm',f'{fmt(m["size"],0)} / {fmt(m["drift"],3)}',f'{fmt(em["size"],0)} / {fmt(em["drift"],3)}'),
        ('Ground / assumed hip gap mm',f'{fmt(m["minClearance"],3)} / {fmt(m["minHipRimGap"],3)}',f'{fmt(em["minClearance"],3)} / {fmt(em["minHipRimGap"],3)}')],8,31)
    r.text(48,175,'Expanding L3 to 500 mm (step40; 1,350 coarse geometries; three local passes) improves '
           'peak by 14.3%, but adds 55 mm link sum and 75.4 mm drift. L3=395 is interior; '
           'L2=180 and qab=1.4 still reach their lower bounds. Unknown moving masses, stiffness and '
           'strength can reverse this preference.',9)
    r.text(48,98,f'The default-domain Pareto run retained {len(front)} nondominated verified alternatives '
           f'after {a["pareto_search"]["evaluations"]} evaluations. It compares the selected peak score, '
           'link sum and drift across the evaluated population. Neither method proves a continuum-wide '
           'or global hardware optimum.',8.3,GRAY)

    # 8 - All nine passive fits
    r.section('Springs / conditional fit','Nine geometries, one load case',
              'Supported hub C; chassis pitch fixed; physical masses total 10 kg; no damping.')
    fits=p['spring_comparisons'];rows=[]
    for i,f in enumerate(fits):
        rows.append((f'{i+1}. {names[f["topology"]]}',fmt(f['stiffness_N_mm'],3),fmt(f['preload_N'],2),
                     fmt(f['physical_free_length_mm'],2),fmt(f['stroke_mm'],2),fmt(f['peak_force_N'],2),fmt(f['residual_rms_Nm'],3)))
    r.table(48,657,[124,55,66,66,63,67,58],['Topology','Rate<br/>N/mm','Installed<br/>load N','Free<br/>mm','Stroke<br/>mm','Peak<br/>load N','Residual<br/>RMS Nm'],rows,7.5,31)
    r.chart(48,291,499,163,[dict(x=list(range(1,10)),y=[f['residual_rms_Nm'] for f in fits],
          label='Static fit residual',scatter=True,color=TEAL)],'Topology ID (table order)',
          'RMS torque (Nm)','Passive fit comparison')
    r.text(48,107,'Rates fit 81 uniformly spaced suspension-angle samples, not the later motion-time RMS. '
           'All fit constraints are ideal: nonnegative rate, correct unilateral force signs and positive '
           'physical free/coil lengths. Chassis-direct free length reaches its 1,000 mm fit bound. '
           'Coil force ratings, solid height and packaging remain unverified.',8.2,GRAY)

    # 9 - Actual anchor/tangent schematics
    r.section('Spring figures / force sites','Applied forces at actual sites',
              'Common useful midpoint pose; illustration uses the fixed-A translated frame.')
    q=(p['travel']['q_start']+p['travel']['q_end'])/2;pc=p['config'];aa=math.radians(pc['alpha'])
    t3=math.radians(pc['phi0'])+(math.pi-q)*(pc['qab']-1)
    rot=lambda v:(math.cos(aa)*v[0]+math.sin(aa)*v[1],-math.sin(aa)*v[0]+math.cos(aa)*v[1])
    bb=rot((-pc['L2']/1000*math.cos(q),-pc['L2']/1000*math.sin(q)))
    cc0=rot((-pc['L3']/1000*math.cos(t3),-pc['L3']/1000*math.sin(t3)));cc=(bb[0]+cc0[0],bb[1]+cc0[1])
    for i,check in enumerate(p['pymunk_topology_checks']):
        column=i%3;row=i//3;x0=48+column*171;y0=660-row*179
        r.c.setFillColor(PALE);r.c.roundRect(x0,y0-163,157,163,5,fill=1,stroke=0)
        r.text(x0+9,y0-9,f'{i+1}. {names[check["topology"]]}',8,NAVY,width=139,bold=True)
        points=[(0.,0.),bb,cc]+[tuple(x['world']) for x in check['actual_force_sites']]
        xmin=min(x[0] for x in points);xmax=max(x[0] for x in points)
        ymin=min(x[1] for x in points);ymax=max(x[1] for x in points)
        scale=min(128/max(.1,xmax-xmin),105/max(.1,ymax-ymin))
        mapping=lambda pt:(x0+14+(pt[0]-xmin)*scale,y0-140+(pt[1]-ymin)*scale)
        A=mapping((0,0));B=mapping(bb);C=mapping(cc)
        r.c.setStrokeColor(TEAL);r.c.setLineWidth(3);r.c.line(*A,*B)
        r.c.setStrokeColor(GOLD);r.c.line(*B,*C)
        sites=check['actual_force_sites'];S=[mapping(tuple(st['world'])) for st in sites]
        r.c.setStrokeColor(RED);r.c.setLineWidth(1.5);r.c.setDash(3,2);r.c.line(*S[0],*S[1]);r.c.setDash()
        for st,point in zip(sites,S):
            dr=st['direction'];r.arrow(point,(point[0]+dr[0]*22,point[1]+dr[1]*22),RED,1)
            r.c.setFillColor(RED);r.c.circle(*point,2,fill=1,stroke=0)
        for label,point in [('A',A),('B',B),('C',C)]:r.text(point[0]+3,point[1]+5,label,6,GRAY,width=15)
    r.text(48,90,'Red dashed spans and arrows show actual point-force directions used in the model. '
           'Pulley examples use ideal payout/tangent forces, not an added spring at the contact patch. '
           'All nine held-pose force-site virtual-work checks pass. Shapes are planar geometry, not a manufacturing drawing.',8.3,GRAY)

    # 10 - Signed complete bidirectional dynamics
    r.section('Motion / both directions','One second each way',
              'C held fixed: compression lowers the chassis; reverse extension raises it.')
    for y,key,label,unit,col in [(650,'tau_motor_Nm','Signed joint-equivalent torque','Torque (Nm)',TEAL),
                                (442,'motor_speed_rad_s','Signed joint angular speed','Speed (rad/s)',BLUE),
                                (234,'motor_accel_rad_s2','Signed joint angular acceleration','Acceleration (rad/s2)',GOLD)]:
        r.chart(48,y,499,159,[cycle(key,label,col)],'Cycle time (s); compression 0-1, raising 1-2',unit,label)
    r.text(48,75,'Full 2 s undamped out-and-back cycle; no dwell. Reported extrema/RMS use 201 points per '
           'direction; plots use a retained 101-point complete cycle. Reduction N=1 and eta=1.',7.6,GRAY)

    # 11 - Coil and speed sensitivity
    r.section('Spring / motor sizing','A spring is a torque profile',
              'Selected hip bellcrank: real anchor span and passive Hooke tension; zero damping.')
    r.chart(48,650,245,210,[cycle('spring_force_N','Coil load',TEAL)],'Cycle time (s)','Coil load (N)','Load over both directions')
    r.chart(302,650,245,210,[cycle('spring_coil_length_mm','Coil length',GOLD)],'Cycle time (s)','Physical coil length (mm)','Actual coil travel')
    r.text(48,420,f'Rate {fmt(s["stiffness_N_mm"],6)} N/mm; installed preload {fmt(s["preload_N"],3)} N; '
           f'free length {fmt(s["physical_free_length_mm"],3)} mm; stroke {fmt(s["stroke_mm"],3)} mm; '
           f'peak load {fmt(s["peak_force_N"],3)} N. Arm 80 mm at 135 deg; chassis mount (120, 50) mm. '
           'These mounts are illustrative, not packaging-approved.',9)
    rows=[]
    for t in p['time_sensitivity']:
        tm=t['metrics'];rows.append((fmt(t['duration_s'],1),fmt(tm['torque_peak_abs'],3),fmt(tm['torque_rms'],3),
                                    fmt(tm['speed_peak_abs'],3),fmt(tm['accel_peak_abs'],3)))
    r.table(48,332,[100,100,100,99,100],['Time each<br/>direction s','Peak<br/>Nm','Time RMS<br/>Nm','Peak speed<br/>rad/s','Peak accel<br/>rad/s2'],rows,8,34)
    r.text(48,178,'Motor conversion is a declared assumption',11,NAVY,bold=True)
    r.text(48,154,'For joint coordinate factor a (hip a=1; relative knee a=-qab): '
           'omega_motor=N*a*qdot; alpha_motor=N*a*qddot; tau_motor=tau_q/(a*N*eta). '
           f'An illustrative hip N=10, eta=0.85 gives {fmt(cm["torque_peak_abs"]/8.5,3)} Nm peak, '
           f'{fmt(cm["torque_rms"]/8.5,3)} Nm RMS and {fmt(cm["speed_peak_abs"]*10,3)} rad/s peak speed. '
           f'That is {fmt(cm["speed_peak_abs"]*10*60/(2*math.pi),1)} rpm and {fmt(cm["accel_peak_abs"]*10,3)} rad/s2. '
           'This calculation omits unknown reflected motor/gear inertia and is not a purchased motor rating.',9)
    r.text(48,80,'A symmetric undamped return preserves torque magnitude, reverses speed, and changes mechanical '
           'power sign. Efficiency is a conservative /eta torque convention; electrical regeneration and heating are unresolved.',8,GRAY)

    # 12 - Held impact stress, not multiplied dynamics
    r.section('Load envelope / held geometry','3g and 4g mean TOTAL support',
              'Requested 4g net upward acceleration instead means 5g support. Keep both interpretations explicit.')
    impacts=p['impact_cases']['cases'];lines=[]
    for mass,col in [(10,TEAL),(11.25,GOLD)]:
        rr=[x for x in impacts if x['corner_mass_kg']==mass]
        lines.append(dict(x=[x['total_support_factor_g'] for x in rr],y=[x['motor_peak_abs_Nm'] for x in rr],label=f'{mass:g} kg corner',color=col))
    r.chart(48,638,499,241,lines,'TOTAL support factor (g multiples)','Peak joint torque (Nm)',
            'Equivalent inertial stress; 1g-fitted spring unchanged',ylim=(0,205))
    rows=[]
    for factor in [1,3,3.5,4,5]:
        c10=next(x for x in impacts if x['corner_mass_kg']==10 and x['total_support_factor_g']==factor)
        c11=next(x for x in impacts if x['corner_mass_kg']==11.25 and x['total_support_factor_g']==factor)
        rows.append((fmt(factor,1),fmt(c10['total_support_force_N'],2),fmt(c10['motor_peak_abs_Nm'],3),
                     fmt(c11['total_support_force_N'],2),fmt(c11['motor_peak_abs_Nm'],3)))
    r.table(48,368,[91,102,102,102,102],['Total factor','10 kg<br/>support N','10 kg<br/>peak Nm','11.25 kg<br/>support N','11.25 kg<br/>peak Nm'],rows,8,30)
    r.text(48,163,'This is a held-pose stress sensitivity: add equivalent downward inertial load '
           '(factor-1)*corner_mass*g at chassis A. Ordinary gravity appears once; no second multiplication '
           'of the one-second trajectory inertia occurs. The spring remains fitted for the nominal case.',9.2)
    r.text(48,97,'Zero damping stores and returns energy. These stress values do not integrate an impact, '
           'predict peak compression, select a shock waveform or establish dissipation. Contact sharing '
           'and remaining travel can dominate the actual response.',8.3,GRAY)

    # 13 - Energy/available-stroke reasoning from the curated source
    r.section('Impact / why stroke matters','A g limit needs an event',
              'Analytical energy illustration; not a prediction of the generalized nonlinear spring.')
    delta=[20+i for i in range(81)];r.chart(48,633,499,244,[dict(x=delta,y=[1+2*100/x for x in delta],
       label='Undamped linear spring peak',color=RED),dict(x=delta,y=[1+100/x for x in delta],
       label='Ideal constant-force mean',color=TEAL)],'Available compression stroke (mm)',
       'TOTAL support / static weight','Equivalent 100 mm drop; initial spring preload mg')
    r.table(48,354,[166,166,167],['Available stroke','Constant-force mean','Linear-spring peak'],[
        ('20 mm','6g','11g'),('50 mm','3g','5g'),('66.7 mm','about 2.5g','about 4g')],8.5,32)
    r.text(48,212,'<font name="Courier-Bold">h = v^2/(2g)<br/>n_mean = 1 + h/delta<br/>'
           'n_peak = 1 + 2h/delta</font><br/>For h=100 mm, v=1.401 m/s. '
           'A geometric 20 mm end buffer is not a declaration of compliant impact travel. Pick a ride pose '
           'and evaluate the real spring-energy rise and compression reserve.',9.2)
    r.text(48,104,'Unequal support sensitivity: at 45 kg whole-robot mass and only two supporting legs, '
           'equal sharing would be 22.5 kg per leg: 220.73 N at 1g, 662.18 N at 3g, 882.90 N at 4g. '
           'This is a load-sharing assumption, not an integrated two-contact scenario or a proven maximum.',8.3,GRAY)

    # 14 - Actual independent evidence and overlay
    r.section('Verification / numerical scope','Actual engine, independent math',
              'Constraint stepping observes motor impulse; analytical torque is used only for comparison.')
    fine=p['pymunk_validation']['refinement'][-1];rr=fine['trace']
    r.chart(48,645,499,199,[dict(x=[x['theta2_deg'] for x in rr],y=[x['analytical_tau_abs_Nm'] for x in rr],label='Independent |tau_q|',color=TEAL),
      dict(x=[x['theta2_deg'] for x in rr],y=[x['pymunk_tau_abs_Nm'] for x in rr],label='Pymunk impulse/dt',color=GOLD,dash=True)],
      'theta2 (degrees)','|Torque| (Nm)','Hip bellcrank, one-second compression, fine step')
    rows=[]
    for check in p['all_nine_dynamic_checks']:
        co,fi=check['refinement'][0],check['refinement'][-1]
        rows.append((names[check['topology']],fmt(co['rms_torque_error_Nm'],4),fmt(fi['rms_torque_error_Nm'],4),
                     fmt(fi['max_torque_error_Nm'],4),'PASS' if check['passed'] else 'FAIL'))
    r.table(48,417,[155,91,91,91,71],['Topology','2 ms RMS<br/>error Nm','1 ms RMS<br/>error Nm','1 ms peak<br/>error Nm','Check'],rows,7.6,23)
    r.text(48,170,'Original solver: 3,853 kinematics + 16,044 statics + 29,863 global-peak assertions. '
           'New analytical suite: 13 tests; physical suite: 12 tests, including old Andy geometry/law '
           'cross-checks. All nine full dynamic checks, selected reverse motion and held-site virtual work pass.',8.4)
    r.text(48,121,'Earlier source-app verification (development evidence): 85 JavaScript and 34 existing '
           'Python tests; full/embedded Edge checks, both directions and nine held checks pass. '
           'Source-app launcher lifecycles passed; this does not require a new Motion Lab integration.',7.8,GRAY)
    r.text(48,82,'Pymunk motor impulse is a magnitude: torque sign is independent analytical telemetry. '
           'No pose resets occur after initialization. Canonical robot physics is NOT APPLICABLE to this '
           'isolated member app; there is no hardware validation, soil, tire rolling or 3D collision proof.',7.6,GRAY)

    # 15 - Parameters, source map and reproducibility
    r.section('Reproduction / provenance','Keep the evidence with the model',
              'Standalone PDF and offline static HTML are the delivery; no new tool integration is required.')
    rows=[('Central geometry','L2/L3 180/340; ra/rb 106.5/60; rc/rd/re/rf 35; rw 200 mm'),
          ('Angles / travel','alpha 4.375; beta 13.5; phi0 0; theta2 100-159.810888 deg; reserves20+20 mm'),
          ('Physical mass allocation','m1 8.30; m2/m3 .35/.35; m5 .10; m6 .90 kg; total 10.0'),
          ('Upper mass sensitivity','m1 9.55; same moving assembly; total 11.25 kg'),
          ('Fixture / trajectory','C fully anchored; pitch held; 1 s quintic each direction; damping 0'),
          ('Spring / transmission','Hip bellcrank / direct / extension; arm80 mm at135 deg; mount(120,50) mm'),
          ('Actual engine check','Pymunk Space.step; 800 iterations; dt 2 and 1 ms; ideal pivots/gears'),
          ('Motor reporting','Hip coordinate; N=1 eta=1 primary values; conditional N10/.85 example'),
          ('Verified app environment','Windows11 Home26200; Python3.13.12; Node22.23.3; Pymunk7.3.0'),
          ('Numerics / report pins','NumPy2.5.3; SciPy1.18.1; npm10.9.9; ReportLab4.4.9; pypdf6.10.0')]
    r.table(48,661,[128,371],['Recorded input','Value / interpretation'],rows,7.8,24)
    r.text(48,379,'Regenerate and recompute',11,NAVY,bold=True)
    r.text(48,354,'From the app root (optional dependencies: requirements-report.txt):<br/><font name="Courier-Bold">python scripts/build_design_report.py<br/>'
           'node --test tests/design-study.test.js<br/>python -m unittest -v test_generalized_leg<br/>'
           'python scripts/verify_generalized_leg.py</font><br/>'
           'PDF generation uses ReportLab and pypdf. Numerical recomputation uses the documented '
           'app environment. The report data records exact configurations, scenario policies, profiles, '
           'source SHA256 fingerprints and base revision 6c74cfd.',8.8)
    r.text(48,247,'Primary sources and repository map',11,NAVY,bold=True)
    r.text(48,224,'Jonathan immutable <b>leg-solver/v1-kinematics.html</b>, '
           '<b>v2-quasi-static.html</b> and <b>v2-model.md</b>; Andy <b>docs/link-sizing.md</b>, '
           '<b>generalized-leg-math.md</b>, <b>generalized-leg-study.md</b>, '
           '<b>generalized-leg-physics.md</b> and <b>impact-load-envelope.md</b>. '
           'Background: <link href="https://modernrobotics.northwestern.edu/chapters/chapter5/" color="#3267A5">'
           'Modern Robotics statics</link>; <link href="https://pymunk.readthedocs.io/en/latest/pymunk.constraints.html" '
           'color="#3267A5">Pymunk constraints</link>; <link href="https://www.maxongroup.com/medias/sys_master/8815460712478.pdf" '
           'color="#3267A5">maxon RMS sizing</link>; <link href="https://www.sdp-si.com/D820/PDFS/Technical-Section.pdf" '
           'color="#3267A5">SDP/SI belts</link>. Mechanism-specific results are computed repository evidence.',8.7)
    r.text(48,124,'Unresolved hardware inputs',11,NAVY,bold=True)
    r.text(48,101,'Measured masses/inertias and spring preload; tooth pitch/wrap/tension; contact friction; '
           'coil force/solid-height/fatigue limits; 3D shafts/chassis/clearance; reflected drivetrain inertia; '
           'motor efficiency, thermal duty and regeneration; measured impact event and contact sharing. '
           'The historical dual-rope design remains IMPOSSIBLE / rejected and is excluded.',8.2,GRAY)


if __name__=='__main__':
    main()
