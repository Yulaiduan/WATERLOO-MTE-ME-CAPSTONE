# Hip motor, reduction and losses

Andy Zhang / Codex, updated 2026-11-01. Experimental quarter-model assumptions; no
measured motor, gearbox efficiency or hardware rating is inferred.

The optional `motorConfig` is saved with project-v3, captured by both engines,
exported with each run, and part of comparison/stale-result identity. An absent
block retains the previous ideal actuator. Disabled blocks retain entered values
but apply none of their inertia, cogging or friction. No old profile is rewritten.
The freely backdriven wheel-drive shaft remains independent of the hip motor.

## Units and command basis

`gearRatio = N_g = ω_motor/ω_gearbox,out` is positive. The optional
`hipBeltRatio = B = ω_gearbox,out/ω_hip` ranges from1 to3; an omitted field
retains B=1 without rewriting the historical snapshot. Total reduction is
`N = N_g B`. A10:1 gearbox followed by a2:1 belt therefore gives20:1 overall.
The separate belt is an ideal rigid, lossless stage with no added hardware
inertia; pulley sizes, routing, compliance, strength and losses remain unknown.
It does not change the mechanism's three carrier belts, spring route or geometry.
Ideal rigid
gearing gives electromagnetic joint torque Nτ_motor and reflected rotor inertia
N²(J_motor + J_gear,input). The optional `gearboxInputInertiaKgM2` is the entire
gear train's input-equivalent inertia, reflected once. Existing
`hipRotorInertiaKgM2` is **additional joint-side** inertia;
existing `dampingNms` is **additional joint-side** viscous damping. Neither is
scaled again by the new gear ratio. Automatic candidate captures now store gear
input inertia in the motor block and only external output inertia in the legacy
joint field, preserving combined inertia without double counting.
Source gearbox output torque and speed limits apply **before** the added belt:
`τ_gearbox,out = τ_hip/B` and `ω_gearbox,out = B ω_hip`. Thus source gearbox
torque limits multiply by B at the hip, while its output-speed limit is checked
at B times hip speed. Motor input-speed limits use total N. The captured bounded
actuator stores the base gearbox `ratio` plus the same optional `hipBeltRatio`.
Legacy captures remain valid with B=1; old results retain their original settings.
Motor translational mass is not added to the
chassis or wheel; supported corner mass remains the builder's explicit input.

`commandBasis='joint'` preserves old terrain/jump/brake/search torque semantics.
Selecting `motor` explicitly treats these entered torques and ceilings as shaft
values and converts them through N. Energy-sized braking is calculated joint-side
and constrained by the converted ceiling; required shaft torque is reported
separately. Static-balance copy compensates cogging and converts to the selected
basis. Electromagnetic command, passive torques and net actuation are distinct.

Motor properties use SI units: J in kg·m², cogging/static-friction torques in N·m,
and viscous coefficient in N·m·s/rad. The static threshold is a torque, not the
wheel/ground friction coefficient μ or spring cable force. Zero values are
compatibility settings, not motor estimates. All signed torques follow +y.

## Conservative and dissipative laws

With q in radians, θ_motor=Nq, fixed phase reference q=0, cogging periods k per
rotor revolution and phase φ:

- τ_cog,motor = A sin(kθ_motor + φ)
- U_cog = A/k cos(kθ_motor + φ)
- Static joint capacity: T_s = N τ_s,m
- At rest: τ_dry is solved within [−T_s, +T_s] to maintain zero hip rate when feasible
- Sliding: τ_dry = −T_s sign(qdot), using the same magnitude by explicit assumption
- Joint viscous torque: τ_viscous = −N² b qdot
- T_drive = ½ (J_motor + J_gear,input) (N qdot)²

The owner changed the former Coulomb input to **static/breakaway friction** on
November1. Its saved compatibility key remains `coulombFrictionNm`, with the
same entered value and motor-shaft units. It includes the earlier lumped cogging
estimate, independent of angle; leave the separate periodic amplitude zero to
avoid counting that estimate twice. No separate kinetic value was supplied, so
the sliding dry magnitude equals the static threshold. Static holding does
zero work; this is not viscous damping or a motor holding command. The dynamic
tabs' explicit Apply buttons offer these unmeasured assumptions:

| Editable shaft assumption | Low | Medium | High |
| --- | ---: | ---: | ---: |
| Static/breakaway torque, also used for sliding (N·m) | 0.02 | 0.05 | 0.10 |
| Viscous coefficient (N·m·s/rad) | 0.0002 | 0.0008 | 0.002 |

Applying an example enables the physical motor block, preserves entered gearing
and inertia, and sets periodic cogging amplitude to zero. It preserves the old
`frictionVelocityScaleRadS` value solely for file compatibility; that hidden
field no longer smooths or changes the dry law. No existing profile is enabled,
given a new coefficient, or rewritten automatically. The retained
[nonideal study](nonideal-study.md) used the older smooth law and retains its
historical settings/results; it is not evidence for current static holding.

For legacy designs, the optional advanced periodic cogging model remains a
conservative sinusoidal detent. Its potential reference can
be negative; it is not lost energy. Sliding dry loss is the negative work of
the resolved dry reaction over actual physical angular travel; sticking loss
is zero. Viscous loss integrates N²b qdot² separately. Discrete positive dry
torque/displacement work is reported as `dryFrictionNumericalWorkJ`, an explicitly
numerical discrepancy rather than heat. Contact/projection and native constraint
accounting stay separate; their large individual terms may cancel.

Both contact engines solve bounded hip friction together with ground/stop
constraints. Analytical inverse mass couples the equal/opposite reaction into
chassis heave. Native finite rods use a passive zero-rate SimpleMotor; the
massless/rotor guide uses a bounded PinJoint with positional bias disabled.
These constrain relative motion only up to the entered torque capacity; neither
pins chassis height or binds the wheel to terrain. Signed native impulse
observation uses the verified Windows AMD64 Pymunk7.3.0/Munk2D ABI even when
rotor inertia is zero; unsupported native builds reject this path explicitly.
The ideal flat bench uses a bounded scalar impulse/event integration with its
transformed chassis equation. Breakaway and re-sticking are dynamical outcomes.

Active dry contact uses a500-sweep numerical budget. Native solves500 sweeps;
analytical projected-residual convergence can exit earlier. Requested and
resolved iteration information is reported. Native exact initial supported
tangency is rounded inward by one machine ULP to register contact immediately;
this is not a finite tire penetration or invented support force. Zero-capacity
and disabled-motor trajectories retain their previous numerical paths.

Integration rejects cogging phase advances above0.25rad per step, and rejects
underresolved explicit viscous relaxation using the reflected coefficient and
available effective inertia. Reducing output sample spacing alone does not fix
an underresolved integration step. Ripple and force plots are finite samples.

## Dynamics and contact impulses

The prescribed-height bench adds reflected rotor inertia to its generalized
mass and includes cogging potential, friction force and integrated losses in
both independent formulations. Nonzero inertia requires a finite input rise;
instantaneous prescribed pose jumps are not given an invented rotor impact law.

For straight-guide actual contact, with u=(h,s,ψ), axis=(a_x,a_z), s=s(q),
J=ds/dq and J_ref=J_legacy+N²(J_motor+J_gear,input):

`M = [[m1+m6, m6*a_z, 0], [m6*a_z, m6+J_ref/J², 0], [0,0,I_wheel]]`.

The analytical engine updates this mass matrix and its configuration derivative
for smooth forces, terrain impulses, travel stops and position projection. The
massless-link Pymunk branch adds a scalar rotational degree of freedom coupled through a
native constraint in the same contact/stop PGS solve; it does not add fake wheel
mass or wheel spin inertia. Its private-ABI support is explicitly version and
platform guarded: Windows AMD64, Pymunk7.3.0 and Munk2D
2.0.1-ade7ed72849e60289eefb7a41e79ae6322fefaf3, with64-bit pointers and double
precision. Unsupported native ABI rejects nonzero rotor inertia with an
explanation; the zero-inertia legacy path remains available. For two finite
uniform rods, the native branch instead adds the reflected drive moment to the
upper rod and uses the actual pivots/belt constraint. Its analytical counterpart
includes the same moment in the full finite-link generalized mass matrix.

Contact rows and event states now also contain exact per-step
`motorCoulombDissipatedJ` and `motorViscousDissipatedJ`, whose sum is the existing
`motorDissipatedJ` account. They are breakdowns, not additional ledger losses.
`rotorKineticJ` retains its legacy name but includes motor plus gearbox train
kinetic energy. Legacy ten-key motor snapshots preserve their exact saved shape;
an omitted gear-input inertia adds zero solely for compatibility.

Native rotor angle/speed residuals, numerical constraint work and energy-ledger
residuals must be inspected with timestep refinement. A signed coupled-constraint
kinetic-work estimate includes solver bias and force splitting; it is not a
measured contact or motor loss. When physical contact/stop loss cannot be
partitioned independently, those fields remain unavailable rather than zero.
Landing energy sizing includes post-impact rotor/chassis kinetic energy and
spring/gravity/cogging work; it remains an average-work screen, not a guaranteed
arrest or peak motor rating. Dynamic first-arrest search includes the full motor
model and retains its bounded-sampling limitations.

## Focused verification — 2026-11-01

Nine static-law groups check bound, exact-threshold sticking, breakaway, gearing,
work and coupled reaction. Nineteen bench/contact motor groups include dt-refined
bench work balance and passive landing. Twenty-one contact/rotor/work regressions
retain native ABI and contact-accounting checks. Eighteen independent actual V5
captures exercise both alpha values, modes and engines; measured hold/breakaway
outcomes are in [V5 designs](v5-suspension-designs.md). No profile is mutated.
The analytical capture diagnostic originally said minimum500sweeps; only that
caption was corrected to a500-sweep budget with projected-residual early exit.
The authentic captures are untouched and the single-literal source transition
is documented separately with an AST-equivalence check. A new diagnostic smoke
checks the corrected caption. Positive-only numerical dry work remains separate
from physical heat, not a signed correction invented to close the ledger.

## Sources

- [Modern Robotics8.9](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-9-actuation-gearing-and-friction/): ideal gearing, power transformation and N² reflected inertia.
- [MathWorks Rotational Friction](https://www.mathworks.com/help/simscape/ref/rotationalfriction.html): separate Coulomb/viscous units and smooth tanh regularization. This app omits its Stribeck term.
- [Pymunk constraints](https://www.pymunk.org/en/latest/pymunk.constraints.html): bounded constraint force/torque, zero-rate motors, positional bias and impulse reporting. The previous MathWorks smooth-law reference describes the historical implementation, not the current static constraint.
- Native engine/header provenance and tested ABI are recorded in `motor_rotor_constraint.py`; these do not imply compatibility with other Pymunk builds.
