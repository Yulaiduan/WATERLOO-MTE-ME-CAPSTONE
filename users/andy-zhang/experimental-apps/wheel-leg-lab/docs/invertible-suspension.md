# Invertible dual-rope and symmetric knee suspension

Andy Zhang with Codex,2026-10-11. Status: editable member experiment, not selected
hardware or canonical robot validation. Source: user's attached sketch and
clarifications in this task: one cap/one loaded rope, actual±5°attachment points,
two small rollers near the knee, and bellcrank spring mount 50 mm from J1.
The later clarification replaces the initial outside-wrap prototype with central
feeds and outward flare. The latest clarification requires knee-rim wrap and
supersedes the earlier no-wrap interpretation. The subsequent correction puts
the attachments on the cylinder-facing side at full contraction, with zero
preload and zero spring force in that pose.

## Three pulleys, one compression cap

The current dual-rope design has one knee pulley and two small rollers on the
femur. The cylinder axis is parallel to r1. Red/blue ropes leave close-set eyes
on one rigid piston rod's yoke, run through the central gap between the rollers,
and flare onto tangent spans and rim arcs to the actual ±5° attachments.
The cable follows the knee circumference instead of crossing its material. These two rollers are part of this new
design; the earlier single-rope mechanism still has no added piston idler.

Demo dimensions: 273 mm links, 50 mm lower extension, 200 mm wheel radius,
30 mm knee attachment radius, 10 mm rollers, centres 60 mm before the knee and
±10.1 mm to either side. The ideal gap is 0.2 mm; rope eyes are ±0.02 mm from the cylinder
centreline. The rod-eye reference is 100 mm from J1, rod length 130 mm, physical
coil free length 120 mm and preload compression 0 mm. The schematic housing
extends 30 mm past J1 at its reference cap position; mounting fit is unverified.
All dimensions are editable demo inputs. Wrapping increases cable travel; the
30 mm drum fits the existing 120 mm coil and rod-eye mount. A 40 mm drum with
those dimensions exhausts cap travel and is rejected rather than clipped.
The gap input keeps its value when roller radius changes.
Current session migration updates the requested roller/pose settings while
retaining link, wheel, mass and input settings; saved records are unchanged.

For knee opening `phi=2theta`, current face attachments rotate at
`phi+pi±delta`. At full contraction `theta=0`, r1/r2 are parallel and both
anchors lie on the left side of the knee drum toward the cylinder. No automatic
anchor switching or relocation occurs during a run; they rotate rigidly with r2.
The reference cable inventories are measured in this folded pose.
Geometry evaluates straight paths only when they clear the knee circle,
plus tangent/arc paths over the small rollers and around the knee drum.
Common circle tangents join roller exit to knee contact; the remaining rim
arc ends at the rotating anchor. Candidates cannot cross pulley material or
bypass the outside of the central roller gate. A cable can lift off the rim
when its attachment directly faces the cylinder. Current central_wrap uses
this contact geometry; explicit central_face preserves the previous no-wrap
study and outer_rim preserves the original external-feed prototype.
Axle/groove/rope-crossing clearance, friction, stretch and winding history are
unverified. Shortest ideal routing does not model captured multi-turn winding.

Let `ell_i(phi,x)` be the full cable length from the moving cap eye to its
face anchor. Current neutral inventories are measured at `phi=0, x=0`. Each rope's
positive cap demand is solved from that inventory, then one common cap follows
the larger demand:

```text
ell_i(phi,x_i) = ell_i(0,0)  [solve when positive take-up is needed]
x = max(0, x_red, x_blue)
z = preload + x; coil_length = free_length - z
U = 0.5*k*z^2
F_cap = max(0, k*z + c*dx/dt)
lead_cosine = incoming cable direction dot cylinder axis
dx_i/dtheta = 2*(partial ell_i / partial phi)/lead_cosine
T_active = F_cap/lead_cosine; T_other = 0
Q_theta = -F_cap*dx/dtheta
slack_i = ell_i(0,0) - ell_i(phi,x)
```

While wrapping, `partial ell_i / partial phi = ±R`; rim arcs contribute real
cable length and torque. Angled leads require slightly more tension than cap force. Ties use the
outgoing branch, with deterministic red at rest. At zero take-up a mechanical
preload/reference stop reacts internal coil force; it is not a controller.
Energy and cap position are continuous at handoffs; derivatives can be
nonsmooth. Equal/opposite forces along the outgoing tangent span reproduce virtual torque
and pin loads. The lower force at the rim contact represents the aggregate
wrapped-drum/anchor reaction; a duplicate anchor force is not added. The upper
force aggregates its massless cylinder/roller reactions. Red and blue do not have separate spring energies.

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

The separate full-angle fixture starts at `theta=-45deg`, with chassis centre
27.5mm above the flat floor and the wheel above it. Pymunk uses real wheel and
chassis contacts: heave/translation are free, chassis pitch is held, and the
2:1 guide keeps absolute upper/lower angles summing to minus pi. No wheel height
is prescribed. The links/transmission use sensor geometry; self-collision is
disabled to represent staggered lateral planes. No3Dclearance claim follows.

Default angle stops are θ=-80° and +80°, with initial |θ|=45°. Therefore
`x_knee-x_hip=L*cos(theta)>0`: the knee stays right while the wheel changes
from above to below the chassis. Pymunk adds a real RotaryLimitJoint between
chassis and femur (five total constraints); recorded poses are not clipped.
Numerical stop overshoot is reported by the real solver. Current defaults use
400 iterations to keep the original guide-error budget through impacts. Runs
that overshoot far enough to move the knee left fail explicitly. Old saved
profiles without stop metadata reproduce their unrestricted configuration.

Clockwise femur torque is positive in the UI: upper body gets `-tau` and chassis
gets `+tau` in world counterclockwise coordinates. Demo input is100Nm with
40ms quintic rise/fall, starting at100ms. Pulse width is240ms dual-rope and
170ms bellcrank; default recording is1s at0.25ms Pymunk steps. These are toy
inputs, not motor ratings. Default cap damping is zero. Release can rebound,
fly briefly or rotate further; the recording does not freeze at a target pose.

For the folded-neutral dual ropes, opening in either direction increases cable
demand and coil compression. The spring resists opening and attracts the leg
toward contraction. With zero preload, full contraction gives exactly zero coil
compression, cap force, cable tension, spring energy and spring torque. A manually
entered preload stores internal spring force at the reference stop and forfeits
the zero-cap-force assumption. Default rod length is130mm to keep its eye outside
the full120mm unloaded coil; the previous120mm rod relied on10mm preload.

Automatic rate for this current geometry matches the **magnitude** of the
gravitational torque at45deg, using distributed link/corner weight. It does not
balance gravity: in the normal pose gravity and spring both tend to close the
leg. The UI explicitly labels this distinction; the spring cannot hold a passive
ride height by itself. Current dual-rope k is13542.156N/m. The unchanged
bellcrank still uses10mm preload and its existing signed gravity calibration
(k5116.73N/m). The default
ground flips are observed, not scripted angle trajectories. Step size must be
refined before interpreting contact/load peaks.

## Independent angular mathematics

SciPy and the matched physical comparison hold J1, without floor contact. They
integrate angle directly, avoiding the height-Jacobian singularity at90deg.
Between stops, ideal equal-link kinematics give the positive effective inertia

```text
M(theta) = I_upper+I_lower + m_upper*L^2/4
 + m_lower*((L+e)^2*sin(theta)^2+(3L-e)^2*cos(theta)^2)/4
 + 4*m_wheel*L^2*cos(theta)^2
M*theta_ddot + 0.5*M'*theta_dot^2 = tau + Q_spring + G*cos(theta)
G = gravity*(m_upper*L/2 + m_lower*(3L-e)/2 + 2*m_wheel*L)
```

The independent angular integrator uses terminal angle events for zero-
restitution impacts, adding loss `0.5*M*omega_before^2` to its energy ledger.
At a loaded stop it remains at rest until free acceleration points inward.
This is a unilateral rigid constraint, not a controller or added damper.
Mathematical stop torque reports continuous holding reaction; its ideal impact
has no finite peak torque. Pymunk reports actual step-averaged stop impulse/dt.
With stops enabled, its mechanical_energy_minus_work_J includes unisolated
constraint-impact losses and is not labeled a closed energy-error ledger.

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

New configs store `rope_routing=central_wrap`, rope-eye offset and editable
angle_limit_enabled/angle_min_deg/angle_max_deg. Current demo lead angles are
within about 0.25° of the cylinder axis; the ideal model does not assume a
measured cable diameter or certify fit through the 0.2 mm ideal gap.
Saved pre-correction profiles are resolved to explicit `outer_rim` reproduction
on import/library execution/native launch; their original JSON and recorded
frames are not modified. The current UI labels those profiles as archived and
offers Load selected flip demo for the corrected route. Current session migration adopts central_wrap, the tighter gap, 30 mm demo
drum and knee-right bounds;
older saved profiles retain their unrestricted angles for reproduction. Direct API configs without a
routing marker use the corrected default; legacy API reproduction must select
`outer_rim` explicitly with its old dimensions and `angle_limit_enabled=false`.
Archived central_face profiles retain their prior no-wrap geometry. Profiles
from before the stop update likewise require explicit false
to reproduce their unrestricted trajectory.

Code: [geometry](../invertible_spring.py), [solvers](../inversion.py),
[model tests](../test_inversion.py), [browser test](../scripts/verify_inversion_ui.cjs),
[native test](../scripts/verify_inversion_native.py). Actual results and failed
early checks are scoped in [validation](validation.md).

## Saved-profile compatibility: folded reference correction

`rope_neutral_pose=folded` is the current dual-rope default. `straight` retains
previous anchor angles `phi±delta`, inventory at `phi=pi` and any saved preload.
Browser/native saved-profile resolvers fill a missing marker as `straight`,
with the historical10mm preload/120mm rod when absent. Current session settings
without this marker migrate to folded with zero preload; the old demo120mm rod
becomes130mm. Other parameters remain remembered. Existing saved JSON/frames
are never rewritten. Both explicit neutral-pose variants are selectable.

A0deg initial angle is accepted for fixed-J1 reference studies. A normal ground
start at0deg places J1/wheel centre at wheel radius; an inverted floor start
at0deg is rejected if it would put the wheel through the floor.
