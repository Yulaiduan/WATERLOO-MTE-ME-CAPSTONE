# Generalized VSL geometry, statics and bounded design search

Author: Andy Zhang with Codex. Updated: 2026-10-14. Status: experimental
analytical study; dimensions below are conditional candidates, not hardware acceptance.

The new [model](../model.js) preserves the conventions of
Jonathan's immutable [v1](../../../../jonathan-xie/experimental-apps/leg-solver/v1-kinematics.html)
and [v2](../../../../jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html),
with the [v2 derivation](../../../../jonathan-xie/experimental-apps/leg-solver/v2-model.md)
as the source for quasi-static equilibrium. The existing
[equal-link sizing study](../../wheel-leg-lab/docs/link-sizing.md) remains a separately reproducible special case.

## Coordinates and ratios

Geometry is in mm, angles degrees, masses kg, forces N and torques Nm.
Global y is horizontal/rearward, z upward. Local u/v rotates clockwise by alpha.
Theta2 points B to A and theta3 points C to B, counterclockwise from +u.
A is the chassis hip, B the knee, C the wheel centre, P the contact patch.
V1 calls its wheel-centre endpoint P; the new study uses v2's C/P distinction.

| Jonathan variable | New field | Meaning |
| --- | --- | --- |
| L2, L3 | L2, L3 | Femur and tibia lengths; independently editable |
| q23 | ratios(config).q23 | L2/L3 |
| qab | ratios(config).qab | ra/rb; free search variable |
| qcd, qef | ratios(config).qcd/qef | rc/rd and re/rf |
| theta2e, theta2c | te, tc | Physical extension/compression stops |
| phi0, alpha, beta | phi0, alpha, beta | Assembly phase, clockwise mounting, contact angle |
| theta4 | t4 = 0 | Locked wheel-drive input during holding |
| theta5, theta6 | t5, t6 | Unwrapped rotations relative to extension |
| K | K | Wheel-angle change per suspension-angle change |
| delta_i | ab/cd/ef.delta | Upper minus lower belt-span tension |

With q = theta2 in radians, k = 1-qab:

```text
theta3 = phi0 + (180 - theta2)(qab - 1)
B = -L2 [cos(theta2), sin(theta2)]
C = B - L3 [cos(theta3), sin(theta3)]
dB/dq = [L2 sin(theta2), -L2 cos(theta2)]
dC/dq = dB/dq + k L3 [sin(theta3), -cos(theta3)]
dy = cos(alpha) du + sin(alpha) dv
dz = -sin(alpha) du + cos(alpha) dv
delta theta3 = (1-qab) delta theta2
relative knee change = -qab delta theta2
theta5 = (1-qcd) delta theta2
theta6 = K delta theta2
K = 1-qab + qef(qab-qcd)
```

The guide does not have a fixed 2:1 ratio. Equal links, qab=2, phi0=alpha=0
recover C_u=0 and C_v=-2L sin(theta2). Andy's fold angle is theta2-90 degrees,
and his displayed wheel-centre angle is 180-theta2 degrees. This mapping gives
the same height, Jacobian and direct hip torque. Signed relative-knee torque is
`tau_knee = -tau2/qab`; its magnitude is `|tau2|/qab` for this
one-degree-of-freedom transmission, from conservation of virtual work;
the study optimizes direct hip/drive outputs without inventing motor gearing.
With qcd=qef=1, K=0 for every qab, so zero wheel spin is not evidence of a 2:1 guide.

## Loads and equilibrium

Beta is clockwise from -z toward -y. In global axes:

```text
n = [sin(beta), cos(beta)]
t = [cos(beta), -sin(beta)]
P = C - rw n
F = Fn n + Ft t
Fy = Fn sin(beta) + Ft cos(beta)
Fz = Fn cos(beta) - Ft sin(beta)
Mw = rw Ft/1000
delta_ef = rw Ft/rf
delta_cd = -(re/rd) delta_ef
tau4 = -qcd qef Mw
tau2 = -(F dot dC/dq + sum(Wi dot dRi/dq))/1000 - Mw K
```

Radii in the moment expressions are mm. Gravity is global -z. The masses m2/m3
are at rod midpoints, m5 at B and m6 at C. m1 is concentrated at fixed A: it changes
chassis support, but has zero displacement and does not directly enter tau2.
Prescribed contact force remains independent of m1. The user's later 40–45 kg
whole-robot estimate means nominal equal sharing of 10–11.25 kg per leg;
98.1–110.3625 N is a separate level-support case, not an automatic replacement
for the screenshot's 100 N vertical and 100 N horizontal force.

The implementation also solves exact external belt-tangent forces and pin
reactions using Jonathan's equilibrium, then checks tau2 independently by virtual
work at every pose. Span preload allocation is T_U=T0+max(delta,0),
T_L=T0+max(-delta,0). It never invents compressive belt tension. Unknown measured
preloads remain unresolved; the explicit default T0=0 is an ideal limiting
assumption. Changing preload affects pin loads, without reducing ideal torque.
No fitted spring is included in this analytical model; the physical study handles
spring assistance and actual dynamic responses separately.

## Screenshot reproduction

The initial reference is L2=L3=250, ra=100, rb=60, rc=rd=re=rf=35, rw=200 mm,
phi0=alpha=0, te=100, tc=165, beta=13.5 degrees, Fy=Fz=100 N, m1=10 kg,
other masses zero, g=9.81 and all preloads zero. Thus qab=5/3, not 2.
At theta2=100.135 degrees:

| Output | Reference |
| --- | ---: |
| theta3 | 53.2433333 deg |
| tau2 | -25.6296597 Nm |
| tau4 | -14.7784911 Nm |
| Tight ab belt, lower span | 84.4859843 N |
| dy | 0.265169876 mm |
| dz | 0.337721468 mm |
| Final dy at 165 deg | 101.157121828 mm |
| Final dz at 165 deg | 338.615930749 mm |

The module reproduces these values and the actual extracted v2 solver over 40
additional varied geometries/masses/loads/poses. With 20 mm vertical reserve at
each end, the initial usable travel is 298.615931 mm. The reference remains
mathematically valid even when an optional design-clearance filter rejects it.

## Travel, weighting and feasibility

Total capacity is the physical wheel-centre vertical stroke te to tc and includes
both end buffers. The current user brief has hard minimum usable stroke 200 mm,
preferred usable stroke around 250 mm, and an editable preferred total of
300–350 mm including all buffers. Central 325 with 20+20 reserves leaves 285 mm
usable; 300 leaves 260 and 350 leaves 310. The optimizer solves tc for the exact
selected total rather than quietly picking the easiest edge of the preference band.
Set exactTarget=false to search a band deliberately.

An mm buffer solves the generalized height inverse; a degree buffer trims the
physical angle directly. convertBuffer preserves the current geometry when
switching units. A changed design can give different mm equivalents for a fixed
degree reserve. No universal cosine conversion is applied to unequal links.
Reversed vertical paths, consumed buffers, overlapping same-stage pitch circles,
excess lateral drift and too-small usable vertical Jacobian are rejected.

Wheel radius changes ground clearance, assumed projected hip clearance, contact
moment and belt loads. It never automatically defines travel. Flat-ground
chassis air gap is -C_z+rw-chassisDepth. The additional conservative projected
hip filter is |C|-rw >= minClearance, enabled by enforceHipRim=true. This treats
the hip as an exclusion disk with an entered clearance, not as measured chassis
geometry. The screenshot fails this projected filter near compression; staggered
axial planes could resolve a projected overlap. Disable it only as an explicit
packaging assumption; 3D wheel/chassis interference remains unresolved.

RMS weighting is explicit:

- angle: uniform suspension-angle speed;
- travel: uniform vertical speed;
- time: uniform time samples of quintic vertical height
  z(u)=z_start+stroke(10u^3-15u^4+6u^5), u in [0,1], using the generalized inverse.

The default cycleSeconds=2 gives a one-second compression stroke and is matched
to the physical comparison's quintic input. The static RMS is over that stroke;
rest time is excluded. A symmetric return gives the same quasi-static RMS.
Velocity, acceleration and dynamic torque do not follow from a quasi-static RMS.
The time duration changes speed, without changing this static time weighting.

Signed tau2/tau4 remain in every sample. Peak/RMS optimization uses the combined
output magnitude sqrt(tau2^2+tau4^2), a declared equal-weight demand score for two
actuator coordinates. It is not an electrical loss or one motor's rating. Nominal
peakTau2/rmsTau2/peakTau4 and robustPeakTau2/robustRmsTau2/robustPeakTau4 remain
separate. meanAbs and signedMean refer specifically to nominal tau2.
signedWorkJ is integral(tau2 dq); absoluteWorkJ integrates |tau2|dq.
loadWorkJ includes horizontal/vertical work and Mw K dq. These preserve the
sign and expose assistive horizontal loads instead of calling cancellation efficient.

Default loadCases=lateral-envelope evaluates Fy=-100,0,+100 N at Fz=100 N
(more generally +/-abs(entered Fy) and zero). Beta stays fixed. The objective is
the worst peak or worst time RMS over these explicit scenarios, so a design
cannot win only because one horizontal force assists lifting. Nominal plotted
traces remain the entered signed force. This envelope is a design assumption,
not demonstrated tire friction/contact feasibility. loadCases=nominal recovers
the original fixed-force calculation. Global Fy/Fz must drive an envelope;
switch to nominal for independently driven Fn/Ft.

## Two implemented search methods

Single-objective search enumerates the bounded coarse geometry grid, ranks
feasible peak or RMS scores, and refines four leading seeds by successively
halving each coordinate step. Pareto search enumerates the same feasible grid,
keeps nondominated selected torque/total-link-size/lateral-drift alternatives,
then refines up to twelve spread frontier seeds. Each evaluated alternative is
retained for dominance checks; neither method changes forces or masses to win.
q23 or L2 can vary with L3, but not both simultaneously. qab/qcd/qef variation
changes the corresponding numerator radius with the denominator held fixed.

Both methods recheck the top forty and all coarse/refined frontier members with
at least 721 pose/time samples before returning results. convergence records
coarse, each local pass and dense verification. boundary identifies winning
coordinates at their configured limits. The evaluation guard reports limited
rather than claiming convergence. Pareto dominance refers to the evaluated and
verified population, not every point in a continuum. This is a useful bounded
analytical search, not a proven global hardware optimum. A worker is required
for responsive browser use; measured default searches took roughly 16–20 seconds.

## Reproducible conditional results

These runs use DEFAULT_CONFIG with samples=81, refineIterations=4, exactTarget
enabled, robust lateral envelope, quintic time RMS and the default conservative
hip filter. Default domains are L2/L3=180..340 step40 mm; qab=1.4..2.4 step0.25;
alpha=0..20 step10 degrees; te=100..110 step10. tc is solved inside 155..170.
Off-grid domain endpoints are included. There are 750 coarse geometries; local
refinement adds about 100 evaluations. All other inputs remain the screenshot values.

| Total / usable mm | Objective | L2 / L3 mm | qab | alpha deg | tc deg | Robust peak Nm | Robust RMS Nm | Drift mm |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300 / 260 | Peak | 205 / 340 | 1.650000 | 0 | 156.715251 | 44.6272 | 38.3676 | 33.8237 |
| 300 / 260 | RMS | 205 / 340 | 1.665625 | 0 | 156.373703 | 44.7197 | 38.3370 | 28.3762 |
| 325 / 285 | Peak | 180 / 340 | 1.775000 | 4.375 | 159.810888 | 46.2598 | 41.0888 | 11.4118 |
| 325 / 285 | RMS | 187.5 / 340 | 1.775000 | 7.5 | 159.298260 | 49.0289 | 39.4434 | 21.7992 |
| 350 / 310 | Peak | 180 / 340 | 1.900000 | 6.875 | 161.088907 | 49.9799 | 45.1581 | 42.0781 |
| 350 / 310 | RMS | 187.5 / 340 | 1.900000 | 12.5 | 160.378032 | 54.5276 | 42.0157 | 20.3625 |

The central peak example has ra=106.5/rb=60, q23=0.5294118, K=0, te=100.
Nominal peak/RMS are 46.2091/37.0417 Nm, nominal leg peak 43.7822 Nm and
nominal drive magnitude 14.7785 Nm. Ground gap is 141.2842 mm, assumed hip-rim
gap 20.8402 mm and usable minimum vertical Jacobian 197.4802 mm/rad.
This is a compact 520 mm summed-link candidate with a free non-2:1 guide.
Its peak search improves 50.6292 → 46.6129 → 46.6129 → 46.6129 → 46.2598 Nm;
the final dense result is 46.2598 Nm. RMS search improves 42.5498 → 39.8691 →
39.5663 → 39.4848 → 39.4434 Nm, with dense RMS 39.4434.

Every narrow-domain winner uses the 340 mm tibia boundary. An expanded check
L3=180..500 step40 with other bounds unchanged, samples=51 and three refinements
finds L2=180/L3=395 mm, qab=1.4, alpha=0, te=100, tc=169.525341. It gives exact
325/285 travel, robust peak/RMS 39.6322/37.1803 Nm, size575 and drift86.7784 mm.
Ground gap is 61.5835 mm and projected hip-rim gap25.5154 mm. The peak falls from
40.3658 coarse to39.7766 and39.6322 refined/dense. L3 is now interior, but L2 and
qab still reach their lower bounds; expanding those is another separate study.
The expanded candidate reduces peak by about14.3% while adding55 mm link sum
and75.4 mm drift versus the compact central example. No stiffness, strength or
moving-link mass penalty establishes that larger tibia as preferable hardware.

A separate Pareto run over L2/L3=200..320 step40, qab=1.5..2.5 step0.25,
alpha=0..20 step10, te=100..120 step10, exact325, two refinements, returns eleven
nondominated alternatives. For example 280/280, qab=1.9375, alpha0 has peak/RMS
53.2586/43.5319 Nm and drift20.9498 mm; 280/280 with qab2 yields negligible drift
but peak55.7675 Nm. The 2:1 point is a sampled alternative, never a fixed assumption.
Different domains must be stated when comparing these numbers.

Reproduce from the app root with installed Node 22:

```javascript
// Run in Node with --input-type=module. The offline report has no worker.
await import('./model.js');
const M = globalThis.DesignStudyModel;
for (const targetTotal of [300, 325, 350]) {
  for (const objective of ['peak', 'rms']) {
    const result = M.optimize({...M.DEFAULT_CONFIG, targetTotal, samples:81},
      {objective, refineIterations:4});
    console.log(targetTotal, objective, result.best.config, result.best.metrics,
      result.convergence, result.boundary);
  }
}
```

## Verification and unresolved inputs

Run `node --test tests/design-study.test.js`. Checks cover actual immutable-v2
parity, screenshot values, generalized finite-difference Jacobians, equal-link
torque and integral agreement, buffer round trips, independent radius/clearance,
preload/m1 invariance, signed load conversion, robust scenarios, quintic time
input, feasibility filters, exact-target/refinement and Pareto nondominance.
Initial tests found that a deliberately small domain had only one nondominated
result; the test was corrected to use an explicitly wider domain with actual
tradeoffs. No solver tolerance was weakened. This is numerical consistency and
bounded optimization evidence, not a canonical robot or hardware physics pass.

Measured spring properties/preloads, moving-link masses/inertias, actual motor
gearing/efficiency/speed/current/duty limits, contact friction/rolling, teeth and
wrap adequacy, collision geometry, structure/strength and 3D shaft/bearing
packaging remain open. The later requested 3–4g impact response belongs to the
dynamic/spring fixture; multiplying a static load envelope is not an impact
simulation. Zero moving masses in this table preserve the original reference,
and can bias size/torque rankings. Production components must not import this app.
