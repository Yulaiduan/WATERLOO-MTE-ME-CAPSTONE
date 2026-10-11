# Passive mechanism audit and curated demo defaults

Owner: Andy Zhang. Updated: 2026-10-10. Status: experimental mathematical and
rigid-body audit, not hardware acceptance or canonical robot validation.
Sources: [kernel](../spring_mechanisms.py), [runtime](../suspension_runtime.py),
[independent math](../math_model.py), [stability tests](../test_mechanism_stability.py)
and [replacement tests](../test_replacement_suspension.py).
Final evidence is centralized in [validation](validation.md); raw runs stay ignored.

## What earlier checks missed

Static preload and short smooth trajectories checked geometry/force closure,
not passive six-second response. Unsafe demo settings and numerical splitting
were corrected explicitly, without a holding motor or fabricated support curve.

| Before / finding | Correction or boundary |
| --- | --- |
| Old 40 mm hip drum, 8 kN/m: balanced at 45° but unstable, acceleration slope about +15.63 s⁻² | Current hip demo uses 80 mm leverage; preload and restoring stability are separate checks |
| Old hip-bellcrank demo was unstable; old legacy-tip and knee-bellcrank square cases fell toward travel limits | Curate each editable mechanism and test the complete finite envelope |
| Native DampedSpring/constraint splitting biased some ride responses | All current presets use real point forces; restricted native_legacy is a warned diagnostic |
| Knee crank 24 kN/m / 500 N s/m reached a Pymunk stop near 5.982625 s at .0625 ms, while SciPy remained bounded | Marginal configuration lacks converged six-second behavior; current demo damping is 1000 N s/m |
| Earlier factory added a second restoring path relative to the replacement intent | Current factory is one upper-r1/chassis unit, auxiliary off; earlier variant stays explicit |
| Guide torque alone cannot determine absolute belt spans/bearing forces | Unknown baseline shows difference only; viewer baseline stays outside solver loads and sheet T₀ |

## Current catalog settings

Rates are SI, editable demonstrations. Hooke auto preload solves free length at
the chosen pose; zero-effective gravity balance calibrates rate instead.
The API returns resolved settings and preserves explicit overrides.

| Preset | Rate N/m | Damping N s/m | Curated leverage / note |
| --- | ---: | ---: | --- |
| legacy_tip | 20000 | 500 | Original hip-to-tip geometry; point-force default |
| hip_pulley | 8000 | 500 | 80 mm suspension drum |
| knee_pulley | 8000 | 500 | 40 mm suspension drum |
| direct_scissor | 8000 | 100 | Midpoint link attachments |
| hip_bellcrank | 8000 | 500 | 80 mm crank |
| knee_bellcrank | 24000 | 1000 | 50 mm crank |
| chassis_direct | 8000 | 100 | Explicit editable chassis/lower mount |
| knee_capture | 8000 | 500 | 40 mm internal drum; compression pull-through |
| gravity_balance | about 2260.04367, auto-resolved | 100 | H=150 mm, R=136.5 mm; neutral elastic support |

The 28/14 mm guide drums are separate from suspension payout drums. Sensor /
viewer geometry adds no inertia, contact or applied guide belt-bearing forces.

## Audit results and finite scope

A separate kernel audit sampled 1404 valid topology/routing/law/angle/speed
combinations, with no negative damping dissipation or compressive rope force.
Maximum force-site power error was 6.9e-13 W and energy-gradient error
1.64e-7 N m. Fifty-four impossible coil lengths were explicitly rejected.
These check signs, passivity and virtual work, not hardware capture or packaging.

The full 114-test Python suite passes, including the finite envelope:
nine catalog presets, initial 30/45/60°, 30 mm / 250 ms smooth quintic step and
square wave, six seconds, SciPy and Pymunk (108 backend cases). All complete with
finite state, no stop/slack/actuator torque, positive prescribed support and
force/moment closure below 1e-7. Focused timestep refinement approaches SciPy.
Numerical tolerances, measured minima and final browser/native/MATLAB checks
belong to [validation](validation.md).

Passive stability excludes active controller gains: restoring, neutral, unstable
or not applicable to the chosen fixture. Exact gravity balance remains neutral
with damping; damping cannot establish a unique static ride height. Arbitrary
edits can invalidate the tested envelope or create slack/dead centres.

## Interpretation limits

Physical point forces are explicit finite-step updates: refine dt for stiffness.
SciPy output spacing is not its adaptive internal step. The native_legacy
diagnostic accepts only legacy_tip/captured/direct/hooke, warns about splitting
and requires refinement/comparison with point-force and independent SciPy.

Rigid-stop and abrupt velocity-join peaks depend on timestep. Smooth agreement
does not certify impact peaks. The wheel-height driver is bilateral, not solved
tire/terrain contact. Positive tested support does not establish rolling,
obstacle climbing, friction or whole-vehicle motion. Coil bind, real belt
elasticity, structural stress, component limits and hardware remain unverified.

MATLAB is the original captured/direct Hooke companion and rejects zero-effective
law and other mechanisms. Preserve older evidence as historical rather than
assigning it to current defaults.
