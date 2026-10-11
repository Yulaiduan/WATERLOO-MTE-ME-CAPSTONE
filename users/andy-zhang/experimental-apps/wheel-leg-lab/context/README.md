# Wheel Leg Lab context

Owner: Andy Zhang. Updated: 2026-10-11. Status: experimental, imported against repository base `0b55ff6`. Publication and current revision are discoverable with `git log` at repository root.

## Playback and setup previews, 2026-10-11

`web/app.js` caches recording bounds/input samples and updates the existing
Plotly cursor SVG plus its layout coordinates without per-frame relayout calls.
The pinned Plotly 3.1.0 shape/axis mapping is covered by zoom/scrub/export tests;
rerun those checks before upgrading Plotly. Recorded time still follows the
animation clock, data stays full resolution, and readouts are exact on pause.
Inactive wheel tabs pause their playback.

`setup_preview.py` and `/api/setup-preview` reuse the wheel builder but never
call Space.step. Separate preview state renders architecture/geometry edits
before Run without invented loads or a saved run. Pending preview requests are
cancelled/superseded, including when Run completes; returning to the previous
recording preserves unsimulated edits. See latest [validation](../docs/validation.md).


## Sources and scope

The user authorized content from both **Create a rough animation** and **Optimize wheel-to-link ratio**. This folder contains curated engineering findings and app source, not private transcripts, account exports or partner materials. The [handoff](../docs/handoff.md) records the full scope and current limitations.

The rough-animation chat progressed from a grounded equal-link 2:1 guide to an independent coaxial wheel drive, tilted and mirrored inversion, two-position reindexing, a fixed 4:1 working-stroke approximation, and a mathematical path family. The latest constraint **prohibits reindexing the hip pulley**. Therefore the reindexing demo is retained as a historical alternative, not the selected fixed-pulley proposal.

The ratio chat corrected tangential-force projection versus total vertical support, separated static torque from effective suspension stiffness/damping, built the spring/damper Pymunk bench and GUI, added pulse/step visualization and N/kgf readouts, and cross-checked the user's wheel-radius/belt equations. It confirms a 200 mm wheel radius for the fixture and a 50 mm lower-link extension; the broader radius study is 150–250 mm. Required travel equal to radius remains a sizing assumption.

## Latest correction: position input

On 2026-10-10 the user clarified that the excitation is a position step. Pymunk now defaults to prescribed wheel-hub height with a floating chassis (pitch fixed, heave free); spring-dependent chassis motion and driver reaction are outputs. The editable 30 mm / 250 ms smooth-rise values are illustrative. Recorded step/square previews have been regenerated; force/torque inputs remain explicitly labeled legacy diagnostics. This correction applies to the Pymunk bench, not the separate JavaScript control model.

## Coordinate boundary

Rough-path displays use positive y down and angles from downward vertical. Detailed mechanics use world y up with fold q from downward vertical. Pymunk uses world y up with θ from horizontal and knee opening 2θ. Screenshot y/z correspond to engine x/y; screenshot q is a moment sign, T₀ is belt tension and β is a belt-span angle. Use the [model](../docs/model.md) and [glossary](../GLOSSARY.md), not identical variable names, to map between these contexts.

## Actual verification and open work

The unified app uses app-local Python/Node dependencies. Current and historical numerical, browser, native-window and restart evidence is retained in [validation](../docs/validation.md); the [mechanism audit](../docs/mechanism-audit.md) owns the curated passive demo settings. MATLAB comparisons apply only to the original captured/direct Hooke tip spring. Canonical robot physics is not applicable to this member toolkit; the shared manifest remains unchanged.

Continue by confirming pulley radii and T₀ value/role, actuator hardware, spring preload/characterization, clearance through inversion and real wheel contact. Do not treat derived torque agreement or a collision-free drawing as hardware validation. The immutable assumptions and decisions are summarized in [decisions](../docs/decisions.md); accepted shared requirements remain in the existing repository records.

## Unified Motion Lab, 2026-10-10

The shared browser menu now separates independent mathematical simulation,
2D Pymunk physics and miscellaneous motion studies, with dark mode, Plotly
charts and a profile/data browser. Use Start Motion Lab.cmd at port 4186;
familiar browser launchers are aliases and the native debugger is preserved
separately. Full workflow, JSON contracts, MATLAB/SciPy agreement and current
verification are in the [unified workspace record](../docs/unified-motion-lab.md).

## Spring sketches and live GUI clarification, 2026-10-10

The current catalog retains the original spring and adds hip/knee pulley,
direct scissor, hip/knee bellcrank, direct-to-chassis and internal knee capture
mechanisms. Their [editable dimensions and laws](../docs/suspension-presets.md)
are experimental interpretations of the sketches. Compression, extension and
bilateral captured coil laws remain separate from direct/pullrod/ideal-rope
transmission. Pull-through input span growth compresses the coil; wrap or mount
direction determines the corresponding leg motion. Ideal rope has zero stretch,
100% efficiency and tension-only loading.

The browser GUI button now launches a live native Pygame/Pymunk window on the
simulation host desktop, stepping a newly built Space with the chosen profile.
Recorded browser engine playback remains explicitly separate and can be used
from a remote browser. Python/SciPy supports the spring catalog; MATLAB supports
only the original `legacy_tip` captured/direct combination. New Pymunk presets
apply actual point forces explicitly each timestep, including the original tip
spring. The original native DampedSpring is now an explicit `native_legacy`
diagnostic because its constraint/spring splitting can bias the response.

## Constant-lift lever and wheel adaptation, 2026-10-10

The user requested both the exact reference lever and a wheel-leg preset.
The standalone [constant-lift study](../docs/constant-lift.md) is available in
Miscellaneous studies only and directly at `/counterbalance/`; it
has independent math/free dynamics, actual Pymunk angle/free runs, profile/run
JSON, data-library records and a model-specific live native GUI.

The ninth suspension preset, `gravity_balance`, attaches an upper-link point
to a downward vertical chassis mount. Zero-effective-span tension gives
constant generalized chassis support, with distributed link weight included.
Auto balance calibrates spring rate explicitly while retaining positive
physical coil free length. Ordinary Hooke preload remains a separate method.
Offset mounts or a finite effective free length break exact constant lift;
neutral gravity compensation alone provides no restoring ride-height stiffness.
The [retained reference sketch](../references/constant-lift-lever.png) and
derived equations describe an ideal study, not confirmed hardware packaging.
Historical constant-lift release evidence (2026-10-10): the combined 82 Python/33
JavaScript checks, real-backend browser workflows,
four live native model cases and durable launcher lifecycle pass. Complete
evidence and numerical limits are recorded in [validation](../docs/validation.md).

## Latest replacement correction, 2026-10-10

The user clarified that constant lift **replaces the original spring**: one unit
runs from upper r1 to the chassis massblock rigidly mounted at J1. The current
[architecture](../docs/suspension-architecture.md) disables the auxiliary strut,
uses primary damping 100 N s/m and keeps the knee controller disabled. Elastic
balance is neutral; damping does not create a unique static ride height.

The chassis and 28/14 mm guide drums are real massless sensor geometry. Belt
marks and tangent vectors visualize the ideal guide's torque-equivalent tension
difference, not additional solver bearing forces. Optional viewer baseline N/kgf
is saved separately from reference-sheet T₀ and solver config. The earlier
two-stage factory is superseded; its explicit optional variant and validation
history remain documented. Continue from the architecture, mechanism audit and
latest validation, not an older release's test count.

## Comparison and free single-link interaction, 2026-10-10

Math now contains only 2D SciPy wheel suspension. The standalone lever lives in
Miscellaneous; detailed linkage is archived there with source/direct route
preserved. Old Math deep links translate to the corresponding Misc entry.
The top-level [Comparison workspace](../docs/comparison-workspace.md) accepts
multiple runs or explicitly runs saved profiles, adds searched channels to the
active plot and supports independent trace visibility/splits and signed deltas.

The standalone default is free, undamped and uncontrolled. Up/Down applies
vertical end force; release leaves angular velocity intact. Place at rest is
an explicit zero-speed reset, not a holding controller. Live stateless SciPy
advances preserve state/force history for replay. The wheel model remains the
upper-link/chassis replacement spring with damping 100 N s/m. Latest scoped
checks are in validation; the unchanged wheel core's full audit was not rerun.
