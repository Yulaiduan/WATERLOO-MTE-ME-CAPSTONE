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
