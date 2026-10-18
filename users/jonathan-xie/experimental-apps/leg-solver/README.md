# General VSL Solver

Owner: Jonathan Xie. Created with Codex, 2026-10-13. Status: experimental analytical tool.

## V4 textbook: 10mm pulley and effective mg compensation — 2026-10-18

Default/Reset now uses the requested13kg,300/300mm,k8N/mm,Sv100mm,rs10mm
textbook example: Su7.157923mm,rh89.416035mm,p0149.918335N,all nominal
spring drivers off. Ideal compensation error stays within±0.06209% over
100–165deg, with at most0.037295Nm applied motor correction. Read the
[textbook derivation/plots](v4-textbook.md) or Load the [complete preset](v4-textbook-10mm.json).

The new **Fit rh,Su,p0 to1mg** button holds k/Sv/rs/nu/leg geometry and jointly
solves rh/Su/p0 numerically, turns nominal drivers off and reports checked error.
The exact point rule/preload button remain available under their zero-radius,
zero-offset assumptions. No exact finite-pulley closed-form identity is claimed.

The owner clarified the percentage: it is **100*(effective support/mg-1)**,
so0%=1mg,-10%=0.9mg,+10%=1.1mg. The middle card now has separate linear
raw-motor and compensation-error graphs; headlines append the compensation
error at the same pose. It is independent of prescribed Fz, and undefined
at zero total weight/vertical Jacobian. The geometry card remains collapsible.
91,128 model/fitter assertions pass; actual browser checks include finite fit
from invalid point geometry, both graphs, zero-mass handling and textbook reset.

## V4 applied CCW torque and 13kg tuning — 2026-10-18

V4 now reports **tau2 as the actual applied CCW motor torque**: tau2=tauG-tauS,
where tauG is the no-spring CCW motor requirement and tauS the physical signed
spring couple. Previous V4 displayed demand signs are reversed; the actual
physical solution and geometric saved settings are unchanged. More preload
raises tau2 over100–165 degrees, by an angle-dependent amount.

The middle geometry section is collapsible. Its right plot now shows motor
torque on a linear Nm axis plus a separate effective mg compensation-error
graph, as clarified above; zero weight/vertical Jacobian is undefined. Current/global tau2
headlines append percentages (global percentage is evaluated at the torque peak).

For the confirmed13kg,300/300mm,k8,Sv100,rs0.1 sample, the product rule alone
requires matching preload as well. Read [tuning explanation and plots](v4-tuning.md),
or Load parameters with the [fitted preset](v4-sample-13kg-fitted.json) and
[point-rule comparison](v4-sample-13kg-point-rule.json). Keep all spring drivers
off for the fitted case. Ideal fitted support error is below0.0004%; this
numerical fit is not a hardware accuracy claim. Revised verifier passes91,128
assertions; both collapse states, preload rise, fit import, percentage singularity
and expanded linear plots pass actual browser checks.

## V4 hip pulley and literal preload

Open [v4-pulley.html](v4-pulley.html) or [Open Leg Solver v4.cmd](Open%20Leg%20Solver%20v4.cmd).
V4 routes a cable from the hip horn over one finite-radius fixed pulley to a
remote spring. The three input rows are k/r_h/S_v (zero or one driven), r_s/p0,
and nu/S_u. All coordinates follow the local u/v frame. P0 is literal spring
force at 90 degrees; invalid reference tangency is flagged even when the 100-degree
operating stop is clear. Cable payout includes tangent span and changing wrap.

The nominal driver uses **k*r_h*S_v = 2*m_total*g*L2*cos(alpha)**. L2 is required
for dimensional consistency; total mass includes all five mass inputs. Matching
point-pulley preload is reported separately: p0=0 is not automatically balanced.
The finite-radius model computes actual spring and applied motor torque throughout.

Current Fs, global max Fs and extension-stop pe occupy the third headline column.
Force masters accept Current xg entries. Graphs default to master bounds, with
optional 90-270-degree expansion when clamping is off. TauG/TauS use subscripts;
duplicate contact controls and r5,I are removed. V1/V2/V3 remain unchanged.

Read [V4 equations, signs, defaults and validation](v4-model.md). Run
`node verify-pulley.cjs` for 91,128 assertions. V4 JSON saves driven/view choices;
older files load geometry/forces with the new spring disabled. Actual browser
checks cover controls, curves, exports and invalid-reference recovery. The
manual offline launcher opens the adjacent file; automated browser QA used the
identical HTML over temporary loopback HTTP. No hosting or hardware claim.

## V3 spring assistance

Open [v3-spring.html](v3-spring.html) or use
[Open Leg Solver v3.cmd](Open%20Leg%20Solver%20v3.cmd). The original V1/V2 files
are preserved. V3 adds one femur-fixed hip horn and a unilateral tension spring,
S_y/S_z anchor coordinates, horn radius/angle, effective zero-force length, added
preload and k. Theta2 motion allows 90–270°; a master checkbox switches all
theta-based graphs, including height sweeps, between 90–180° and 90–270°.

V3 uses the requested **tau2 = tauG - tauS** residual load convention; the
physical applied CCW motor couple is **-tau2**, while tau4 keeps V2's sign.
Every torque graph includes all four quantities. The spring updates the femur
FBD and hip reaction; live/global headline tau2 values are residuals. A labeled
whole-leg/hip-detail diagram reports installed length and tension, and a separate
full-range support graph exposes poles, slack and reversed spring action.

The compact sample is an approximate ±2.20% fit over 100–165°, not an exact
constant-force mechanism. Its spring goes over centre near 246.874° and reverses
torque; full-travel peak residual is about 25.16 Nm. Read the
[V3 model, signs, defaults and validation](v3-model.md),
[dimensioned diagram](v3-hip-horn-geometry.png) and
[full-range plots](v3-full-range.png). Run `node verify-spring.cjs` for 28,616
assertions. JSON and CSV include spring state; importing older parameter files
defaults the spring off. Contact forces remain independent inputs, not m1*g.

## Versions

| Version | Open | Purpose |
| --- | --- | --- |
| v4 hip pulley | [v4-pulley.html](v4-pulley.html) | Finite-radius cable wrap, literal preload, driven spring scale, Fs/pe and bounded plots |
| v1 kinematics | [v1-kinematics.html](v1-kinematics.html) | Original mechanism, with live/final atan2 travel angles gamma_uv and gamma_yz in rows 3/6 and the angle plot |
| v3 spring assistance | [v3-spring.html](v3-spring.html) | Hip tension horn, residual actuator torque, 90–270° travel, labeled geometry and full-range equivalent support |
| v2 quasi-static | [v2-quasi-static.html](v2-quasi-static.html) | Prescribed contact loads, masses/gravity, span tensions, motor torques, five FBDs, switchable force conventions, twelve loading sweep plots and angles versus vertical travel |

Use [Open Leg Solver v2.cmd](Open%20Leg%20Solver%20v2.cmd) for v2 on Windows.
Read the [v2 model and usage](v2-model.md) for point-name changes, force directions,
equilibrium derivation, preload assumptions, master sliders and validation.
V2 renames the wheel centre C and uses P for the contact patch. V1 retains its
original P endpoint name. Displacements in v2 track C relative to C at extension.
Both versions are self-contained HTML files with no runtime dependencies/server.

V1's new gamma angles use quadrant-aware atan2(horizontal, vertical), in degrees,
as requested in the follow-up clarification. Zero travel direction is undefined
(— / empty CSV cell); curves break at undefined poses and angle wraps. The updated
kinematic checker passes 3,853 assertions; v2's checker passes 16,044.

V2 result sections have arrow buttons beside their titles: collapse the FBD block,
individual FBDs, any loading-sweep row, or the final result cards. Everything
starts expanded; hidden sections retain their current plots and values.

## Global headline maxima

The second headline row shows maxima across **all θ₂ × β combinations** in the
master bounds, with **α fixed at its current value** and driving force inputs
held fixed. Values use the same size as the current row; torque signs are kept,
Tab includes preload and its tight side, and dz is the largest absolute travel.
Each maximum includes a peak pose. Changing current α updates the calculation.
The search targets a magnitude gap ≤0.001 Nm/N/mm; if a computation limit is
reached, it displays an estimate and the remaining gap. Hover for details.

Run `node verify-global-maxima.cjs` for the new 29,863-assertion check against
actual FBD results, closed-form extrema and domain bounds. Core quasi-static
checks remain 16,044 assertions; v1 remains unchanged.

## Latest v2 controls

The θ₂ master has minimum, maximum and current boxes; its bounds also set θ₂ᵉ/θ₂ᶜ.
α and β share a row. Choose the **Driving** column for global Fy/Fz or wheel Fn/Ft;
the other components update automatically, and switching preserves the load.
Only one master plays at a time. The headline shows both torques, tight a/b belt
tension (upper/lower), and vertical wheel-centre displacement dz. Show/hide
checkboxes control each motor arrow and the driving wheel-force decomposition.

FBDs use two cards above three cards (Links 2/3, then 4/5/6). Below the θ₂ loading
sweep is a working-range dz sweep; the bottom row adds Angles vs dz between the
original plots. Parametric height curves retain reversing travel and multiple
poses at the same height. JSON saves the force convention and view settings;
legacy v2 JSON remains accepted. CSV adds dz sweeps and explicit x units.

## V1 kinematics


Open [v1-kinematics.html](v1-kinematics.html) directly in a browser, or double-click
[Open Leg Solver.cmd](Open%20Leg%20Solver.cmd) on Windows. This is a self-contained,
offline HTML file: no server, package installation or internet connection is needed.
All code, styles and equations are embedded. Reopen the file or refresh to restart.

The Desmos-style parameter panel offers four ratio/dimension triplets, exactly one
driven value per triplet, dimension swaps, numeric inputs, dimensional sliders,
and 1-degree mounting/phase/endpoint sliders. Manual angle inputs also accept
fractional degrees within the stated domains. Ratios are first dimension divided
by second dimension. Lengths and pitch radii are in mm.

The animation includes a dotted working-range foot path, three open belt stages,
material dots on belts and pulleys, wheel rotation, global/local axes, pause/play,
pose scrubbing and cycle speed. Graphs show the full 90–180-degree domain with
endpoint boundaries and a working-range band. Hover for values; legend checkboxes
toggle individual curves. Live readouts include all link angles and signed local
and global displacements/strokes. The envelope table distinguishes sampled interior
extrema from signed endpoint values. Save/load parameters as JSON or export the
full angle sweep as CSV (metadata lines start with `#`). Export includes the exact
extension/compression angles in addition to 0.1-degree grid samples.

## Confirmed model

All belts are open and nonslipping. Pulley a is chassis-fixed; b belongs to Link 3;
c is locked; d/e is a rigid double pulley independently bearing-mounted at B;
f is rigidly fixed to the wheel. The user's clarification supersedes the initial
phrase saying b was attached to the femur.

Theta2 points B→A; theta3 points P→B, counterclockwise from local +u. These reversed
link vectors reconcile the downward leg with theta2 in [90,180] degrees. The user's
clarification confirms these directions and replaces the requested displacement
plot's `dx` typo with `dz`. Global x is out of plane, also called w. The duplicated
L1/L2 wording in the input list is interpreted as the explicitly requested L2/L3
triplet; Link 1 is the fixed pulley, with no separate linear length.

With q_ab = ra/rb, q_cd = rc/rd and q_ef = re/rf:

```text
theta3 = phi0 + (180 - theta2)(q_ab - 1)
B = -L2 [cos(theta2), sin(theta2)]
P = B - L3 [cos(theta3), sin(theta3)]
delta2 = theta2 - theta2e
delta3 = (1 - q_ab) delta2
theta4 = 0
theta5 = (1 - q_cd) delta2
theta6 = q_ef theta5 + (1 - q_ef) delta3
       = [1 - q_ab + q_ef(q_ab - q_cd)] delta2
```

Trig functions above take degrees. Theta5's zero is a freely selected extension
assembly phase; theta6's zero is the requested wheel setpoint at extension.
Both are unwrapped absolute rotations relative to the fixed local frame, not
rotations relative to the adjacent link. Actual global orientations subtract alpha.
The relative knee coordinate changes by -q_ab delta2.

Displacements subtract P at theta2e, then rotate clockwise by alpha:
dy = cos(alpha) du + sin(alpha) dv; dz = -sin(alpha) du + cos(alpha) dv.
Signed h values are evaluated at theta2c, rather than treated as interior maxima.
The interface's expandable model notes show the carrier-frame belt derivation.

## Main analytical findings

- L2 = L3 = L, q_ab = 2, phi0 = 0 gives Pu = 0, Pv = -2L sin(theta2).
- Wheel rotation cancels when K = 1 - q_ab + q_ef(q_ab - q_cd) = 0.
- If q_ab differs from q_cd, cancellation requires positive
  q_ef = (q_ab - 1)/(q_ab - q_cd). Otherwise it cannot be realized using these open
  belts and positive radii. If q_ab = q_cd = 1, all positive q_ef cancel; if
  q_ab = q_cd differs from 1, none cancel.
- Ratios determine angular coupling. Absolute pulley radii affect belt geometry;
  lengths and phase affect the foot path; alpha rotates the path into vehicle axes.
- rw affects the drawing/free rim arc, not the unconstrained wheel angle or centre path.

The default dimensions (300 mm links, 100 mm wheel radius) are demonstration
values, not hardware recommendations. Presets reset all parameters: Straight 2:1
uses q_cd = q_ef = 1; Wheel spin uses q_cd = 2, q_ef = 1; Cancel spin uses
q_cd = 1.5, q_ef = 2 with q_ab = 2.

## Validation and limits

Run `node verify-kinematics.cjs` with installed Node.js; it requires no packages.
The check extracts the actual embedded solver, checks both script syntaxes,
closed-form scissor geometry, three independent carrier-frame constraints,
finite-difference position/angular sensitivities, global rotation invariants,
spin/cancellation degeneracies, exact belt lengths and material velocities at
both pulley wraps, invalid inputs and sampled envelopes.

Browser verification and numerical results are recorded in [context](context/README.md).
Canonical robot physics is not applicable to this isolated member app. No force,
spring, torque, inertia, dynamics, ground-contact rolling, belt compliance or 3D
collision analysis is implemented. Projected stages occupy separate axial planes.
Pitch circles within one stage must not overlap; invalid belt layouts are flagged
while ideal linkage equations remain available. Dot spacing is illustrative,
not a specification of matching timing teeth. Graphs and envelopes use finite
sampling and may miss very narrow extrema at extreme ratios.

Sources: the user's concept GIF/screenshots and clarified mechanism description
(2026-10-13). Hardware background: [SDP/SI technical handbook](https://www.sdp-si.com/D820/PDFS/Technical-Section.pdf).
Moving-carrier constraints and zero-spin condition are derived here.

## Continue development

Read the root repository protocol and [app context](context/README.md).
Keep future kinetics in a separate version so v1 remains reproducible. Add forces,
actuator coordinates and spring law only after their definitions are confirmed.
