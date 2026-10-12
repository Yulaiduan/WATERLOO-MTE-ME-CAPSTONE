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
now uses zero primary damping and keeps the knee controller disabled (2026-10-11 correction). Elastic
balance is neutral; damping does not create a unique static ride height.

The chassis and 28/14 mm guide drums are real massless sensor geometry. Belt
marks and tangent vectors visualize the ideal guide's torque-equivalent tension
difference, not additional solver bearing forces. Optional viewer baseline N/kgf
is saved separately from reference-sheet T₀ and solver config. The earlier
two-stage factory is superseded; its legacy API and validation
history remain documented, but its browser option is retired. Continue from the architecture, mechanism audit and
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
advances preserve state/force history for replay. The wheel model now uses an
undamped upper-link/chassis replacement spring (2026-10-11 correction). Latest scoped
checks are in validation; the unchanged wheel core's full audit was not rerun.

## Cylinder visualization and setting memory, 2026-10-11

The user requested cylinders and cable/end-cap routing instead of an ideal-coil
symbol. `web/spring-transmission.js` renders actual captured coil length and
resolved free length with a constant display scale, plus enlarged top-right
geometry and three illustrative +20mm travel comparisons. Housing and routing
are explanatory geometry only; no solver bodies/contact are added.

`web/form-memory.js` matches control identity, type, options, units/scale and
bounds before restoring values. Wheel controls/views use backend-specific
session memory; Misc snapshots a study before its shared iframe navigates and
restores matching fields after load. Explicit imported profiles/settings win.

The current gravity-balance catalog/factory has damping0 and auxiliary off.
The browser removes constant-lift damping and all extra-tip strut controls;
legacy solver fields and previously recorded runs remain reproducible. Continue
from current validation rather than applying historical damping100 evidence to
this undamped profile.

## Corrected transmission taxonomy, 2026-10-11

Latest user clarification: type1 is a bare inline spring with normal travel;
type2 is a reversing cylinder/piston with rigid rod; type3 is that piston with
rope attached at the external rod end. All pulley mechanisms now use type3 in
current catalog/UI. Non-pulley mechanisms offer type1 or type2. Coil law remains
separate, and rope is tension-only. See the current [preset record](../docs/suspension-presets.md).

`web/spring-transmission.js` no longer draws a housing around type1 or a rope
through the coil in type3. Rod eye and cap move equally with fixed rigid rod
length; cable starts at the exterior eye and goes directly to the existing
joint pulley (latest correction removes the earlier extra idler).
Session imports restore configuration from the config object, then only view
fields/disclosures, so an older remembered dropdown cannot undo route migration.
Legacy API/config IDs remain for reproduction; recorded data is not rewritten.

## One mechanism pulley, 2026-10-11

User correction: do not put an extra pulley on the piston assembly. The main
view now draws cable from the piston rod eye directly to the existing hip/knee
spring-drum tangent and wrap. Generic piston comparison diagrams have no pulley.
The enlarged view explicitly repeats the same named joint pulley with its
configured radius and recorded angle; it is labeled as the same part. No solver
geometry, forces or saved profiles changed in this presentation-only correction.

## Invertible suspension / ground-torque fixture, 2026-10-11

User confirmed: both ropes pull one cap, one taut at a time; ±5° are actual
attachment offsets, and the new design includes two small routing pulleys near
the knee to keep rope feeds linear. The default symmetric bellcrank is at the
knee with its other spring end50mmfromJ1 along the femur. See
[invertible-suspension.md](../docs/invertible-suspension.md).

`invertible_spring.py` calculates external/inner circle tangents, visible direct
paths, circle arcs and shortest admissible routing while rejecting other-idler
intersections. Cap take-up is the greater cable demand, preload uses a mechanical
reference stop, and one spring energy generates the force/torque. Preloaded
bellcrank endpoint force remains nonzero at dead centre while torque is zero.

`inversion.py` is separate from the existing limited-angle/position-driver
bench. Pymunk ground mode has real wheel/chassis contacts, free heave/translation
and held chassis pitch. The independent SciPy and matched Pymunk fixture hold
J1 without floor; direct angles remain regular through90°. Default undamped
100Nm demo pulses flip the −135° start, with rebound/continued motion recorded.
Quarter-ms contact timestep is the current demo; an earlier coarse borderline
pulse failed refinement and is not accepted evidence. New frontend, library,
comparison and native viewer retain their own backend identity/config.

Single-rope presets still have no added piston idler. The two routing pulleys
exist only in the newly requested dual-rope design. Shortest routing omits rope
winding/groove history;3Dself-clearance and whole-vehicle self-righting are not
validated. Latest scoped verification is in the app validation record.

## Central face routing correction, 2026-10-11

User clarified central feeds between the rollers, flaring outward to the knee
face anchors, with no outside rim wrap. Current `central_face` routes use full
moving-cap cable inventory, inner roller tangents/arcs or free central spans.
Finite lead angles give T=Fcap/cos(lead angle); force-site virtual work remains
consistent. Default rollers are ±15 mm, eyes ±2 mm; remembered numbers survive.
The knee pulley is not a circular rope obstacle. Either roller can guide a
rope as its anchor moves. The main diagram, enlarged close-up and native GUI
use the actual computed paths, without a knee-rim arc.

Pre-correction saved profiles resolve to explicit `outer_rim` reproduction;
original records/frames stay intact. Fresh defaults/session editing use current
routing; loading the flip demo selects updated dimensions. Current model and
validation docs supersede the initial outer-route description above.

## Tight rollers and knee-right demo, 2026-10-11

Current demo: 1 mm clear roller gap, ±0.1 mm cap eyes and ±80° angle stops,
starting at |θ|=45°. The knee remains to the right while the wheel moves above
or below the chassis. Pymunk uses a real fifth constraint, not clipped playback;
independent SciPy uses rigid-stop events, inelastic impact loss and inward-load
release. Current default solver iterations are400. Lead alignment and signed
stop torque are recorded; mathematical impact loss has its own energy channel.
The gap stays fixed when editing roller radius. Session migration updates these
requested geometry/pose settings while retaining other dimensions/input values;
older saved profiles/recordings retain explicit unrestricted reproduction.
See the current invertible model and validation records for exact scope.

## Latest clarification: wrap the knee pulley, 2026-10-11

Current central_wrap replaces the no-wrap interpretation: centre-fed cables
flare over the tight rollers, follow common tangents and knee-rim arcs, then
end at the offset attachments. Cable length and force use those contacts;
the cable can lift off when its attachment faces the cylinder. Demo drum30mm,
ideal gap0.2mm and eyes±0.02mm fit the existing coil/mount and keep pull nearly
axial. Editable knee-right ±80° stops and |θ|=45° start remain. Older central_face
and outer_rim profiles/frames stay reproducible. The latest invertible model
and validation record supersede the earlier no-wrap and wider-gap descriptions.

## User-requested rollback,2026-10-11

The user withdrew the unloaded-full-contraction correction. Current mechanics
return to7bbbceb: phi plus/minus5deg attachments, inventory at phi=pi,10mm
preload,120mm rod and signed gravity calibration. Knee-rim wrap,0.2mm gap and
real +/-80deg stops remain. Current folded-session settings migrate back while
retaining unrelated inputs. Contribution history and original saved JSON/frames
are preserved; temporary folded exports are historical and their removed API
field is not accepted for new solver runs on this reverted branch.
