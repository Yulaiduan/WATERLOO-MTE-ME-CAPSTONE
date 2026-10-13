# General VSL Solver — v1 kinematics

Owner: Jonathan Xie. Created with Codex, 2026-10-13. Status: experimental analytical tool.

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
