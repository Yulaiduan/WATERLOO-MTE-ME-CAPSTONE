# Using the detailed linkage bench

Open [the linkage simulator](http://127.0.0.1:4175/linkage/). If the server is stopped, double-click `Start Capstone.cmd` in this app folder and wait for Ready. `Stop Capstone.cmd` shuts down the matching project server.

This deliverable targets desktop use. The desktop interface and three-route launcher lifecycle have been reviewed; mobile use is outside the requested scope.

Start with equal links, a grounded guide ratio of 2, zero guide phase and two 1:1 wheel-drive belt stages. Vary fold angle to inspect vertical wheel travel. Then change a stage ratio to see the wheel spin coupling created during folding. These are two independent coordinates: fold and wheel-drive input.

Enter measured masses, centre-of-mass locations and COM inertias before interpreting dynamic loads. Link inertias are editable physical inputs. Default values are estimates; they do not automatically change when lengths or masses are edited.

Review a torsion spring first, then choose a linear spring and its physical attachment geometry. Stiffness, free length and placement determine spring torque together. Software `Kp` and `Kd` act through a separate MIT-style actuator command. Keeping these physical and software contributions visible makes passive, ideal-control and finite-actuator runs comparable.

Inspect static demand before running a transient. Torque and torque–speed limits, actuator lag and slew can change the achieved motion. A prescribed-motion demand curve is an ideal load estimate; it is not an achieved trajectory.

Local poles describe the selected operating point and unsaturated branch. Read the force-balance residual and saturation status alongside them. Wheel-angle marginality can coexist with a stable fold mode; repeated zero poles can allow drift. “No growing modes” is not an automatic full-state stability claim. Fully decaying local modes still do not establish global stability or robustness to terrain impact.

Exports retain inputs, units and model assumptions so a run can be reproduced. The fixed-pivot bench and terrain workbench are separate models; moving-chassis contact is a future coupling task.

For offline verification with installed Python, NumPy, SymPy and SciPy, run `python scripts/validate_linkage_reference.py` from the project root. The script derives scalar kinetic and potential energies independently, compares their derivatives with the browser model via the installed Node.js executable, and saves compact cases in `tests/fixtures/linkage/sympy-reference.json`. Python is optional for app use.
