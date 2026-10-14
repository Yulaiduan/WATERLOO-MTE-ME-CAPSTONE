# Force, travel and link length at alpha zero

Andy Zhang with Codex, 2026-10-14. Source base `d1596e5`.
Status: proposed ideal design screen, independently checked numerical evidence;
physical full inversion and hardware selection remain unresolved.

Open [the offline report](../force-travel.html) or its [nine-page PDF](force-travel-report.pdf).
This follows the [alpha-zero path search](inversion-path-study.md) and the owner's
request to rank the invertible, slightly tilted paths for force and travel.
The older reports and Motion Lab examples/GIFs remain intact. The new optimizer
and report stay outside Motion Lab tooling.

## Recommended choices

For **original assembly phase zero**, use **320/320 mm links, guide 9:5** as a
rounded starting point. Alpha is zero, ra/rb = 108/60 mm, and the total normal
theta2 window is **110–155.398008 degrees**. It provides **325 mm total /285 mm
usable** vertical height with 20 mm reserved at each end. The usable hip interval
is determined by inverse height, not by subtracting a fixed angle.

Its endpoint chord is **10.313393 degrees** from vertical, with **9.179225 mm
maximum bow (2.778744% of the chord)**. Local tangents range **5.048892–19.301782
degrees**: it does not keep every tangent inside 10–15 degrees. Its minimum
wheel-centre/hip distance on the total normal window is **241.215995 mm**,
leaving 41.216 mm wheel-rim/hip distance and **21.216 mm surplus above the
assumed 220 mm wheel-plus-gap exclusion**. No chassis volume is represented.

If fixed **lower-link assembly indexing** is acceptable, **300/300 mm, guide
2:1, phi0 = -25 degrees, alpha = 0** is the cleaner alternative. It follows an
exact **12.5 degree line**, with the same 325/285 mm height. Its normal interval
is **87.5–142.033095 degrees**, and its shifted ideal full envelope is
87.5–247.5 degrees. This changes assembly phase and required ROM; it relaxes
the original ratio/length-only, phase-zero request. No indexing changes during
movement, and original Jonathan/Motion Lab validators and saved profiles stay
unchanged. Minimum normal hip distance is **257.993810 mm**, 37.994 mm beyond
the assumed exclusion. It still crosses the hip during full inversion.

| Design, all 325/285 mm total/usable | Worst vertical force per hip Nm | Hip peak at 45 kg robot | Height-weighted RMS hip torque | Usable hip ROM | Bow |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rounded 320/320 mm, 9:5, phase zero | 1.90833 N/Nm | 57.832 Nm | 48.062 Nm | 38.9814 deg | 9.179 mm |
| Existing 350/350 mm, 7:4, phase zero | 1.78567 N/Nm | 61.805 Nm | 52.727 Nm | 35.0570 deg | 9.659 mm |
| Best tested equal 425/425 mm under 2% bow | 1.48643 N/Nm | 74.246 Nm | 63.884 Nm | 28.7915 deg | 6.560 mm |
| Rounded 300/300 mm, 2:1, phase -25 deg | 1.92730 N/Nm | 57.263 Nm | 44.783 Nm | 44.2735 deg | Zero ideal bow |

All torque values above use an **equivalent 110.3625 N vertical endpoint load**,
massless moving links and no spring. They isolate force transmission; they are
not complete supported-chassis motor predictions. RMS uses constant vertical
speed without dwell. The earlier mass allocation, spring fit and 6.449 Nm
dynamic example belong to a different geometry and are not transferred here.

## Owner inputs and explicit assumptions

- Wheel radius 200 mm, diameter 400 mm, alpha zero, equal/near-equal links.
- Minimum 200 mm useful height; approximately 250 mm preferred. Total
  300–350 mm includes every buffer. The report keeps the earlier assumed 20 mm
  each-end reserves; these have not been physically specified or tested.
- Robot approximately 40–45 kg, equal four-corner support: 10–11.25 kg and
  98.1–110.3625 N per corner. Uneven support can change those forces.
- Pure vertical endpoint-force ranking, Fy = 0. Screenshot Fy = Fz = 100 N
  remains a separate fixed-A diagnostic. Original V2 comparison uses beta = 0
  so pure vertical contact force has no separate wheel-drive moment; geometry
  retains the screenshot beta 13.5 convention, which does not affect C's locus.
- Moving links are massless in the force comparison. Positive mass allocation
  is used only in the independent collision-disabled geometry engine check.
  No gravitational force is added again to the equivalent support load.
- New illustrative path policy: 10–15 degree endpoint chord, at most 3% chord
  bow and at most 15 degree tangent span. The former tighter 2% policy is
  separately compared, not retrospectively reclassified as passing.
- Normal-branch wheel-centre/hip distance at least 220 mm: wheel radius plus
  assumed 20 mm gap. Unknown chassis thickness, axial offsets, tire deformation,
  belt wrap/strength, spring routing and manufacturing tolerances remain open.
- Full ideal inversion: a continuous height-monotone below-to-above-hip sweep,
  with Jz at least 5 mm/rad. It is not unrestricted 360 degree rotation or an
  actual ground flip. **Every shortlisted full coplanar sweep fails clearance.**

## Correct metrics and torque coordinates

Let q = theta2, t = q - pi, r = qab = ra/rb, k = r - 1,
a = L2 and b = L3. At alpha = phi0 = 0, Jonathan's convention gives, in mm:

```text
x = a cos(t) - b cos(k t)
z = a sin(t) + b sin(k t)
Jx = -a sin(t) + k b sin(k t)
Jz =  a cos(t) + k b cos(k t)
```

Convert Jacobians to metres/radian before multiplying force. Ideal virtual work
gives signed hip holding torque `tau_h = -(Fy Jx + Fz Jz)`. For the positive-Jz,
pure-vertical working branches, its magnitude is `Fz Jz`.

1. **Peak force capability:** guaranteed vertical force per unit direct hip
   torque is `1 / max(Jz)` over the **usable** stroke. Using `1 / min(Jz)` would
   wrongly advertise the most favourable pose as the capability everywhere.
   These values require Fy = 0 and ideal losses; tangential force uses
   `1 / max(hypot(Jx,Jz))`, a different direction.
2. **Height-weighted RMS:** `Fz sqrt(integral(Jz^2 dz)/H)`, equivalently
   `Fz sqrt(integral(Jz^3 dq)/H)`. This is temporal RMS only at constant vertical
   speed without dwell. Actual motor heating needs the real time-weighted duty.
3. **Average torque:** uniform-angle mean magnitude is `Fz H / deltaq`.
   Increasing ROM can reduce it. Height average and angle average differ;
   retained evidence records their weighting explicitly.
4. **Travel/peak-torque score:** `H / tau_peak` helps compare bounded designs,
   but is not energy efficiency. Torque must also obey
   `tau_peak >= Fz H / deltaq`; the retained utilization shows this tradeoff.
5. **Work:** `integral(tau dq) = Fz H`. Every ideal 285 mm lift costs
   **27.9585–31.4533 J per corner** under the stated static loads. Geometry
   trades torque for angular motion; it does not reduce ideal lifting energy.

The relative knee derivative is `d(theta_knee_rel)/dq = -r`.
Consequently `tau_knee_rel = -tau_h/r` and knee speed is `-r` times hip speed.
Power remains equal. This is the relative-knee coordinate, not a second
independently actuated joint. Extra motor gearbox reduction, belt loss and
motor inertia must be specified separately. A universal half-torque statement
cannot be applied to every changed guide ratio or shaft coordinate.

## Search and two optimization methods

[force_travel_search.py](../force_travel_search.py) enumerates **11,478,060**
strict geometry/window combinations. These include rejected combinations;
they are not a count of viable physical robots. Domain:

- L3: 200–450 mm in 10 mm steps, plus 275/325/375/425 (30 scales).
- L2/L3: 0.85–1.15 in 0.01 steps; exact equal and 5/10/15% deviation tiers.
- Guide: 1.4–2.6 in 0.005 steps plus exact 5/3; rb = 60 mm.
- Normal theta2 start: 100–140 degrees in 2.5 degree steps; end at most 175.
- Exact total heights: 300, 325 and 350 mm, solved by bracketing/root finding.
- Total-window branch clearance, guide pitch-circle separation
  `L2 > 60(r+1)`, path policy, and full q100–260 positive-Jz filter.

51-pose coarse quality counts: **509,233** angle/clearance/full-inversion passes,
**238,853** within 3% bow/15 degree span, **9,724** within 2%/15 degree span.
Every retained candidate's final geometry and metrics are recalculated at
2001 poses. Ranked candidates minimize useful-stroke peak Jz, then link sum;
16 leaders per bucket are retained for dense final screening. This finite
candidate-pool/grid procedure is bounded numerical screening, not a global
continuous optimality certificate. Size-bucket leaders are also retained;
the two-objective size/peak-J Pareto screen has one retained nondominated row
under its 15% mismatch policy, not evidence that curvature has no tradeoff.

**Second method:** grid-seeded SLSQP refines L3, L2/L3, guide and start for
325 mm total, with 401-pose geometry constraints and a 2001-pose final check.
Both 14-iteration runs report success and pass dense acceptance:

| Local result | L2/L3 mm | Guide | Direct hip peak at 45 kg | Worst F/T |
| --- | ---: | ---: | ---: | ---: |
| Equal | 303.463 /303.463 | 1.807104 | 55.423 Nm | 1.99127 N/Nm |
| Within 5% | 293.780 /309.242 | 1.786363 | 54.206 Nm | 2.03598 N/Nm |

Both reach the 10 degree chord, 15 degree tangent-span and 220 mm normal
clearance boundaries. The near-equal design also reaches `L2/L3 = 0.95`, its
5% mismatch bound. Those improvements leave zero surplus over the assumed
wheel-plus-gap filter. Rounded 320 mm is preferred as a practical study seed,
with no claim that its remaining margin is a certified chassis clearance.

Allowing 15% mismatch finds 276.25/325 mm, guide 1.74, with 52.027 Nm peak,
but loosens the near-equal preference for a small further gain. The simpler
330/330 mm 7:4 diagnostic has 9.97044 mm bow, **3.004279%**, so it narrowly
fails the actual 3% policy despite being below 10 mm bow. 340/340 mm 7:4 passes
(2.95445%, 60.415 Nm peak); existing 350/350 adds normal clearance margin.
Do not round the 330 mm diagnostic into a passing result.

## Travel and indexed alternatives

| Equal-link strict grid winner | Guide | Total /usable height | Peak hip torque at 45 kg | Useful ROM |
| --- | ---: | ---: | ---: | ---: |
| 300/300 mm | 1.810 | 300 /260 mm | 53.680 Nm | 38.928 deg |
| 310/310 mm | 1.795 | 325 /285 mm | 56.334 Nm | 39.975 deg |
| 325/325 mm | 1.800 | 350 /310 mm | 59.626 Nm | 41.205 deg |

300 mm total already gives more than approximately 250 mm useful height.
325 mm is a balanced comparison point; use 350 only if the additional useful
range earns its size/torque/ROM cost. These 20 mm buffers are not validated
impact energy absorption, spring compression or an agreed chassis reserve.

The separately labelled indexed search evaluates **11,070** combinations
(6,162 dense accepted normal windows): fixed phi0 -25 degrees, r = 2, L3
250–450 mm step 5, link ratios 0.95/0.975/1/1.025/1.05, starts 87.5–130 degrees
step 2.5, three total heights. At equal L, `d=phi0/2` gives exactly:

```text
C = 2L sin(q-pi-d) [-sin(d), cos(d)]
```

Equal-link winners use 270 mm for 300 total, 285 mm for 325, and 295 mm for
350. Their full folds still coincide with the hip. Rounded 300 mm is the
recommended indexed illustration for greater normal margin, not the minimum
force result. Original phi0 = 0 has x even and z odd about q180, so its fold
tangent stays vertical and inverted working branches have opposite tilt.
Ratio and near-equal length alone cannot create the same tilted straight line
through that fold. The historical **dual-rope IMPOSSIBLE /rejected** decision
is preserved; these are ideal guide-geometry studies, not its revival.

## Velocity, horizontal force and held-load sensitivity

At an illustrative **0.25 m/s constant vertical speed**, the rounded strict
320 mm case needs at most **0.8714 rad/s** useful-stroke hip speed, while the
indexed 300 mm case needs **1.3757 rad/s**. The indexed option's smaller
low-end Jacobian lowers initial holding torque but raises joint speed.

```text
qdot  = zdot / Jz
qddot = zddot / Jz - (dJz/dq) zdot^2 / Jz^3
```

These constant-speed curves do not model smooth starts/stops, actuator inertia
or real cycle acceleration. The report plots hypothetical `Fy/Fz = -0.3, 0,
+0.3` sensitivity for the strict case; this is an assumption, not a measured
traction envelope. General torque depends on `Fy Jx + Fz Jz`, so pure-vertical
rankings may change under side loads.

For the 320 mm case, equivalent 45 kg **3g and 4g total supported-load** peaks
are **173.496 and 231.328 Nm** direct hip; indexed 300 mm gives 171.789 and
229.052 Nm. Three/four g scales total force, rather than being added on top of
gravity. These are held-force sensitivities, **not real transient impact
predictions or motor ratings**. Actual spring compression, contact load sharing,
drop speed/energy, moving masses, damping, gearing and structural limits remain
unresolved. See the earlier [impact record](impact-load-envelope.md) for its
separate assumptions and sources; no new impact threshold is invented.

## Validation boundaries and reproduction

[Selected evidence](force-travel-results.json) retains source hashes,
domains/counts, 21 accepted or explicitly diagnostic/reference cases,
grid/size leaders, force/path metrics, local refinements and 61 display poses
per curve. Dense metrics and display sampling are distinct. Source versions:
Python 3.13.12, NumPy 2.5.3, SciPy 1.18.1, Pymunk 7.3.0; Node 22.23.3.

- Five new tests check original trig finite differences, inverse-height buffers,
  SciPy quadrature, analytic peak J, relative-knee power and rejected cases.
  Existing five inversion and twelve generalized tests also pass (22 total).
- [Original-model checks](force-travel-math-checks.json) compare Jonathan V2 and
  the existing Andy 2D statics at all 21 x61 useful poses: **10,248 scalar
  comparisons**, maximum **3.410605e-13 mm/Nm** error. They use vertical load,
  beta zero and zero moving masses, not simulated motor-force measurements.
- Independent read-only review recomputes all 21 cases using original trig,
  root solving, continuous bow minimization and quadrature: peak J agreement
  7.22e-15 m/rad, RMS J 5.91e-9 m/rad, continuous versus sampled bow discrepancy
  at most 3.81e-6 mm; all acceptance classifications agree. Near-equal active
  mismatch bound and the 330 mm diagnostic failure are explicitly retained.
- [Actual Pymunk checks](force-travel-engine-checks.json) step three new full
  angular sweeps with real pivots/gears/motor, positive masses and no pose resets
  after initialization. Zero gravity/contact and absent collision shapes make
  them geometry checks. All 1/0.5 ms runs pass the unchanged 0.1 mm path/pin,
  1e-4 rad guide and 0.01 rad tracking thresholds and converge. **All 2 ms path
  checks fail** (0.10465–0.13657 mm), and failures remain recorded. Fine path
  errors are 0.02589–0.03378 mm. This does not certify physical inversion.
- First evidence export failed on NumPy boolean JSON serialization; explicit
  scalar conversion fixed export and the full search was rerun. No physical
  limit or tolerance was weakened.

Optional commands from this app's root, with the existing pinned environment:

```sh
.venv/Scripts/python.exe force_travel_search.py
.venv/Scripts/python.exe -m unittest -v test_force_travel test_inversion_search test_generalized_leg
.venv/Scripts/python.exe scripts/verify_force_geometry.py
node scripts/verify_force_report.cjs --math-only
.venv/Scripts/python.exe scripts/build_force_report.py
node scripts/verify_force_report.cjs
```

The builder uses retained evidence, not a silent new search or simulation.
Report reading needs no runtime, server or internet. The browser verifier uses
the sibling locked Playwright and installed Edge/Chrome; screenshots/print QA
and raw frames remain ignored. Source geometry/statics:
[Jonathan V2](../../../../jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html),
[Andy 2D model](../model.js), [generalized engine](../generalized_leg.py).
No canonical robot, hardware, structural, GPU, other-OS, physical contact/impact
or three-dimensional packaging validation is claimed.

Next: measure axial/chassis geometry and real wheel sweep; agree accepted bow
and local-angle limits; define motor shaft/gearing and useful impact stroke;
then allocate measured masses, refit the selected spring topology and evaluate
a smooth supported-chassis/contact trajectory. Those inputs may change the
best torque RMS and the design choice.
