# Kinefold

Owner: Andy Zhang. Created 2026-10-22. Experimental mechanism design and solver workspace;
no canonical robot or hardware acceptance is implied.

Double-click **[Start Kinefold.cmd](Start%20Kinefold.cmd)** and wait for Ready,
then open <http://127.0.0.1:4191/>. The builder/static server requires installed
Python 3.10+; there is no npm install or build. Run **[Setup Kinefold.cmd](Setup%20Kinefold.cmd)** once (Python 3.12+)
to install this app's isolated SciPy/Pymunk environment for dynamic runs.
The detached server survives Codex closing.
After a reboot or shutdown, use the same launcher and URL. Repeated startup
reuses this app; an occupied port fails visibly. **[Stop Kinefold.cmd](Stop%20Kinefold.cmd)**
stops only this app. Failures are readable in the launcher and `.preview/server.log`.
No login/boot automation is installed. Node.js is needed only for developer checks.

## Workspace

- **00 Designs:** named saved mechanisms and shared run profiles, a working
  draft, explicit example templates and portable project JSON. Storage
  is local to this browser/origin; export backups for another PC or browser.
- **Mechanism builder:** Geometry, Suspension, Loadings & preloads at left;
  live side/isometric mechanism preview at right, with layers, dimension labels,
  full-range travel path, pose scrub and prescribed kinematic playback. Mechanism,
  Full travel and Spring detail framing, zoom and drag-to-pan support inspection.
  Parameter shortcuts and ? buttons open the appropriate variable definition.
- **Conventions & variables:** independently expandable illustrated frame,
  topology, right-hand-rule signs, spring/loading laws, dynamics assumptions and a searchable
  dictionary. Search is available at the top; section shortcuts open the selected
  reference, including a geometrically scaled baseline topology illustration.
  The front-left frame is +x forward, +y left, +z up; positive +y rotation is
  counterclockwise in the left-side x–z view (+x left, +z up, +y toward you).
- **Export design** / **Import** retain the complete mechanism, view and shared
  solver settings in a versioned `kinefold/project-v2` document. Legacy
  `kinefold/mechanism-v1` files migrate explicitly. Invalid imports leave the
  current design unchanged. Browser storage is not shared between users or ports.

The visual shell follows Motion Lab's app-owned sage/cream tabbed interface.
This is a separate app: it neither changes nor imports the Motion Lab UI/runtime.
The three carrier belts, finite-idler tangency and V4 baseline come from
[Jon's VSL v4](../../../jonathan-xie/experimental-apps/vsl-solver/v4/README.md).
[reference.json](reference.json) records the source revision/hash;
`reference-v4.js` retains unchanged analytical blocks, with an app-owned frame adapter.

The preview grid is calibrated in world millimetres; its displayed cell size
updates with zoom, with major lines every five cells. Index axes and rim marks
follow all six pulleys and the wheel. Belt material dots follow the exact open
belt loops, accounting for the moving carrier; their larger reference dot is
not a tooth or a manufacturing feature. The baseline has K=0, so the wheel
index stays level as the leg folds. Side view preserves plane lengths uniformly;
the isometric view is an orthographic projection. No wheel width is invented.

V4 uses a **linear coil with approximately constant support**, not constant cable
tension. Both that reference and an **ideal constant cable-force** option are
explicitly available in the builder. The separate static tab now shows signed
torque sweeps, belt tensions and equilibrium residuals from these same inputs. Wheel loads are prescribed; gravity acts on the individual masses.
The default 8.75 kg is a single-leg supported mass, not a whole-vehicle mass.
Remote spring housing is schematic. Cable stretch, friction, strength, contact,
manufacturing and 3D packaging remain unresolved. Travel is sampled at 181 poses.

## Developer checks

From this directory: `node verify.cjs` checks source parity, geometry, world
forces/moments, finite-pulley energy derivatives, both spring laws and JSON state.
`node verify-drawing.cjs` independently checks all index radii/orthogonality and
finite-difference belt material velocities on both wraps of every pulley stage.
Run `python preview.py start --no-browser` for HTTP readiness without opening a
browser. See [context](context/README.md) for actual verification and handoff.

## Coupled solver workspaces — 2026-10-22

Tab3 **Static solver** uses the retained Jon VSLv4 equations directly with the
current builder design. It evaluates the current pose and181 working-range
samples; the reported sampled peak is not a global bound. Hip torque signs
remain positive about+y, counterclockwise in the x-left/z-up side view.

Tab4 **Dynamic · analytical** integrates reduced equations with SciPy DOP853.
Tab5 **Dynamic · 2D Pymunk** integrates constrained planar rigid bodies.
Both consume the exact builder parameters and one shared saved run profile;
they have no embedded reference bench or sibling service dependency.

Both carry a persistent **¼ MODEL · SINGLE LEG** badge. The fixture fixes hip A,
locks θ₄ and integrates θ₂ through the same belt-coupled geometry and finite-idler
spring route. It applies the builder's gravity and prescribed wheel load, then
stops at a working-range limit. This is a fixed-hip mechanism test, not a floating
corner suspension, terrain contact, tire model or full vehicle simulation.
The supported mass is already per leg and is never divided by four again.

Moving masses and inertias must be explicit. m₁ stays at fixed A, contributes to
weight-reference loading and adds no moving inertia. Uniform rods/discs and the
reflected hip rotor inertia are labelled assumptions; custom centre-of-mass
inertias are editable. The original static baseline's zero moving masses are
never silently replaced. Choose the labelled dynamics example in00 Designs or
enter your own moving masses. Holding-torque and zero-torque buttons change the
shared profile only by explicit action.

Each run captures the project snapshot and model revision. Editing physical
inputs or loading a profile marks prior results stale; late results for another
revision are discarded. Real returned θ₂ samples drive the x-left/z-up preview,
including the grid, carrier belts and wheel/pulley indices. Angle, angular rate,
torque, energy and tension plots preserve their own units. JSON export includes
the full project snapshot, run settings, warnings, diagnostics and output;
CSV exports the sampled data. Results do not certify hardware or canonical physics.

Same-origin POST `/api/dynamics` accepts `{engine,params,runConfig}` and invokes
`dynamics.py --request-stdin` using this app's `.venv` Python. The standard-library
preview starts without physics packages, rejects malformed/nonfinite/oversized
requests, allows one run at a time and stops a worker exceeding90 seconds.
Missing dependencies give an actionable setup error. The original4191 launcher,
authenticated stop and restart behavior remain unchanged; no boot/login automation.
