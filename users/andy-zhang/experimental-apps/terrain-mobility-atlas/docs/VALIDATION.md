# First-iteration validation

## Current redesign and workbench

The combined `npm test` suite passes 25/25 (11 atlas, 14 workbench), exit 0. `npm run build` also passes, exit 0, Vite 7.3.6, 19 modules; both atlas/workbench HTML entries and local simulation/MapLibre workers are emitted. Root observed atlas geographic rendering, missing-evidence behavior in Siberia, immediate grade-failure updates and selected-scenario JSON preview. Final production observations/screenshots will be recorded here and in [workbench validation](workbench/VALIDATION.md). All first-iteration checks below apply to the earlier interface and do not establish verification of the current redesign.

Current `npm audit --audit-level=high` passes, exit 0, reporting zero vulnerabilities.

Root's stable production review at `http://127.0.0.1:4175/` verified saved vehicle restoration after reload, Siberia missing-evidence status, grade 10 causing the Canadian Shield scenario to show Outside Limits, and full selected-data JSON preview. Compact atlas client/scroll widths were 360/360 px, with a 326 px map and no horizontal overflow. Actual current screenshot: [simplified atlas](../evidence/workbench-ui/atlas-desktop.jpg). New browser evidence applies to the current simplified interface, independently of the earlier screenshots below. Serialized export contents are verified; native blob download completion remains unverified because the in-app browser event wait timed out.

Validation date: **2026-10-02** (America/Toronto). Observed software checks do not validate assumed terrain or physical capability.

## Observed commands

| Check | Result | Notes |
| --- | --- | --- |
| `npm test` | PASS, 11/11, exit 0 | Documentation/review agent ran this during interface work. |
| Initial concurrent `npm run build` | Transient failure | Styles worker was replacing `src/style.css`; Vite observed it absent. Final completed-tree build required below. |
| Completed-tree `npm run build` | PASS, exit 0 | Ran after stylesheet landed; Vite 7.3.6 built 10 modules in 1.61 s. CSS 119.90 kB; initial app JS 46.71 kB; lazy MapLibre JS 1,064.17 kB before gzip. |
| Post-map-repair `npm test` | PASS, 11/11, exit 0 | Documentation/review agent reran after namespace/worker/motion changes. |
| Post-map-repair `npm run build` | PASS, exit 0 | Vite 7.3.6, 11 modules, 2.06 s; local worker 507.81 kB, CSS 119.90 kB, app JS 47.12 kB, lazy MapLibre JS 1,064.17 kB before gzip. |
| Documentation local-link probe | PASS | All local Markdown links across README, notices, and five new docs resolve. |
| Final `npm test` (root) | PASS, 11/11 | After final export and mobile-layout polish. |
| Final `npm run build` (root) | PASS | Local worker 507.81 kB, app JS 47.66 kB, CSS 120.00 kB, lazy MapLibre JS 1,064.17 kB before gzip. |
| `npm audit --audit-level=low` (root) | PASS | Zero reported vulnerabilities in the installed dependency set at validation time. |
| Module inventory probe | PASS | 16 scenarios, 1,057 cells; default global sample coverage 20.6075712458%, describing synthetic sampled area only. |

Tests cover hard cross-slope precedence, missing evidence versus known failure, surface failure, inverse boundaries, limiting margin, area-weighted unknown denominator, gained/lost area, monotonic improvements, latitude-sensitive area, deterministic geometry, and saved-profile normalization.

## Final checks

Final tests, build, audit, and production-preview review pass. Browser QA uncovered two inherited MapLibre 6 integration failures: `.default` was undefined, and worker auto-detection failed for Vite's prebundled module URL. The application worker changed initialization to namespace exports and the official `?worker&url` import/`setWorkerUrl` setup, with a separately emitted local worker, and improved map failure reporting. Root then verified geography in development and production preview. This shows why a successful bundle alone was insufficient to establish working geography.

## Observed browser QA

Root inspected the actual development app after the MapLibre repairs:

| Check | Observation |
| --- | --- |
| Map runtime | Geographic fills and synthetic cells render. Clicking a Sahara cell on the canvas updates the inspector to Sahara / Outside assumed limits. |
| Desktop layout | 1440 × 1000, no horizontal overflow; viewport production capture [terrain-desktop.jpg](../evidence/ui-iteration-1/terrain-desktop.jpg). |
| Laptop layout | 1080 × 900, no horizontal overflow; [terrain-laptop.jpg](../evidence/ui-iteration-1/terrain-laptop.jpg) saved. |
| Mobile layout | 390 × 844 viewport, actual client width 375 px, no horizontal overflow; six sliders reachable. [terrain-mobile.jpg](../evidence/ui-iteration-1/terrain-mobile.jpg) saved. Cramped upgrade strip was corrected to a grid with CTA below. |
| Preset | Compact crawler loads grade 40 and sample coverage 68.2%. |
| Saved profile | “Scout QA” survives reload. Original Scout 01 was reset/saved after the test. |
| Unknown evidence | Siberia scope reports 100% unknown. |
| Keyboard/model update | Home on Canadian Shield cross-slope sets 3%, produces blocked result and 0% passing regional coverage. |
| Upgrade/baseline | Loose-surface upgrade changes global coverage 20.6% → 45.5%, +24.9 percentage points. Capturing current baseline resets delta to 0.0. |
| Layers | Biome, evidence, and capability legends checked. |
| JSON review/copy | Shortened preview 2,622 characters / 120 lines; complete payload 4,007,566 characters. Copy JSON succeeds and complete payload parses: schema 1, 1,057 cells, default coverage 20.607571245801566%, units/provenance/mode/layer present. Saved [verified-scenario.json (archived)](../../capstone-archive/README.md). |
| CSV contents | Complete 251-sample preview spans 0–50 m with synthetic provenance. Saved [verified-profile.csv](../evidence/ui-iteration-1/verified-profile.csv). |

Application screenshots are ordinary viewport captures. A full-page capture distorted WebGL canvas sizing, so root replaced all three same-name screenshots with verified viewport captures using `getScreenshot`; this was a screenshot-tool issue, not an application rendering regression. Viewport overrides were reset and the production tab retained.

The JSON copy path and inspected payload are verified. Native browser download-to-disk verification timed out in the in-app browser, so file completion through the download link remains **unverified**; do not infer success from a click status. CSV contents are verified independently of that native download path.

## Production preview

Root verified the completed build at [http://127.0.0.1:4173](http://127.0.0.1:4173): all geographic context and hexagonal fills render; region-to-all transition and Fit all work; Methodology dialog opens and closes. Fresh production browser logs contained no warnings or errors (`[]`). The production tab is the review deliverable. The dev server at 5173 and production preview at 4173 remained running at handoff; temporary viewport overrides were reset.

This is a targeted first-iteration review, not a formal accessibility or exhaustive cross-browser audit.

## Limits

Tests exercise known model records, not measured terrain, GIS ingest, routing, or full browser interactions. No importer exists. No empirical validation, dynamics solver, traction/sinkage estimate, rollover calculation, or actuator sizing runs here. Existing evidence assets are future inputs. Font fallback and unavailable-WebGL paths are not fully tested unless explicitly exercised.
