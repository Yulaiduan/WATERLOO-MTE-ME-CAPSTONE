# Terrain Workbench architecture

## Entries and modules

`workbench/index.html` loads `src/workbench/main.js` and `style.css`. `main.js` manages controls, scenario state, plot selection, exports and worker requests. `charts.js` renders engineering plots. `terrain.js` owns profile generation/import, evidence and numerical terrain statistics. `engine.js` owns linkage and reduced dynamics. `worker.js` isolates calculation from interaction.

- `buildTerrain(config)` returns `{samples, summary, metadata}`. Each sample contains `x`, `z`, `baseline`, `roughness`, and `obstacle` in metres, with layers summing to `z`. Modes are periodic, seeded stochastic, Class 3 slope cycle, and imported replay. `parseTerrainCsv(text)` validates metres, increasing distances and complete layer sets; `serializeTerrainCsv(terrain)` exports all samples. For measured/imported data without resolved components, CSV omits component columns so unknown roughness remains unknown after reimport. Export the companion JSON to preserve full source metadata.
- `linkageAtAngle(angleRad, mechanism)` returns equal-link kinematics, Jacobian and usable-range status. `simulateScenario(terrain, scenario, mechanism, actuator)` returns ideal and limited passes plus conventions, assumptions and unknown fields. Each pass includes histories, summary, simultaneous operating points, route-completion status and first-failure location.
- `serializeResultsCsv(result)` exports both passes at recorded output cadence. `fullHistory` means the complete recorded history, not every solver step. Plot histories are reduced with selected extrema; scalar summaries and torque–speed bins are computed at solver cadence.
- Worker request is `{id, terrain, scenario, mechanism, actuator}`; response is `{id, result}` or `{id, error}`. The UI correlates each response with its request.

The data path is:

```text
Source record / imported profile → terrain layers → spatial profile
Geometry + spring + mass → linkage and static support
Spatial profile + speed → time input → reduced dynamics
Dynamics → joint histories → actuator demand / candidate checks
Case + evidence + histories → plots, summary and export
```

The worker is created through an ES module URL so Vite can emit its production asset. Saved/exported cases must include inputs and evidence, allowing the numerical result to be reproduced without reading visual controls.

## Terrain evidence and units

Runtime calculation uses SI units: metres, seconds, kilograms, newtons, newton-metres and radians. UI conversions such as mm, degrees, percent grade and rpm must be explicit. Terrain CSV elevation is height versus horizontal distance in metres. Grade percent is `100 dz/dx`; it is not degrees.

The original evidence package remains in `data/terrain/`. The USGS example is a 1,001-sample 1 km northward line in Shenandoah, Virginia, derived from the VA_Shenandoah_2014 1 m bare-earth DEM in NAVD 88. It is neither a surveyed trail nor a biome calibration. USFS Class 3 values are historical design guidelines; cycle pitch length and spacing remain chosen assumptions. Terrain archetypes and the periodic defaults are synthesized engineering envelopes.

Separate macro elevation, roughness and obstacles. A periodic sine has peak amplitude `sqrt(2) × RMS`; at speed `v`, its excitation frequency is `v / wavelength`. Repeated grade patterns accumulate elevation rather than resetting height at block boundaries. Every export must retain provenance and added assumptions.

## Model interpretation

This is a V1 vertically guided two-mass model. Equal links satisfy `ell = 2L cos(q)` and `J = -2L sin(q)`. Fold `q` is measured from downward vertical: upper `+q`, lower `−q`, relative knee `−2q`. Wheel-coordinate active force maps to output-shaft torque as `tau = force × J`. A preloaded equivalent linear spring supports the chosen sprung mass. Active actuator torque excludes passive spring/damper support; total joint torque includes it.

Prescribed forward speed maps distance to time. The tire supplies unilateral compliant normal force, clamped at zero and with no damping force across a geometric gap. Passive, active damping and body isolation modes are available. Body reference follows macro baseline; an import without fine layers assigns the entire elevation to that baseline and explicitly leaves roughness unknown. Ideal demand is unconstrained; the hardware-limited pass applies a chosen linear torque–speed envelope, response lag and slew limit. Envelope saturation duration and response/lag-limited duration are reported separately: saturation means demand or lag state exceeds instantaneous torque–speed capacity; response-limited means target tracking mismatch exceeds 2% or 0.01 N·m. RK4 timestep is bounded by tire natural period, terrain sample traversal and actuator response. Runs stop for unreachable/singular geometry or travel bounds and retain their first failure location. RMS and load-duration figures describe only the simulated portion.

Excluded: propulsion/traction, chassis pitch/roll, skid steering, wheel-radius obstacle filtering, credible step climbing, link mass distribution and rotational inertia, reflected rotor inertia, belt/pin reactions and coaxial drive/fold interaction. Wheel radius affects plotted axle height; it does not establish obstacle filtering. Current, voltage, electrical loss, thermal capacity, battery energy and regeneration remain unknown. The generic actuator values are chosen assumptions, not manufacturer specifications. A completed numerical route is not hardware approval and no approved body-acceleration/contact acceptance limits are supplied.

The original [development plan](../terrain-simulation-development-plan.md) remains the staged roadmap, rather than a claim that every proposed feature is implemented.
