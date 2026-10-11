# Toolkit architecture

Author: Andy Zhang with Codex. Updated: 2026-10-10. Status: member experiment.

One loopback-only Python server serves the Pymunk API and all web routes. `motion_input.py` computes displacement/velocity/acceleration trajectories in SI. `physics.py` builds the actual space and records solver states; `debug_view.py` captures engine draw callbacks and object descriptions. `debug_gui.py` calls the same builder/input helper in a live Pygame viewer. Browser Pymunk motion is recorded playback, not a second physical model.

`scripts/record_position_preview.py` regenerates the embedded floating-chassis step/square traces and actual debug primitives. It decimates display frames and retains trace-bucket extrema; full solver exports remain available in the main bench.

The seven rough-motion HTML fragments and retained remote playback live under `animations/`. `scripts/build_animations.py` wraps them using local app-owned styles and a standalone state adapter, replacing D3's CDN reference with the local library. Generated `web/animations/` and `web/recorded/` remain ignored. The gallery links them to `/force-plots/`, the editable static calculator source.

The detailed continuous-mechanics solver is isolated under `src/linkage/`, with browser workers and ml-matrix. Vite builds its `linkage/index.html` into ignored `web/linkage/`, using a `/linkage/` asset base. The main Python server can serve those static bundles without importing that solver or sharing live physical state with it. See [detailed mechanics](linkage-model.md).

Python and Node dependencies are pinned in requirements/package manifests and npm's lockfile. The server and Windows launchers resolve paths from their own files. Port-specific PID/creation-time records prevent stopping a different app; 4186 is the unified toolkit, and 4175 preserves legacy geometry routes. No code in canonical simulation imports this member toolkit.

Experiments and all runtime exports go under ignored `artifacts/` or `.preview/`. The selected screenshot equations are compact reference sources, not canonical physical data. Private transcripts, environment binaries, node_modules and frame dumps are excluded from publication.

## Unified Motion Lab, 2026-10-10

The shared browser menu now separates independent mathematical simulation,
2D Pymunk physics and miscellaneous motion studies, with dark mode, Plotly
charts and a profile/data browser. Use Start Motion Lab.cmd at port 4186;
familiar browser launchers are aliases and the native debugger is preserved
separately. Full workflow, JSON contracts, MATLAB/SciPy agreement and current
verification are in the [unified workspace record](unified-motion-lab.md).

`spring_mechanisms.py` owns editable preset geometry and passive coil laws;
`suspension_runtime.py` applies their point forces to actual Pymunk bodies.
All nine current presets use explicit `point_force` integration and force/torque
ledgers. `native_legacy` preserves DampedSpring only as an advanced diagnostic
for the original captured/direct Hooke tip law; all require timestep refinement.
`math_model.py` integrates the independent SciPy equations with the same
specified geometry. See [suspension presets](suspension-presets.md).

`native_viewer.py` validates/builds the selected config, launches the installed
app-local Python/`debug_gui.py` process and monitors owned status files. It
opens a visible live Pygame window; no requested executable/path is accepted.
`native_suspension.py` adds schematic ideal routing/coil overlays to the actual
engine debug drawing. Recorded `/physics/?viewer=1` remains separate playback.

`counterbalance.py` owns the independent energy equation and actual Pymunk
single-lever experiment. `/counterbalance/` uses its own math/physical APIs;
versioned library backend IDs distinguish these configs from wheel fixtures.
The native launcher accepts a fixed `model: counterbalance` envelope to select
`debug_counterbalance_gui.py`; users cannot choose an arbitrary executable.
The main menu, theme, data library, port and manual restart launcher are shared.

`suspension_architecture.py` builds the replacement folding-leg profile: one
upper-link/chassis constant-lift unit, primary damping 100 N s/m, auxiliary off
and no knee controller. The optional earlier hip-to-tip strut stays explicit.
Chassis/guide sensors visualize existing bodies without changing mass/inertia.
Cold entry loads the factory profile before solving; the lever bridges to that
physical workspace. See [suspension architecture](suspension-architecture.md).

`guide_belt.py` and `web/guide-belt.js` compute matching exact tangent loops,
material motion and ideal torque-equivalent span-force difference;
`native_guide_belt.py` draws the desktop counterpart. Viewer baseline and force
visibility live in `reference_inputs.guide_visualization`, separate from solver
configuration and reference-sheet T₀. They are not applied spring/bearing loads.
Native wheel launch may use `{model:'wheel_leg',config,guide_visualization}`;
legacy flat wheel configs remain compatible. Only validated baseline/visibility
options enter the owned native viewer, and its reuse key includes those options.
The shell uses the active frame's latest config/references, or an explicit
selected record. Lever envelopes remain model-specific. Live status and owned
`/show` restoration are separate from recorded browser playback.

[Mechanism audit](mechanism-audit.md) owns current curated defaults and
integration rationale; [validation](validation.md) owns actual test evidence.

## Comparison and single-link force workspace, 2026-10-10

Math now hosts only the 2D SciPy suspension; the lever lives in Miscellaneous
and detailed linkage is archived there. Direct routes remain; historical
Math deep links translate to Misc. `web/comparison.js` mounts the workspace,
`web/comparison-data.js` owns pure unit/family/time matching and signed deltas,
and `web/comparison.css` styles recursive splits. Original records stay attached
to exported layouts. Profiles explicitly run their matching backend before
becoming plotted data. See [comparison contract](comparison-workspace.md).

The standalone lever defaults to free undamped motion with one PivotJoint;
only prescribed diagnostic mode adds a motor. Vertical end force acts at the
actual tip and enters energy/pivot/angular balances.
`POST /api/counterbalance/advance` validates supplied config/state/force and
advances an independent SciPy chunk without server-owned state. Browser pacing
and force history supply live interaction and portable replay. Wheel suspension
equations/damping are unchanged.
