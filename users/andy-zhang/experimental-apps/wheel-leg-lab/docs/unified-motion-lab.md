# Unified Motion Lab

Owner: Andy Zhang. Updated: 2026-10-10. Status: experimental motion workspace.

## Browser workflow

Use **Start Motion Lab.cmd** in the app root, wait for Ready and open
[http://127.0.0.1:4186/](http://127.0.0.1:4186/). The main menu hosts:

| Section | Model and outputs |
| --- | --- |
| Mathematical model | Independent Python/SciPy energy ODE for all nine wheel-leg spring presets; instantaneous forces, torques, motion and energy; original-spring MATLAB ode45 companion is downloadable |
| Constant-lift lever, within mathematical tools | Separate fixed-pivot lever with ideal gravity compensation, SciPy free dynamics, analytic prescribed-angle demand and actual Pymunk comparison |
| Detailed linkage, within mathematical tools | Existing two-coordinate guide/independent-drive model, dynamics, inverse demand and local poles/Bode analysis |
| 2D physical model | Actual Pymunk space, nine editable wheel-leg spring presets, pivots, guide and travel limits; solver impulse loads and motion |
| Miscellaneous studies | Wheel/link ratio calculator, seven pulley/linkage motion studies, constant-lift lever and recorded Pymunk playback |
| Profiles & data | Browser-local profile/run library, JSON import/export, numeric channels, Plotly inspection and complete table CSV |

The persistent **Show Pymunk visual GUI** button launches a **live native
Pygame/Pymunk window** with the selected wheel-height profile. That window builds
an actual Space and calls `Space.step(dt)` while running; it is not a replay of
browser frames. It opens on the simulation host's desktop, so a remote browser
requires access to that desktop to see it. **Open Native Pymunk Debugger.cmd**
remains a project-local alternative. The browser's separately labeled recorded
engine playback remains available for scrubbing completed outputs and remote
inspection.

Opening the native viewer from Mathematical tools runs the Pymunk backend with
the corresponding profile; it does not render SciPy as Pymunk. The independent
wheel-drive linkage is a distinct model with no two-axis native implementation;
select the wheel suspension model to launch that physical fixture.
The constant-lift lever selector launches its own live lever model, using the
same native-GUI controls with an explicitly separate profile envelope.

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
Optional guide baseline N/kgf and vector visibility are also saved under
`reference_inputs.guide_visualization`, independently of sheet T₀. Unknown
baseline means only the ideal guide tension difference is known; these viewer
arrows do not add forces to the solver.
The data browser retains source values/units and shows model/configuration/scope.
Its previews are short; JSON/CSV preserve full recorded outputs.

## Independent equations and comparison

Read the [mathematical model](../math/README.md). SciPy DOP853 integrates the
scalar equal-link energy equation independently of Pymunk. It supports the
floating chassis with prescribed smooth C2 wheel height, real spring leverage,
wheel-lock inertia and optional clipped knee impedance. Mathematical stops
terminate before impact. Pymunk's rigid stops produce solver constraint impulses.
Output cadence dt in SciPy is not its adaptive internal integration step.

The [spring catalog](suspension-presets.md) includes the original hip-to-tip
spring, six sketch mechanisms, internal knee captured pull-through and the
later `gravity_balance` upper-link attachment. Select
topology, compression/extension/captured coil law and direct/pullrod/ideal-rope
routing independently. Demo drum/crank/mount dimensions are editable and have
not been confirmed as hardware. Pull-through span growth compresses the coil;
mount geometry or pulley wrap determines which leg motion causes that growth.
Ideal rope is tension-only, zero-stretch and 100% efficient. The cranks/drums are
massless ideal transmissions with no friction, coil-bind or attachment-contact
model. Python supports all presets; MATLAB currently supports only
`legacy_tip` + captured + direct and rejects other combinations explicitly.

The [constant-lift study](constant-lift.md) derives the exact reference lever
and adapts its spring geometry to the guided wheel leg. The constant quantity
is equivalent elastic vertical lift; spring tension and moment vary with pose.
Zero effective input free length is separate from the positive physical coil
free length. Automatic wheel-leg balance calibrates stiffness for that law and
records the resolved rate. Ordinary finite-effective-free-length springs retain
angle-dependent residual demand. Exact undamped compensation is neutrally
balanced, providing no restoring ride-height stiffness by itself. The standalone
lever has separate free/prescribed-angle modes, profiles and backend records;
it has no MATLAB companion.

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

`/counterbalance/` uses its own controls and the APIs
`GET /api/counterbalance/defaults`, `POST /api/counterbalance/math` and
`POST /api/counterbalance/pymunk`. Its `counterbalance_math` and
`counterbalance_pymunk` run records enter the common profile/data library without
being mistaken for wheel-height runs.

`GET /api/spring-presets` returns the mechanism catalog and editable demo
defaults. `POST /api/native-gui` validates a Pymunk config and starts the
project-owned native viewer; `GET /api/native-gui/<id>` reports its status and
live step count. `POST /api/native-gui/<id>/show` restores only its verified
desktop window; foreground activation follows Windows' rules. Its
profile/status/log files remain in ignored `.preview/`.
Flat wheel configs remain compatible. Wheel launch can also use
`{model:'wheel_leg',config,guide_visualization:{pretension_N,show_force_vectors}}`
to preserve viewer-only assumptions. Guide metadata is validated separately,
included in reuse matching and not applied to solver pin/bearing loads. The
active frame supplies the global launch config; explicit saved-record/child
configs remain authoritative. Lever launch uses
`{model:'counterbalance',config:...}`. Free lever mode has one pivot constraint;
prescribed mode adds an actual velocity-driven SimpleMotor. Timestep-dependent
angle tracking and load peaks require refinement rather than exact pose claims.
The catalog/force-law kernel is standard-library geometry rather than a Pymunk
dependency in SciPy. All nine current Pymunk presets apply real point forces
before each step (`spring_integration=point_force`). The original DampedSpring
requires explicit `native_legacy`, restricted to captured/direct Hooke tip
spring, and warns about constraint/spring splitting bias. Refine physical dt
for stiff or sharp inputs before using their peak loads.

The old browser `.cmd` names forward to the canonical Motion Lab launcher,
including the imported Capstone/force launchers. Source and legacy standalone
PowerShell services remain preserved; existing port-4175 terrain pages can still
be served independently. The normal browser entry is now one port-4186 menu.
Old source/archive files are retained; no boot/login automation is added.

## Historical unified-release verification (2026-10-10)

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

### Historical preset/constant-lift releases (superseded defaults, 2026-10-10)

The earlier counts and browser/native checks above describe the preceding
unified release. The eight-preset expansion passed all 64 Python tests, including 12
mechanism-kernel, 15 independent mathematical and 10 preset-physics tests.
All eight presets pass real-backend browser checks, and the native API opens a
real desktop window with increasing solver steps, loops and graceful close.
Start/reuse/scoped-stop/restart passes from outside the app directory; the
[validation record](validation.md) records accuracy and limitations. MATLAB verification
remains scoped to the original captured/direct tip spring. This new work does
not upgrade the earlier numerical checks into hardware acceptance.

The subsequent constant-lift integration passes **82 Python tests** (71
wheel-leg checks and 11 standalone lever checks) and **33 JavaScript tests**
(nine library contracts and 24 detailed mechanics checks). Real-backend browser
checks pass all nine wheel presets, both lever APIs, JSON/library integration
and the unified menus. Actual native runs pass captured-knee, gravity-balance,
prescribed lever and free lever cases with live solver steps, window restoration,
looping and graceful close. The prescribed lever uses two constraints and the
free lever uses one; both render the actual three-shape model. The durable
launcher passes fresh start/reuse/scoped-stop/restart outside the app directory.
These historical checks retain their original scope; see [validation](validation.md)
for the latest evidence and limits.

Primary API references: [Plotly chart configuration](https://plotly.com/javascript/configuration-options/)
and [SciPy solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html).
Live engine references: [Pymunk Space/body APIs](https://www.pymunk.org/en/latest/pymunk.html)
and [Pygame DrawOptions](https://www.pymunk.org/en/latest/pymunk.pygame_util.html).

## Current replacement suspension architecture

The [replacement architecture](suspension-architecture.md) has a direct
`/?tab=physics&architecture=constant-lift` entry and a bridge from the lever.
It queues the factory profile before the first solve. One upper-link/chassis
unit replaces the old lower-tip spring; auxiliary is off and primary damping
is 100 N s/m. Exact elastic compensation is neutral, not a restoring ride spring.
Six actual sensor shapes include the chassis and 28/14 mm guide drums; twelve
Plotly charts separate elastic support, damping and dynamic loads. The recorded
coil/damper drawing uses the primary anchors and labels its ideal routing.

The optional earlier auxiliary restoring strut remains selectable and clearly
separate from the factory. [Mechanism audit](mechanism-audit.md) explains the
curated passive defaults and point-force integration. The latest
[validation](validation.md) owns solver/browser/native/launcher evidence and
finite-envelope limits; historical release counts above do not certify current
or edited configurations. MATLAB remains legacy-only.
