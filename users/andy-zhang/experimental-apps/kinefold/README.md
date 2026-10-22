# Kinefold

Owner: Andy Zhang. Created 2026-10-22. Experimental mechanism design and solver workspace;
no canonical robot or hardware acceptance is implied.

Double-click **[Start Kinefold.cmd](Start%20Kinefold.cmd)** and wait for Ready,
then open <http://127.0.0.1:4191/>. It requires installed Python 3.10+ only;
there is no npm install or build. The detached server survives Codex closing.
After a reboot or shutdown, use the same launcher and URL. Repeated startup
reuses this app; an occupied port fails visibly. **[Stop Kinefold.cmd](Stop%20Kinefold.cmd)**
stops only this app. Failures are readable in the launcher and `.preview/server.log`.
No login/boot automation is installed. Node.js is needed only for developer checks.

## Workspace

- **Mechanism builder:** Geometry, Suspension, Loadings & preloads at left;
  live side/isometric mechanism preview at right, with layers, dimension labels,
  full-range travel path, pose scrub and prescribed kinematic playback. Mechanism,
  Full travel and Spring detail framing, zoom and drag-to-pan support inspection.
  Parameter shortcuts and ? buttons open the appropriate variable definition.
- **Conventions & variables:** independently expandable illustrated frame,
  topology, right-hand-rule signs, spring/loading laws and an 81-entry searchable
  dictionary. Search is available at the top; section shortcuts open the selected
  reference, including a geometrically scaled baseline topology illustration.
  The front-left frame is +x forward, +y left, +z up; positive +y rotation is
  counterclockwise in the left-side x–z view (+x left, +z up, +y toward you).
- Browser-local autosave; **Export design** / **Import** retain every input and
  view setting in `kinefold/mechanism-v1` JSON. Invalid imports leave the design
  unchanged. Browser storage is not shared between users or ports.

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

## Solver workspaces — 2026-10-22

Tab3 **Static solver** uses the retained Jon VSLv4 equations directly with the
current builder design. It evaluates the current pose and181 working-range
samples; the reported sampled peak is not a global bound. Hip torque signs
remain positive about+y, counterclockwise in the x-left/z-up side view.

Tab4 **Dynamic · analytical** connects the existing Motion Lab SciPy DOP853
bench. Tab5 **Dynamic · 2D Pymunk** connects its actual rigid-body engine.
Both carry a persistent **¼ MODEL · SINGLE LEG** badge and scope block.
These are independently configured reference benches, not automatic dynamic
versions of the builder's V4 cable route. Their engine x/y correspond to
Kinefold -x/z. The supported corner mass is entered in each bench; the app
neither assumes equal vehicle load sharing nor divides it by four again.

Opening a dynamic tab starts/reuses the sibling Motion Lab service at4186
through its verified durable launcher. A new checkout needs that app's
[documented setup](../wheel-leg-lab/README.md) once. Missing prerequisites appear
as a readable retry message. The Kinefold launcher remains the entry at4191.
Motion Lab is shared with its own app and stays running when Kinefold stops;
use its [Stop Motion Lab.cmd](../wheel-leg-lab/Stop%20Motion%20Lab.cmd) to stop
that service when it is no longer needed. No boot/login automation is added.
