# Validation record

Author: Andy Zhang with Codex. Updated: 2026-10-10. Status: locally checked member experiment, not canonical robot or hardware validation.

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
