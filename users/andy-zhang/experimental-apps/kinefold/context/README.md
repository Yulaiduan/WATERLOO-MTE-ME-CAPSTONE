# Kinefold context

## Latest — 2026-10-30 chassis pin and gearbox response

Read [gear-response study](../gear-response-study.md). Based on main c623463;
three authorized GPT-6.1 Sol workers owned constrained contact, UI/persistence
and the bounded runner in separate worktrees. Parent integrated/audited, ran
physics, exported Plotly/GIF media, documented and published. No Computer skill.
Optional runConfig.fixture=pinned-chassis fixes only chassis height during actual
terrain stability; physical wheel collision, spin, slip and separation remain.
Signed pinForceZN is interval-average fixture force +z, with momentum budget,
zero ideal work and unavailable t0; support=m1*g-pin. Floating fields stay null.
Pinned bench/jump/landing and pinned nonzero height steps reject transactionally.
Optional actuatorConfig rideTargetStepMm/time change only the floating terrain
controller reference; stationary actual floor accepts speed0, prescribed bench
still requires positive speed. All-case automatic jobs reject pinned diagnostic.

An actual finite-link/hardware flat-pin run exposed near-zero-speed holding
dropout: braking classification now requires shaft speed above the existing
1e-12 cutoff. Below it, conservative holding conversion keeps torque present;
regen/contact/power caps unchanged. The old42 preliminary runs are superseded.
Final50 fresh runs (36base,8half-step,6large-step) all resolve,25exact enginepairs;
source hashes, raw metrics, signed pin budgets and6live HTTP cases pass.
ODrive+G5/G10/G20+B2 gives totalN10/20/40,peak64.4/128.8/244.4Nm,
reflectedJ.0591/.2364/.9457. 100mm rise118/108/113ms; settle344/347/598ms.
Same gains:20 helps a torque-limited larger move;40 overshoots more. Highest
passing tested terrain speed4/3/1m/s, not certified maxima. Half-step preserves
10pass/20fail at4m/s. Contact and controller response matter; terrain never
reaches torque cap. Full assumptions and discrete loaded-contact definition
are in the report. No hardware or full-body stability claim.

Focused tests and existing JS/replay/Plotly checks pass; actual launcher reuse /
stop/start at4191 passes. The live profile library is preserved (outside user
edits remain); no runner writes it. Six Plotly PNGs,3paired actual GIFs and
compact exact settings/raw-example ZIP stay app-local ignored/native Notion.
Use gear_response_study.py with a fresh output/config for bounded refinements,
and retain physical unilateral contact instead of binding the wheel to terrain.

## Latest — 2026-10-30 ODrive, hip belt and terrain speed

Read [terrain-speed study](../terrain-speed-study.md). Based on mainaca73a1;
three authorized GPT-6.1Sol workers owned Python belt mechanics, JS consumers
and bounded runner; parent integrated/audited, ran physics, exported media and
handled reporting/publication. Optional hipBeltRatioB1..3 multiplies base gearbox
ratio; missingB preserves legacy shape/default1. Torque/speed/Coulomb scaleN,
input-equivalent inertia/viscous scaleN²; gearbox caps stay beforebelt. The extra
belt is ideal/noaddedJ, distinct from existing carrier belts and spring geometry.

ODriveM8325s100KV +AB90G10 +B2=20:1:128.8Nm rest motoring,147.6Nm backdrive
braking under assumed efficiencies. RotorJ estimated,.0001 gearJ assumed;
constant Coulomb/cogging.05Nm,viscous.0008Nms. Source6.64Nmpeak3s/3.32continuous;
4800rpm ideal48V envelope. Matched Flipsky uses samegear/B2 with6240rpm envelope.
20actualruns +6half-step ODrive checks: all numericallyresolved. Same1.8m strip
and.6–1.8m weightedmetrics, no contactloss/saturation/stops in these mildcases.
ODrive RMS1.688→1.879mm vsFlipsky1.698→2.605mm at.4→3m/s; lower estimated
reflectedJ is consistent with better heave here, not a global optimum. ODrive
jump.502/.499m misses2m target;2m landingarrests at568/561mm minclearance,
with substantial rigidimpact loss. Half-step classifications unchanged, landing
engine clearancegap8mm remains. No hardware impact/full-body stability claim.

Four actual paired1×GIFs plus3PlotlyPNGs and compactdataZIP are app-local ignored
exports/native Notion attachments. Source/config guards and13enginepairs pass;
live HTTP B2results matchcaptures. Actual capturedcase replay/mirror DOMchecks
pass; no GUI automation. Legacy/live profilelibrary unchanged. Use newrunner
settings/freshapp-localfolders; Start Kinefold.cmd retains4191 afterrestart.

## Latest — 2026-10-30 small workflow example and saved terrain GIFs

Owner narrowed the followup to a simple worked workflow and limited search/data.
Based on main183f860, two authorized GPT-6.1Sol workers owned a bounded three-choice
runner and saved-frame GIF export. Existing model/UI source is unchanged.
Read [workflow example](../workflow-example.md). The choices are6384+AB90G10,
80100+AB90G10 and80100+AEP90G20, with45kg chassis/55kg gross, alpha20deg,
2m targets,50mm clearance, constant Coulomb/cogging and viscous drag.
There are18 actual runs /9 exact pairs: conservative jump rises.443/.786/.898m;
the first choice bottoms out from2m and the other two arrest. Terrain RMS
1.676/1.679/1.698mm is a practical tie within an editable0.1mm band.
The20:1 choice leads jump/first-arrest clearance among these three; none reaches
the2m jump target. These are conditional examples, not hardware optima.
Four paired GIFs (three prior N20 terrains plus the worked80100+AB90G10) use
91 frames /4.5s, a labelled0.5s end pause, one camera and+x left/+z up.
Source clock/settings and geometry are validated. Sharp/Pillow export uses no
GUI or new physics and removes its temporary caches. Summary retains all18
requests; raw frames remain only for one combination's six captures, in a3.13MB
ZIP. Six comparison tests and15 animation assertions pass. PNG/GIF/data stay
in ignored app folders and native Notion attachments. Capture/source guards
remain intact; no live profile writes or catalogue-wide scan occurred.

## Latest — 2026-10-30 nonideal motor and heave study

Based on main1ab279e. Owner requested constant Coulomb/cogging drag plus viscous
losses, explicit motor/gear inertia and jumping/terrain comparisons. Two authorized
GPT-6.1Sol workers owned core/UI/persistence and a standalone study runner;
parent owned architecture, actual study runs, audit, Plotly/Notion and publication.
No Computer skill, GUI automation, source-app or canonical component changes.

Read [nonideal study](../nonideal-study.md) and [motor model](../motor-model.md).
Optional motorConfig.gearboxInputInertiaKgM2 reflects once with motorJ through N²;
legacy10-key snapshots preserve their shape. New loss Apply buttons explicitly
lump cogging into constant Coulomb, set periodic amplitude0, preserve gear/J,
and offer low/medium/high shaft placeholders. Every actual-contact row/event
now carries exact Coulomb/viscous integrals, summing to unchanged aggregate loss.
Motor sample diagnostics use actual current/native state; bounded shaft conversion
is retained. The old rotorKineticJ name now explicitly includes gear train energy.

Retained72runs use45kg chassis plus four1/1/.5kg leg assemblies =55kg gross,
alpha20, full65deg,2m targets and50mm clearance. At20:1, jump about1.35m reference
versus0.90m with driveJ+drag; both arrest2m with driveJ+drag, much energy removed
by rigid collision, not friction/motor alone. Mild seeded terrain RMS about1.70mm;
grade case1.79mm tracking error versus intentional raw uphill rise. High-gain
40:1 reaches stops; coarse native is incomplete, finer both physical-limit cases.
Do not call finite-gain exact-state feedback mathematically perfect/optimal or
the quarter heave model full-body stability. Unknown thermal/continuous ratings
remain unassessed. Capture source/config guards and actual failed cases retained.

13PlotlyPNG and five data/source ZIPs remain ignored under app exports and are
attached natively in Andy's Codex Studies. Final72-run source/config-pair checks
pass; maximum Coulomb+viscous minus aggregate error3.13e-13J. Short actual HTTP
engine pairs and durable launcher stop/start/reuse/restart pass at4191; live
profile SHA b580c793d96ce2c3fa912490e1d11f8a3fff11854dd7a065d462cc61482fb511 unchanged.
Focused engine, preset, replay and UI tests are recorded in the contribution log;
known prior whole-JonHTML provenance test failure is not claimed fixed.

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

## 2026-10-26 — dedicated jump and landing energy workspace

Based on main `5a2b537`. The owner requested all energy calculations and plots,
with energy sizing separated from the simulation Run workflow. A GPT-6.1 Sol
worker implemented the feature in an isolated worktree; parent reviewed the
equations, UI structure, handoff and final integration. Current order is
00 Mechanism studio, 01 Energy, 02 Analytical, 03 Pymunk, 04 Presets & studies,
05 System flow and 06 Conventions. Existing tab IDs/legacy studio aliases remain.

Energy has Jump/Landing selectors, immediate edits, the saved mechanism identity,
four expanded Plotly charts per case, complete quantity/equation/value/unit
tables and expandable 81-height/161-stroke sample tables. Charts show joint and
shaft torque versus height, signed energy terms versus height, accumulated work
and kinetic budget along the stroke, and hip height/underbody clearance versus
angle. Local plot range defaults to 0–3000mm, editable within 0–5000mm; it is
not saved as a physical input. Out-of-range targets are labelled. Optional
catalog controls/long rating tables collapse; calculation tables/charts remain
visible. Parent made desktop inputs a compact two-column grid and retained a
single-column small-screen layout; live CSS layout is unverified.

The pure `workspace(project, kind, options)` helper retains the existing landing
and jump APIs/numbers and adds raw signed work samples. Negative kinetic budgets
remain negative and flag sampled barriers; no sampled pass certifies a path.
Jump is an optimistic full-extension/locked-flight work screen, using chassis
stance gravity and chassis-plus-wheel flight mass. Landing retains full chassis
drop energy without impact/friction credit and assesses first arrest only.
The 50mm residual clearance is distinct from the 50mm underside offset. Missing
stroke/clearance, moving link mass, slack and unsupported geometry stay explicit.
See [equations and scope](../energy-calculator.md), not a new robot baseline.

Existing energyConfig/torqueTargetConfig store analysis metadata; no schema
migration or automatic optional block is added. Shared landing opening/underside
remain physical case edits. Candidate motor/gearing stays analysis-only. Explicit
Use physical estimate actions recompute with the actual saved motor and cogging,
convert to its saved torque basis, validate complete commands and open an engine
without running. Contact incompatibilities block copying, with actionable reasons
and a settings link; no masses are substituted. Review caught the old landing
brake limit silently capping a larger command: copying now explicitly raises a
lower limit, discloses that limit and validates before any write. Dynamic target
searches and all existing energy plots are retained; duplicate full calculators
are removed from the dynamic panels. Complete JSON uses energy-workspace-v1;
curve/stroke CSV and JSON use existing app-folder exports, not Downloads.

Parent integrated checks PASS: 115 retained energy assertions, 4,490 detailed
energy assertions, 642 DOM/VM assertions with 48 scatter-compatible chart mounts,
33 project groups, 17 temporary-disk profile tests, 48 preset UI assertions with
20 chart mounts, 19 Plotly lifecycle assertions, 14 equilibrium and 3,404 dynamic
trace assertions, and 2,000 core assertions. Fifteen pre-change fixtures match
exactly across both spring laws/off and heights 0/100/500/2000/5000mm; the V4 2m
landing result remains 232.345151886620Nm. Initial worker fixtures used an invalid
spring identifier, wrong independent height formula, host-VM realm and CJS export
name; these harness errors were corrected before passing. Source EOL churn was
removed. No production validation guard or tolerance was weakened. JS parsing,
Python compilation, documentation links and whitespace are checked before push.

Actual project-local Stop/Start/Stop/restart/reuse from an unrelated directory
PASS at4191. Eight changed assets match disk bytes; all seven tabs and two legacy
routes return HTTP200. Live library.json is byte-identical to its pre-task backup,
SHA256 efc400c3fd5e3112cfce92ecddb25ac81b0683a7b55f1633306d6211ec01eb7f.
CUA lists no enabled apps/browsers, and opening IAB reports unavailable. New live
visual, pointer, console, zoom and real browser theme review remain UNVERIFIED;
the DOM harness is not a browser. No new dynamic integration/hardware test is
claimed for this calculation/UI contribution. Canonical robot physics is NOT
APPLICABLE; normal fetched-base checks and publication hooks still apply.
Restart via app-root Start Kinefold.cmd, stop via Stop Kinefold.cmd; the preview
remains http://127.0.0.1:4191/?tab=energy, without login/boot automation.

## 2026-10-26 — mounting pitch α in energy calculations

Based on main `08acb24`. Owner requested α in energy calculations. A GPT-6.1 Sol
worker implemented the calculation/UI/tests in an isolated worktree; parent
reviewed the rotation, work signs, glossary and final integration. The old
blanket vertical-guide rejection is removed for supported straight, nonsingular,
monotonic world-height branches. Both Jump and Landing use the full saved
projection `C_z=−sin(α)P_u+cos(α)P_v`, `h=r_w−C_z`; signed wheel x coordinates
use `C_x=−cos(α)P_u−sin(α)P_v`. Here source P is the local wheel centre,
distinct from Kinefold's statics rim-load point P. Nonzero φ₀ is included.

The chassis retains fixed x and pitch and moves vertically, on a horizontal
stationary floor. Wheel height stays r_w but horizontal wheel motion is allowed.
This is an endpoint work assumption, not a new contact integration. Ideal guide
and floor reactions do no work; retained wheel-spin/rotor kinetic energy and
rolling/contact/impact/friction losses remain outside this screen. Spring geometry
is chassis-local: α alone neither retunes preload/stiffness nor scales spring
work. Only φ₀=0 reduces vertical travel/gravity to the cos(α) expression. The
underside offset remains the declared vertical distance below A. Clearance roots
use rotated geometry and retain the earlier stop/clearance limit.

The Energy tab now shows saved α with an Edit in Mechanism studio action, full
projection equations and guide orientation, signed horizontal wheel travel,
α-labelled Plotly charts and explicit α in every height/stroke CSV row. Additive
JSON fields carry these same projections/metadata; no saved-profile/schema or
default-input migration occurs. Negative signed demand still clamps only the
torque magnitude: jump surplus or landing's unreachable endpoint/earlier arrest
are explained separately. Physical command handoff supports tilted contact cases
without running them. The separate legacy dynamic energy-sized controller stays
vertical-only and impact-adjusted; it was not changed by this contribution.

Integrated checks PASS: 185,698 independent tilted assertions across480 endpoint
fixtures (α0/10/20/30/45°, φ₀0/20°, both spring laws/on/off, stop/clearance limits,
heights0/100/2000mm);115 retained energy;4,490 workspace;712 DOM/VM with52 BASIC
chart mounts;2,000 core;33 project groups;48 preset UI with20 mounts;19 Plotly
lifecycle and6 motor UI. Independent raw two-link rotation, full-potential finite
derivative integration, gravity cos projection, invariant local spring work,
signed budgets, gearing, purity, reload/export and tilted handoff are covered.
The initial450mm-clearance fixture was corrected from400mm because the φ₀20°
stop already leaves409.0268mm; no guard or tolerance was weakened. V4 α0 2m
remains232.345151886620Nm. Copied current free-wheel design at α30 gives
226.970867387894Nm, unchanged spring storage29.644002342084J and lower compression
gravity25.667800887858J. Those sensitivity copies never replace the saved design.
Fifteen retained pre-change α0 fixtures match all195 numeric fields exactly.

Actual app-root Stop/Start/Stop/restart/reuse from unrelated cwd PASS4191; three
served JS assets match disk and five relevant routes returnHTTP200. Live profile
library remains byte-identical, SHA256
efc400c3fd5e3112cfce92ecddb25ac81b0683a7b55f1633306d6211ec01eb7f.
Four actual-data Plotly PNGs plus a combined overview/ZIP are exported under
ignored app exports and visually checked; initial mixed light/dark plotting
palette was corrected before final review. PNGs are static figures, not browser
screenshots. Live browser/pointer review and new trajectories/hardware tests are
UNVERIFIED; canonical robot physics is NOT APPLICABLE to this member workspace.
Use the existing app-root Start/Stop launchers and refresh the stable energy URL.

## 2026-10-27 — actual contact work integrals and separate chassis arrest

Based on fetched main `c2c59d8`. The owner requested integral portions stored by
the spring in both proper dynamic engines and clarification of velocity at
ground contact. A GPT-6.1 Sol worker implemented the isolated app changes;
parent reviewed event semantics, work signs, external-load/projection accounting,
native energy partitions, plot endpoints and integration. No contact force law,
velocity clamp, spring law, saved profile, reference source or canonical model
was changed. V4 remains approximately constant chassis support; exact ideal
chassis gravity compensation is distinct from constant cable tension.

Both actual-contact tabs now open eight matching Plotly work views, exact event
tables and signed first-contact-to-arrest accounts. Landing defaults to the
earlier arrest/compression-stop endpoint; full trajectory retains rebound and
signed reversals. Exact step states survive sparse display sampling. First
contact means first wheel impulse: analytical speculative contact can begin at
positive gap, so its first wheel velocity need not be zero. Chassis arrest is
later; bottom-out before or at arrest remains failure. Source/loss/numerical
terms and unavailable native rotor partitions are kept separate.

Additive contact-v2 work metadata, row deltas and contact-prefixed CSV columns
reuse per-step motor/source/loss work and exact spring potentials. Additional
global-force/couple work is now explicit, excluding analytical position
projection. Pymunk component wheel kinetic/gravity energy now uses actual body
states; ideal-guide reconstruction had differed slightly from native total
energy under constraint residual. CSV safely quotes nested objects and strings.
The glossary defines signed accounts and their contact-relative aliases.

Worker checks PASS: six new Python work groups; 530 real-engine Plotly/work
assertions; nine existing contact-case groups and 27 independent analytical,
motor-contact/native-rotor groups. Parent integration PASS: 530 work, 3,770
dynamic-trace, 48 comparison, 2,000 core, 33 project and 19 Plotly lifecycle
assertions, syntax/compile and eight copied saved-profile rollouts. The initial
test assumption of exactly zero wheel speed at the first analytical impulse
was corrected to the actual speculative-contact definition; a harness calling
the prescribed-height CLI with contact input was corrected. No production
guard or tolerance was weakened. Native energy-component mismatch was fixed
before the work-ledger checks passed.
The staged whitespace check caught CRLF in the two new test files; those files
were normalized to LF before the clean staged/publication checks.

Actual copied 2m/260Nm/200Hz landing at dt0.000125s: analytical first impulse
0.638500s/arrest0.742375s, spring storage25.722834J, motor removal171.272717J,
compression gravity25.754155J; Pymunk0.638625s/0.742625s,25.828902J/171.843841J/
25.822637J. Both arrest before bottom-out. Chassis is still descending about
6.26m/s at first impulse. Full-run maximum unresolved residual decreases
2.714240→1.354243J analytical and4.381007→2.107557J Pymunk when dt halves
0.00025→0.000125s; this is not tight conservation. Zero-braking 2m controls
bottom out in both engines. The 100mm/12.5Nm copied landing still arrests.

Parent rendered19 actual-data PNGs (three comparison figures plus all16 new
app-generated traces), CSV, complete eight-run JSON and source/hash ZIP under
ignored app exports. All images and ZIP were checked, with overview/contact
sheets visually reviewed. Initial export dimensions defaulted to700×500; they
were explicitly corrected to1500px width before delivery. PNGs are scientific
figures, not browser screenshots. CUA has no enabled surfaces, so live visual,
pointer and browser-console review remains unverified. Reviewed plots and data
were uploaded as actual Notion attachments under the existing studies page.

Actual app-root Stop/Start/Stop/restart/reuse from C:/Windows/Temp PASS4191.
Five routes returnHTTP200; all five changed browser assets match disk bytes.
Fresh same-origin API landing requests pass both engines with81 rows each and
the same first-arrest times. The full live profile library remains byte-identical
SHA256 efc400c3fd5e3112cfce92ecddb25ac81b0683a7b55f1633306d6211ec01eb7f.
Canonical robot/hardware physics is NOT APPLICABLE to this isolated experimental
workspace. Use app-root Start Kinefold.cmd after shutdown, Stop Kinefold.cmd
to close it; http://127.0.0.1:4191/?tab=analytical retains the original server.

## 2026-10-29 — sheet-derived periodic terrain profiles

Based on main `e83271d`. Owner requested short periodic terrain representations
from Terrain Data Table, Terrain Estimates `A4:X20`; sheet read-only, retrieved
2026-10-29. A GPT-6.1 Sol worker implemented the isolated feature; parent reviewed
source extraction, geometry, integration and actual API behavior. All 16 source
archetypes retain synthesized status/confidence and typical/difficult/extreme
estimates in the offline catalog. Snow's misaligned RMS/spacing/corridor stay
unresolved; an explicit period is required, and snow RMS mode is blocked.

Both dynamic tabs have source/severity/representation/repeat controls, Plotly
preview, explicit Apply, short preview, square restoration and existing input
preset saving. One optional strict terrain-v1 block flows through project-v3,
disk/input presets, immutable comparison identities, exports and viewer dispatch.
Both actual engines collide with the same 96-segment periodic top contour;
native/browser playback uses returned geometry plus the actual moving transform.
Obstacle peak and continuous mean-removed RMS are separate representations.
Extreme spacing reuses difficult spacing explicitly; roughness wavelength reuse
is an assumption. Short preview sets period/6 speed and6.5s duration with0.5s
delay; rim lead can prevent a full cycle passing the wheel. Physical mechanism,
spring, motor and friction are preserved. Flat average grade and rigid2D contact
do not reproduce grade/cross-slope/corridor or soil/snow/water behavior.

Parent verification passes12,802 independent source/geometry assertions across
93 configurations,34 terrain DOM assertions/29 Plotly mounts,7 Python terrain
groups,33 project groups,55 preset assertions and rerun9 contact-case/8 contact
groups. Worker separately passed91 mirrored contours,48 preset UI/712 energy UI/
3770 dynamic Plotly/48 comparison/666 contact-drawing assertions,17 disk-profile/
9 disk-preset groups and actual Tk contour/playback smoke. Three worker surfaces
(gravel obstacle/RMS,300mm talus) completed6.5s in each engine. These are selected
numerical fixtures, not validated traversability of all archetypes or hardware.

Parent HTTP review caught missing static-asset allowlist entries and corrected
them. A20Hz final-output remainder also exposed a false36GN warm-start impulse
spike; both contact clocks now snap only output-boundary roundoff within1e-10s,
with a6.5s flat-support regression. No force/velocity/penetration clamp was added.
Fresh actual API gravel runs after repair complete131 rows through6.5s at
dt0.0005s: analytical13.37s wall/Pymunk1.51s, penetration0.008381/0.016758mm,
responses1.13/1.37MB, matching captured design hashes. Seven served browser assets
match disk exactly. Read-only probes leave the current library byte-identical at
SHA256 b681d0f2f86f1d487a3700dd9efd8696215ced3ed276b5594a454b61ff13d458;
no named designs or preset library are written by validation.

Two scientific Plotly PNGs (16-surface overview and actual engine comparison)
and their data ZIP live in ignored exports and are visually verified. They are
not UI screenshots. Browser review was interrupted/unavailable; the user then
explicitly disallowed computer-use, so final live layout/pointer/console review
remains unverified. Actual app-local Start/Stop/restart/reuse is checked at4191;
use the existing Start Kinefold.cmd after shutdown. Canonical physics is NOT
APPLICABLE to this isolated experimental workspace. Publication uses normal
workspace/log checks and hooks; no shared model, dependency or rule changes.

## 2026-10-29 — seeded cell variation and longitudinal grade

Based on main `1a05f43`. Owner requested variation between periodic cells and
physical slope. GPT-6.1 Sol worker implemented app source/tests in the existing
isolated checkout; parent reviewed, integrated and independently checked the
geometry/initial mechanics. No computer-use, browser/native UI automation or GUI
window is used for this task, as the owner requested. Source catalog is unchanged.

Strict optional terrain-v2 adds seed(uint32), variationPercent0–50 and signed
gradePercent−100–100. Existing v1 remains flat/regular and is not silently migrated.
New selections preview seed481/20% variation and the sheet maximum grade as a
declared test envelope. Explicit Apply captures values in input presets and both
engine snapshots. Cell center/width/asymmetry/amplitude use a stateless uint32
mixer keyed by seed/cell/channel; duration does not change earlier cells. A 0%
variation preserves legacy nodes. Three-cell surface/baseline and grade-removed
roughness plots show actual peak/RMS; generated-mesh statistics identify their
complete-cell window, excluding supporting tails/lead. Random peaks may exceed
nominal source estimates. Cross-slope and deformable ground remain unmodeled.

Positive grade rises toward world+x. The full contact chain/tails are inclined;
horizontal terrain translation raises/lowers ground under the fixed-x chassis.
Gravity is still world-down once, and terrain work uses actual ground velocity.
Mounting α is unchanged. Shared initial stance uses r*sqrt(1+grade²), preserving
circular-rim clearance, and a grade-compatible initial normal velocity at the
entered hip rate. Spin starts at zero. Horizontal rail reactions make free-vehicle
normal-load/climbing formulas inapplicable. Native camera bounds exclude far
slope tails. Jump/landing and the prescribed bench ignore retained terrain-v2.

Parent PASS377,736 independent checks across216configs/30initialstances, exact
JS/Python seeded sequences, negative cells, duration prefix, legacy nodes and
piecewise-linear detrended RMS; old12,802 source/v1 checks remain passing. Parent
reran5 variation/7 terrain Python groups,52 terrain DOM assertions/35 Plotly mounts,
33 project groups and55 preset assertions. Worker additionally passed270 parity
cases, old8 contact/9 case groups and energy/preset/comparison/drawing regressions.

Fresh HTTP same-capture±15% grade, seed481/20%, RMS15mm, explicit600mm repeat,
300mm/s,2.6s/dt0.00025/50Hz produces131rows in all4 runs. Both exact generated
contours and design hashes match; max chassis discrepancy0.000550mm uphill and
0.000767mm downhill for the savedα0 fixture. Max penetration<=0.004144mm,
responses1.21–1.28MB, walltimes12.32–12.39s analytical/2.33–2.41s Pymunk.
Read-only checks preserve live library SHA256
b681d0f2f86f1d487a3700dd9efd8696215ced3ed276b5594a454b61ff13d458.
These period/speed values are numerical fixture overrides, not sheet recommendations.

Separateα20/downhill worker cases retain coarse dt0.0005 max heave difference
9.495mm, reducing to3.196mm at0.00025; final energy residuals0.228J/2.230J are
reported rather than treated as physical absorption or tight conservation.
Both engines complete the fixtures. Pure-incline6.5s final-force checks retain
the prior no-epsilon-contact-step regression. No force/penetration guard was weakened.

Scientific Plotly PNG examples and16-surface grade-removed overview are saved in
ignored exports and visually verified. Live UI layout/pointer review is unverified
under the no-computer-use constraint. App-local Start/Stop/restart/reuse, exact
served-asset checks and ordinary workspace/log publication gates apply at4191;
restart using Start Kinefold.cmd. Canonical robot/hardware physics is NOT APPLICABLE.

## 2026-10-29 — Rev2/SO catalog, V4.5 and independent actuator calculator

Based on main `ad62f91`. The owner explicitly requested another agent, a searchable
Pure Motor Rev2/SO Gearbox Index catalog, V4.5 link/wheel masses and a separate
acceleration/jump information calculator. Two GPT-6.1 Sol workers owned isolated
new source/test files; parent owned architecture, integration, profile, independent
source/mechanics audits, documentation and publication. No computer skill,
browser/native UI automation or GUI window was used. The private ChatGPT URL was
unreadable; no transcription or source-chat equation claim is made.

Offline catalog snapshots14 motors/157 exact SO listings from the supplied sheet,
with name-joined Rev2 annular-component estimated rotor inertias and scenario
bounds. All motor speed cells are missing;14 gearbox efficiencies unresolved;
only12 source input inertias exist. Blank remains null. The standalone tab06
supports search/filter, exact-SKU choices, four pinned comparisons, app-folder JSON
exports, reflected inertias, acceleration/speed/stroke times, three editable loss
scenarios, nine base Plotly charts plus pinned comparison and conditional COM
jump height. Conventions remains last as tab07. Candidate settings never apply to
simulation motorConfig. Complete equations/source limitations are in
[actuator-calculator.md](../actuator-calculator.md).

V4.5 keeps original V4 geometry/alpha0/spring and8.75kg chassis, sets m2=m3=1kg,
m6=0.5kg,m5=0, total11.25kg per corner. New tracked portable profile and studio
template preserve V4. Prescribed-height input has explicit10mm C2 transitions;
actual-contact massless-link and old Energy-tab guards remain unchanged. Existing
spring is not retuned. Copied10mm-height/1s tests in both prescribed engines end
at travel limit around0.708s with16rows, rather than claiming duration completion.
The parent also ran both through the actual HTTP APIs. The existing four named
designs remain byte-identical as records; the prior working copy was archived as
a new named design, V4.5 saved and selected through optimistic revisions224→227.
Library before SHA256 b681d0f2f86f1d487a3700dd9efd8696215ced3ed276b5594a454b61ff13d458;
after b580c793d96ce2c3fa912490e1d11f8a3fff11854dd7a065d462cc61482fb511.
Subsequent read-only API tests preserve the new library exactly. Portable V4.5
travels through Git; machine-local ignored libraries are not silently synchronized.

Calculator assumptions: gearbox output drives hip1:1, uniform rods, independent
wheel spin; source rotor J is estimated. Unsourced6000rpm example and missing
efficiency0.9/gear inertia0 omission are explicit editable examples. Low/medium/high
output Coulomb are1/3/8% of usable peak; viscous drag reaches the same fraction at
10rad/s. Constant detent resistance is a worst-case cogging envelope, not actual
conservative periodic cogging. Fixed-hip balance is ideal external assistance;
jump uses all-body gravity and retained spring. N² inertia is reflected once.
The COM apex above takeoff excludes rotor/internal/horizontal energy and assumes
full-stroke release without unilateral liftoff/traction/stop assessment.

Parent PASS4,190 independent catalog/source/component checks and3,081 mechanics
checks over240 fixtures/198 closed-form poses. Source-value mapping covers all
171 records and84 annular components; generalized inertia finite-difference error
<=1.56e-10kg m², J-prime error<=3.56e-10. Worker/new retained suites PASS1,389
catalog assertions and6,152 calculator assertions/57 BASIC chart mounts. Existing
34 project groups,55 preset,712 Energy UI,48 preset UI/20 chart mounts,3,770
dynamic Plotly and185,698 alpha-energy assertions pass. Tab-route expectations
in two retained UI suites were updated for the additive actuator route.

The broad legacy `node verify.cjs` stops on a pre-existing whole-source-HTML hash
mismatch: unchanged source Jon V4 HTML now hashes9fa3528c... instead of recorded
37767388.... Its retained mathematical blocks still exactly hash the recorded
901bd626... and are present verbatim in reference-v4.js. No source/provenance or
test assertion was weakened to hide this existing mismatch. The new independent
mechanics checks and focused affected suites pass; this is not an all-suite pass.

Two overview and all10 actual calculator Plotly PNGs plus full configuration/data,
source/math/API evidence and portable profile are in ignored app exports. The
overview and jump plots were visually checked; a clipped energy label was fixed
before delivery. No UI screenshot claim is made. Actual app-root Stop/Start/reuse
from unrelated cwd and11 exact served assets/actuator route are checked at4191.
Live layout/pointer review remains unverified. Use Start Kinefold.cmd and refresh
the app to load the selected V4.5. Canonical robot/hardware physics is NOT APPLICABLE.


## 2026-10-30 — Automatic V4.5 actuator comparison and finite-link contact

Based on main96c7f56. Three authorized GPT-6.1 Sol workers owned separate
backend, finite-physics and UI files; parent integrated/audited/replayed cases,
fixed native bottom-out detection, added interval acceleration, graded target,
regen final-step cap, source-speed checks and recoverable latest-job pointer.
No Computer skill, GUI/browser automation or live physical profile write.

Tab06 now has Automatic comparison and the retained Inertia quick calculator.
Captured V4.5 defaults: 2m wheel-bottom drop, 2m COM jump above takeoff, 50mm
minimum underbody clearance and separate50mm underside offset; all editable.
Four native bodies/3 pivots/GearJoint/hip stops independently cross-check exact
analytical finite-link mass/COM equations. Old massless branch stays intact;
mixed rod masses, nonzero compound/custom inertias and curved paths stay blocked.
New actuation captures actual delivered torque after speed/current/power/regen
caps with N² motor/gear inertia and editable drag/controllers. Inputs never apply
to Studio motor settings. Source assumptions and limits remain explicit.

HTTP job a52d2ac28caf4bc6968814610af1be29 screened2198pairs and completed12cases
(two pairs x3cases x2engines),228s,dt.000125/3s/50Hz. Original assessments/records
are backed up; final review replayed two native landings after missed stop-event
fix and recomputed all metrics from preserved actual rows. Both80100/AB90-G10
and80100/AEP90-G10 fail landing at compression stop and jump(0.886/0.884m and
0.867/0.865m), pass entered short terrain thresholds; no all-target winner.
Other catalog rows are screens, not dynamic passes. Max source speed violation
fails a case; pointwise impact acceleration is unresolved, output-interval
acceleration is labelled. Native signed combined constraint/numerical accounting
is not physical absorption. Complete equations/assumptions/results/checks are in
[automatic-comparison.md](../automatic-comparison.md).

Parent final7finite,21actuator/source/job,88comparisonUI checks pass, plus affected
catalog/quickcalc/Plotly/energy/project checks. Worker43legacycontact groups pass.
Static finite weights match Jon V4; airborne all-bodyCOM and alpha20/refinement
are checked. Existing broad whole-source HTML provenance mismatch is unchanged.
40PlotlyPNG/full-dataZIP are ignored app exports and native Notion attachments.
No live UI or hardware acceptance is claimed. App-root Start/Stop launchers and
HTTP guard/assets are verified at4191. Library SHA remainsb580c793d96ce2c3fa912490e1d11f8a3fff11854dd7a065d462cc61482fb511.

## 2026-10-30 — Exact saved actuator case playback

Based on mainb5a84ce. Two authorized GPT-6.1 Sol workers built isolated replay
service/player files; parent integrated the saved row selector, read-only02/03
mirrors, recovery/source guards and actual HTTP validation. No Computer skill or
browser/native UI automation. Tab06 filters saved motors/exact gearboxes, then
opens Landing/Jump/Terrain with one shared clock/camera. Missing pairs run only
on explicit request using captured settings. The immutable original batch/table
is preserved; supplemental replay assessments/frames have separate storage.
Native desktop viewer is still a separate live-design path.

Entry modules: comparison-replay.js (actual last-sample player and pure SVG),
comparison-replay-bridge.js (pair/solver-tab handoff and Plotly),
comparison_replay_service.py and comparison_replay_worker.py (owned bounded job,
guarded endpoint, exact payload/source identity, persisted cache). Saved settings
are cloned/frozen, no Studio setters are used, live controls are preserved.
Refresh resumes the existing owned case; monitor failure retains Cancel.
Generator source drift blocks unrun-case regeneration, not exact cached playback.

Final16backend groups with --real run six temporary actual engine cases;212player,
48integration and115automaticUI assertions pass. Three additional cases for
Flipsky6384 170KV Battle Hardened/HTG90-G20 completed through guarded4191HTTP,
151rows/frames per engine, exact matching settings. Original full studylatest
and libraryhash above remain unchanged. Affected dynamicPlotly/energy/project/
preset checks pass; the earlier broad JonHTML provenance mismatch remains open.
Scientific previews3PNG/3GIF and captured-dataZIP are ignored app exports and
native Notion attachments. See automatic-comparison.md for usage, exact API,
limitations and numerical results; use app-root Start/Stop Kinefold.cmd at4191.

## 2026-10-30 — Supplied landing table audit

Owner requested45kg chassis,1/1.5m wheel-bottom falls,alpha0/20 andfull65deg in
bothactual engines. App nowaccepts landingOpenFraction1 (fullte100→tc165) while
preserving2/3defaults. OneGPT-6.1Sol worker owned range/UItests and two stop-event
fixes; parent owned study/inverse-load runner, static-oracle tests, actualruns,
report/Plotly/media/integration/publication. No Computer skill/GUI automation.

Read table-landing-study.md for all inputs/results. Masslessrods, explicit.5kg
wheel,friction.8,ideal jointmotor;45kgchassis means11.25kgpercorner pluswheel.
Springoff versus V4k/p0scaled(11.25/8.75)*cos(alpha),unchangedroute,noextra softstop.
Assisted localupperpassing torqueA/P:1a96.24/96.62,1b144.78/144.78,2a97.008/97.253,
2b145.92/145.92Nm. ABtightstrand atprinted97/146Nm:1a5.721/5.774,1b7.714/7.796,
2a3.221/3.221,2b4.200/4.201kN. These are1msmassless-link inverse-dynamics estimates,
not physical beltshock peaks. Springoffprintedcommandsallbottomout. Rounded97
fails2a atzeroreserve; unrounded97.28162256passesboth atdt.0001. Whole-numbercommon
commands97/145/98/146assisted and137/185/140/189off passboth atdt.0001.

Study exposedanalyticalPGS andplainnativegroove stopimpulsesmissedbyoldposition/
velocitysign events, creatingfalsemotor-onlyarrest. Nowclassify actualstopimpulse;
native rotorwheelkick removedbeforegrooveprojection,finite native stop retained.
Force laws/constraints/tolerances unchanged. Initialfailedcaptures retainedignored;
final240-run evidence usesfixedclassifications.29analytical/case/finite and34native/
case/motor/work groups,35projects,115energy,185698alpha and3study groups pass.
Fouractualstaticruns matchJonAB spanswithin.1N andbodymomentumwithin.001N;10um
poseholding boundacknowledgesnativecoldcontactslop. Priorwhole-sourcehashfailure
unchanged/unclaimed. Case1bdt.00025→.0001 reducesgcompresidual6.17→2.46JA,
8.93→3.56JP;zerostopreservebracketprecision isnotphysicalaccuracy.

18PlotlyPNG,primary/fine/coarserawdata,sources and16portableprofileJSON remain
ignoredappfolders andnativeNotionattachments. Noactiveprofile write;librarySHA
b580c793d96ce2c3fa912490e1d11f8a3fff11854dd7a065d462cc61482fb511 unchanged.
Newenginehashes invalidate unrun generation fromoldercomparison captures bydesign;
exactstoredframes remainhistoricalevidence. Createa freshstudy fornewcomputations.
