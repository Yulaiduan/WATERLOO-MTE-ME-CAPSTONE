# CAMEL geometry and spring ranges for the requirement tests

[Documentation home](../../README.md) · [Simulation component](../../../simulation/README.md)

Study date: 2026-10-02, America/Toronto. Prepared with Codex for Yulai Duan; publication package updated 2026-10-03. Status: literature review and verified analytical screening. These are proposed simulation inputs; no driven terrain simulation, hardware test, component selection, or team design decision was completed here.

## Main recommendation

For a 150 mm step and a slope above 30° **with some chassis pitch allowed**, start with **235–250 mm equal links**, **300–400 mm outside wheel diameter**, **0.7–1.2 kg per complete wheel**, and a **loaded whole-robot COM 300–400 mm above the ground**, centered over the support footprint. Use the 240 mm link, 350 mm wheel, and 25 kg unloaded robot below as one explicit assumption set. The earlier 11.2 kg compact case remains a separate comparison, not an established final mass.

The most important alternative is a **horizontal chassis on the slope**. At a 700 mm wheelbase, the ideal geometry requires 312 mm links for 30° and 379 mm links for 35°, before travel reserve. Explore approximately **400–430 mm** if horizontal chassis operation at 35° is required. That alternative raises torque, mass and packaging demands and needs a fresh COM design.

The literature supports the mechanisms and optimization methods. The dimensional intervals above are engineering screening recommendations derived here, not published universal optima. Wheel mass is especially a mass budget pending a real assembly, load rating and structural check.

## Requirements and evidence

The Table 1 screenshot supplied on 2026-10-02 takes precedence over the older local proposal transcription: robot mass <35 kg; cost <CAD 15,000; width ≤750 mm; payload/robot mass ≥0.3; slope >30°; step ≥150 mm; range ≥15 km; storage volume reduction ≥30%; teleoperation ≥100 m. The local proposal describes concrete for slope and flat concrete for range. Test payload, speed and surface condition remain to be fixed. The screenshot resolves the older note about the storage-volume inequality for this study.

The mechanism is four coupled one-DOF legs plus two shared side-drive commands. A free chassis still has six spatial degrees of freedom. The reviewed proposal selects 6-DOF-B with a spring wound around a hip drum rotating with the upper link. Its actuator description is not sufficiently precise to identify every shaft and reaction path. Knee torque values below assume the actuator applies torque to the **relative knee joint**, between upper and lower links. A chassis-mounted motor needs its actual transmission relationship applied.

### Relevant online findings

| Source | Evidence and its use here |
| --- | --- |
| [Alamdari and Krovi, 2016](https://doi.org/10.1016/j.mechmachtheory.2016.02.010) | Articulated leg-wheel design combines link geometry with spring stiffness/preload optimization. The accessible publisher abstract supports this design method; full numerical results were not accessible and were not used as CAMEL dimensions. |
| [Bjelonic et al., 2023](https://arxiv.org/html/2301.03509v1) | Experiments on ANYmal with an optimized parallel spring report a 33% improvement in the torque-square metric, 30% lower maximum joint torque, and 11% longer operation time on flat terrain. Their spring/cam is different from CAMEL. This supports measuring battery energy separately from torque reduction. |
| [Belov et al., 2024](https://arxiv.org/html/2411.18295v1) | Derives optimal linear spring parameters from angle and torque histories by minimizing squared residual actuator torque. Its reported large gains concern a simplified simulated leg; this study uses the fitting idea without transferring those gains to CAMEL. |
| [Keep Rollin, 2019](https://arxiv.org/abs/1809.03557) | A wheeled ANYmal experiment reports 83% lower cost of transport relative to its legged comparison and a speed of 4 m/s. This supports wheeled cruise but gives no direct 15 km prediction for CAMEL. |
| [Schwalbe rolling resistance guidance](https://www.schwalbe.com/en/technology-faq/rolling-resistance/) | Tire diameter, pressure, tread and construction affect losses. Smaller diameters increase deformation at the same pressure; road and rough-surface pressure tradeoffs differ. Diameter alone cannot identify an energy optimum. |
| [Schwalbe 50-203 Big Apple specification](https://www.schwalbe.com/en/Big-Apple-11100681.02) | The indexed manufacturer page lists 310 g for the tire and a 55 kg maximum tire load. It is a tire-only value, not a complete wheel mass or a CAMEL impact/side-load rating. Product revisions differ; verify the purchased SKU. |
| [Boston Dynamics patent US11130235B2](https://patents.google.com/patent/US11130235B2/en) | Describes a 2:1 hip/knee belt relationship producing straight-line endpoint motion. It supports the mechanism concept, not CAMEL's detailed pulley topology or performance. |

## Proposed simulation inputs

All numerical inputs in this table are proposed assumptions unless marked as a user requirement. The intervals are not a Cartesian product of guaranteed feasible designs.

| Input | First exploration | Seed |
| --- | --- | --- |
| Equal pivot-center link lengths | Broad comparison 160–400 mm; prioritize 235–250 mm if pitch is allowed | 240 mm each |
| Hip angle from chassis downward vertical | Stops at 25° and 75° provisionally; ride pose 45–55° | 50° |
| Relative knee angle | q_k = −2θ, with verified sign, zero and axes | −100° at ride pose |
| Tire outside diameter | 300–400 mm; retain 508 mm as the earlier large-wheel comparison | 350 mm |
| Tire width | 40–65 mm as a packaging exploration | 60 mm |
| Complete wheel mass | 0.7–1.2 kg, excluding remote motors; stress test up to 1.5 kg | 0.90 kg |
| Each moving link mass | 0.25–0.50 kg provisional budget including its carried fittings | 0.35 kg |
| Unloaded robot mass | Use the actual mass budget; screen 20, 25, 30 and the 35 kg boundary | 25 kg |
| Payload | 0 and 0.3 × unloaded mass; also test heavier/offset loads if intended | 7.5 kg; 32.5 kg gross |
| Chassis assembly mass | Total less moving links and wheels; include battery, all chassis-mounted motors and electronics | 18.6 kg |
| Wheelbase / track between contact centers | 650–800 / 550–650 mm, coupled to COM and steering losses | 700 / 600 mm |
| Whole-system COM including payload | 300–400 mm height; aim near the lower end while keeping obstacle clearance | ≈350 mm |
| COM offsets | Prefer longitudinal offset ≤0.05 wheelbase and lateral offset ≤0.05 track on level ground | Centered; test ±35 mm longitudinal and ±30 mm lateral |
| Hip spring drum effective radius | 40–60 mm, distinct from the 2:1 coupling pulleys | 50 mm |
| Spring force at the 25° stop | Approximately 200–300 N for the 25 kg robot / 0–7.5 kg payload case | 272 N for the loaded fitted case |
| Linear spring rate | About 5–8 N/mm across empty/loaded fits at 240 mm links and a 50 mm drum | 7.35 N/mm loaded fit |
| Nominal gravity-assist target | Sweep 75%, 90%, 100%, plus spring disabled | 90% target over the angular interval |
| Straight cruise speed | 0.5, 1.0, 1.5 m/s, subject to torque-speed limits | 1.0 m/s for the range calculation |
| Contact friction and rolling resistance | μ = 0.4, 0.6, 0.8, 1.0; Crr = 0.01, 0.02, 0.04 initially | Assumptions to replace with measurements |

At the seed pose the hip is 483.5 mm above the ground. A feasible mass layout must produce the COM target: for illustration, put the 18.6 kg chassis assembly COM 120 mm below the hip plane and the 7.5 kg payload COM at 400 mm ground height. Uniform 0.35 kg links and 0.90 kg wheels then give an approximately 348 mm loaded COM. This is a packaging target, not an assertion that the current CAD fits it. Belly clearance and guards must be checked.

The 600 mm track and 60 mm tires give a 660 mm tire envelope; pulleys and guards can increase overall width. The 700 mm wheelbase and 350 mm wheels give a 1050 mm tire length. Outward knee sweep can extend the centerline envelope to about 1164 mm before component thickness.

The 35 kg unloaded case is a conservative boundary calculation: the requirement is strictly less than 35 kg. Its 0.3 payload ratio corresponds to a 45.5 kg gross boundary. Do not use 35 kg as the loaded mass when checking this corner.

## Link length and usable obstacle travel

Let θ be upper-link rotation from downward vertical fixed to the chassis. For equal links and q_k = −2θ,

\[
x_w=0,\qquad z_w=-2L\cos\theta,\qquad J_z=2L\sin\theta.
\]

With provisional 25–75° limits, the **total** usable upright stroke is 1.29498 L. Upward travel available from the 50° ride pose is only 0.76794 L:

\[
\Delta z_\mathrm{bump}=2L(\cos50^\circ-\cos75^\circ).
\]

| Each link | Total stroke | Upward travel from 50° | Largest ideal slope with a horizontal chassis, B = 700 mm |
| --- | --- | --- | --- |
| 160 mm | 207 mm | 123 mm | 16.5° |
| 200 mm | 259 mm | 154 mm | 20.3° |
| 220 mm | 285 mm | 169 mm | 22.1° |
| 240 mm | 311 mm | 184 mm | 23.9° |
| 250 mm | 324 mm | 192 mm | 24.8° |
| 350 mm | 453 mm | 269 mm | 32.9° |
| 380 mm | 492 mm | 292 mm | 35.1° |

The 150 mm target plus an **assumed 30 mm travel reserve** requires L ≥234.4 mm at this ride pose. This motivates 235–250 mm as the first region to investigate. The upper endpoint is a compactness/torque preference, not a demonstrated optimum. At a fixed load and angle, torque increases linearly with L. The old 350 mm example demands about 46% more gravity torque than 240 mm links, before its likely increase in link mass.

This is a clearance screen, not a step-climb proof. A grounded rear axle can push a front wheel into a step; a 1-DOF vertical leg cannot move its wheel forward independently of the chassis. Verify the full approach, lift/contact sequence, three/four-contact support, tire traction, belly collision, motor torque and suspension-induced wheel rotation. A 300 mm wheel has radius equal to the target step; wheel diameter alone does not establish passive traversal. The axle-push-only ideal rigid-wheel relation F/W = sqrt(2rh−h²)/(r−h) for 0<h<r becomes unfavorable near h=r. It excludes wheel torque and active lifting and is not a limit on the complete robot.

### Slope levelling changes the preferred geometry

A horizontal chassis with wheel centers separated horizontally by B needs a front/rear leg-extension difference B tan α. For B = 0.7 m this is 404 mm at 30° and 490 mm at 35°. Divide by 1.29498 to obtain the minimum equal link lengths, 312 and 379 mm respectively. These are endpoint-to-endpoint limits with no residual travel margin. A 400–430 mm exploration adds modest reserve at 35° but must be rechecked for clearance and loads.

Climbing 35° while the chassis pitches is a different requirement. With the ideal seed geometry, using the full available stroke can reduce chassis pitch to about 35−atan(0.311/0.700) = 11.1°. This consumes the available differential stroke and is not a dynamic operating guarantee. A 240 mm design cannot promise a horizontal chassis on that slope.

## COM and traction for slopes

For slow motion on a planar grade, with all wheels driven and sufficient torque,

\[
\mu_\mathrm{required}\ge \tan\alpha+C_{rr}.
\]

At Crr = 0.02 this is 0.597 at 30° and 0.720 at 35°. Testing a measured tire/surface combination around μ = 0.8 is a reasonable first 35° scenario; it is not a universal friction value for concrete. Loose or wet surfaces need their own measured traction model. μ = 0.35 or 0.20 cannot sustain this climb in the simple friction-limited model. Extra torque or preload cannot overcome that traction bound.

Let h be COM height normal to the support plane in the tested pose, and x its uphill offset from the contact-footprint center along that plane. The distance of the gravity projection from the downhill edge is

\[
d_x=B/2+x-h\tan\alpha.
\]

Use an actual pose/contact calculation when the chassis is actively levelled. For a centered simplified configuration at 35°, an **assumed 10% wheelbase reserve** gives h ≤0.4B/tan35° =400 mm for B =700 mm. The corresponding cross-slope result is only 343 mm at T =600 mm. A 350–400 mm COM may be appropriate for an uphill test while giving less side-slope margin; uphill capability does not establish equal cross-slope capability.

At B =700 mm, centered static fore/aft tipping angles are 49.4°, 45.0°, 41.2° and 35.0° for COM heights 300, 350, 400 and 500 mm. Actual operations must stay below these boundaries and account for COM shifts, braking, accelerations and contact loss. Prefer central low battery/payload placement over adding wheel ballast. If only uphill travel matters an uphill COM shift helps; centered placement is a more balanced starting point for uphill, downhill and turning.

## Wheel mass and inertia

There is no nonzero ideal wheel-mass optimum from the requirements alone. Reduce wheel mass until strength, traction, tire size, side load, bearings and impact life become binding. The proposed 0.7–1.2 kg interval budgets a complete 300–400 mm wheel, including tire, tube if present, rim, hub, axle fittings and driven pulley. It is not measured vendor data. Use actual assembly mass before hardware selection.

Initially bracket spin inertia by I = κ m_w r² with κ =0.5–1.0, or use CAD. For the 0.90 kg, 175 mm radius seed, that is 0.0138–0.0276 kg m². It is a screening bracket for hub-to-rim mass distribution; the other principal inertias also need geometry. Joint-mounted mass and motor inertia reflected through gearing must remain in the model.

Low unsprung mass primarily helps contact response and impact loads. At steady flat speed, extra wheel mass contributes ordinary rolling resistance. Adding 0.5 kg to each wheel adds about 2.2 Wh over 15 km at Crr =0.02 and η =0.75, before other effects. It does not justify claiming a large constant-speed range gain from wheel mass alone. Repeated acceleration, impacts, steering and terrain deformation can change that comparison.

## Hip spring regression and knee torque

### Static load model

The regression uses a level chassis, four identical legs and symmetric grounded wheels. Let m_c include chassis plus payload, m_u and m_l be uniform upper/lower link masses per leg, and m_w the wheel mass. With the wheel centers at fixed ground height, the effective supported force is

\[
F_*=g\left(m_c/4+3m_u/4+m_l/4\right),\qquad
\tau_g(\theta)=2LF_*\sin\theta.
\]

This follows by differentiating the gravitational potential energy of the chassis and both links. It excludes wheel weight from the lifting work because wheel centers are fixed in this symmetric standing test. Do not substitute it for asymmetric obstacle loads or airborne-wheel dynamics.

For a motor applying torque to relative q_k =−2θ, virtual work gives |τ_k| = |τ_g−τ_s|/2 and |qdot_k| =2|θdot|. The torque reduction is accompanied by twice the joint speed. If the actual motor coordinate is φ_m, use τ_m = (τ_g−τ_s)/(dφ_m/dθ) ideally, then include losses, inertia and torque-speed limits. The two wheel-drive motors also have distinct transmission paths and power budgets.

### Actual spring law and fit

A circular hip drum with radius r_s, increasing spring extension as θ increases, gives

\[
F_s(\theta)=F_\mathrm{pre}+k r_s(\theta-\theta_\min),\qquad
\tau_s=r_sF_s.
\]

F_pre is the **total tension at the 25° extended stop**. This is not tension at the ride pose, not belt pretension, and not spring stiffness. A real extension spring's built-in initial tension must be included separately when translating the force into installed extension.

We fit a+b(θ−50°) to τ_g over 1001 equally spaced angles from 25° to 75°. Angles inside equations are radians. For the 32.5 kg gross seed,

\[
\tau_g=32.3730\sin\theta\ \mathrm{N\,m},\quad
\widehat\tau_g=24.0182+20.4147(\theta-0.872665)\ \mathrm{N\,m}.
\]

The fit has **R² =0.981997**, RMSE 0.697 N m and maximum absolute error 1.656 N m in hip-equivalent torque. This is a fit to a derived static gravity curve, not regression on published robot data or measured range/step performance. Uniform-angle sampling is an explicit assumption. A mission-weighted fit should use time spent in each pose, actual load histories and motor constants.

Scaling this fitted curve to a **90% assistance target** gives the following separate tuning cases at L =240 mm and r_s =50 mm:

| Gross mass | Preload at 25° | Spring rate | Tension at 50° | Maximum tension at 75° | Additional spring travel |
| --- | --- | --- | --- | --- | --- |
| 25 kg, empty seed | 198 N | 5.34 N/mm | 314 N | 431 N | 43.6 mm |
| 32.5 kg, loaded seed | **272 N** | **7.35 N/mm** | **432 N** | **593 N** | **43.6 mm** |
| 45.5 kg boundary case | 401 N | 10.82 N/mm | 637 N | 873 N | 43.6 mm |

The 90% target applies to the fitted curve across travel. At 50° it supplies about 87.2% of the exact gravity torque. The loaded seed's ideal knee holding torque falls from 12.40 to 1.59 N m at that pose. This does **not** establish a sufficient motor rating: uneven support, slope forces, lifting a wheel, damping and acceleration remain to be added.

For the same angles, the force scales approximately as LF*/r_s and stiffness as LF*/r_s². Increasing drum radius from 40 to 60 mm reduces required force to two thirds and stiffness to four ninths, but increases spring travel by 50%. The 2:1 coupling-pulley radius and spring-drum radius are separate design choices.

One physical spring has one rate: the rows do not describe a preload adjustment that changes stiffness. For a first 25–32.5 kg model, keep about 7.35 N/mm and sweep preload approximately 200–300 N, allowing the motor to carry residual mismatch. To cover the 45.5 kg boundary or longer links, retune the rate or size more motor authority. The general 75–100% fitted-assistance sweep for the loaded seed spans 227–302 N preload and 6.12–8.17 N/mm; for the 45.5 kg boundary it spans 334–445 N and 9.02–12.03 N/mm.

The least-squares optimum for static torque residual alone is the 100% fit. The proposed 90% point deliberately leaves some positive motor support; it is a control/packaging starting point rather than a demonstrated range optimum. Springs can oppose retraction when a wheel is unloaded. Check retention, force over the full stroke, cable curvature, hard stops, spring hysteresis and damping. Gravity compensation alone does not demonstrate an unpowered stable posture or adequate ride damping.

## Propulsion and the 15 km target

At 35°, Crr =0.02 and 175 mm wheel radius, the minimum summed wheel torque per side is

\[
\tau_\mathrm{side}={Mg(\sin\alpha+C_{rr}\cos\alpha)r_w\over2}.
\]

It is approximately 16.5 N m at 32.5 kg gross and 23.0 N m at 45.5 kg gross. These are **wheel-equivalent side totals**, not per-wheel or motor-shaft ratings. Divide by side-drive reduction and efficiency for motor torque, and check the simultaneous speed. At 1 m/s the wheels turn 54.6 rpm. Unequal wheel loading and coupled front/rear belts still require traction and transmission analysis.

For constant straight motion on level concrete, an initial electrical-energy equation is

\[
e_\mathrm{Wh/km}={1\over3.6}\left({C_{rr}Mg\over\eta_d}+{P_\mathrm{aux}+P_\mathrm{susp}\over v}\right),\qquad
E_\mathrm{nominal}\ge{15e\over f_\mathrm{usable}}.
\]

Here η_d includes propulsion conversion and drivetrain losses; the other power term covers electronics and suspension electrical demand. Turning, drag, terrain work, acceleration, thermal limits and slope are omitted in these examples. Negative mechanical work is not automatically recovered into the battery.

For M =32.5 kg, Crr =0.015, η_d =0.75 and f_usable =0.80:

| Cruise speed | Auxiliary plus suspension power | Energy per km | Nominal capacity for 15 km |
| --- | --- | --- | --- |
| 1.0 m/s | 30 W | 10.10 Wh/km | 189 Wh |
| 1.0 m/s | 50 W | 15.66 Wh/km | 294 Wh |
| 1.0 m/s | 100 W | 29.55 Wh/km | 554 Wh |
| 0.5 m/s | 100 W | 57.33 Wh/km | 1075 Wh |

Thus 400–600 Wh is a useful **candidate battery interval only if** the measured cruising load is close to the 1 m/s cases. It is not a battery selection or verified 15 km range. Battery mass must be included in the 25 kg budget. Sustained climbing requires elevation energy; a 15 km flat-concrete pass cannot establish 15 km rugged-terrain endurance.

For total constant auxiliary/suspension power, every extra 10 W at 1 m/s costs41.7 Wh over15 km. This can matter more than modest wheel-mass savings. Minimize total measured Wh/km while preserving terrain performance; a reduction in motor torque-squared is only a copper-loss proxy, not a full battery-energy prediction.

## What to optimize in the first full vehicle simulation

Use a constrained comparison rather than a single weighted score that can trade away a failed requirement. Retain only candidates meeting the agreed tests, then compare energy, mass, torque reserve, body acceleration and packaging on a Pareto front.

| Metric | Proposed test or calculation |
| --- | --- |
| Step ≥150 mm | Sweep 100, 150, 180 mm at 0.1–0.3 m/s as initial assumptions; use loaded/unloaded and varied friction cases. Log completion, body collision, support contacts, slip, peak/RMS torque and saturation. |
| Slope >30° | Test 32° and 35° uphill/downhill on the specified surface and payload. Record whether body levelling is required. Evaluate cross-slope separately. |
| Range ≥15 km | Electrical Wh/km with battery state, usable capacity, cruise speed, payload, tire pressure and terrain fixed; include controller/electronics and shared drive limits. |
| Payload ratio ≥0.3 | Drive with at least 0.3 × robot mass; vary its position/height. Passing flat payload travel alone does not establish slope/step capability with that payload. |
| Mass <35 kg | Mass ledger including spring drums, belts, guards, fasteners and battery; use changing link/wheel mass models in geometry optimization. |
| Width ≤750 mm | Maximum outer envelope including pulleys, guards and all tested configurations. |
| Volume reduction ≥30% | Folded external bounding-box volume / deployed external volume ≤0.70 with a defined packing method and no collision. Stroke alone does not prove this. |
| Cost <CAD 15,000 | Costed bill of materials with shipping, fabrication, electronics and contingency; link length alone cannot verify it. |
| Teleoperation ≥100 m | Separate radio/control test with latency, loss and stopping behavior; mechanical optimization cannot establish range. |

First vary equal link length, actual wheel packages, COM placement, drum radius and preload/rate together. Suggested broad link points are 160, 200, 240, 280, 350, 400 mm. Use at least empty and 0.3 payload cases, plus the 35 kg mass boundary. Maintain one realistic controller family and equivalent tuning effort across designs. Reject mechanical/contact failures before fitting an energy-response model. Then fit a cross-validated quadratic response surface or other surrogate to successful simulation data and verify its proposed optimum in fresh runs. Do not regress commercial robot headline specifications to infer CAMEL's optimum: the battery, gearing, control, mass and terrain conditions differ.

## Reproduction and checks

The reproducer is [requirement_parameter_screen.py](../../../simulation/experiments/requirement_parameter_screen.py). From the Capstone root:

```sh
.venv/bin/python simulation/experiments/requirement_parameter_screen.py --output simulation/results/requirement-parameter-screen
```

Retained outputs: [geometry](geometry.csv), [spring fits](spring_fits.csv), [spring curve](spring_curve.csv), [slope calculations](slopes.csv), [range examples](range_cases.csv), and [runtime, assumptions and script hash](summary.json).

Python 3.11.16 and NumPy 2.4.6 were used. This deterministic analytical calculation has no controller, integration timestep, random seed or contact solver. The 1001 samples are angular evaluation points. Finite differences of whole-system gravitational potential independently agree with the derived per-leg gravity torque to 1.41×10⁻⁸ N m; kinematic horizontal cancellation and knee/hip ideal power mapping also agree. These checks verify the calculation implementation, not the proposed operating envelope.

The 11.2 kg rows in spring_fits.csv are mass sensitivity at the new 240 mm geometry and 0.9 kg wheels, not a re-evaluation of the historical 160 mm compact platform. The current simulation model is unchanged. The earlier project records remain historical evidence with their original assumptions.

## Remaining inputs

Before calling any interval optimal, define whether the slope test needs a horizontal chassis; confirm the actuator's input/output shafts; provide actual tire and wheel assemblies, battery and motor efficiency maps, spring/damper packaging and force curves, and payload location. These determine which constraints become binding. The calculations above are enough to start comparative simulation, with all assumptions visible.

## Update log

- 2026-10-02: Added source-grounded design trends, original geometry/static spring regression, explicit knee torque mapping, slope and range screens, and a proposed requirement-test matrix. No hardware performance claim or team decision recorded.
