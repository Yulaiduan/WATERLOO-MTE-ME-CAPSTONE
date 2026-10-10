# Model and coordinate map

Author: Andy Zhang with Codex. Updated: 2026-10-10. Status: experimental models and derived equations, not selected hardware.

## Related model layers

| Layer | Question | Coordinates |
| --- | --- | --- |
| Rough animation/path family | What path can a fixed-ratio guided leg draw? | q from downward vertical; x right, screen y down |
| Detailed JavaScript bench | How do guide, independent wheel drive, inertia, spring and impedance interact? | q from down vertical, φ independent drive input; world y up |
| Pymunk fixture | What are the actual solver loads and motion under prescribed disturbances? | θ from horizontal, knee opening α = 2θ; world x right, y up |
| Independent SciPy suspension | What motion and instantaneous loads follow the specified geometry and energy equation? | Same θ and y-up geometry as the guided physical fixture; analytic kinematics and adaptive ODE |
| Constant-lift lever | What equivalent lift follows a vertical-anchor zero-effective-length spring, and how does an ordinary coil differ? | Fixed O, anchor A=(0,H), lever B/C at radii R/L; θ from horizontal, y up |

For the zero-phase equal-link guide, `θ = π/2 − q`. The knee's relative signed angle is `−2q = 2θ−π`; its opening speed is `2 θdot`. The physical guide ratio is 2:1, but the equivalent absolute-angle Pymunk GearJoint is ratio −1 and phase π. It constrains the two link angles to counter-rotate; using an absolute gear ratio 2 would change the geometry.

## Fixed-pulley paths and inversion

With physical guide ratio ρ, link lengths L1/L2 and zero phase, the screen-down path is

```text
beta = (1 − rho) q
x = L1 sin(q) − L2 sin((rho−1)q)
y_down = L1 cos(q) + L2 cos((rho−1)q)
```

At 2:1 this becomes `x = (L1−L2) sin(q)` and `y_down = (L1+L2) cos(q)`: an ellipse for unequal links and an exact vertical line for equal links. A phase `2a` creates an equal-link straight line tilted by a: `beta = 2a−q`. One fixed tilted line has opposite below/above branches; below-left continues above-right. Exact below-left **and** above-left strokes require changed timing or a different path approximation.

The earlier two-position study indexes the hip pulley 24°, producing a 48° lower-link timing change while fully folded. The latest user constraint excludes that approach. The retained fixed-ratio example uses L1 = 250 mm, L2 = 168.449 mm and ρ = 4:1. It gives about 42.35 mm working travel with less than 0.768 mm perpendicular error from the 12° left rays, but full transition swings to the right and requires roughly 525° of relative knee rotation. These are geometric observations; joint travel, belt routing and wheel/chassis collision clearance are unresolved.

## Coaxial wheel drive

The guide controls leg shape. A separate coaxial drive input at the chassis passes through freely rotating compound pulleys at the knee. In the ideal two-stage 1:1 arrangement, wheel rotation relative to the chassis equals the input rotation at every fold pose. Relative to the lower link, wheel speed differs by the lower link's own angular speed. General nonunit stage ratios include carrier motion; a product of one alone does not guarantee cancellation. The [detailed model](linkage-model.md) retains the full equations.

## Link length, force and suspension

For equal links L, horizontal angle θ and hip-to-wheel separation h:

```text
h = 2 L sin(theta)
S = 2 L [sin(theta_max) − sin(theta_min)]
L/D = (S/D) / {2[sin(theta_max) − sin(theta_min)]}
```

If S equals wheel radius D/2, `L/D = 1 / {4[sin(theta_max)−sin(theta_min)]}`. The radius study is 150–250 mm, so diameter is 300–500 mm. This does not independently prove an obstacle of that height can be climbed.

Quasi-static vertical load W requires knee opening torque `T_k = W L cos(theta)`. Constant hip-equivalent torque gives `Fz = tau_hip/(2 L cos(theta))`; a direct knee torque gives `Fz = T_k/(L cos(theta))`. Projecting only a tangential force as `(T_k/L)cos(theta)` omits the other force component required by the vertically constrained mechanism. This distinction caused the initial intuition correction.

For constant torque, travel-average force is `tau_hip Δtheta/S` with radians. It is not a time or uniformly angle-weighted average. There is no useful suspension optimum from static force alone: speed, bump/droop reserve, load support, preload and structural constraints matter.

With knee opening motion ratio `J = L cos(theta)`, damping maps as `Cz = c_alpha/J²` and the unloaded stiffness contribution as `Kz ≈ k_alpha/J²`. A preloaded opening spring adds a geometric term:

```text
Kz = k_alpha/J² − tau_s L sin(theta)/(2 J³).
```

At the same link lengths, lower angles need more holding torque but less knee speed per vertical speed. Higher angles provide more compression reserve and less extension reserve; they increase motion sensitivity near straightening. At the same supported load, more upright links carry more axial compression and less transverse force/bending. These statements are scoped mechanics, not a blanket claim that a lower or higher angle is best.

## Pymunk spring and prescribed motion

The disturbance is **wheel-hub vertical position relative to its initial height**, corrected by the user on 2026-10-10. In the default floating fixture, a kinematic carriage drives a PivotJoint at the wheel COM (x held, y prescribed). The dynamic chassis has infinite rotational inertia to hold pitch while allowing heave. A 30 mm step with a 250 ms quintic rise is an illustrative default. For ramp fraction u, displacement fraction is `10u³−15u⁴+6u⁵`; velocity and acceleration are its first and second time derivatives, zero at both ends. Repeating square and single bump pulse inputs also support finite fall time. Linear ramps are selectable but have velocity jumps at joins. Instantaneous position jumps are rejected because they cannot yield finite velocity, acceleration or reaction loads.

The carriage is integrated with interval-average prescribed velocity rather than teleporting the dynamic body. Record both commanded/achieved height and tracking error. `driver_force` is the signed vertical force on the moving body (up positive), obtained from momentum balance and checked against the public constraint impulse magnitude. Negative support means this bilateral fixture would pull downward; real ground may lose contact. Changing spring stiffness changes chassis response, not the prescribed input. Input displacement is in metres internally and mm on screen; its time integral is m·s, not a force impulse.

Fixed-hip wheel motion and fixed-wheel chassis motion use a horizontal GrooveJoint that only imposes height, avoiding a redundant x constraint. The fixed-hip auto-preload design load (default 80 N) sets spring free length; it is not an additional applied force. Floating auto-preload supports the chassis/link weight. A constant wheel vertical bias is absorbed by the motion fixture and does not change floating-chassis spring preload. Constant external force biases remain separate optional loads; force and knee-torque excitation remain explicit legacy diagnostic modes.

### Physical spring and loads

The original lower rod extends e = 50 mm beyond the knee away from the wheel,
and the native DampedSpring joins the hip to that tip for `legacy_tip` with
captured/direct settings. With equal L, its anchor distance is
`sqrt(L²+e²+2Le cos(2θ))`; forces and moments use the actual anchor geometry.
Default masses/inertias and spring values are explicit assumptions. Spring
auto-balance chooses a free length for the initial load and pose; it is not an
invisible holding controller.

The [nine-preset catalog](suspension-presets.md) adds hip/knee pulley,
scissor, hip/knee bellcrank, chassis attachment, internal knee capture and
constant-lift gravity balance.
Coil law (compression, extension or bilateral captured) is independent of
transmission (direct, rigid pullrod or ideal rope). Increasing pull-through
input span decreases coil length; the corresponding leg motion follows the
selected attachment Jacobian or wrap direction. Ideal rope carries tension
only, with zero stretch and 100% transmission efficiency. Drums and crank arms
are massless ideal geometry; no transmission friction, coil bind, contact or
hardware packaging is resolved.

Except for the original captured/direct tip combination, Pymunk applies the
selected spring's equal-and-opposite forces at actual world anchor/tangent
sites before stepping the Space. Lever-arm torques and pin loads therefore
retain the transmission force path. These spring forces use explicit timestep
integration and require refinement for stiff/abrupt cases. Dead centres,
incompatible one-sided auto-preloads and nonpositive spans fail explicitly.

Hub loading gives no radius moment. Prescribed tire-bottom horizontal force gives `Fx r_w`; a free wheel spins, while a wheel drive locked relative to the lower link transmits `Fx r_w − Iw alpha_w` into the link. This lock is not the independent chassis-referenced 1:1 drive model and does not create ground contact. Rotary-stop impulse peaks remain timestep dependent. Geometry shapes are sensors: no tire collision, rolling/slip, terrain, belt elasticity or beam stress is solved.

Joint resultants are Pymunk impulse/dt. Signed vectors are reconstructed from COM momentum and checked against those resultants. Guide/stop/drive torques are reconstructed from angular momentum and checked against engine impulses. Pin joints themselves are free hinges. All three pins have world-point velocity/acceleration, and knee relative and link angular motion are retained.

## Reference sheet and units

The [equation cross-check](equation-cross-check.md) preserves distinct T₀ and T terms and `Fy r_w`. Its reported torques at 0°/42° are reproduced with conditionally inferred equal 400 mm links and a 200 mm wheel, not the default 273 mm fixture. T₀ affects reference bearing loads but cancels from the visible upper-link moment. Its numeric value, tight/slack role and pulley radius remain unknown; the ideal guide does not resolve explicit belt-span bearing loads.

Internal units are m, kg, s, rad, N and N·m. Force displays also show kgf with `1 kgf = 9.80665 N`, independent of the configured gravity value. A user-entered T₀ starts unspecified and is saved as a reference-only quantity, not silently applied to the physics solver.

## Independent mathematical suspension model

The [Python/SciPy model and MATLAB companion](../math/README.md) derive the scalar
equal-link energy equation independently of Pymunk and reconstructs
instantaneous Newton–Euler forces. It is distinct from solver impulse/dt loads
and from the two-coordinate JavaScript drive model. Adaptive integration,
exact imposed kinematics and pre-impact stop termination have their own
interpretation; [the unified workflow](unified-motion-lab.md) keeps these
boundaries visible in browser comparison/data exports.
SciPy supports all nine spring mechanisms. MATLAB currently supports only the
original `legacy_tip` captured/direct spring; it rejects other topology/law/
transmission combinations. A mathematical travel-limit event ends the run
before impact, while the physical fixture resolves a stop impulse. Neither
behavior establishes tire contact, terrain response or hardware suitability.

## Constant-lift geometry and wheel mapping

The [standalone derivation](constant-lift.md) uses O=(0,0), A=(0,H),
B=R(cos θ,sin θ) and C=L(cos θ,sin θ). Span `d` obeys
`d²=H²+R²−2HR sin θ`; zero-effective tension `T=k*d` gives spring moment
`kHR cos θ` and equivalent upward tip force `kHR/L`. This cancels gravity for
`kHR=gL(m_payload+m_lever/2)`, including uniform lever weight. Tension and
torque vary with angle; equivalent force is undefined at vertical singularity.
A positive physical coil free length is preserved through ideal routing/preload
emulation, rather than assuming an ordinary coil obeys this input force law.

For `gravity_balance`, the chassis mount is downward by H relative to the hip
and the upper-link attachment lies R from that hip. The mirrored geometry
gives the same span identity. With `h=2L sin θ`, generalized elastic chassis
lift is `kHR/(2L)` and required support is
`g[m_chassis+0.75m_upper+0.25(1+e/L)m_lower]`. Zero-effective automatic balance
calibrates stiffness; Hooke automatic balance continues to calibrate free
length/preload. Horizontal mount offset, nonzero effective input free length
and damping break exact constant elastic lift. The fully calibrated undamped
case is neutral, so it supplies gravity compensation without restoring ride
height or a complete suspension.

The [two-stage architecture](suspension-architecture.md) adds an independent
hip-to-lower-extension strut. Its energy and generalized force add to the gravity
stage, and pin-force/moment ledgers include both sets of actual force sites.
Automatic auxiliary free length gives zero elastic force at the initial pose;
captured behavior restores either side. Per-stage telemetry stays separate.
