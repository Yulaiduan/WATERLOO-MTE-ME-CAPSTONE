# VSL V3 — hip tension horn

Author: Jonathan Xie with Codex. Updated 2026-10-17. Experimental analytical tool;
sample geometry is a numerical fit, not an accepted hardware design.

Open [v3-spring.html](v3-spring.html), or double-click
[Open Leg Solver v3.cmd](Open%20Leg%20Solver%20v3.cmd). Standalone offline HTML;
no server, package installation or internet is needed for normal use. V1 and V2
remain separate. The [V2 model](../v2/v2-model.md) owns the unchanged belt and load model.

## Geometry and spring law

Global y points right/rearward; z points up. A is fixed at (0,0). Local u/v are
rotated clockwise by alpha relative to y/z. Theta2 points B→A, measured CCW from
+u; theta3 points C→B. C is wheel centre; P is contact patch. All angles below
are in radians for derivatives; UI angles are degrees. Positions are mm.

```
theta3 = phi0 + (pi - theta2)(q_ab - 1)
B_local = -L2 [cos theta2, sin theta2]
C_local = B_local - L3 [cos theta3, sin theta3]
[y,z] = [cos alpha*u + sin alpha*v, -sin alpha*u + cos alpha*v]
S_global = [Sy, Sz]
phi_h = theta2 + eta - alpha
D_global = r_h [cos phi_h, sin phi_h]
D'_global = r_h [-sin phi_h, cos phi_h]
ell = |D-S|
ell' = (D-S) dot D' / ell
x = ell - ell0 + p
Fs = springEnabled ? k max(0,x) : 0
U_s = k max(0,x)^2 / 2000   [joules; k N/mm, x mm]
F_s,on2,global = Fs (S-D)/ell
```

`Sy` and `Sz` are global chassis coordinates, not local u/v coordinates. Thus
varying alpha alone rotates the leg/horn relative to a fixed chassis mount S.
`eta` is a fixed horn offset from the B→A direction; the equivalent offset from
the physical femur direction A→B is eta+180° modulo 360°. No independent horn
rotation is introduced. A-D is rigidly part of Link 2, not another moving linkage.

`ell0` is the effective zero-force pin-to-pin span; `p` is added preload extension
in mm. When taut, changing p adds k*p N to tension without changing k. There is
no separately assumed built-in initial tension. Initial installed length and
tension at the selected start angle are calculated outputs. If ell-ell0+p≤0,
the tension spring is slack, with zero force/energy/torque. A real spring/shock's
mount lengths, initial tension, travel limits, stress and internal leverage must
be mapped to this effective law; its feasibility is not inferred from a fit.

## Torque signs and residual balance

V3 implements the requested sign change explicitly:

```
tauG = -(V2 holding tau2)              [Nm]
tauS = Fs * ell' / 1000               [Nm, signed spring resistance]
tau2 = tauG - tauS                    [remaining load demand, Nm]
applied_CCW_motor2 = -tau2
physical_spring_couple_on2 = -tauS
tau4 = V2 applied CCW drive torque    [unchanged convention]
```

TauG is a convenient name for the complete pre-spring generalized load, including
prescribed contact load, moving-link weights and wheel-drive coupling. It is
not generally just chassis weight. With derivative per radian and all lengths
converted to metres, virtual work gives

```
tauG = F_contact dot C' + sum(W_i dot R_i') + Mw*K
K = 1 - q_ab + q_ef(q_ab-q_cd)
tauS = dU_s/dtheta2
```

For L2=L3=L, q_ab=2, phi0=0, beta=0, Fy=0 and Fz=mg, with zero moving masses:

```
C_global = [-2L sin(alpha) sin(theta2), -2L cos(alpha) sin(theta2)]
Jz = dz_C/dtheta2 = -2L cos(alpha) cos(theta2)
tauG = mg*Jz = -2mgL cos(alpha) cos(theta2)   [L metres]
F_eq = tauS / Jz                           [Jz metres/radian]
support_ratio = F_eq / (m1*g)
```

Positive equivalent support means downward spring action on the wheel balancing
the prescribed upward load, hence upward support on the chassis. Its definition
is virtual-work equivalence for the constrained one-DOF leg, not the vertical
component of the spring itself. It is undefined where Jz=0 (90°/270° for A/B),
even if torque is finite. Full-range curves break across zero Jacobian and use a
symmetric-log y scale. A negative ratio means reversed spring action. The sample
does not implement a symmetric outward-bias architecture about the chassis plane.

Moving masses remain explicit V2 weights. m1 is fixed at A and does not directly
produce actuator torque in the fixed-chassis FBD. The prescribed Fz defaults to
98.1 N independently of m1=10 kg: changing m1 does not silently change contact
load. Enter the intended per-leg wheel load as a force. The support graph uses
m1*g only as its chosen reference normalization; at zero m1*g it is undefined.

## Actual force balance, not just torque subtraction

The direct hip spring acts on the femur and chassis, so the unchanged tibia,
wheel and belt equations still determine their forces and tau4. V3 adds Fs at
D to Link 2, changes its hip reaction to `F12_v2 - F_s,on2`, and changes its
applied motor couple to `-tau2`. Every body is rechecked for force/moment balance.
The chassis receives the opposite spring force at S. Including that mount
reaction restores the same resultant whole-system ground support as V2; the
spring is internal to the complete assembly. Reducing motor torque does not
remove the tibia's belt tension or the spring mount's load.

## Sample and full travel

| Input | Sample A |
| --- | ---: |
| L2, L3 | 300 mm each |
| q_ab, phi0, alpha, beta | 2, 0°, 0°, 0° |
| Sy, Sz | 94.620590929, 61.041136907 mm |
| Horn radius r_h | 63.025544878 mm |
| Horn offset eta | -34.047265734° |
| Effective zero-force span ell0 | 54.992217392 mm |
| Added preload p | 0 mm |
| k | 13.247872608 N/mm |
| Wheel force Fy, Fz | 0, +98.1 N |
| m1; moving masses | 10 kg; all zero |

At 100°: length 69.0264 mm, installed extension 14.0341 mm, tension 185.9226 N.
At 135°: length 106.5987 mm, extension 51.6065 mm, tension 683.6757 N.
Over 100–165°: support ratio 0.977968–1.022031 (dense numerical sampling), maximum
absolute residual 1.25254 Nm. This is approximate balancing, not exact constant
force and not a certified globally optimal geometry.

| theta2 | F_eq/(mg) | Residual tau2 (Nm) |
| --- | ---: | ---: |
| 90° | undefined; +infinity from inside | -3.0740 |
| 100° | 1.0220 | -0.2252 |
| 135° | 1.0149 | -0.6183 |
| 165° | 0.9780 | 1.2525 |
| 180° | 0.9271 | 4.2911 |
| 210° | 0.7431 | 13.0974 |
| 240° | 0.2624 | 21.7068 |
| 250° | -0.1749 | 23.6524 |
| 260° | -1.4309 | 24.8458 |
| 270° | undefined; -infinity from inside | 25.1437 |

The spring is taut throughout this full range. It goes over centre at
`atan2(Sz,Sy)+180°-eta = 246.874°` (approximately), where spring torque vanishes
despite peak tension about 1.598 kN. Beyond it, torque changes sign. Maximum
absolute residual is approximately 25.159 Nm near 268.07°. No shock stroke/force
rating, spring strength, friction, damping, linkage mass or collision is verified.
Plane overlap is deliberately outside this study, as requested.

Sample B rotates the sample's S clockwise by 20° and keeps eta/r_h unchanged;
k becomes k_A*cos(20°)=12.448928131 N/mm. With the same vertical load its support
ratio versus theta2 matches Sample A. Merely setting alpha=20° without moving S
does not reproduce that scaled geometry. A/B preset buttons reset the example.

## Controls, graphs, saved files

Working bounds and current theta2 allow 90–270°, with start≤end. Endpoint labels
are parameter-range bounds; extension/compression need not be monotonic for an
arbitrary geometry. The master checkbox changes every theta-based full-domain
graph and the parametric dz loading/angle graphs between 90–180° and 90–270°.
The beta/alpha graph domains remain 0–90°/0–45°, evaluated at current theta2.
The support graph always covers 90–270° independently of the checkbox.
Animation, endpoint envelope and headline maxima use working bounds, not graph
domain. A pose outside a shortened graph remains valid but its cursor is offplot.

All four torque graphs show tauG, tauS, new residual tau2 and tau4 with independent
visibility toggles and the existing absolute-value/sign-dash convention. Current
headline and global maximum tau2 use the residual demand. Physical arrows/FBD
couples use -tau2. Spring pin/force and initial tension appear in the diagrams.

JSON schema is `general-vsl/v3-spring`, adding the spring parameters and graph
checkbox. V1/V2 JSON imports default the spring OFF to preserve the old physical
motor torque; V3 reports the opposite sign as tau2 demand. Legacy loads/mode
retain V2's migration defaults. V3 CSV adds tauG, tauS, applied motor2 CCW torque,
spring length, force and support ratio. Undefined ratios are blank, not infinity.
Both theta and dz sweeps follow the graph checkbox and preserve repeated heights.

## Verification and numerical limits

Run `node verify-spring.cjs`; `--output` regenerates the dense sample CSV and
verification JSON. `python plot-v3-sample.py` then regenerates the PNG/SVG
[geometry](v3-hip-horn-geometry.png) and [full-range plots](v3-full-range.png).
Python plotting requires NumPy and Matplotlib; the actual HTML requires neither.
The dense CSV is generated evidence, not required by the app.

28,616 assertions passed, including 450 varied spring/load/geometry poses,
unassisted parity with the changed sign, unilateral slack, moment/force balance,
independent finite-difference energy derivative, fast/full solver parity, and
14 full-range/working-range global searches with attained-peak and domain checks.
Maximum force residual 3.22e-13 N, moment residual 7.11e-14 Nm; energy derivative
error 5.94e-9 Nm. These are numerical consistency checks, not hardware validation.
Dense sampling found a minimum support 0.97796816 slightly below the previous
coarser 0.97796937; sample parameters were unchanged and no equilibrium tolerance
was weakened. Actual browser checks cover 270° bounds, graph domains, preload,
spring off, slack, A/B, saved V3 restoration and CSV identity. Browser logs empty.

The maximum search retains analytic beta extrema at fixed alpha and conservative
theta interval bounds. Smooth taut intervals use a second-derivative bound;
slack crossings use a Lipschitz bound. It targets 0.001 Nm/N/mm remaining magnitude
gap, reporting estimates on the iteration limit. The internal general alpha-box
peak API rejects nonzero alpha-width when a spring is enabled: only the existing
fixed-alpha user-facing search is supported. Alpha plots themselves remain valid.
Plots and inverse-height roots are sampled and may miss very narrow features.
Coincident spring pins are rejected. No dynamic, damping, strength or hardware
certification is implied. Canonical robot physics is not applicable to this member app.
