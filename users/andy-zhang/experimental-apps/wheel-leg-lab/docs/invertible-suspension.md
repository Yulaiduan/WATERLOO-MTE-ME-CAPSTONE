# Invertible dual-rope and symmetric knee suspension

Andy Zhang with Codex,2026-10-11. Status: editable member experiment, not selected
hardware or canonical robot validation. Source: user's attached sketch and
clarifications in this task: one cap/one loaded rope, actual±5°attachment points,
two small routing pulleys near the knee, and bellcrank spring mount50mmfromJ1.

## Three pulleys, one compression cap

The new dual-rope design has one knee drum and two real routing pulleys on the
femur. The red/blue parallel feeds attach to a yoke on one rigid piston rod.
The cylinder axis is parallel to r1. The routing pulleys keep those input runs
linear; they are deliberately part of this new design, unlike the rejected
extra idler in the earlier single-rope symbol.

Demo dimensions are273mm links,50mm lower extension,200mm wheel radius,
40mm knee drum,10mm routing radii, centres60mm before knee and±35mm to either
side. The rod-eye reference is100mmfromJ1, rod length120mm, physical coil free
length120mm and preload compression10mm. The schematic housing consequently
extends20mm past J1 at its reference cap position; mounting fit is unverified.
All these dimensions are editable demonstrations.

For relative knee opening `phi=2theta`, attachments rotate at `phi±delta`.
The geometry code evaluates visible straight connections, circle tangent
segments and surface arcs around the assigned routing pulley and knee drum.
It selects the shortest admissible external path without crossing the other
routing pulley. Overlapping pulley circles are rejected. This is ideal routing
without rope winding/groove/crossover history, stretch, friction or binding.

Let `ell_i(phi)` be the downstream route length; the parallel input span shortens
by the same cap displacement for both ropes. Neutral references are measured
at a straight knee, `phi=pi`:

```text
x_i = ell_i(phi) - ell_i(pi)
x = max(0, x_red, x_blue)
z = preload + x; coil_length = free_length - z
U = 0.5*k*z^2
F_cap = max(0, k*z + c*dx/dt)
Q_theta = -F_cap*dx/dtheta
```

Only the active cable has tension `F_cap`; the other has zero tension and its
slack is `x-x_i`. Ties use the outgoing branch (deterministic red at rest).
At zero take-up a mechanical preload/reference stop reacts internal coil force;
it is not a controller. Energy and cap position remain continuous at ordinary
handoffs while derivatives can be nonsmooth. The opposite upper/lower force
pair at actual cable tangent/contact points reproduces virtual torque and pin
loads. There are no separate invented spring energies for red and blue.

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
Default rates are about5617.83N/m dual-rope and5116.73N/m bellcrank. The default
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

Code: [geometry](../invertible_spring.py), [solvers](../inversion.py),
[model tests](../test_inversion.py), [browser test](../scripts/verify_inversion_ui.cjs),
[native test](../scripts/verify_inversion_native.py). Actual results and failed
early checks are scoped in [validation](validation.md).
