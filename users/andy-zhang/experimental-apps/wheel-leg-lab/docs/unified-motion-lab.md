# Unified Motion Lab

Owner: Andy Zhang. Updated: 2026-10-10. Status: experimental motion workspace.

## Browser workflow

Use **Start Motion Lab.cmd** in the app root, wait for Ready and open
[http://127.0.0.1:4186/](http://127.0.0.1:4186/). The main menu hosts:

| Section | Model and outputs |
| --- | --- |
| Mathematical model | Independent Python/SciPy energy ODE, instantaneous joint/driver forces, torques, motion and energy; equivalent MATLAB ode45 source is downloadable |
| Detailed linkage, within mathematical tools | Existing two-coordinate guide/independent-drive model, dynamics, inverse demand and local poles/Bode analysis |
| 2D physical model | Actual Pymunk space, spring, pivots, guide and travel limits; recorded solver impulse loads and motion |
| Miscellaneous studies | Wheel/link ratio calculator, seven pulley/linkage motion studies and recorded Pymunk playback |
| Profiles & data | Browser-local profile/run library, JSON import/export, numeric channels, Plotly inspection and complete table CSV |

The persistent **Show Pymunk visual GUI** button opens actual captured engine
shapes/constraints and playback controls. Mathematical runs never masquerade as
Pymunk: opening their GUI runs the Pymunk backend with the corresponding flat
wheel-height profile. The independent-drive linkage is a different model; its
Pymunk viewer remains the separate wheel-height fixture, not a two-axis physics
implementation. The native desktop debugger is retained as **Open Native Pymunk
Debugger.cmd** for optional local inspection.

Dark mode is explicitly selected and shared with embedded benches/studies.
All quantitative charts use locally bundled Plotly 3.1.0, including time histories,
force/travel, wheel-path families, torque–speed, poles/Bode and the data browser.
Charts support zoom, pan, reset and image export. Mechanical diagrams remain
animated mechanism drawings. Plotly is generated from the pinned npm dependency,
not a multi-megabyte tracked blob or a mandatory runtime CDN request.

## Profiles, data and units

Save a **profile** for current input settings; save a **run JSON** for complete
recorded outputs. Successful embedded runs are also appended to IndexedDB.
The library is local to this browser and origin. Download JSON for a portable
backup or transfer; no cloud synchronization or remote upload is performed.
Records have unique IDs and never replace an earlier run. Clearing browser site
data can remove the library, so JSON exports are the durable backup.

The importer accepts versioned profile/library records, complete SciPy/Pymunk
results, detailed-linkage run packets and MATLAB ode45 numeric-column JSON.
MATLAB columns are preserved and exposed as plot-ready rows. Detailed comparison
modes become distinct tables rather than one discontinuous concatenated curve.
Miscellaneous studies also export their controls/widget state and displayed
Plotly samples as JSON. Restore saved study settings through the data browser;
these records stay separate from runnable solver profiles. Pure mechanism
animations save settings, while ratio/path-family/recorded plots also save data.
Row-only JSON remains read-only data without an invented runnable configuration.
Malformed/nonfinite/unsafe payloads, unknown schemas and oversized JSON are
rejected. Backend controls/API perform the full model-specific validation.

Internal inputs use m, kg, s, rad, N and N m. The UI converts mm/degrees and
also displays force in N/kgf. Reference belt T₀ remains independent and is
retained with saved profiles without being applied as a suspension force.
The data browser retains source values/units and shows model/configuration/scope.
Its previews are short; JSON/CSV preserve full recorded outputs.

## Independent equations and comparison

Read the [mathematical model](../math/README.md). SciPy DOP853 integrates the
scalar equal-link energy equation independently of Pymunk. It supports the
floating chassis with prescribed smooth C2 wheel height, real spring leverage,
wheel-lock inertia and optional clipped knee impedance. Mathematical stops
terminate before impact. Pymunk's rigid stops produce solver constraint impulses.
Output cadence dt in SciPy is not its adaptive internal integration step.

**Run both & compare** sends the same profile to the two backends, saves both
results and overlays chassis displacement/input. These are numerical checks of
ideal models, not hardware or canonical robot validation. Neither wheel-height
fixture solves unilateral tire contact, explicit belt elasticity or beam stress.

## Architecture and compatibility

`web/index.html`, `motion.js` and `motion.css` own the shared menu. The backend
pages `/mathematical/` and `/physics/` share `app.js`; `/linkage/` retains its
detailed controls. Embedded pages exchange same-origin run/profile/theme/height
messages. `library.js` and `data-browser.js` own IndexedDB and imports/plots.
`theme.js` handles standalone/embedded theme and sizing. The backend serves
`/api/math/simulate` separately from `/api/pymunk/simulate`; the old
`/api/simulate` physical endpoint remains compatible. Locks are per solver.

The old browser `.cmd` names forward to the canonical Motion Lab launcher,
including the imported Capstone/force launchers. Source and legacy standalone
PowerShell services remain preserved; existing port-4175 terrain pages can still
be served independently. The normal browser entry is now one port-4186 menu.
Old source/archive files are retained; no boot/login automation is added.

## Actual verification

- 37 Python tests pass: 27 existing physical/reference checks plus 10 independent
  mathematical checks, including energy and timestep/load convergence.
- 32 JavaScript tests pass: 24 detailed mechanics plus eight profile/data contracts.
- MATLAB R2025b Update 3 batch comparisons pass: default step differs from SciPy
  by at most 8.40e-8 degrees / 1.18e-6 N knee load; locked-square/clipped-impedance
  case also agrees. Octave is untested.
- Browser checks pass the unified menu, APIs, paired comparison, actual engine
  viewer, zoom/theme persistence, JSON/library/load/reload, imported-data errors,
  motion studies and mobile layout. Detailed Plotly geometry/response/poles/Bode,
  image/JSON exports and embedded profile controls were checked independently.
- Legacy Pymunk/calculator/study browser suites pass with Plotly selectors;
  recorded remote JSON remains byte-identical.

Dependencies are pinned: NumPy 2.5.3, SciPy 1.18.1, Pymunk 7.3.0, Plotly 3.1.0,
Vite 7.3.6 and Playwright 1.62.1. `pip check` reports no broken requirements;
npm installation audit reported no vulnerabilities. Build/launcher and repository
scope checks are rerun before publication. Canonical assets/shared runtime remain
unchanged; workspace scope is explicitly not a canonical physics pass.

The canonical launcher passes actual start/reuse/scoped-stop/restart from an
unrelated Windows directory. The old Pymunk/geometry/Capstone/force command names
reuse that same verified service. Production Vite/gallery builds pass without
runtime CDN dependencies; the final detailed module waits for local Plotly and
announces readiness before accepting a queued profile.

Primary API references: [Plotly chart configuration](https://plotly.com/javascript/configuration-options/)
and [SciPy solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html).
