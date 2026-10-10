# Design decisions and superseded alternatives

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
| Use real DampedSpring geometry and separate knee impedance | Physical attachment leverage/preload and virtual gains are different quantities | Implemented |
| Prescribe wheel height rather than applied disturbance force | User corrected the input quantity on 2026-10-10; measure support reaction and suspension response instead | User correction, implemented |
| Default to floating chassis with fixed pitch | Allows spring-dependent chassis heave; fixed hip remains a constrained joint-load test and fixed wheel permits chassis-height input | Prototype fixture choice, not confirmed hardware boundary |
| Use finite smooth C2 position ramps | An instantaneous height jump gives unbounded ideal velocity/acceleration; linear joins remain timestep dependent | Implemented |
| Keep prescribed bilateral fixture separate from terrain/contact simulation | Negative reaction flags that real ground may detach; does not establish obstacle climbing or tire behavior | Implemented scope |
| Expose bottom loading and relative wheel-drive lock separately | The reference Fy r_w torque spins a free wheel or loads the leg through a constrained drive; reflected wheel inertia matters | Implemented selectable assumption |
| Preserve T₀ separately, with N/kgf conversion | User confirms belt tension but its value/span interpretation is unresolved; do not replace it with spring force or guessed zero | Confirmed term, unresolved magnitude |
| Publish portable source and rebuild generated pages | Source stays under Andy's member folder; no environments, raw runs or author-specific runtime paths enter Git | Publication decision |

These are reversible experimental choices unless promoted through the repository's shared-engineering workflow. The [model](model.md) records the mathematical derivations and the [handoff](handoff.md) records unresolved physical inputs.
