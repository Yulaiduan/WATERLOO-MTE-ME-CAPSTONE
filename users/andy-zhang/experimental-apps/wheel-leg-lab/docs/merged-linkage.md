# General linkage in the original suspension bench

Author: Andy Zhang with Codex. Updated: 2026-10-14.
Status: experimental analytical/dynamic fixture; no canonical robot or hardware claim.

The owner corrected the first integration: add Jonathan's tooling to the original
Math and 2D Physics solvers. This implementation supersedes the separate editor
introduced at `c8b3c8b`. Open `/?tab=math` or `/?tab=physics`, then select
**Geometry → Editable links · three carrier belts** in the existing controls.
The default **Original equal-link 2:1** model keeps its previous equations,
spring presets, position driver, plots, profiles, comparison and native viewer.

## Controls and reference analysis

The editable design has independent L2/L3, four ratio/dimension triplets with one
driven variable and swap, and the straight/spin/cancel presets. It adds all six
pitch radii, clockwise mounting alpha, lower-link phase phi0, compound mass m5
and rim-inertia radius, three slack-side preloads, beta, signed global Fy/Fz or
normal/tangential Fn/Ft, and beta bounds for headline maxima. Existing wheel
radius, masses, gravity, theta bounds, spring geometry/law, knee impedance and
smooth prescribed height remain the same bench controls. Presets change geometry
only, preserving spring, input and mass settings. Changing force convention
preserves the current world force; a beta sweep then holds the chosen components.

The embedded audit runs the exact three analytical scripts from
[Jonathan's v2](../../../../jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html).
[His model record](../../../../jonathan-xie/experimental-apps/leg-solver/v2-model.md)
owns the tangent-span, equilibrium and preload assumptions. The build copies
only those functions, with source/model SHA-256 hashes; it does not copy his
editor. Five FBDs and their force/direction tables, twelve loading plots, three
geometry plots, current values and four bounded global maxima use those functions.
Maxima search theta2 × beta within the selected bounds with alpha held at its
current value; the source reports attained poses and a 0.001-unit error gap.
Travel directions use atan2(horizontal, vertical); zero displacement is undefined,
and plots break at angle branch cuts. Displacement plots retain parametric branches.

Reference CSV/library data has four explicit parameter tables, source units and
provenance. It has no simulated time axis or runnable configuration. Original
v1/v2 parameter JSON imports map mm to metres and source angles into the existing
SI profile; profile/run JSON and dynamic CSV retain the original backend identity.
Source zero masses remain zero: statics still works, but a dynamic Run requires
positive chassis/link/wheel masses and an initial theta strictly inside its stops.
Only m5 can be massless, in which case no dummy body/inertia is inserted. A file
without a current theta uses the middle of its explicitly supplied working range.

## Coordinate and dynamics cross-check

In this bench world x/y corresponds to source global y/z, with y upward. The
original bench theta is measured from horizontal; source theta2 = pi − theta.
For q = bench theta in radians, a = alpha, p = phi0 and k = qab − 1:

```text
upper world angle = -q - a
lower world angle = k*q + p - pi - a
compound world angle = (qcd-1)*(q-theta_max) - a
wheel world angle = -K*(q-theta_max) - a
K = 1 - qab + qef*(qab-qcd)
relative knee speed = qab*qdot
```

`linkage_geometry.py` provides C-relative positions r_i(q), first/second
derivatives and body-angle derivatives s_i. The original wheel carriage prescribes
C = (0,z(t)); the hip translates in both axes while its pitch is held. Uniform
rods use mL²/12, the full lower rod includes the existing extension, and the general
wheel/compound use Jonathan's thin-rim mr² assumptions. Original mode retains
the prior disk-wheel inertia. Shared geometry does not share an integration engine.

```text
M(q) = sum(m_i |r_i'|² + I_i s_i²)
M'(q) = 2 sum(m_i r_i'·r_i'')
Gy(q) = sum(m_i r_i,y')
M*qddot = -T*J + qab*tau_knee - K*Mw
           - Gy*(g + zddot) - 0.5*M'*qdot²
J = d spring-input-length / dq
Mw = rw*Ft at the specified patch; zero at the hub
```

SciPy DOP853 integrates this direct angle equation without importing Pymunk.
The existing spring catalog computes its actual attachment leverage, preload and
force law, with generalized hip/knee cable payout. Local ride stiffness uses the
general path's height Jacobian, excluding feedback/damping; it is unavailable at
a height turning point. Exact constant lift is not claimed after editing geometry.
Mathematical travel events end before impact, as in the original bench.

Pymunk builds actual unequal rod bodies/pivots and independent compound/wheel
GearJoints, and steps the original point-force spring and prescribed carriage.
It handles unity guide and zero wheel-spin coefficients without singular gears.
Newton–Euler reconstruction uses measured body accelerations and actual applied
spring/controller loads; resultant pin forces and gear/stop torques are checked
against impulses/dt. Chipmunk's GearJoint impulse gives torque on its second body;
applying the symmetric 2:1 scaling to a general ratio would be incorrect.
Physical energy uses actual COM velocities/positions/spins and current spring
geometry. Applied spring force channels are sampled before each solver step;
energy/pose channels are sampled after it. Refine dt for comparisons or peaks.

## Physical boundaries

Jon's audit holds A fixed, with m1 at A and m3 at the B/C midpoint. The dynamic
fixture has a moving chassis, spring and acceleration, and retains the full
lower extension/COM. Thus its actuator loads and bearing reactions should not
equal the displayed fixed-A reference values. The geometry and source holding
torques are independently checked, rather than comparing unlike fixtures.

The dynamic guide/drive are ideal equivalent angular constraints. Source
preloads and exact span forces change the **reference** bearing/FBD loads; the
dynamic constraints do not apply physical belt-span bearing forces. No belt
elasticity, motor-shaft freedom, unilateral tire contact or rolling is solved.
The wheel patch is a specified applied-load point, not a terrain contact model.
The general fixture requires floating support, one primary point-force spring
and no legacy wheel lock/auxiliary strut. Existing old fixture modes remain
available under Original geometry. MATLAB remains original-tip-only.

The native viewer builds this same Pymunk fixture, draws all three carrier belts
using actual body poses, and exposes its real constraint ratios/compound body.
Separate belt planes, 3D clearance, tire/soil physics, hardware inputs, GPU and
other operating systems remain unverified. The historical rejected dual-rope
inversion design and separate offline design report are unchanged.

## Reproduction

From this app, use installed runtimes and the existing manual Start/Stop Motion
Lab.cmd at loopback4186. Rebuild after Jonathan source changes:

```sh
npm run build
npm test
.venv/Scripts/python.exe -m unittest -q test_generalized_linkage
node scripts/verify_merged_linkage.cjs
```

The generalized tests execute Jonathan's original source via Node for 288
deterministic varied poses and independently verify holding torque, world
coordinates/angles, force conversion and inertia. They also recover the original
2:1 dynamics, finite-difference geometry/spring/energy derivatives and demonstrate
actual Pymunk timestep refinement. See [validation](validation.md) for exact
commands/results and the scope of browser/native verification.
