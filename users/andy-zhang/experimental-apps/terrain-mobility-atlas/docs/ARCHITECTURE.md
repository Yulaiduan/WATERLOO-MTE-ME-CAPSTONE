# Architecture and model contract

The atlas now has a simplified interface while retaining the deterministic screening modules described below. A separate implemented numerical tool is built at `/workbench/`; its [architecture](workbench/ARCHITECTURE.md) documents the reduced physics and evidence adapters. Vite emits both `index.html` and `workbench/index.html`.

Current atlas UI retains vehicle inputs, region/cell selection, map, constraint inspector and one selected-scenario JSON export. It removes presentation coverage/upgrade/baseline boards, extra map layers and the illustrative profile CSV. Underlying model coverage/comparison functions and tests remain available as software APIs. The first-iteration UI/export details below are historical and do not describe removed controls.

## Runtime

| File | Responsibility |
| --- | --- |
| `index.html` | Page metadata and Vite entry point. |
| `src/main.js` | State, HTML rendering, events, MapLibre initialization/layers, dialogs, storage, and downloads. |
| `src/style.css` | Theme tokens, layout, controls, dialogs, responsive behavior. |
| `src/model.js` | Vehicle defaults/presets, controls, normalization, evaluation, coverage, comparison. |
| `src/data.js` | Sixteen assumed envelopes, deterministic variation, geometry, spherical area, default selection. |
| `public/countries.geojson` | Bundled Natural Earth context; geography does not drive terrain values. |
| `tests/model.test.js` | Model precedence, boundaries, area accounting, upgrades, geometry, and input normalization. |
| `vite.config.js` | Local server on 127.0.0.1:5173, fixed port, build configuration. |

MapLibre loads asynchronously so the numerical interface renders independently of its engine. Version 6 uses namespace/named exports; initialize from the imported namespace rather than a presumed `.default`. Its worker is imported using `maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url` and registered with `setWorkerUrl`, following the [official Vite ESM installation guidance](https://maplibre.org/maplibre-gl-js/docs/). Vite emits the local worker bundle; relying on module URL auto-detection failed for prebundled modules, while a plain `?url` import would leave production shared imports unresolved. The map uses local GeoJSON, not remote tiles. If map startup or rendering fails, scenario controls and results remain available, a map message is shown, and the original error is logged rather than attributing every failure to WebGL. Downloads use Blob/object URLs that are revoked after use.

```text
Assumed envelopes → synthetic cells → evaluate(cell, vehicle) → map / inspector
Current scope + vehicle + baseline → coverage / comparison → metrics / upgrades
Controls → in-memory state → render
Vehicle → localStorage (explicit save)
State + results → JSON download
Selected cell → illustrative profile generator → chart / CSV download
```

Initial `Scout 01`: grade 25%, cross-slope 15%, roughness 100 mm, obstacle 200 mm, minimum spacing 1 m, required corridor 1.2 m, and hard/mixed surfaces. Saved values are normalized: finite numbers clamp to control ranges, invalid fields fall back, names cap at 60 characters, and surface values are whitelisted.

## Constraint semantics

For grade, cross-slope, roughness, and obstacle height, demand must not exceed capacity:

```text
margin = (capacity - demand) / capacity
```

For spacing and corridor, available terrain distance must be at least the vehicle requirement:

```text
margin = (available - required) / available
```

Surface passes when its category belongs to the supported list. Null inputs are unknown. Numeric constraints fail below a `-1e-9` floating-point tolerance, are near-limit below 0.15 headroom, and otherwise pass. Equality is feasible with zero margin and is near-limit.

Precedence: any failure → fail; otherwise any unknown → unknown; otherwise any near-limit → near; otherwise pass. Pass and near count toward feasible coverage. Displayed margin is rounded minimum normalized headroom as a percentage; failed results show zero, unknown results null. This is not probability or a physical vehicle simulation.

## Geometry and coverage

`data.js` creates 1,057 synthetic hexagons. A point-in-polygon check selects centres inside approximate scenario polygons. Positions determine repeatable numeric variation, not sampled elevation. Null inputs stay null, categorical surfaces stay unchanged, and corridor/spacing vary inversely to the other demands.

Area uses a spherical radius of 6,371.0088 km. Polygons are not clipped to land or exact scenario boundaries. Coverage sums each displayed footprint, including unknowns, and divides pass-plus-near area by total. It does not establish unique global land coverage or account for unsampled terrain. Comparison sums newly feasible and newly infeasible footprints under the same scope; changes are percentage points.

## Persistence and exports

`terrain-vehicle-v1` contains the explicitly saved vehicle in localStorage. Reload restores a normalized profile when parsing succeeds. Study scope, map layer, selected cell, and baseline are session state. Storage failure leaves controls usable; JSON is an alternate download.

Scenario JSON schema version 1 includes time, provenance, current vehicle, baseline, selected cell, region filter, view mode/layer, coverage, comparison, methodology/units/assumptions, and active cells with evaluations. No JSON import UI is implemented. JSON and CSV exports open a review dialog with metadata, file size, a readonly preview, a persistent download link, and a copy action with manual-selection fallback. JSON preview is bounded to 120 lines/12,000 characters and clearly marked shortened; download and copy retain the complete payload. Small CSV previews remain complete. If clipboard copying is unavailable, fallback reveals/selects the complete payload for manual copying. The dialog owns its Blob URL and revokes it on close.

Profile CSV fields are `distance_m,relative_elevation_m,provenance`: 251 samples at 0.2 m spacing over 50 m, all synthetic. The two-sine curve uses roughness as an amplitude input and a scaled grade term; it does not match the declared RMS or grade and cannot validate cell properties or dynamics.

## Existing evidence work

Runtime does not import `data/terrain/`. Preserved future adapter inputs:

- [Terrain data and profile specification](terrain-data-and-profile-specification.md): evidence categories, source limits, archetypes, transects, benchmarks.
- [Terrain simulation development plan](terrain-simulation-development-plan.md): mechanism, dynamics, actuator demands, validation stages.
- [USGS provenance](../data/terrain/usgs-shenandoah-provenance.json) and [1 km samples](../data/terrain/usgs-shenandoah-transect-1000m.csv): local DEM-derived evidence at source scale.
- [USFS benchmarks](../data/terrain/usfs-trail-benchmarks.json): published design guidelines, not measurements of all trails.
- [Terrain archetypes](../data/terrain/terrain-archetypes.json): synthesized design envelopes.
- [Evidence builder](../scripts/build_terrain_evidence.py): independent workflow, not run by Vite/startup.

## Measured-data extension

Add an adapter at the data boundary. Validate finite values, units, increasing profile distances, source resolution, and gaps. Preserve raw sources, time, datum, uncertainty, processing method, and evidence per parameter. Reject NaN, invalid units, and impossible geometry before `evaluate`; the current evaluator expects trusted records and null for missing data.

Use appropriate measured regional footprints/clipping before changing coverage claims. A 1 m elevation product cannot alone establish wheel-scale steps or roughness. A measured-slope/assumed-obstacle record remains hybrid. Integrate calibrated vehicle limits and surveyed routes before treating sliders as physically achieved hardware upgrades. Connectivity, heading, turning, collision, and access need separate modules.

If complexity grows, split main.js into storage/export adapters, map controller, and panel renderers while preserving the pure model API. The first iteration does not require that refactor.
