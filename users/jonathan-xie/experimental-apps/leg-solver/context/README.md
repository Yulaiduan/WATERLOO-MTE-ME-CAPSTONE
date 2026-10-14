# Leg Solver context

## Headline maxima — 2026-10-14

User's final steering fixes alpha at its current value and searches all theta2 ×
beta combinations inside the master bounds. A second equal-size headline row
shows signed torque extrema, total tight Tab/side and absolute dz, plus peak
poses and numerical search gap. Changing alpha recalculates; theta/beta playback
inside unchanged bounds reuses cached results. Alpha-window endpoints are ignored.
Beta extrema are analytic; theta uses conservative second-derivative interval
bounds and 0.001-unit tolerance, with explicit estimate/gap on iteration limit.

New verify-global-maxima.cjs passes 29,863 assertions. Existing quasi-static
16,044 assertions pass; core solver blocks and v1 are unchanged. Browser checks
confirm eight headline cards, matching 19px current/global values, torque signs,
mode and bound changes, theta/beta cache stability, alpha-window independence,
recalculation on current alpha and fixed-alpha peak poses. Logs are empty and
the preview is retained outside Git. Numerical tests include both driving force
conventions, actual FBD parity, attained poses, domain bound checks, interior
beta extrema, zero-width windows, preloads, negative travel and estimate fallback.
A test fixture initially expected a sinusoid maximum outside its beta interval;
correcting the force direction puts the intended maximum inside the interval.
No tolerance or equilibrium requirement was weakened. Local save only, no push.

## Collapsible results — 2026-10-13

User requested collapse arrows from FBDs onward. V2 now has 15 expanded-by-default
disclosures: full FBD section, five individual FBDs, four loading rows and five
final result cards. Buttons expose expanded state/control IDs and support keyboard
Enter/Space. DOM stays mounted while hidden; the torque display checkbox remains
available when FBDs are collapsed. Both embedded solver blocks and v1 are unchanged.
All 15 controls passed browser collapse/reopen checks; changing theta while the
FBD block was hidden restored its current 140-degree pose. Independent cards and
Enter/Space were verified, all 21 SVGs remain, and browser warning/error logs are
empty. All embedded scripts parse. No numerical model tests were added for this
visibility-only change. Local app/output/ZIP updated; no commit/push or hosting.

## V2 control and height-plot refinements — 2026-10-13

User requested eight direct v2 changes. V1 HTML is unchanged byte-for-byte
(SHA256 5D338B33A1CC80C66DC85E2F1B574F414BBE96550E8A84428CFECBACCAA502A1).
Local work only; no commit/push or hosting. Current usage is in [v2-model](../v2-model.md).

- θ₂ has min/max/current fields synced with the extension/compression controls.
  α/β share a row; global Fy/Fz and wheel Fn/Ft are paired columns with exactly
  one driving selection. Switching preserves the force vector. Derived controls
  fade/disable; only one independent master plays at a time. Components are
  signed, including outward Fn; unilateral contact remains outside scope.
- Four headline cards show τ₂, τ₄, total tight Tab + upper/lower (balanced if
  equal), and dz. Separate diagram toggles show motor couples and the driving
  force decomposition. Total mass remains available in the sidebar.
- FBD order is 2/3 then 4/5/6. Twelve loading graphs use theta2, dz, beta and
  alpha in four rows. The bottom row is angle/theta2, angle/dz, displacement/theta2.
  Working dz axes include 0/hz and interior extrema; angle/dz covers theta90..180,
  including negative travel. Parametric paths preserve repeated heights; darker
  branches identify valid theta poses. Exact fractional endpoints are included.
- JSON schema stays additive-compatible, saving loadMode, six non-theta windows
  and optional view settings. Legacy v2 JSON loads with nt driving. CSV now has
  four sweeps, 31 columns, explicit x units, resolved force components and dz.

Validation: 16,044 quasi-static assertions and 3,853 kinematic assertions pass;
all embedded scripts parse. Existing force/moment/virtual-work residual limits
remain 9.722e-13 N / 3.624e-13 Nm / 3.979e-13 Nm. Added tests compare both driving
conventions over 91 beta values, including negative Fn, and check force norm,
global-sweep invariance, exact fractional endpoints, reversing/negative travel,
two poses at dz=0 and a constant-height display domain.

Actual HTTP browser checks verify editable theta bounds/current, four headlines,
no torque jump on mode switch, conversion during beta changes, disabled derived
controls, exclusive playback, all three arrow toggles, FBD order, twelve sweep
SVGs and three bottom plots. JSON saved/restored current mode and legacy settings;
actual CSV has 1,448 rows / 31 columns across four sweeps, audited for finite
values, conversions, fixed global loads and dz units/reference/boundaries. Desktop
layout and 390px responsive structure were inspected; viewport reset afterward.
Browser warnings/errors are empty. No dynamics/hardware/rolling/contact-feasibility
claim is added; direct file opening and Windows launchers remain manual, with
identical standalone HTML tested over HTTP. Interior extrema/inverses are sampled.

Final repository checks pass: 528 files, 10 changed paths, workspace scope;
structure/require-passed succeeds, scoped physics is NOT APPLICABLE and whitespace
checks pass. App Markdown links and all nine delivery/ZIP files are verified.
The first whitespace check caught CRLF in three rewritten documents; normalizing
only owned app text to LF resolves it without changing content or Git settings.

Construction: an initial task-local helper used the Windows default text encoding
and failed before assembling the refinements; rerun with explicit UTF-8 succeeded.
An old test rejected signed Fn and was revised to reject nonfinite Fn and exercise
signed-convention equivalence instead. No tolerance or equilibrium check was weakened.

## Original V2 handoff (historical) — 2026-10-13

Source: follow-up user request and explicit clarifications. Repository base:
`d45d01a` on main. The requested local HTML workflow continues; no publication
is requested. [V2 model](../v2-model.md) is the current model/usage reference.
The separate v1 HTML remains functional, with the requested two travel angles.

- Contact naming: C is wheel centre, P contact patch; beta clockwise from global
  -z toward front/-y. Positive Ft produces positive CCW wheel moment. Displacement
  and gamma outputs in v2 track C; contact coordinates/path are shown separately.
- Gravity is global -z; masses can be zero. Fixed-A m1 contributes to chassis
  support and mT, not motor torque. Moving masses are at the requested centres.
  Rod/rim inertias are recorded (effective rim radius r5I is explicit), never used
  to introduce dynamics. Contact forces stay prescribed independently of masses.
- gamma_uv = atan2(du,dv), gamma_yz = atan2(dy,dz), degrees -180..180, undefined
  at zero displacement; readout rows 3/6 show live/final values; five angle curves
  render by default and break at undefined poses/wraps. V1 keeps its original
  endpoint naming while v2 labels C/P explicitly.
- Exact tangent span forces and the specified fixed-slack-preload rule determine
  all pin reactions. Fw is complete wheel-on-tibia reaction, including contact,
  wheel gravity and e/f belt pull. Motor holding torques satisfy both individual
  FBD equilibrium and independent virtual work. Fij acts from i onto j.
- Five masters are theta2, alpha, beta, Fn, Ft; only one auto-plays. Four new
  windows are editable, alpha domain expanded to 0..45. The UI includes all five
  FBDs, total mass, recorded inertias, torque arrows/cards, belt-span highlighting,
  contact force arrows and nine sweeps (theta2/beta/alpha × torque/tension/forces),
  followed by original kinematic plots and envelope/coupling outputs.

### V2 verification

`node verify-kinematics.cjs`: PASS, 3,853 assertions and both v1 script parses.
`node verify-quasi-static.cjs`: PASS, 13,483 assertions and all v2 script parses;
240 varied geometry/mass/load/pose cases, all FBD force/moment balances, exact
tangent moments and tension allocation, reaction pairs, whole-system support,
contact directions, independent finite-difference virtual work, preload/m1 torque
invariance and fast/full sweep parity. Maximum force residual 9.722e-13 N, moment
3.624e-13 Nm and analytic virtual-work discrepancy 3.979e-13 Nm. These are numerical
consistency checks, not hardware tests.

Actual browser testing of the same standalone HTML over loopback HTTP verifies
v1's six displacement/angle rows and five angle curves; v2's five FBDs, nine sweep
graphs in three desktop columns, finite SVG coordinates, zero/invalid geometry
states, driven L2 = 420 for q23 = 1.4, all five mutually exclusive master controls,
fixed values of non-playing masters, alpha 45-degree endpoint, custom beta 20..60
window, invalid windows, negative Ft, preloads, absolute torque dash styling,
mass/gravity updates and complete parameter/pose JSON restoration. Desktop at
1600px and the default narrow 588px layout were visually inspected; viewport
override is reset after testing. Browser warning/error logs are empty.

Actual v2 CSV export has 1,083 rows over three sweeps and 27 columns. Finite numeric
values, exact reference gamma blanks, -2 Nm drive torque for the saved 20 N /100 mm
rim example with unit ratios, and 10 N slack-side preloads are independently
verified. JSON saved/restored alpha 15, beta 30, Fn 120, Ft 20, link masses, preloads
and theta2 126 degrees. V2 accepts v1 parameter schema with explicit new defaults.

During construction, tests caught a public belt-centre property accidentally
renamed during v2 point migration; it was corrected. Browser checks caught gamma
legend entries without initial curve visibility, a missing alpha caption, and
master bound/current boxes that waited on change rather than updating on input;
all are corrected and verified. Deferred sweep redraw now also completes after
manual scrubbing stops. These failures are retained here rather than treated as
passing original runs.

Direct file-URL/Windows launcher execution is not claimed as browser-verified;
the browser tool permits HTTP/HTTPS only, as recorded in the original handoff.
The delivered HTML has no imports/fetched resources and is intended for direct
manual opening. No dynamics, spring response, no-slip ground contact, friction,
hardware feasibility or canonical-robot validation is claimed. Curves use finite
sampling; arrow size/opacity cap for readability. New model notes distinguish
signed torque from total tight-span tension and fixed carrier-side U/L labels.

### Repository validation

Both `python tools/check_entry.py --base origin/main` and its `--require-passed`
variant pass: 528 files, 10 changed paths, scope workspace. The scoped
`python tools/physics_gate.py --base origin/main` reports canonical robot physics
NOT APPLICABLE. `git diff --check` passes; only the ten intended app/index/log
paths differ. Fourteen local app Markdown links are verified. Both actual target
HTML files and all delivery copies match their checked task files byte for byte.
The original envelope now also updates while alpha auto-plays; browser checks
confirm h_y = 217.80 mm at alpha30 and changing live values during playback.
Updated v1 CSV has 901 rows /11columns, both added gamma columns, correct extension
blanks and final gamma_yz =15 for alpha15. The ZIP contains all nine app files.
No commit or push was made.

## Historical v1 handoff

Owner: Jonathan Xie. Source: Codex user request and explicit mechanical/angle
clarifications, 2026-10-13. Status: v1 kinematics and v2 quasi-static analysis; no hardware acceptance.
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
