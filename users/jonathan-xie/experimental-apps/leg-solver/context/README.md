# Leg Solver context

Owner: Jonathan Xie. Source: Codex user request and explicit mechanical/angle
clarifications, 2026-10-13. Status: v1 analytical kinematics; no hardware acceptance.
Repository base when work started: `3bbe964` on main.

## Model and implementation

The [README](../README.md) and standalone [HTML](../v1-kinematics.html) retain
the exact model, equations and units. Three open nonslipping belts use rotating
carrier constraints. Pulley b is fixed to tibia; d/e is independent of both links.
Theta2 and theta3 point proximally, B→A and P→B, as confirmed by the user.
Wheel and intermediate pulley angles use extension as zero; locked c stays at 0.
Wheel coupling K = 1 - q_ab + q_ef(q_ab - q_cd). Out-of-plane displacement is zero.
Endpoint h is signed; sampled extrema are reported separately.

All production app code is embedded in one HTML file, so it runs offline by opening
the file. No dependencies or server. The Windows launcher opens that adjacent file.
Parameters can be exported/imported as schema `general-vsl/v1-kinematics` JSON;
exports contain all dimensions, endpoint/mounting/phase angles and driven choices.
CSV exports contain degrees/mm and parameter metadata. Browser refresh restores
demo defaults; save parameters explicitly to preserve a study.

## Validation state

`node verify-kinematics.cjs` passes 3,838 mathematical assertions, with both
embedded scripts parsing successfully. The checks cover closed-form straight
travel; three belt constraints across 60 ratio combinations and five poses each;
position/angular derivatives; link lengths; frame invariance; spin cancellation,
including degeneracies; exact belt geometry, continuity and material velocities
at both wraps; invalid inputs and interior extrema.

Actual in-app browser testing of the unchanged static HTML over a temporary
loopback HTTP preview passes: both plots and SVG render; no browser warnings or
errors; all four triplets support a driven dimension with one checkbox selected;
driven L2 updates to 420 mm for q23 = 1.4 and L3 = 300 mm; swap gives L2 = 300,
L3 = 420 and q23 = 0.714285714286; decimal key-by-key input retains 310.5 mm;
mounting-angle slider reaches 30 degrees; numeric phase/mounting changes transform
live displacement; changing extension resets all four displacement zeros;
reversed endpoint order, zero-width range and overlapping pulleys are handled;
spin preset ends at theta5 = theta6 = -65 degrees; cancellation preset ends at
theta5 = -32.5 and theta6 = 0 degrees; pause/play and keyboard pose scrubbing work.
Saved JSON parameters successfully reload after selecting another preset.

Actual CSV export contains 901 finite grid rows for the demo, exact extension
zeros and 435.593224745812 mm endpoint vertical travel. JSON schema and demo
values are verified. A screenshot of the visible desktop interface was inspected.
Browser tests found and fixed decimal typing that discarded the decimal point,
and combined coincident local/global axis labels at alpha = 0.

Direct file-URL browser verification was blocked by the browser tool's protocol
policy (HTTP/HTTPS only). No bypass was attempted. The app has no fetched resources,
module imports, packages or network calls; direct offline opening and the .cmd
launcher remain untested through this browser tool. Mobile/responsive rendering
has not been independently exercised. These limits do not affect the completed
static HTTP browser checks. The local preview is temporary; normal user operation
is by opening the HTML file, without a server.

Final repository checks pass: `python tools/check_entry.py --base origin/main`
and the `--require-passed` variant both report 524 files, 7 changed paths,
scope `workspace`; `python tools/physics_gate.py --base origin/main` reports
canonical robot physics NOT APPLICABLE; `git diff --check` passes. Six local
Markdown links across the two app documents are verified. The requested
repository copy matches the delivered files byte for byte.

Initial repository checks exposed this clone's CRLF conversion of index-LF files:
the append-only log check failed and raw-byte scope detection incorrectly invoked
the unavailable canonical-robot gate. Normalizing 381 index-LF text checkouts
and the contribution log to LF, with local core.autocrlf=false, preserves all text
contents and the full previous Git log as an exact byte prefix. The actual Git
diff remains the seven intended member/log paths. All final checks above pass;
no enforcement or canonical model was changed. No commit or push was made.

## Scope and next work

Only member-app local files are requested; no publication is requested.
Keep the v1 kinematics model separate from a future kinetic solver.
Resolve forces, spring placement/law, mass/inertias, actuator coordinates,
wheel/terrain contact and damping before deriving kinetics. Do not equate the
free wheel rim arc with no-slip rolling distance. Manufacturing tooth pitch,
wrap, belt tension, interference and 3D shaft/bearing packaging remain unverified.
