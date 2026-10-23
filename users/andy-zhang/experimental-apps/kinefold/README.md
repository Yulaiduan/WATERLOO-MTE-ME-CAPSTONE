# Kinefold

Owner: Andy Zhang. Created 2026-10-22. Experimental mechanism design and solver workspace;
no canonical robot or hardware acceptance is implied.

Double-click **[Start Kinefold.cmd](Start%20Kinefold.cmd)** and wait for Ready,
then open <http://127.0.0.1:4191/>. The builder/static server requires installed
Python 3.10+; there is no npm install or build. Run **[Setup Kinefold.cmd](Setup%20Kinefold.cmd)** once (Python 3.12+)
to install this app's isolated SciPy/Pymunk environment for dynamic runs.
The detached server survives Codex closing.
After a reboot or shutdown, use the same launcher and URL. Repeated startup
reuses this app; an occupied port fails visibly. **[Stop Kinefold.cmd](Stop%20Kinefold.cmd)**
stops only this app. Failures are readable in the launcher and `.preview/server.log`.
No login/boot automation is installed. Node.js is needed only for developer checks.

## Workspace

- **00 Mechanism studio:** compact save/profile actions and an expandable full
  named-design library above one mechanism workspace. Geometry, Suspension,
  Loadings & preloads stay at left. The calibrated mechanism preview is at right,
  followed directly by all 17 equilibrium charts in categorized expandable groups.
  Diagnostic ranges inspect the same builder design without editing its physical
  stops. See [plot coverage and controls](equilibrium-plots.md).
- **01 Analytical / 02 Pymunk:** shared quarter-model case controls, playback,
  categorized result charts and exact-snapshot engine comparison described below.
- **03 Conventions & variables (last):** expandable frame, topology, signs,
  spring/loading laws, dynamics assumptions and searchable variable definitions.
  The front-left frame is +x forward, +y left, +z up; +x faces left and +z up
  in side view, with positive +y moments counterclockwise.

All data plots use the pinned offline **Plotly basic 4.1.2** runtime; no CDN or
npm install is needed. Plotly supports hover, zoom, pan, legends and reset axes.
Existing contextual JSON/CSV exports write to this app's `exports/` folder;
Plotly's browser-download camera is removed. Mechanism, spring, free-body and
conventions drawings remain geometrically scaled SVG illustrations.
Old `?tab=designs` and `?tab=static` links open the relevant studio section.
Builder playback defers equilibrium rebuilding until the pose settles and labels
those charts as showing the last settled pose while it plays.

- **Export design** / **Import** retain the complete mechanism, view and shared
  solver settings in a versioned `kinefold/project-v3` document. Legacy
  `kinefold/mechanism-v1` and fixed-hip `project-v2` files migrate explicitly, preserving geometry and an archived prior profile. Invalid imports leave the
  current design unchanged. Existing browser data is retained as a migration backup;
  the app-folder store becomes authoritative after startup.

The visual shell follows Motion Lab's app-owned sage/cream tabbed interface.
This is a separate app: it neither changes nor imports the Motion Lab UI/runtime.
The three carrier belts, finite-idler tangency and V4 baseline come from
[Jon's VSL v4](../../../jonathan-xie/experimental-apps/vsl-solver/v4/README.md).
[reference.json](reference.json) records the source revision/hash;
`reference-v4.js` retains unchanged analytical blocks, with an app-owned frame adapter.

The preview grid is calibrated in world millimetres; its displayed cell size
updates with zoom, with major lines every five cells. Index axes and rim marks
follow all six pulleys and the wheel. Belt material dots follow the exact open
belt loops, accounting for the moving carrier; their larger reference dot is
not a tooth or a manufacturing feature. The baseline has K=0, so the wheel
index stays level as the leg folds. Side view preserves plane lengths uniformly;
the isometric view is an orthographic projection. No wheel width is invented.

V4 uses a **linear coil with approximately constant support**, not constant cable
tension. Both that reference and an **ideal constant cable-force** option are
explicitly available in the builder. The equilibrium section beneath the preview shows signed
torque sweeps, belt tensions and equilibrium residuals from these same inputs. Wheel loads are prescribed; gravity acts on the individual masses.
The default 8.75 kg is a single-leg supported mass, not a whole-vehicle mass.
Remote spring housing is schematic. Cable stretch, friction, strength, contact,
manufacturing and 3D packaging remain unresolved. Travel is sampled at 181 poses.

## Developer checks

`node verify-plotly-runtime.cjs`, `node verify-equilibrium-plotly.cjs` and
`node verify-dynamic-plotly.cjs` check lifecycle and trace semantics. The offline
vendor checksums/provenance and license are in [vendor/README.md](vendor/README.md).
Real pointer, sizing and zoom behavior also require browser review.

From this directory: `node verify.cjs` checks source parity, geometry, world
forces/moments, finite-pulley energy derivatives, both spring laws and JSON state.
`node verify-drawing.cjs` independently checks all index radii/orthogonality and
finite-difference belt material velocities on both wraps of every pulley stage.
`node verify-equilibrium.cjs` checks all17 chart datasets against original V4
series, support gaps and multibranch travel; `node verify-equilibrium-diagrams.cjs`
checks all five body balances and finite-idler route geometry.
`node verify-projects.cjs` checks migration/persistence safety; after Setup, run
`.venv/Scripts/python.exe verify_dynamics.py` for exact square, independent heave,
source parity, event continuity and cross-engine refinement checks.
Run `.venv/Scripts/python.exe validate_static.py` for both engines' actual
flat-input holding runs against Jon's original HTML; see the
[static-limit comparison](static-validation.md) for results and load mapping.
Run `python preview.py start --no-browser` for HTTP readiness without opening a
browser. See [context](context/README.md) for actual verification and handoff.

## Native equilibrium and vertical-chassis workspaces — 2026-10-22

All tabs use Kinefold's own interface. Actual terrain contact is a separate saved
Pymunk mode; see [contact model and checks](terrain-contact.md). The retained finite-idler equations are
reference evidence, attributed above; no source app or copied tab is embedded.
Equilibrium evaluates the current builder with cached finite samples: 480 intervals
for working peaks/loading curves, 720 or more for kinematics, and 180 for α/β.
Five body diagrams and exact spring-route detail accompany all17 reference plots.
The sampled peak is not a certified global maximum.

The original prescribed-height bench uses both dynamic engines with one saved mechanism and profile. The chassis mass m1
moves vertically with fixed horizontal position and pitch, while wheel height
is prescribed. No guide rods are drawn. Analytical dynamics use reduced equations;
Pymunk integrates a real vertically constrained chassis body, with the ideal
transmission and moving-body inertia condensed into its force law. It is not
an all-body rigid linkage, tire/collision or whole-vehicle simulation.

V4 baseline /150mm square keeps m1=8.75kg, all other masses zero and adds no
rotor inertia or damping. Its input is150mm high,150mm wide with150mm gaps,
default speed100mm/s and initial delay0.5s. Run duration6.5s covers two cycles.
Zero transition distance applies exact square events: chassis height and velocity
remain continuous while the ideal massless linkage can change pose instantly.
Do not interpret edge angular rates as finite peak jump speed. Positive moving
inertia or damping requires a declared finite transition distance; quintic ramps
lie inside the nominal plateau. Requested and applied traces are both retained.

The world-frame preview uses one fixed camera over the full trajectory, a moving
chassis mass marker and horizontally translating prescribed spatial floor. It preserves +x left,
+z up and +y toward the viewer. It does not render guide rods or pretend the base
input is rolling collision terrain. Native expandable categories contain17 matching dynamic plots for motion,
kinematics, forces and energy/numerical checks. A paired run captures identical
inputs once and compares exact time/event-side samples with overlays and errors. Reactions supply support dynamically; weight reference is not applied
again as an extra gravity-sized force. Nonweight builder loads remain additional.

Projects use kinefold/project-v3, including all geometry, view and input/run
settings. Version2 fixed-hip projects retain exact geometry and an archived
legacySolverConfig; their original browser keys remain untouched. Migration
notices identify the change in boundary conditions. Legacy positive-mass designs
receive a declared10mm finite transition with no mass substitution. Export
project JSON for portable backups. Profiles are local app-folder files, not cloud storage.

Each run captures the full project/profile and preserves rows, world frames,
exact jump events and diagnostics. Result labels identify the captured design;
geometry/profile edits mark old results stale. JSON run export contains the
snapshot and engine output; CSV contains rows. No hardware validation is implied.

Same-origin POST /api/dynamics accepts engine/params/runConfig and invokes
dynamics.py --request-stdin using this app's isolated .venv. Run
[Setup Kinefold.cmd](Setup%20Kinefold.cmd) once with Python3.12+ for pinned
SciPy/Pymunk. Builder/equilibrium preview needs standard-library Python3.10+.
The existing Start/Stop launchers preserve4191 and support readable errors and
restart without Codex. No boot/login automation is installed.


## Dynamic comparison, desktop viewer and app-folder files

Read [dynamic analysis](dynamic-analysis.md) for plot definitions, event-aware
comparison, shared playback time and spatial-floor conventions. Run both & compare
uses one captured mechanism/profile; mismatched/stale data is blocked. Comparison
JSON includes both snapshots and raw results. Requested sharp and applied finite
profiles move right (−x), synchronized to time and the exact wheel-height input.
This adds no collision/rolling model.

Open desktop Pymunk launches a real Tk results-playback window after computing
the captured case with Pymunk. It shows actual chassis frames and ideal linkage,
with pause, scrub and replay. The app owns one closable process; Stop Kinefold
also closes it. No new package dependency is required on this verified Python/Tk
installation. Failure/status messages identify missing runtime or opening errors.

Named designs and the exact working copy now live in [profiles](profiles/README.md),
with atomic revision-checked writes. Initial migration retains the original
browser keys and writes an immutable profiles/browser-backup.json; another browser’s
old designs can be recovered explicitly without replacing current disk data.
All project, equilibrium, dynamic and comparison exports write into
[exports](exports/README.md), with a saved relative path shown in the app. Export
buttons no longer send files to Downloads. These generated JSON/CSV files are
ignored by Git and remain on this PC after Codex/server shutdown. The five known
older QA downloads were moved into .preview/recovered-downloads inside this app;
unrelated Downloads files were untouched.

Developer checks: node verify-dynamic-analysis.cjs --real checks paired actual
baseline trajectories and frontend/Python input-law parity; node verify-projects.cjs
checks browser-to-disk migration and failure safety. App .venv Python
verify_profiles.py tests atomic files/revisions/exports, and verify_viewer.py --gui
runs actual native Pymunk/Tk lifecycle and controls. Hardware remains unvalidated.


## Actual wheel / terrain contact

Use **Save & open contact demo** in Pymunk or the studio library to create a separate
saved V4 profile with the explicitly selected1.5 kg wheel, μ0.8, zero bounce and
freely backdrivable drive. The original200 mm radius, link geometry, masses and
spring remain unchanged; prior named designs and the working snapshot are retained.
This mode has an actual circular wheel, frictional collisions and a translating
world square mesh. Wheel spin and height come from the engine; corners and150 mm
gaps can be bridged. The original height-driven/K=0 bench remains available.

The exact two-body model supports massless equal links/2:1 guide on a nonsingular
straight path, with positive chassis/wheel masses and uniform wheel-disc inertia.
Unsupported curved paths, extra link/custom wheel inertia and prescribed contact
loads fail explicitly. No substitute masses are added. Contact mode runs in both independent engines with exact saved-profile comparison;
the original prescribed-height benchmark remains a separate interaction model. Browser/native playback uses actual
world mesh/body transforms, backdriven pulley indices and moving belt markers.
Read [terrain-contact.md](terrain-contact.md) for equations, limits and actual
friction/corner/refinement evidence. Profiles/exports stay in the app folders.

## Contact cases and energy studies — 2026-10-23

Both dynamic tabs now solve actual contact for the same saved mechanism/material.
Choose Terrain stability, Jump or Landing in the shared case selector; jump and
landing use a stationary flat floor, physical inelastic travel stops and explicit
motor/hold/braking commands. User-supplied underside offset50mm is editable.
The energy option separates chassis½mv², wheel/spring/gravity energy and actual
motor∫τdθ; bounded landing torque assessment reports tested feasibility/brackets.
Read [contact-scenarios.md](contact-scenarios.md) for independent-engine equations,
case/controller definitions and limits. Legacy named profiles remain unchanged.


## Optional geared hip motor — 2026-10-23

Both dynamic tabs share a saved **Hip motor, gearing & losses** section and
Plotly result category. Enable explicit motor-side rotor inertia, conservative
sinusoidal cogging, smooth Coulomb friction and viscous losses; choose joint-side
or motor-shaft torque inputs. Reduction converts speed by N, torque by N and
inertia by N². Existing profiles retain their ideal actuator until edited.
Legacy joint inertia/damping stay additive, and the wheel drive remains free.
Read [motor-model.md](motor-model.md) for phase/units, coupled contact inertia,
numerical guards, energy accounting and native ABI limitations.


## Energy-only drop calculator — 2026-10-23

Both dynamic tabs offer an instant **Energy only · drop height → braking torque**
calculator without a simulation run. It uses saved chassis/spring/motor geometry,
separates the50mm ground-clearance target from the underside offset, and reports
joint/shaft resisting magnitudes, available stroke and endpoint drop capacity.
The explicit editable1° stop reserve is an illustrative margin. A Plotly curve,
work breakdown and app-folder export accompany the result. This conservative
initial-arrest work screen does not change dynamic controller torques or certify
impact peaks/holding. See [energy-calculator.md](energy-calculator.md).

## Visible jump/drop targets and torque sizing — 2026-10-23

Jump and Landing now show their parameters directly below the case selector in
both dynamic tabs. Set jump rise above takeoff, or drop height and minimum
underbody clearance, then **Solve torque for target**. Each tab searches actual
trials using its own engine and reports a passing tested command, achieved height
or clearance, and a lower known-failing bracket when available. **Use tested
torque** applies the captured command explicitly; run both engines normally to
compare that same command. Saved targets, energy estimates, indeterminate trial
handling and first-flight/first-arrest limits are documented in
[target torque decisions and checks](target-torque.md).
