# Linkage simulator architecture

The detailed belt linkage is a third entry point, `/linkage/`, in the existing Capstone Vite application. `/` and `/workbench/` remain available. The installed Node.js runtime serves the saved production build on `127.0.0.1:4175`; numerical work runs in a browser worker and requires no second local service.

The interface uses the existing vanilla JavaScript/SVG approach, with editable engineering inputs, mechanism drawings and numerical plots. The visible calculation graph represents the actual model stages. It is documentation/navigation of these calculations, not a bdsim execution backend.

`ml-matrix` supplies browser-compatible matrix operations and eigenvalue decomposition for local pole analysis. An independent offline Python reference uses SymPy and SciPy to check selected mechanics and small-signal results. Python is not required to start or operate the application. This keeps the durable launcher independent of Python environments, simulator server processes and external accounts.

Heavy contact engines, Chrono, robotics middleware and reinforcement learning are future integration choices. The current deliverable is the constrained belt mechanism bench with hybrid spring/control analysis, rather than an installation of every tool mentioned in the source chats.

## Startup and build

From this app folder, double-click `Start Capstone.cmd`; it verifies atlas, workbench and linkage HTTP markers before opening them. The same launcher reuses a verified matching server. `Stop Capstone.cmd` checks the recorded process identity before stopping it. Logs remain in `.preview/`. No login or boot automation is configured.

For development, `npm run dev` serves port 5173. `npm run build` emits all three entry points. `npm test` runs the Node model tests. Production preview remains at [the linkage route](http://127.0.0.1:4175/linkage/).

## References

- [MIT manipulation control notes](https://manipulation.mit.edu/force.html): joint torque commands, stiffness and damping, gravity compensation.
- [SymPy Lagrange mechanics](https://docs.sympy.org/latest/explanation/modules/physics/mechanics/lagrange.html): independent energy-based mechanics checks.
- [SymPy mechanics linearization](https://docs.sympy.org/latest/modules/physics/mechanics/linearize.html): operating-point and small-perturbation conventions.
- [ml-matrix](https://github.com/mljs/matrix): numerical matrix and eigenvalue routines bundled with the application.
