# Contact dynamics, jump and landing studies

Updated2026-10-23. Experimental quarter model; editable study torques are not
hardware ratings. Both native dynamic tabs use the same saved builder geometry,
spring, masses, contact material, case and run settings. The original
prescribed-height benchmark remains a separate interaction mode.

## Two independent engines, one physical problem

The analytical contact engine does not call/import Pymunk. It integrates reduced
coordinates `u = (h, s, ψ)`, where h is chassis height, s is straight-guide
separation and ψ is actual free-wheel spin. In source right/up coordinates,
wheel position is `(a_x s, h + a_z s)`. The constant mass matrix is

```
M = [[m1+m6, m6*a_z, 0],
     [m6*a_z, m6,     0],
     [0,       0,     I6]]
I6 = 0.5*m6*rw²
```

The positive explicit chassis/wheel masses make M positive definite. There are
no substitute link masses. The analytical solver applies accumulated unilateral
normal/Coulomb tangential impulses to circle/rectangle/base geometry; spin is a
result of rim impulses. Pymunk separately integrates actual chassis and wheel
bodies, shapes and constraints. Geometry/material/controller helpers are shared;
the integration and constraint/contact implementations are independent.
See [MIT multibody notes](https://underactuated.csail.mit.edu/multibody.html)
for generalized mass/contact equations and [Box2D Solver2D](https://box2d.org/posts/2024/02/solver2d/)
for accumulated impulse clamping and the distinction between physical velocity
and position stabilization.

Both engines preserve the [bounded straight-path model](terrain-contact.md):
equal massless links,2:1 guide ratio, real uniform wheel inertia, free drive,
chassis x/pitch locked, rigid unilateral contact and zero bounce. Output contact
forces are impulse sums divided by the same output interval, not certified
continuous impact peaks. Comparison pairs common timestamps without moving one
engine's actual impact or takeoff time to match the other.

## Saved cases and controllers

Optional `caseConfig` extends project-v3. Old saved projects remain unchanged
when this block is absent; the resolved case is terrain-stability. Every run and
export captures the complete resolved case and material. Editing any physical,
case or numerical setting makes prior results stale.

- **Terrain stability:** existing translating square collision mesh, with actual
  separation, spin, friction and gap bridging. Dimensions/speed remain editable
  in the shared run profile.
- **Jump:** stationary flat floor, zero initial speed and fully compressed pose
  θ_c. The entered positive extension-torque magnitude commands torque toward
  decreasing θ₂ until the extension stop, then cuts off. Takeoff/apex arise from
  dynamics; a low entered torque may fail to jump. The inelastic extension stop
  transfers momentum and records its energy loss.
- **Landing:** stationary flat floor, zero initial velocity, wheel-bottom gap
  equal to the entered drop height. Initial pose is
  `θ_c + openingFraction*(θ_e−θ_c)`, default2/3. The motor compensates relative
  spring/external forcing during the held fall; hold torque is reported. First
  actual contact releases that hold. Entered braking resists compression and
  respects the entered ceiling. Energy-sized braking uses the explicitly scoped
  average-work estimate. Compression bottom-out before chassis arrest fails the
  landing criterion even if an inelastic stop prevents further motion.

Both engines use physical unilateral travel stops; no pose is teleported from
compression to extension. Case events, controller/motion phase, motor torque,
contact force, clearances and stop losses accompany playback. The user supplied
the editable underside offset50mm below hip A. Clearance is A height minus this
offset and terrain height under the hip; null explicitly means chassis strike
is unassessed. This threshold is not an invented chassis collision box.

## Energy sizing and braking requirement

The energy option reports requested chassis `½ m1 v_A²` separately from wheel
translation/rotation, spring energy, gravitational energy and inelastic stop
loss. Actual motor work is the signed trajectory integral `∫ τ_motor dθ₂`.
Positive work supplies energy; negative braking work removes it. Position
stabilization must be distinguished from physical work and checked by step
refinement.

For a vertical guide on a stationary flat floor, an average landing torque can
screen post-wheel-impact chassis energy plus gravity/spring work over remaining
compression. It is not a peak or a guarantee of arrest. Tilted guides require
the full trajectory and contact energy; the scalar vertical estimate is scoped
accordingly. The bounded torque assessment tests dynamic arrest with the selected
engine and reports the lowest passing tested value, a lower failing bracket and
all tested outcomes. Limited sampling, rebound, stops and timestep can make
feasibility nonmonotonic; this is not a certified global minimum.

Profiles remain in `profiles/library.json`; project/run/comparison/study exports
stay in `exports/`. Native desktop playback uses captured Pymunk case frames and
the same actual mesh. No new top-level tab, copied source UI or iframe is used.

## First wheel contact is different from chassis arrest

First contact constrains the wheel's normal motion against the floor. The
chassis can continue downward while the leg compresses; zero restitution does
not set the chassis velocity to zero. Chassis arrest is a later zero crossing
of its downward velocity. A travel stop can also arrest motion by impact, so
an arrest after bottom-out does not pass the landing criterion. Rigid-contact
impulses depend on the coupled inertia, geometry and numerical solver.
The reported first-contact event is the first wheel impulse. Analytical contact
can apply a speculative impulse just before the gap closes, so wheel normal
speed need not be exactly zero in that first event. Inspect its gap and
before/after velocities; compare event timing under timestep refinement.

Spring work is recoverable storage, not dissipation. With signed cable payout
`c` in metres and hip angle `q` in radians:

```
ΔUs = ∫ Fs dc = −∫ τspring dq
Wmotor = ∫ τmotor dq
Bmotor = −Wmotor
ΔK = Wmotor + Wdamping + Wterrain + Wexternal
     − ΔUs − ΔUg − ΔUc − motorLoss − constraintLoss
     + positionStabilization + unresolvedResidual
```

Positive `Bmotor` means net mechanical extraction; it is not automatically heat
or electrical regeneration. Negative spring-storage change means release back
into the system. Integrals follow actual signed displacement through reversals,
rather than total absolute travel. Contact/stop accounting, native coupled-rotor
constraint work, projection energy and the unresolved residual retain their
engine-specific meanings; they must not be counted twice as physical absorption.

The owner's requested ideal constant chassis support is `Fgc=m1*g`. Constant
cable tension is a different law. On a supported compression stroke ideal
gravity compensation removes exactly the gravitational work added by chassis
descent, leaving incoming kinetic energy for braking. The saved V4 linear
spring approximates that support but retains its actual finite-idler force law;
these plots do not silently replace it with an ideal compensation actuator.


## Actual numerical and UI evidence

App-local `verify_contact.py` passes8 original contact groups;
`verify_contact_cases.py` passes9 shared/Pymunk case groups;
`verify_analytical_contact.py` passes11 independent contact/case groups.
Flat normal100.5525N and steady spin28.6478898deg/s independently match gravity
and100mm/s divided by200mm. Frictionless spin stays0. Held landing follows
ballistic freefall before contact with constant pose and reported hold torque.
Spring-off100Nm extension motor work is113.44640138J = τ(θ_c−θ_e), with separate
stop loss; zero-torque negative control does not jump. Zero-brake landing
bottoms out and fails, while100Nm arrests the same spring-off case. Initially
intersecting undersides and reversed compression endpoint conventions are
rejected. Energy sizing/demand is unavailable on tilted guides; usable flat-floor
compression ends at the entered underside threshold when earlier than θ_c.

R100/H150 impossible-wall controls stop at the declared1mm penetration limit
in both engines, with partial results. The final R200 analytical default completes
6.5s/651samples with0.006285mm maximum preprojection penetration and negligible
postprojection penetration. Sustained bottom-out remains supported with normal
100.5525N; tilted endpoint momentum and refinement tests pass.

`verify_contact_comparison.py` confirms independent import (no Pymunk in the
analytical process),201 common samples for2s jump/landing and equal captured
hashes. Maximum chassis disagreement at dt0.0005/0.00025/0.000125s is
2.24675/1.38403/1.09242mm for Jump and4.85817/1.69714/0.910564mm for Landing.
These are converging numerical approximations, not exact equality. Pymunk's
reported impulse loss includes constraint-bias effects and leaves a nonzero
energy-ledger residual; the UI exposes it prominently. Analytical position
projection changes potential separately, never physical kinetic energy.

Actual browser tests find both engines arrest a100mm/20Nm landing. A200mm
energy-sized22.6905Nm near-boundary case arrests analytically but bottoms out in
Pymunk at dt0.00025s; the comparison warns that outcomes differ. This disagreement
is retained and requires refinement, not tuned away. The Pymunk bounded search
on the100mm case reports a tested10.938failing–12.5passingNm bracket from10trials.
An actual Tk/Pymunk jump playback self-test verifies pause/scrub/replay/auto-close;
browser native open/status/close also passes. Profiles/exports stay inside Capstone.


Torque assessment trials stop at the first arrest/failure criterion, rather than
integrating every settled trajectory to6.5s. Later rebound and full-duration
chassis safety still require a normal run. Focused tests compare the same
first-arrest criterion against complete runs in both engines. Actual10-trial
100mm searches take8.63s analytical/1.29s Pymunk on this PC and return the same
10.9375–12.5Nm local tested bracket; no portable throughput claim is made.
