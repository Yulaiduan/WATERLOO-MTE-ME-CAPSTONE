# Independent actuator calculator

Owner: Andy Zhang with Codex. Updated: 2026-10-29.
Status: preliminary component and analytical screening, not a hardware rating.

The **Actuator calculator** tab reads the mechanism profile's geometry, mounting
angle and masses. Motor/SO gearbox choices and the calculator's example inputs
stay separate from physical `motorConfig`, saved dynamic runs and the older
chassis-only Energy tab. It recalculates without calling either dynamics engine.
Only an explicit export writes a calculation artifact into this app's `exports/`.

## Sources and V4.5

The read-only [motor comparison sheet](https://docs.google.com/spreadsheets/d/1ttHpUltfZHpnzD9DO-fUXWn_x426xmtnoujWum3Lag4/edit)
provides **Pure Motor Rev2** (`gid=1825746970`), **SO Gearbox Index**
(`gid=20261027`) and **Rev2 Inertia Model** (`gid=202610300`). The offline snapshot
preserves row identities, source links, units, estimate status and missing values.
All motor rated/no-load RPM cells are blank. A user-entered speed or labelled
example assumption is necessary for a speed/time prediction. Rotor inertias
come from the name-matched assumed geometry/material model; its scenario bounds
are not statistical confidence intervals. Do not reuse misaligned old inertia
cells or infer a measured rotor inertia from whole motor mass.

The referenced private ChatGPT conversation was not readable through the available
tools. Equations below are explicit derivations, not a transcription of that chat.

**V4.5** adds a 1 kg upper link (`m2`, user's first leg link), 1 kg lower link
(`m3`, user's second link) and 0.5 kg wheel (`m6`) to the original V4 geometry.
Corner chassis mass stays 8.75 kg and knee compound mass stays zero: total single
corner mass is 11.25 kg. Uniform rods represent the links. Alpha remains 0 degrees
in the reference template and remains editable. The original V4 spring stiffness,
preload and cable geometry are retained, without retuning gravity compensation.
The portable [V4.5 profile](saved-configurations/vsl-v45-nominal-alpha0.json)
has its own identity; original V4 files are unchanged. Use the studio's reference
templates to open a new V4.5 working copy and save it under any name.

Finite-mass prescribed-height dynamics needs a declared smooth transition: the
template retains 150 mm height/plateau/gap with 10 mm C2 transitions. Existing
actual-contact engines still require massless links and reject V4.5 link masses.
The original Energy tab's massless-link endpoint equations retain their guard.
The independent actuator calculator supports the new masses without claiming
that either existing contact engine has gained rigid-link dynamics.

## Inertia, torque and acceleration

The coordinate is the saved hip angle `q = theta2` in radians, increasing toward
compression. The ideal belt constraint gives lower-link absolute angular-rate
ratio `k3 = 1 - ra/rb`; the knee compound uses `k5 = 1 - rc/rd`.
All positions and derivatives are rotated by the saved mounting alpha before
world heights or velocities are evaluated.

For body centre `r_i(q)`, COM inertia `I_i` and angular-rate ratio `k_i`:

```text
J_leg(q) = sum_i [m_i |dr_i/dq|² + I_i k_i²]
I_rod = m L²/12
J_drive = N² (J_motor + J_gear,input) + J_gear,output
N = motor speed / hip speed
tau_drive = efficiency × N × tau_motor
J qdd + 0.5 J_prime qdot² = tau_drive - tau_loss - dU/dq
```

The selected gearbox output is assumed to drive the hip directly, with no
additional external reduction. The leg's pulley ratios define internal link
motion separately from this motor-to-hip ratio.
Efficiency does not multiply inertia. An input-equivalent gearbox inertia is
reflected once, not counted again as independent output inertia. Source gearbox
`kg cm²` converts to `kg m²` with a factor of `1e-4`. Missing gearbox inertia must
remain unassessed or be omitted only as an explicit editable example assumption.
Free wheel spin is an independent coordinate and adds no forced spin energy to
this one-coordinate screen; wheel translational inertia remains present.

Motor/gearbox housing mass is not automatically added to the profile's fixed
chassis mass. Include installed actuator masses in the chassis budget when
editing a physical design; source catalog mass remains comparison context.

The fixed-hip acceleration screen has an explicit exact-gravity-balance assumption.
It measures how quickly a free leg can be moved; it is separate from a grounded
chassis launch. With equal 300 mm V4.5 links and a free wheel, a useful independent
fixed-hip check is `J_leg(q) = 0.06 + 0.36 cos(q)² kg m²`: at 135 degrees it is
`0.24 kg m²`. Rotating the entire fixed-hip mechanism by alpha cannot change that
inertia, although the unbalanced gravitational torque changes.

Motor peak and gearbox nominal/momentary output ratings remain separate. A
linear torque decline from entered peak to entered no-load RPM is an illustrative
model, not a measured BLDC/controller curve. Source speed limits bound their
stated shaft side. Peak duration, thermal capacity, current, voltage, adapter
fit, mounting, backlash and backdrive/regenerative capability remain unverified.

## Preliminary nonideal cases

Three low/medium/high loss scenarios are editable study assumptions. Initial
Coulomb magnitudes are 1%, 3% and 8% of the usable selected joint peak torque;
viscous coefficients produce the same respective torque fractions at 10 rad/s.
For a 50 N m joint cap these are `(0.5 N m, 0.05 N m s/rad)`,
`(1.5 N m, 0.15 N m s/rad)` and `(4 N m, 0.4 N m s/rad)`.
The model
uses joint-output Coulomb torque in N m and viscous coefficient in N m s/rad:

```text
tau_loss = tau_C + b |qdot|       during forward motion
motor-side Coulomb contribution scales with N
motor-side viscous contribution scales with N²
```

A constant detent resistance is a worst-case opposing cogging envelope; real
cogging is angle-dependent and can return stored energy. These scenarios are
not measurements or additions to the simulator's conservative sinusoidal model.
Any efficiency assumption and additional drag are shown separately; avoid
interpreting the combined provisional loss model as identified hardware data.

## Jump estimate

For this separate screen the wheel stays at height `rw` on a flat floor and the
chassis translates vertically at fixed x and mounting alpha. Wheel horizontal
motion is allowed. Starting at the compression stop, extension uses positive
stroke coordinate `s = tc - q`. For each COM, add `h = rw - C_z(q)` to its
hip-relative vertical position. Chassis mass, both links, compound and wheel
contribute to supported inertia and gravitational potential. The wheel's
horizontal kinetic energy and drivetrain/internal kinetic energy remain separate.

```text
U_gravity(s) = g sum_i m_i z_i(s)
E(s) = 0.5 J(s) omega(s)²
dE/ds = tau_drive(omega) - tau_loss(omega) - dU/ds
U = U_gravity + saved spring potential        [when selected]
v_COM,z = [sum_i m_i dz_i/ds / sum_i m_i] omega
optimistic COM rise above takeoff = v_COM,z² / (2g)
```

The endpoint estimate does not transfer retained rotor, horizontal or internal
kinetic energy into vertical COM flight. It assumes release at full extension,
without solving earlier unilateral liftoff, tire forces, grip or an extension-stop
impulse. A stalled stroke has no completed endpoint launch estimate. A target
height is a reference for comparison, not a proven jump capability. Alpha changes
the grounded COM Jacobian and gravity work; it does not retune the spring.
With massive links, gravity work generally does not scale with cosine alpha
alone: their COMs also have horizontal offsets in the chassis frame. For V4.5's
equal links and 1 kg rods, full-stroke gravity rise is
`g [(m1+1) 2L delta(sin q) cos(alpha) + L delta(cos q) sin(alpha)]`.
The implementation rotates each COM rather than applying a chassis-only shortcut.

Only supplied finite inputs and assessed or explicitly assumed values enter a
calculation. Plots and exported tables carry units and scenario identity. Results
are sampled numerical screens, not certified global acceleration extrema or a
catalog recommendation to purchase compatible hardware.
