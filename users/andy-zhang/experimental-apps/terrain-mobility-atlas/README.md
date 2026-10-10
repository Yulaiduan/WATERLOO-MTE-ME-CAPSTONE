# Terrain Mobility Atlas and Workbench

Owner: Andy Zhang. Imported: 2026-10-10. Status: member experimental app.

This is the former loose Capstone app, preserved inside the GitHub member
workspace. Normal browser command names now forward to the unified
[Motion Lab](../wheel-leg-lab/README.md) menu at **http://127.0.0.1:4186/**.
Set up that app with Setup Motion Lab.cmd; Start Capstone.cmd and Start Force
Plots.cmd are compatibility aliases. Stop Capstone.cmd stops the Motion Lab.
Its mathematical/physical/study/data UI is documented in the
[unified workflow](../wheel-leg-lab/docs/unified-motion-lab.md).

The original standalone atlas/workbench source and port-4175 routes remain
available through Start-Capstone.ps1 / Stop-Capstone.ps1 after this folder's
`npm ci` and `npm run build`. These preserved legacy helpers operate that
separate service; the familiar browser .cmd names open the unified menu.

Read [app instructions](AGENTS.md), [context](context/README.md) and the
[import verification](docs/IMPORT-2026-10-10.md). The current Pymunk bench is
[Motion Lab](../wheel-leg-lab/README.md), using port 4186. Its common browser
entry requires one launcher; standalone services reject unrelated port owners.

All original loose files remain in the sibling local Capstone_Old archive.
The [GitHub archive package](../capstone-archive/README.md) also preserves full
historical source, large evidence and outputs. Installed dependencies/logs stay
local. Large evidence and original review outputs in this working copy are
ignored; a fresh clone can restore them from the archive into a new directory.

The dated notes below describe earlier iterations; the import record documents
fresh checks. These models do not validate the team's canonical robot.

---

# Terrain — Mobility Atlas

## Pymunk spring linkage bench

The actual Python rigid-body bench is in [Wheel Leg Lab](../wheel-leg-lab/README.md). Double-click [Start Pymunk Linkage.cmd](../wheel-leg-lab/Start%20Pymunk%20Linkage.cmd) to open [http://127.0.0.1:4186/](http://127.0.0.1:4186/). It models the grounded 2:1 guide, a 200 mm-radius wheel, and a hip-to-lower-link spring attached 50 mm past the knee. The maintained bench provides prescribed wheel-height step/square/pulse inputs with a floating chassis, animated solver states, pin forces, separate torque channels, pin and knee velocity/acceleration, full CSV traces and saved run configurations. Its server and stop launcher are independent of the Vite previews.

## Animated wheel-leg force plots

Double-click [Start Force Plots.cmd](Start%20Force%20Plots.cmd) in this project to open [force plots](http://127.0.0.1:4175/force-plots/). It starts or reuses the verified Capstone preview and verifies the actual force page before opening it. Stop with `Stop Capstone.cmd`. The saved page and D3 library work offline and survive closing Codex or restarting Windows.

Compare three equal-link legs sized for the same vertical travel, with synchronized geometric playback and markers on force-versus-angle and force-versus-travel plots. Wheel radius (150–250 mm), required travel, hip output torque, lower angle and widest upper angle are editable. The default torque is 1 N·m, so initial force values are capacity per unit hip torque. Radius and travel are independent; the initial 200 mm of each retains the design notes' preliminary assumption.

The model uses an ideal 2:1 guide constraint, θ from horizontal, `h = 2 L sin θ`, and static capacity `F = τhip / (2 L cos θ)`. Each link is sized as `L = S / [2(sin θmax − sin θmin)]`. Travel-average force is `τhip (θmax − θmin) / S`, with radians. Optional dashed curves show the sketch's tangential projection `τhip cos θ / (2 L)`; those curves are not constrained-leg support capacity. Springs, gravity of moving links, friction, motor speed limits and dynamics are excluded. Playback is geometric motion rather than a dynamic simulation. The upper angle is capped at 85° to avoid the straight-leg singularity.

Validation: production build; browser numerical comparisons against the existing linkage Jacobian and numerical travel integration; radius/travel/torque edits; projection and visibility; animation, pause, scrubbing and complete cycle; 360 px layout and extreme geometry; offline load with no external requests; launcher start/reuse/stop/restart from `C:\Windows`. Browser verification is saved at `scripts/verify-force-plots.cjs`; reviewed views are in `artifacts/force-plots/`.

## Numerical workbench

**Restart after closing Codex or rebooting:** double-click [Start Capstone.cmd](Start%20Capstone.cmd) in this app folder. It verifies all three pages before opening [atlas](http://127.0.0.1:4175/), [workbench](http://127.0.0.1:4175/workbench/), and [detailed linkage](http://127.0.0.1:4175/linkage/), and reuses the same verified server if already running. Stop it with [Stop Capstone.cmd](Stop%20Capstone.cmd). The launchers use installed Node.js and the saved production build; errors remain readable and persistent logs are in `.preview/`. No login/startup automation is installed.

Launcher lifecycle verified October 4, 2026 from `C:\Windows`: actual batch start, repeat/reuse, scoped stop and restart all pass; both original routes and JS/CSS assets return HTTP 200. The detached server survives the calling terminal's exit and uses installed Node.js 22.20.0 independently of Codex.

The separate **Terrain Workbench** is available at [http://127.0.0.1:5173/workbench/](http://127.0.0.1:5173/workbench/). It provides terrain profiles, a belt-leg model, numerical histories, actuator demand and a readable calculation graph. Its reduced physics and terrain evidence are documented in [workbench architecture](docs/workbench/ARCHITECTURE.md), with [design](docs/workbench/DESIGN.md), [decisions](docs/workbench/DECISIONS.md), [validation](docs/workbench/VALIDATION.md), and [handoff](docs/workbench/HANDOFF.md).

Run all three tools with the same commands below. The atlas remains at `/`; the workbench is at `/workbench/`; the detailed mechanism simulator is at `/linkage/`. `npm run build` emits all three entry points. For a local production preview use `npm run preview -- --port 4175 --strictPort`, then open the desired route on the printed local URL. The tools are not published to an internet host by this build.

Current reviewed production preview: [atlas](http://127.0.0.1:4175/) and [workbench](http://127.0.0.1:4175/workbench/). Checks: 25 tests pass, both entries build, audit reports zero vulnerabilities, and targeted browser review verifies terrain sources, numerical runs, graph selection and compact layouts. Export contents are verified; native in-app download completion remains unverified. The workbench supports reduced single-corner screening; completed runs do not establish motor, thermal or structural suitability.

**Current redesign, 2026-10-02:** a simpler PostHog-inspired terrain atlas alongside a separate numerical workbench. See [Decisions](docs/DECISIONS.md), [Design](docs/DESIGN.md), [Architecture](docs/ARCHITECTURE.md), [Validation](docs/VALIDATION.md), [Handoff](docs/HANDOFF.md), and [Third-party notices](THIRD_PARTY_NOTICES.md).

The earlier atlas review is retained as a dated record in [Validation](docs/VALIDATION.md). Current redesign and workbench checks are recorded separately there and in [workbench validation](docs/workbench/VALIDATION.md).

A local interactive design sandbox for screening a vehicle capability envelope against illustrative terrain scenarios. Built with Vite, vanilla JavaScript, and MapLibre GL JS.

## Detailed linkage simulator

The [detailed linkage bench](http://127.0.0.1:4175/linkage/) models the belt mechanism from the rough-animation chat: fold `q`, an independent coaxial drive input `phi`, a grounded guide that constrains lower-link orientation, two carrier-relative wheel-drive belts, and a physical passive spring in parallel with MIT-style fold control. It is a fixed-pivot mechanism model, with moving inertia, nonlinear spring geometry, load conversion and local dynamic analysis. It does not simulate a terrain-contact vehicle.

Read the [coordinate and force conventions](docs/linkage/MODEL.md), [architecture and startup](docs/linkage/ARCHITECTURE.md), and [validation evidence](docs/linkage/VALIDATION.md). Browser numerical workers keep the app self-contained; `ml-matrix` supplies local pole eigenvalue calculations. Offline `python scripts/validate_linkage_reference.py` independently checks selected mechanics using SymPy and SciPy; Python is optional and is not required by the launcher.

Current combined verification: **49 tests pass** across the three tools, all three production entry points build, and the dependency audit reports zero vulnerabilities. Three independent SymPy/SciPy cases agree with geometry, mechanics, ideal and finite-lag local modes, and frequency responses. Nondecaying modes and force-balance/saturation validity remain explicit in local analysis.

The linkage tool targets desktop use. Desktop mechanism editing, drive reference frames, all three simulation modes, MIT torque breakdown and local equilibrium analysis are reviewed. The launcher verifies all three routes and passes start/reuse/scoped-stop/restart from `C:\Windows`. See [the reviewed interface](evidence/linkage-ui/desktop.jpg) and [detailed validation](docs/linkage/VALIDATION.md).

## Run

```sh
npm ci
npm run dev
```

Use Node.js 20.19+ or 22.12+ and npm for the installed Vite 7 toolchain. Open [http://127.0.0.1:5173](http://127.0.0.1:5173). The server uses a fixed local port; stop any other server using 5173 before starting a second copy. `npm test` checks the constraint engine and area calculations. `npm run build` creates the production bundle in `dist/`; `npm run preview` serves it at the URL printed by Vite. No public hosting is configured.

## Included

- Interactive world map with public-domain Natural Earth outlines, bundled locally.
- Sixteen illustrative environments with 1,057 deterministic synthetic hexagonal terrain cells.
- Grade, cross-slope, roughness, obstacle height, spacing, corridor, and surface controls.
- Hard failure rules, explicit unknowns, and near-limit classification.
- Per-cell constraint breakdown and minimum normalized margin.
- Regional filtering, a selected scenario inspector, saved vehicle profiles, and compact JSON exports.
- Responsive layout and keyboard-operable controls.

## Interpretation

Terrain inputs and regional boundaries are **illustrative assumptions**, not satellite-derived measurements. Geography comes from Natural Earth, but it does not feed the terrain constraint values. Generated cells use deterministic variation of assumed biome scenarios.

An exceeded hard constraint makes a cell fail; missing critical evidence makes it unknown unless a known constraint already establishes failure. Passing within 15% of a threshold is marked near-limit. Margin is minimum normalized headroom, **not success probability**. Capabilities assume 1 m/s, fixed payload, no seasonality, and an assumed heading. Grade is a symmetric uphill/downhill percent limit. Roughness represents synthetic RMS over a 5 m detrended profile; step geometry is simplified.

Coverage is weighted by spherical hexagon area. Hexagons are not clipped to land or exact region boundaries. Coverage therefore describes the displayed sampled footprints, **not worldwide accessible land**. Passing cells do not establish route connectivity, steering clearance, turning feasibility, lateral stability, soil bearing capacity, traction, or legal access.

The atlas has no dynamics or terrain-profile sizing workflow. Use the separate workbench for profile generation/import and reduced numerical calculations.

Vehicle profiles are stored in localStorage on the current browser/device. Exports include model assumptions, units, source context, baseline, and cell-level results. They are downloads only; the app does not upload user data.

## Data and next integration steps

The measured-data preparation assets in `data/terrain/` remain the workbench's evidence inputs and are not imported by the atlas runtime. See the existing [Terrain data and profile specification](docs/terrain-data-and-profile-specification.md) and [Terrain simulation development plan](docs/terrain-simulation-development-plan.md) for the USGS transect, USFS benchmarks, and staged dynamics work.

The selected visual reference is the [PostHog demo](https://code.jiangshu.ai/awesome-design-html/assets/web/design.posthog.html) from [yzfly/awesome-design-html](https://github.com/yzfly/awesome-design-html). This independent Terrain adaptation has no PostHog affiliation. Reference attribution and MIT terms are retained in [Third-party notices](THIRD_PARTY_NOTICES.md).

Natural Earth 1:110m country outline source:
https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson

Natural Earth is public domain:
https://www.naturalearthdata.com/about/terms-of-use/

The current map has no remote tile dependency. Google Fonts is an optional network request, with local font fallbacks.

Future measured-data integration should preserve source/version, timestamp, resolution, vertical datum, uncertainty, and processing method per property. Replace assumed global geometry with regional screening from suitable elevation data; inspect local LiDAR point clouds before deriving wheel-scale obstacles. Land cover and predicted soils need calibrated mappings before interpreting them as mechanical surface capability. Validate on surveyed test routes and connect a vehicle model before labeling any upgrade as mechanically achieved.

Core modules:
- `src/model.js`: capability schema, feasibility, margins, coverage, comparison.
- `src/data.js`: synthetic scenarios, deterministic cells, spherical areas.
- `src/main.js`: UI, MapLibre layers, persistence, exports, dialogs.
- `src/style.css`: responsive layout and visual styling.
