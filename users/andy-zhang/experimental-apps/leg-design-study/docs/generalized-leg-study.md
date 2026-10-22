# Generalized leg design study

Author: Andy Zhang with Codex. Date: 2026-10-14. Status: experimental design
screening; no selected hardware or canonical robot certification.

The owner's request combines Jonathan's V1/V2 leg solver with Andy's wheel/link
sizing study, then checks one design with independent 2D mechanics and Pymunk.
Open the standalone [offline HTML report](../index.html) directly in a browser,
or use **Open Design Report.cmd** in this folder. The owner explicitly requested
static delivery separate from Motion Lab tooling. The original
[equal-link study](../../wheel-leg-lab/docs/link-sizing.md) remains reproducible.
The [PDF report](generalized-leg-report.pdf), also available from the study's
download link, collects the parameters, figures, numerical comparisons and
validation evidence for this revision.

## Provenance and conventions

Starting repository revision: `6c74cfd` on main. The two sources are
[Jonathan V1](../../../../jonathan-xie/experimental-apps/vsl-solver/v1/v1-kinematics.html)
and [Jonathan V2](../../../../jonathan-xie/experimental-apps/vsl-solver/v2/v2-quasi-static.html),
with [V2's model](../../../../jonathan-xie/experimental-apps/vsl-solver/v2/v2-model.md).
Jonathan's published folder has README and context/README.md, but no app-level
AGENTS.md or context.md; the repository rules apply. His standalone source is
retained unchanged. The user's supplied screenshot is the initial parameter
source; the request explicitly asks to inherit Jonathan's variable conventions.
Private conversation screenshots are not copied into the public repository.

Lengths/pitch radii are mm; angles are degrees in the interface and radians in
derivatives; masses kg, force N, torque N m, spring rate N/mm, time seconds.
Local +u points right and +v up. Global +y points right/rearward and +z up.
Alpha rotates the local frame clockwise. Theta2 points B to A; theta3 points C
to B. C is wheel centre and P the contact patch. Beta is clockwise from global
downward vertical toward -y. The generalized knee relative-angle derivative is
`d(theta3-theta2)/dtheta2 = -q_ab`, not a universal factor of two.

In the equal-link, alpha=phi0=0, q_ab=2 limit, Jonathan's theta2 equals
180 degrees minus Andy's upward wheel-centre angle. Andy's fold q equals
theta2 minus 90 degrees. Alpha in this study is a frame mounting angle; older
fixtures sometimes use alpha for the knee opening. These meanings must not be
interchanged when transferring configurations.

## Screenshot starting case

| Input | Initial value | Origin |
| --- | --- | --- |
| L2, L3 | 250, 250 mm | Screenshot |
| ra, rb; q_ab | 100, 60 mm; 5/3 | Screenshot |
| rc, rd, re, rf | 35 mm each | Screenshot |
| rw | 200 mm radius (400 mm diameter) | Screenshot and owner |
| theta2e, theta2c; current theta2 | 100, 165; 100.135 degrees | Screenshot |
| alpha; beta | 0; 13.5 degrees | Screenshot |
| Fy, Fz | 100, 100 N, global driving convention | Screenshot |
| m1; m2, m3, m5, m6 | 10 kg; zero | Screenshot |
| g; r5I | 9.81 m/s²; 35 mm | Screenshot |
| phi0; belt preloads | 0 degrees; 0 N | Not visible: explicit V2 demo assumptions |

Executing the original embedded V2 model reproduces the screenshot: theta3
53.24333 degrees, tau2 -25.62966 N m, tau4 -14.77849 N m and tight a/b tension
84.48598 N on the lower span. The current displacement is (0.26517, 0.33772) mm.
At theta2=165 degrees, displacement is **101.15712 mm lateral and 338.61593 mm
vertical**, with gamma_yz=16.63283 degrees. The global maxima over theta2=100–165
and beta=0–90 at fixed alpha=0 reproduce |tau2|=44.44895 N m,
|tau4|=20 N m and tight Tab=337.98316 N. These are attained ideal-model values;
they are not hardware measurements or a motor specification.

## Diagnosis

The starting design already reaches the requested 300–350 mm total vertical
range, but its approximately 101 mm sideways motion matters for wheelbase,
packaging and tire motion. Allowing alpha, link ratio and pulley ratio to change
can improve the vertical window or reduce drift. A design cannot be ranked by
height alone, and a low-torque point is not a useful control window.

The previous 120 mm equal-link result solved a different problem: 200 mm usable
travel, 20 mm geometric reserves at either end, a vertical 100 N hub load and
an ideal fixed 2:1 guide. It is not transferable to Jonathan's different angle
window, 300–350 mm total travel, lateral load or pulley geometry. Wheel radius
sets packaging/clearance and tire moment; it does not independently set link
length or unconstrained wheel-centre travel.

Jonathan's V2 math is internally consistent in the tested cases. Its fixed-A
mass m1 affects the chassis support reaction, while prescribed contact force
determines leg torque. Treating m1*g as another wheel force would double-count
or change the load case. Moving the supported chassis instead is a separate
energy/inertia problem, explicitly identified by the new study.

Signed average torque can hide large positive and negative demands. Mean
absolute torque describes typical magnitude; time RMS is the useful first
copper-heating proxy; peak sizes the transient requirement. A control window
also needs finite vertical Jacobian, speed/acceleration limits, end reserves,
drift/clearance constraints and a specified trajectory. Work per vertical metre
is not generally torque: ideal work is the integral of torque over angle.

## Assumptions for unattended continuation

The owner clarified a **200 mm minimum usable travel**, approximately **250 mm
preferred usable travel** to allow extra chassis height, and **300–350 mm total
capacity including all buffers**. The central study uses 325 mm total capacity
with assumed 20 mm at each end, leaving 285 mm usable travel. Compare the compact
300/260 mm and larger 350/310 mm total/usable cases. Buffers reserve geometry;
they are not automatically spring preload or coil compression.

The illustrative motion lasts 1 second with a quintic, zero-end-velocity and
zero-end-acceleration travel profile. The owner estimates a 40–45 kg robot, so
the moving-chassis example uses 10 kg per leg and checks 11.25 kg sensitivity
under equal four-leg support. The requested 3–4g impact envelope means total
support load in this study; 4g upward acceleration instead requires 5g support.
Unequal contact sharing and available impact stroke matter; see the
[load-factor and impact reasoning](impact-load-envelope.md).
Zero moving masses in the screenshot remain a static limiting case; any added
link/wheel mass used in dynamics must be explicitly recorded. Damping remains
zero. Motor-shaft gearing, efficiency and inertias require explicit inputs;
joint-output requirements must not be presented as a purchased motor rating.

## Two ways to select a design

1. **Constrained scalar search:** fix a load/motion scenario, reject invalid
   geometry and control windows, enumerate a bounded coarse grid and refine
   promising candidates. Minimize peak torque for transient capacity or RMS
   for repeated-duty demand. Report grid/bounds/refinement and boundary winners;
   the result is a best tested candidate, not a proof of a global optimum.
2. **Pareto comparison:** retain candidates that improve torque, total link
   length or sideways motion without being worse on all of them. Select a
   practical compromise after inspecting its complete angle/height window.
   This makes the compactness/torque/path tradeoff visible without hiding it
   inside arbitrary weights. Spring and motor constraints can then reject
   candidates before selecting hardware.

For higher-dimensional follow-up, bounded differential evolution followed by
local refinement is an option, but multiple starts and independent verification
are still needed; see [SciPy's documented method](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html).
The implemented search and retained numerical results are detailed in
[the generalized math record](generalized-leg-math.md).

## Numerical and physical boundaries

The compact example is **L2=180 mm, L3=340 mm, q_ab=1.775 and alpha=4.375
degrees**. Physical theta2 spans 100 to 159.810888 degrees. With 20 mm vertical
reserves, the usable control interval is 106.429341 to 157.077766 degrees,
giving 285 mm usable travel within 325 mm total. The lower-link upward angle
from global horizontal through C is theta3-alpha: it spans 52.642261 to
13.389732 degrees over that usable interval. Its full-path lateral excursion
is 11.412 mm. This distinguishes the wheel-centre angle from Jonathan's motor
coordinate instead of applying the equal-link shortcut to unequal links.

The robust static peak score is 46.260 N m, combining the two direct-input
torques for the stated force scenarios. The 180 mm upper-link minimum and
340 mm lower-link maximum are active search bounds. An expanded 395 mm tibia
case lowers the score to 39.632 N m but increases lateral excursion to 86.778 mm.
For a compact example with a nearly vertical path, retain the 180/340 candidate;
the [math tables](generalized-leg-math.md) show the alternative objectives and
300/350 mm cases. This selection is a documented tradeoff, not a global minimum.

Using the explicit physical mass allocation of m1=8.30, m2=m3=.35, m5=.10 and
m6=.90 kg, the illustrative hip-bellcrank fit uses **4.3698 N/mm**, **213.95 N
installed preload**, **67.78 mm coil stroke**, and **510.15 N peak coil load**.
Its 80 mm arm at 135 degrees and chassis mount (120,50) mm are assumed mount
geometry; its 35.25 mm free length is a fitted model parameter, not a selected
catalog spring. All nine fits are tabulated in the [physics record](generalized-leg-physics.md).

A one-second, 285 mm quintic traverse gives **6.449 N m peak / 3.641 N m time
RMS** at the direct leg input, **1.605 rad/s peak speed** and **6.573 rad/s²
peak acceleration**. The full undamped out-and-back motion has the same peak
and RMS; the raising stroke reverses speed. With an explicitly assumed 10:1
motor reduction and 85% efficiency, the simplified shaft values are about
0.759 N m peak, 0.428 N m RMS, 16.052 rad/s (153 rpm), and 65.731 rad/s².
These omit rotor inertia and real gearbox/drive losses and are not a motor
selection. The guide ratio 1.775 is separate from that motor reduction.

The same fixed spring under 4g total support requires **123.35 N m** direct-input
holding demand at 10 kg per leg, or **143.77 N m** at 11.25 kg. The 5g
sensitivity gives 164.19/189.71 N m respectively. These held-pose equivalent
loads are distinct from the 1g smooth trajectory and do not establish impact
duration, stopping stroke or energy dissipation. A final motor/gearbox choice
needs the peak torque-speed envelope, thermal duty, gearbox shock limits and
measured contact/spring behavior in addition to the nominal RMS figure.

The new [generalized physics record](generalized-leg-physics.md) distinguishes
independent inverse dynamics from actual Pymunk constraint stepping, includes
the suspension assumptions and records the tested example. Numerical agreement
does not establish hardware strength, belt tooth counts/wrap, friction limits,
spring fatigue/solid height, motor thermal ratings or 3D collision clearance.
The rejected dual-rope invertible design stays **IMPOSSIBLE / rejected** and
is excluded from design recommendations. The separate symmetric bellcrank does
not inherit that rejection.

Relevant primary background: [Jacobian-transpose statics and virtual work](https://modernrobotics.northwestern.edu/chapters/chapter5/),
[Pymunk constraints](https://pymunk.readthedocs.io/en/latest/pymunk.constraints.html),
and [maxon's motor load/RMS sizing guide](https://www.maxongroup.com/medias/sys_master/8815460712478.pdf).
The mechanism-specific equations, implementation and numerical checks are
repository evidence rather than claims that those sources validate this design.

See [revision history](revisions.md) and [validation](validation.md) before
continuing from a later checkout.
