# Wheel Leg Lab

Owner: Andy Zhang. Updated: 2026-10-10. Status: experimental, combining **Create a rough animation** and **Optimize wheel-to-link ratio**. This member toolkit does not define or validate the team's canonical robot.

## Unified browser workspace

**Start Motion Lab.cmd** is the canonical launcher. Open http://127.0.0.1:4186/
for the shared main menu, dark-mode toggle and always-available Pymunk visual GUI.
Read the [workflow and data contracts](docs/unified-motion-lab.md),
[spring presets](docs/suspension-presets.md) and [current validation](docs/validation.md).

| Tool | Route | Content |
| --- | --- | --- |
| Main menu | `/` | Mathematical / physical / miscellaneous / profiles and data |
| Mathematical suspension | `/mathematical/` | Independent Python/SciPy ODE with nine spring presets; MATLAB companion supports the original captured/direct tip spring |
| Pymunk physical bench | `/physics/` | Actual rigid-body engine, nine editable spring presets, wheel-height input, floating chassis and solver loads |
| Constant-lift lever | `/counterbalance/`, Mathematical selector and Miscellaneous studies | Independent lever equations/free dynamics and actual Pymunk counterpart; variable tension, constant equivalent lift, JSON and native GUI |
| Detailed linkage | `/linkage/` | Two-coordinate guide/drive, physical spring, impedance and local dynamics |
| Miscellaneous studies | `/animations/`, `/force-plots/`, `/recorded/` | Motion studies and Plotly data charts |
| Native live debugger | Browser GUI button or `Open Native Pymunk Debugger.cmd` | Live `Space.step` simulation in the official Pygame debug renderer on the host desktop |

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
[MATLAB companion and its supported scope](math/README.md).

**Show Pymunk visual GUI** starts a live native Pygame simulation using the
current wheel-height or constant-lift lever profile. The window opens on the computer running this
server; a remote browser does not receive that desktop window. Captured engine
playback remains separately labeled in the browser. The SciPy and independent
wheel-drive models retain their own identities; launching the native viewer
runs the corresponding Pymunk model. The independent wheel-drive linkage uses
the wheel-height fixture because it has no two-axis native counterpart.

Nine [suspension presets](docs/suspension-presets.md) cover the original spring,
six sketch mechanisms, internal knee capture and constant-lift gravity balance.
Choose compression, extension or a bilateral captured coil, independently of
direct, rigid-pullrod or ideal-rope routing. Increasing pull-through input span
compresses the coil; the leg motion that produces that span change depends on
mounts and wrap direction. Rope is tension-only, zero-stretch and 100% efficient.
All new mechanism dimensions are editable demonstrations, not measured hardware.

The [constant-lift study](docs/constant-lift.md) implements both the exact
standalone lever from the reference sketch and its guided wheel-leg adaptation.
Zero **effective** free length gives tension proportional to span while the
physical coil free length stays positive through ideal routing/preload emulation.
The flat quantity is equivalent lift, not spring tension or torque. An ordinary
finite-effective-free-length coil leaves angle-dependent residual loads. Exact
gravity compensation is neutral and supplies no restoring ride height; it needs
separate suspension stiffness/control and damping.

## Position input correction

The user clarified on 2026-10-10 that the disturbance is **position**, not force. Default: an illustrative 30 mm upward wheel-hub step, starting at 0.5 s with a 250 ms smooth C2 rise; these values are editable, not confirmed hardware inputs. The floating chassis has an 8 kg corner mass with pitch held and heave free. Its displacement, velocity and acceleration are outputs, alongside pin forces, spring/guide torques and the signed vertical reaction needed to impose the wheel motion. Fixed-hip wheel motion and fixed-wheel chassis motion are alternative fixture tests. Position square waves and finite bump pulses have independent rise/fall times. A zero-duration position jump is rejected; linear joins still give timestep-dependent acceleration/load peaks.

## Model, decisions and continuation

Read [app instructions](AGENTS.md), [context](context/README.md), [model and coordinates](docs/model.md), [design](docs/design.md), [decisions](docs/decisions.md), [architecture](docs/architecture.md), [validation](docs/validation.md), [handoff](docs/handoff.md) and [glossary](GLOSSARY.md). The detailed bench retains its [full mechanics](docs/linkage-model.md). The [reference equation cross-check](docs/equation-cross-check.md) distinguishes belt forces from ideal constraint reactions.

Shared requirements remain in the [repository research record](../../../../database/md_research/requirement-parameter-research.md) and [project documentation](../../../../docs/README.md). Chat inputs and app defaults are experimental assumptions, not accepted team requirements.

## Checks and limitations

```sh
npm test
.venv/Scripts/python.exe -m unittest -v test_physics test_equation_checks test_position_input test_math_model test_spring_mechanisms test_suspension_physics test_gravity_balance test_counterbalance
npm run test:browser
node scripts/verify_pymunk.cjs
node scripts/verify-force-plots.cjs
node scripts/verify_suspension_ui.cjs
node scripts/verify_counterbalance_ui.cjs
node scripts/verify_motion_lab.cjs
.venv/Scripts/python.exe scripts/verify_native_gui.py
```

The preceding eight-preset release passed 64 Python and 32 JavaScript tests. Its preset/browser checks pass
both actual backends; native launch verification confirms a real desktop window,
advancing solver steps, looping and graceful close. Details and numerical
tolerances are in the [validation record](docs/validation.md). The native renderer can be checked with
`Open Native Pymunk Debugger.cmd --headless-check`. No canonical robot or hardware
validation is claimed.

The current constant-lift integration passes **82 Python tests** (71 wheel-leg
and 11 lever) and **33 JavaScript tests**. Real-backend browser checks pass all
nine presets, both lever APIs, JSON/library integration and the unified menus.
Actual native runs pass captured-knee, gravity-balance, prescribed-lever and
free-lever models, including solver stepping, owned-window restoration and
graceful close. The durable launcher passes fresh start/reuse/scoped-stop/restart
outside the app directory. See the validation record for full evidence and limits.

The seven animation fragments are retained as editable source under `animations/`. The old high-resolution GIFs, raw frame directories and full traces are not committed; interactive pages retain the motion content and can be rebuilt. The Pymunk bench defaults to a prescribed vertical wheel-height step and floating chassis, with force/torque modes retained as legacy diagnostics. It uses sensor geometry, with no automatically solved tire contact, soil, belt elasticity or structural stress. The fixed 4:1 approximation is not an exact straight full inversion. Missing belt radii/T₀ value, real actuator limits, spring characterization, collision clearance and hardware validation remain open.
