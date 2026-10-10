# Draft terrain simulation and motor sizing development plan

Draft date: October 2, 2026. This proposal defines a numerical design tool for the Capstone wheel-legged platform. Its purpose is to convert terrain, speed, payload, mechanism geometry, and suspension objectives into joint motion, mechanical loads, and actuator requirements. Clear numbers, comparable plots, and reproducible runs take priority over interface polish.

The recommended progression is a single-leg sizing prototype, a two-leg planar vehicle model, and a calibrated four-corner design tool. Every stage uses the same terrain, mechanism, actuator, and result definitions. The first stage supports preliminary sizing; later stages add the interactions needed for hardware decisions.

## Design basis from the chats

The platform discussed in the cloud chats has four independently actuated wheel modules and two traction actuators, with front and rear wheels mechanically coupled on each side. Treat the roughly 20 kg platform and payload targets discussed previously as configurable planning assumptions until requirements are confirmed.

The user selected the geometry from **Create a rough animation** for the first prototype. Use its current intended configuration:

- A is the chassis pivot, above the wheel.
- Equal-length links A–B and B–C form the folding leg.
- A grounded large pulley and a knee pulley at B, with a 2:1 diameter ratio and the appropriate phase, make C move vertically in the ideal geometry.
- A separate rotary input coaxial at A drives a wheel at C through a transfer at B. The animation chat currently proposes two equal-ratio drive stages and a freely rotating compound pulley at B.
- The grounded suspension pulley, rotating upper link, and coaxial drive input are distinct mechanical parts. The drive transfer at B must also be independent of the pulley controlling the lower link.

The coaxial drive addition is being developed in the animation chat. Its actual dimensions, routing, and physical feasibility are not yet established. Use the arrangement as a model hypothesis and verify the transmission before using its predicted loads for purchasing hardware.

Spring location and compliance architecture are still unresolved. The initial recommended baseline is a spring acting in parallel with a backdrivable, torque-controlled leg coordinate, plus damping. Support an actuator-only comparison. If a series spring or independent passive coordinate is chosen, represent that additional motion explicitly. A perfectly locked leg coordinate cannot simultaneously provide passive suspension travel through that same coordinate.

The recurring design objective is broad acceptable terrain performance, with stronger performance on selected terrain families. Compare passive response, active damping, and body isolation under common terrain and hardware constraints. Allow each controller to be tuned for its mechanism. Body references should follow long terrain undulations and slopes while rejecting shorter disturbances; constant absolute chassis height over a long incline is not a feasible general target.

## What the tool must answer

For a specified design, terrain, speed, payload, and control objective, report:

1. Joint and wheel motion throughout the run.
2. Contact, spring, actuator, and internal mechanism loads available at that model level.
3. Required actuator torque and speed at the same instants, including sustained and transient demands.
4. Whether a candidate actuator achieves the requested performance when its limits are applied.
5. Which constraint fails first, and how geometry, spring choice, gearing, or speed changes the result.

Terrain geometry alone does not determine force. Kinematics determines motion relationships; dynamics and contact determine loads. A requested ideal motion also needs a physically feasible reference and contact state. Consequently, use two passes: **demand estimation with ideal actuation**, then **forward simulation with candidate actuator limits**. Keep their results separately labeled.

## Shared pipeline and data

```text
Terrain CSV or generator + geometry + mass + speed + performance targets
    → terrain validation and wheel interaction
    → suspension and vehicle dynamics with a controller
    → angles, velocities, accelerations, contact forces and joint loads
    → actuator demand envelope and candidate actuator checks
    → plots, capability tables, failure reasons and saved run data
```

Candidate actuator mass, inertia, losses, and response limits feed back into the dynamic model. A gearbox change is therefore a new simulation case, not just a conversion applied to an old report.

Use SI units internally: m, s, kg, rad, N, N·m, A, V, W and J. Display mm, degrees, rpm and Wh where helpful. State the coordinate system, angle zero, sign conventions, and shaft reference. Distinguish ground height, wheel-centre height, suspension extension, and body height.

| Record | Minimum content |
| --- | --- |
| Terrain | Distance and height arrays, units, source, sample spacing, uncertainty if known, seed and generation parameters when synthetic |
| Mechanism | Link lengths, pivots, angle limits, pulley ratios and phase, wheel radius, spring attachment, component masses and inertias |
| Scenario | Payload and location, initial conditions, speed or drive command, controller mode, performance thresholds |
| Actuator | Output or rotor shaft reference, torque–speed data, continuous and transient limits, ratio, inertia and losses when known, source and test conditions |
| Run | Input snapshots, software and solver versions, timestep, model level, seed, status, warnings, full histories and summary metrics |

Accept the existing atlas CSV columns `distance_m,relative_elevation_m,provenance` through an adapter. Use a canonical distance and height schema for new imports. Validate finite values, increasing distance, unit declarations and sufficient resolution. Reject missing sections or require an explicit gap-handling choice; preserve raw data alongside processed data. Resampling does not create missing terrain detail.

Synthetic inputs must control grade, detrended roughness RMS, wavelength or correlation length, obstacle height, width, shape, edge radius and spacing. Store surface mechanics separately. Define the roughness statistic and measurement window. Use repeatable seeds and distinguish periodic tests from stochastic test sets.

The terrain layer is now specified in [Terrain data and profile specification](terrain-data-and-profile-specification.md). It includes the original eleven terrain archetypes, visually verified USFS ATV design benchmarks, a retrieved 1 m USGS DEM transect, and explicitly synthetic cycle examples. Each parameter must carry its own evidence type and scale. Terrain names select a record of parameters and evidence; they do not by themselves establish a measured roughness value or a natural repeat cycle.

## Version 1 single leg sizing prototype

**Decision supported:** compare geometry, spring and preliminary actuator requirements on smooth terrain with a declared supported mass. Proposed effort is roughly 2–3 focused development weeks, depending on availability and unresolved geometry.

### Core implementation

1. **Terrain ingestion and generation.** Import measured or synthetic 2D profiles and generate flat ground, smooth ramps, sinusoidal waves, rounded bumps and correlated random roughness. Make 100 m and 1 km outputs core terrain-layer features, with shorter 5–50 m cases for solver validation. Show 1 km context, the same route's 100 m detail and individual cycles at 5–10 m. Preserve grade, roughness and obstacle layers separately; display source, evidence type and added assumptions with the parameters. Defer large batch dynamic missions until the short tests are validated. Sharp steps remain explicit geometry for Version 2; do not differentiate discontinuities to invent impact loads.
2. **Actual linkage calculator.** Implement the animation geometry, pulley constraints and coaxial drive mapping. Report upper and lower link angles, relative knee angle, extension, wheel path, motion ratios and reachable range. Verify that changing drive angle at fixed leg pose rotates the wheel and that folding at fixed drive input produces the predicted wheel rotation.
3. **Spring and static load model.** Calculate spring length or deflection at its actual attachment, preload, static sag, holding torque, compression and extension reserve, and wheel stiffness across payload and pose. Include component gravity. Produce quasi-static pin and belt loads from free-body equilibrium where the geometry and tension assumptions are defined. Label unavailable reactions explicitly.
4. **One-corner dynamics.** Connect the leg to a vertically guided supported body mass and wheel or unsprung mass. Include wheel/tire compliance and an explicit contact assumption. Start with small smooth motions and validate the local model; add nonlinear linkage mapping and moving inertia consistently. A quarter of sprung mass is only the symmetric screening assumption, not a universal wheel load.
5. **Control comparisons.** Run the declared passive/backdrive condition, active damping, and body isolation on the same test. Define whether an inactive actuator is backdrivable, resistive or locked. Apply travel limits. For the candidate pass include a torque–speed envelope and simple finite response; unknown response values become sensitivity cases, not manufacturer claims.
6. **Actuator report and small sweeps.** Sweep speed, payload, spring rate/preload and a small number of geometry variants. Export full histories, summaries and plots. If current conversion is unavailable, report torque requirements and leave current unknown.

For equal link lengths L and fold angle q measured from the downward vertical, an ideal reference model is:

```text
wheel x relative to A = 0
leg extension ell(q) = 2 L cos(q)
dell/dq = -2 L sin(q)
```

The knee relation depends on the declared angle convention and belt phase; encode it once and verify it against the animation. Near the straight posture, `dell/dq` approaches zero. Small calculated support torque there does not establish a good operating point: the inverse motion requirement becomes ill-conditioned and internal loading must be checked. Exclude singular regions with an explicit usable range.

For a force transmitted through an axle, its generalized load contribution is `J(q)^T F`. Add gravity, inertia, spring/damper forces, transmission reactions and losses consistently; this contribution alone is not total motor torque. Belt and pin forces require constraint reactions or link free-body equations. The [MuJoCo dynamics documentation](https://mujoco.readthedocs.io/en/stable/computation/index.html) describes the motion and force mappings and coupled dynamics.

### Required plots and numbers

| Plot or table | Purpose |
| --- | --- |
| Terrain and wheel/body height | Verify what ground input the system actually experiences |
| Leg extension and all joint angles | Expose working range, phase conventions and travel limits |
| Jacobian, spring support and holding torque versus pose | Compare leverage and spring assistance throughout travel |
| Torque, angular speed and acceleration versus time | Locate transient demand and its terrain event |
| Torque–speed operating points with candidate envelope | Check simultaneous requirements rather than independent headline peaks |
| Body acceleration and support/contact force | Compare isolation, oscillation and loss of support within the model scope |
| Speed versus peak/RMS load, travel margin and body acceleration | Identify usable operating ranges and trade-offs |

Summaries include peak positive/negative torque, RMS torque, holding torque, peak speed, peak mechanical power, longest intervals above declared load thresholds, saturation time, travel reserve and body acceleration RMS/peak. Pair each extreme with its time, terrain location, joint and operating condition. Report mechanical positive and negative work separately. Stationary support can consume electrical power even when mechanical power is zero.

**Version 1 completion gate:** a saved case reproduces the same result; static loads and ideal linkage equations agree with independent hand calculations; the Jacobian passes a numerical derivative check; the local smooth response agrees with an analytical spring–mass reference; timestep and terrain-resolution refinement leave the main conclusions stable; impossible travel or contact assumptions are flagged; demand and limited-actuator runs are clearly separated. Set numerical tolerances before testing, using tighter tolerances for analytic kinematics than nonlinear contact quantities.

**Scope limit:** this version does not establish step-climbing ability, front/rear load transfer, roll, tank-turning loads, final structural stress, or final hardware suitability.

## Version 2 planar vehicle and credible hardware sizing

**Decision supported:** narrow motors, gearing and springs using front/rear interaction, propulsion and obstacle crossing. Proposed effort is a further 3–5 focused development weeks; overlap experimental calibration with development.

Build one side of the vehicle with front and rear copies of the same leg, a shared rigid chassis, wheel rotation and one traction input. Under left/right symmetry use half the shared sprung mass and pitch inertia while retaining actual per-leg component properties. Keep front/rear wheel coupling in the transmission model; do not assign independent wheel controllers.

Add:

- Chassis forward motion, heave and pitch; payload CG and inertia; actual per-corner component mass and wheel inertia.
- Wheel-size-aware collision/contact for steps, logs, ditches, crests and repeated bumps, allowing slip and separation. Use explicit primitives for vertical faces; a sampled smooth profile cannot faithfully represent every obstacle.
- Drive and braking reactions through the articulated transmission. Check belt path length, take-up, wrap, tension and bearing loads as routing becomes defined. Do not infer belt preload or absolute tension solely from drive torque.
- Candidate-specific torque/current/speed limits, reflected inertia, friction, latency, response lag and slew limits. Preserve rotor/output conventions and avoid counting reflected inertia twice.
- Torque–speed and load-duration checks, approximate electrical losses and a lumped thermal model when the needed data exists. Unsupported thermal or dynamic ratings yield unknowns and parameter sweeps.
- Larger sweeps over terrain, speed, payload, posture, gearing, spring parameters, control gains and random seeds. Tune mechanisms under the same objectives and sensing assumptions.
- An initial measured single-leg dataset: angles, spring force, motor current, load, body acceleration and timestamps. Calibrate friction and damping; test actuator delay and reversal response.

Use Python as the proposed numerical orchestration layer, with array/ODE tools and plots; use MuJoCo for contact-driven cases. This is a design recommendation based on its articulated dynamics, coupling constraints and Python interface, described in the [official overview](https://mujoco.readthedocs.io/en/stable/overview.html). Keep the fast screening model as an independent check rather than rewriting all modules around a viewer.

Publish capability plots for roughness amplitude × wavelength, obstacle height × width, and grade × payload. Each cell shows tested passing speed or a failure reason. Search speed in multiple intervals if resonance creates non-monotonic passing regions; report tested ranges rather than assuming every slower speed passes.

**Version 2 completion gate:** front/rear static equilibrium and mass scaling are checked; candidate limits actually affect motion and success; obstacle results withstand solver/contact and timestep sensitivity checks; internal transmission coupling is verified; at least one physical leg dataset is compared with predictions; numerical peaks that do not converge remain flagged. Preliminary hardware sizing carries margins and clearly stated unvalidated conditions.

## Version 3 four corner design tool with experimental calibration

**Decision supported:** establish the platform's tested operating envelope and choose revisions using whole-vehicle behavior. Develop incrementally alongside hardware, rather than making the full tool a prerequisite for building the robot.

First connect four planar leg modules to one shared spatial chassis with heave, pitch and roll and separate left/right terrain tracks. This intermediate model supports asymmetric support and diagonal articulation. It is not yet a full steering or lateral-contact model.

Then add full spatial motion and suitable contact for tank turning, oblique obstacles, cross-slopes, lateral sliding and wheel lift. Retain four leg actuators and two coupled side drives. Extend reports to yaw/turning performance, underside clearance, chain/belt loads, support margin and transient corner loads.

Add measured terrain routes when resolution supports the features being modeled; calibrated motor, loss and thermal data; battery voltage/current/charge-acceptance constraints; electronics consumption; mission energy and range; and synchronized hardware replay. Separate suspension and propulsion energy. Account for regeneration and braking-energy disposal, rather than subtracting all negative mechanical work from battery use.

Add optional terrain preview only after the feedback baseline works. Compare feedback-only, accurate preview and degraded preview with delay and position/height error. Preview cannot remove travel, speed or force limits.

Provide batch comparison and sensitivity/uncertainty bands. Add optimization only after reproducibility and validation gates pass. Keep rigid-ground friction distinct from soil deformation; introduce soft-ground models only if experiments or trusted parameters justify them. Learning controllers, photorealistic worlds and detailed electromagnetic motor design are separate extensions.

**Version 3 completion gate:** predictions are compared against held-out terrain and hardware tests; errors and parameter uncertainty are reported; failures are retained in the results; mission and thermal conclusions use validated inputs; turning and cross-slope capabilities are supported by the applicable model and tests.

## Reporting and interface rules

The initial interface can be configuration files plus a run command and a generated report. A later minimal page needs only input selection, run/sweep controls and a results view. Show a mechanism sketch for debugging angle conventions; animation is secondary to the histories and decision plots.

Every plot must have a descriptive title, labeled units, declared shaft/coordinate, readable legend and scenario context. Synchronize time or distance across history plots; show travel and actuator limits; use consistent scales when comparing designs; retain raw data and peak timestamps when displaying downsampled curves. Mark filtered and unfiltered accelerations separately.

Every summary must distinguish completed, failed, aborted and numerically invalid runs. Low torque from a run that stopped before the obstacle is not a successful small-motor result. Preserve failures and their locations. Do not collapse all performance into one score that hides an essential terrain family failing.

Proposed labels are **meets target**, **usable at reduced speed or declared compromise**, **outside constraints**, and **unknown**. Require configurable thresholds for speed, payload acceleration, travel, contact, temperature and electrical limits. No robot-specific acceptance numbers have been approved in this draft.

For motors, prioritize simultaneous torque–speed operation, peak duration, RMS torque/current, inertia, voltage headroom, latency, slew and output bandwidth. The [maxon motor simulation guidance](https://support.maxongroup.com/hc/en-us/articles/360013761160-Motor-data-and-simulation) explains why operating conditions, electronics and consistent motor constants matter. The prior RobStride chat leaves some inertia, response and peak-duration fields unverified; import those as unknown until checked, not as zero or inferred from communication frequency.

## Existing terrain atlas integration

The local [README](../README.md) describes an illustrative mobility atlas with a synthetic profile export. Inspection of `src/main.js` shows a 50 m preview at 0.2 m sample spacing, made from two sinusoidal components and a reduced slope term. Obstacle dimensions and spacing do not drive that profile.

Reuse its CSV interface and source labeling. Replace the preview generator for engineering work with the Version 1 generator and resolution checks. Do not treat the atlas's entered capability limits or regional percentages as dynamically achieved vehicle performance. Eventually, validated simulation results can supply capability envelopes back to the atlas under stated speed, payload and surface conditions.

## Recommended build order and calendar

1. Freeze angle conventions, belt constraints, compliance topology and record schemas.
2. Implement terrain import/generation, analytic linkage, static support and spring plots.
3. Add guided-mass dynamics, demand histories and candidate limits.
4. Add repeatable short test cases and speed/payload sweeps; complete Version 1 validation.
5. Add shared chassis pitch, coupled drive and explicit obstacle contact; measure the first physical leg.
6. Calibrate Version 2 and use it to support motor/spring downselection.
7. Add four-corner interactions and selected spatial tests as hardware develops.
8. Complete mission, thermal, preview and uncertainty analysis only where they support current design decisions.

The earlier timeline chat targets a March 2027 demonstration with February reserved for fixes and validation. Suggested calendar targets are Version 1 in mid/late October, Version 2 sizing and leg-test correlation through November, and Version 3 features introduced selectively from December through February. These are planning targets, not measured delivery estimates. Avoid delaying the physical leg prototype until the full simulator exists.

The next concrete implementation milestone is **one reproducible terrain case through the actual belt leg to a complete joint-load report**, with a speed sweep and clear failure flags. It should answer what torque and speed are required, what the spring contributes, and what changes when the candidate actuator cannot meet demand.

## Source chats and review limits

Reviewed accessible text from twelve cloud Capstone chats, plus the selected local animation chat. The core sources are:

- [Robot Simulation Tools Brainstorm](https://chatgpt.com/c/6abca1c0-c654-83e9-8c1e-b91a49deedf8): connected modules, planar vehicle, terrain-driven sizing and comparative capability.
- [Terrain Variability Studies](https://chatgpt.com/c/6abb5d6d-029c-83ea-8d0d-cab0e6a3ef19): height-versus-distance profiles, random and periodic generation and terrain descriptors.
- [Motor Metrics Needed](https://chatgpt.com/c/6abda3a8-d12c-83ea-ba91-a06552449cb8): actuator response, inertia, shaft references, internal loads and motor-data gaps.
- [Active Suspension Operation](https://chatgpt.com/c/6abe9c2b-534c-83ea-a977-1f6f8b36f21d): force control, springs, guided-mass and shared-chassis models, damping and isolation objectives.
- [Explain Linkage Animation](https://chatgpt.com/c/6abdad23-d440-83e9-97e5-8153f7e42954): grounded pulley, knee coupling and ideal straight-line geometry.
- [Simulation Tools Map](https://chatgpt.com/c/6abeb9a9-a2c4-83e9-9e13-7a32a550f602): tool inputs and outputs; its embedded diagram was not present in the retrieved text.
- [Chinese EV Suspension Comparison](https://chatgpt.com/c/6abe9e2d-33a4-83e9-b062-a1d1c8ec3862): preview versus feedback and physical actuator limits.
- [Six Actuator Robot Design](https://chatgpt.com/c/6abc9799-dd14-83e9-b935-a93f37e07df6): four suspension inputs and two coupled side drives.
- [Development Timeline Planning](https://chatgpt.com/c/6abe9aec-0a70-83e9-9a18-84ed1310d1d5): physical prototype and March demonstration timing.
- **Create a rough animation**, local Codex chat: selected inverted belt leg and current coaxial drive addition.

Also scanned Robot Specs Comparison, Robot Design Search Terms and Teleoperation Link Design for relevant requirements and sensing context. Some long chat responses are truncated by the retrieval tool, and cloud attachments are not included. This draft is grounded in the accessible discussion and local source, not an audit of the latest Notion specs, motor spreadsheet, CAD or hardware. Robot ratings and previous assistant recommendations are not treated as verified manufacturer data.
