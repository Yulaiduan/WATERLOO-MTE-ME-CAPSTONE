# Terrain Workbench decisions

- Keep the existing vanilla JavaScript/Vite project. Build a separate `/workbench/` entry so the numerical workflow does not alter the atlas's existing assumptions or interface.
- Use local ES modules and a simulation worker for numerical work. Introduce no web framework, cloud account, map or remote compute dependency.
- Build both HTML entry points with Vite's multi-entry Rollup configuration and root-relative module URLs. Production output includes `dist/index.html` and `dist/workbench/index.html`.
- Treat terrain evidence per parameter. Measured DEM elevation, historical trail guidelines, synthesized biome envelopes and chosen engineering cycles have different meanings.
- Preserve source resolution. Interpolating the 1 m USGS DEM does not create measured centimetre-scale roughness. User imports require units and explicit provenance; unavailable evidence remains unknown.
- Express motor demand at a named shaft. Torque–speed pairs are more useful than independent peak torque and peak rpm. The reduced model supports screening; structural, thermal and hardware suitability require additional evidence.
- Use a PostHog-inspired cream/olive/amber style, flat borders and plain controls. Prioritize clear axes, numerical tables and calculation dependencies over decorative interactions.
- Dispatching implementation subagents does not authorize public hosting. This delivery builds and serves locally; internet publication is a separate task.
