# Design decisions and superseded alternatives

On 2026-10-10 the user clarified that the constant-lift unit **replaces** the
original spring: one upper-r1/chassis-massblock spring/damper, auxiliary off and
primary damping 100 N s/m. The earlier two-stage factory is superseded. Exact
elastic compensation remains neutral; no hidden spring or controller supplies
restoring stiffness. The [architecture](suspension-architecture.md) records this
experimental choice and its limits.

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
| Use point-force spring integration for all nine current presets | Real attachment forces/moments must agree with independent geometry; native constraint/spring splitting biased older responses | Current; native DampedSpring retained only as explicit `native_legacy` diagnostic |
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
| Retain nine editable spring presets | Preserve the original tip spring, six sketch concepts, internal knee capture and gravity compensation without selecting hardware | Implemented experimental interpretations |
| Separate coil mode from topology and transmission | Compression, extension and captured describe the coil law; a pull-through mechanism can load the external linkage in tension while compressing its coil | User clarification captured in [preset equations](suspension-presets.md) |
| Define pull-through by input-span growth, not vague leg extension | `dc/dell=-1`; which leg motion compresses the coil depends on geometry or wrap direction | Explicit coordinate convention |
| Treat ideal rope as tension-only, zero-stretch and 100% efficient | Rope cannot push; slack removes elastic and damper input load, while coil damping remains dissipative | Requested ideal assumption |
| Apply real spring anchor/tangent forces for every current preset | Pin forces must follow the spring load path; torque alone would omit them. Explicit force integration requires timestep refinement | Implemented; evidence in mechanism audit and validation |
| Keep SciPy independent and label MATLAB's narrower scope | SciPy supports every catalog mechanism; MATLAB supports only the original captured/direct tip configuration and rejects unsupported combinations | Implemented model boundary |
| Launch a live desktop Pymunk GUI from the browser button | Actual Pygame rendering and Space.step run on the simulation host; recorded browser playback remains distinct and available remotely | User GUI clarification, implemented; see validation |
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

## Replacement and passive audit decisions, 2026-10-10

| Decision | Consequence | Status |
| --- | --- | --- |
| Replace lower-tip strut with one upper-link/chassis unit | Auxiliary is off; damping belongs to that same unit. No automatic second restoring spring | Latest user correction |
| Keep exact gravity balance neutral | Damping dissipates motion but does not select a static ride height | Derived identity |
| Draw guide drums as sensors and exact belt material motion | 28/14 mm demo radii enforce physical 2:1 visualization without mass/contact changes | Implemented ideal guide |
| Separate guide tension difference from optional absolute baseline | Unknown baseline does not determine absolute spans or bearing load. Viewer N/kgf remains independent of sheet T₀ and solver config | Implemented reference boundary |
| Audit full passive demo horizon, not only preload and short trajectories | Curated rates/geometry are tested at 30/45/60° under six-second smooth step/square; edited settings can still be unstable | Bounded experimental scope; see [audit](mechanism-audit.md) |
| Retain native spring splitting only as a diagnostic | Explicit `native_legacy` applies only to original captured/direct Hooke spring; warnings require refinement and independent comparison | Supersedes earlier default implementation |

Earlier two-stage restoring-strut evidence remains in [validation](validation.md)
and the optional-variant section of the architecture; it is not the current
factory. The independent two-stage coaxial wheel-drive concept is unchanged.
