# First-iteration handoff

## Current handoff supersedes the interface workflow below

The October 2 follow-up simplifies the atlas to vehicle controls, map, one selected scenario inspector and compact exports. Hero/rover art, global coverage board, upgrade cards and overlays have been removed. The separate numerical tool lives at `/workbench/`; see [its handoff](workbench/HANDOFF.md). Build both with `npm run build`, and run a local preview with `npm run preview -- --port 4175 --strictPort`. The current reviewed production URLs are [atlas](http://127.0.0.1:4175/) and [workbench](http://127.0.0.1:4175/workbench/); restart if the server has stopped. Current tests pass 25/25, build passes and audit reports zero vulnerabilities. Actual simplified view: [atlas screenshot](../evidence/workbench-ui/atlas-desktop.jpg). Current verification is recorded separately from the historical review below.

Date: **2026-10-02**, America/Toronto. This iteration applies the user's chosen PostHog UI language to the working Terrain atlas. Astra orchestrated/reviewed; three GPT-6.1 Sol workers implemented application, styling, and documentation changes. Autonomous choices are recorded in [DECISIONS.md](DECISIONS.md).

## Run and review

```sh
npm ci
npm run dev
npm test
npm run build
npm run preview
```

Working production preview: [http://127.0.0.1:4173](http://127.0.0.1:4173). Development URL: [http://127.0.0.1:5173](http://127.0.0.1:5173). Both were left running at handoff; restart if a later session has stopped them. Node.js 20.19+ or 22.12+ is required by the installed Vite toolchain. Use `npm ci` when dependencies are not installed; an existing dev server can be reused. Port 5173 is fixed. Preview uses the production bundle and prints its own URL.

The visual reference is the [PostHog demo](https://code.jiangshu.ai/awesome-design-html/assets/web/design.posthog.html). The locally captured reference is [posthog-reference.jpg](../evidence/ui-iteration-1/posthog-reference.jpg). Actual application screenshots: [desktop](../evidence/ui-iteration-1/terrain-desktop.jpg), [laptop](../evidence/ui-iteration-1/terrain-laptop.jpg), [mobile](../evidence/ui-iteration-1/terrain-mobile.jpg). Browser results: [VALIDATION.md](VALIDATION.md).

## Working workflow

1. Choose a vehicle preset or change capability sliders and supported surfaces.
2. Select a study environment or all scenarios; inspect the map or selected cell.
3. Read each constraint, primary limiter, evidence note, and area-weighted sample coverage.
4. Compare with a session baseline, apply an illustrative upgrade, and capture/restore a baseline.
5. Switch capability, biome, and evidence layers.
6. Save the vehicle locally or review/download the scenario JSON. View/download a synthetic profile CSV.

JSON/CSV exports open a review dialog with metadata, file size, and payload preview before download. Large JSON previews are clearly shortened to 120 lines/12,000 characters; download and copy keep complete contents. Blocked clipboard copying reveals/selects complete text for manual copying. Saved vehicle storage remains browser-local under `terrain-vehicle-v1`; comparison baseline and study state are session-only.

## Verified state

Final model tests pass 11/11, production build passes, and dependency audit reports zero vulnerabilities. Development and production browser review confirms geographic context and cells render after fixing the inherited MapLibre namespace-export and Vite-worker integration bugs. Desktop/laptop/mobile review found no horizontal overflow; presets, constraint changes, unknowns, upgrades, baseline capture, layers, saved-profile reload, and Methodology open/close were exercised. Fresh production logs contain no warnings/errors.

Complete JSON copying was verified and the parsed snapshot is saved as [verified-scenario.json (archived)](../../capstone-archive/README.md); profile CSV contents are saved as [verified-profile.csv](../evidence/ui-iteration-1/verified-profile.csv). **Native download-to-disk completion remains unverified:** the in-app browser verification timed out. The complete copy path and export contents are verified, so the reviewable snapshots are available even with that remaining browser-tool limitation.

## Material choices

- Keep the engineering workspace and adapt PostHog's cream/olive/orange, typography, flat borders, and compact chrome.
- Use original Terrain branding/rover artwork; preserve reference attribution and MIT terms.
- Retain the existing vanilla/Vite/MapLibre stack and deterministic 16-scenario model.
- Correct MapLibre 6 namespace/worker initialization and respect reduced motion in CSS and camera movement.
- Keep hard constraints and explicit unknowns; margin is normalized headroom, not success probability.
- Show area-weighted **sample** coverage; unknowns stay in the denominator and changes use percentage points.
- Keep environment and vehicle choices separate; a biome label does not establish mechanical performance.
- Preserve local profile persistence and add reviewable exports with units/provenance.
- Keep large JSON previews short and labeled; Download/Copy retain complete contents.
- Document decisions/design/architecture/validation and preserve earlier simulation/evidence work.
- Interpret “deploy 6.1 Sol agents” as agent dispatch. Deliver a local working application and build.

## What was not integrated in iteration 1

The measured terrain preparation pipeline, USGS transect, USFS benchmarks, archetype data, scripts, and two existing engineering Markdown documents are preserved. **There is no runtime import of that measured-data pipeline yet.** See [ARCHITECTURE.md](ARCHITECTURE.md#existing-evidence-work) for the inventory and links.

There is no dynamics engine, vehicle-mechanics calibration, route planner, account/backend, or public hosting. The synthetic profile preview is an interface example; its shape is not calibrated to the cell's declared RMS or grade. No slider adjustment establishes a physically achieved hardware upgrade. Hexagons remain approximate, unclipped footprints.

## Suggested next iteration

1. Define a baseline vehicle, payload, heading/speed conditions, and sourced capability limits.
2. Adapt one existing measured local transect and preserve evidence per parameter. Avoid presenting regional/small-scale DEM data as wheel-scale obstacle measurements.
3. Implement a parameter-controlled profile generator with declared grade, detrended RMS, wavelengths, step shape/spacing, and reproducible seed, separate from the UI example.
4. Follow the preserved simulation plan toward a validated single-leg sizing prototype; export reproducible SI-unit runs and compare demanded vs achievable actuator response.
5. Validate on surveyed routes before broadening coverage claims; add connectivity, heading, turning, and measured footprint handling only when evidence and scope support them.

Software checks and practical test limits: [VALIDATION.md](VALIDATION.md). Model/export extension contract: [ARCHITECTURE.md](ARCHITECTURE.md). Design rules: [DESIGN.md](DESIGN.md).
