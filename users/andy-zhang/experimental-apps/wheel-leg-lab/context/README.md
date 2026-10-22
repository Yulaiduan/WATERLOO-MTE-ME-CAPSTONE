# Wheel Leg Lab context

## VSL source relocation — 2026-10-21

Jonathan renamed leg-solver to vsl-solver and placed each version in its own
folder. Active source readers and links now use those versioned paths; V1–V3
HTML hashes and this app’s numerical evidence are unchanged. Motion Lab’s V4
adapter serves the required library-model asset and suppresses the standalone
Excel panel inside its iframe; use Jonathan’s root launcher for XLSX sync.
Only path/resource parity is checked in this migration; the complete Motion Lab
GUI/native simulation suite was not rerun.


## Suspension sizing and V4 integration, 2026-10-19

Read [the sizing record](../docs/actuator-sizing.md). New main tabs `sizing` and
`vsl` use the original port4186 launcher. Basic constant-lift analytical loads,
54 motor/listing combinations and mass/link contours use a verified Google Sheets
readback. CSV refresh is explicit; there is no cloud credential or live sync.
V4 is served from Jonathan's unchanged source with a theme/transfer bridge;
its source hash, parameters, units and quasi-static hip sweep enter the browser
library and sizing overlay. Keep V4 fixed-A/prescribed loads separate from the
basic heaving-chassis model; no unvalidated motor/thermal or canonical physics
claim. The user authorized ignoring the missing Jon AGENTS.md for this task
and requested the linked housekeeping note in his app context.


Owner: Andy Zhang. Updated: 2026-10-14. Status: experimental, imported against repository base `0b55ff6`. Publication and current revision are discoverable with `git log` at repository root.

## Merged original suspension tooling, 2026-10-14

The owner corrected the c8b3c8b separate-editor integration: extend the original
Math and 2D Physics solvers with Jon's features and validate against his source.
The [merged model](../docs/merged-linkage.md) now owns general link lengths,
three carrier belts, phases/mounting, masses/inertia, loads and source statics.
The original UI, spring presets, position input, SciPy/Pymunk APIs, saved profiles,
comparison and native viewer remain the foundation; original geometry is default.
Jon's three math scripts are bundled verbatim as hashed reference functions,
without his editor. The dynamic generalized fixture is independent of the fixed-A
reference FBDs, preloads and holding loads; source zero masses are not fabricated
into dynamic bodies. Read current validation before interpreting numerical claims.
Continue with the original port4186 Start Motion Lab.cmd and select editable
Geometry in either original bench. Keep rejected dual-rope inversion status,
separate offline reports/examples and canonical engineering records intact.

## Separate offline design report, 2026-10-14

Jonathan/Andy generalized design work continues in
[leg-design-study](../../leg-design-study/context.md), with static HTML/PDF,
selected evidence, reproducible math/physics checks and a revision map. The
owner explicitly requested that the new report not enter Motion Lab tooling;
the initial unpublished study/menu/API integration was removed. Existing sizing
controls, solvers, profiles and the dual-rope IMPOSSIBLE status are preserved.

## Link sizing / torque sweep, 2026-10-12

The sizing display now uses theta upward from wheel-centre horizontal (0° flat,
90° upright), with per-pose horizontal rays and angle arcs. Individual torque
curves compare each length's best window, top 30 profiles or objective winners;
clicking a curve selects it. The new lift/RMS score ranks usable travel per
torque demand, with ideal work and actuator ROM shown separately. The 2:1 guide
makes relative knee motion twice hip motion, so direct hip actuator torque is
twice relative-knee torque; fixed guide reactions are a different quantity.
Internal q, existing conversions/config JSON, position input and rejected
dual-rope status are preserved. See [link sizing](../docs/link-sizing.md) and
[validation](../docs/validation.md) for formulas, metric limitations and checks.

Actual Windows laptop reconstruction from `c6a79b5` is now verified with installed
Python 3.13.12 and Node 22.23.3 / npm 10.9.9. Setup Motion Lab.cmd rebuilt its
own dependencies/assets; the real app-root Start/Stop Motion Lab.cmd pass
start, scoped stop, restart and reuse at 4186. See the
[laptop setup record](../../laptop-handoff.md#actual-laptop-setup-2026-10-12) and
[validation](../docs/validation.md) for actual checks and limitations. Continue
from the sizing state below; no mechanics or stored model decisions changed.

The force calculator at /force-plots/ now includes [link sizing](../docs/link-sizing.md).
It starts with the existing 200mm radius (400mm diameter), nominal200mm lift,
editable demo20mm start/end reserves and air gap,200mm chassis depth and100N
constant net load. Diameter/radius are distinct synchronized inputs. Custom ROM
and both buffers convert degrees/mm at a reference link; units stay fixed while
sweeping. Internal fold q is from downward vertical; displayed theta=90deg−q.
Peak/mean/CV objectives are separate, averages explicitly use uniform travel or
angle, and torque can be hip-equivalent or half-sized relative-knee. No actual
spring law/preload/assistance or dynamic optimization is inferred. Original force
animation/math and solvers are preserved; new config JSON is calculator-specific.
Actual analytical/browser and launcher checks are recorded in validation. Continue
by supplying real net-load, chassis/spring and speed/strength inputs before using
the sampled winners as hardware decisions. Start Motion Lab.cmd remains canonical.

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

## Design status — IMPOSSIBLE,2026-10-12

The user marked the invertible **dual-rope knee-pulley design** as impossible
and requested this label on2026-10-12. It is a rejected physical design,
retained as a historical idealized simulator and source reference. Previous
numerical runs establish behavior inside that ideal model, not buildability.
No physical failure explanation or impossibility proof was supplied with the
status decision; none is invented here. The symmetric knee bellcrank and the
ordinary2:1guide are separate designs and do not inherit this label.
Original code, profiles, records, equations and prior validation remain available.

## Owner-requested labelled examples and GIFs, 2026-10-14

After the offline report at `12e227c`, the owner requested labelled examples in
Motion Lab and animated GIFs. This explicitly authorizes the visualization
entry, while the design report/calculations stay in the separate sibling app.
[The new record](../docs/design-examples.md) lists five exact report cases,
working/full-inversion views, angle/scale conventions, ten GIFs, original-V2
parity and actual browser/launcher checks. The cases are read-only kinematics;
no spring/motor model or historical saved profile is migrated. The global native
GUI action explains its supported-fixture boundary instead of showing an
unrelated old wheel model. Continue from the source report for numerical design
choices, and retain projected-clearance limitations and historical IMPOSSIBLE.
