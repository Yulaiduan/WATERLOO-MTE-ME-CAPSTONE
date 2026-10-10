# Validation record

Author: Andy Zhang with Codex. Updated: 2026-10-09. Status: locally checked member experiment, not canonical robot or hardware validation.

## Rebuilt import

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

## Physics interpretation and repository scope

Independent Pymunk angle errors decrease at 2/1/0.5/0.25 ms: approximately 0.175/0.089/0.044/0.022° in the mild-impulse case. A locked-contact case also agrees with an independent energy model including wheel inertia. Checked force/moment residuals are below 1e-7. Rigid-stop peak loads remain timestep dependent.

The fixed 4:1 example retains about 42.35 mm working travel with less than 0.768 mm ray error, not global straightness or collision-free inversion. The reference sheet's two torques reproduce with inferred 400 mm links/200 mm radius, not independently confirmed dimensions or belt-bearing loads.

With shared documentation indexes, publication uses preliminary scope. Repository regressions ran 36 tests: 34 pass and two MuJoCo fixture tests are skipped because the global environment lacks MuJoCo. These skips are not canonical physics passes. The shared manifest stays empty and unchanged; canonical physics is not applicable to this isolated toolkit. Architecture, link/log checks and the scoped gate must pass before publication.

Untested: hardware, real belt pretension/elasticity, tire/terrain/soil contact, structure/buckling, inversion clearance, GPU performance, other operating systems, and missing T₀/pulley/component limits.
