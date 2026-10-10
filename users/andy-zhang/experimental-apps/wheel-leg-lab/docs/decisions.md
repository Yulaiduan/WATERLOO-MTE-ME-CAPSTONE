# Design decisions and superseded alternatives

On 2026-10-10 the user selected the existing 2:1 folding leg with a restoring
spring and damper for constant-lift suspension. Weight compensation and ride
restoration are separate passive paths; no hidden controller supplies restoring
force. The [architecture](suspension-architecture.md) records demo dimensions,
rates and validation.

Author: Andy Zhang with Codex. Updated: 2026-10-10. Status: prototype decisions and user constraints; no team hardware selection.

| Decision | Reason and consequence | Status |
| --- | --- | --- |
| Grounded 2:1 guide for the equal-link reference | Gives exact straight wheel-centre motion and one leg-shape coordinate; do not use an absolute Pymunk ratio 2 | Prototype reference |
| Separate coaxial wheel-drive coordinate | Wheel motion is independent of folding in the ideal two-stage 1:1 case; report chassis- and link-relative spin distinctly | Requested in rough-animation chat |
| Retain all tilt/inversion studies, label their constraints | A single fixed timing gives one straight tilted line, not two same-side branches | Verified ideal geometry |
| Do not reindex the guide in the latest fixed-pulley study | Later user constraint supersedes the earlier two-position indexing proposal; that demo is historical | User constraint |
| Explore unequal links and 4:1 as a short-stroke approximation | Approximately 42.35 mm working stroke / 0.768 mm ray error trades global straightness for working-region fit and large inversion travel | Exploratory candidate, not selected hardware |
| Optimize travel, stiffness/damping and motor constraints together | Average static force alone rewards near-singular leverage and cannot select a useful suspension | Derived model boundary |
| Radius 200 mm and lower-link extension 50 mm in the Pymunk fixture | These are explicit user inputs; larger 150–250 mm radius sweep remains a separate study | User prototype inputs |
| Preserve the original native DampedSpring and separate knee impedance | Physical attachment leverage/preload and virtual gains are different quantities; the original captured/direct tip combination keeps its solver implementation | Implemented |
| Prescribe wheel height rather than applied disturbance force | User corrected the input quantity on 2026-10-10; measure support reaction and suspension response instead | User correction, implemented |
| Default to floating chassis with fixed pitch | User selected floating chassis with prescribed wheel height; fixed hip remains a joint-load test and fixed wheel permits chassis-height input | User fixture choice; hardware boundary remains unresolved |
| Use finite smooth C2 position ramps | An instantaneous height jump gives unbounded ideal velocity/acceleration; linear joins remain timestep dependent | Implemented |
| Keep prescribed bilateral fixture separate from terrain/contact simulation | Negative reaction flags that real ground may detach; does not establish obstacle climbing or tire behavior | Implemented scope |
| Expose bottom loading and relative wheel-drive lock separately | The reference Fy r_w torque spins a free wheel or loads the leg through a constrained drive; reflected wheel inertia matters | Implemented selectable assumption |
| Preserve T₀ separately, with N/kgf conversion | User confirms belt tension but its value/span interpretation is unresolved; do not replace it with spring force or guessed zero | Confirmed term, unresolved magnitude |
| Publish portable source and rebuild generated pages | Source stays under Andy's member folder; no environments, raw runs or author-specific runtime paths enter Git | Publication decision |

These are reversible experimental choices unless promoted through the repository's shared-engineering workflow. The [model](model.md) records the mathematical derivations and the [handoff](handoff.md) records unresolved physical inputs.

## Unified Motion Lab, 2026-10-10

The shared browser menu now separates independent mathematical simulation,
2D Pymunk physics and miscellaneous motion studies, with dark mode, Plotly
charts and a profile/data browser. Use Start Motion Lab.cmd at port 4186;
familiar browser launchers are aliases and the native debugger is preserved
separately. Full workflow, JSON contracts, MATLAB/SciPy agreement and current
verification are in the [unified workspace record](unified-motion-lab.md).

## Suspension sketches and native viewer, 2026-10-10

| Decision | Reason and consequence | Status |
| --- | --- | --- |
| Retain the original eight editable spring presets | Preserve the original tip spring, six sketch concepts and internal knee capture without selecting hardware | Implemented experimental interpretations |
| Separate coil mode from topology and transmission | Compression, extension and captured describe the coil law; a pull-through mechanism can load the external linkage in tension while compressing its coil | User clarification captured in [preset equations](suspension-presets.md) |
| Define pull-through by input-span growth, not vague leg extension | `dc/dell=-1`; which leg motion compresses the coil depends on geometry or wrap direction | Explicit coordinate convention |
| Treat ideal rope as tension-only, zero-stretch and 100% efficient | Rope cannot push; slack removes elastic and damper input load, while coil damping remains dissipative | Requested ideal assumption |
| Apply real anchor/tangent forces for new physical presets | Bearing/pin forces must follow the spring load path; torque alone would omit them. Explicit force integration requires timestep refinement | Implemented; expanded validation pending |
| Keep SciPy independent and label MATLAB's narrower scope | SciPy supports every catalog mechanism; MATLAB supports only the original captured/direct tip configuration and rejects unsupported combinations | Implemented model boundary |
| Launch a live desktop Pymunk GUI from the browser button | Actual Pygame rendering and Space.step run on the simulation host; recorded browser playback remains distinct and available remotely | User GUI clarification, implemented; integration validation pending |
| Keep sketch dimensions editable and illustrative | Drum/crank/mount sizes lack measured hardware input; reject invalid spans/preloads rather than silently substituting values | Experimental assumptions |

The ideal mechanisms omit crank/drum inertia, transmission friction, rope
elasticity, coil solid height/bind and attachment contacts. None of these
choices promotes the member toolkit to a canonical robot or confirms a spring
package. See [validation](validation.md) for the final integration result.

## Constant-lift lever and wheel preset, 2026-10-10

| Decision | Reason and consequence | Status |
| --- | --- | --- |
| Implement both exact standalone lever and guided wheel-leg adaptation | User requested both; standalone lever profiles/backends remain distinct, while `gravity_balance` becomes the ninth wheel preset | Implemented experimental models |
| Name the flat quantity equivalent lift | `T=k*d` varies with span and its moment varies with cos θ; leverage yields constant `kHR/L` for the lever and `kHR/(2L)` for the wheel leg | Derived ideal identity |
| Separate effective input length from physical coil free length | Positive-free-length coil plus declared ideal routing/preload emulates the zero-effective law; an ordinary finite-effective-length coil retains residual variation | Explicit model assumption |
| Calibrate zero-effective spring rate and report it | Rate follows distributed gravitational demand; preserve physical free length and keep ordinary Hooke free-length preload behavior distinct | Implemented portable metadata |
| Treat exact gravity compensation as neutral, not a complete suspension | Balanced gravity has no ride-height restoring stiffness; damping/control/travel reserve require separate design | Derived scope limit |
| Drive physical lever angle through an actual speed motor | Avoid teleporting the body; tracking lag and applied-force loads require timestep refinement | Implemented Pymunk counterpart |
| Keep lever JSON/native launches model-specific | `counterbalance_math`/`counterbalance_pymunk` records and explicit native envelope prevent interpreting lever angles as wheel-height input | Implemented interface boundary |

The [constant-lift record](constant-lift.md) retains the reference sketch,
equations, demo parameters and validation scope. Finite effective free length
or offset mounts do not inherit exact constant lift from the default geometry.
This study does not accept a manufactured spring, prove routing/package clearance
or validate a canonical robot.
