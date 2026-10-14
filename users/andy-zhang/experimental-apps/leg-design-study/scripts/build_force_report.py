"""Typeset offline force/travel HTML and a vector PDF from retained evidence.

Run from app: .venv/Scripts/python.exe scripts/build_force_report.py
Inputs: force-travel-results, math-checks and engine-checks JSON; explicit
mm/deg/N/Nm/rad units. Outputs: force-travel.html, docs/force-travel-report.pdf.
Uses existing ReportLab helpers and pinned report dependencies. No search,
simulation or network runs during rendering. Limits: conditional ideal force
screening, not a hardware, impact, collision or canonical robot certification.
"""
from pathlib import Path
import json
import math
import re
import html
from reportlab.lib import colors
from build_design_report import Report, GRAY, NAVY, TEAL, fmt
from build_inversion_report import svg_chart, table, pdf_paths, PALETTE

APP=Path(__file__).resolve().parents[1]
LABELS={'rounded_equal320_9over5':'320/320, 9:5','reference_practical_equal350_7over4_start115':'350/350, 7:4',
 'equal_325_bow2':'425/425, 2% bow','rounded_indexed_equal300':'300/300, indexed',
 'refined_equal':'303/303, refined','refined_within5':'294/309, refined',
 'reference_equal_325':'450/450, earlier', 'equal_300_bow3':'300/300, 300 total',
 'equal_325_bow3':'310/310, 325 total','equal_350_bow3':'325/325, 350 total'}


def prose(text):
    """Normalize display spacing only; numerical evidence and identifiers stay intact."""
    text=re.sub(r'(?<=\d)(?=(?:mm|Nm|kg|ms|rad|degrees?|deg|g)\b)',' ',text)
    words='approximately|approximate|allowing|gives|chord|span|the|rounded|minimum|error|existing|same|extra|choose|or|with|use|keep|tighter|exact|unchanged|at|every|two|about|winner|date|step|ratio|adding|indexed|shifted|range|inside|all|andy|illustrative|strict|and|assumed|below|beyond|coplanar|cost|envelope|ideal|its|leaves|older|reaches|red|report|roughly|simultaneous|start|these|versus|vertical|a|is'
    text=re.sub(r'\b('+words+r')(?=\d)',r'\1 ',text,flags=re.I)
    for a,b in [('fullq','full q'),('withphi0','with phi0'),('withphase','with phase'),('indexingphi0','indexing phi0'),('mm9:5','mm, 9:5'),('mm7:4','mm, 7:4'),('mm2:1','mm, 2:1'),('ratio0','ratio 0')]:text=text.replace(a,b)
    return text


def get(d,key):return next(c for c in d['selected'] if c['id']==key)


def label(c):return LABELS.get(c['id'],c['id'])


def lines(cases,key,xkey='height_mm'):
    return [dict(x=[s[xkey] for s in c['force']['samples']],y=[s[key] for s in c['force']['samples']],
       label=label(c),color=colors.HexColor(PALETTE[i]),html_color=PALETTE[i]) for i,c in enumerate(cases)]


def paths(cases):
    return [dict(x=[s['x_mm']-c['samples'][0]['x_mm'] for s in c['samples']],
       y=[s['z_mm']-c['samples'][0]['z_mm'] for s in c['samples']],label=label(c),
       color=colors.HexColor(PALETTE[i]),html_color=PALETTE[i]) for i,c in enumerate(cases)]


def full_paths(cases):
    out=[]
    for i,c in enumerate(cases):
        p=c['config'];a,b=p['L2'],p['L3'];k=p['qab']-1;phi=p['phi0']*math.pi/180
        qs=[c['full_inversion']['bounds_deg'][0]+j/160*(c['full_inversion']['bounds_deg'][1]-c['full_inversion']['bounds_deg'][0]) for j in range(161)]
        ts=[q*math.pi/180-math.pi for q in qs]
        out.append(dict(x=[a*math.cos(t)-b*math.cos(phi-k*t) for t in ts],
          y=[a*math.sin(t)-b*math.sin(phi-k*t) for t in ts],label=label(c),
          color=colors.HexColor(PALETTE[i]),html_color=PALETTE[i]))
    return out


def shortlist(d):return [get(d,k) for k in ['rounded_equal320_9over5',
    'reference_practical_equal350_7over4_start115','equal_325_bow2','rounded_indexed_equal300']]


def short_rows(cases):
    return [[label(c),fmt(c['path']['chord_tilt_deg'],2),fmt(c['path']['max_chord_error_mm'],2),
      fmt(c['force']['min_force_per_hip_N_Nm'],3),fmt(c['force']['peak_45kg_hip_Nm'],2),
      fmt(c['force']['hip_ROM_deg'],2)] for c in cases]


class ForceReport(Report):
    def text(self,x,y,message,*args,**kwargs):return super().text(x,y,prose(message),*args,**kwargs)

    def section(self,*args):
        super().section(*args)
        self.c.setFillColor(colors.white);self.c.rect(46,24,450,21,fill=1,stroke=0)
        self.text(48,37,'2026-10-14 | Force/travel study | Base d1596e5 | Experimental',7,GRAY)


def render_pdf(d,e,v):
    target=APP/'docs/force-travel-report.pdf';r=ForceReport(target,d)
    r.c.setTitle('CAMEL | Force, travel and link length at alpha zero')
    picks=shortlist(d);primary=picks[0];indexed=picks[-1];f=primary['force'];p=primary['path']
    r.section('Recommendation / conditional design choice','Force and useful travel',
      'Alpha=0; 200 mm wheel radius; 325 mm total height including 20 mm buffers at each end.')
    r.box(48,653,157,87,'Rounded strict option','320 / 320 mm','9:5 guide, original phase zero')
    r.box(218,653,157,87,'Usable height','285 mm','325 total, two 20 mm reserves')
    r.box(388,653,157,87,'Worst force gain','1.908 N/Nm','Direct hip input; vertical load')
    r.text(48,539,'Start with equal 320 mm links and guide ra/rb=108/60=1.8 if the original '
      'assembly phase must remain zero. It has a 10.31 degree chord, 9.18 mm maximum bow '
      'and 57.83 Nm unassisted static hip peak for an equally loaded 45 kg robot. '
      'Normal-branch hip distance stays at least 241.22 mm, 21.22 mm beyond the assumed '
      '220 mm wheel-plus-gap exclusion. Local tangents range5.05-19.30 degrees;10.31 is the chord. '
      'This is a rounded compromise, not the lowest mathematical torque.',10)
    r.table(48,410,[149,59,59,78,78,76],['Example','Chord<br/>deg','Bow<br/>mm','Worst F/T<br/>N/Nm','Hip peak<br/>Nm,45kg','Hip ROM<br/>deg'],short_rows(picks),8,33)
    r.text(48,231,'The indexed 300/300 mm option keeps alpha=0, but changes fixed lower-link '
      'assembly phase to -25 degrees and uses a 2:1 guide. It produces an exact 12.5 degree line '
      'with similar static peak (57.26 Nm), a wider usable hip range (44.27 degrees) and greater '
      'speed demand. It is a separately labelled relaxation of the original ratio/length-only request.',10)
    r.text(48,128,'All these legs have an ideal continuous height-inverse through the hip. None '
      'has demonstrated physical full inversion: a coplanar 200 mm wheel intersects the hip region '
      'at the fold. Axial/chassis packaging, belts, structure and real contact remain unresolved. '
      'Historical dual-rope stays IMPOSSIBLE / rejected.',9,GRAY)

    r.section('Metrics / what best force means','Torque is a transmission tradeoff',
      'q is direct hip-input theta2; Jz=dz/dq, in metres per radian.')
    r.text(48,660,'<font name="Courier-Bold">|tau_hip| = Fz Jz<br/>guaranteed Fz / |tau_hip| = 1 / max(Jz)<br/>'
      'RMS_z(tau) = Fz sqrt(integral(Jz^2 dz) / H)<br/>W = integral(tau dq) = Fz H<br/>'
      'tau_relative-knee = -tau_hip / r<br/>relative-knee speed = -r hip speed</font>',12)
    r.text(48,492,'Use the worst force per input Nm for a peak-limited actuator, and height-weighted '
      'RMS torque as a secondary measure when moving at constant vertical speed. Angle-average torque '
      'is Fz H / ROM: a larger joint sweep can lower it without improving energy efficiency. '
      'RMS requires time weighting once the real cycle includes acceleration or dwell.',10.2)
    r.chart(48,381,499,225,lines(picks[:3],'force_per_hip_N_Nm'),'Usable vertical height (mm)','Vertical force / hip Nm (N/Nm)')
    r.text(48,126,'The ideal 285 mm lift needs 27.96-31.45 J per leg for 40-45 kg four-leg '
      'static loading, regardless of these ratios. Lower torque trades for a larger/faster joint '
      'motion. The knee coordinate changes torque and speed together; an additional motor gearbox '
      'is a separate mapping. No electrical efficiency or thermal rating is inferred.',9.2,GRAY)

    r.section('Search / reproducibility and active bounds','Grid first, local refinement second',
      '11,478,060 strict combinations; 11,070 separate fixed-indexing combinations.')
    r.table(48,660,[172,327],['Input / constraint','Declared policy'],[
      ('L3 / L2:L3','200-450 mm; 30 scales. Ratio0.85-1.15 step0.01; equal/5/10/15% tiers'),
      ('Guide / start','r1.4-2.6 step0.005 plus exact5/3; q100-140 step2.5; end<=175'),
      ('Travel / reserves','300/325/350 mm total; actual inverse-height 20 mm trim at both ends'),
      ('Path quality','Chord10-15 deg; bow<=3%chord; tangent span<=15 deg. 2% compared separately'),
      ('Feasibility','Normal |C|>=220 mm; fullq100-260 Jz>=5 mm/rad; L2>60(r+1)'),
      ('Ranking / sampling','Minimum useful-stroke maxJz, then size; 51 coarse /2001 finalist poses'),
      ('Second method','SLSQP seeded by grid; two325mm refinements, 401-pose constraints; dense check')],8.4,40)
    refined=[get(d,'refined_equal'),get(d,'refined_within5')]
    r.table(48,318,[139,96,91,91,82],['Locally refined','Links mm','Guide','Hip peak Nm','Worst F/T'],[
      [label(c),f"{c['config']['L2']:.2f}/{c['config']['L3']:.2f}",fmt(c['config']['qab'],6),
       fmt(c['force']['peak_45kg_hip_Nm'],3),fmt(c['force']['min_force_per_hip_N_Nm'],4)] for c in refined],8,36)
    r.text(48,185,'The equal local optimum is approximately303.46/303.46 mm; allowing5% mismatch '
      'gives293.78/309.24 mm. Both sit at chord10 degrees, tangent span15 degrees and the220 mm '
      'clearance boundary. Their torque improvements are conditional and leave no surplus beyond '
      'that assumed gap. The near-equal result also reaches its 5% mismatch bound. The rounded320 mm '
      'case adds useful packaging allowance. Local convergence '
      'and bounded grids do not establish a global or hardware optimum.',9.5)
    r.text(48,80,'Quality counts use coarse samples. All published candidate acceptance and profile metrics '
      'are densely rechecked. The first evidence export rejected NumPy boolean serialization; explicit '
      'scalar conversion fixed export and the complete search was rerun.',8,GRAY)

    r.section('Travel / capacity versus leverage','300, 325 or 350 mm total?',
      'Equal-link phase-zero grid winners under the same3%bow /15degree-span policy.')
    travel=[get(d,k) for k in ['equal_300_bow3','equal_325_bow3','equal_350_bow3']]
    r.table(48,660,[88,74,77,79,91,90],['L2=L3<br/>mm','Guide','Total /<br/>usable mm','Hip ROM<br/>deg','Hip peak<br/>Nm,45kg','Worst F/T<br/>N/Nm'],[
      [fmt(c['config']['L2'],0),fmt(c['config']['qab'],3),f"{c['total_mm']:g}/{c['force']['usable_mm']:.0f}",
      fmt(c['force']['hip_ROM_deg'],2),fmt(c['force']['peak_45kg_hip_Nm'],2),fmt(c['force']['min_force_per_hip_N_Nm'],3)] for c in travel],8.1,38)
    r.chart(48,460,499,290,lines(travel,'torque_45kg_Nm'),'Usable vertical height (mm)','Unassisted static hip torque (Nm)')
    r.text(48,130,'300 mm total gives260 mm usable and already exceeds the owner\'s approximate250 mm '
      'preferred useful height. Choose325 mm as a middle study point, or350 mm if the extra50 mm '
      'useful height compared with300 is valuable. Extra travel requires more size or joint motion '
      'and generally weakens worst-case force leverage here. Buffers are geometric end reserves, '
      'not a measured impact stroke or spring deflection allowance.',10)

    r.section('Individual curves / same travel and load','The force-oriented shortlist',
      'All four shown cases: 325 mm total /285 mm usable, Fy=0, 11.25 kg equivalent static corner load.')
    r.chart(48,640,499,275,lines(picks,'torque_45kg_Nm'),'Usable vertical height (mm)','Direct hip holding torque magnitude (Nm)')
    r.table(48,317,[154,84,88,86,87],['Design','40kg /1g<br/>hip peak','45kg /1g<br/>hip peak','45kg /3g<br/>hip peak','45kg /4g<br/>hip peak'],[
      [label(c),fmt(c['force']['peak_40kg_hip_Nm'],1),fmt(c['force']['peak_45kg_hip_Nm'],1),
       fmt(3*c['force']['peak_45kg_hip_Nm'],1),fmt(c['force']['peak_4g_45kg_hip_Nm'],1)] for c in picks],8,37)
    r.text(48,97,'These numbers are unassisted equivalent-load holding torques. 3g/4g scales the '
      'total supported force, rather than adding3g/4g on top of gravity. They do not include '
      'motor/gear inertia, link masses, transient impacts or spring assistance. Do not transfer '
      'the earlier unequal-leg spring or6.449 Nm dynamic example to these geometries.',9.2,GRAY)

    r.section('Indexing / separate design relaxation','An exact tilted line at alpha zero',
      'Fixed lower-link indexing phi0=-25 degrees, guide r=2; no ratio change or reindexing during movement.')
    r.text(48,659,'For equal links and d=phi0/2:<br/><font name="Courier-Bold">C=2L sin(q-pi-d) [-sin(d),cos(d)]</font><br/>'
      'The wheel centre stays on an exact12.5 degree line. Original phase zero cannot achieve this same '
      'tilted line through inversion because x is even and z odd aboutq180 degrees.',10.5)
    pdf_paths(r,paths([primary,indexed]),y=540,h=295)
    r.table(48,238,[167,166,166],['Parameter','Strict rounded','Indexed rounded'],[
      ('Links / guide','320/320 mm;9:5','300/300 mm;2:1'),
      ('Total angle window',f"110-{primary['config']['tc']:.3f} deg",f"87.5-{indexed['config']['tc']:.3f} deg"),
      ('Useful hip range',f"{f['hip_ROM_deg']:.2f} deg",f"{indexed['force']['hip_ROM_deg']:.2f} deg"),
      ('Useful peak at0.25m/s',f"{f['constant_vertical_speed_0p25m_s_peak_hip_rad_s']:.3f} rad/s",f"{indexed['force']['constant_vertical_speed_0p25m_s_peak_hip_rad_s']:.3f} rad/s")],8,28)
    r.text(48,90,'Indexed285 mm is closer to clearance; rounded300 mm adds margin. '
      'This family needs the shifted87.5-247.5 degree envelope, outside the old V2 validator. '
      'Original app validators and live presets are unchanged.',8,GRAY)

    r.section('Control / force, velocity and side load','Check more than average torque',
      'Illustrative constant vertical speed 0.25 m/s; not a smooth-start actuator specification.')
    speed=lines([primary,indexed],'Jz_m_rad')
    for line in speed:line['y']=[.25/x for x in line['y']]
    r.chart(48,641,499,260,speed,'Usable vertical height (mm)','Hip speed at0.25m/s (rad/s)')
    side=[]
    for ratio in [-.3,0,.3]:
        rows=primary['force']['samples'];side.append(dict(x=[s['height_mm'] for s in rows],
          y=[abs(110.3625*(s['Jz_m_rad']+ratio*s['Jx_m_rad'])) for s in rows],
          label=f'Fy/Fz={ratio:+.1f}',color=[TEAL,colors.HexColor(PALETTE[1]),colors.HexColor(PALETTE[2])][len(side)]))
    r.chart(48,318,499,195,side,'Usable vertical height (mm)','Hip torque with side load (Nm)')
    r.text(48,88,'General endpoint load uses tau=-(Fy Jx+Fz Jz). A side load can raise or reduce '
      'the instantaneous demand; the pure-vertical ranking is not universal. Smooth motion also '
      'needs qddot=zddot/Jz-(dJz/dq)zdot^2/Jz^3. Actual acceleration/duty, moving masses, spring '
      'geometry, damping and impact/contact data are needed before selecting a motor.',8.8,GRAY)

    r.section('Inversion / mathematical and physical checks','Ideal invertibility is conditional',
      'Neither a positive Jacobian nor a collision-disabled Pymunk sweep proves wheel/chassis clearance.')
    pdf_paths(r,full_paths([primary,indexed]),y=648,h=345,disk=True)
    r.table(48,270,[174,103,111,111],['Actual Pymunk case','2ms error<br/>mm','1ms error<br/>mm','0.5ms error<br/>mm'],[
      [LABELS.get(c['id'],c['id']),*[fmt(a['max_path_error_mm'],5) for a in c['refinement']]] for c in e['cases']],8,35)
    r.text(48,119,'All three full angular sweeps pass the unchanged0.1 mm path/pin thresholds at '
      '1 and0.5 ms; every2 ms path result fails and is retained. At the fold, near-equal link '
      'distance is |L2-L3|, well below the220 mm exclusion. An axial stagger may change collision '
      'geometry, but its dimensions are unknown. The strict branch mirrors after inversion and '
      'has a vertical fold tangent; the indexed line keeps its tilt. These engine runs check '
      'positive-mass ideal constraints with no gravity, contact or collision shapes.',9.2,GRAY)

    r.section('Validation / sources and next decisions','Use the ranking as a design screen',
      'Preserve the old reports, models, Motion Lab illustrations and historical decisions.')
    r.table(48,657,[189,310],['Evidence','Result / boundary'],[
      ('Numerical tests','5 new force tests; existing5 inversion and12 generalized tests pass'),
      ('Original V2 + Andy statics',f"{v['scalar_comparisons']:,} scalar comparisons; max error{v['max_error_mm_Nm']:.2e} mm/Nm"),
      ('Actual constrained Pymunk','3 new full-sweep refinements; geometry only, no reset after initialization'),
      ('Independent math review','Force/work/knee mapping, analytic peaks and selected dense path checks'),
      ('Offline delivery','Static HTML with embedded SVG/JSON, local PDF, no server or connection'),
      ('Canonical / hardware','Not applicable /not certified; no strength, actual impact or packaging pass')],8.5,38)
    r.text(48,378,'Practical choice: use320/320 mm9:5 when fixed phase zero is required and9 mm bow '
      'is acceptable. Keep350/350 mm7:4 if a12 degree chord and existing example are preferred. '
      'Use425 mm tested links only if tighter2%bow dominates force and size. If fixed assembly '
      'indexing is allowed,300/300 mm2:1 withphi0=-25 gives the cleanest line, with a wider '
      'control/speed range. These are recommendations within this declared ideal domain.',10.3)
    r.text(48,251,'Next measure wheel/chassis axial separation and physical sweep clearance; agree '
      'accepted local tangent/bow limits, motor-shaft mapping and actual usable impact stroke. '
      'Then allocate measured moving masses, refit the chosen spring topology and run a smooth '
      'supported-chassis contact model. A different load cycle can change the best RMS design.',10)
    r.text(48,140,'Sources: Jonathan leg-solver V2 embedded solver/statics; existing Andy model.js and '
      'generalized_leg.py; retained force-travel search, tests, math and engine evidence. '
      'Commands and equations are in docs/force-travel-study.md. Base d1596e5; date2026-10-14. '
      'The screenshot\'s Fy=Fz=100 N case remains separate from this pure-vertical40-45 kg load '
      'comparison. No new motor/spring product or canonical geometry is published.',9.2,GRAY)
    r.c.save();return target


def render_html(d,e,v):
    css=re.search(r'<style>([\s\S]*?)</style>',(APP/'inversion-paths.html').read_text(encoding='utf-8')).group(1)
    picks=shortlist(d);primary=picks[0];indexed=picks[-1];sections=[]
    def sec(id,title,body):sections.append((id,title,f'<section class="section" id="{id}"><div class="section-title"><span>{len(sections)+1:02}</span><h2>{html.escape(title)}</h2></div>{prose(body)}</section>'))
    def fig(title,l,x,y,**kw):return '<figure><figcaption>'+html.escape(title)+'</figcaption>'+svg_chart(l,x,y,**kw)+'</figure>'
    sec('choice','Shorter links improve force leverage',
      '<p class="lead">For the strict <b>α=φ₀=0</b> design, start with <b>320/320 mm links and a 9:5 guide</b>. '
      'This rounded compromise gives <b>325 mm total /285 mm usable</b>, a10.31° chord and9.18 mm maximum bow.</p>'+
      table(['Example','Chord°','Bow mm','Worst vertical F/T N/Nm','Static hip peak Nm,45kg','Useful hip ROM°'],short_rows(picks),'shortlist')+
      '<p>320 mm links are a proposed compromise, not a global minimum. The equal-link grid winner is310 mm, '
      'and local refinement reaches303.46 mm at the clearance/path boundaries. Rounded320 mm leaves21.22 mm '
      'beyond the assumed220 mm exclusion on its <b>normal branch</b>. The older350 mm7:4 case remains a useful '
      'simple-ratio option.</p><div class="note rejected"><b>Physical inversion remains unresolved:</b> '
      'all these near-equal legs intersect the hip region with a coplanar200 mm wheel during full inversion. '
      'They are ideally height-invertible; axial/chassis packaging is still required.</div>')
    sections[-1]=(sections[-1][0],sections[-1][1],sections[-1][2].replace('</section>',
      '<p>The strict 320 mm figure is the <b>chord</b> tilt; local tangents range 5.05–19.30°. '
      'It does not keep every tangent inside 10–15°.</p></section>'))
    sec('metrics','Force metric, torque average and work',
      '<pre>|τhip| = Fz Jz; Jz=dz/dq in m/rad\nguaranteed Fz per hip Nm = 1/max(Jz)\nRMSheight(τ) = Fz √[∫Jz² dz/H]\nmeanangle(τ) = Fz H / ROM\nW = ∫τ dq = Fz H\nτrelative-knee = −τhip/r; knee speed = −r × hip speed</pre>'
      '<p>Minimize the worst useful-stroke Jacobian for force at a peak torque limit. Use height-weighted RMS '
      'for constant vertical speed without dwell, then actual <b>time-weighted</b> RMS for a real mission. '
      'Lower average torque can simply mean a larger angle sweep. All ideal285 mm lifts cost27.96–31.45 J '
      'per leg under these40–45 kg static loads. The geometry changes torque/speed, not ideal energy efficiency.</p>'+
      fig('Guaranteed leverage varies through each useful stroke',lines(picks[:3],'force_per_hip_N_Nm'),'Useful vertical height (mm)','Vertical force per hip Nm (N/Nm)'))
    sec('search','11.48 million strict windows and local refinement',
      table(['Domain /filter','Policy'],[['Strict enumerated combinations','11,478,060; invalid windows included'],['L₃ /L₂:L₃','200–450 mm,30 scales;0.85–1.15 step0.01'],['Guide /start','1.4–2.6 step0.005 plus exact5/3;100–140° step2.5'],['Total /reserves','300/325/350 mm;20 mm each end by inverse height'],['Path /clearance','10–15° chord,≤3%bow,≤15° tangent span; total-window |C|≥220 mm'],['Full inversion /guide','q100–260°, minimum Jz≥5 mm/rad; L₂>60(r+1)'],['Sampling /second method','51 coarse,2001 finalist; grid-seeded local SLSQP, dense final check'],['Separate indexed search','11,070 combinations, phase−25°,r2,L₃250–450step5, start87.5–130°']])+
      table(['Refined example','L₂/L₃ mm','Guide','Static hip peak Nm','Worst F/T N/Nm'],[[label(c),f"{c['config']['L2']:.3f}/{c['config']['L3']:.3f}",fmt(c['config']['qab'],6),fmt(c['force']['peak_45kg_hip_Nm'],3),fmt(c['force']['min_force_per_hip_N_Nm'],4)] for c in [get(d,'refined_equal'),get(d,'refined_within5')]])+
      '<p>Both refinements touch the10°chord,15°tangent-span and220 mm clearance limits. Allowing5% link '
      'mismatch gives only a modest additional torque gain and reaches its5%bound. These are bounded/local results. Strict2%bow '
      'requires much longer tested links. Counts are coarse; published selected acceptance uses dense metrics.</p>')
    travel=[get(d,k) for k in ['equal_300_bow3','equal_325_bow3','equal_350_bow3']]
    sec('travel','Choose how much travel is actually needed',
      table(['Equal links mm','Guide','Total /useful mm','Useful ROM°','45kg static hip peak Nm'],[[fmt(c['config']['L2'],0),fmt(c['config']['qab'],3),f"{c['total_mm']:g}/{c['force']['usable_mm']:.0f}",fmt(c['force']['hip_ROM_deg'],2),fmt(c['force']['peak_45kg_hip_Nm'],2)] for c in travel])+
      fig('Equal-link grid winners: more height versus required torque',lines(travel,'torque_45kg_Nm'),'Useful vertical height (mm)','Direct hip torque magnitude (Nm)')+
      '<p>300 mm total gives260 mm useful, already beyond the approximate250 mm target. 325 mm is the '
      'middle study point;350 gives310 mm useful. Extra capacity is valuable only if it earns its '
      'size/ROM/torque cost. The20 mm end buffers remain geometric assumptions, not tested impact reserves.</p>')
    sec('curves','Individual torque curves under one load',
      fig('All examples:325 mm total,285 useful;110.3625 N pure vertical load',lines(picks,'torque_45kg_Nm'),'Useful vertical height (mm)','Unassisted direct hip torque (Nm)')+
      table(['Design','40kg1g peak Nm','45kg1g peak Nm','45kg3g peak Nm','45kg4g peak Nm'],[[label(c),fmt(c['force']['peak_40kg_hip_Nm'],1),fmt(c['force']['peak_45kg_hip_Nm'],1),fmt(3*c['force']['peak_45kg_hip_Nm'],1),fmt(c['force']['peak_4g_45kg_hip_Nm'],1)] for c in picks])+
      '<p>Massless moving links isolate transmission geometry. Load is the equivalent supported force '
      'per corner, not the screenshot’s simultaneous100 N horizontal and100 N vertical diagnostic. '
      '3g/4g scales the total equivalent force; these are held-load sensitivities, not actual impacts '
      'or motor ratings. Springs and inertia are absent. The earlier spring/dynamic motor numbers '
      'do not transfer to these new designs.</p>')
    sec('indexed','If fixed indexing is allowed, use an exact line',
      '<p><b>300/300 mm,r2,φ₀=−25°,α=0</b> gives an exact12.5°line,325/285 mm total/useful, '
      '57.26 Nm static hip peak and44.27°useful hip ROM. The indexed grid winner285 mm has less '
      'clearance allowance; rounded300 mm leaves37.99 mm beyond220 mm on its working branch.</p>'+
      fig('Start-aligned paths, equal physical axis scale',paths([primary,indexed]),'Relative C_y (mm), equal scale','Relative C_z (mm)',equal=True)+
      '<pre>C=2L sin(q−π−d)[−sin(d),cos(d)], d=φ₀/2</pre>'
      '<p>This changes fixed <b>lower-link assembly indexing</b>, not mounting alpha and not reindexing '
      'during motion. It relaxes the original phase-zero ratio/length-only requirement. The total '
      'normal range is87.5–142.033°; full mathematical envelope87.5–247.5°. The old V2 validator '
      'and Motion Lab presets remain unchanged. Phase-zero inverted branches mirror their tilt; '
      'the indexed exact line retains it, while fold clearance still fails.</p>')
    speed=lines([primary,indexed],'Jz_m_rad')
    for line in speed:line['y']=[.25/x for x in line['y']]
    side=[]
    for ratio in [-.3,0,.3]:
        rows=primary['force']['samples'];side.append(dict(x=[s['height_mm'] for s in rows],
          y=[abs(110.3625*(s['Jz_m_rad']+ratio*s['Jx_m_rad'])) for s in rows],label=f'Fy/Fz={ratio:+.1f}'))
    sec('control','Control range and side loads can change the ranking',
      fig('Illustrative0.25 m/s constant vertical speed',speed,'Useful vertical height (mm)','Direct hip speed (rad/s)')+
      fig('320 mm case, hypothetical horizontal-force sensitivity',side,'Useful vertical height (mm)','Direct hip torque magnitude (Nm)')+
      '<pre>τhip = −(Fy Jx + Fz Jz)\nqdot = zdot/Jz\nqddot = zddot/Jz − (dJz/dq)zdot²/Jz³</pre>'
      '<p>The indexed leg has similar peak torque but higher peak hip speed:1.376 versus0.871 rad/s '
      'at this illustrative speed. Acceleration, dwell and hardware inertia are unspecified; these '
      'are not smooth-start motor requirements. Side loads can alter torque and which leg wins.</p>')
    sec('inversion','Mathematical inversion and actual engine refinement',
      fig('Full ideal paths; red220 mm projected wheel-centre exclusion',full_paths([primary,indexed]),'C_y (mm), equal scale','C_z (mm)',equal=True,disk=True)+
      table(['Actual Pymunk case','2ms error mm','1ms error mm','0.5ms error mm'],[[LABELS.get(c['id'],c['id']),*[fmt(a['max_path_error_mm'],5) for a in c['refinement']]] for c in e['cases']])+
      '<p>All three full angular sweeps pass at1 and0.5 ms and converge. All2 ms path checks '
      '<b>fail</b> the unchanged0.1 mm threshold and remain recorded. Real motor/pivot/gear constraints '
      'generate movement; only initial poses are assigned. Positive masses, zero gravity/contact, '
      'and no collision shapes make these <b>geometry checks</b>, not force or packaging certification.</p>'
      '<div class="note rejected">At the fold, wheel-centre hip distance is |L₂−L₃|, far below220 mm. '
      'Resolve actual axial/chassis clearances before calling any candidate physically invertible. '
      'Historical dual-rope stays <b>IMPOSSIBLE /rejected</b>.</div>')
    sec('evidence','Reasoning, validation and reproduction',
      f'<p>Five new tests check finite differences, buffer roots, quadrature, exact force peaks, knee work '
      f'and rejected geometries. The existing5 inversion and12 generalized tests pass. '
      f'<b>{v["scalar_comparisons"]:,}</b> scalar comparisons against original Jonathan V2 and existing '
      f'Andy2D statics pass, max discrepancy{v["max_error_mm_Nm"]:.2e} mm/Nm. Independent review '
      'checks the force/work mapping and selected dense geometry. Three actual Pymunk refinements '
      'provide separate geometry evidence.</p>'
      '<p><b>Recommended choice:</b>320/320,9:5 if phase zero is required and9 mm bow suits the design; '
      '350/350,7:4 for the existing roughly12°example;425 mm links only if2%bow dominates size/force. '
      'If fixed indexing is acceptable,300/300,2:1,φ₀−25°is the cleanest line with a wider control range. '
      'Full physical inversion remains a packaging decision.</p>'
      '<pre>python force_travel_search.py\npython -m unittest -v test_force_travel test_inversion_search test_generalized_leg\npython scripts/verify_force_geometry.py\nnode scripts/verify_force_report.cjs --math-only\npython scripts/build_force_report.py\nnode scripts/verify_force_report.cjs</pre>'
      '<div class="links"><a href="docs/force-travel-report.pdf">Companion PDF</a><a href="docs/force-travel-study.md">Full design reasoning</a><a href="docs/force-travel-results.json">Selected evidence</a><a href="docs/revisions.md">Revision map</a><a href="inversion-paths.html">Earlier path report</a><a href="index.html">Earlier spring/motor report</a></div>'
      '<p>Source base d1596e5;2026-10-14. Measured mass, axial packaging, accepted local-angle limits, '
      'spring routing, impact stroke, motor/gearing/inertia and thermal duty remain open. No canonical '
      'robot, hardware, other-OS or actual impact validation is claimed. This report adds no Motion Lab controls.</p>')
    toc=''.join(f'<a href="#{id}">{i+1:02} {html.escape(title)}</a>' for i,(id,title,_) in enumerate(sections))
    payload=json.dumps(d,separators=(',',':'),ensure_ascii=False).replace('<','\\u003c')
    output='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'"><title>CAMEL · Force and useful travel</title><style>'+css+'</style></head><body><header class="top"><div class="brand">CAMEL <small>Design report3 /October2026</small></div><div class="top-actions"><a id="pdf-link" href="docs/force-travel-report.pdf">PDF report ↗</a><button id="print-report" class="print-button">Print report</button></div></header><div class="hero"><div><p class="eyebrow">ALPHA ZERO · FORCE AND TRAVEL</p><h1>Force leverage &<br>useful travel.</h1><p>Which invertible ideal leg path is worth its link length, torque and control range? A separate offline design screen with explicit packaging limits.</p></div><div class="hero-box"><b>Offline report3</b><span>2026-10-14 · base d1596e5</span><span>11.48 million strict windows</span></div></div><main class="reader"><nav class="toc">'+toc+'<small>Embedded static figures.<br>No connection or server needed.</small></nav><article class="report">'+''.join(s[2] for s in sections)+'</article></main><footer class="footer">Experimental member study · ideal alpha-zero geometry · physical inversion unresolved</footer><script type="application/json" id="report-evidence">'+payload+'</script><script>document.getElementById("print-report").addEventListener("click",()=>window.print());</script></body></html>'
    output=output.replace('Design report3 /October2026','Design report 3 / October 2026').replace('Offline report3','Offline report 3')
    (APP/'force-travel.html').write_bytes(output.encode())


def main():
    load=lambda p:json.loads((APP/'docs'/p).read_text(encoding='utf-8'))
    d=load('force-travel-results.json');e=load('force-travel-engine-checks.json');v=load('force-travel-math-checks.json')
    pdf=render_pdf(d,e,v);render_html(d,e,v)
    from pypdf import PdfReader
    print(json.dumps(dict(pdf=pdf.name,pages=len(PdfReader(pdf).pages),bytes=pdf.stat().st_size,
      html_bytes=(APP/'force-travel.html').stat().st_size)))


if __name__=='__main__':main()
