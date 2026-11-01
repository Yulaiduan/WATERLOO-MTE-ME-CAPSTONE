# V5 gravity-compensation designs

Andy Zhang / Codex, 2026-11-01. Experimental member-app designs based on
`48b1a9e`, updated to the owner's zero-initial-velocity ground check. These are ideal mechanism/simulation configurations, not selected
hardware or a certified suspension.

## Two portable designs

- [V5 α0°](saved-configurations/v5-alpha0-4to1.json)
- [V5 α20°](saved-configurations/v5-alpha20-4to1.json)
- [Exact fit inputs, locked fields and numerical evidence](saved-configurations/v5-fit-evidence.json)

Both use300mm links,200mm wheel radius,8.75kg supported chassis per corner,
1kg per uniform link,0.5kg wheel and zero compound-pulley mass. Total corner
mass is11.25kg. Uniform-rod COM inertias are0.0075kg·m² each; the wheel-disc
inertia is0.01kg·m². Custom-inertia fields set to0 are inactive overrides,
not massless bodies. A real drive motor/input inertia is not supplied.

The AB leg coupling remains50/25=2:1. The two wheel-drive stages are
25→50mm at the hip/knee and25→50mm at the knee/output: **2:1 reduction each,
4:1 overall with the leg held**. Moving carriers give
`ω6 = −ω2/4 + ω4/4`. Actual contact keeps the input freely backdrivable,
massless and unforced; a held/loaded/inertial wheel-drive input is a different
model. The prescribed-height bench holds that input and retains its coupled
wheel rotational inertia.

Spring rate8N/mm, reference force330.869282809N atθ2=90°, idler radius10mm
and horn offset0° remain fixed. α0 changes horn radius and Sv. α20 also
changes Su with the owner's explicit approval. Idler and horizontal spring
body stay fixed to the chassis; only the horn follows the leg. See
[mount convention](spring-mounting.md). The bounded fit minimizes residual
holding torque across the whole working travel. The extra horn-radius root
previously added to cancel the135° starting residual has been removed: it made
an unperturbed test appear stationary and did not test imperfect compensation.
There is no motor holding bias or initial velocity.

| Design | Horn radius, mm | Su, mm | Sv, mm | Peak / RMS holding error, N·m |
| --- | ---: | ---: | ---: | ---: |
| α0° | 66.462290 | 9.387777 | 103.678515 | 0.084261 / 0.049103 |
| α20° | 64.017026 | 45.479600 | 91.651684 | 0.041829 / 0.030794 |

At the135° starting pose the required holding torques are−0.034188N·m and
−0.027188N·m. With zero applied torque and zero initial velocity, the remaining
imbalance initially drives compression/downward chassis motion. This is the
intended test of imperfect gravity compensation; no kick is added.

## Mass audit

There was **no omitted-leg/wheel-mass bug in the force equations**. The fit
uses all individual masses at their actual COMs. Automatic weight-reference
ground reaction is `(m1+m2+m3+m5+m6)g = 110.3625N`. Increasing wheel mass by1kg
increases that reaction by9.81N. It does not increase static hip gravity work
when the wheel stays at constant world height: `d(m6*g*z_wheel)/dq = 0`.
Wheel mass and rotational inertia remain active in both dynamic engines.

For equal links, AB2:1, φ0=0, zero compound mass and the vertical chassis guide,
the equivalent gravity-support target is

`F_required(q) = g[m1 + 3m2/4 + m3/4 − (m2+m3)tan(q)tan(α)/4]`.

Use radians inside the trigonometric functions. Atα0 this is95.6475N.
Atα20, finite-link COM motion makes the target vary with pose; a good gravity
fit is therefore not literally constant gross-weight lift or constant cable
tension. The fitter now records every mass, resolved load convention, RMS/peak
holding torque and equivalent-force residual in its JSON and closed mass-basis
disclosure. Independent body-potential differences check the static equations.

## Why the screenshots failed, and what changed

Exactθ2=90° extension has zero vertical Jacobian. It is a finite ideal Energy
endpoint but an unsupported dynamic boundary. V5 uses **95–175° operating
stops,80° travel**, with the135° starting pose. The theoretical90° limit stays
available as an explicitly labelled Energy study; it is not substituted into
these runnable profiles. Singular guards were not weakened.

The former prescribed-height UI could drive the wheel through a150mm square.
The owner clarified that this mode is only a **flat-ground support check**.
Terrain editors are now disabled/hidden there and the exact effective capture
has height, speed, transition and delay all0, with a floating chassis. Both
engines, comparisons, run exports and desktop requests use that same capture.
Stored square/periodic terrain settings remain available when returning to
actual contact and survive saved-design reload/project export. The serialized
mode remains `prescribed-height` for compatibility. Legacy standalone Python
moving-height inputs remain explicitly separate from this app mode.

Saved defaults: floating chassis; free wheel; μ0.8; zero restitution;3s;
dt0.000125s;50Hz output;150mm-high,150mm-wide square terrain with150mm gaps,
100mm/s translation and0.5s delay. The bench uses a stationary flat input.
Jump/drop targets are2m, with50mm underside offset and50mm minimum-clearance
target. Entered250Nm jump and300Nm landing commands are **ideal joint commands**;
the500Nm search ceiling is not a hardware rating. Terrain torque/damping stay0.

## Terrain retuning limits

The owner retained fixed k/preload and allowed geometry changes only. Bounded
geometry experiments checked exact ride-pose balance, positive stiffness,
upward assistance and actual engine response. Strong restoring geometry could
avoid terrain stops but pulled downward near full extension and failed the
prescribed bench; it was rejected. Three upward-assist alternatives did not
avoid terrain endstops while retaining bench compatibility. A separate explicit
damping diagnostic was not installed as a saved design.

The delivered designs preserve approximate upward gravity compensation and
their measured residual error. They **do not claim passive chassis-height regulation**. The150mm
terrain input can reach an operating stop, especially atα20. A spring-only
geometry search is not an active height controller. The negative results remain
documented rather than changing contact constraints, inputs or losses to hide them.

The owner's final clarification is accepted: some drift in a lossless bench is
expected, and zero drift is not a condition for accepting the gravity fit.
Locally, a residual generalized torque drives motion even with no terrain.
Viscous friction slows that motion but supplies no holding torque at rest;
true static friction can hold while residual torque is below breakaway.
An ideal neutral balance also has no restoring force after a displacement.
The saved profiles deliberately use zero motor losses and zero hip damping so
these effects are not concealed. A smooth Coulomb approximation need not
provide exact stiction. Long-term position holding requires a separately
declared friction/restoring/control model, not more digits in the spring fit.

## Current zero-velocity ground checks

All eight current runs start at135° with **zero hip and chassis velocity**.
Duration6.5s, dt0.000125s and20Hz output are explicit diagnostic settings;
the portable profiles retain their3s default. Height/speed/rise/delay are0.
No motor, holding or braking torque, hip damping or enabled motor loss model
acts in these runs. The chassis is not pinned. Each cell is analytical / Pymunk.

| Downward chassis movement after6.5s, mm | α0° | α20° |
| --- | ---: | ---: |
| Ideal flat-ground support check | 175.617 / 175.613 | 97.300 / 97.302 |
| Actual wheel/flat-floor contact | 175.948 / 176.498 | 97.219 / 97.581 |

All eight finish without travel stops. Both contact runs are still moving at
the end; this is residual-driven drift, not a recovery/settling test. The two
modes have different wheel-drive boundary conditions, so agreement between
engines within one mode is distinct from equality between modes.

For α0 actual contact, the initial net compression torque is0.034188N·m and
the grounded effective inertia is1.725kg·m². Thus initial hip acceleration is
0.019819rad/s² (1.13556°/s²), giving chassis acceleration−8.4086mm/s².
The short-time estimate `Δh ≈ ½ a₀ t²` gives−177.63mm at6.5s, close to the
full nonlinear result. No initial velocity is needed to explain this motion.
The static fit reference remains110.3625N; actual normal force is solved from
accelerating masses and need not equal the static weight at every sample.

Actual contact retainsμ0.8 and zero restitution, with free wheel spin. Motor
Coulomb and viscous terms are implemented but disabled in these profiles.
The existing smooth Coulomb law does not model exact static stiction. Pymunk
global damping is1 and its sleep threshold is infinite; neither introduces
automatic settling or a sleeping hold. Analytical contact/projection terms
and native signed constraint/residual terms can nearly cancel even at rest;
their individual magnitudes must not be called measured physical absorption.

Passed861mass/fit/profile assertions including deterministic refit,82mode and
capture checks,35project groups,48dynamic comparisons,4,090Plotly exact-sample
checks,7Python dynamics tests and19temporary profile-storage tests. A separate
48-assertion replay regression uses existing actual landing/jump/terrain bundles;
it does not claim new executions of those scenarios. Eight new exact compressed
captures total2,859,044bytes with profile and11source hashes. No initial-velocity
kick is used as evidence for this check. The actual Pymunk desktop request is
checked with the same flat snapshot; a desktop window is not opened in QA.

## Historical one-pose calibration results — superseded

The numbers in this section belong to commit `48b1a9e` and its now-superseded
one-pose-calibrated geometry. They must not be presented as current full-travel
fit results. The previous initial-velocity diagnostic is also separate from
the owner's requested zero-velocity check and is not used as its evidence.

The final exact-profile matrix completed16three-second engine runs plus four
one-second stationary-floor diagnostics, with finite rows and frames. These are
execution/compatibility passes, not16stability or hardware-performance passes.
The two columns below report analytical / Pymunk values.

| Measurement | α0° | α20° |
| --- | ---: | ---: |
| Stationary-floor maximum chassis drift in1s, mm | 0.004569 / 0.000028 | 0.003907 / 0.000069 |
| Settled wheel normal force, N | 110.362589 / 110.362500 | 110.362576 / 110.362499 |
| First-flight COM rise with250N·m, mm | 2040.023 / 2039.715 | 2003.005 / 2002.720 |
| Minimum underside clearance,2m drop /300N·m brake, mm | 377.010 / 375.648 | 370.475 / 369.136 |
| Maximum same-time chassis difference in prescribed bench, mm | 0.010363 | 0.007371 |
| Maximum same-time chassis difference in terrain run, mm | 0.320565 | 83.605803 |

Stationary-floor support matches the full11.25kg corner weight. The α0 terrain
run spans about2.4mm chassis height with no travel-stop events. The α20 terrain
run reaches the compression stop near1.19s in both engines; minimum hip height
is249.140 /248.934mm. Its moving-floor start spins the free wheel and is not
the same condition as the stationary-floor balance diagnostic.

The first jump apex agrees within0.31mm of COM rise, but uncontrolled
post-jump re-landing differs substantially: maximum same-time height differences
over the full3s are589.316mm /543.381mm for the α0 /α20 designs.
Landing runs arrest above the requested50mm clearance, but their full-trajectory
height differences reach7.377 /5.710mm. Do not use first-apex agreement as
evidence of complete contact-model equivalence. Native rigid-contact energy
residuals and sub-millimetre penetration remain reported numerical limitations.

That revision passed838V5 mass/profile/calibration assertions,26,214existing fitter assertions,
35project/library groups and22interaction-mode assertions. Headless browser QA
checks both saved profiles, exact captured requests, both animations, Energy
plots, mass disclosure and desktop/phone layouts; it does not mutate the live
profile library. Raw20captures are retained losslessly in about5.1MB of ignored
app-local gzip files with source, profile and request/result hashes.

## Reproduction and interpretation

Run `node build-v5-profiles.cjs` to reproduce the frozen portable JSON and
`node verify-v5-profiles.cjs` for mass/work, locks and drivetrain checks.
The generator documents its calibration/refit path. Run
`node verify-contact-mode.cjs` for interaction-switch checks.

With the app's installed Python environment:

```powershell
python verify_v5_scenarios.py --profile saved-configurations/v5-alpha0-4to1.json --profile saved-configurations/v5-alpha20-4to1.json --output .preview/v5-scenarios
```

The bounded matrix captures16 engine/scenario requests and four one-second
flat-support diagnostics. Each retains exact settings, rows, frames and source
hashes under ignored app output. Compatibility, successful first arrest/first
flight and agreement after an uncontrolled re-landing are distinct claims.
Native energy residuals are numerical/accounting differences, not physical
spring absorption. Spring packaging, tire/chassis interference, belt strength,
drive inertia and hardware motor/regeneration capability remain unassessed.
