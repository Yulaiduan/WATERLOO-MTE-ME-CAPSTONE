# Kinefold context

Andy Zhang with Codex, 2026-10-22. Started from main `5e52a12`.
Experimental app; no canonical robot or hardware acceptance.

The user requested a separately named future combined motion/terrain/VSL tool,
starting with mechanism builder tab 1 and a conventions tab. The initial two workspaces are now joined by static and quarter-model dynamic
solver tabs, as requested later on the same date. Follow Motion Lab's app-owned
sage/cream shell; terrain remains outside the implemented scope.

Reference source: Jonathan's `vsl-solver/v4/v4-pulley.html`; retained solver,
statics and finite-idler spring blocks are unchanged and hashed in reference.json.
Kinefold's adapter maps source [y,z] to new [-y,0,z], equivalently x=-source_y,
z=source_z, and old +x to new +y. The left-side camera now places +x left and +z up, with +y toward the viewer;
positive +y torque and source-positive rotations appear counterclockwise.
This supersedes the initial x-right preview; physical coordinates, scalar
torque signs and saved designs retain their meanings.
β patch direction is from down toward forward: P-C = rw[sinβ,0,-cosβ].
Positive Ft points backward at β=0 and gives positive wheel τ_y.

V4's default 8.75kg/300mm/200mm-wheel baseline uses its linear coil and exact
finite-idler cable path. An explicitly selected ideal constant-force option
uses k=0 at the entered p0. The stored coil rate survives switching laws.
Weight-reference load follows all five masses; global/contact modes preserve
prescribed force values independently. Fixed-A masses and loads are static;
animation simply prescribes θ2. Remote spring housing is schematic.

No source-app comparison is presented in the product. Motion Lab's V4 iframe
serves Jon's original blocks (see its actuator-sizing record); its separate
SciPy/Pymunk suspension models instead move the chassis and include dynamics.
The owner requested that distinction as a chat answer, not as new tool content.

Validation: `node verify.cjs` passes 2,000 assertions: retained-source parity
(after LF normalization), varied unequal-link geometry, applied world forces,
right-hand-rule moments, FBD/virtual-work balance, both spring laws, energy
finite differences and rejected invalid/unknown JSON. Geometry error is zero;
maximum cable-energy derivative error is 1.74e-9 Nm. Initial harness path/EOL
assumptions failed and were corrected; no physical tolerance was relaxed.
Browser checks verify live length edits, side/isometric/layer controls, constant
force at 160 degrees, mass10kg -> Fz98.1N, global/contact conversion, invalid
idler errors, blank pose handling, playback, dictionary search, independent
section collapse, actual JSON download/import and reload persistence. Browser
warning/error logs are empty. The current desktop viewport was visually checked;
mobile/hardware/full source-app dynamic suites were not run.
Actual app-root launcher started from unrelated working directories, reused its
running instance, stopped only its authenticated service and restarted at the
same URL. All served assets return HTTP200; Python compilation and repository
structure/log/workspace gate checks are performed in final validation.
Canonical physics is NOT APPLICABLE to this isolated member experiment.
Restart: project-local Start Kinefold.cmd; stop with Stop Kinefold.cmd.
URL: http://127.0.0.1:4191/. Python standard library; no package setup.

## X-left preview correction — 2026-10-22

The user requested the entire mechanism preview to face +x left, with +z up.
Both side and oblique projections now flip horizontally, including links,
wheel, spring route, travel, load arrows and dimension geometry; text remains
readable. The left-side camera looks along -y, so +y points toward the viewer
and positive +y moments appear counterclockwise. The overview illustration,
torque arrow, axis markers and dictionary agree with this right-handed frame.
This also corrects the earlier verbal claim that +y would point into the screen.

The 2,000 existing numerical assertions still pass; source geometry/forces and
saved parameter meanings are unchanged. Live browser inspection confirms the
mirrored mechanism and counterclockwise torque illustration; current baseline
readouts remain 435.6mm travel, 570.5N cable force and -442.4mm wheel-centre z.

Final staged checks exposed CRLF-as-whitespace in the new launchers and a Git
hook resolving python3 to the Windows Store alias. The launcher files now use
LF and are rechecked through actual start/stop/restart; hooks use the existing
CAMEL_PYTHON override pointing to installed Python for the publication command.
No hook code, global interpreter setting or shared policy is changed.

## Mechanism inspection and geometrical preview — 2026-10-22

The user requested a UI reassessment against the original two-tab brief, then
specifically asked for geometrically correct previews, a grid, belt rotation
indicators and wheel/pulley index axes. Tab1 remains a mechanism builder and
Tab2 remains conventions; +x left/+z up and +y toward the side-view observer
are preserved. No solver chart, terrain run or optimizer is added.

The preview now uses its actual viewport, readable labels, calibrated mm grid,
Mechanism/Full travel/Spring detail framing, zoom, panning and exact index axes
for all six pulleys plus the wheel. Independent belt material markers use the
carrier-relative angular displacement and exact common-tangent perimeter.
The default wheel stays level because K=0. Pulleys/indices remain visible when
belts are hidden. The isometric camera uses orthogonal equal-length projection
rows; the illustrative wheel width was removed. The remote coil housing alone
remains explicitly schematic; length/radius/tangent geometry shares one scale.

Inputs have direct ? links to their definitions, the parameter column scrolls
independently and its group shortcuts keep the preview in view. Tab2 has top
search, section shortcuts, 81 individually explained variable entries and an
actual baseline topology drawing. Search handles theta2 and Unicode subscripts.

Verification: existing 2000 model checks plus1123 drawing checks pass. Independent
finite-difference velocities on both wraps of all3 belt stages agree with their
pulley surface velocities to1.75e-7mm/rad; index radii and perpendicular axes
are exact within numerical tolerance. Actual rendered side-view femur/wheel
and tibia/wheel radius ratios are1.500008; wheel/grid spacing is2.000025 for the
300mm links/200mm wheel/100mm grid (SVG coordinates round to0.001px). Browser
checks confirm seven axes,32 baseline material dots, pose-dependent belt travel,
zero baseline wheel index rotation, zoom, exact40/30px pan, independent layers,
parameter shortcuts and linked reference search. Browser warning/error logs are
empty. Mobile, hardware and full dynamic source-app suites are not run.
The app server was restarted after adding the new allowlisted browser module.

## Static and quarter-model dynamic tabs — 2026-10-22

The user's new request expands the earlier two-tab scope to five tabs: builder,
conventions, V4 static solver, analytical dynamics and2D Pymunk dynamics.
Static results use the live builder parameters and existing V4 core, including
spring law and load convention; 181 samples provide a labelled sampled peak.
Both dynamic tabs embed actual Motion Lab engines with persistent quarter-model
scope indicators and independent-input/coordinate notices. They do not silently
map the V4 finite-idler architecture into Motion Lab's different dynamic fixtures.
The tab navigation, keyboard order and direct query URLs cover all five entries.

The same-origin-only POST /__kinefold_solvers lazily calls the sibling durable
NoBrowser launcher, verifies app identity/root at4186, and returns readable
startup errors. Shared Motion Lab remains alive when Kinefold stops; its own
Stop launcher controls that service. Existing setup dependencies are unchanged.
Browser verifies static values and connected frames/badges; real one-second
API runs return1000 rows and112 frames from each engine. SciPy warnings are empty;
Pymunk retains its explicit-force timestep-refinement and ideal-rope caveat.
An initial0.05s probe was rejected by existing input validation;1s is accepted.
Existing3123 model/drawing assertions pass. No hardware/canonical physics claim.

## Static import freshness — 2026-10-22

The static workspace now refreshes immediately when a design is imported while
that tab remains selected. The existing V4 core and JSON schema are unchanged.
A real browser file import changed m1 to10kg and theta2 to145deg, immediately
showing Fz98.1N, hip torque -6.014Nm, tension678.474N and sampled peak7.044Nm.
The8.75kg/132.5deg baseline was restored after testing. Browser warnings/errors
were empty and all3123 existing model/drawing assertions passed.
The global footer and opening scope descriptions now reflect the solver tabs.
The user requested GPT-6.1 Sol development agents with the parent handling
architecture and review; that working preference was followed for this finish.

## Unified design profiles and native dynamics — 2026-10-22

This supersedes the independent embedded-bench architecture described above.
The owner asked for all solvers to use the mechanism builder and for a00 Designs
workspace. Static and both native dynamic tabs now use the shared project-v2
mechanism. Both dynamics use one saved runConfig; the Studio bridge emits
monotonic revision/modelRevision snapshots and rejects malformed profile updates.
The analytical/Pymunk output belongs to an exact captured snapshot: physical
edits/load mark old results stale, and late results for another revision are
rejected. JSON run export retains the full project, run settings and engine result;
CSV retains returned rows. Playback uses real returned theta2, with one-scale
x-left/z-up geometry, finite belt loops, spring path and body indices.

The fixed-hip experimental fixture holds A and theta4; theta2 is the moving
coordinate and the builder's prescribed wheel load remains external. No ground
contact, floating chassis or whole-vehicle claim applies. m1 affects the weight
reference but is fixed at A and adds no moving inertia. Moving masses are never
substituted for the original zero-mass static baseline. The explicitly labelled
00 Designs dynamics example supplies illustrative moving masses, while the
inertia panel distinguishes uniform rods/discs, custom inertias and hip rotor.
Static holding-torque and release actions update the saved profile explicitly.

POST /api/dynamics replaces /__kinefold_solvers and no longer starts/requires4186.
It validates origin/header/content/shape/nonfinite JSON and bounded body, serializes
workers, and invokes the app .venv Python dynamics.py --request-stdin with a90s
limit. Builder/static preview needs only standard-library Python; Setup Kinefold.cmd
installs isolated numerical dependencies. Existing4191 Start/Stop launchers remain
canonical; integrated launcher lifecycle checks belong to final validation.

Development used separate worktrees and GPT-6.1 Sol agents under parent architecture
review. Solver UI/server checks so far: node --check solvers.js and conventions.js,
python -m py_compile preview.py, and four request-shape/missing-environment probes
pass. Full combined browser/backend/start-restart evidence is recorded by the
integration agent after all workspaces are assembled. Canonical physics remains
NOT APPLICABLE to this isolated experimental app; hardware is unvalidated.


## Integrated verification — 2026-10-22

The parent reviewed architecture and delegated implementation to GPT-6.1 Sol
workers in isolated worktrees. Integration retains one native project model and
removes all sibling dynamic-service/iframe dependencies. The local app now has
its own pinned SciPy/Pymunk environment and Setup Kinefold.cmd (Python3.12+).
Actual setup/reuse/stop/start from an unrelated working directory passes at4191.

All3123 existing model/drawing assertions,14 project/library scenario groups,
all JS parsing and Python compilation pass. Six Python dynamics tests verify
source-static parity (max2.84e-14Nm), energy derivatives, both-engine equilibrium
(max Pymunk holding drift4.33e-5deg), travel termination, actual rigid frames,
zero-mass validation and timestep refinement. Pymunk maximum angle errors versus
the analytical trajectory decrease0.06897/0.03388/0.01679deg as dt halves from
0.002 to0.001 to0.0005s; work-energy residuals likewise decrease.
Real0.3s native API runs return31 rows/31 frames from each engine. Missing-env
503 and foreign-origin403 errors are explicit. Browser checks cover saved
profiles/reload, shared holding torque, project import on static, duplicate,
rename/delete/undo, both-engine holding runs, release trajectory/scrub/export
and stale-state marking. Native prompt/confirm were unsupported in IAB and are
replaced with accessible in-page dialogs; a fetch failure during deliberate
service lifecycle testing was retried after restart. No hardware/terrain or
canonical robot validation is claimed.

Pymunk belts/indices explicitly reconstruct ideal constraints from returned q;
actual A/B/C linkage positions are overlaid dashed, with sampled pin/angular
residuals displayed next to playback time. Run notes and detailed fixture
assumptions expand on demand; quarter-model scope and run controls stay visible.


## Vertical chassis correction and exact V4 square input — 2026-10-22

The user corrected the dynamics boundary condition: hip/chassis A moves vertically,
with fixed horizontal position/pitch, and no guide rods drawn. This supersedes
all fixed-hip dynamic descriptions above. Builder and equilibrium remain
hip-relative design references; every tab is a native Kinefold surface.

The exact V4 baseline retains m1=8.75kg, all other masses0, both300mm links and
all existing spring parameters. Default profile: floating-chassis,6.5s,150mm
height/plateau/gap,100mm/s,0.5s delay, zero rise/damping/added rotor inertia.
Massless transmission pose can jump at an ideal input edge while chassis h/v
stay continuous. Positive moving inertia or damping requires a declared finite
rise; quintic ramps lie inside the nominal plateau. Weight support is not applied
again as an extra force. Pymunk has a genuine constrained moving chassis body
and exact condensed ideal linkage/inertia; it is not an all-body linkage engine.

Project-v3 and new browser working/library keys migrate v2/v1 without changing
old keys or geometry. Fixed-hip profiles remain archived as legacySolverConfig.
A positive-mass legacy design receives a visibly declared10mm transition; no
mass is substituted.18 state scenarios cover migration, preserved original data,
validation bounds, failed persistence and archived-profile validation. The full
native interface, search dictionary and docs describe the new boundary condition.

The preview uses one fixed camera across all world frames, showing a chassis
mass marker, exact ideal mechanism and prescribed base platen. No rods, collision
terrain or exaggerated heave are shown. Chassis displacement relative to its
initial height has an independent plot axis. Returned duplicate-time jump rows
remain discontinuous in plots/playback. Peak hip speed across a jump is undefined.

Both full default browser/API runs return656rows through6.5s with5exact square
jumps, unchanged baseline masses and duration termination. Chassis range is
about6.47mm; final Pymunk A height643.95mm and q150.67deg match the scrubber.
The six Python groups verify source torque parity2.84e-14Nm, independent heave
acceleration1.14e-13m/s², baseline cross-engine heave difference0.004197mm and
energy residual4.26e-14J/1.67e-6J. Finite-rise trajectory/work-energy errors
halve with dt refinement. Boundaries cap10000 input transitions; analytic output
only rounds range endpoints within1e-10rad, otherwise it fails explicitly.
Launcher reuse/stop/restart from unrelated cwd passes at4191. Parent architecture
and browser review approved the experimental scope; hardware remains unvalidated.

## Dynamic static-limit validation — 2026-10-22

The owner asked to run both floating dynamics as static and compare with Jon's
VSLv4. [The comparison](../static-validation.md) and
[reproducible script](../validate_static.py) use original hash-verified HTML
analytical blocks directly in Node, independently of Python/adapter expectations.
72 matched cases produce144 actual one-second engine rollouts, all duration
termination: baseline, unequal geometry/ratios, masses, alpha, both spring laws,
idler variants and additional loads. Maximum torque error5.69e-14Nm, spring
error3.42e-13N; maximum chassis drift7.96e-13mm analytical and0mm Pymunk.
Baseline132.5deg requires -0.027168833380Nm, Fs570.491044815N and85.8375N support.

Mapping is essential: dynamic support acts vertically atC, while Jon's total
wheel load acts at rimP. Supply Jon totalverticalMg and the same horizontal
load; tauJon-tauFloating=rw*R*sin(beta)*K for supportR=Mg-FzExtra. Baselinebeta0
matches directly; offsetbeta25/Knonzero matches after removing only the support
rim moment. Zero-torque baseline and uncorrected-offset negative controls move
as expected. Support/spring readouts are derived force-law quantities, not
independently measured Pymunk contact reactions; individual belt/pin forces are
not validated. No runtime/UI/profile or source-app changes, no server lifecycle
change; saved150mm square settings remain intact. An import-order harness error
and a mistaken assumption that zero-height inputs emit no scheduled events were
fixed before the clean final check; no numerical tolerance was relaxed.

## Complete native static analytical workspace — 2026-10-22

The current tab order is00 Designs,01 Builder,02 Equilibrium · static,
03 Dynamic analytical,04 Pymunk guided chassis,05 Conventions. Stable tab IDs,
query URLs and variable-help links are unchanged; keyboard End reaches Conventions.
Equilibrium now owns a separate native module; the old solvers.js static renderer
is removed so shared-design/import events cannot overwrite the expanded UI.

[Plot coverage](../equilibrium-plots.md) maps all17 original charts and series:
2 suspension/support,3 kinematics and12 loading plots (four axes × three kinds).
Five native individual-body diagrams and finite-idler spring detail supplement
these charts. Categories and selected sweep axes render lazily; physical-input
and diagnostic-range keys cache rows, while series toggles reuse them. Diagnostic
windows never edit the builder or saved run profile. All points/forces use global
+x left/+z up, couples+y CCW; source d_y maps to−d_x and travel inclinations use
their own atan2 convention. Undefined support/angle/spring data stays null/gapped.

node verify-equilibrium.cjs passes9404 assertions across266 cases against original
hash-verified HTML blocks, all17 manifest entries and8 multibranch travel queries.
node verify-equilibrium-diagrams.cjs passes11757 assertions over45 varied cases:
maximum world force residual5.24e-13N, moment7.11e-14Nm, route arc endpoint1.43e-14mm.
Existing2000 model/1123 drawing assertions and18 project-state groups pass.
Source reference hashes are unchanged. No dynamics engine/profile/schema changes
were needed, so the earlier floating dynamics and static-limit evidence remains
separate. No hardware/canonical-robot validation is claimed.

Start launcher reuse/Stop/restart/reuse from C:/Users/zhang passes at4191;
all four new assets and stable static/conventions URLs returnHTTP200. The same
project-local Start/Stop launchers remain the durable restart path. Browser QA
is performed by the parent architect using CUA, with final evidence below.

Parent CUA review passes six-tab order, Home/End navigation and L2 help links,
all four loading axes (481θ/d_z and181α/β samples), expanded90–270° domain,
linked angle-series toggles, readable spring detail and all5FBDs without clipped
tables. Import while static is active changes all groups to the10kg/high-ratio
145° fixture (τ₂−44.239Nm, spring disabled/support−100%) without changing physical
stops through diagnostic controls. Exported analytical JSON contains17manifest
entries/all four sweep datasets; CSV exports the selected axis/context. Actual
center-travel hover recovers one pose; automated8multiroot queries supply branch
coverage. The exact pre-test portable backup was restored and reloaded at the
user's140.8954° pose with its profile unchanged. Browser console is empty.

Review improved plot/FBD grids to two columns with readable14–15px SVG labels;
small screens use one column. Pointer hover maps screen coordinates through the
actual SVG screen CTM, preserving correct coordinates under letterboxing. Parent
architecture/coverage/UI review approved before repository publication. No new
dynamics runs were needed or claimed for this presentation-only change.

## Matched dynamic workspaces, desktop viewer and disk profiles — 2026-10-22

Both dynamic tabs now use17 matching native plots in lazy Motion/Input,
Kinematics, Forces/Actuation and Energy/Numerics categories. Shared playback
retains simulationtime and exact before/after side between engines. Run both &
compare captures one project/profile once; mechanism hash, fullparams/config and
exact time/eventSide must match. Overlays, Pymunk-minus-analytical sampled max/RMS
errors, overlap/sample counts and early-termination reasons remain available in
both tabs. There is no interpolation across jumps or extrapolation. Diagnostic
rates/reactions break at exact jumps; no dynamic belt/pin-force solve is implied.

The prescribed spatial square moves toward−x/screenright, anchored under current
wheelCx. Requested sharp and applied quintic/exact profiles match backend input
at the wheel, includingdelay and eventside. The fixed world camera preserves
actual heave; floor motion adds no rolling/collision physics. Tiny values use
scientific notation and SVG hover/cursors use actual content coordinates.
[Dynamic analysis](../dynamic-analysis.md) records chart and comparison meaning.

Open desktop Pymunk computes the captured Pymunkcase, then opens a real Tk results-
playback window with actual chassis frames and ideal condensed linkage. Pause,
scrub, replay, worldgrid and movingfloor are native. The bounded same-origin
/api/viewer accepts onlyopen/status/close and a fixed appscript/runtime; it owns
one closable process, which also closes with the server. Nativewindow/readiness,
controls and geometry were actually inspected through the approved desktop UI.

Profiles now persist in profiles/library.json (nameddesigns +exactworkingcopy +
optimisticrevision), with atomic validation and rollback on failure. Migration
keeps originalbrowserkeys and an immutable profiles/browser-backup.json; explicit
recovery copies laterbrowserdata without replacingcurrentdiskstate. Startup is
blocked untilstorageinitialization succeeds. All project/static/dynamic/comparison
exports use the bounded /api/profiles endpoint and write unique files in exports/;
no exportbutton sendsfiles toDownloads. Five knownolderQA downloads were moved
into app.preview/recovered-downloads byparent, unrelatedfiles untouched.

Validation:2788 presentation/comparison assertions include64 independent Python
Model.input probes and actual6.5s baseline engines with656 matched pairs; max
baselineheaveerror0.00419668mm. Existing2000 model/1123drawing assertions and27
project/disk-state groups pass;11 Python profile tests cover atomicfailure,
conflicts, immutablebackup, corruption,6MiBexports, path/size limits andg0.
Nativeisolatedworker GUItest passesall7 cases; mainnon-GUI rerun passes5 with2
GUIcases explicitlyskipped, supplemented byparent actualnativevisual/control QA.
JSparse/Pythoncompile/diffchecks pass. All3foreignOriginAPIs reject403; unsafe
exportpath rejects400. Engineequations/referencehashes remain unchanged.

Actualbrowsermigration preserves2nameddesigns and workingpose140.8954° with full
150/150/150mm@100mm/s,6.5s profile. Diskworking and namedlibrary deep-equal the
originalbrowserbackups aftersaveas/reload/delete/import QA. Eightactualexports
(5JSON/3CSV, including3.027MBcomparison and3.283MBstaticdata) parse insideexports/,
with noKinefoldfiles leftinDownloads. Browsercurrentpose pairhas656samples each,
shared2.48s cursor andcomparisonfield changes pass,17plotcategories/floormotion
play pass, no consoleerrors. Individualexportbuttons arevisiblebesideRunboth.
LauncherStop/start/reuse from unrelatedcwd passes4191 afterbackendintegration;
server remainsrunning. Parentarchitecture/browser/native/diskreview approved
beforepublication; no hardware/collision/fullvehicle validation is claimed.

## Actual terrain contact and freely backdriven wheel — 2026-10-22

The previous section describes the retained prescribed-height benchmark. A new
separate terrain-contact profile uses two actual Pymunk bodies (heaving chassis
and freely rotating circular wheel), a non-sensor wheel shape and moving terrain
polygons. The exact straight massless linkage is represented by a chassis-relative
groove; unsupported curved paths, moving link masses and additional inertias are
explicitly rejected. The analytical benchmark is not a contact solver, so paired
comparison is unavailable for contact mode. See [terrain-contact.md](../terrain-contact.md)
for equations, source anchors, tolerances, fields and limitations.

The user approved an editable 1.5 kg wheel, effective friction0.8, zero bounce
and free drive. The deliberate demo action preserves the original working design
as a named backup and creates a separate complete profile with final V4 geometry:
wheel radius200mm, chassis8.75kg, massless links,150mm step/plateau/gap,
100mm/s and dt0.00025s. Optional contactConfig leaves old project-v3 snapshots
unchanged when omitted. Initial terrain spacing includes circular-rim clearance;
the actual world mesh is shared by browser and desktop playback. No wheel-height
teleport or terrain anchoring to wheelCx occurs. Gap bridging and separation are
physical contact outcomes. Excessive penetration stops a partial result explicitly.

Main validation:8 contact test groups pass; flat normal100.552499227N matches
10.25kg gravity, flat spin28.6478897565deg/s matches100mm/s divided by200mm,
and frictionless spin remains0. Baseline spring570.491044815N and holding hip
torque−0.027168833380Nm remain unchanged. Default6.5s contact finishes with
maximum penetration0.004186895mm; dt refinement reduces heave error and penetration.
An R100/H150 negative control stops at0.51275s rather than tunnelling. Tilted
nonunit-drive/index and spring virtual-work checks pass.666 drawing assertions,
39 dynamic-analysis assertions,29 project groups,12 profile tests,2000 model and
1123 drawing assertions pass. Viewer tests pass8 with3 GUI cases skipped in the
headless suite; a separate actual Tk/Pymunk contact controls/auto-close test passes.
The first/airborne frame uses unavailable-slip text instead of formatting null.
Manual desktop visual inspection was occluded this turn and is not claimed.

Parent browser QA verifies651 contact samples over6.5s, actual spin and moving
mesh, a4.3s gap bridge, disabled analytical/contact comparison, blank-friction
rejection, accurate Designs/conventions copy and no console warnings/errors.
The original two named designs remain deeply equal to the pre-contact snapshot;
four designs now include the exact working backup and separate contact demo.
Current working design equals that demo after reload. Legacy baseline paired
benchmark still returns656 exact pairs with maximum heave error0.00419668mm.
Contact JSON7.44MB and CSV396k parse inside app exports/. Start/Stop/restart/reuse
via project-local launchers from an unrelated cwd passes at4191. Parent final
architecture/browser review approved; final view is paused at4.3s and screenshot
is ignored .preview/contact-gap-bridging-final.png. Source apps, immutable V4
reference and canonical components remain unchanged; no hardware/full-vehicle
validation or all-body linkage contact model is claimed.

## Shared actual-contact engines and case studies — 2026-10-23

This supersedes the prior contact-mode Pymunk-only limitation. Both existing
dynamic tabs now solve the same actual wheel/terrain contact case. Analytical
contact is an independent reduced-coordinate mass-matrix/accumulated-impulse
integrator; it does not import Pymunk. Shared contact_cases.py contains geometry,
material, controller, energy-screening and case-metric laws, not an integrator.
Pymunk retains actual chassis/wheel bodies. The prescribed-height benchmark is
still separate. See [contact-scenarios.md](../contact-scenarios.md) for derivation,
controller/stop semantics, primary sources and numerical evidence.

Optional project-v3 caseConfig preserves old snapshots when omitted and is
included in content/model revision, captured identity, comparison and disk/native
payloads. Both tabs share Terrain stability, Jump and Landing controls. Jump
starts compressed/rest, extends with entered torque and cuts off at extension.
Landing starts at editable default2/3 opening, zero speed and entered bottom gap;
reported spring/external-load compensation holds pose until actual first contact,
then entered or energy-sized limited braking resists compression. Unilateral
inelastic travel stops transfer momentum and record loss; bottom-out before arrest
fails landing. The user supplied editable underside offset50mm below A. Initial
intersection is rejected, threshold strike terminates, and null means unassessed.
No chassis collision shape is invented. The point is marked in browser/native
previews; jump/landing floors are stationary and ignored input/actuation fields
are disabled. Reversed geometric compression branches are explicitly rejected.

Energy displays separate chassis½m₁v², wheel kinetic energy, spring/gravity energy,
motor∫τdθ, contact/stop losses and unresolved numerical ledger residual. Pymunk
impulse-loss accounting includes bias effects; analytical position projection
energy is separate. Neither is presented as tight conservation or peak torque.
Vertical flat-floor energy sizing truncates compression at an earlier underside
threshold; tilted energy sizing/demand is unavailable. Bounded per-engine landing
search uses a coarse scan/local tested bracket, not a globally monotone minimum.
Different engine outcomes get a prominent comparison warning rather than being
hidden by equal observation durations. All exports, including torque assessment,
remain in the app exports/ folder.

Main validation:8 original Pymunk contact groups,9 shared/Pymunk case groups and
11 independent analytical groups pass. Flat normal100.5525N/spin28.6478898deg/s,
frictionless zero spin, held ballistic fall, spring compensation, exact spring-off
100Nm extension work113.44640138J, zero-torque jump negative control, failed
zero-brake bottom-out, successful100Nm arrest, initial overlap/clearance guards,
R100/H1501mm jam termination, sustained bottom-out support and tilted stop momentum
checks pass. Full analytical R2006.5s case has651rows/frames,0.006285mm maximum
preprojection penetration, negligible postprojection and0.003178J final ledger
residual. Independent import check confirms no Pymunk in the analytical process.
Two-second matched201-sample Jump/Landing comparisons refine max heave difference
2.24675→1.38403→1.09242mm and4.85817→1.69714→0.910564mm for dt.0005/.00025/.000125.
Near-boundary200mm energy-sized22.6905Nm landing differs: analytical arrest versus
Pymunk bottom-out at dt.00025; this is retained and requires refinement.

Presentation/persistence checks pass46 comparison assertions,31 project-state
groups,13 profile tests,666 contact-drawing and2000 existing model assertions.
Native regression passes9 with4 GUI tests explicitly skipped, supplemented by
actual Tk/Pymunk jump pause/scrub/replay/auto-close PASS1. Browser native open,
ready/status and close also passes. Start/Stop/restart/reuse through project-local
launchers from unrelated cwd passes4191 after all new assets/API registration.
No canonical robot, hardware, whole-vehicle or tire-compliance validation is claimed.


Final parent architecture/browser approval: fresh6.5s terrain pair has651 exact
common samples, maximum heave difference0.00416921764mm and wheel-spin RMS
0.232471deg/s (event maximum5.93141deg/s). The17,768,364byte comparison export
parses inside exports/. Jump2s/20Nm and100mm Landing2s/20Nm pairs complete with
201 common rows; the near-boundary200mm energy-sized disagreement is explicit.
Energy toggle, shared case persistence, stale-result guard, native open/status/
close and no console warnings/errors are verified. The four named designs and
working snapshot deep-equal the captured pre-QA backup after UI restore. A later
unsaved baseline was observed by name without a complete captured snapshot; its
exact restoration is not claimed. Final proof is ignored
.preview/shared-contact-cases-final.png, with .preview/landing-case-reviewed.png.

Assessment-only early stopping was added after timing review: each torque trial
stops on first chassis arrest, bottom-out, underside threshold, jam or duration.
Ordinary full-duration simulation is unchanged, and later rebound/safety is not
certified by this first-arrest assessment. Focused full-versus-early first-arrest
checks for the passing/failing bracket pass in both engines. The default10-trial
search takes8.63s analytically and1.29s in Pymunk on this PC, both returning the
10.9375failing/12.5passingNm bracket; these timings are not hardware benchmarks.


## 2026-10-23 — merged studio and offline Plotly

Current top tabs are 00 Mechanism studio, 01 Analytical, 02 Pymunk and
03 Conventions. The saved-design library is expandable above the builder;
all equilibrium categories sit directly below its RHS mechanism preview.
Legacy designs/static URL aliases scroll to their corresponding inner section.
All static, dynamic and comparison data charts now use local Plotly basic4.1.2;
mechanism/FBD/convention SVGs remain illustrations. The pinned compressed vendor
asset is398299bytes, verified/decompressed by a fixed server route, with license
and hashes tracked. Plotly camera downloads are removed; existing app-folder
JSON/CSV exports remain. No numerical engine or profile schema changes occur.

Source/static9404, model2000, drawing1123, dynamic presentation46, profile-state31,
new static trace14, dynamic trace2535 and shared Plotly lifecycle11 assertions
pass. Launcher Stop/Start/reuse from unrelated cwd and new asset GET/HEAD/hash
checks pass at4191. Parent final browser/architecture approval: merged four-tab layout and readable RHS single-column plots; static point-click, drag zoom and series toggles; legacy static/designs aliases; builder Play/pause with settled refresh; dynamic comparison selectors and0.37s cursor retained through light/dark/light theme, engine switch and collapsed comparison reopening. Actual6.5s100mm/20Nm Landing pair651 exact common rows, both arrested, sampled maximum heave difference1.84191mm;13,148,659byte comparison JSON parses in app exports/. No console warnings/errors. Current working and all4 named designs deeply equal .preview/pre-plotly-studio-library.json revision57 after temporary pose changes were restored, without import. Final screenshots .preview/merged-studio-final.png and .preview/merged-static-plotly-final.png remain ignored.
Assumptions: four top-level workspaces, stable old URL aliases, library collapsed
by default, and engineering illustrations remain SVG. Builder Play labels
last-settled static results and refreshes after the pose settles.


## 2026-10-23 — optional motor inertia, reduction, cogging and losses

The optional project-v3 motorConfig is shared across both dynamic tabs, storage,
captured comparisons, exports and native playback. No existing profile receives
this block automatically. Default command basis stays joint-side; explicit
motor-side commands convert through positive reduction N. Rotor inertia reflects
as N²Jm and adds to legacy additional joint inertia; hip damping is separately
joint-side. Sinusoidal cogging uses fixed q=0 phase and conservative potential;
regularized Coulomb/viscous friction has nonnegative integrated motor loss and
explicit phase/drag resolution guards. These idealizations supply no measured
hardware values, gearbox compliance, stiction or electrical efficiency model.

The prescribed-height equations include physical reflected inertia and energy.
Analytical contact uses variable mass with its Christoffel term for smooth forces,
contact/stops and projection. Pymunk couples a scalar rotor in the same native
PGS iterations without fake translational mass or altered wheel spin inertia.
The private ABI is limited to verified WindowsAMD64/Pymunk7.3.0/Munk2D
2.0.1-ade7ed72849e60289eefb7a41e79ae6322fefaf3; other ABIs reject nonzeroJ.
Actual rotor angle/rate drive native motor work/KE/losses. Signed numerical
constraint work and coupled free-to-solved KE remain separate from motor loss;
contact/stop physical-loss partition is null when unavailable. No tight energy
conservation or impact peak claim is made. See motor-model.md.

Combined50 physics tests pass, including independent N/N², conservative cogging,
reverse-speed losses, held impact, physical native impulse coupling, stops,
friction/cogging guards and legacy source/contact cases. Motor impact discrepancy
refines0.546505→0.283404→0.144773mm atdt.0005/.00025/.000125. Bench motor finite-rise
error0.015915mm, ledgers3.61e-14/5.34e-6J. Native ABI suite7 tests includes actual
floor impact and callback lifecycle/version rejection. UI/state checks33 profile
groups,14 temporary-disk tests,6 balance conversion,48 comparison,3404 Plotlytrace
and19 delayed lifecycle assertions pass. The initial zero native motor-work bug
was fixed by capturing actual rotor angle before prepare(), with an independent
τshaft·Δθshaft identity regression. A late async Plotly purge race was addressed
with per-host serialized operations, generations and deferred destruction;
obsolete work is skipped, current errors still surface, and owned ResizeObserver
replaces Plotly's independent responsive resize callback. Parent final browser/architecture review passes shared motor controls, reload persistence, invalidN rejection and disabled zero effects; eight motor Plotly plots and comparison selectors; actual native desktop open/status/2s/close (manual native visual inspection not claimed). Corrected201-sample100mm Landing pair, N10/Jm.002/motor-basis2Nm, both arrested: max heave difference2.31726mm, motor-work difference0.0363737J, loss difference0.00045759J; final work−6.90556195/−6.94193569J. Numerical ledger maxima2.364J Pymunk versus0.08362J analytical remain explicit, not tight conservation. Captured motor profiles match in4,456,913byte comparisonJSON; CSV201rows/246155bytes parse in app exports/. Final delayed-chart repro passes two paired runs, rapid work/loss/rotor selectors, themes, result replacement and original-profile import/stale purge, with no new console warning/error. Current working and4 named designs deeply equal pre-motor-library backup after exact UI restore (revision85). Proof .preview/motor-comparison-final.png remains ignored.


## 2026-10-23 — standalone energy-only drop/torque screen

Both dynamic tabs now include a no-run local calculator with a Plotly curve and
app-folder JSON export. The residual underbody-to-ground target defaults50mm,
separate from the shared underside offset below hip A. An explicit editable1°
pre-stop reserve is an illustrative margin; zero is labeled stop-boundary only.
Optional energyConfig persists full calculator inputs but is absent in legacy
profiles and excluded from physical modelRevision/snapshot identity. Shared
opening/underside edits explicitly change the landing case; no controller laws
or torque commands are changed automatically.

The chassis-only screen retains m1*g*H without impact/friction credit, adds
compression gravity and signed spring/cogging release, then divides by available
joint radians. Rotor endpoints are at rest; no inertia energy is added. The
inverse is a sufficient selected-endpoint drop capacity, not a global optimum,
impact peak or post-arrest hold guarantee. Unsupported geometry/loads, slack
recovery and unavailable stroke are explicit. Original massless-wheel V4 and
prescribed-height mode work without contact/dynamics setup.

Independent baseline matches11.6103416383Nm at100mm, qend164°, endclearance
315.382413mm and20Nm endpointcapacity172.214939136mm; spring-disabled torque
51.7318271992Nm. Pure math39 assertions,15 temporary-disk tests,33 project-state,
48 comparison,19 Plotly lifecycle and2000 unchanged model assertions pass.
Launcher Stop/Start/reuse from unrelated cwd and both new assetHTTP200 pass4191.
Parent final architecture/browser QA passes baselineH100→11.610341638281414Nm joint/capacity172.214939mm/clearance315.382413mm; H300→34.846Nm; H200 with target500mm→43.452Nm and capacity92.003mm; negative height rejection; zero-reserve stop-boundary warning; shared tabs, N10 shaft1.1610341638281414Nm, reload persistence, Plotly light/dark and app-folder export. Export JSON is11542bytes with81 curve points and captures the exact project/calculation. No console warnings/errors. Current working and all4 named designs deeply equal revision87 pre-energy backup after exact UI restore (current library revision100), with optional motor/energy blocks absent again. Proof .preview/energy-calculator-reviewed.png is ignored. Parent independently verified spring work, endpoint geometry and positive interior kinetic energy. Publication review approved.

## 2026-10-23 — visible jump/drop parameters and target torque searches

Based on main0e73508. The user reported missing jump/drop parameters and asked
whether Pymunk could solve torque for jump height or drop/minimum chassis height.
Case inputs are now visible on both dynamic tabs. Jump height is first chassis
apex above actual takeoff; landing drop is wheel-bottom gap, minimum height is
underbody-to-ground clearance (default50mm, distinct underside offset50mm).
Read [target-torque.md](../target-torque.md) for all definitions and decisions.

Both engines run the same bounded five-coarse/five-local command search using
their own integrator. Observers measure every step through genuine first flight
or first arrest, freezing terminal measurements. Short horizons and numerical
failures stay indeterminate, never lower failing bounds. The search can probe
below the first passing command even if zero never takes off. Use tested torque
is explicit and blocked for changed mechanism/targets; target-only saved metadata
does not stale physical simulation results. Full outcome readouts now use the
same above-takeoff datum and show first-arrest clearance separately from full-run
minimum. Controllers and force laws remain unchanged. Energy estimates and
explicit copy-to-energy action retain distinct assumptions and saved values.

Validation:57 independent energy assertions,33 project-state groups,16 temporary
disk tests,48 comparison assertions,3404 dynamic Plotly assertions and19 lifecycle
assertions pass. Six target groups passed together (69.1s), including actual
engines, chatter/recontact guards, full/early agreement, known/unknown trial
boundaries and N10 motor/joint search equivalence; an added actual0.05s horizon
group passes separately. Nine existing contact-case groups pass. At7Hz versus
100Hz, measured jump-rise differences are0.633137mm analytical/0.000458mm Pymunk;
landing clearance differences0.000121mm/0.511062mm, with the same tested fixture
classifications. Output schedules change numerical substeps, so exact trajectory
invariance was an incorrect initial test assumption. A VM fixture realm error and
an initial0.02s horizon outside the existing0.05s minimum were corrected in tests;
no production tolerance/schema guard was weakened. The GPT6.1Sol implementation
agent hit its usage limit after integration; parent completed final fixes and QA.

Actual browser H100 jump finds10.9375Nm in each engine (9.375Nm known failure),
with105.380mm analytical/105.118mm Pymunk above takeoff; ideal work estimate
8.859123Nm. H100 landing target50 gives12.5Nm Pymunk; target500 gives21.875Nm
in both, minimum clearances501.453mm/500.355mm. Invalid negative target, shared
tabs, stale apply guard, apply command, reload, explicit energy-copy and JSON
exports pass, no browser warning/error. Full applied10.9375Nm jump pair completes
651 exact samples each through6.5s; sampled max heave difference7.23474mm and
Pymunk max energy-ledger residual5.772J remain visible. Paired export13872714bytes,
jump assessment13223bytes and landing assessment11656bytes parse in app exports.
Normal Pymunk run confirms the new first-flight-height outcome readout.

Actual app-local Stop/Start/reuse from unrelated cwd passes4191. Original working
and all4 named designs deeply equal pre-target-torque-library backup after UI
import restore, library revision110. Proof .preview/target-torque-jump-reviewed.png
is ignored. New target metadata is absent again in the restored original design.
No canonical robot/hardware, global optimum, impact peak or post-arrest safety
validation is claimed. Required workspace publication gates/hooks follow final QA.

## 2026-10-23 — visible energy equation and Flipsky/gearbox screening

Based on main425406a. The user requested the2m landing equation as a calculator
table and asked to add Flipsky peak torque and gearbox ratios from their motor
workbook. Both dynamic tabs now show the live quantity/equation/value/unit table
inside the energy calculator, with a2m height-only example button. Nine motor
variants and four distinct EG23 reductions (5/10/20/50) are transcribed; sale20
and used50 listings are deduplicated. Public product references and all ratings
are recorded in [energy-calculator.md](../energy-calculator.md); private workbook
IDs, unrelated data and account material are not included in the public repo.

Optional energyConfig.screening saves motorId, gearboxId, editable peakShaftNm,
customRatio and nullable customMomentaryNm. Legacy/manual profiles remain absent.
CandidateN is analysis-only, including conservative cogging recalculated from
explicitly retained enabled saved passive motor values; disabled passives stay
zero. No actual motorConfig/controller input or physical result identity changes.
Ideal motor peakN*shaft and separate gearbox momentary output cap determine the
available screen torque. Unknown custom gearbox limits cannot pass. Catalog
maxima are not continuous or verified regenerative-braking ratings, and listed
forward efficiency supplies no backdrive credit. Inertia/losses are not guessed.

The2m V4 baseline reproduces232.345151886620Nm over0.738856050011rad from
171.669621162138J motor work. All four listed gearbox momentary limits20–60Nm
fail this demand; an80100/20:1 has340Nm ideal motor peak but only60Nm gearbox
capacity. These are initial-arrest endpoint screens, not impact/hardware ratings.

The separate dynamic-case energy guidance uses landingEstimate with the actual
saved physical motor, excluding catalog selection while retaining requested
case height/clearance. Parent integration review caught and corrected candidate
gearing leaking into that guidance before publication.

Validation:115 energy assertions,33 project-state groups,19 Plotly lifecycle
assertions and17 temporary-disk tests pass, plus JS parsing/Python compilation,
whitespace and app-doc relative links. An ignored two-panel VM UI integration
check passes initial absence,2m button, candidate/gear cap, peak override,
shared-tab synchronization, manual restore and unchanged physical identity.
Its first attempts exposed missing fake-DOM methods/selectors, corrected only
in the harness; no production guard was weakened. Real browser automation had
no enabled surfaces, so new visual layout/pointer/console QA is unverified.
Actual project-local Stop/Start/reuse from C:/Windows/Temp passes4191, both tab
URLs and changed assets returnHTTP200, and the server remains running. The
working copy and all4 named designs deeply equal the pre-task library backup
at revision111. Canonical physics and new dynamic integrations are not applicable
to this isolated analysis-only change; hardware remains unvalidated.

## 2026-10-23 — consolidated findings PDF and Pymunk spring visibility

Based on main `3d959e4`. The user requested one PDF of this app's learnings and
findings and a check that the constant-force spring actually works in Pymunk.
Audit found the exact constant-tension law already enters both prescribed and
contact dynamics through the finite-idler generalized torque. The contact/native
illustrations omitted the wrap, outgoing cable and remote assembly. Browser
playback now shares frame-driven spring geometry; the native Tk viewer mirrors
it. The complete cable, schematic housing/payout dial and active-law/Fs/torque/
delta-L90 readouts follow captured physical frames, not decorative time rotation.
Camera bounds include the route, and hip labels avoid the chassis mass label.
No backend law, force/controller interface or saved profile was changed.

New `verify_spring_playback.py` passes three groups: eight actual engine runs,
five-pose virtual-work controls for each spring law and222 SVG geometry checks.
At q0=132.5deg, dt0.00025s, flat input, zero actuation/damping and constant
p0=330.869282809N, actual Pymunk tension stays constant while q reaches
156.111563deg prescribed /156.111368deg contact in0.3s. Cable payout changes
25.462562/25.462355mm. At common t0.2s, prescribed chassis height is556.974252mm
ON versus446.411652mm OFF; contact is556.974675mm ON versus446.411652mm OFF.
The OFF prescribed run stops at0.242s, so final unequal-time endpoints are not
used for that claim. Maximum ON analytical/Pymunk heave discrepancy is0.221102mm
prescribed /0.199504mm contact. Contact explicitly uses the1.5kg wheel, mu0.8,
zero bounce and free drive; the original saved coil profile remains unchanged.

Parent integration checks pass14 `verify_viewer.py --gui` groups including actual
Tk playback, witness motion and service start/close/restart;2000 core,1123 drawing
and666 contact-drawing assertions; JS parse/Python compilation and whitespace.
The development worker initially corrected old fake viewer-model fixtures to use
validated real models. One first native contact GUI self-test failure did not
reproduce alone, in two worker suite reruns, or in the parent14-group rerun; no
production tolerance/guard was weakened. Browser automation has no enabled
surfaces, so manual live browser/native visual and pointer review is unverified.
Two actual-frame contact SVG illustrations were rasterized and inspected; they
show different payout/dial positions and no overlapping hip/mass text.

`build_findings_report.py`, optional `requirements-report.txt` and the curated
`spring-report-evidence.json` reproduce the12-page `exports/kinefold-findings.pdf`.
It distinguishes historical checks from this new audit, coil support from
constant cable tension, impact energy from survival claims, shaft/joint torque
and gearbox caps. The2m result is232.345152Nm with the V4 coil or252.378648Nm
with ideal constant p0; current EG23 caps all fail. ReportLab4.4.9 generated the
PDF; all12 rendered pages and the updated page4 were visually checked, with
page count, footers, text bounds and missing-glyph checks. PDF/raw results and
images stay ignored under app exports/.preview; reproducible source is tracked.
Final app-local Stop/Start/restart/reuse checks from C:/Windows/Temp pass at4191;
both dynamic routes and the three changed browser assets returnHTTP200. The full
current profile library deeply equals the revision111 pre-task backup, including
all four named designs. Report text/footers/bounds/glyph checks and30 app-document
links pass. Actual run environment: Python3.13.12, NumPy2.5.3, SciPy1.18.1,
Pymunk7.3.0; numerical agreement is scoped to this environment and these fixtures.

## 2026-10-24 — publish local configuration snapshots

The owner requested committing and pushing all changes. Tracked source was
already clean at `156ba08`; the new work was in the ignored local profile store.
[Portable configurations](../saved-configurations/README.md) now retain the one
named VSL V4 nominal alpha-zero profile and a separate exact working-draft copy
from library revision 20. The live library and original exports are untouched.
Import either project JSON through the app and use Save as for a new named copy;
their preserved original IDs are the same.

The nominal profile keeps 8.75 kg chassis, zero other masses, 135-degree starting
pose, V4 coil and the 150 mm prescribed square over 6.5 s. Its previous local
analytical/Pymunk pair had 656 matched samples and maximum chassis difference
0.00594036 mm; those outputs remain ignored and are not new physics evidence.
The working draft has m2=m3=1 kg, m5=m6=0 and terrain-contact mode, so it is
explicitly unsupported by the current contact solver. Preserve the owner's
inputs and resolve model/mass/input requirements before running that draft.

Snapshot JSON/import validation, exact source equality, nominal source parity,
retained-run evidence and the draft's expected contact rejection are checked
for this publication. No new simulation, browser or hardware check is claimed;
the required workspace entry/gate checks and installed hooks apply.

## 2026-10-25 — independent component presets and comparison studies

Based on main `9d086a8`. The user requested reusable motor/gearbox combinations,
nonideal inertia/cogging/viscous effects, multi-candidate contour/range studies
and a system graph showing numerical inputs, equations and outputs. Sol workers
implemented storage, pure calculation and UI in isolated worktrees; parent
specified the contracts, reviewed the physics mapping and completed integration.

Top tabs now retain00 studio,01 analytical and02 Pymunk, then add03 Presets &
studies and04 System flow, with05 Conventions last. Stable existing URLs remain.
[Parametric preset notes](../parametric-presets.md) explain the separate
profiles/presets.json revision, typed suspension/actuator/input records, immutable
resolved study copies, import-as-copies and explicit project-v3 composition.
Existing library.json and all4 named designs/working copy remain byte-identical
to the pre-task backup at revision111. Preset selection, calculation and batches
do not edit that working design. Local bundles/outputs stay under app exports;
source pulls do not synchronize live libraries automatically.

The fixed-hip prescribed-load screen reuses V4 static demand and derives body
Jacobian inertia, J-prime velocity term, N-squared reflected motor inertia,
inverse-squared motor-equivalent leg inertia, periodic fixed-amplitude cogging,
Coulomb and viscous losses. It distinguishes motor EM-equivalent joint demand
from actual gearbox output load; contact/impulse output loads stay unassessed.
Computed triangle-clipped isobands/isolines use offline Plotly BASIC scatter.
Peak/rpm/gearbox ratings are independent bounds, not a torque-speed motor curve.
Missing passive data blocks composition unless explicitly idealized; speed and
torque ratings remain nullable. The deliberate V4 example creates separate ideal
study records without changing the original design. No physical motor law or
engine integration code changed; actual candidates use the existing laws.

Parent validation:55 preset JS assertions with37 mirrored fixtures,9 temporary
Python preset groups,92 independent kernel assertions,48 DOM/VM UI assertions
and20 BASIC chart mounts pass. Existing33 project groups,17 disk-profile tests,
2000 model/115 energy assertions and19 lifecycle/14 equilibrium/3404 dynamic
Plotly assertions pass. The UI harness uses real kernel/store contracts with
mock trajectory rows; actual visual/pointer review is unverified because CUA
inventory contains no enabled browsers/apps. Parent corrected invalid nested
motor labels with an accessibility regression and retained actionable candidate
composition failures before scheduling a backend.

The retained [actual batch check](../verify-preset-batch.cjs) separately passes
both subprocess and same-origin HTTP modes: two illustrative N5/N10 motors with
nonzero rotor/cogging/Coulomb/viscous terms, one captured1.5kg-wheel flat-floor
contact case, four engine jobs over0.3s. Each pair has16 matching samples; max
chassis differences are0.000390809/0.001226938mm. These are numerical fixtures,
not measured motor parameters or terrain-edge/hardware certification. An initial
parent harness called compare instead of comparison; corrected before the clean
rerun. Worker VM realm fixtures and an explicit-null motor validation omission
were corrected before final passing tests; production guards were not weakened.

Actual project-local Stop/Start/reuse/Stop/restart from C:/Windows/Temp passes4191.
Both new routes and all five new assets return200 with exact source bytes;
preset-list200, foreign Origin403 and stale revision409 are verified. JS parsing,
Python compilation, whitespace and relative documentation links pass. Publication
uses workspace scope, normal hooks and fetched-base checks; canonical robot
physics is NOT APPLICABLE. Stop with Stop Kinefold.cmd and restart through the
existing Start Kinefold.cmd; no boot/login automation is added.


## 2026-10-26 — visible linear compression spring

Based on main 599a626 after fast-forwarding the unrelated Controls Lab updates.
The owner requested a compression-spring illustration in place of the circular
remote-housing/payout dial. A GPT-6.1 Sol worker implemented the shared browser
and native drawing; parent reviewed, integrated and visually refined the wire.

Both dynamic browser previews and the desktop viewer now show a fixed near seat,
moving cable seat, axial spring body and complete cable. Positive cable payout
retracts the far seat by exactly the same distance, compressing the spring while
keeping total geometric cable length constant. The illustrative seat separation
is 80 mm plus full-travel maximum payout minus current payout. Exact existing
route extrema provide a stable envelope; there is no visual stroke clamp.
Assembly points participate in fixed-camera bounds. The 80 mm clearance, wire
radius and mounting offset are drawing choices, not measured spring packaging,
new physical stops or additional inertia. Selected V4/constant-force laws,
prescribed/contact solvers, project schemas and saved inputs are unchanged.

Actual verification: three spring groups pass, including eight existing actual
engine on/off runs and 4,506 browser/native geometry assertions for route,
compression direction, 1:1 stroke and constant total cable length. Existing
1,123 drawing, 666 contact-drawing and 2,000 core assertions pass. Worker native
GUI suite passes all 14 groups; parent reran the focused actual Tk compression
seat/motion check after thinning the final wire/seat strokes. The inherited
arbitrary 5-pixel dial threshold initially failed; it was replaced with exact
camera-scaled seat travel and an independent greater-than-5-mm physical-stroke
check. Parent XML rendering initially rejected valueless data attributes; explicit
empty values fixed both standalone SVGs before successful XML/raster checks.
Two actual contact frames were rasterized and visually inspected; spring turns,
shortening and complete framing are clear. Real browser/pointer review remains
unverified because CUA reports no enabled surfaces.

Actual project-local Stop/Start/Stop/restart/reuse from an unrelated directory
passes at 4191. Both dynamic routes return HTTP200, and all three changed browser
assets match disk bytes. The complete live profile library remains byte-identical
to the pre-task backup (SHA256 efc400c3fd5e3112cfce92ecddb25ac81b0683a7b55f1633306d6211ec01eb7f).
The preview stays running; refresh and rerun a case to use the new browser
drawing, or reopen the desktop viewer. Source publication uses workspace scope,
normal hooks and fetched-base checks; canonical robot/hardware validation is
not applicable to this drawing-only change. Historical dial/report evidence
above describes the earlier representation and is not a new physical package.
