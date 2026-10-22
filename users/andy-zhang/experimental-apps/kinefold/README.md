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
  solver settings in a versioned `kinefold/project-v3` document. Legacy
  `kinefold/mechanism-v1` and fixed-hip `project-v2` files migrate explicitly, preserving geometry and an archived prior profile. Invalid imports leave the
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
`node verify-projects.cjs` checks migration/persistence safety; after Setup, run
`.venv/Scripts/python.exe verify_dynamics.py` for exact square, independent heave,
source parity, event continuity and cross-engine refinement checks.
Run `python preview.py start --no-browser` for HTTP readiness without opening a
browser. See [context](context/README.md) for actual verification and handoff.

## Native equilibrium and vertical-chassis workspaces — 2026-10-22

All tabs use Kinefold's own interface. The retained finite-idler equations are
reference evidence, attributed above; no source app or copied tab is embedded.
Equilibrium evaluates the current builder and181 samples of its working range.
The sampled peak is not a certified global maximum.

Both dynamic engines use one saved mechanism and profile. The chassis mass m1
moves vertically with fixed horizontal position and pitch, while wheel height
is prescribed. No guide rods are drawn. Analytical dynamics use reduced equations;
Pymunk integrates a real vertically constrained chassis body, with the ideal
transmission and moving-body inertia condensed into its force law. It is not
an all-body rigid linkage, tire/collision or whole-vehicle simulation.

V4 baseline /150mm square keeps m1=8.75kg, all other masses zero and adds no
rotor inertia or damping. Its input is150mm high,150mm wide with150mm gaps,
default speed100mm/s and initial delay0.5s. Run duration6.5s covers two cycles.
Zero transition distance applies exact square events: chassis height and velocity
remain continuous while the ideal massless linkage can change pose instantly.
Do not interpret edge angular rates as finite peak jump speed. Positive moving
inertia or damping requires a declared finite transition distance; quintic ramps
lie inside the nominal plateau. Requested and applied traces are both retained.

The world-frame preview uses one fixed camera over the full trajectory, a moving
chassis mass marker and prescribed wheel-height platen. It preserves +x left,
+z up and +y toward the viewer. It does not render guide rods or pretend the base
input is rolling collision terrain. Plots show requested/applied input, chassis
and wheel height, chassis speed, hip angle, spring tension and wheel-input
reaction. Reactions supply support dynamically; weight reference is not applied
again as an extra gravity-sized force. Nonweight builder loads remain additional.

Projects use kinefold/project-v3, including all geometry, view and input/run
settings. Version2 fixed-hip projects retain exact geometry and an archived
legacySolverConfig; their original browser keys remain untouched. Migration
notices identify the change in boundary conditions. Legacy positive-mass designs
receive a declared10mm finite transition with no mass substitution. Export
project JSON for portable backups; this browser's library is not cloud storage.

Each run captures the full project/profile and preserves rows, world frames,
exact jump events and diagnostics. Result labels identify the captured design;
geometry/profile edits mark old results stale. JSON run export contains the
snapshot and engine output; CSV contains rows. No hardware validation is implied.

Same-origin POST /api/dynamics accepts engine/params/runConfig and invokes
dynamics.py --request-stdin using this app's isolated .venv. Run
[Setup Kinefold.cmd](Setup%20Kinefold.cmd) once with Python3.12+ for pinned
SciPy/Pymunk. Builder/equilibrium preview needs standard-library Python3.10+.
The existing Start/Stop launchers preserve4191 and support readable errors and
restart without Codex. No boot/login automation is installed.
