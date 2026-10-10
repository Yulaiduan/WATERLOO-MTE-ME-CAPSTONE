# Wheel Leg Lab

Owner: Andy Zhang. Updated: 2026-10-09. Status: experimental, combining **Create a rough animation** and **Optimize wheel-to-link ratio**. This member toolkit does not define or validate the team's canonical robot.

## Included tools

| Tool | Route | Content |
| --- | --- | --- |
| Pymunk spring bench | `/` | Actual rigid-body engine, 200 mm-radius wheel, 50 mm lower-link extension spring, impulse/square inputs, joint forces/torques, velocity/acceleration and native debug draw |
| Seven rough motion studies | `/animations/` | Moving-belt straight leg, independent coaxial drive, tilted/mirrored inversion, historical reindexing alternative, fixed 4:1 near-linear strokes and mathematical path family |
| Wheel/link calculator | `/force-plots/` | Radius 150–250 mm, independently adjustable travel, equal-link lengths, force curves and synchronized motion |
| Detailed linkage bench | `/linkage/` | Two-coordinate guide/drive kinematics, mass matrix, physical spring, MIT-style control, finite actuator response and local dynamics |
| Recorded remote playback | `/recorded/` | Captured Pymunk shapes, moving disturbance profile and force readouts in N/kgf; playback does not rerun the engine |
| Native live GUI | `Open Pymunk GUI.cmd` | Official Pygame debug renderer with run/pause/step/reset and body inspection |

## Setup and restart

Requires installed **Python 3.13** (verified), **Node.js 22.20.0** (verified) and npm. The Vite toolchain also supports its documented Node 20.19+/22.12+ range, but those alternatives were not tested here. From this folder:

```sh
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
npm ci
npm run build
```

On Windows, **Setup Pymunk.cmd** performs these steps. Then double-click **Start Pymunk Linkage.cmd** and wait for Ready. Open [Pymunk](http://127.0.0.1:4186/), [all studies](http://127.0.0.1:4186/animations/), [force calculator](http://127.0.0.1:4186/force-plots/) or [detailed linkage](http://127.0.0.1:4186/linkage/). The server runs independently of Codex. Close it with **Stop Pymunk Linkage.cmd**; after shutdown or reboot, double-click the start launcher again and use the same URLs. Startup does not reinstall dependencies. Errors remain readable and persistent logs stay in ignored `.preview/`. No login/boot automation is installed.

**Start Geometry Preview.cmd** preserves the older geometry URLs [force plots](http://127.0.0.1:4175/force-plots/) and [linkage](http://127.0.0.1:4175/linkage/). It uses a separate tracked port-4175 process; **Stop Geometry Preview.cmd** stops only that process. If another project owns either port, the launcher reports the conflict without killing it or choosing a new port. The original external prototypes can remain on disk, but only one matching service can own a given port.

The launchers resolve their own folder and use its `.venv`; no author-specific filesystem paths are needed. A missing generated gallery/linkage build requires `npm run build`. Generated pages/bundles, environments, logs and test captures are intentionally ignored; source, pinned dependencies and lockfile are retained.

## Model, decisions and continuation

Read [app instructions](AGENTS.md), [context](context/README.md), [model and coordinates](docs/model.md), [design](docs/design.md), [decisions](docs/decisions.md), [architecture](docs/architecture.md), [validation](docs/validation.md), [handoff](docs/handoff.md) and [glossary](GLOSSARY.md). The detailed bench retains its [full mechanics](docs/linkage-model.md). The [reference equation cross-check](docs/equation-cross-check.md) distinguishes belt forces from ideal constraint reactions.

Shared requirements remain in the [repository research record](../../../../database/md_research/requirement-parameter-research.md) and [project documentation](../../../../docs/README.md). Chat inputs and app defaults are experimental assumptions, not accepted team requirements.

## Checks and limitations

```sh
npm test
.venv/Scripts/python.exe -m unittest -v test_physics test_equation_checks
npm run test:browser
node scripts/verify_pymunk.cjs
node scripts/verify-force-plots.cjs
```

There are 24 detailed-model tests and 19 Pymunk/reference tests. Browser checks cover the seven offline studies, fixed-ratio geometry, force calculator, detailed bench, recorded preview and Pymunk controls/exports. The native renderer can be checked with `Open Pymunk GUI.cmd --headless-check`. See the validation record for results and remaining checks.

The seven animation fragments are retained as editable source under `animations/`. The old high-resolution GIFs, raw frame directories and full traces are not committed; interactive pages retain the motion content and can be rebuilt. The Pymunk bench uses prescribed loads and sensor geometry, with no automatically solved tire contact, soil, belt elasticity or structural stress. The fixed 4:1 approximation is not an exact straight full inversion. Missing belt radii/T₀ value, real actuator limits, spring characterization, collision clearance and hardware validation remain open.
