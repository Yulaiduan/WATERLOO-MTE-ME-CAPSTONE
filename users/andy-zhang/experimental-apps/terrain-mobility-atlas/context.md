# Terrain Atlas — portable development context

Owner: Andy Zhang. Updated: 2026-10-12. Status: member experimental app.

Start with [README.md](README.md), [AGENTS.md](AGENTS.md) and
[context/README.md](context/README.md). Laptop/setup/storage details are in
[the member handoff](../laptop-handoff.md).

## Maintained source and history

- Atlas: `src/`, synthetic capability/terrain screening and local country map;
  [architecture](docs/ARCHITECTURE.md), [decisions](docs/DECISIONS.md),
  [handoff](docs/HANDOFF.md), [validation](docs/VALIDATION.md).
- Reduced terrain workbench: `src/workbench/`, prescribed spatial terrain/speed,
  two-mass suspension and unilateral compliant tire force;
  [architecture](docs/workbench/ARCHITECTURE.md),
  [handoff](docs/workbench/HANDOFF.md), [validation](docs/workbench/VALIDATION.md).
- Historical detailed linkage: `src/linkage/`, fixed-pivot guide and independent
  coaxial wheel drive; [model](docs/linkage/MODEL.md),
  [handoff](docs/linkage/HANDOFF.md), [validation](docs/linkage/VALIDATION.md).
- [Import record](docs/IMPORT-2026-10-10.md) preserves the old workspace's provenance.
  Small runtime DEM/provenance inputs are in Git. The four ignored large
  PDF/synthetic-CSV inputs match hashes in the [legacy archive](../capstone-archive/README.md)
  and can be restored without the PC. Original historical search/export helpers
  also remain in that archive with exact bytes.

The current wheel-height/Pymunk experiments and new link sizing are in
[Motion Lab](../wheel-leg-lab/context.md). Geometric capability margins and
reduced simulations do not establish whole-robot/hardware performance.

## Independent startup

From this app: `npm ci`, `npm run build`, then **Start Terrain Atlas.cmd**.
It finds installed Node.js on PATH, verifies the actual production routes at
127.0.0.1:4175, and preserves the host/port on restart. **Stop Terrain Atlas.cmd**
checks PID, creation time, recorded executable, app folder and Vite/port arguments
before stopping only this server. These are the standalone atlas launchers.

The familiar **Start Capstone.cmd**, **Start Force Plots.cmd** and **Stop Capstone.cmd**
remain compatibility aliases to the Motion Lab menu at port 4186. The optional
Motion Lab legacy service also uses 4175; only one service can own that port.
The maintained atlas at 4175 and main Motion Lab at 4186 can coexist.

Atlas vehicle profiles are browser-local. Download/import their JSON if wanted
on the laptop; source, history and defaults do not depend on that storage.
