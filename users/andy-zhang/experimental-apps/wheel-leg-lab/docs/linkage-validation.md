# Detailed linkage validation

Author: Andy Zhang with Codex. Updated: 2026-10-09. Status: numerical prototype validation.

The imported standalone model passes 24 JavaScript tests covering guide/drive kinematics, virtual work, mass/inertia, gravity/spring energy derivatives, IK, equilibrium, passive behavior, MIT/finite dynamics, modes, solver refinement and retained SymPy/SciPy fixtures. The independent Python derivation checks three equal/unequal/linear-spring cases against the installed Node model. See the unified [validation record](validation.md) for commands and actual results. Earlier counts included unrelated atlas/workbench tests and are not attributed to this import.

These results validate the checked ideal equations and branches; they do not establish hardware calibration, global stability, rolling contact or a canonical robot.
