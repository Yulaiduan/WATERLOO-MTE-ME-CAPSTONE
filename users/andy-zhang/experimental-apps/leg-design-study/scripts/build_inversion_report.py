"""Create a separate offline HTML and vector PDF for alpha-zero path searches.

Run: .venv/Scripts/python.exe scripts/build_inversion_report.py
Inputs: retained inversion-path-results.json and inversion-engine-checks.json;
mm, degrees, Nm, radians and explicitly labelled numerical errors.
Outputs: inversion-paths.html and docs/inversion-path-report.pdf. ReportLab and
pypdf are pinned in requirements-report.txt; no network assets or server needed.
Limits: presents selected deterministic kinematic evidence, not a fresh search,
hardware, collision/contact, motor/spring or canonical robot certification.
"""
from pathlib import Path
import json
import math
import html
import re
from reportlab.lib import colors
from build_design_report import Report, TEAL, BLUE, GOLD, RED, NAVY, GRAY, INK, W, H, fmt

APP=Path(__file__).resolve().parents[1]
PALETTE=['#087e76','#3267a5','#b17832','#9a5562','#7566a0']


class PathReport(Report):
    def __init__(self,target,data):
        super().__init__(target,data)
        self.c.setTitle('CAMEL | Alpha-zero angled paths and full inversion')

    def section(self,*args):
        super().section(*args)
        self.c.setFillColor(colors.white);self.c.rect(46,24,450,21,fill=1,stroke=0)
        self.text(48,37,'2026-10-14 | Alpha-zero path study | Base 865b5f1 | Experimental',7,GRAY)


def get(data,key):
    for field in ['selected','examples','practical']:
        for c in data[field]:
            if c['id']==key or key in c.get('aliases',[]):return c
    raise KeyError(key)


def path_lines(cases,full=False,relative=False):
    rows=[]
    for i,c in enumerate(cases):
        samples=c['full_samples'] if full else c['samples']
        x=[v['x_mm'] for v in samples];z=[v['z_mm'] for v in samples]
        if relative:x=[v-x[0] for v in x];z=[v-z[0] for v in z]
        rows.append(dict(x=x,y=z,label=short(c),color=colors.HexColor(PALETTE[i%len(PALETTE)])))
    return rows


def short(c):
    p=c['config'];return f"{p['L2']:g}/{p['L3']:g}, r={p['qab']:.4g}"


def residual(c):
    rows=c['samples'];a,b=rows[0],rows[-1]
    dx,dz=b['x_mm']-a['x_mm'],b['z_mm']-a['z_mm'];length=math.hypot(dx,dz)
    return [((v['x_mm']-a['x_mm'])*dz-(v['z_mm']-a['z_mm'])*dx)/length for v in rows]


def chart_limits(lines,pw,ph):
    xs=[v for l in lines for v in l['x']];ys=[v for l in lines for v in l['y']]
    xmin,xmax=min(xs),max(xs);ymin,ymax=min(ys),max(ys)
    sx=max(xmax-xmin,1)*1.12;sy=max(ymax-ymin,1)*1.12
    sx=max(sx,sy*pw/ph);sy=sx*ph/pw
    xc,yc=(xmin+xmax)/2,(ymin+ymax)/2
    return (xc-sx/2,xc+sx/2),(yc-sy/2,yc+sy/2)


def pdf_paths(r,lines,y=652,h=360,disk=False):
    if disk:lines=lines+[dict(x=[-220,220],y=[0,0],label='',color=colors.white,scatter=True)]
    xl,yl=chart_limits(lines,442,h-57)
    r.chart(48,y,499,h,lines,'C_y (mm) - equal axis scale','C_z (mm)',xlim=xl,ylim=yl)
    if disk:
        scale=442/(xl[1]-xl[0]);px=48+47+(0-xl[0])*scale;py=y-h+37+(0-yl[0])*scale
        r.c.setStrokeColor(RED);r.c.setLineWidth(1);r.c.setDash(3,2)
        r.c.circle(px,py,220*scale,stroke=1,fill=0);r.c.setDash()
        r.c.setFillColor(RED);r.c.circle(px,py,2,fill=1,stroke=0)


def render_pdf(d,e):
    target=APP/'docs/inversion-path-report.pdf';r=PathReport(target,d)
    p=get(d,d['recommended_id']);m=p['metrics'];best=get(d,'equal_325')
    phase=get(d,'phase_near_equal_12p5');strict=get(d,'transition_equal_325')
    count=d['search']['total_geometry_window_evaluations']
    r.section('Decision / requested zero mounting angle','Angled branches, mirrored inversion',
              'Pulley ratios and nearly equal links searched from the screenshot; alpha fixed at zero.')
    r.box(48,653,157,88,'Windows evaluated',f'{count/1e6:.2f} million','Two distinct window families')
    r.box(218,653,157,88,'Practical branch','12.02 degrees','350/350 mm; 7:4 guide')
    r.box(388,653,157,88,'Maximum bow','9.66 mm','2.91% of its endpoint chord')
    r.text(48,536,'The strict requested combination is not attained: with alpha=0 and the original '
           'assembly phase phi0=0, a normal-to-inverted path has a vertical tangent at the fold. '
           'A symmetric full stroke has a vertical chord. Ratio and link-length changes can produce '
           'a useful angled suspension branch, but its inverted branch tilts the opposite way.',11)
    r.table(48,416,[174,325],['Requirement / interpretation','Finding'],[
       ('10-15 deg normal working path','Many candidates; straightness and tangent spread vary'),
       ('Same tilted line through full inversion','Impossible under fixed alpha=phi0=0 ideal equations'),
       ('Near-equal links + coplanar 200 mm wheel','Every searched full inversion fails projected hip clearance'),
       ('Pulley indexing allowed as a relaxation','phi0=-25 deg, guide 2 gives a true 12.5 deg line; fold collision remains')],8.6,37)
    r.text(48,226,'Practical example: 325 mm total vertical capacity with 20 mm at each end gives '
           '285 mm usable. Its 9.66 mm bow is acceptable only if that approximately 3% deviation suits '
           'the design. It fails the stricter illustrative 2% preference. The straightest tested branch '
           'uses longer links near the 450 mm search boundary.',10)
    r.text(48,105,'This report preserves the earlier study and Motion Lab tooling. Fully invertible here '
           'means continuous ideal guide motion from below to above the hip; it is not a demonstrated '
           'ground flip or physical wheel/chassis clearance. Dual-rope remains IMPOSSIBLE / rejected.',8.2,GRAY)

    r.section('Exact model / why the restriction matters','The fold tangent stays vertical',
              'Jonathan variables retained: q=theta2, guide r=ra/rb, link lengths a=L2 and b=L3.')
    r.text(48,665,'With t=q-pi and k=r-1, alpha=phi0=0:<br/><br/>'
           '<font name="Courier-Bold">x = a cos(t) - b cos(k t)<br/>z = a sin(t) + b sin(k t)<br/>'
           'x(-t) = x(t);  z(-t) = -z(t)<br/>C(pi) = (a-b,0)<br/>C\'(pi) = (0,a+k b)</font>',12)
    r.text(48,476,'The horizontal coordinate is even and height is odd. Upper/lower inversion branches '
           'mirror across the horizontal hip plane; their local tilts have opposite signs. At the fold '
           'the tangent is vertical, with a finite positive Jacobian for the searched ratios. A chord '
           'tilted 10-15 degrees over an asymmetric interval does not remove that vertical tangent.',10.2)
    r.table(48,358,[166,333],['Exact constraint','Consequence'],[
        ('r=2, a=b, phase 0','The only exact nondegenerate straight path is vertical'),
        ('r not 2','Distinct angular frequencies produce curvature'),
        ('r=1+sqrt(a/b)','Cancels central quadratic lateral curvature; centre remains vertical'),
        ('beta=13.5 deg','Defines contact/load orientation; it does not rotate the wheel-centre path')],8.5,34)
    r.text(48,184,'Centre series:<br/><font name="Courier">x = (a-b) + (b k^2-a)t^2/2 + O(t^4)<br/>'
           'z = (a+b k)t - (a+b k^3)t^3/6 + O(t^5)</font><br/>'
           'Changing ratio can make the centre locally straighter, but cannot create a nonzero central tilt.',9.3)
    r.text(48,83,'Proof scope: constant positive links and ideal fixed-ratio guide. Variable-ratio transmissions '
           'or an additional linkage are different architectures and were not silently substituted.',8,GRAY)

    r.section('Search / what was enumerated','A broad reproducible sweep',
              'Search counts describe geometry-plus-window combinations, not hardware designs or global proof.')
    domains=d['search']['domains'];counts=d['search']['counts']
    r.table(48,660,[178,321],['Variable','Domain / policy'],[
       ('Lower-link L3','200-450 mm in 10 mm steps, plus 275/325/375/425'),
       ('Link ratio L2/L3','0.85-1.15 in 0.005 steps; equal/5%/10%/15% tiers'),
       ('Guide ratio ra/rb','1.4-2.6 in 0.0025 steps, plus exact 5/3; rb 60 mm'),
       ('Mounting / assembly phase','alpha 0, phi0 0 in the strict search'),
       ('Normal start / total','theta2=100/105/110/115/120; total 300/325/350 mm'),
       ('Crossing-window allocation','Above-hip fractions 20/35/50/65/80%; exact heights'),
       ('Pose verification','33 coarse poses; finalists 2001 dense poses; TLS uniform height'),
       ('Screenshot values retained','rw 200; drive radii 35; beta 13.5; Fy=Fz100; m1=10, others 0')],8.3,31)
    r.table(48,357,[249,250],['Count','Observed result'],[
       ('Normal-window combinations',f"{counts['normal_grid']:,}"),
       ('Crossing-window combinations',f"{counts['inversion_grid']:,}"),
       ('Normal 10-15 deg + branch-clearance passes',f"{counts['normal_clearance_pass']:,}"),
       ('Coarse normal <=2% bow, <=15 deg tangent span',f"{counts['normal_quality_pass']:,}"),
       ('Crossing-window candidates meeting both limits',str(counts['transition_quality_pass'])),
       ('Full coplanar inversion clearance passes','0, also excluded by the exact fold-distance argument')],8.4,28)
    r.text(48,150,'Full height-monotone inversion is checked across theta2=100-260 degrees. Normal branch '
           'candidates retain positive vertical Jacobian and projected wheel/hip margin >=20 mm. '
           'The 20 mm geometric reserves are not spring compression. Ranking minimizes maximum '
           'orthogonal chord error, then tangent spread, then link sum. These are bounded grid winners.',8.9)
    r.text(48,74,'Floating grid coordinates are rounded before deduplication. Quality counts use 33 coarse poses. Source, domains, metrics '
           'and selected curves are retained in inversion-path-results.json; raw runs stay ignored.',7.9,GRAY)

    r.section('Normal suspension / equal and near-equal','What the branch search found',
              'All rows below have alpha=phi0=0. Tilt is the endpoint chord, not every local tangent.')
    normal=[x for x in d['selected'] if x['kind']=='normal_branch' and x['id']!='original_scale_325']
    rows=[]
    for c in normal:
        a=c['config'];b=c['metrics']
        rows.append((f"{a['L2']:g}/{a['L3']:g}",fmt(a['qab'],4),fmt(b['vertical_mm'],0),
            fmt(b['chord_tilt_deg'],2),fmt(b['max_chord_error_mm'],2),fmt(b['tangent_spread_deg'],2),
            fmt(b['wheel_hip_margin_mm'],1)))
    r.table(48,660,[90,59,62,70,72,73,73],['L2/L3<br/>mm','Guide','Total<br/>mm','Chord<br/>deg','Bow<br/>mm','Tangent<br/>span deg','Wheel/hip<br/>margin mm'],rows,7.3,27)
    r.text(48,212,'The straightest branches sit near the maximum link-length bound and the lower 10-degree '
           'angle target. Increasing size narrows the joint-angle window for the same 325 mm height, '
           'reducing bow. This does not establish a structural, mass or motor optimum. The 350/350 mm '
           'example preserves equal links and uses a simple 7:4 ratio at greater curvature.',9.4)
    r.text(48,107,'Link closeness uses |L2/L3-1|. A 5% link mismatch improves the best 325 mm bow only '
           'slightly in this domain. Full inversion clearance fails for every row, even when its normal '
           'working branch passes the projected filter.',8.3,GRAY)

    r.section('Practical comparison / simple guide ratio','Equal links with a 7:4 guide',
              'Illustrative compromise: 350 mm links, zero mounting angle, zero assembly phase.')
    r.table(48,660,[178,321],['Parameter / requirement','Recorded value'],[
       ('L2/L3; ra/rb','350/350 mm; 105/60 mm -> 7:4'),
       ('Physical theta2 interval',f"115 to {fmt(p['config']['tc'],6)} degrees"),
       ('Total / usable height','325 / 285 mm; 20 mm reserved at either end'),
       ('Endpoint chord / TLS angle',f"{fmt(m['chord_tilt_deg'],4)} /{fmt(m['tls_tilt_deg'],4)} degrees"),
       ('Maximum orthogonal chord bow',f"{fmt(m['max_chord_error_mm'],4)} mm ({fmt(m['chord_error_percent'],3)}%)"),
       ('Local tangent range',f"{fmt(m['tangent_min_deg'],4)} to {fmt(m['tangent_max_deg'],4)} degrees"),
       ('Minimum normal branch wheel/hip margin',f"{fmt(m['wheel_hip_margin_mm'],4)} mm"),
       ('Full 100-260 degree sweep','Normal and inverted heights, finite vertical Jacobian; fold radius 0')],8.4,31)
    r.chart(48,340,499,188,[dict(x=[v['z_mm']-p['samples'][0]['z_mm'] for v in p['samples']],y=residual(p),label='350/350;7:4',color=TEAL)],
            'Vertical travel from branch start (mm)','Chord error (mm)','Bow relative to the endpoint chord')
    r.text(48,113,'This candidate conditionally suits a design that accepts about 10 mm bow over 325 mm. '
           'It does not meet the illustrative 2% straightness preference, and the local tangent is not '
           'confined to 10-15 degrees. Full inversion is only an ideal linkage result until axial '
           'wheel/chassis routing is defined.',8.5,GRAY)

    r.section('Sensitivity / ratio tunes angle and bow','Ratio alone introduces curvature',
              'Equal 350 mm links, start 115 degrees, exact 325 mm vertical stroke; alpha=phi0=0.')
    sweep=d['guide_sweep'];xs=[v['qab'] for v in sweep]
    r.chart(48,657,499,220,[dict(x=xs,y=[v['metrics']['chord_tilt_deg'] for v in sweep],label='Chord orientation',color=BLUE)],
            'Guide ratio ra/rb','Chord tilt (degrees)')
    r.chart(48,374,499,220,[dict(x=xs,y=[v['metrics']['max_chord_error_mm'] for v in sweep],label='Maximum chord bow',color=GOLD)],
            'Guide ratio ra/rb','Maximum bow (mm)',ylim=(0,max(v['metrics']['max_chord_error_mm'] for v in sweep)*1.1))
    r.text(48,108,'Moving away from 2:1 changes the wheel-centre path orientation over a selected branch '
           'and introduces bow. The exact equal-link 2:1, phase-zero case is vertical. Different '
           'qcd/qef wheel-drive ratios do not change the wheel-centre locus; only qab affects this '
           'guide geometry. Keep nominal wheel spin K distinct from path straightness.',8.6,GRAY)

    r.section('Full inversion / the two branches','The inverted branch leans oppositely',
              'World wheel-centre coordinates, equal axis scales; red 220 mm disk is projected exclusion.')
    pdf_paths(r,path_lines([p,get(d,'screenshot_250_5over3')],full=True),y=653,h=412,disk=True)
    r.text(48,216,'The normal 350/350 branch leans 12.02 degrees by its endpoint chord. Its mirrored '
           'inverted suspension branch leans -12.02 degrees. The complete symmetric sweep has a '
           'vertical chord, with a vertical tangent at the folded position. A single angled line is '
           'not maintained through the inversion.',10)
    r.text(48,128,'All phi0=0 full strokes pass C=(L2-L3,0). For equal links, wheel centre C coincides '
           'with hip A. With <=15% mismatch and L3<=450 mm, |L2-L3|<=67.5 mm, below the 220 mm '
           'projected exclusion. Axial separation could change physical clearance but is not specified.',8.9,RED)

    r.section('Misleading chord / finite crossing windows','A tilted chord can hide a large bow',
              '300-350 mm total inversion transitions also searched, with 20-80% above-hip allocation.')
    transitions=[c for c in d['selected'] if c['kind']=='inversion_transition']
    r.table(48,660,[126,65,84,79,78,67],['L2/L3 mm','Guide','Chord deg','Bow mm','Tangent span','Hip distance'],[
      (short(c).split(',')[0],fmt(c['config']['qab'],4),fmt(c['metrics']['chord_tilt_deg'],3),
       fmt(c['metrics']['max_chord_error_mm'],3),fmt(c['metrics']['tangent_spread_deg'],3),fmt(c['metrics']['minimum_hip_distance_mm'],1)) for c in transitions],8,36)
    r.chart(48,485,499,240,[dict(x=[v['z_mm']-c['samples'][0]['z_mm'] for v in c['samples']],y=residual(c),label=short(c),color=colors.HexColor(PALETTE[i])) for i,c in enumerate(transitions)],
       'Vertical travel from transition start (mm)','Chord error (mm)','Endpoint angle 10-15 deg; large internal deviation')
    r.text(48,209,'The best sampled 325 mm crossing examples bow about 24 mm, or 7.25% of chord, '
           'and have roughly 33.5-degree tangent variation. None of the crossing candidates meets '
           'both <=2% bow and <=15-degree tangent spread. The midpoint vertical tangent prevents '
           'an everywhere 10-15-degree path, even if the endpoints appear promising.',9.5)
    r.text(48,115,'A finite normal suspension window and a normal-to-inverted window are distinct tasks. '
           'The full inversion envelope of 350 mm links has approximately 1296 mm vertical extent; '
           'its selected suspension branch has 325 mm total. Do not call both325 mm travel.',8.5,GRAY)

    r.section('Explicit relaxation / keep alpha zero','Pulley indexing can tilt a true line',
              'Supplementary alternative: phi0 is allowed to change; it is not the strict phase-zero search.')
    r.text(48,665,'For equal links L and guide 2:<br/><font name="Courier-Bold">'
           'C = 2L sin(t-phi0/2) [-sin(phi0/2), cos(phi0/2)]</font><br/><br/>'
           'Thus phi0=-20 to -30 degrees produces a true 10-15-degree line with alpha=0. '
           'This sets the lower-link assembly/belt phase. Mounting alpha instead rotates both '
           'links and their frame; the wheel-centre line can coincide while the knee path differs.',10.2)
    r.table(48,482,[115,95,98,96,95],['Case','Vertical mm','Chord deg','Bow mm','Tangent range'],[
        ('250/250,2:1,-25deg','325.998','12.500','0.000','12.5 to 12.5'),
        ('275/250,2:1,-25deg',fmt(phase['metrics']['vertical_mm'],3),fmt(phase['metrics']['chord_tilt_deg'],3),fmt(phase['metrics']['max_chord_error_mm'],3),'10.762 to 12.859')],8,42)
    pdf_paths(r,path_lines([get(d,'phase_equal_12p5'),phase]),y=337,h=196)
    r.text(48,112,'The phase alternative relaxes the request for the offset to arise only from ratio and '
           'length. It still folds to zero hip distance for equal links, or 25 mm for 275/250. '
           'It therefore does not solve coplanar 200 mm wheel clearance. It is a candidate only '
           'with explicit indexing and unresolved axial packaging.',8.6,RED)

    r.section('Diagnostic / inherited load convention','Joint torque is a separate requirement',
              'Original prescribed Fy=Fz=100 N; m1 at fixed A, other masses zero; no fitted spring.')
    compare=[get(d,'screenshot_250_5over3'),p,best]
    r.chart(48,651,499,285,[dict(x=[v['q_deg'] for v in c['samples']],y=[v['tau_hip_Nm'] for v in c['samples']],label=short(c),color=colors.HexColor(PALETTE[i])) for i,c in enumerate(compare)],
       'theta2 (degrees)','Signed direct hip torque (Nm)')
    r.text(48,310,'The displayed torque follows the same fixed-A virtual-work load case as the original '
           'screenshot. It is not a standing 10 kg-per-leg dynamics prediction or a motor rating. '
           'An above-hip contact force is only a prescribed algebraic load, not proof of ground contact.',10)
    r.text(48,198,'Coordinate relation:<br/><font name="Courier-Bold">'
           'd(relative knee)/dq = -qab<br/>tau_knee = -tau_hip/qab</font><br/>'
           'A smaller torque in another coordinate accompanies greater angular speed. The guide '
           'ratio is separate from any motor reduction; ideal work is conserved.',10)
    r.text(48,86,'This follow-up selects path geometry. Existing spring/motor and impact estimates '
           'remain in the earlier report and do not silently transfer to these longer or fully inverted legs.',8.3,GRAY)

    r.section('Verification / actual constrained stepping','Math and engine checks',
              'Independent equations, dense rechecks and actual Pymunk motion; physical collision excluded.')
    r.text(48,657,'Independent review recomputed all 24 displayed cases from the original V2 equations '
           'at 20,001 poses. Endpoint classifications agree; maximum chord-error difference from '
           'retained 2001-pose checks is 0.0000044 mm. Existing model parity covers 8,784 comparisons '
           'with maximum 3.98e-13 mm/Nm discrepancy. Five new numerical tests cover derivatives, '
           'parity/fold identities, phase lines and exact un-clipped search capacity.',10)
    rows=[]
    for c in e['cases']:
        co,mid,fi=c['refinement']
        rows.append((short(get(d,c['id'])) + ('; phase -25' if c['id'].startswith('phase_') else ''),
            fmt(co['max_path_error_mm'],4),fmt(mid['max_path_error_mm'],4),fmt(fi['max_path_error_mm'],4),'PASS' if c['passed'] else 'FAIL'))
    r.table(48,466,[181,79,79,79,81],['Actual engine case','2ms error<br/>mm','1ms error<br/>mm','0.5ms error<br/>mm','Fine check'],rows,7.8,33)
    r.text(48,234,'Engine fixture: positive recorded masses, hip fixed, zero gravity/contact, '
           '2-second quintic angular sweep, 800 solver iterations. Only initial poses are assigned; '
           'Space.step and real motor/pivot/gear constraints generate motion. Wheel position is '
           'compared with independent V2 coordinates at the actual femur angle. Coarse 2 ms runs '
           'exceed the 0.1 mm path tolerance in all five cases; 1 and 0.5 ms pass and converge.',9.4)
    r.text(48,111,'A first zero-buffer height-driven check hit endpoint floating-point bracketing; '
           'this independent angular fixture avoids that inverse-height dependency. No old solver '
           'or tolerance was weakened. Self-collision/ground contacts are absent, so these passes '
           'do not negate the rejected projected-clearance result.',8.3,GRAY)

    r.section('Continuation / sources and decisions','Choose which constraint may change',
              'The strict outcome and the practical alternatives stay separate from hardware acceptance.')
    r.text(48,662,'If approximate mirrored branches are acceptable, begin with equal 350 mm links '
           'and a 7:4 guide, while reserving about 10 mm path bow. If straightness dominates size, '
           'compare the 450 mm-bound candidates. If one same-direction 10-15-degree line through '
           'inversion is essential, the phase-zero fixed-ratio architecture must change.',11)
    r.text(48,542,'Allowing assembly phase offers an exact tilted line at alpha 0. Axial packaging '
           'must separately keep a 200 mm wheel clear of the hip/chassis during folding. Neither '
           'a promising plot nor a collision-disabled engine run establishes that clearance.',10.2)
    r.text(48,429,'Reproduction from the standalone report folder:<br/><font name="Courier-Bold">'
           'python inversion_search.py<br/>python -m unittest -v test_inversion_search<br/>'
           'python scripts/verify_inversion_geometry.py<br/>python scripts/build_inversion_report.py<br/>'
           'node scripts/verify_inversion_report.cjs</font>',9.5)
    r.text(48,277,'Primary project sources: Jonathan vsl-solver/v1/v1-kinematics.html, '
           'v2-quasi-static.html and v2-model.md; this app model.js and generalized_leg.py; '
           'new inversion_search.py, retained results and engine checks; docs/inversion-path-study.md. '
           'Read the revision map for the source base 865b5f1 and later publication.',9.5)
    r.text(48,176,'Unresolved: axial offsets, chassis shape, shaft/gear/belt wrap and tooth counts, '
           'load path and spring routing through inversion, measured masses, structural limits and '
           'ground-contact behavior. The earlier dual-rope design remains IMPOSSIBLE/rejected; '
           'this report neither reuses nor revives it. No canonical robot validation is claimed.',9.2,GRAY)
    r.c.save()
    return target


def svg_chart(lines,xlabel,ylabel,equal=False,disk=False):
    w,h=900,460;left,right,bottom,top=78,24,54,24;pw,ph=w-left-right,h-top-bottom
    xs=[v for l in lines for v in l['x']];ys=[v for l in lines for v in l['y']]
    if disk:xs+= [-220,220];ys+=[0]
    if equal:xl,yl=chart_limits([dict(x=xs,y=ys)],pw,ph)
    else:
        xl=(min(xs),max(xs));yl=(min(ys),max(ys));xp=max(xl[1]-xl[0],1)*.04;yp=max(yl[1]-yl[0],1)*.1
        xl=(xl[0]-xp,xl[1]+xp);yl=(yl[0]-yp,yl[1]+yp)
        if ylabel=='Maximum chord bow (mm)':yl=(0,yl[1])
    xx=lambda v:left+(v-xl[0])/(xl[1]-xl[0])*pw
    yy=lambda v:h-bottom-(v-yl[0])/(yl[1]-yl[0])*ph
    esc=html.escape
    parts=[f'<svg class="chart" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(ylabel)} versus {esc(xlabel)}">']
    for i in range(5):
        a=xl[0]+(xl[1]-xl[0])*i/4;b=yl[0]+(yl[1]-yl[0])*i/4
        parts+=[f'<line class="grid" x1="{left}" x2="{w-right}" y1="{yy(b):.2f}" y2="{yy(b):.2f}"/>',
          f'<text class="tick" x="{left-10}" y="{yy(b)+4:.2f}" text-anchor="end">{b:.1f}</text>',
          f'<text class="tick" x="{xx(a):.2f}" y="{h-bottom+20}" text-anchor="middle">{a:.1f}</text>']
    if disk:parts.append(f'<circle cx="{xx(0):.3f}" cy="{yy(0):.3f}" r="{220*pw/(xl[1]-xl[0]):.3f}" fill="none" stroke="#af5256" stroke-dasharray="6 4"/><text class="tick" x="{xx(0)+8:.3f}" y="{yy(0)-8:.3f}">A</text>')
    for i,l in enumerate(lines):
        color=l.get('html_color',PALETTE[i%len(PALETTE)])
        points=' '.join(f'{xx(x):.3f},{yy(y):.3f}' for x,y in zip(l['x'],l['y']))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"><title>{esc(l["label"])}</title></polyline>')
    parts.append(f'<text class="axis" x="{left+pw/2}" y="{h-8}" text-anchor="middle">{esc(xlabel)}</text><text class="axis" transform="translate(17 {top+ph/2}) rotate(-90)" text-anchor="middle">{esc(ylabel)}</text></svg>')
    parts.append('<div class="legend">'+''.join(f'<span><i style="background:{l.get("html_color",PALETTE[i%len(PALETTE)])}"></i>{esc(l["label"])}</span>' for i,l in enumerate(lines))+'</div>')
    return ''.join(parts)


def table(headers,rows,id=''):
    return f'<div class="table-wrap"><table id="{id}"><thead><tr>'+''.join(f'<th>{html.escape(str(x))}</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{html.escape(str(x))}</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'


def render_html(d,e):
    original=(APP/'index.html').read_text(encoding='utf-8')
    css=re.search(r'<style>([\s\S]*?)</style>',original).group(1)
    css+='\n@media print{.top,.toc,.print-button{display:none}.reader{display:block;padding:0}.section{border:0;padding:15px;break-inside:auto}figure{break-inside:avoid}.chart{max-height:95mm}details{display:none}.hero{display:block;padding:0}body{background:white}h1{font-size:28px}tr{break-inside:avoid}}'
    p=get(d,d['recommended_id']);m=p['metrics'];phase=get(d,'phase_near_equal_12p5');count=d['search']['total_geometry_window_evaluations']
    sections=[]
    def section(id,kicker,title,body):sections.append((id,title,f'<section id="{id}" class="section"><div class="section-title"><span>{len(sections)+1:02}</span><div><p class="eyebrow">{kicker}</p><h2>{title}</h2></div></div>{body}</section>'))
    def fig(title,lines,x,y,**kwargs):return f'<figure><figcaption>{title}</figcaption>'+svg_chart(lines,x,y,**kwargs)+'</figure>'
    section('decision','ZERO MOUNTING ANGLE','A useful branch; a strict full-inversion limit',
      f'<p class="lead">Searched <b>{count:,}</b> geometry-plus-window combinations with <b>α=0°</b>, the original assembly phase <b>φ₀=0°</b>, and equal or nearly equal links.</p>'
      '<div class="metrics"><div class="metric"><span>PRACTICAL LINKS</span><strong>350 /350 <em>mm</em></strong><small>Equal upper and lower</small></div><div class="metric"><span>GUIDE RATIO</span><strong>7:4</strong><small>ra/rb=105/60 mm</small></div><div class="metric"><span>BRANCH CHORD</span><strong>12.02 <em>°</em></strong><small>From global vertical</small></div><div class="metric"><span>MAXIMUM BOW</span><strong>9.66 <em>mm</em></strong><small>2.91% of chord</small></div></div>'
      '<p>The branch gives <b>325 mm total / 285 mm usable</b> with 20 mm end reserves. It is a practical candidate only if roughly 10 mm bow is acceptable; it fails the illustrative 2% straightness preference.</p>'
      '<div class="note amber"><b>Strict result:</b> ratio and link length alone do not create the same 10–15° line through full inversion at φ₀=0. The normal branch and inverted branch mirror, and the fold tangent is vertical.</div>'
      '<div class="note rejected"><b>Projected packaging:</b> every searched full inversion fails clearance for a coplanar 200 mm wheel. Ideal inversion and actual wheel/chassis clearance are different checks.</div>')
    section('proof','EXACT EQUATIONS','Why the full path mirrors',
      '<p>Jonathan’s coordinate convention is retained: q=θ₂, r=qₐᵦ=ra/rb, a=L₂, b=L₃; let t=q−π and k=r−1.</p>'
      '<pre>x = a cos(t) − b cos(k t)\nz = a sin(t) + b sin(k t)\nx(−t)=x(t); z(−t)=−z(t)\nC(q=π)=(a−b,0)\nC′(q=π)=(0,a+k b)</pre>'
      '<p>A symmetric full inversion has a vertical chord; at the folded pose the tangent is also vertical. Distinct angular frequencies prevent an exact tilted line when r≠2. The exact equal-link 2:1 case is straight and vertical.</p>'
      '<p>The ratio r=1+√(a/b) cancels the central quadratic lateral curvature and makes a locally straighter <b>vertical</b> transition. β=13.5° is a load/contact convention and does not rotate C’s path.</p>')
    dom=d['search']['domains'];cnt=d['search']['counts']
    section('search','BROAD DETERMINISTIC SCREEN','What was searched and measured',
      table(['Variable','Domain / policy'],[['L₃','200–450 mm step 10, plus 275/325/375/425'],['L₂/L₃','0.85–1.15 step 0.005; equal/5%/10%/15% tiers'],['Guide ra/rb','1.4–2.6 step 0.0025, plus exact 5/3; rb 60 mm'],['α /φ₀','0° /0° throughout strict search'],['Normal start /total','θ₂ 100/105/110/115/120°; total 300/325/350 mm'],['Crossing windows','20/35/50/65/80% of total above the hip'],['Geometry samples','33 coarse; 2001 dense finalist; TLS uniform vertical height']], 'search-domains')+
      table(['Outcome','Count'],[['Normal windows',f"{cnt['normal_grid']:,}"],['Crossing windows',f"{cnt['inversion_grid']:,}"],['Normal angle+clearance passes',f"{cnt['normal_clearance_pass']:,}"],['Coarse normal ≤2% bow, ≤15° tangent spread',f"{cnt['normal_quality_pass']:,}"],['Crossing windows meeting both',cnt['transition_quality_pass']],['Full coplanar inversion clearance passes',0]],'search-counts')+
      '<p>Endpoint angles solve the exact requested height; no silent endpoint clipping. Normal branch leaders pass positive vertical Jacobian, 20 mm projected hip margin, and a full 100–260° monotone-height check. Ranking minimizes maximum orthogonal chord deviation, then tangent spread, then link sum. Quality counts use 33 coarse poses; selected metrics use 2001. These are bounded tested candidates.</p>')
    rows=[]
    for c in d['selected']:
      a,b=c['config'],c['metrics']
      rows.append([c['id'],f"{a['L2']:g}/{a['L3']:g}",fmt(a['qab'],4),fmt(b['vertical_mm'],0),fmt(b['chord_tilt_deg'],3),fmt(b['max_chord_error_mm'],3),fmt(b['tangent_spread_deg'],3),fmt(b['wheel_hip_margin_mm'],2), 'YES' if c['full_inversion']['min_vertical_jacobian_mm_rad']>=5 else 'NO'])
    section('candidates','EQUAL AND NEAR-EQUAL LENGTHS','The selected alternatives',
      table(['Family','L₂/L₃ mm','Guide','Total mm','Chord°','Bow mm','Tangent span°','Branch wheel/hip margin mm','Full ideal height invertible'],rows,'candidate-table')+
      '<p>The straightest branches are near the 450 mm length limit and the lower 10° tilt boundary. Those limits are active; this is not a proven hardware optimum. Longer links reduce angular change for a fixed height, trading size for lower bow. The original_scale_325 and transition rows are diagnostic: they fail branch clearance or other requested filters. The full-height column records ideal guide motion; all full coplanar wheel-clearance checks fail.</p>')
    section('practical','SIMPLE RATIO COMPROMISE','350/350 mm links with a 7:4 guide',
      table(['Measure','Value'],[['θ₂ physical interval',f"115–{p['config']['tc']:.6f}°"],['Total /usable','325 / 285 mm'],['Chord /TLS tilt',f"{m['chord_tilt_deg']:.6f} /{m['tls_tilt_deg']:.6f}°"],['Maximum bow',f"{m['max_chord_error_mm']:.6f} mm ({m['chord_error_percent']:.3f}%)"],['Local tangent range',f"{m['tangent_min_deg']:.6f}–{m['tangent_max_deg']:.6f}°"],['Normal branch wheel/hip margin',f"{m['wheel_hip_margin_mm']:.6f} mm"]],'practical-parameters')+
      fig('Bow relative to the endpoint chord',[dict(x=[v['z_mm']-p['samples'][0]['z_mm'] for v in p['samples']],y=residual(p),label='350/350 mm,7:4')],'Vertical travel from branch start (mm)','Orthogonal chord error (mm)')+
      '<div class="note amber">12.02° describes the endpoint chord. The tangent varies 6.27–20.47°; it does not remain inside 10–15°. This approximate candidate requires accepting about 10 mm bow and unresolved full-inversion axial packaging.</div>')
    comparisons=[get(d,'scale300_equal_325'),p,get(d,'equal_325')]
    section('profiles','INDIVIDUAL PATHS','Straightness changes with scale and ratio',
      fig('Normal path shapes, aligned at their starting wheel centres',path_lines(comparisons,relative=True),'Relative C_y (mm), equal scale','Relative C_z (mm)',equal=True)+
      fig('Individual local tangent angles',[dict(x=[v['z_mm']-c['samples'][0]['z_mm'] for v in c['samples']],y=[v['tangent_deg'] for v in c['samples']],label=short(c)) for c in comparisons],'Vertical travel (mm)','Local tangent from vertical (degrees)')+
      '<p>Equal axis scale preserves actual path angles. Start-normalized paths compare shape and do not show absolute chassis clearance.</p>')
    sweep=d['guide_sweep']
    section('ratios','GUIDE SENSITIVITY','A pulley ratio can tune the branch angle',
      fig('Equal 350 mm links, θ₂ start 115°, exact 325 mm height',[dict(x=[v['qab'] for v in sweep],y=[v['metrics']['chord_tilt_deg'] for v in sweep],label='Chord orientation')],'Guide ratio ra/rb','Chord tilt (degrees)')+
      fig('Curvature accompanies a changed ratio',[dict(x=[v['qab'] for v in sweep],y=[v['metrics']['max_chord_error_mm'] for v in sweep],label='Maximum bow')],'Guide ratio ra/rb','Maximum chord bow (mm)')+
      '<p>qcd/qef remain 1 as in the screenshot; their drive ratios affect wheel spin and loads, not the wheel-centre locus. K=0 is compatible with many guide ratios.</p>')
    fulls=[p,get(d,'screenshot_250_5over3')]
    transitions=[c for c in d['selected'] if c['kind']=='inversion_transition']
    section('inversion','BOTH SIDES OF THE HIP','The complete path and the fold',
      fig('Full ideal inversion; red 220 mm projected wheel-centre exclusion',path_lines(fulls,full=True),'World C_y (mm), equal scale','World C_z (mm)',equal=True,disk=True)+
      '<p>The mirrored normal/inverted working branches have opposite chord tilts. The full symmetric 100–260° sweep has zero chord tilt. For equal links C=A at the fold; near equality leaves |L₂−L₃|, at most 67.5 mm in this search, below 220 mm exclusion.</p>'+
      fig('Asymmetric 325 mm crossing windows can hide large internal bow',[dict(x=[v['z_mm']-c['samples'][0]['z_mm'] for v in c['samples']],y=residual(c),label=short(c)) for c in transitions],'Vertical travel (mm)','Orthogonal chord error (mm)')+
      '<p>The best crossing examples have roughly 24 mm bow (7.25% chord) and 33.5° tangent variation. No crossing window meets both straightness limits. Full inversion extent is about 1296 mm for 350 mm links; its selected suspension branch is 325 mm.</p>')
    section('phase','CLEARLY LABELLED RELAXATION','Indexing the lower link can produce a true tilted line',
      '<p>This keeps α=0 but permits φ₀ to change, so it relaxes the request for the angle to arise only from ratio and length.</p>'
      '<pre>For L₂=L₃=L and r=2:\nC=2L sin(t−φ₀/2)[−sin(φ₀/2), cos(φ₀/2)]</pre>'
      '<p>φ₀=−20…−30° gives an exact 10–15° line. This is a lower-link belt/assembly indexing choice; mounting α rotates both links and the frame. The knee path is different even when the wheel-centre line coincides.</p>'+
      table(['Geometry /phase','Height mm','Chord°','Bow mm','Tangent range°'],[['250/250,2:1,−25°','325.998','12.500','0.000','12.5–12.5'],['275/250,2:1,−25°',fmt(phase['metrics']['vertical_mm'],3),fmt(phase['metrics']['chord_tilt_deg'],3),fmt(phase['metrics']['max_chord_error_mm'],3),'10.762–12.859']],'phase-table')+
      fig('Phase alternative: true line versus thin near-equal curve',path_lines([get(d,'phase_equal_12p5'),phase]),'World C_y (mm), equal scale','World C_z (mm)',equal=True)+
      '<div class="note rejected">This improves path straightness but does not solve clearance: equal links still cross the hip, and 275/250 links leave only 25 mm minimum distance.</div>')
    section('torque','ORIGINAL PRESCRIBED LOAD','Torque coordinate stays explicit',
      fig('Original 100 N horizontal /100 N vertical algebraic load, fixed A',[dict(x=[v['q_deg'] for v in c['samples']],y=[v['tau_hip_Nm'] for v in c['samples']],label=short(c)) for c in comparisons],'θ₂ (degrees)','Signed direct hip torque (Nm)')+
      '<p>Relative-knee torque is −τhip/qab and relative-knee speed is −qab times hip speed. Motor gearing is separate. This is a fixed-A diagnostic with massless moving links, not a standing-load, spring-assisted or motor rating estimate. Above-hip contact feasibility is not assumed.</p>')
    erows=[]
    for c in e['cases']:
      a,b,f=c['refinement'];erows.append([short(get(d,c['id'])) + ('; phase -25' if c['id'].startswith('phase_') else ''),fmt(a['max_path_error_mm'],5),fmt(b['max_path_error_mm'],5),fmt(f['max_path_error_mm'],5),'PASS' if c['passed'] else 'FAIL'])
    section('validation','INDEPENDENT EQUATIONS AND ACTUAL ENGINE','What has been checked',
      '<p>Independent V2 equations checked 24 displayed cases at 20,001 poses. Endpoint and inversion classifications agree; maximum chord-error sampling discrepancy is 0.0000044 mm. Original-model browser parity covered 8,784 comparisons with maximum 3.98×10⁻¹³ mm/Nm discrepancy. Five new numerical tests pass.</p>'+
      table(['Actual Pymunk case','2 ms path error mm','1 ms error mm','0.5 ms error mm','Fine check'],erows,'engine-table')+
      '<p>Actual Space.step drives a two-second angular sweep using real motor, pivot and gear constraints. Only initial poses are assigned. Wheel position is compared against independent geometry at the actual upper-link angle. Positive masses are explicit; gravity, contact and collision geometry are absent. All five 2 ms cases fail the 0.1 mm tolerance; 1 and 0.5 ms pass and converge.</p>'
      '<p>An initial zero-buffer height-driven attempt encountered endpoint bracketing roundoff. The independent angular fixture avoids that inverse-height dependency; the existing solver and tolerances are preserved.</p>'
      '<div class="note">These checks verify mathematical and ideal rigid-body consistency. They do not establish ground inversion, wheel/chassis clearance, spring routing, belt strength or hardware acceptance. The historical dual-rope design stays IMPOSSIBLE/rejected.</div>')
    section('reproduction','DOCUMENTED CHOICES AND NEXT INPUTS','Keep the report with its evidence',
      '<p>Use the simple 7:4 equal-link branch if roughly10 mm bow and mirrored inversion are acceptable. Use longer tested links if straightness dominates size. For the same 10–15° line through inversion, change an explicit design constraint: assembly phase, mounting, or linkage architecture. Resolve axial wheel/chassis packaging independently.</p>'
      '<pre>python inversion_search.py\npython -m unittest -v test_inversion_search\npython scripts/verify_inversion_geometry.py\npython scripts/build_inversion_report.py\nnode scripts/verify_inversion_report.cjs</pre>'
      '<div class="links"><a href="docs/inversion-path-report.pdf">Companion PDF</a><a href="docs/inversion-path-study.md">Design reasoning</a><a href="docs/inversion-path-results.json">Selected evidence</a><a href="docs/revisions.md">Revision map</a><a href="index.html">Earlier design report</a></div>'
      '<p>Sources are the repository’s Jonathan V1/V2 equations, this app’s mathematical/physical models, and the new retained search/verification scripts. Source base 865b5f1. Physical tooth counts, axial offsets, chassis shape, spring inversion routing, contact behavior and structural limits remain open.</p>')
    toc=''.join(f'<a href="#{id}">{i+1:02} {title}</a>' for i,(id,title,_) in enumerate(sections))
    payload=json.dumps(d,separators=(',',':'),ensure_ascii=False).replace('<','\\u003c')
    output='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'"><title>CAMEL · Alpha-zero angled paths</title><style>'+css+'</style></head><body><header class="top"><div class="brand">CAMEL <small>Design report 2 /October 2026</small></div><div class="top-actions"><a id="pdf-link" href="docs/inversion-path-report.pdf">PDF report ↗</a><button id="print-report" class="print-button">Print report</button></div></header><div class="hero"><div><p class="eyebrow">ALPHA ZERO · PULLEY RATIO & LINK GEOMETRY</p><h1>Angled paths &<br>full inversion.</h1><p>A separate offline study of equal and nearly equal legs. The practical branch candidates, exact restrictions and explicit phase relaxation are documented together.</p></div><div class="hero-box"><b>Offline report 2</b><span>2026-10-14 · source 865b5f1</span><span>26.46 million tested windows</span></div></div><main class="reader"><nav class="toc">'+toc+'<small>Static embedded figures.<br>No server or connection needed.</small></nav><article class="report">'+''.join(s[2] for s in sections)+'</article></main><footer class="footer">Experimental member study · α=0 · source 865b5f1 · no canonical robot certification</footer><script type="application/json" id="report-evidence">'+payload+'</script><script>document.getElementById("print-report").addEventListener("click",()=>window.print());</script></body></html>'
    (APP/'inversion-paths.html').write_bytes(output.encode())


def main():
    d=json.loads((APP/'docs/inversion-path-results.json').read_text(encoding='utf-8'))
    e=json.loads((APP/'docs/inversion-engine-checks.json').read_text(encoding='utf-8'))
    pdf=render_pdf(d,e);render_html(d,e)
    from pypdf import PdfReader
    reader=PdfReader(pdf)
    print(json.dumps(dict(pdf=pdf.name,pages=len(reader.pages),pdf_bytes=pdf.stat().st_size,
        html_bytes=(APP/'inversion-paths.html').stat().st_size,
        text_characters=sum(len(p.extract_text() or '') for p in reader.pages))))


if __name__=='__main__':main()
