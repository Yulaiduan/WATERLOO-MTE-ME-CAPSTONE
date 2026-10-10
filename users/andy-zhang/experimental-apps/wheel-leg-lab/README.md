# Wheel Leg Lab

Owner: Andy Zhang. Updated: 2026-10-10. Status: experimental, combining **Create a rough animation** and **Optimize wheel-to-link ratio**. This member toolkit does not define or validate the team's canonical robot.

## Unified browser workspace

**Start Motion Lab.cmd** is the canonical launcher. Open http://127.0.0.1:4186/
for the shared main menu, dark-mode toggle and always-available Pymunk visual GUI.
Read the [workflow, data contracts and validation](docs/unified-motion-lab.md).

| Tool | Route | Content |
| --- | --- | --- |
| Main menu | `/` | Mathematical / physical / miscellaneous / profiles and data |
| Mathematical suspension | `/mathematical/` | Independent Python/SciPy ODE, load/motion/energy data and MATLAB companion |
| Pymunk physical bench | `/physics/` | Actual rigid-body engine, wheel-height input, floating chassis and solver loads |
| Detailed linkage | `/linkage/` | Two-coordinate guide/drive, physical spring, impedance and local dynamics |
| Miscellaneous studies | `/animations/`, `/force-plots/`, `/recorded/` | Motion studies and Plotly data charts |
| Native live debugger | `Open Native Pymunk Debugger.cmd` | Optional official Pygame debug renderer |

## Setup and restart

Requires installed Python 3.13 and Node.js 22.20.0 (verified) with npm.
Double-click **Setup Motion Lab.cmd** in a new checkout, then **Start Motion
Lab.cmd** and wait for Ready. It uses the app-local installed environment and
saved build; startup does not reinstall dependencies. Errors remain readable
in the window and ignored .preview logs.

After shutdown/reboot, double-click the same start launcher and reopen
http://127.0.0.1:4186/. **Stop Motion Lab.cmd** stops only the verified process
and archives its state. No login/boot automation is installed. The familiar
Pymunk/geometry/Capstone browser command names remain aliases to this menu.
The legacy standalone port-4175 service helpers/source are retained separately.

```sh
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
npm ci
npm run build
```

Profiles and generated runs are appended to browser IndexedDB. Save/download
JSON for portable backup; import JSON through Profiles & data. Plotly charts
support zoom, pan, reset and image export; full JSON/CSV retains recorded data.
The Mathematical tab also offers same-input SciPy/Pymunk comparison and the
[verified MATLAB model](math/README.md).

## Position input correction

The user clarified on 2026-10-10 that the disturbance is **position**, not force. Default: an illustrative 30 mm upward wheel-hub step, starting at 0.5 s with a 250 ms smooth C2 rise; these values are editable, not confirmed hardware inputs. The floating chassis has an 8 kg corner mass with pitch held and heave free. Its displacement, velocity and acceleration are outputs, alongside pin forces, spring/guide torques and the signed vertical reaction needed to impose the wheel motion. Fixed-hip wheel motion and fixed-wheel chassis motion are alternative fixture tests. Position square waves and finite bump pulses have independent rise/fall times. A zero-duration position jump is rejected; linear joins still give timestep-dependent acceleration/load peaks.

## Model, decisions and continuation

Read [app instructions](AGENTS.md), [context](context/README.md), [model and coordinates](docs/model.md), [design](docs/design.md), [decisions](docs/decisions.md), [architecture](docs/architecture.md), [validation](docs/validation.md), [handoff](docs/handoff.md) and [glossary](GLOSSARY.md). The detailed bench retains its [full mechanics](docs/linkage-model.md). The [reference equation cross-check](docs/equation-cross-check.md) distinguishes belt forces from ideal constraint reactions.

Shared requirements remain in the [repository research record](../../../../database/md_research/requirement-parameter-research.md) and [project documentation](../../../../docs/README.md). Chat inputs and app defaults are experimental assumptions, not accepted team requirements.

## Checks and limitations

```sh
npm test
.venv/Scripts/python.exe -m unittest -v test_physics test_equation_checks test_position_input test_math_model
npm run test:browser
node scripts/verify_pymunk.cjs
node scripts/verify-force-plots.cjs
```

There are 32 JavaScript tests and 37 Python mechanics/reference tests. Browser checks cover the unified UI/library, seven offline studies, fixed-ratio geometry, force calculator, detailed bench, recorded preview and Pymunk controls/exports. The native renderer can be checked with `Open Native Pymunk Debugger.cmd --headless-check`. See the validation record for results and remaining checks.

The seven animation fragments are retained as editable source under `animations/`. The old high-resolution GIFs, raw frame directories and full traces are not committed; interactive pages retain the motion content and can be rebuilt. The Pymunk bench defaults to a prescribed vertical wheel-height step and floating chassis, with force/torque modes retained as legacy diagnostics. It uses sensor geometry, with no automatically solved tire contact, soil, belt elasticity or structural stress. The fixed 4:1 approximation is not an exact straight full inversion. Missing belt radii/T₀ value, real actuator limits, spring characterization, collision clearance and hardware validation remain open.
