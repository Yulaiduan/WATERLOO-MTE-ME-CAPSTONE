# Terrain specifications for simulation and training

**Status:** proposed training/test design, not accepted robot requirements or demonstrated performance.  
**Prepared:** 2026-09-30 by Codex from the user-provided [Notion “Specs” page](https://app.notion.com/p/Specs-3ebb26c7416c801aa3acd33e730cba0c).  
**Scope:** preserve the suggested terrain envelopes and translate them into reproducible simulation, training and evaluation work. No terrain generator, training run or hardware validation is implemented by this document.

The Notion page calls its representative terrain values **synthesized engineering design envelopes**, not measured averages for entire biomes. Its source references motivate the terrain description; they do not independently establish every numerical row below. The curriculum, implementation conventions and acceptance process in this document are proposals derived from that source, clearly separated from the source values.

## Suggested robot specifications

The source proposes moving-payload ratios relative to unloaded robot mass, including battery and permanent hardware:

| Suggested level | Payload / unloaded mass | Example payload for a 20 kg robot | Total loaded mass in that example |
| --- | --- | --- | --- |
| Initial validation | 0.50 kg/kg | 10 kg | 30 kg |
| Main design target | 0.75 kg/kg | 15 kg | 35 kg |
| Stretch | 1.00 kg/kg | 20 kg | 40 kg |

These are discussion targets, not accepted requirements. The 20 kg mass is an illustrative design basis, not a measured CAMEL mass. Payload testing must specify terrain, speed, duration and payload placement/centre of mass; supporting a stationary load does not establish mobility with that load. Train an unloaded baseline as well as candidate loaded cases, with mechanically feasible mass and inertia.

Flat speed, rough-terrain speed, range/endurance and ingress protection still need CAMEL targets and test conditions. Manufacturer comparisons on the source page are context, not requirements: maximum speed, laboratory peak speed, single-obstacle height and continuous stair capability are distinct tests. The source also identifies impulse tolerance and terrain-excitation frequency as gaps.

The proposed distance / (Wh × kg) metric in Notion is unresolved. Record distance, energy and the mass basis separately first. For comparisons, proposed alternatives are energy per distance (Wh/m) and electrical cost of transport, `E_J / (m_loaded × g × distance_m)`, with a stated battery-energy measurement boundary. Neither removes the need to specify terrain, speed and payload. Mechanical actuator work is not automatically battery consumption.

## Source terrain vector and units

The source groups terrain into six selectors:

`T = [grade, cross-slope, (RMS, wavelength), (obstacle height, spacing), corridor width, surface class]`

| Selector | Meaning | Training representation / missing detail |
| --- | --- | --- |
| Grade | Longitudinal slope | Explicit signed percent slope; test both uphill and downhill |
| Cross-slope | Lateral slope | Explicit signed percent slope; test left and right lean |
| Roughness | RMS vertical variation and characteristic wavelength | Metres; wavelength is **not numerically specified** in the source table |
| Obstacles | Heights plus spacing; roots, rocks, logs and ledges | Metres; shape, width, orientation and spacing convention also needed |
| Corridor | Minimum clear width | Metres; account for the robot's swept envelope while turning |
| Surface | Hard, loose, soft or mixed | A label linked to a separately calibrated physical model, not a friction coefficient |

Source classes: hard = pavement/rock/compact dirt; loose = gravel/scree/sand; soft = mud/muskeg/snow; mixed = natural combinations. Rut depth, gap width, water depth and snow depth are optional later additions. Model vegetation as obstacle geometry or confinement where appropriate; temperature is a separate environmental requirement.

**Do not mix percent grade and degrees.** For grade `p`, `angle_deg = atan(p / 100) × 180 / pi`. Examples: 25% ≈ 14.04°, 35% ≈ 19.29°, while 30° ≈ 57.74%. Dune slopes in the source are in degrees; most other rows use percent. Convert lengths from mm to m at the configuration boundary. Store explicit units rather than an ambiguous field named `slope`.

## Representative terrain specifications from Notion

The following preserves all 11 archetypes and their qualifiers. `~` means approximate; `+` means the cited upper example is open-ended, not an approved maximum. Qualitative entries remain qualitative. None of these ranges guarantees robot traversability or defines a sampling distribution.

| Terrain archetype | Grade | Cross-slope | Roughness | Obstacles | Clear corridor | Surface |
| --- | --- | --- | --- | --- | --- | --- |
| Improved road | 0–7% | <5% | 2–10 mm RMS | <25 mm, rare | >3 m | Hard |
| Gravel / service road | 0–15% | <8% | 8–30 mm RMS | 25–75 mm, sparse | >2 m | Hard / loose |
| Maintained natural trail | 5–15% | <10% | 25–80 mm RMS | 50–150 mm, ~2–5 m spacing | ~1.2–2 m | Mixed |
| Primitive trail | 10–25% | <15% | 40–120 mm RMS | 100–300 mm, ~1–3 m spacing | ~0.8–1.5 m | Mixed |
| Canadian Shield / boreal rough trail | Up to ~25% | Up to ~20% | ~70–120 mm RMS | 150–300 mm roots/rock | ~0.8–1.5 m | Hard / mixed |
| Wet forest / Amazon-style | ~10–20% | ~10–15% | ~50–100 mm RMS | 150–300 mm roots/logs | ~0.6–1.2 m | Soft / mixed |
| Grassland / open field | ~0–15% | ~0–10% | ~20–80 mm RMS | 50–200 mm, sparse | Open | Mixed |
| Sand / dunes | ~5–15° normal; ~30° slip face | Low–moderate | Low small-scale roughness | Usually small | Open | Loose |
| Tundra / muskeg | Usually low | Usually low | ~30–100 mm RMS | 100–300 mm hummocks | Open | Soft |
| Alpine / scree | ~10–30%+ | ~10–25% | ~80–150+ mm RMS | 200–400+ mm, dense | ~0.5–1.5 m | Loose / rock |
| Talus / boulder field | ~10–30%+ | ~15–30% | ~100–250+ mm RMS | 200–600+ mm, dense | Variable | Hard / loose |

**Still unspecified:** wavelength in every row; quantitative obstacle spacing except maintained and primitive trails; numerical definitions for rare/sparse/dense, open/variable, low/moderate/small; grade-segment length; route length; terrain directionality; and surface-model parameters. Do not silently replace missing values with zero or turn `30%+` into a bounded 30% maximum. Resolve finite implementation ranges and record their approval/assumption status before sampling.

The source emphasizes narrow rough trails, forest roots/deadfall, irregular cross-slopes, scree, boulders, and diagonal ruts as useful challenging scenarios. Its comments about how well those terrains are served are discussion context, not a market survey verified here.

## Normalize difficulty to the actual robot

Report the source's dimensionless descriptors alongside absolute geometry:

| Descriptor | Formula | Interpretation |
| --- | --- | --- |
| Obstacle ratio | `h_obstacle / wheel_diameter` | Step/root size relative to wheel |
| Roughness ratio | `RMS / wheel_diameter` | Continuous disturbance scale |
| Clearance ratio | `h_obstacle / clearance` | Potential interference / high-centering challenge |
| Corridor ratio | `robot_width / corridor_width` | Straight-path fit; turning needs a swept-envelope check |
| Breakover proxy | `clearance / wheelbase` | Geometry descriptor, not an exact breakover angle |
| Stability proxy | `track_width / CG_height` | Geometry descriptor, not a dynamic rollover guarantee |

Use the loaded robot's geometry and centre of mass at the stated suspension posture. Wheel size, wheelbase, track, clearance, payload location and suspension limits are not frozen. Screen scenarios for geometric feasibility before calling failures controller deficiencies; 300 mm obstacles may demand very different behavior at different robot scales. Keep deliberately infeasible stress cases separately labelled, and report any rejected samples.

## Proposed terrain implementation conventions

1. **Separate slope, continuous roughness and discrete obstacles.** Define a base grade/cross-slope surface, add a controlled roughness field, then place roots/rocks/steps. As a proposed convention, report background RMS after subtracting the base surface and mean, excluding separately placed obstacles; also report whole-route geometry. The source does not specify detrending, measurement windows or obstacle inclusion, so record those choices explicitly.
2. **Control spatial scale.** Specify longitudinal/lateral wavelengths or correlation lengths, their definition, grid spacing and sampled area. Measure the realized RMS and spatial scale after generation and after simulator import. Do not generate uncorrelated per-cell noise and assume that matching RMS alone matches the terrain. For a repeated feature with spacing `lambda` crossed at constant speed `v`, `v / lambda` gives a characteristic encounter frequency, not a full vibration spectrum.
3. **Represent obstacle geometry explicitly.** Specify shape, width, orientation, lateral placement, height relative to the local base and edge-to-edge or centre-to-centre spacing. Include left/right offset obstacles and diagonal approaches, not only a symmetric bump under all wheels. Use explicit objects where overhangs, gaps or discontinuous contacts matter.
4. **Check heightfield scaling.** MuJoCo heightfields are elevation matrices; its documented normalization and physical size parameters determine actual horizontal and vertical scale. Verify the imported geometry in metres instead of treating image intensity or the elevation scale as an RMS value. See the [official heightfield reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-hfield).
5. **Keep fidelity labels honest.** A fixed rigid surface with altered friction is a traction proxy, not evidence of sand displacement, mud sinkage, snow compaction or moving scree. Label each case as rigid geometry, traction proxy, or calibrated deformable/moving-ground model. Soft/loose-terrain claims need physical evidence or an appropriate validated model; a surface name alone supplies neither.
6. **Use the intended mechanism.** Existing local educational demos are not a validated CAMEL robot. Preserve the proposed coupled one-actuated-DOF-per-leg mechanism and left/right wheel-pair drive when building the actual model. Do not train against independent actuation that the intended hardware cannot execute.

## Proposed curriculum and test coverage

This ordering is a recommendation for implementation, not a selection of final use case or a claim that the listed difficulty is achievable. Start with feasible geometry, low commanded speed, unloaded mass and conservative actuator bounds. Choose speed ranges and promotion thresholds before training; none is supplied by the Notion terrain table.

| Stage | Candidate scenarios | Purpose and gate |
| --- | --- | --- |
| 0 — baseline | Flat hard ground; improved road | Verify model, commands, contact, tracking, braking and repeatability before learning |
| 1 — isolate effects | Grade-only uphill/downhill, cross-slope-only both signs, isolated step/root, roughness-only, corridor-only | Find failure boundaries without confounding all terrain variables |
| 2 — moderate combinations | Gravel/service road, grassland, maintained trail | Combine feasible roughness, obstacles and slopes; introduce payload and placement variation |
| 3 — intended rough-trail candidates | Primitive and Canadian Shield/boreal trails; narrow paths and diagonal articulation | Test suspension/contact retention and confinement together; include turns and slope transitions |
| 4 — advanced / fidelity-dependent | Wet forest, dunes, tundra/muskeg, alpine/scree and talus | Separate geometry/traction proxies from validated substrate behavior; retain explicit stress-case labels |

Keep simpler cases in the training mixture as difficulty increases. Vary one variable first, then plausible combinations; do not sample every range maximum together and describe that as a typical trail. Define archetype weights, within-envelope distributions, correlations and bounded stress extensions explicitly. Payload levels from the source are candidates only after geometry and actuator checks.

Reserve fixed **training, validation and final-test splits** with distinct terrain seeds/layouts. Use validation for curriculum and policy selection; do not tune on the final test set. Hold out obstacle arrangements and some terrain combinations as well as random seeds. Log both the requested envelope and realized geometry. Compare passive/baseline and active/learned controllers on identical terrain, payload, initial conditions, speed commands and episode limits.

Proposed domain randomization includes calibrated bounds on mass/inertia and payload position, traction, actuator limits/delay, sensor noise and state-estimation delay. These bounds are not supplied by Notion and must be measured or explicitly labelled assumptions. Keep observation inputs compatible with available robot sensing; privileged simulation information must not silently become a hardware-policy dependency.

## Evaluation: report more than training reward

| Outcome | Record per terrain/payload/speed case |
| --- | --- |
| Traversal | Completed route, travelled distance/progress, elapsed time, actual speed and tracking error |
| Failure | Tip-over, stuck/timeout, corridor exit/collision, high-centering, travel/actuator limit violation; retain failed runs |
| Chassis behavior | Roll/pitch, acceleration frame and gravity convention, peak and RMS disturbances |
| Suspension and contact | Leg travel/limit hits, wheel normal loads, unloaded-contact duration and a defined low-speed-safe slip metric |
| Effort | Torque/speed demand, saturation, mechanical work; separate electrical energy only when modelled/measured |
| Repetition | Number of trials, seeds, success fraction with uncertainty, per-case distributions and worst cases |

Define route length, time limit, allowable roll/pitch, required speed, corridor clearance, actuator limits and success-rate threshold **before** evaluation. They are open requirements, not numbers to invent from a manufacturer's top speed. Reward terms may encourage progress/tracking and penalize attitude error, slip, impacts, excess effort and abrupt actions, but reward weights are tunable training choices. Hard failure conditions and independent evaluation metrics remain explicit.

For repeatable physical comparisons, NIST's [stepfield work](https://www.nist.gov/publications/stepfield-pallets-repeatable-terrain-evaluating-robot-mobility) is a useful reference for controlled terrain apparatus. A custom course is not automatically a standards-compliant test.

## Reproducibility and repository ownership

Use one canonical terrain definition across local evaluation and remote training. The proposed locations below describe future implementation, not files already available:

| Repository area | Responsibility |
| --- | --- |
| `shared/interfaces/` | Terrain schema/version, units, unresolved-value rules, compatibility checks |
| `simulation/config/presets/` | Small approved terrain/geometry presets with provenance; robot definitions remain in `assets/` |
| `simulation/` | Generators, MuJoCo adapters and realized-geometry checks |
| `training/configs/` | Curriculum, sampling distributions, payload/speed sweeps and split manifests |
| `deploy/` | Launch the pinned code/config on the chosen GPU backend; no duplicate terrain implementation |
| `docs/benchmarks/` | Selected results, methods, limits and links to retained raw artifacts |

Each run manifest should identify: terrain/preset version and source date; robot/assets and interface revisions; generator version; seed and split; signed grade/cross-slope; target/realized RMS and spatial scale; obstacle shape/placement/spacing; corridor; surface model and calibrated parameters; payload mass/pose; speed command; solver/timestep/backend; policy/baseline revision; episode limits; metrics and failure reason. Record config hashes and code commit. Reject required unresolved fields at execution time rather than silently applying defaults.

A GPU backend must support the chosen terrain/contact representation and produce checked behavior against the local baseline. Sharing preset numbers alone does not establish equivalent physics. Save full outputs outside Git; retain compact manifests and results in dated benchmarks.

## Decisions needed before executable training presets

1. Select the primary mission/terrain subset; the 11 archetypes form a candidate library, not a promise to traverse all of them.
2. Freeze a first robot model with wheels, envelope, clearance, loaded CG, actuator bounds and feasible payload cases.
3. Define roughness spatial scales/measurement procedure, obstacle spacing/shapes, finite corridor and slope ranges, route length and randomization distributions.
4. Choose and calibrate surface-model parameters; decide which soft/loose cases remain labelled proxies.
5. Set commanded speeds, durations, success/failure thresholds, baseline controller and fixed held-out evaluation suite.
6. Choose the GPU backend and verify terrain/contact compatibility before scaling runs.

## Source traceability

- **Primary project source, read 2026-09-30:** [Notion Specs](https://app.notion.com/p/Specs-3ebb26c7416c801aa3acd33e730cba0c), especially “Implications for our platform,” “Terrain / Mobility,” “Representative terrain specifications,” and “Vehicle-relative terrain metrics.” Numeric envelopes above are attributed to this page, not independently measured or rederived from the references below.
- **References cited by Notion, retained for follow-up rather than represented as fully audited here:** [ISO 8608:2016](https://www.iso.org/standard/71202.html), [SAE terrain roughness paper](https://saemobilus.sae.org/papers/terrain-roughness-standards-mobility-ultra-reliability-prediction-2003-01-0218), [Durst et al. DOI](https://doi.org/10.1016/j.jterra.2010.05.004), [ASTM F3218-25](https://store.astm.org/f3218-25.html), and [USFS trail design guide](https://www.fs.usda.gov/eng/pubs/pdfpubs/pdf11232804/pdf11232804dpi100.pdf). Check specific trail class and short-pitch versus sustained grade before using a standard as an acceptance criterion.
- **Environmental context cited by Notion:** [Canadian boreal forest](https://natural-resources.canada.ca/forests-forestry/sustainable-forest-management/boreal-forest), [Canadian climate/wetlands atlas](https://natural-resources.canada.ca/maps-tools-publications/maps/atlas-canada/climate-environment), [NASA Amazon flooding](https://earthobservatory.nasa.gov/images/39359/flooding-near-manaus-brazil), [USGS dunes](https://www.usgs.gov/geology-and-ecology-of-national-parks/geology-great-sand-dunes-national-park), and [USGS tundra](https://data.usgs.gov/usnvc-explorer/unitDetails/1298996). These contextual references do not make the synthesized biome envelopes measured averages.
- **Implementation references checked for this note:** official [MuJoCo heightfield documentation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-hfield) and the [NIST stepfield publication abstract](https://www.nist.gov/publications/stepfield-pallets-repeatable-terrain-evaluating-robot-mobility).

**Update log:** 2026-09-30 — captured the source's 11 terrain envelopes and proposed payload levels; added explicit units, missing-parameter register, curriculum, evaluation and repository handoffs. No team acceptance or performance result recorded.
