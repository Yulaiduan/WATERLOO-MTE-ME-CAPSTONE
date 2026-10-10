# First-iteration decisions

## Superseding simplification, October 2, 2026

The user requested a simpler atlas and a numerical tool. The atlas now centers vehicle controls, map, selected scenario and compact export; marketing hero/rover presentation, global coverage board, upgrade cards and decorative overlays are removed. Preserve the underlying deterministic screening model and provenance. Add `/workbench/` as a separate entry for data-driven profiles and reduced single-leg calculations. No public hosting is implied. Decisions below are the retained first-iteration history; removed UI features are not current requirements.

Decision date: **2026-10-02**, using the user's America/Toronto date. The user requested the PostHog UI, a good working first iteration, autonomous routine choices, and Markdown documentation. Astra orchestrates; three GPT-6.1 Sol workers implement the application, styling, and documentation.

## Product and delivery

| Decision | Choice and rationale | Tradeoff / alternative |
| --- | --- | --- |
| Product shape | Retain the working Mobility Atlas and apply the chosen PostHog visual language. The map, envelope, inspector, and comparison are the core workflow. | A literal marketing-page clone would bury the engineering workflow. The reference informs structure, typography, surfaces, and accents. |
| Scope | Complete the interface iteration on the existing deterministic model and 16 scenarios. | Measured GIS ingestion, dynamics, routing, accounts, and public hosting are later work. |
| Framework | Retain vanilla modules, Vite, and MapLibre. | No framework migration or new UI dependency is needed; main.js remains the single-page orchestration module. |
| Runtime correction | Use MapLibre 6 namespace exports plus the official Vite `?worker&url` worker import and `setWorkerUrl`; show accurate map failure feedback and log the error. | Browser QA uncovered inherited default-export and worker-auto-detection failures. Bundle the worker locally without a CDN/dependency/configuration migration; a plain URL import would not correctly bundle production shared imports. |
| Deployment | Make the local app and production build reviewable. Interpret “deploy agents” as agent dispatch. | No public site deployment was requested or configured. |
| Documentation | Add decisions, design, architecture, validation, handoff, and notices; preserve prior engineering documents. | Avoid folding future simulation planning into claims about the current app. |

## Design and interaction

| Decision | Choice and rationale | Tradeoff / alternative |
| --- | --- | --- |
| Reference | Use the repository's PostHog demo and retain a local reference plus MIT license. | The demo is a third-party interpretation, not an official PostHog specification. |
| Visual language | Cream/olive neutrals, orange emphasis, readable sans text and monospaced engineering labels, flat panels, and fine borders. | Adapt a marketing reference to dense controls and a continuously visible map. |
| Fonts | Use IBM Plex Sans and IBM Plex Mono for the engineering workbench. | The selected demo loads Inter/JetBrains Mono; this intentional adaptation preserves the technical character with one coherent family. |
| Map and artwork | Warm parchment map, olive outlines, original Terrain rover SVG. | Keep the chosen palette without reusing a PostHog mascot or corporate artwork. |
| Reading/layout | Readable body and control text, responsive columns, and natural page scrolling. | Dense controls should not be compressed merely to fit one fixed-height viewport. |
| Motion | Respect reduced-motion in both CSS and map fit/fly camera duration. | CSS alone does not govern MapLibre camera animations. |
| Exports | Review metadata and a clearly labeled JSON/CSV preview before download; provide complete download/copy and a manual fallback. | JSON preview is bounded to 120 lines/12,000 characters for readability. Complete contents remain in download/copy; blocked clipboard reveals complete text for selection. |
| Vehicle vs environment | Vehicle presets change capabilities; environment selection changes the study scope. | A named biome does not mechanically establish the vehicle's limits or measured terrain conditions. |
| Persistence | Browser-local vehicle storage and downloadable exports. Comparison baseline is session state. | No account synchronization, multi-profile library, import workflow, or backend. |

## Engineering and evidence

| Decision | Choice and rationale | Tradeoff / alternative |
| --- | --- | --- |
| Engineering result | Keep hard constraints, fail-before-unknown precedence, 15% near-limit threshold, and minimum normalized margin. | A weighted score could conceal a blocking constraint. Thresholds remain assumed, not empirically calibrated. |
| Coverage | Use spherical area of current sample footprints; unknown area stays in the denominator. Report changes in percentage points. | Reproducible sample coverage is not global accessible land or route success. Unclipped footprints remain an explicit limitation. |
| Evidence | Keep runtime terrain labeled illustrative and preserve incomplete examples. Preserve measured-data assets separately. | The existing USGS transect and USFS benchmarks deserve future adapters; their presence does not make global scenarios measured. |
| Profile preview | Retain a deterministic synthetic 50 m profile as a CSV/interface demonstration. | It is not reconstructed from the map or calibrated to terrain grade/RMS; a specified generator belongs in the integration stage. |

## Retained assumptions

- Capability limits apply at assumed 1 m/s with fixed payload and heading.
- Grade is percent rise/run, with one symmetric ascent/descent limit.
- Cross-slope uses the assumed travel heading; no lateral stability solver runs.
- Roughness is described as synthetic RMS over a 5 m detrended window in screening inputs.
- Obstacle height represents a simplified perpendicular step; spacing and corridor use inverse inequalities.
- Surface support is categorical, with no traction, bearing capacity, or sinkage calculation.
- A passing local cell does not establish connectivity or legal access.

Update this log when behavior or scope changes. Link measured evidence to the relevant parameter rather than calling a whole biome record measured. Validation records distinguish command results, browser observations, and untested engineering claims.
