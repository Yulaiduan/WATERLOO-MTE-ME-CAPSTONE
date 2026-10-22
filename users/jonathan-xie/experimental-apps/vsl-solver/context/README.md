# VSL Solver context

## Flexible spring fit and physical hip torque signs — 2026-10-21

All seven spring inputs now have **Driving** checkboxes: checked values are
held; unchecked values are fitted. Defaults hold k,S_v,r_s,ν and fit r_h,p₀,S_u.
The single Fit button minimizes peak |τ₂| over working θ₂ at current α/β/loads,
with a result/warning box. Zero through seven fitted variables are supported;
old point-preload and textbook buttons are removed. Spring/mass descriptions
are compact; only φ₀ remains in the sidebar angle controls. θ₂ master bounds
are labeled θ₂ᵉ and θ₂ᶜ.

Hip signs are now **τ₂=−τG−τS**, all positive CCW on Link2. Only τG's definition
changes; actual motor torque is unchanged. τ₄ stays CCW on its own drive shaft.
Saved configurations migrate the gravity sign and preserve all physical values;
new checkbox selections persist through JSON, row Save/Load and Excel.
The usual8.75kg/10mm-idler fit now gives max|τ₂|≈0.023771Nm over100–165°.
This is a bounded sampled numerical minimum, not a proof of global optimality.
See [fit details](../v4/v4-model.md) and [verification](../v4/v4-flex-fit-verification.json).


## Current release — 2026-10-21

App renamed leg-solver → vsl-solver; each version lives in its own folder.
Use [the root launcher](../Open%20VSL%20Solver%20v4.cmd) for V4 and Excel sync.
See [current setup/defaults/library](../README.md). q_dc=rd/rc, q_fe=rf/re;
rw200mm, total mass8.75kg. Mass/g changes preserve active force ×g. Automatic
maximum-required ζ uses all working travel; positive rotates CW, negative stays
visually horizontal. P₀ is extrapolated at90° if wrap is absent there, but a
pin inside/on the finite pulley at90° remains invalid (explicit user choice).
V4 library has immutable row snapshots and explicit XLSX save/load; a local
stdlib Python bridge is required for automatic filesystem access. Browser
drafts protect unsaved edits; Excel revisions protect concurrent saves.

Earlier sections below are historical. In particular their13kg default and
fixed-horizontal-exit routing descriptions are superseded by this release.


Pending shared-checkout housekeeping: [publish the intended app AGENTS.md](2026-10-19-agent-entry-note.md).

## V4 textbook10mm and clarified compensation — 2026-10-18

This supersedes the percentage description below: user wants effective mg
compensation error100*(Feq/(m_total*g)-1), not tau2/abs(tauG). Separate linear
raw-tau2 and compensation plots; latter spans at least±10%, with0%=1mg.
Headline brackets use compensation error at same/torque-peak pose. Zero mass
or vertical Jacobian is undefined; changing prescribed Fz does not change it.

Default/Reset/Textbook uses13kg chassis, zero moving masses,300/300mm,qab2,
alpha=phi0=nu=beta=0,Fy0,Fz127.53N,k8,Sv100,rs10 andtheta100–165deg.
Calculated Su7.1579230735mm,rh89.416035166mm,p0149.918334501N yield
pe195.954393852N,maxFs963.065307336N,95.888864mm working spring stroke,
max compensation error0.06208975% and peak motor0.037294803Nm.
All nominal spring drivers default off. [Textbook report](../v4/v4-textbook.md)
and complete JSON retain the dense independent fit and plots;0.1mm study remains.

The new dependency-free finite fit button solves rh/Su/p0 while holding
k/Sv/rs/nu/leg geometry, disables nominal drivers and reports sampled error.
Affine Chebyshev p0 elimination plus2D multistart Nelder-Mead uses181 objective
angles and6501 verification poses; this case about0.06219%, near SciPy's denser
reference0.06209%. No exact finite-radius identity/global optimum proof claimed.
Refit after changes. Literal90deg guard remains; point rh95.6475/Su0 is invalid
with a10mm pulley, but the joint fit repairs it without reinterpreting p0.

91,128 checks pass including both-radius fit controls/held parameters, actual
textbook solver and compensation semantics. Browser verifies fit from invalid
draft geometry, zero mass, Fz-independent support, textbook reset, collapse,
24 finite SVGs and empty warning/error logs. Physical spring/tolerance/contact
behavior remains unvalidated. V1-V3 unchanged; local save only, no commit/push.

## V4 applied CCW signs and tuning — 2026-10-18

This revision supersedes the V4 displayed-demand signs below: tauG=V2 holding
motor, tauS=-Fs*cprime/1000 is the physical spring couple, tau2=tauG-tauS is
the applied CCW motor, and tau2Applied=tau2. dU/dtheta=-tauS. Physical motor,
FBD forces and frame reactions are unchanged. Preload raises normal-range tau2
by delta(p0)*cprime/1000, not a uniform shift. Tau4 remains applied CCW.

The user confirmed tuning assumptions13kg chassis, no moving masses, equal300mm
links,qab2,alpha=phi0=nu=0,Fz=127.53N,Fy=beta=0,k8,Sv100,rs0.1 and100–165deg.
[Tuning report](../v4/v4-tuning.md) explains the missing matching-p0 condition and
finite wrap correction. Point rule rh95.6475,p034.82,Su0 yields0.800255% max
error; fitted Su0.0495235514,rh95.5636321098,p036.3389792098 yields0.000392529%
and0.000290116Nm max residual. Load the fitted JSON with all spring drivers off;
enforcing the nominal point product would overwrite its correction.

Geometry/support card now collapses. Right graph is signed motor torque (linear
Nm) and signed100*tau2/abs(tauG) (independent linear percent axis); singularity
is undefined. Headline percentages use the same pose, including the torque-peak
pose for global tau2. Tiny results retain significant digits. New JSON includes
torqueConvention=applied-ccw; old mechanical parameters keep their physical meaning.

83,803 numerical assertions and four independent65001-angle fitting sweeps pass,
including6501 actual embedded-model samples per case, applied signs and preload
slope. Production CSV handler capture1446x43 preserves residual identity below
9.46e-13Nm and now tau2=applied. Actual browser verifies collapse/reopen, preload
rise, preset import, tiny headline values, zero-gravity percent, expanded/clamped
linear graph,23 finite SVGs and empty warning/error logs. Local save only;
V1/V2/V3 byte-preserved. No hardware tolerance/rating/clearance claim.

## V4 finite hip pulley — 2026-10-18

The owner selected one small fixed idler at local S and a remote spring, with
nu=Su=0 defaults, literal p0=Fs(90 degrees), theta2e=100 degrees. Input rows:
k/rh/Sv with exclusive optional driver; rs/p0; nu/Su. Total mass drives the
nominal k*rh*Sv=2*m_total*g*L2*cos(alpha) relation. L2 is necessary for units;
arbitrary ratio/moving mass/load settings still use full quasi-static equations.

See [v4-model.md](../v4/v4-model.md) for tangent choice, continuous clockwise wrap,
payout, unilateral tension, energy and complete-frame reactions. tau2=tauG-tauS,
physical applied motor=-tau2; tau4 unchanged. Point-pulley exact balance additionally
requires p0=k*abs(Sv-rh). Finite rs changes the actual curve. The user explicitly
chose to flag invalid 90-degree reference geometry, rather than extrapolate p0.

V4 adds current/global Fs and pe, force xg boxes, master-domain clamping default
on and expanded theta default off. Clamping wins over expansion. V4 saves nullable
driver and graph flags; V1/V2/V3 imports disable the new spring. Existing versions
are byte-preserved. The removed r5,I was unused by this static model.

57,524 assertions pass over600 varied poses and24 global-bound cases, including
independent cable/energy derivatives and complete FBD/frame force/moment balance.
Actual browser verifies row layout, zero/exclusive drivers, force multiples,
domains, literal-reference failure/recovery, save/reload, migration,23 finite SVGs
and empty warning/error logs. Actual CSV1446x43 has residual identity below
9.60e-13 Nm. The manual offline launcher is provided; automated QA used identical
HTML on temporary HTTP. Local save only; no commit/push or hardware validation.

## V3 hip tension horn — 2026-10-17

User selected the compact direct hip tension horn; do not reintroduce bulky pulley
routes. S is global y/z relative to hip A; the rigid horn points at theta2+eta-alpha.
One tension spring uses k*max(0,ell-ell0+p). All definitions/defaults/derivations
are in [v3-model](../v3/v3-model.md). V1/V2 remain byte-identical.

V3's signed tau2 is remaining load demand tauG-tauS; applied CCW motor=-tau2.
TauG=-V2 holding torque; tauS=dU/dtheta2. The actual femur FBD includes spring
force at D and the changed hip reaction. Tau4/belt loads retain their prior model.
Allowed theta2 motion is 90–270°. The master checkbox switches full-domain
theta/height graphs only; working animation/envelope/headline bounds remain
independent. Support graph always spans 90–270°, using symmetric-log scaling
and undefined zero-Jacobian endpoints. V3 JSON/CSV include added fields;
legacy V1/V2 imports disable the spring and preserve legacy nt load-mode defaults.

Sample A has Sy=94.62059, Sz=61.04114, r_h=63.02554 mm, eta=-34.04727°,
ell0=54.99222 mm, p=0, k=13.24787 N/mm and 98.1 N upward wheel force.
100–165° support is 0.977968–1.022031 mg; max residual 1.25254 Nm. A denser
sweep corrected the old coarse minimum by about 1.2e-6 in support ratio.
Spring reverses torque near 246.874°; full-range max residual ~25.159 Nm near
268.07°, peak tension ~1.598 kN. Sample B rotates S clockwise20 and scales k
by cos20; changing alpha alone holds S fixed and does not retain that fit.

28,616 V3 assertions pass: 450 varied poses, FBD/virtual-work/energy checks,
spring-off parity, slack and 14 bounded peak searches. V1/V2 regressions pass
3,853/16,044/29,863 assertions. Actual browser checks pass 270° inputs,
180/270 graph/height domains, A/B, preload, spring off/slack, V3 save/reload,
legacy load migration, all23 finite SVGs, and CSV1444 rows/37 columns with
residual identity to1.01e-12 Nm and exact applied-motor sign. Browser logs empty.
The first dense-fit assertion revealed the previous coarse sampling minimum;
the corrected expectation uses the unchanged parameters on a finer grid.

Regenerate dense data/summary with `node verify-spring.cjs --output` and figures
with `python plot-v3-sample.py` (NumPy/Matplotlib). Dense CSV is ignored locally;
retained figures/JSON are small. Local-only save; no commit/push or hosting.
The manual offline launcher is provided; browser verification used identical
HTML over temporary loopback HTTP, not default-browser file-launch automation.
Root checkout was clean and fast-forwarded to fetched3908c3b before saving.
No hardware spring travel/rating/damping or canonical robot validation claimed.



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
Local work only; no commit/push or hosting. Current usage is in [v2-model](../v2/v2-model.md).

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
is requested. [V2 model](../v2/v2-model.md) is the current model/usage reference.
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

The [README](../README.md) and standalone [HTML](../v1/v1-kinematics.html) retain
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


## Support chart axes — 2026-10-22

The V4 effective support error graph now fits its finite sampled min/max with
8% padding, without the old ±10% floor. Left ticks are signed Δkg = Feq/g −
m_total; right ticks show the same error in percent. Negative kg means deficient
spring support relative to the total target weight. Hover shows both units;
zero-weight/Jacobian cases remain undefined. Raw torque and saved designs are unchanged.
