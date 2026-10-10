# Linkage validation

Model checks distinguish constrained geometry, virtual work, energy consistency, local analysis, numerical integration and application startup. A passing calculation check establishes the tested ideal equations; physical calibration remains outstanding.

## Independent reference derivation

`python scripts/validate_linkage_reference.py` passes three independently derived SymPy cases: equal-link reference geometry, unequal links with nonunit drive carriers, and a linear spring on the lower link. It forms scalar kinetic energy and checks its velocity Hessian against the JavaScript mass matrix; it also checks wheel coordinates, full Jacobian, absolute wheel rotation, gravity potential and two derivatives, spring potential/torque/tangent stiffness, static fold torque, and generalized-versus-Cartesian power. Comparisons use relative tolerance `2e-10` and absolute tolerance `2e-11`.

The script also independently forms ideal-controller and six-state finite-lag matrices and computes their poles with SciPy. Both matrices and all matched poles agree with the JavaScript local-analysis results in all three cases at relative/absolute tolerance `2e-7`. Independent complex SciPy solves also agree with the displayed fold, vertical and wheel frequency responses at 0.05 Hz, approximately 3.162 Hz, and 200 Hz for both modes. For the finite-lag comparison, actuator torque limits are raised to `1e6 N m` solely in the verification call to ensure an unsaturated equilibrium; this isolates the local lag equations rather than asserting a hardware torque capability. Saved reference configurations and expected values are in `tests/fixtures/linkage/sympy-reference.json`.

Installed offline reference versions: Python 3.13, NumPy 2.4.2, SciPy 1.17.1, SymPy 1.14.0. The app itself requires Node.js and browser JavaScript, not Python.

Dependency audit after adding `ml-matrix` reports zero vulnerabilities.

## Integrated numerical checks

The completed combined test suite passes **49 tests**: 24 detailed-linkage checks and the original 25 atlas/workbench checks. Linkage tests cover carrier-aware geometry, virtual work, mass/energy consistency, passive and hybrid equilibria, spring curvature, analytical ideal and lagged-controller modes, nonlinear simulation/refinement, actuator limits, stopping at working bounds, exports and invalid inputs.

The final `npm run build` succeeds and emits all three entry points and the linkage numerical worker. The final dependency audit reports **zero vulnerabilities**. Independent Python reference checks pass against this same integrated model.

## Interpreting modal results

The UI distinguishes fully decaying modes, no growing modes, and growing modes. A zero or otherwise nondecaying pole is not automatically a statement of full-state stability. An uncontrolled wheel angle may be a neutral coordinate, while an undamped free rotor can have a repeated zero pole with drift. The interface therefore reports these modal conditions without treating a nonpositive real part alone as proof of stability. An unsaturated force-balanced operating point is required before interpreting local results as equilibrium analysis.

## Desktop application review

The user selected **desktop-only** scope. Desktop browser review passes; mobile behavior is not a target of this deliverable and was not reviewed.

- Changing the upper link to 200 mm gives axle `x = 11.29 mm` and `y = -313.63 mm` at the reviewed pose, showing the lateral travel created by unequal links.
- A 30 rpm drive input gives 30 rpm wheel rotation relative to the chassis. The recorded wheel speed relative to the lower link is 33.88 rpm while folding; these distinct reference frames are shown explicitly.
- A five-second sinusoidal scenario completes in all three modes without errors. MIT position/velocity references, proportional and derivative contributions, holding feedforward and delivered torque are visible and consistent with the run.
- The reviewed finite local model has a force-balance residual of approximately `6.66e-16 N m` and a reported natural frequency of `6.2793 Hz`.
- For the unequal-link passive case, selecting the computed equilibrium `q = 0.69232778827 rad` gives residual approximately `1.78e-15 N m` and valid equilibrium analysis.
- Numeric editing followed by a single click on a different tab works. The blur redraw fix preserves the intended next action.
- The production build includes the final wheel-angle guide-phase correction.

Desktop screenshot: [reviewed linkage interface](../../evidence/linkage-ui/desktop.jpg).

## Restart lifecycle review

The actual project-local `Start Capstone.cmd` was run from `C:\Windows`. Start, verified reuse, process-scoped stop and restart all pass. Atlas `/`, workbench `/workbench/` and linkage `/linkage/` return HTTP 200 on the preserved `127.0.0.1:4175` server. The installed Node.js runtime serves the saved production build independently of the Codex terminal; `.preview/` retains startup logs. No boot or login automation was added.
