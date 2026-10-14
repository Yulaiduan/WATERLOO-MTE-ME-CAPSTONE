# Validation record

Author: Andy Zhang with Codex. Updated: 2026-10-12. Status: locally checked member experiment, not canonical robot or hardware validation.

## Design rejected as impossible,2026-10-12

The user marked the dual-rope invertible pulley design **IMPOSSIBLE**. Earlier
passing numerical/browser/native checks remain evidence about the retained
idealized simulator only. They are not a physical-feasibility approval and do
not override this status. The symmetric knee bellcrank is a separate experiment.
This update changes status text and documentation only; it does not change
mechanics, integration, profiles, units or recorded values. Fresh run/preview
scope text carries the historical-model label, and old records remain intact.
Current label checks are recorded in the latest root contribution entry;
physics suites are not rerun for this status-only update.

## User-requested rollback of unloaded contraction,2026-10-11

The user withdrew the1ecff9f correction. Mechanics/native code and controls are
restored to the previously validated7bbbceb state: phi±delta anchors,
phi=pi inventory reference,10mm preload,120mm rod and signed gravity calibration.
The0.2mm gap, knee-rim wrap,45deg start and±80deg actual stops remain.
Browser session migration removes the temporary neutral marker and restores
only the reverted demo values, preserving unrelated input settings. The
contribution log and saved runs/JSON stay intact. Temporary folded-neutral
exports may be inspected as original recordings; rerunning that retired
configuration requires its historical Git version.

Rollback checks pass23 scoped Python tests and63 JavaScript tests, plus the
actual inversion browser workflow with folded-session migration, both flips,
Plotly/JSON/library/native request envelopes and matched model comparison.
Core/native/library source is byte-identical to7bbbceb; native windows were
not rerun for this restoration. Actual launcher start/restart/reuse passes at
4186 from an unrelated directory. The in-app preview is refreshed and run.
Publication results are recorded in the latest root contribution entry. Historical counts/results below describe7bbbceb.

## Current tight, wrapped, knee-right demo, 2026-10-11

The latest user clarification supersedes the no-wrap interpretation. Current
central_wrap uses the tight centre channel, roller tangents and knee-rim arcs
to the ±5° attachments. Every straight span clears the knee disk; wrap length
and ±R angular derivative participate in cap travel, tension and actual force
sites. A visible attachment can lift off the rim naturally. Earlier central_face
and outer_rim profiles/recorded frames remain available without rewriting data.

Current editable defaults: 30 mm knee drum, 0.2 mm ideal roller gap, ±0.02 mm
cap eyes, |θ|=45° start and ±80° real angle stops. This drum fits the existing
120 mm coil/rod and 100 mm rod-eye mount. The old40mm drum exhausts that mount's
travel with wrapping and is explicitly rejected. Maximum recorded compression
is94.761mm, leaving25.239mm coil length. Calibrated k is10848.294N/m. Cable lead
angle stays below0.244°, and guide error below3.35e-9rad at400 iterations.

All 23 scoped Python tests pass (inversion, angle_stops, replacement_suspension,
setup_preview). Coverage includes actual rim tangents/arcs, disk clearance,
inventory/slack, force-site virtual work, energy gradients, cap/tension
projection, invalid travel, old route reproduction, both ground flips,
knee-right bounds and independent rigid-stop impact/hold/release/energy.
All63 JavaScript tests pass. The actual inversion browser suite passes wrapped
main/detail drawings, tight gap, both presets, ten Plotly charts, JSON/library,
current native envelope and matching fixed-J1 comparison. Both actual desktop
windows pass4001 steps with five constraints, every-step knee-right/bound checks
and graceful exit0. In-app preview and actual run are checked; launcher
start/stop/restart/reuse passes from C:/Windows at4186. Raw evidence is ignored.

| Dual-rope Pymunk step (ms) | First wheel-below (s) | Angle at 1 s (°) |
| --- | --- | --- |
| .5 | .357500 | 44.187 |
| .25 | .360500 | 42.779 |
| .125 | .360750 | 42.487 |

Reversing the normal-start torque reaches wheel-above at .24175s dual/.23650s
bellcrank with default0.25ms steps; the knee stays right. The unchanged bellcrank
wheel-below time is .39725s. Matched fixed-J1 half-second max absolute angle
deltas are1.38600° dual/.78804° bellcrank through rigid impacts; mathematical
impact losses307.262/301.274J and energy residuals4.62e-4/1.13e-5J. These cases
retain their actual impact error, rather than claiming the low-load .1° budget.
Stop peaks remain step dependent; ideal mathematical impacts have no finite
instantaneous peak. Pymunk reports averaged constraint impulse/dt.

The earlier100-iteration guide failure and subsequent400-iteration repair are
recorded below. The latest wrap correction also required a feasible demo drum
size; infeasible travel is not clipped or silently ignored. Old recordings do
not gain fabricated new channels. Cable diameter/fit, winding/groove history,
rope crossing, stop compliance, actuator ratings and3Dclearance are unverified.
Canonical robot physics is NOT APPLICABLE to this isolated member workspace.

## Initial tight-gap/no-wrap bounded check, 2026-10-11 (superseded by rim-wrap clarification)

Current defaults use a 1 mm clear roller gap, ±0.1 mm cap eyes, |θ|=45° start
and editable ±80° angle stops. Both mechanisms keep `x_knee-x_hip>0` while the
wheel moves above/below the chassis. Pymunk has an actual RotaryLimitJoint,
five total constraints, recorded stop impulse/dt and no clipped poses.
Independent SciPy uses unilateral zero-restitution stop events, impact energy
loss and release when free acceleration points inward. Its continuous holding
torque is distinct from an ideal impact impulse or Pymunk's averaged loads.

All 22 scoped Python tests pass: inversion, angle_stops, replacement_suspension
and setup_preview. They retain force/work and fixed-J1 energy/refinement checks,
and add actual right-side geometry, tight lead alignment, stop load, invalid
initial pose, impact/hold/release including zero-force rest without chatter,
and unrestricted historical reproduction. All 63 JavaScript tests pass.
The actual inversion browser workflow passes: 1 mm gap, −45° initial pose,
stop indicators, ten Plotly charts, all recorded knees on the right, no rim
wrap, both preset flips, JSON/library/native routing and matched fixed-J1 runs.
Actual desktop native checks pass both 4001-step windows with five constraints,
owned handles, every-step knee-right/angle checks and graceful exit0.
Launcher start/stop/restart/reuse passes from C:/Windows at4186. The user's
in-app session is migrated, visually inspected and run with its unrelated
dimensions/input settings preserved. Generated files remain ignored.

Adding stop impacts initially exceeded the old 1e-8 rad guide-error budget at
100 iterations. Iteration checks at200/300 improved error but still missed the
budget; the default400 passes without loosening it. The current dual-rope
0.25 ms run has maximum guide error3.49e-9 rad and cable lead angle1.026°.
The tighter gap is editable and stays fixed when roller radius changes.

| Dual-rope Pymunk step (ms) | First wheel-below (s) | Angle at 1 s (°) |
| --- | --- | --- |
| .5 | .339500 | 41.348 |
| .25 | .341750 | 40.465 |
| .125 | .341625 | 40.287 |

At the default0.25ms, bellcrank reaches wheel-below at .39725s. Reversing the
normal-start torque reaches wheel-above at .23375s dual/.23650s bellcrank;
both retain a positive knee-right margin. This is a bounded contact demo,
not a full revolution or a target-holding controller. Small numerical stop
overshoot and timestep-dependent impulse peaks remain visible in solver data.
Invalid runs crossing to the left fail rather than being cosmetically clipped.

In a separate matched fixed-J1 half-second case, max absolute Pymunk-minus-
SciPy angle differences are1.31332° dual/.78804° bellcrank through impacts.
Math impact losses are310.685/301.274J and energy residuals2.17e-4/1.13e-5J.
These high-torque rigid-stop cases do not inherit the low-load .1° refinement
claim. Pymunk's mechanical_energy_minus_work_J includes unisolated constraint
losses; it is not labeled a closed energy-error ledger with stops enabled.

Old saved profiles without stop metadata explicitly reproduce unrestricted
angles, and their original records/frames stay unchanged. Current session
migration updates the requested roller/pose settings and old default solver
iteration count. Cable diameter/fit, stop material/compliance, actual actuator
ratings, 3D packaging and whole-vehicle self-righting remain unverified.
Canonical physics is NOT APPLICABLE to this member experiment.

## Central feeds and knee-face anchors, 2026-10-11

User correction supersedes the initial outside-wrap prototype below: both ropes
feed between the two rollers, which guide outward flare to the actual ±5° knee
face anchors. The current route has no knee-rim arc. Main preview, enlarged
close-up and live native drawing use the same full cable inventory geometry.
Free central spans can lose roller contact; either roller can guide an outward
flare. Cap travel is solved rather than approximated by drum payout, and active
cable tension is cap force divided by the incoming lead cosine.

All 18 scoped Python tests pass (inversion, replacement_suspension,
setup_preview), including path inventory/slack, inside-gap eyes, absence of
drum arcs, roller contact, force-site virtual work and energy gradients across
the angular sweep away from exact handoff ties. Explicit outer_rim reproduction
is retained. All 63 JavaScript tests pass, including non-mutating saved-profile
route resolution. The real inversion browser workflow passes: actual ground
flip, central lead metadata, no knee arc in any recorded frame, close-up with
both rollers, both presets, JSON/library/Math comparison and native routing.
Actual native desktop checks pass both 4001-step windows with graceful exit0.
The project-local CMD start/stop/restart/reuse passes from C:/Windows at4186.
Current in-app preview shows central routing while retaining remembered numbers.

Default dual-rope calibration is now 7882.99 N/m. The 100 N m / 240 ms pulse
still flips with actual floor contact. Current dual-rope refinement gave:

| Step (ms) | First flip (s) | Angle at 1 s (°) | Maximum sampled wheel penetration (mm) |
| --- | --- | --- | --- |
| .5 | .316000 | 100.236 | 1.281 |
| .25 | .316750 | 78.066 | .179 |
| .125 | .316875 | 59.588 | .669 |

First flip time refines, but the later undamped impact/rebound trajectory has
not converged well at these three steps. Do not infer quantitative post-impact
angle or force-peak accuracy from this contact demo. The separate fixed-J1
SciPy comparison retains its tested energy/refinement limits. No target pose
is held or frozen. The bellcrank mechanism/equations are unchanged.

Pre-correction saved profiles reproduce the old outer route explicitly through
the library/import/native bridge; original JSON/frames are preserved. Fresh
defaults/session edits use central_face. Direct API reproduction of an old
profile requires explicit outer_rim and its original dimensions. An initial
test edit had an indentation syntax error, corrected before the passing rerun.
No axle/3D/groove/rope-crossing, hardware or canonical validation is claimed.
Canonical physics is NOT APPLICABLE to this isolated member workspace.

## Initial outer-route inversion prototype, 2026-10-11 (superseded)

The [new study](invertible-suspension.md) implements actual ±5° knee rope
attachments, two small routing pulleys and a single shared compression cap,
plus a symmetric knee bellcrank with its femur attachment 50 mm from J1.
Ground-mode Pymunk applies femur torque with actual wheel/chassis contacts;
matched independent SciPy comparisons hold J1 and omit the floor in both models.
Chassis pitch is held and self-collision is excluded for staggered lateral planes.

- All 62 JavaScript tests pass, including portable inversion profile/run records,
  explicit units and distinct comparison family. All 16 scoped Python tests pass
  in `test_inversion`, `test_replacement_suspension` and `test_setup_preview`.
  They check actual attachment geometry, one loaded rope/common cap, spring
  energy gradients, force-site virtual work, symmetric energy/torque, nonzero
  preloaded dead-centre endpoint force, initial zero-step preview and both real
  ground flips. Fixed-J1 SciPy energy residual is below .001 J; Pymunk final
  angle error refines below .1° at .125 ms in the tested low-load cases.
- Five actual browser suites pass: `verify_inversion_ui.cjs`,
  `verify_motion_lab.cjs`, `verify_suspension_architecture_ui.cjs`,
  `verify_transmission_memory_ui.cjs` and `verify_comparison_ui.cjs`.
  They cover three physical pulley symbols, red/blue handoff, moving shared cap,
  both ground flips, 50 mm bellcrank mount, Plotly, JSON/library/comparison,
  preserved original bench, tab memory and current-edit native launch routing.
  Browser native endpoint calls are mocked; the desktop tests below are separate.
- `scripts/verify_inversion_native.py` passes both actual desktop Pygame/Pymunk
  windows: 4001 advancing steps each, four constraints, eight shapes for dual
  rope and five for bellcrank, owned window handles and graceful exit code zero.
  Native snapshots/state/logs and browser recordings remain ignored artifacts.
- The app-local CMD launcher passes stop/start/restart and matching-server reuse
  from C:/Windows at the original port 4186. Source syntax/compilation, edited
  Markdown links/fences and diff hygiene are checked before publication.

Contact timestep refinement of the current 100 N m demo pulses (dual 240 ms,
bellcrank 170 ms; 40 ms smooth rise/fall, zero damping) gave:

| Preset | Step (ms) | First flip (s) | Angle at 1 s (°) | Maximum sampled wheel penetration (mm) |
| --- | --- | --- | --- | --- |
| Dual rope | .5 | .3115 | 130.338 | 4.211 |
| Dual rope | .25 | .3120 | 130.814 | 1.398 |
| Dual rope | .125 | .3120 | 131.136 | .505 |
| Bellcrank | .5 | .3315 | 33.328 | .884 |
| Bellcrank | .25 | .3325 | 32.178 | .793 |
| Bellcrank | .125 | .332875 | 31.643 | .749 |

These trajectories continue after the flip; they do not demonstrate a settled
upright pose. Contact forces and peak accelerations remain step dependent.
An earlier dual-rope 180 ms pulse at 1 ms appeared to flip but failed at finer
steps; it was rejected and replaced by the refined current demo. The initial
fixed-J1 .25 ms error missed the .1° budget; the retained .125 ms refinement
passes without loosening that budget. Initial geometry checks also found pulley
overlap/intersection and a incorrectly zeroed dead-centre cap force; both were
corrected and are covered by the retained tests. A native-config UI race and a
409 from the old Math background run were fixed by immediate config publication
and bounded busy retries; final browser checks pass.

Shortest ideal rope routing omits winding/groove/crossover history, friction,
stretch and binding. Routing parts are massless; cylinder mounting fit, real
coil solid height, 3D clearance, motor ratings and whole-robot self-righting
remain unverified. MATLAB remains legacy-tip-only. The unchanged older full
numerical/envelope suites are historical evidence, not reruns for this feature.
Canonical robot physics is NOT APPLICABLE to this isolated member workspace.

## Existing joint pulley only, 2026-10-11

The user corrected the earlier added piston idler. It is removed from the main
mechanism and generic transmission comparisons. Cable now starts at the moving
external piston rod eye and goes directly to the actual existing hip/knee
spring-drum tangent/wrap. The enlarged view repeats that same named joint pulley
with matching configured radius and recorded angle, labeled "same pulley".
The separate2:1 guide and all solver configurations/data remain unchanged.

All61 JavaScript tests pass, including absence of an implicit piston pulley and
an explicit-only same-joint close-up. Three actual browser suites pass:
transmission_memory, setup_preview and playback. Assertions check exactly one
spring drum in each hip/knee/capture main view, zero routing-idler shapes,
matching main/detail joint identity, no pulley in generic comparisons, real
recorded coil/cap motion, all9 setup presets, settings memory and Plotly behavior.
The in-app preview was refreshed and visually inspected. The actual project-local
CMD stop/start/reuse passes from C:/Windows at127.0.0.1:4186. Source syntax,
Markdown links/fences and diff hygiene are checked before publication.

This is a presentation-only correction. Numerical/physics and native-window
suites were not rerun; the previous40 affected-model tests remain historical
evidence. No backend, constraint, spring law, profile schema, saved result or
hardware definition changed. Canonical physics is NOT APPLICABLE to this member
workspace. Housing placement is schematic, while the main pulley location and
radius still follow the actual recorded/setup mechanism geometry.

## Three physical transmission assemblies, 2026-10-11

The user's follow-up distinguishes bare inline spring, reversing cylinder/piston,
and that piston pulled by a rope attached at its external rod end. The current
preview follows these assemblies. Type1 has no housing or piston rod. Type2
keeps a rigid rod's length fixed while rod eye and cap move together. Type3
adds rope starting at the outside eye, with an external idler and routed tail;
it does not run through the coil or attach directly to the cap.

Hip/knee pulley and knee-capture catalog defaults use compression/type3. Their
current UI offers only that route; non-pulley layouts offer inline or rigid
reversing piston. Coil law remains separate and rope remains tension-only.
Legacy solver IDs/explicit routes and saved recordings remain available. Current
profile/session imports adapt incompatible old route choices and show the new
selection; configuration fields are restored from config, with only matching
view controls/disclosures subsequently restored from raw form memory.

60 JavaScript tests pass, including structural SVG checks for no inline housing,
external cable/rod-eye attachment, a constant rod length and reversed cap travel.
All40 Python tests in spring_mechanisms, suspension_physics, setup_preview and
math_model pass. They cover nine actual force/work/energy models, independent
SciPy/Pymunk loads and refinement, old/new routing compliance equivalence and
reversed internal coil travel. The Pymunk/SciPy errors for the updated pulley
presets at1/.5/.25ms remain .0024606/.0012375/.0006206deg (hip) and
.0089326/.0045268/.0022777deg (knee/capture) in the tested1.2s case.
Four browser suites pass transmission_memory, setup_preview, suspension_ui and
playback: all9 presets run both backends, three hardware drawings/options,
recorded cap travel, cable eye, profile/refresh/tab memory and Plotly behavior.

Initial Python route-comparison assertions assumed knee-pulley defaults were
still extension/direct; those legacy reference cases now select that combination
explicitly. An interim rerun had imported the old assertion before the edit;
the final full40 affected-test run passes without relaxing tolerances. A broad
doc-table edit briefly described bellcranks as rope layouts; it was corrected
to their unchanged extension/inline defaults before publication.

The actual project-local CMD launcher passes stop/start/reuse from C:/Windows,
at127.0.0.1:4186. Syntax/compilation, edited Markdown links/fences, diff hygiene
and repository gates are checked. The updated in-app preview was visually
inspected and retained. No additional full125-test/108-six-second audit or native
window lifecycle is claimed for this correction. Earlier evidence keeps its
original scope. Package sizes, idler positions and mounting fit remain schematic;
no extra solver masses/contact/structural or hardware validation is implied.
Canonical robot physics is NOT APPLICABLE to this member app.

## Cylinder/routing, UI memory and undamped constant lift, 2026-10-11

Current gravity-balance factory/catalog damping is **0 N s/m**; auxiliary is off.
The browser has no constant-lift damping field or optional tip-strut controls.
The standalone lever's damping control is also retired. Legacy backend fields
and original saved recordings remain available for historical reproduction;
loading a profile into current controls selects the undamped, one-spring form.

- 58 JavaScript tests pass, including the recorded-length/slack adapter checks.
- The full 125-test Python run initially passed 123 tests and the six-second
  108-backend-case catalog sweep (no stops/slack/nonfinite state/actuator, positive
  prescribed support). Two old assumptions failed after the intended damping
  change: a minimum chassis response and a damped final-angle error budget.
  Current undamped chassis isolation is now checked using actual relative leg
  travel, low absolute chassis motion, zero dissipation and energy closure;
  the historical damping-ledger test explicitly selects damping100. All31 tests
  in the four affected modules pass on rerun; the full125 suite was not repeated.
  The unchanged other modules' initial passes remain scoped to that run.
- Actual current undamped 1.2s/8mm case Pymunk/SciPy angle discrepancies at
  1/.5/.25ms were .0315123/.0133835/.0061061deg; the retained explicit damping100
  diagnostic refines to .0158129/.0065896/.0029694deg. These are experimental
  numerical comparisons, not hardware accuracy or a new6mdeg acceptance claim.
- Seven browser suites pass: transmission_memory, suspension_architecture,
  playback, setup_preview, lever_force, counterbalance and motion_lab. Real
  recorded end-cap positions match captured coil length and sign, including the
  three routes and rope idler. Tests cover tab/refresh/study number, checkbox,
  slider and view memory, changed-field exclusion, explicit profile precedence,
  old-record library/native routing, mobile/theme and no per-frame Plotly relayout.
- The early transmission harness used direct compression with incompatible
  automatic support preload, correctly rejected by the backend; it now uses
  a bilateral coil to compare routes. A later harness assumed a select existed
  in the ratio study, corrected to its actual number/checkbox/slider controls.
  Playback's second case initially restored the previous case's2x speed through
  the new memory; its strict wall-clock check now explicitly sets1x and passes.
  This failure was initially suspected to be concurrent CPU load, then traced
  to the retained speed. No timing assertion was loosened.
- The cylinder was initially offset below the upper link. User feedback moved
  it above r1 and removed the old duplicate straight orange tangent-span line.
  Gray is the mounting bracket, purple the rod/cable, orange coil/drum, green cap.
  The current in-app preview was refreshed and visually inspected with settings
  preserved. Three comparison examples use a positive200mm reference coil and
  +20mm input travel, independently of edited solver preload.
- Actual project-local CMD stop/start/reuse succeeds from C:/Windows at the
  original127.0.0.1:4186. Node syntax, Python compilation, Markdown links/fences,
  diff hygiene and repository gates are checked before publication.

Housing/bracket/idler packaging is an explanatory massless drawing, not added
solver inertia/contact, cable inventory, solid-height or clearance validation.
The selected moving cap uses actual resolved physical free length and captured
coil length, not a second integration. Zero-effective compensation is still an
ideal offset/preload emulation. New full desktop-window lifecycle tests were
not run; browser native endpoint routing was checked with the existing mocks.
Earlier live-window evidence remains historical. Canonical physics is NOT
APPLICABLE to this member workspace. Historical performance timings below
predate this additional cylinder overlay; only the current playback regression,
not a new FPS benchmark, is claimed here.

## Playback performance and setup previews, 2026-10-11

The cause was 11/12 Plotly cursor relayouts every 0.1 simulation seconds, each
costing about 4.63 ms synchronously: approximately 51–56 ms redraw bursts.
Bounds, input extrema and disturbance decimation were also recomputed each frame.
The fix caches those recording-wide quantities, moves only the existing cursor
SVG path and its serializable Plotly shape coordinates, and updates HTML load
readouts at 15 Hz while motion/cursors follow animation frames. Pause and scrub
refresh exact selected-sample values. No numerical solver or data sampling changed.

Same headless Edge (1400×1000), four-second playback, six-second/6000-row runs,
668 geometry frames, with the same RAF/Plotly/SVG/CPU-profiler instrumentation:

| Case | p95 frame interval before → after | Gaps over 33 ms before → after | Mean callback CPU before → after |
| --- | --- | --- | --- |
| Original tip / 11 plots | 50.1 → 4.3 ms | 38 → 0 | 6.33 → 0.78 ms |
| Replacement / 12 plots | 62.5 → 4.3 ms | 38 → 0 | 8.25 → 1.15 ms |

The actual fixed code makes zero Plotly.relayout calls during playback; these
are measured fixes, not the earlier diagnostic ablation. Headless cadence is
comparative evidence and does not certify remote display FPS. Paused 1.5-second
cursors match raw/complete layout and transformed SVG coordinates across every
plot, including angle axes. Zoom/pan, dark redraw and SVG export retain correct
cursor positions. Evidence stays in ignored artifacts/playback-baseline and
artifacts/playback-fixed; `scripts/verify_playback_ui.cjs` reproduces regression
checks without imposing a hardware-dependent frame-rate threshold.

`/api/setup-preview` returns initial bodies, anchors and coil geometry with
solver_steps=0 and no trace/load rows. Three Python tests cover all nine presets,
replacement force sites/sensor geometry, edits and validation; a mocked Space.step
raises if preview construction ever integrates. Real-browser setup tests pass
all nine presets in both tabs with no simulation requests before Run, no fake
loads, geometry changes, guide drawing, superseded selections, immediate Run
cancellation and previous-recording separation. Pending responses cannot replace
completed recorded results.

All 56 JavaScript tests pass. Browser suites `verify_pymunk.cjs`,
`verify_playback_ui.cjs`, `verify_setup_preview_ui.cjs`, `verify_suspension_ui.cjs`,
`verify_suspension_architecture_ui.cjs` and `verify_motion_lab.cjs` pass. Existing independent numerical
audits remain scoped historical evidence; they were not rerun for the renderer.
The actual project-local stop/start launchers restart the updated server from
an unrelated Windows directory and preserve port4186. Canonical robot physics
is not applicable to this isolated member-app work.

## Compact comparison follow-up, 2026-10-10

The later UI request collapses per-plot controls and source/help sections,
adds a hideable channel sidebar and Focus plots / Exit focus / Escape, and
expands/resizes the charts. The updated real-browser comparison suite passes
compact positioning, control expansion, sidebar visibility, focus/restore,
independent traces/legends, both splits, JSON roundtrip, profile execution,
zoom, dark mode and mobile. The 22 comparison/library unit tests still pass.
The live in-app comparison was backed up and restored with all user-selected
channels intact; focus and Escape were visually verified. Its two full six-second
recordings occupied 87,116,203 bytes as indented JSON, exceeding the import cap.
Comparison exports now use compact JSON, matching the 80 MiB size guard; the
actual 55,032,085-byte export is below the cap and retains identical results and
layout, preserving the prior trace visibility alongside added channel selections.
The original backup remains intact. No numerical solver changed
in this UI follow-up.


## Current contract and evidence scope

The latest architecture replaces the old lower-tip strut with **one upper-link /
chassis massblock spring/damper**. Auxiliary is off, primary damping is 100 N s/m,
knee impedance is disabled and elastic compensation is neutral. All nine
current wheel presets use `point_force`; `native_legacy` is a restricted
diagnostic. Chassis and 28/14 mm guide sensors add no mass/contact. Belt viewer
baseline/force arrows stay independent of sheet T₀ and solver bearing loads.

[Mechanism audit](mechanism-audit.md) records corrected geometry/rates,
passivity and the tested envelope. Following release blocks are preserved
historical evidence; earlier counts, native-spring integration, four-shape /
two-stage architecture and unsafe old demo defaults are superseded. They are
not current-profile acceptance. Latest evidence is appended below.

## Historical position-input release, 2026-10-10

The user corrected force excitation to prescribed displacement. All **27** Python checks pass: the 19 historical force/reference checks now explicitly select diagnostic force mode, and eight position checks cover ramp derivatives, trajectories, driver type, tracking, force-versus-position separation, spring sensitivity, independent energy response/refinement and fixed-hip range rejection. Build and browser suites pass after regenerating step/square recordings. Actual backend checks cover default position/floating controls, a 30 mm moving-height arrow, full CSV/config, N/kgf and retained diagnostic modes; offline mobile recorded playback passes. The native live renderer advances the default position model and draws three shapes/seven constraints.

For the 30 mm C2 step at 1.2 s, independent scalar-energy RK4 gives θ = 48.02864444°. At 1/0.5/0.25 ms, engine angle error decreases **0.19835/0.09011/0.04298°**, and maximum wheel tracking error decreases **0.15887/0.07931/0.03963 mm**. Momentum/torque residuals stay below 1e-7 in the tested runs. This is convergence evidence for the ideal bilateral fixture, not hardware or unilateral contact validation. Linear joins and rigid-stop peak loads remain timestep dependent.

This follow-up is confined to the member app and contribution log: workspace scope, canonical physics NOT APPLICABLE. The earlier shared-index import used preliminary scope; that historical result remains below.

## Historical rebuilt import

The app-local Python 3.13.12 environment installs Pymunk 7.3.0, pygame-ce 2.5.8, cffi 2.1.1 and pycparser 3.11. The build uses Node.js 22.20.0, Vite 7.3.6, ml-matrix 6.15.0 and Playwright 1.62.1 with installed Edge for browser tests. Seven animation fragments, recorded playback and the detailed Vite entry build successfully with project-relative sources and local web assets.

| Check | Actual result |
| --- | --- |
| `npm test` | 24 tests pass, no skips, including refreshed independent reference fixtures |
| `.venv/Scripts/python.exe -m unittest -v test_physics test_equation_checks` | 19 tests pass: guide/spring geometry, wave area, reactions, equilibrium, reference algebra, wheel-contact torque and refinement |
| `python scripts/validate_linkage_reference.py` | Three independent SymPy/SciPy cases agree; optional analysis versions NumPy 2.4.2, SciPy 1.17.1, SymPy 1.14.0 |
| `npm run test:browser` | Seven offline studies, path coordinates, fixed 4:1 error under 0.768 mm, force calculator, detailed entry and recorded mobile disturbance pass |
| `node scripts/verify_pymunk.cjs` | Actual backend/objects, moving-input arrows, N/kgf, CSV/config, reference residuals, contact/drive modes, fixtures and responsive layout pass without external requests/errors |
| `node scripts/verify-force-plots.cjs` | Force/minimum/travel averages agree with the detailed Jacobian and numerical integral; edits, cycle/pause/scrub and mobile/offline checks pass |
| `.venv/Scripts/python.exe debug_gui.py --headless-check` | Live solver advances and official renderer draws actual engine shapes/constraints |

Initial import harness checks used a visible wait on a zero-width vertical SVG path and an old-port offline allowlist. These were harness failures, corrected to an attached-path wait and the imported URL. Both checks then passed; neither is hidden as a physics pass.

## Launcher lifecycle

From an unrelated Windows directory, the imported 4186 launcher starts the actual app, reuses its matching server, stops only the tracked process and restarts successfully. The 4175 geometry launcher also passes start/reuse/scoped-stop/restart; `/animations/`, `/force-plots/` and `/linkage/` return HTTP 200 there. Health reports the imported app root and identity. No boot/login automation or unrelated process kill is used. The external original source folders remain intact.

The launchers require setup/build in a new clone, resolve their own directory and reject unrelated port owners. Test screenshots, logs and full traces remain ignored.

## Historical import physics interpretation and repository scope

Independent Pymunk angle errors decrease at 2/1/0.5/0.25 ms: approximately 0.175/0.089/0.044/0.022° in the mild-impulse case. A locked-contact case also agrees with an independent energy model including wheel inertia. Checked force/moment residuals are below 1e-7. Rigid-stop peak loads remain timestep dependent.

The fixed 4:1 example retains about 42.35 mm working travel with less than 0.768 mm ray error, not global straightness or collision-free inversion. The reference sheet's two torques reproduce with inferred 400 mm links/200 mm radius, not independently confirmed dimensions or belt-bearing loads.

With shared documentation indexes, publication uses preliminary scope. Repository regressions ran 36 tests: 34 pass and two MuJoCo fixture tests are skipped because the global environment lacks MuJoCo. These skips are not canonical physics passes. The shared manifest stays empty and unchanged; canonical physics is not applicable to this isolated toolkit. Architecture, link/log checks and the scoped gate must pass before publication.

Untested: hardware, real belt pretension/elasticity, tire/terrain/soil contact, structure/buckling, inversion clearance, GPU performance, other operating systems, and missing T₀/pulley/component limits.

## Unified Motion Lab, 2026-10-10

The shared browser menu now separates independent mathematical simulation,
2D Pymunk physics and miscellaneous motion studies, with dark mode, Plotly
charts and a profile/data browser. Use Start Motion Lab.cmd at port 4186;
familiar browser launchers are aliases and the native debugger is preserved
separately. Full workflow, JSON contracts, MATLAB/SciPy agreement and current
verification are in the [unified workspace record](unified-motion-lab.md).

## Historical eight-preset/native release (superseded defaults), 2026-10-10

The expanded suite passes **64 Python tests**: 27 original physical/reference/
position cases, 15 independent SciPy cases, 12 mechanism-kernel cases and 10
actual Pymunk preset cases. `npm test` retains all 32 passing JavaScript tests.
Run the six Python test modules listed in the app README to reproduce them.

All eight topologies satisfy physical point-force virtual work for both drum
wrap directions. Pin/guide/stop/driver impulse checks and angular ledgers close
near roundoff in the smooth 8 mm step. Static finite-step deviations at 1 ms are
bounded by 0.005° / 0.5 N / 20 µm; measured maxima were 0.00179° / 0.2873 N /
9.61 µm. Refining Pymunk from 1 to 0.5 to 0.25 ms decreases each preset's final
angle error against independent SciPy. The largest finest-step error is 0.02636°
in the hip pulley demo. A conservative actual-body case's energy drift falls
0.00547 → 0.00273 → 0.00136 J from 0.4 J initial stored energy. These are finite
integration checks, not exact agreement or peak-load convergence at rigid stops.

`node scripts/verify_suspension_ui.cjs` checks all eight presets on both real
backends, editable demo resets, 11 Plotly charts, actual attachment overlays,
coil telemetry, profile JSON and mobile layout. `verify_motion_lab.cjs` passes
the full shell/data/comparison workflow, separately labeled recorded playback,
and mocked native launch/config/status/failure/query handling. The existing
Pymunk, miscellaneous-study and force-calculator browser suites also pass.
The first parallel browser run met the server's deliberate busy response;
the Pymunk harness passes when run after the other API suite completes.

`scripts/verify_native_gui.py` calls the actual native launch API and verifies
a Windows desktop HWND owned by the returned PID, increasing `Space.step`
counts, a completed loop, three real engine shapes and six real constraints
for knee capture. It then posts Close only to that verified window and waits
for a zero process exit. Cross-origin launch, incompatible preload and unknown
session requests are rejected. All eight presets also pass headless official
Pygame rendering; the original native spring has seven constraints. A first
close check observed the GUI's final state before process exit; the harness now
waits for both, and the repeat passes. Show restores only that verified window;
Windows may decline foreground activation while still restoring its visibility.
The test compares the live state's PID because Windows' venv launcher can spawn
the actual GUI in a child process. Generated screenshots/logs stay ignored.

The launcher passes start, reuse, scoped stop and restart from C:\Windows. A
PowerShell 7 JSON date was decoded as DateTime, so string comparison refused
the first stop safely; comparing UTC DateTime values preserves fractional ticks
and also works with Windows PowerShell's string decoding. Previous state/log
files are archived and no unrelated process or source file is removed.

The historical 40 mm hip-pulley demo's instability was explicitly tested;
the current curated default is repaired as documented in the mechanism audit.
Spring law and transmission are independent settings; increasing pull-through
travel compresses the coil, while wrap/mount geometry selects the leg-loading
direction. SciPy supports the full catalog; MATLAB's expanded-profile parsing
was checked in R2025b for the original captured/direct tip spring and rejects
other mechanisms explicitly. No hardware, coil-bind, cable friction/stretch,
tire contact, whole vehicle or canonical robot validation is claimed.

## Historical constant-lift integration, 2026-10-10

The final combined suite passes **82 Python tests** (71 wheel/kernel/reference
plus 11 standalone-lever cases) and **33 JavaScript tests** (24 detailed model
plus nine library contracts). All nine wheel presets pass real-backend browser
checks, including calibrated constant elastic lift and the additional Plotly
lift-versus-angle chart. The standalone lever browser suite passes independent
math/Pymunk APIs, ideal/ordinary spring comparison, free/prescribed motion,
portable profiles/full runs, saved-data playback, dark mode, zoom and mobile.
The full unified shell suite also passes; lever records never use wheel APIs.

Seven dedicated wheel-adaptation tests verify rate calibration, effective
versus physical lengths, force/energy balances and refinement. The calibrated
demo rate is 2260.043672222 N/m and elastic equivalent support 84.751637708 N.
At 1 / 0.5 / 0.25 ms the final angle error against SciPy is approximately
0.015813 / 0.006590 / 0.002969°. Actual-body elastic support drift decreases
0.004108 / 0.001032 / 0.000259 N. Damping and dynamic inertial reactions are
separate quantities and need not be constant.

The lever's default rate is 215.7463 N/m, supporting an equivalent tip load of
21.57463 N with the stated distributed lever weight. Its tension varies by
more than 50 N over the ±80° sweep. Exact balance is neutral: angular velocity
can persist in free mode without a hidden holding motor. Ordinary-coil free
angle errors decrease 0.060354 / 0.030213 / 0.015115°, and actual conservative
energy drift decreases 0.003478 / 0.001728 / 0.000861 J at the same timesteps.
Prescribed Pymunk motor angle tracking refines from 0.225° at 1 ms to below
0.06° at 0.25 ms; this is solved dynamics rather than pose teleportation.

Actual native verification now covers knee capture, wheel gravity balance,
prescribed lever and free lever. Each has three real engine shapes; constraint
counts are respectively 6 / 6 / 2 / 1. HWND ownership, advancing solver steps,
looping, visible restore and graceful zero-exit close all pass. Repeating a
native launch for an identical resolved profile reuses its owned live window.
The official lever renderer also passes headless checking. Source figures are
retained; all generated snapshots, sessions and raw solver outputs stay ignored.

The final server and original project-local CMD launcher preserve port 4186.
Existing binary/source/archive files remain intact; no boot automation or
canonical robot changes are introduced. MATLAB remains the explicitly labeled
legacy tip-spring companion. Hardware, real routing/coil packaging, contact,
other desktop operating systems and restoring-suspension design are unverified.

The final exported profile's new force-law/effective-length fields also pass
MATLAB R2025b parsing. Its legacy step differs from SciPy by at most
1.041e-8 degrees in the checked 1.2 s case; requesting zero-effective law is
explicitly rejected. The initial local probe used MATLAB run's changed working
directory; resolving the app root from the script path then passed without
warnings. No new mechanism is silently evaluated with the old MATLAB law.

## Historical two-stage architecture (superseded factory), 2026-10-10

All **90 Python tests** pass: the prior 82 plus eight dedicated architecture
cases. The nine auxiliary-disabled preset trajectories remain unchanged.
Tests verify initial gravity support and zero ride elastic load, restoring
force on both sides of ride pose, positive damper dissipation, actual point-force
and impulse/moment closure, unchanged chassis mass/inertia after adding its
sensor polygon, and independent energy/step refinement. Architecture final-angle
errors decrease 0.009763 / 0.005147 / 0.002635° at 1 / 0.5 / 0.25 ms. Finest-step
final differences are about 0.0450 N at J2, 0.0166 N driver reaction, 0.00309 Nm
guide torque and 0.0511 N ride-strut force. Conservative body-energy drift
decreases 0.002542 / 0.001250 / 0.000619 J. All 33 JavaScript tests still pass.

The factory at this historical stage used primary damping zero and ride damping 500 N s/m;
these are labeled editable demos. Real browser checks pass the cold architecture
entry with one configured run, four actual shapes and two coil paths, restoring/
damper telemetry, per-stage energies, 15 Plotly charts, JSON/library-to-math
preservation, embedded/standalone lever bridges, dark mode and mobile. The
existing lever and main-menu suites also pass, including the native active-frame
regression: a 350 mm Math lever remains selected after an inactive 400 mm Misc
lever is opened. Explicit saved-record/child configurations stay authoritative.

The actual native test now passes five fixtures, including the two-stage model
with four shapes and six constraints. Window ownership, live step advancement,
looping, visible restore, exact-profile reuse and graceful zero exit pass.
Official headless rendering also passes and shows the rigid compensator mount,
chassis and independent ride strut. MATLAB accepts the expanded auxiliary-off
legacy profile; enabled auxiliary mode is explicitly unsupported. These checks
do not establish real contact, packaging, structural stress or hardware ratings.

## Current replacement and passive audit, 2026-10-10

Full app-local Python unittest discovery passes **114 tests** in 299.557 s.
Its six-second envelope covers 108 backend cases: nine catalog presets,
30/45/60° initial poses, smooth 30 mm / 250 ms quintic step and square inputs,
SciPy and Pymunk. Every case completes with no stops, slack, nonfinite values
or actuator torque; force/moment closure stays below 1e-7 and signed prescribed
support stays positive. Minimum observed support is 49.65184 N in Pymunk
`chassis_direct`, 30° square. This is a bounded ideal-fixture result, not
global passive stability or ground-contact acceptance.

At 30° square, final-angle errors against SciPy decrease with 1/.5/.25 ms:

| Repaired preset | Error at 1 / .5 / .25 ms, degrees |
| --- | --- |
| Original tip | .465685 / .262895 / .133506 |
| Hip pulley | .003096 / .001546 / .000773 |
| Hip bellcrank | .000498 / .000240 / .000117 |
| Knee bellcrank | .012975 / .006191 / .003024 |

Kernel audit covers 1404 valid mechanism/routing/law/angle/speed combinations,
with no negative damping dissipation or compressive rope force. Force-site
power error is at most 6.9e-13 W; energy-gradient error at most 1.64e-7 N m.
Fifty-four impossible coil lengths are explicitly rejected. The
[mechanism audit](mechanism-audit.md) explains repaired defaults and the limits
of short-run/preload checks.

All **43 JavaScript tests** pass. Actual API browser suites pass
`verify_passive_stability_ui.cjs`, `verify_suspension_ui.cjs` (all nine presets /
both backends), `verify_pymunk.cjs`, `verify_suspension_architecture_ui.cjs` and
`verify_motion_lab.cjs`. They check passive metadata/default reset, controls,
export/library flow, current single primary path, six engine shapes, twelve
charts, guide dots/spokes/vector reference metadata, zoom/theme and mobile.
Shell native requests are mocked in browser tests; actual native checks below
are separate. Earlier lever UI tests remain scoped to the unchanged tool.

Actual `scripts/verify_native_gui.py` passes five desktop fixtures: knee capture,
gravity balance, corrected replacement wheel-leg envelope with viewer baseline
60 N, prescribed lever and free lever. Replacement has six sensor shapes and
six constraints, auxiliary off and viewer baseline outside solver config.
Verified HWND/PID ownership, more than 1500 advancing solver steps, loop
completion, owned `/show` restoration, exact-profile reuse and graceful zero-exit
close pass. The final replacement native window was visually reviewed for its
rigid chassis mount, upper attachment, belt marks, pivot spokes and
unknown-baseline difference labels. Generated sessions/logs remain ignored.

Actual MATLAB R2025b comparison of the updated full legacy profile
(k20000 N/m, c500 N s/m, 1.2 s, 8 mm step starting .3 s) passes: maximum
matched-time angle difference 2.5674e-8° and J2-force difference 1.0209e-6 N
against SciPy. Zero-effective law is explicitly rejected. This does not extend
MATLAB support to the new mechanisms; Octave remains untested.

The actual project-local CMD launcher passes scoped stop/start from C:/Windows
and duplicate matching-server reuse on the new backend, preserving port 4186.
The in-app preview was checked for single upper-anchor geometry, auxiliary off,
200 mm wheel, primary damping 100, zero controller, neutral 0 N/m stiffness /
zero initial balance residual and an advancing completed run.

Rigid-stop peaks remain timestep dependent; prescribed height is bilateral and
chassis pitch is held. No hardware, real spring/belt packaging, tire/terrain
contact, structural, GPU or other-OS validation is claimed. Repository publication
gates are reported separately in the contribution log.

## Comparison and single-link force update, 2026-10-10

Scoped lever checks pass 19 Python tests: eleven existing lever cases and eight
new end-force/live-advance cases. All 56 JavaScript tests pass, including twelve
comparison contracts and force-history JSON validation. Five live browser suites
pass: verify_lever_force_ui.cjs, verify_comparison_ui.cjs, verify_motion_lab.cjs,
verify_counterbalance_ui.cjs and verify_suspension_architecture_ui.cjs.
The harness fixes opened a collapsed control and waited for responsive Plotly
layout to settle; assertions were not relaxed. Checks cover new navigation,
explicit profile execution, multi-import, active-plot channels, visibility,
split layout, signed delta/unit/gap rules, workspace roundtrip and live force
release/reset/history. Native requests mocked by browser suites remain separate
from actual desktop checks.

Actual five-case native API checks pass. A new force-mode headless render
advances 1000 steps with three real shapes, one PivotJoint and no motor.
The default standalone model is free, damping zero and uncontrolled. This
does not change the wheel replacement unit's damping of 100 N s/m.

A 2 N pulse for .3 s, with .05 s rise/fall beginning .1 s, gives SciPy angle
51.55276285° at 1 s and release speed .50101018 rad/s. Energy/work residual is
4.6e-10 J. Pymunk angle errors decrease .26191165 / .13057446 / .06519184°
at 1 / .5 / .25 ms. Release preserves velocity and coasts; explicit Place at
rest zeros speed without a holding controller. Prescribed motion remains an
explicit motor diagnostic, not the default.

The wheel core is unchanged; its preceding 114-test/108-case audit was not rerun
for this update. Historical evidence above retains its original scope.
The new matched-profile comparison script and portable records use recorded
overlap/union timestamps, with full-window startup errors reported separately
from post-startup errors. See [Comparison](comparison-workspace.md).
Publication gates remain separately reported by the contribution log.

### Matched-profile wheel model comparison

The actual scripts/compare_suspension_models.py run writes four portable records
and summary JSON to ignored artifacts/model-comparison. Both models use the
same 200 mm wheel, 273 mm links, 45° initial angle, 30 mm / 250 ms quintic
position step and six-second horizon. Delta is Pymunk minus SciPy over the
union of recorded timestamps in shared overlap, matching the Comparison UI:
6000 samples at 1 ms and 12000 at .5 ms. RMS is a sample RMS.

| Quantity / window | Original tip: max absolute delta at 1 / .5 ms | Constant lift: max absolute delta at 1 / .5 ms |
| --- | --- | --- |
| Chassis displacement, full window | .5892305 / .2894302 mm | .3246738 / .1512563 mm |
| J1 force, full window | 7.210894 / 7.210894 N | 48.609238 / 48.609238 N |
| J2 force, full window | 7.603287 / 7.603287 N | 16.053063 / 16.053063 N |
| Hip guide reaction, full window | 4.315348 / 4.315348 N m | 20.198128 / 20.198128 N m |
| J1 force, t >= .05 s | 3.613304 / 1.794493 N | .227748 / .114630 N |
| J2 force, t >= .05 s | 3.644238 / 1.809873 N | .064025 / .032034 N |
| Hip guide reaction, t >= .05 s | .069036 / .034253 N m | .036278 / .018583 N m |

Full-window force/guide maxima are dominated by initial constraint initialization
and do **not** halve with timestep here. Post-50-ms errors refine, but that
window must not replace the full result without disclosure. These compare
physical step-averaged impulse loads to instantaneous mathematical loads,
not measured hardware. The script summary retains RMS and signed final values
for every listed channel as well as the complete configs.

## Link sizing / torque sweep, 2026-10-12

The user confirmed the starting case as 200 mm radius / 400 mm diameter and
200 mm usable lift. The [sizing study](link-sizing.md) adds constant-net-load
analytical enumeration to /force-plots/; no wheel dynamic solver is changed.

- All70 JavaScript tests pass with npm test, including seven new sizing checks.
  Torque agrees with the existing linkage Jacobian and an independent finite
  height derivative. Both exact mean/RMS/CV integrals agree with20,000-point
  midpoint quadrature; work conservation, half-sized knee torque, degree/mm
  round trips, boundaries, feasibility and objective ranking also pass.
- node scripts/verify_link_sweep.cjs passes actual browser tests of both wheel
  dimensions, nominal/custom angular ROM, all three buffer/ROM conversions,
  both torque coordinates/weightings, objectives, reference-link selection,
  stricter chassis clearance, infeasible searches, all-candidate CSV and JSON
  config import/export, refresh and Motion Lab study-switch memory, Plotly zoom,
  dark theme,360px layout, locally served assets and zero browser errors. An
  infeasible config export correctly carries no selected candidate. Raw evidence
  stays ignored under artifacts/link-sweep/; screenshots were visually inspected.
- The existing node scripts/verify-force-plots.cjs suite passes force/Jacobian
  averages, controls, projections, animation/full-cycle, zoom/theme, mobile and
  extreme geometries, and offline assets. The original numerical calculator
  and dynamic solvers are preserved.
- npm run build passes Vite and the seven-study/gallery build. The real app-local
  Start Motion Lab.cmd / Stop Motion Lab.cmd pass verified scoped stop, fresh
  start, stop/restart and running-server reuse from C:/Users/zhang, with sizing
  HTML and model HTTP readiness on the original127.0.0.1:4186 route. The original
  Motion Lab URL remains usable; errors remain in the launcher/.preview logs.

A browser rerun initially caught conversion rounding excluding the exact120mm
feasibility boundary. Millimetre UI conversion now rounds to six decimals while
degree conversion keeps ten; the complete sizing browser suite passes after the
fix. Earlier passing records remain historical, with their original scope.

Initial uniform-travel hip example:2,586 candidates /97 lengths, minimum peak
and mean at120mm links,19.5773N m mean /23.9165N m peak. Lowest CV is at the600mm
search boundary with119.9833N m peak; expand/refine before treating it as an
optimum.20mm buffers/gap,200mm chassis depth and100N load are editable demo
assumptions. No spring-force/preload law, distributed link weight, dynamic motor
load, actual3Dclearance, strength, hardware or canonical robot validation is
claimed. Python/native/physics solvers are not rerun for this analytical UI change;
canonical physics is not applicable to the isolated member workspace.

## Actual Windows laptop reconstruction, 2026-10-12

Source base `c6a79b5`; full-history clone on Windows 11 Home x64. Installed
Python 3.13.12, Node 22.23.3 and npm 10.9.9 are durable per-user runtimes.
Actual Setup Motion Lab.cmd recreated `.venv`, installed all pinned requirements,
ran npm ci (zero vulnerabilities) and rebuilt Vite plus all seven studies.
`pip check` reports no broken requirements; all 70 JavaScript tests pass.

The full `.venv/Scripts/python.exe -m unittest discover -v` run passes **139
tests** in 578.836 seconds, including the 108-backend-case six-second passive
envelope, independent SciPy/Pymunk refinement, position/force ledgers, spring
mechanisms, inversion/stop events and setup previews. Minimum prescribed support
in that envelope is 49.65184 N. These are experimental fixture checks, not
hardware or a canonical robot validation; legacy reproduction cases retain
their explicit historical interpretation. The complete raw log stays ignored
in `.preview/laptop-python-tests.log`.

Existing browser suites pass: `verify_link_sweep.cjs`, `verify-force-plots.cjs`,
`npm run test:browser` and `verify_motion_lab.cjs`. They verify sizing/defaults,
degree/mm buffers and ROM, objectives/selection/clearance, JSON/CSV, session
memory, original force equations, seven offline studies, mobile layouts and
real independent SciPy/Pymunk API runs plus the library/comparison workflow.
Native endpoints in the unified browser suite are mocked. Actual
Open Native Pymunk Debugger.cmd --headless-check steps the live engine and
renders three shapes/six constraints with pygame-ce 2.5.8. The sizing desktop
and mobile captures remain ignored under artifacts/; the desktop was inspected.

The first unified browser run timed out waiting for its mathematical recording
while the restart verification overlapped it. A stable-server rerun passes the
same suite unchanged; no timeout or assertion was relaxed.
Actual Start/Stop Motion Lab.cmd pass fresh start, scoped stop (4186 listener
disappears), restart and matching-server reuse from outside the app directory.
Health identifies this laptop's app root and Pymunk 7.3.0. Motion Lab remains
running with Atlas/workbench independently at 4175. No copied PC environment
or remote server was used.

The current architecture defaults API confirms damping zero, auxiliary off,
knee kp/kd zero, wheel radius .2 m and prescribed position. Only stale model
prose is corrected to match that existing architecture. Sizing remains 200 mm
radius / 400 mm diameter / 200 mm lift with configurable degree/mm buffers and
ROM; dual-rope IMPOSSIBLE status and historical rollback/source are preserved.
Visible native windows, MATLAB, hardware, GPU, canonical robot physics and
other operating systems are unverified by this setup. Canonical physics is not
applicable to the isolated workspace contribution.

## Wheel-centre angles, profile curves and lift/RMS, 2026-10-12

At base `7cfacbf`, the sizing UI changes its displayed coordinate to theta
upward from wheel-centre horizontal, while retaining internal q and the same
geometry/conversion/search equations. New individual torque curves, click
selection and a fourth lift/RMS ranking use the same static load model.

All **72 JavaScript tests** pass. The two new analytical cases independently
check wheel-centre vector angles/height, curve endpoints, monotonic lift/angle/
torque, equal hip/knee work integrated along their different angular strokes,
the exact 120 mm feasibility/peak boundary, lift/RMS rankings in both weighting
and torque coordinates, and unchanged ideal work. Hip torque remains twice
relative-knee torque; 2:1 guide motion is not an additional motor reduction.

`node scripts/verify_link_sweep.cjs` passes both standalone and embedded UI,
wheel-centre reference origins/arcs and complementary angle readouts, all 97
initial profile curves, clicking a curve, winner/top-30 comparisons, explicitly
disclosed sampling above 300 curves, the lift/RMS objective, unit/ROM controls,
clearance, JSON/CSV, refresh/study memory, Plotly zoom/theme and 360px layout.
Existing `verify-force-plots.cjs` passes its original analytical/UI suite.
No page errors or external asset requests occur. The initial sizing browser
rerun caught an obsolete `(35.00°)` text assertion after the readout gained
separate link/actuator ROM labels; it now checks both explicit 35-degree values
and the complete suite passes. No physics tolerance or timeout was relaxed.

Build and JavaScript syntax checks pass. Actual app-root CMD stop/start/reuse
from outside the app directory verifies the updated source at 127.0.0.1:4186.
Angle and curve screenshots were inspected; the end wheel's previously clipped
top edge is corrected by reserving its radius in the diagram layout. Raw QA
captures/exports remain ignored under artifacts/link-sweep. The main UI remains
running locally; refresh the sizing page to load the updated module.

Default 100 N / 200 mm case: 120 mm links, theta66.44354→4.78019 degrees, hip
peak23.91652 / mean19.57728 / RMS19.96664 N m, lift/RMS10.01671 mm/(N m),
hip ROM61.66334 degrees. Knee values are half the torque, twice the ROM and
twice the numerical lift/RMS score; both do20 J ideal work. The score compares
travel with torque demand, not energy efficiency or hardware thermal suitability.
Python/native/dynamic solvers are unchanged and not rerun; canonical robot
physics is not applicable to this isolated analytical app contribution.

## Labelled alpha-zero examples and GIFs, 2026-10-14

Source `12e227c`; isolated workspace visualization. [Design examples](design-examples.md)
records five selected mechanisms and ten curated working/full-inversion GIFs.
Node 22.23.3 build and all 76 tests pass, including four new tests and 3,010
original-Jonathan-V2 pose comparisons. Exact retained configs, metric records
and source hash agree. Actual Edge controls/menu-memory/dark/mobile checks
pass, with zero page errors/external requests and ten HTTP GIF signatures.
The native-GUI action for this study makes no launch POST, preserving the
explicit kinematic/physical-fixture distinction. Optional pinned Pillow 12.3.0
installs into this laptop's Python 3.13.12 venv; pip check passes.

All GIFs reopen as 48-frame 600x720 infinite loops, 4.8 seconds each; frames and
actual browser drawings were visually reviewed, with merged/separated fold
labels repaired and re-exported. Sizes/hashes are retained in the GIF manifest.
Actual app-root Stop/Start Motion Lab.cmd works from an unrelated directory: the
listener disappears, restart succeeds and /design-examples/ returns 200 at 4186.
The first integration harness used a Frame API on a FrameLocator; the corrected
harness passes without changing a mathematical tolerance. No new physics
backend, contact/impact, canonical robot, hardware, GPU or other-OS validation
is claimed. Historical dual-rope remains IMPOSSIBLE/rejected.

Final GIF reproduction is byte-identical for all ten files (2,589,694 bytes
total; largest 311,008 bytes), with matching delivered renderer/data and GIF
hashes. One hundred relative documentation links pass. An ad-hoc link check
initially used the lexical parent of Path('.'); resolving the app directory
then produced the passing check without changing any source/result.
