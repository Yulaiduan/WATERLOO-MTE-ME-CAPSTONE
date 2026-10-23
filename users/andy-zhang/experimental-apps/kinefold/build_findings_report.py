"""Build the dated Kinefold engineering findings PDF from reviewed local evidence.

Run: python build_findings_report.py --spring-evidence spring-report-evidence.json
  --output exports/kinefold-findings.pdf
Inputs: the dated findings below and required --spring-evidence JSON, containing
reviewed Pymunk verification rows/notes; units mm, degrees, kg, N, Nm, J and s.
Output: one paginated PDF; requires reportlab==4.4.9 (optional report dependency).
Limitations: archival synthesis of experimental app results, not a fresh physics
run, hardware rating, canonical robot validation or automatic live-sheet import.
"""
from argparse import ArgumentParser
from html import escape
from pathlib import Path
import json

from reportlab import __file__ as reportlab_file
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                               TableStyle, PageBreak, KeepTogether)
from reportlab.graphics.shapes import Drawing, Line, Circle, String, Polygon

ROOT = Path(__file__).resolve().parent
INK = colors.HexColor('#20352f')
SAGE = colors.HexColor('#3f6b58')
MUTED = colors.HexColor('#61706a')
PALE = colors.HexColor('#edf3ee')
LINE = colors.HexColor('#d2ddd4')
AMBER = colors.HexColor('#925b24')
WIDTH = A4[0] - 96
BASELINE = '3d959e4'
DATE = '23 October 2026'


def clean(text):
    return str(text).translate(str.maketrans({'\u2011': '-', '\u2013': '-', '\u2014': '-', '\u2212': '-'}))


def setup_fonts():
    fonts = Path(reportlab_file).parent / 'fonts'
    pdfmetrics.registerFont(TTFont('Kinefold', str(fonts / 'Vera.ttf')))
    pdfmetrics.registerFont(TTFont('Kinefold-Bold', str(fonts / 'VeraBd.ttf')))
    pdfmetrics.registerFontFamily('Kinefold', normal='Kinefold', bold='Kinefold-Bold')


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.states = []

    def showPage(self):
        self.states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self.states)
        for state in self.states:
            self.__dict__.update(state)
            self.setStrokeColor(LINE)
            self.line(48, 39, A4[0] - 48, 39)
            self.setFillColor(MUTED)
            self.setFont('Kinefold', 7.5)
            self.drawString(48, 26, 'KINEFOLD  /  EXPERIMENTAL ENGINEERING FINDINGS  /  ' + DATE)
            self.drawRightString(A4[0] - 48, 26, f'{self._pageNumber} / {total}')
            super().showPage()
        super().save()


def build(output, evidence):
    setup_fonts()
    styles = {
        'body': ParagraphStyle('body', fontName='Kinefold', fontSize=9.2, leading=14,
                               textColor=INK, spaceAfter=9, alignment=TA_LEFT),
        'small': ParagraphStyle('small', fontName='Kinefold', fontSize=7.8, leading=11.5,
                                textColor=MUTED, spaceAfter=7),
        'h1': ParagraphStyle('h1', fontName='Kinefold-Bold', fontSize=23, leading=29,
                             textColor=INK, spaceAfter=14),
        'h2': ParagraphStyle('h2', fontName='Kinefold-Bold', fontSize=12, leading=17,
                             textColor=SAGE, spaceBefore=11, spaceAfter=7),
        'cell': ParagraphStyle('cell', fontName='Kinefold', fontSize=8.1, leading=11.6,
                               textColor=INK, splitLongWords=True),
        'head': ParagraphStyle('head', fontName='Kinefold-Bold', fontSize=8, leading=11,
                               textColor=colors.white),
        'formula': ParagraphStyle('formula', fontName='Kinefold-Bold', fontSize=10,
                                  leading=16, textColor=SAGE, spaceAfter=9),
        'cover': ParagraphStyle('cover', fontName='Kinefold-Bold', fontSize=37,
                                leading=43, textColor=INK, spaceAfter=17),
    }
    story = []

    def p(text, style='body'):
        return Paragraph(escape(clean(text)), styles[style])

    def add(text, style='body'):
        story.append(p(text, style))

    def heading(text):
        add(text, 'h2')

    def page(number, title, subtitle):
        story.append(PageBreak())
        add(f'{number:02d} / FINDINGS & DECISIONS', 'small')
        add(title, 'h1')
        add(subtitle, 'small')

    def table(headers, rows, widths=None):
        widths = [WIDTH * v for v in widths] if widths else [WIDTH / len(headers)] * len(headers)
        values = [[p(v, 'head') for v in headers]] + [[p(v, 'cell') for v in row] for row in rows]
        t = Table(values, colWidths=widths, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SAGE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, PALE]),
            ('LINEBELOW', (0, -1), (-1, -1), .6, LINE),
            ('LEFTPADDING', (0, 0), (-1, -1), 7), ('RIGHTPADDING', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.extend([t, Spacer(1, 10)])

    def callout(title, text):
        box = Table([[p(title, 'formula')], [p(text)]], colWidths=[WIDTH])
        box.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), PALE),
                                ('BOX', (0, 0), (-1, -1), .7, LINE),
                                ('LEFTPADDING', (0, 0), (-1, -1), 13),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 13),
                                ('TOPPADDING', (0, 0), (-1, 0), 12),
                                ('BOTTOMPADDING', (0, -1), (-1, -1), 10)]))
        story.extend([KeepTogether([box]), Spacer(1, 11)])

    add('CAMEL  /  MECHANISM & QUARTER-MODEL STUDIES', 'small')
    story.append(Spacer(1, 22))
    add('Kinefold\nFindings & learnings'.replace('\n', ' / '), 'cover')
    add('Geometry, suspension, contact dynamics, jump / landing and motor sizing', 'h2')
    add(f'Andy Zhang with Codex  |  {DATE}  |  Code baseline {BASELINE}', 'small')
    story.append(Spacer(1, 18))
    callout('The most important distinction',
            'Jon\'s V4 coil is tuned for approximately constant chassis support. An ideal constant-force spring instead supplies constant cable tension. Its hip torque still varies with cable geometry. These are separate selectable laws.')
    for title, text in [
        ('One saved physical problem', 'The builder, equilibrium and both dynamic engines share geometry and case settings. Both dynamic models use a vertically floating chassis with x and pitch constrained.'),
        ('The spring was physically present', 'The Pymunk audit found an incomplete spring illustration, not a missing constant-force law. The revised playback exposes the complete route, reel witness and force / payout readout; actual run checks are on page 4.'),
        ('The 2 m demand is substantial', 'The V4 coil baseline requires 232.345 Nm constant hip braking by the scoped energy calculation. The ideal constant-tension option at the same p0 requires 252.379 Nm. Listed EG23 gearboxes allow only 20-60 Nm momentarily.'),
        ('Agreement has a defined scope', 'Static-limit consistency is excellent. Contact trajectories are numerical approximations; near a failure boundary the engines can disagree, and energy residuals remain visible.'),
    ]:
        heading(title)
        add(text)
    add('Reading map: 2 Geometry / frame; 3 Spring laws; 4 Pymunk spring audit; 5 Static validation; 6 Dynamic/contact comparison; 7 Jump and landing; 8 Worked energy calculation; 9 Motor physics and catalog; 10 Gearboxes; 11 Workflow / validation limits; 12 Sources and assumptions.', 'small')
    add('Experimental member-app evidence. This is not an approved robot design, component selection, hardware-survival certificate or whole-vehicle simulation.', 'small')

    page(2, 'Geometry and the coordinate frame', '[R1, R2, R3] The side projection preserves scale; the chassis guide condition is an explicit study assumption.')
    table(['Parameter', 'Baseline', 'Meaning'], [
        ('L2 / L3', '300 / 300 mm', 'Equal femur / tibia links'),
        ('Wheel radius rw', '200 mm', '400 mm diameter; not 200 mm diameter'),
        ('Hip travel', '100 to 165 deg', 'Extension to compression stop'),
        ('Supported chassis m1', '8.75 kg per leg', 'A quarter chassis, not total vehicle mass'),
        ('Moving link masses', '0 kg', 'Exact massless straight-guide contact model'),
        ('Contact wheel m6', '1.5 kg', 'Explicit free-wheel demo; original V4 wheel is massless'),
        ('Gravity', '9.81 m/s2', 'Applied once to each physical mass'),
    ], [.28, .28, .44])
    d = Drawing(WIDTH, 215)
    for x in range(20, 500, 23):
        d.add(Line(x, 15, x, 205, strokeColor=PALE, strokeWidth=.5))
    for y in range(15, 210, 23):
        d.add(Line(20, y, WIDTH-5, y, strokeColor=PALE, strokeWidth=.5))
    a=(345,180); b=(345+202.67706228469808*.23,180-221.18320104303723*.23)
    c=(345,180-442.36640208607446*.23); floor=c[1]-46
    d.add(Line(245, floor, 455, floor, strokeColor=LINE, strokeWidth=2))
    d.add(Circle(*c, 46, strokeColor=INK, fillColor=None, strokeWidth=2))
    d.add(Line(*a, *b, strokeColor=SAGE, strokeWidth=7))
    d.add(Line(*b, *c, strokeColor=colors.HexColor('#758fa7'), strokeWidth=7))
    for point, text, off in [(a,'A / hip',(-52,9)),(b,'B / knee',(8,0)),(c,'C / wheel',(-86,0))]:
        d.add(Circle(*point,4,fillColor=colors.white,strokeColor=INK))
        d.add(String(point[0]+off[0],point[1]+off[1],text,fontName='Kinefold',fontSize=8,fillColor=INK))
    d.add(Line(100,135,40,135,strokeColor=SAGE,strokeWidth=2))
    d.add(Polygon([40,135,48,139,48,131],fillColor=SAGE,strokeColor=None))
    d.add(Line(100,135,100,190,strokeColor=SAGE,strokeWidth=2))
    d.add(Polygon([100,190,96,182,104,182],fillColor=SAGE,strokeColor=None))
    for x,y,text in [(36,119,'+x / front'),(111,183,'+z / up'),(55,89,'+y toward viewer'),(27,52,'q = 132.5 deg'),(27,35,'Grid = 100 mm')]:
        d.add(String(x,y,text,fontName='Kinefold',fontSize=9,fillColor=INK))
    d.add(Circle(100,104,6,fillColor=None,strokeColor=SAGE)); d.add(Circle(100,104,1.7,fillColor=SAGE,strokeColor=None))
    story.append(d)
    add('Front-left right-handed frame: +x forward and left on screen, +y to the robot\'s left and toward the observer, +z up. Positive +y moments appear counterclockwise. Source coordinates map x = -source_y, z = source_z and source +x to new +y.')
    add('Equal links and the 2:1 guide pulley ratio give the certified straight path used by contact. Belts follow moving carriers; pulley / wheel index axes and material markers show their actual reconstructed motion. A K=0 locked-drive baseline does not rotate the wheel merely because the leg folds.', 'small')

    page(3, 'Constant support is not constant tension', '[R1, R2, R4] The spring cable route and finite-idler moment arm are shared by statics and dynamics.')
    table(['Law', 'Cable force', 'Consequence'], [
        ('V4 coil', 'F = p0 + k(L - Lref)', 'Changing tension is fitted to roughly balance chassis gravity.'),
        ('Ideal constant force', 'F = p0; cable k = 0', 'Constant cable tension; changing lever arm gives varying hip torque.'),
        ('Spring disabled', 'F = 0', 'A useful negative control; the mechanism still retains its geometry.'),
    ], [.23, .33, .44])
    add('tau_spring = -F * dL/dq, with L in metres and q in radians', 'formula')
    add('U_coil = p0*DeltaL + 0.5*k*DeltaL^2; U_constant = p0*DeltaL', 'formula')
    add('The generalized spring torque is converted to an equal / opposite guide force. A generic linear Pymunk spring would not reproduce the finite horn / idler transmission. The visible reel is a schematic witness of payout, not a simulated strip-spring construction.')
    add('V4 baseline: p0=330.869283 N at the source\'s 90 deg reference and k=8 N/mm (8000 N/m). That preload reference is outside the 100-165 deg working interval; it is not the tension at the extension stop. Use metres and N/m consistently in the energy formula.', 'small')
    table(['Hip q (deg)', 'Payout (mm)', 'V4 coil F (N)', 'Constant F (N)', 'Constant tau (Nm)'], [
        ('100', '55.719', '348.731', '330.869', '-8.475'),
        ('132.5', '83.439', '570.491', '330.869', '-20.164'),
        ('164', '117.161', '840.273', '330.869', '-19.518'),
    ], [.15,.19,.22,.22,.22])
    heading('What was learned')
    add('A visibly moving spring does not prove its force enters the equations; a static-looking drawing does not prove it is absent. Force, torque, work and on/off trajectory controls are required in addition to rendering checks.')
    add('The saved default retains the V4 coil law. Selecting the constant-tension law while keeping p0 = 330.869 N deliberately changes the support and stored-energy behavior. It should not be expected to reproduce the coil-tuned suspension.')
    add('For a real constant-force element, housing, strip radius, hysteresis, travel limits and packaging require a separate hardware model. The app currently models ideal cable tension and exact cable payout; it does not invent those mechanical dimensions.', 'small')

    page(4, 'Pymunk spring audit and visibility fix', '[R4, R10] New audit evidence, kept separate from historical validation results.')
    if not evidence.get('validated'):
        raise ValueError('Reviewed spring evidence is required before generating the final report.')
    add(evidence['finding'])
    table(evidence['headers'], evidence['rows'], evidence.get('widths'))
    for text in evidence['notes']:
        add(text)
    heading('How to inspect it in Kinefold')
    add('In Mechanism studio, open Suspension and choose Ideal constant cable force, set the desired p0, and keep the spring enabled. Run the same saved design in Pymunk. Play or scrub through a changing leg pose; inspect the complete horn / tangent / idler / exit route, the reel / payout witness and the active-law force readout.')
    add('A paused frame, a held free-fall leg, exact equilibrium, or the old V4 coil selection can all explain an apparently static spring. The reel witness follows cable payout; it is not decorative time-driven rotation. Switch to spring disabled and rerun to establish the mechanical contribution.')
    add(evidence.get('visual_scope', 'Numerical and geometry checks are distinct from a manual browser / native-window review.'), 'small')
    add('Reproduce with app .venv Python verify_spring_playback.py; it invokes verify-spring-playback.cjs with captured JSON fixtures. The checks retain on/off controls, the work derivative and frame-dependent cable / reel geometry.', 'small')

    page(5, 'Static consistency with Jon\'s VSL v4', '[R2, R5] Historical matched-boundary validation: 72 cases and 144 actual one-second equilibrium rollouts.')
    add('Both dynamic engines were run as static problems: flat input, zero initial speed, zero damping and the original V4 holding torque. All rollouts completed their requested duration. Reaching a travel stop could not count as a pass.')
    table(['Baseline quantity', 'V4 / analytical / Pymunk'], [
        ('Required hip torque at 132.5 deg', '-0.027168833380 Nm'),
        ('V4 coil cable tension', '570.491044815 N'),
        ('Required vertical support', '85.8375 N'),
        ('Maximum holding-torque error, all cases', '5.69e-14 Nm'),
        ('Maximum spring-force error, all cases', '3.42e-13 N'),
        ('Maximum chassis drift, analytical / Pymunk', '7.96e-13 mm / 0 mm'),
    ], [.59,.41])
    heading('Boundary conditions matter')
    add('Jon\'s static wheel load acts at rim point P. The original floating-height bench supplies vertical support at wheel centre C. At beta=0 these support lines agree; at an offset contact angle their moments differ.')
    add('tau_Jon - tau_floating = rw * R * sin(beta) * K', 'formula')
    add('Only the introduced support moment is removed. Explicit additional loads keep their own rim moment. A deliberate offset case differs by -0.183072319 Nm before correction; using the wrong torque produces visible drift.')
    add('The baseline coil fit is close to support balance, not exact: zero hip torque produces -7.659992 mm/s2 initial chassis acceleration and about -0.153 mm movement in 0.2 s. This is expected model behavior.')
    add('These are numerical consistency checks of an ideal model. They do not independently validate belt / pin forces, impacts, tire compliance, strength or hardware. Historical spring and support readouts are derived model quantities.', 'small')

    page(6, 'Dynamic contact and engine comparison', '[R3, R6, R7] One physical fixture, two independent integrators; contact is distinct from prescribed wheel height.')
    table(['Mode', 'What is actually solved'], [
        ('Prescribed-height benchmark', 'Floating chassis; wheel-centre height is imposed. The moving floor explains the height input. It cannot create friction-driven wheel spin.'),
        ('Actual terrain contact', 'A real circular wheel, unilateral normal contact and Coulomb friction. The floor mesh translates through the world; spin, slip, separation and gap bridging are outcomes.'),
        ('Analytical contact', 'Reduced-coordinate mass matrix and accumulated contact impulses. This engine does not import Pymunk.'),
        ('Pymunk contact', 'Actual chassis / wheel bodies and constraints, plus exact condensed massless-link forces. It is not an all-body rigid linkage.'),
    ], [.31,.69])
    add('Contact demo assumptions: m1=8.75 kg, m6=1.5 kg, rw=200 mm, friction=0.8, zero bounce, free drive, and 150 mm height / plateau / gap at 100 mm/s. The original massless-wheel V4 benchmark remains separate.')
    add('Reduced state u=(h,s,psi): chassis height, guide separation and wheel spin. With guide vertical component az, J=ds/dq and Jref the reflected hip inertia, the mass matrix has rows [m1+m6, m6*az, 0], [m6*az, m6+Jref/J^2, 0], [0, 0, I6], with I6=0.5*m6*rw^2. Nonzero reflected inertia makes it configuration-dependent.', 'small')
    heading('Independent checks and numerical limits')
    add('Flat support is 100.5525 N = (8.75+1.5)g. Steady rolling spin is 28.647890 deg/s = 100/200 rad/s. Frictionless wheel spin remains zero. A 400 mm diameter wheel can bridge a 150 mm gap; centre motion need not copy the square floor.')
    table(['Historical case', 'Maximum chassis discrepancy'], [
        ('V4 prescribed-height 6.5 s benchmark', '0.004197 mm'),
        ('Jump: dt 0.0005 / 0.00025 / 0.000125 s', '2.247 / 1.384 / 1.092 mm'),
        ('Landing: same timestep sequence', '4.858 / 1.697 / 0.911 mm'),
    ], [.63,.37])
    add('Compare identical captured mechanisms, cases and numerical settings at equal sample times / event sides. Do not align impact times artificially or interpolate across discontinuities. Contact force is interval impulse divided by time, not a certified instantaneous impact peak.', 'small')

    page(7, 'Jump, landing and target torque studies', '[R6, R8] Heights, opening fractions and failure criteria need explicit definitions.')
    table(['Case', 'Definition / controller'], [
        ('Terrain stability', 'Moving bumps / gaps with free wheel contact; evaluate heave, travel, contact force, slip and separation.'),
        ('Jump', 'Start fully compressed and at rest. Constant extension torque acts until the extension stop, then cuts off. Target rise is above actual takeoff, excluding stance extension.'),
        ('Landing', 'Start at rest, default two-thirds open, with a wheel-bottom gap equal to drop height. Hold pose during free fall; actual contact releases hold into resisting braking.'),
        ('Success / failure', 'Observe first flight / apex or first chassis arrest. Bottom-out before arrest or insufficient underbody clearance fails the landing criterion.'),
    ], [.25,.75])
    add('Minimum underbody-to-ground clearance (default 50 mm) differs from underside offset below hip A (also 50 mm). Chassis clearance = hip height - underside offset - local floor height. A threshold is not a modeled chassis collision box.')
    heading('Energy estimates and dynamic inverse search answer different questions')
    add('Ideal jump energy includes stance gravity and the chassis / wheel rise in flight, less released spring / cogging energy. It neglects contact / stop / friction losses and retained rotor energy, so it is optimistic.')
    add('tau_jump = max(0, [m1*g*stanceRise + (m1+m6)*g*targetRise - springRelease - coggingRelease] / Deltaq)', 'formula')
    add('For a 100 mm jump target, the reference energy estimate is 8.859 Nm. Historical actual-engine searches found 10.9375 Nm passing in both engines, with rises 105.380 / 105.118 mm; 9.375 Nm was a tested failure.')
    add('For a 100 mm drop with a 500 mm minimum-clearance target, both engines found 21.875 Nm passing, achieving first-arrest clearances 501.453 / 500.355 mm. A 200 mm energy-sized near-boundary case disagreed between engines at dt=0.00025 s; that disagreement remains explicit.')
    add('Search uses five coarse commands and at most five local probes. It returns the lowest tested passing command and a known failing bracket when available, not a global minimum. Unobserved events / numerical failures are indeterminate; later rebound and holding require a full run.', 'small')

    page(8, 'The 2 m landing energy calculation', '[R4, R9] Constant resisting torque magnitude, per hip, using the V4 coil baseline and rest endpoints.')
    add('tau_hip = max(0, [m1*g*(H+s) - DeltaU_spring - DeltaU_cog] / Deltaq)', 'formula')
    add('tau_shaft = tau_hip / N; compression braking command is negative.', 'formula')
    table(['Quantity', 'Value', 'Interpretation'], [
        ('m1 / g / H', '8.75 kg / 9.81 / 2 m', 'Supported quarter chassis; full drop energy'),
        ('Initial / arrest hip angle', '121.666667 / 164 deg', 'Two-thirds open; 1 deg stop reserve'),
        ('Available Deltaq', '0.738856050 rad', 'Torque work uses radians'),
        ('Chassis compression s', '0.345287590 m', 'Gravity continues to release energy'),
        ('Drop energy m1*g*H', '171.675 J', 'Equivalent to 0.5*m1*v^2'),
        ('Compression gravity', '29.638623504 J', 'Additional energy to absorb'),
        ('V4 spring energy stored', '29.644002342 J', 'Energy absorbed by the spring'),
        ('Net motor braking work', '171.669621162 J', 'Cogging contribution zero in this baseline'),
        ('Constant hip magnitude', '232.345151887 Nm', 'Net work / Deltaq'),
        ('Arrest underbody clearance', '315.382413 mm', 'Stop reserve limits travel before 50 mm target'),
    ], [.36,.29,.35])
    add('At N=10 the ideal shaft demand is 23.2345 Nm; at N=20 it is 11.6173 Nm. With the spring disabled, hip demand is 272.4666 Nm. Switching only to ideal constant tension p0=330.869 N stores 14.8421 J and requires 252.3786 Nm instead.')
    add('Assumptions: fixed wheel after impact, stationary flat ground, massless moving links, full chassis drop energy, no friction / impact-loss credit, rotor rest endpoints and initial arrest only. This is an endpoint work screen, not peak torque or a hardware-survival result. A 50 mm gap is a minimum constraint, not necessarily the achieved endpoint.', 'small')

    page(9, 'Motor gearing, inertia and peak choices', '[R9, R10] Shaft properties and joint properties must not be mixed.')
    add('N = motor speed / hip speed; joint torque = N*shaft torque; reflected rotor inertia = N^2*Jmotor. Joint viscous coefficient = N^2*bmotor; joint Coulomb / cogging amplitude scales by N, while cogging cycles per joint revolution scale by N.')
    add('Motor friction is modeled as -Fc*tanh(omega/omega_epsilon) - b*omega. Cogging is conservative with a fixed phase. Rotor inertia contributes to transient motion / impulses even when its start-to-end energy change is zero. Legacy joint inertia and joint damping remain additive; wheel drive is separate.')
    add('theta_motor=N*q; tau_cog,motor=A*sin(k*N*q+phi); U_cog=A/k*cos(k*N*q+phi); rotor kinetic energy=0.5*Jmotor*(N*qdot)^2. Native Pymunk rotor coupling is ABI-guarded; its numerical constraint work remains separate from physical motor loss.', 'small')
    table(['Flipsky motor / winding', 'Peak shaft Nm'], [
        ('6374 190KV', '8'), ('6384 170KV Battle Hardened', '9'),
        ('6354 140KV Battle Hardened', '7'), ('6384 140KV', '9'),
        ('6374 140KV Battle Hardened', '8'), ('7070 110KV Battle Hardened', '9.5'),
        ('6368 140KV Battle Hardened', '5'), ('63100 140KV Battle Hardened', '10'),
        ('80100 130KV', '17'),
    ], [.75,.25])
    add('Catalog snapshot transcribed 23 October 2026. All are maximum / peak values, not continuous torque. The 63100 source specifies at most 30 s at maximum torque; other peak durations are unspecified. Regenerative braking and controller / DC-bus capability are unverified.')
    add('Energy-only component choices are saved separately from the physical motorConfig. A candidate ratio recalculates the energy screen using explicitly retained enabled passive motor assumptions; it does not infer actual Flipsky cogging, losses or inertia. Dynamic-case guidance always uses the saved physical motor.', 'small')

    page(10, 'Gearboxes can be the limiting component', '[R9] Ratio multiplication alone is not a gearbox-output-capacity check.')
    table(['Model', 'N', 'Nominal Nm', 'Momentary Nm', 'Forward efficiency'], [
        ('EG23-G5-D10', '5', '28', '56', '96%'),
        ('EG23-G10-D10', '10', '10', '20', '96%'),
        ('EG23-G20-D10', '20', '30', '60', '94%'),
        ('EG23-G50-D10', '50', '25', '50', '94%'),
    ], [.30,.10,.19,.21,.20])
    add('The unusual 10:1 rating is retained exactly. Sale 20:1 and used 50:1 listings duplicate the same mechanical models and are not additional designs. The family table calls the first output rating nominal; product pages call it maximum permissible. Momentary duration and BLDC shaft / adapter fit remain unverified.')
    add('Ideal motor output = N * peak shaft torque', 'formula')
    add('Effective screen capacity = min(ideal motor output, gearbox momentary output)', 'formula')
    callout('Worked pairing: Flipsky 80100 + 20:1 EG23',
            '17 Nm x 20 = 340 Nm ideal motor output, but the gearbox momentary limit is only 60 Nm. The motor meets the 11.617 Nm ideal shaft demand for the 2 m coil-baseline landing; the gearbox does not meet the 232.345 Nm hip demand.')
    table(['Reduction', '2 m required shaft Nm', 'Gearbox cap Nm', 'Gearbox screen'], [
        ('5:1', '46.4690', '56', 'Fails'), ('10:1', '23.2345', '20', 'Fails'),
        ('20:1', '11.6173', '60', 'Fails'), ('50:1', '4.6469', '50', 'Fails'),
    ], [.20,.33,.25,.22])
    add('Listed forward efficiency is reference information, not established backdrive efficiency. The energy calculator gives no unverified braking-efficiency credit. Direct drive has no gearbox cap; a custom gearbox with an unknown momentary rating remains unassessed and cannot receive an overall pass.', 'small')

    page(11, 'Workflow lessons and validation limits', '[R1, R6, R8, R10] Keep source lineage, saved state, numerical evidence and hardware claims separate.')
    table(['Decision / learning', 'Practical consequence'], [
        ('One project-v3 physical profile', 'Builder, statics and both engines share inputs. Captured physical edits stale old runs; exact snapshots are required for comparison.'),
        ('Analysis-only metadata', 'Energy / target settings mark designs dirty but do not silently alter motor commands. Applying a tested torque is explicit.'),
        ('App-owned interface', 'Mechanism studio combines library, builder and 17 categorized static plots; two dynamic tabs follow; conventions are last. Data plots use offline Plotly.'),
        ('Local files in Capstone', 'Profiles live in profiles/library.json; generated exports / PDF stay in app exports/. No browser Downloads workflow is required.'),
        ('Durable launcher', 'Start Kinefold.cmd preserves 127.0.0.1:4191 after shutdown; Stop Kinefold.cmd stops only the owned app. No boot automation.'),
        ('Honest diagnostics', 'Preserve missing values, event discontinuities, indeterminate trials, contact disagreements and unresolved energy ledger residuals.'),
    ], [.32,.68])
    heading('Evidence is layered')
    add('Historical suites include 2,000 core-model assertions, 1,123 drawing assertions, 9,404 static-series assertions and 11,757 equilibrium-diagram assertions. The latest energy / catalog work passed 115 energy assertions, 33 project-state groups, 17 temporary-disk tests and 19 Plotly lifecycle assertions. These counts describe separate dated suites, not a new combined hardware test.')
    add('The current spring-specific numerical and drawing checks are reported on page 4. Browser / native manual review status is stated there explicitly. Static-limit agreement is not independent measurement of contact force; contact / stop losses and stabilization work do not automatically imply tight energy conservation.')
    add('Still unresolved: canonical robot, physical strip / coil mechanism selection, motor current and thermal limits, regenerative energy handling, gearbox duration / fit / strength, compliant tires, 3D packaging, four-leg load transfer and a controller for rebound / holding after first arrest.', 'small')

    page(12, 'Sources, assumptions and next evidence', 'A dated synthesis of this Kinefold development conversation and repository records; superseded fixture descriptions are not current behavior.')
    refs = [
        ('R1', 'README.md and context/README.md', 'Current app architecture, decisions and dated verification handoffs.'),
        ('R2', 'reference.json; reference-v4.js; model.js', 'Retained V4 analytical blocks, provenance hashes and coordinate adapter. Source: Jonathan Xie\'s vsl-solver/v4/v4-pulley.html at revision 5e52a12.'),
        ('R3', 'equilibrium-plots.md; dynamic-analysis.md', '17 static chart definitions, dynamic comparison semantics and world-frame playback.'),
        ('R4', 'Spring law / energy calculations in model.js and dynamics.py', 'Reference-pose force samples and independent 2 m work calculations reproduced for this report.'),
        ('R5', 'static-validation.md; validate_static.py', '72 matched original-source cases, 144 actual holding rollouts and deliberate boundary-mismatch controls.'),
        ('R6', 'terrain-contact.md; contact-scenarios.md', 'Actual circle / terrain contact, free wheel, case controllers, comparison and refinement evidence.'),
        ('R7', 'verify_contact_comparison.py and dated context', 'Independent-integrator checks and historical maximum chassis discrepancies.'),
        ('R8', 'target-torque.md; torque_targets.py', 'Height definitions, bounded inverse search, first-event observations and indeterminate outcomes.'),
        ('R9', 'energy-calculator.md; energy-analysis.js', 'Landing equation, motor / gearbox catalog snapshot and output-capacity screening. Public maker / gearbox source links are retained in that note.'),
        ('R10', 'motor-model.md; verify_spring_playback.py; verify-spring-playback.cjs', 'Geared motor laws, native ABI constraints and the new spring rendering / physical-response audit.'),
    ]
    for key, path, meaning in refs:
        add(f'[{key}] {path}', 'small')
        add(meaning, 'small')
    heading('Use the result within its scope')
    add('Re-run the exact saved candidate with both engines, refine timestep near a contact / travel boundary, inspect the energy residual and full post-arrest trajectory, then measure real component behavior. Catalog peaks and analytical work are screening evidence; physical design acceptance remains open.')
    add(f'Provenance: code baseline {BASELINE} plus the spring-visibility changes and run evidence reviewed on {DATE}. Private workbook IDs / account data and unrelated personal material are excluded. Generated PDF is local; its report builder and source decisions are versioned.', 'small')

    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=48, leftMargin=48,
                            topMargin=47, bottomMargin=54, title='Kinefold - Findings and Learnings',
                            author='Andy Zhang with Codex', subject='Experimental mechanism and quarter-model validation')
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f'Created {output}')


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'exports/kinefold-findings.pdf')
    parser.add_argument('--spring-evidence', type=Path, required=True,
                        help='Reviewed compact spring audit evidence, not an unverified raw log.')
    args = parser.parse_args()
    evidence = json.loads(args.spring_evidence.read_text(encoding='utf-8'))
    build(args.output, evidence)


if __name__ == '__main__':
    main()
