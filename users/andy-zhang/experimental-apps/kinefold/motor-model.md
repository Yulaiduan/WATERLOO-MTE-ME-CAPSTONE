# Hip motor, reduction and losses

Andy Zhang / Codex, updated 2026-10-30. Experimental quarter-model assumptions; no
measured motor, gearbox efficiency or hardware rating is inferred.

The optional `motorConfig` is saved with project-v3, captured by both engines,
exported with each run, and part of comparison/stale-result identity. An absent
block retains the previous ideal actuator. Disabled blocks retain entered values
but apply none of their inertia, cogging or friction. No old profile is rewritten.
The freely backdriven wheel-drive shaft remains independent of the hip motor.

## Units and command basis

`gearRatio = N = ω_motor/ω_hip` is positive, with direct drive N=1. Ideal rigid
gearing gives electromagnetic joint torque Nτ_motor and reflected rotor inertia
N²(J_motor + J_gear,input). The optional `gearboxInputInertiaKgM2` is the entire
gear train's input-equivalent inertia, reflected once. Existing
`hipRotorInertiaKgM2` is **additional joint-side** inertia;
existing `dampingNms` is **additional joint-side** viscous damping. Neither is
scaled again by the new gear ratio. Automatic candidate captures now store gear
input inertia in the motor block and only external output inertia in the legacy
joint field, preserving combined inertia without double counting.
Motor translational mass is not added to the
chassis or wheel; supported corner mass remains the builder's explicit input.

`commandBasis='joint'` preserves old terrain/jump/brake/search torque semantics.
Selecting `motor` explicitly treats these entered torques and ceilings as shaft
values and converts them through N. Energy-sized braking is calculated joint-side
and constrained by the converted ceiling; required shaft torque is reported
separately. Static-balance copy compensates cogging and converts to the selected
basis. Electromagnetic command, passive torques and net actuation are distinct.

Motor properties use SI units: J in kg·m², cogging/Coulomb amplitudes in N·m,
viscous coefficient in N·m·s/rad and smoothing speed in rad/s. Zero values are
compatibility settings, not motor estimates. All signed torques follow +y.

## Conservative and dissipative laws

With q in radians, θ_motor=Nq, fixed phase reference q=0, cogging periods k per
rotor revolution and phase φ:

- τ_cog,motor = A sin(kθ_motor + φ)
- U_cog = A/k cos(kθ_motor + φ)
- τ_friction,motor = −F_c tanh(ω_motor/ω_epsilon) − bω_motor
- T_drive = ½ (J_motor + J_gear,input) (N qdot)²

The owner's October30 comparison explicitly **lumps cogging into constant
Coulomb resistance**, independent of angle, and sets the separate periodic
amplitude to zero. This is a dissipative engineering approximation, not a
measured cogging waveform. The dynamic tabs' explicit Apply buttons offer:

| Editable shaft assumption | Low | Medium | High |
| --- | ---: | ---: | ---: |
| Coulomb resistance, including cogging estimate (N·m) | 0.02 | 0.05 | 0.10 |
| Viscous coefficient (N·m·s/rad) | 0.0002 | 0.0008 | 0.002 |

Applying an example enables the physical motor block, preserves entered gearing
and inertia, sets periodic cogging amplitude to zero, and uses shaft smoothing
speed10rad/s for a broad, stable illustrative transition. All fields remain
editable. The retained [nonideal study](nonideal-study.md) explicitly narrows
that transition to0.5rad/s with a checked0.25ms timestep; resistance approaches
constant magnitude away from zero. It opposes motion rather than changing sign
with angle. No static stiction or breakaway model is added.

For legacy designs, the optional advanced periodic cogging model remains a
conservative sinusoidal detent. Its potential reference can
be negative; it is not lost energy. Smooth Coulomb regularization does not solve
static stiction, breakaway or a Stribeck curve. Friction loss power is nonnegative
−τ_friction,motor ω_motor; cumulative motor loss stays separate from joint
damping, wheel contact loss and numerical constraint/projection work.

Integration rejects cogging phase advances above0.25rad per step, and rejects
underresolved explicit drag relaxation using the reflected near-zero slope and
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

## Sources

- [Modern Robotics8.9](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-9-actuation-gearing-and-friction/): ideal gearing, power transformation and N² reflected inertia.
- [MathWorks Rotational Friction](https://www.mathworks.com/help/simscape/ref/rotationalfriction.html): separate Coulomb/viscous units and smooth tanh regularization. This app omits its Stribeck term.
- Native engine/header provenance and tested ABI are recorded in `motor_rotor_constraint.py`; these do not imply compatibility with other Pymunk builds.
