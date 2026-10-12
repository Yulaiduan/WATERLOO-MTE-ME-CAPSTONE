# Invertible dual-rope and symmetric knee suspension

Andy Zhang with Codex,2026-10-11. Status: editable member experiment, not selected
hardware or canonical robot validation. Source: user's attached sketch and
clarifications in this task: one cap/one loaded rope, actual±5°attachment points,
two small rollers near the knee, and bellcrank spring mount 50 mm from J1.
The later clarification replaces the initial outside-wrap prototype with central
feeds, outward flare and face anchors, with no knee-rim wrap.

## Three pulleys, one compression cap

The current dual-rope design has one knee pulley and two small rollers on the
femur. The cylinder axis is parallel to r1. Red/blue ropes leave close-set eyes
on one rigid piston rod's yoke, run through the central gap between the rollers,
and flare outward to the actual ±5° attachments on the knee pulley face.
There is no wrap around its outer rim. These two rollers are part of this new
design; the earlier single-rope mechanism still has no added piston idler.

Demo dimensions: 273 mm links, 50 mm lower extension, 200 mm wheel radius,
40 mm knee attachment radius, 10 mm rollers, centres 60 mm before the knee and
±15 mm to either side. The gap is 10 mm; rope eyes are ±2 mm from the cylinder
centreline. The rod-eye reference is 100 mm from J1, rod length 120 mm, physical
coil free length 120 mm and preload compression 10 mm. The schematic housing
extends 20 mm past J1 at its reference cap position; mounting fit is unverified.
All dimensions are editable demo inputs. Existing remembered dimensions stay
unchanged; Load selected flip demo explicitly selects these updated defaults.

For knee opening `phi=2theta`, face attachments rotate at `phi±delta`.
Geometry evaluates a free straight central path and inner-side tangent/arc
paths over either roller. The rope can lose roller contact when its face
anchor remains inside the channel. Paths cannot bypass the outside of the
roller gate; the knee face is not a circular obstruction. Overlapping rollers,
rope eyes outside the central gap and exhausted travel are rejected.
Axle/groove/rope-crossing clearance, friction, stretch and binding are unverified.

Let `ell_i(phi,x)` be the full cable length from the moving cap eye to its
face anchor. Neutral inventories are measured at `phi=pi, x=0`. Each rope's
positive cap demand is solved from that inventory, then one common cap follows
the larger demand:

```text
ell_i(phi,x_i) = ell_i(pi,0)  [solve when positive take-up is needed]
x = max(0, x_red, x_blue)
z = preload + x; coil_length = free_length - z
U = 0.5*k*z^2
F_cap = max(0, k*z + c*dx/dt)
lead_cosine = incoming cable direction dot cylinder axis
dx_i/dtheta = 2*(partial ell_i / partial phi)/lead_cosine
T_active = F_cap/lead_cosine; T_other = 0
Q_theta = -F_cap*dx/dtheta
slack_i = ell_i(pi,0) - ell_i(phi,x)
```

Angled leads require slightly more cable tension than cap force. Ties use the
outgoing branch, with deterministic red at rest. At zero take-up a mechanical
preload/reference stop reacts internal coil force; it is not a controller.
Energy and cap position are continuous at handoffs; derivatives can be
nonsmooth. Equal/opposite forces along the outgoing cable span reproduce
virtual torque and pin loads. The upper force aggregates its massless
cylinder/roller reactions. Red and blue do not have separate spring energies.

## Symmetric knee bellcrank

One crank is rigidly attached to the lower link at the knee. Its spring connects
to the femur50mmfromJ1, with an editable50mm crank radius. Set `a=L-50mm` and
`b=crank_radius`; then

```text
d^2 = a^2 + b^2 - 2*a*b*cos(phi-pi)
x = d - abs(a-b)
dd/dtheta = 2*a*b*sin(phi-pi)/d
```

A reversing compression unit uses the same preload/energy law. Distances and
energy are symmetric about the straight knee; torque reverses across it.
Endpoint forces act along the actual spring span. A nonzero preloaded spring
force remains at dead centre even though its moment is zero. Coincident mounts
and exhausted coil travel are rejected. This is one spring, not two opposing
springs or a hidden holding motor.

## Inverted start and applied femur torque

The separate full-angle fixture starts at `theta=-135deg`, with chassis centre
27.5mm above the flat floor and the wheel above it. Pymunk uses real wheel and
chassis contacts: heave/translation are free, chassis pitch is held, and the
2:1 guide keeps absolute upper/lower angles summing to minus pi. No wheel height
is prescribed. The links/transmission use sensor geometry; self-collision is
disabled to represent staggered lateral planes. No3Dclearance claim follows.

Clockwise femur torque is positive in the UI: upper body gets `-tau` and chassis
gets `+tau` in world counterclockwise coordinates. Demo input is100Nm with
40ms quintic rise/fall, starting at100ms. Pulse width is240ms dual-rope and
170ms bellcrank; default recording is1s at0.25ms Pymunk steps. These are toy
inputs, not motor ratings. Default cap damping is zero. Release can rebound,
fly briefly or rotate further; the recording does not freeze at a target pose.

Automatic spring rate balances the chosen normal ground ride pose (45deg demo)
using distributed link and corner weight; it does not guarantee global stability.
Default rates are about 7882.99 N/m dual-rope and 5116.73 N/m bellcrank. The default
ground flips are observed, not scripted angle trajectories. Step size must be
refined before interpreting contact/load peaks.

## Independent angular mathematics

SciPy and the matched physical comparison hold J1, without floor contact. They
integrate angle directly, avoiding the height-Jacobian singularity at90deg.
For ideal equal-link kinematics the positive effective inertia is

```text
M(theta) = I_upper+I_lower + m_upper*L^2/4
 + m_lower*((L+e)^2*sin(theta)^2+(3L-e)^2*cos(theta)^2)/4
 + 4*m_wheel*L^2*cos(theta)^2
M*theta_ddot + 0.5*M'*theta_dot^2 = tau + Q_spring + G*cos(theta)
G = gravity*(m_upper*L/2 + m_lower*(3L-e)/2 + 2*m_wheel*L)
```

Mathematical ground impacts are not synthesized. Ground experiments and fixed-J1
comparisons have different boundaries and must stay distinct. Pin/floor loads
are Pymunk impulse/dt resultants; mathematical channels report the independent
angular/energy state. Stored energy has a shared world-height datum. MATLAB
remains restricted to the old legacy-tip model.

## UI, records and live GUI

Open [the study](http://127.0.0.1:4186/inversion/?backend=pymunk) with the existing
Start Motion Lab.cmd. Choose a preset, Load selected flip demo, and Run torque /
flip. Start inverted and all dimensions/input slopes are editable. Before Run,
the diagram is geometry only and no solved joint/contact loads are shown.

Math/Physical tabs and their original height bench remain available. JSON and
the browser library use `inversion_math` / `inversion_pymunk`, a distinct model
family with explicit units. Run both & compare uses fixed J1 for both models.
The native button opens the actual `debug_inversion_gui.py` desktop simulation
on the server computer. Space pauses, period steps and R resets. The diagnostic
`--quit-at-end` exits only its own test window; normal server launch can loop.

New configs explicitly store `rope_routing=central_face` and rope-eye offset.
Saved pre-correction profiles are resolved to explicit `outer_rim` reproduction
on import/library execution/native launch; their original JSON and recorded
frames are not modified. The current UI labels those profiles as archived and
offers Load selected flip demo for the corrected route. Session edits retain
numeric choices while adopting the current route. Direct API configs without a
routing marker use the corrected default; legacy API reproduction must select
`outer_rim` explicitly with its old dimensions.

Code: [geometry](../invertible_spring.py), [solvers](../inversion.py),
[model tests](../test_inversion.py), [browser test](../scripts/verify_inversion_ui.cjs),
[native test](../scripts/verify_inversion_native.py). Actual results and failed
early checks are scoped in [validation](validation.md).
