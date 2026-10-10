# Wheel Leg Lab context

Owner: Andy Zhang. Updated: 2026-10-10. Status: experimental, imported against repository base `0b55ff6`. Publication and current revision are discoverable with `git log` at repository root.

## Sources and scope

The user authorized content from both **Create a rough animation** and **Optimize wheel-to-link ratio**. This folder contains curated engineering findings and app source, not private transcripts, account exports or partner materials. The [handoff](../docs/handoff.md) records the full scope and current limitations.

The rough-animation chat progressed from a grounded equal-link 2:1 guide to an independent coaxial wheel drive, tilted and mirrored inversion, two-position reindexing, a fixed 4:1 working-stroke approximation, and a mathematical path family. The latest constraint **prohibits reindexing the hip pulley**. Therefore the reindexing demo is retained as a historical alternative, not the selected fixed-pulley proposal.

The ratio chat corrected tangential-force projection versus total vertical support, separated static torque from effective suspension stiffness/damping, built the spring/damper Pymunk bench and GUI, added pulse/step visualization and N/kgf readouts, and cross-checked the user's wheel-radius/belt equations. It confirms a 200 mm wheel radius for the fixture and a 50 mm lower-link extension; the broader radius study is 150–250 mm. Required travel equal to radius remains a sizing assumption.

## Latest correction: position input

On 2026-10-10 the user clarified that the excitation is a position step. Pymunk now defaults to prescribed wheel-hub height with a floating chassis (pitch fixed, heave free); spring-dependent chassis motion and driver reaction are outputs. The editable 30 mm / 250 ms smooth-rise values are illustrative. Recorded step/square previews have been regenerated; force/torque inputs remain explicitly labeled legacy diagnostics. This correction applies to the Pymunk bench, not the separate JavaScript control model.

## Coordinate boundary

Rough-path displays use positive y down and angles from downward vertical. Detailed mechanics use world y up with fold q from downward vertical. Pymunk uses world y up with θ from horizontal and knee opening 2θ. Screenshot y/z correspond to engine x/y; screenshot q is a moment sign, T₀ is belt tension and β is a belt-span angle. Use the [model](../docs/model.md) and [glossary](../GLOSSARY.md), not identical variable names, to map between these contexts.

## Actual verification and open work

The unified app uses app-local Python/Node dependencies and no machine-specific runtime paths. Current verification passes 90 Python tests (79 wheel-leg and 11 lever) and 33 JavaScript tests. Both backends, the complete two-stage suspension, nine-preset/lever browser checks, JSON/library integration, actual native launch/window restore and durable restart evidence are retained in [validation](../docs/validation.md). MATLAB comparisons apply to the original captured/direct tip spring, not the new presets, ride strut or lever. Canonical robot physics is not applicable to this member toolkit; the shared manifest remains unchanged.

Continue by confirming pulley radii and T₀ value/role, actuator hardware, spring preload/characterization, clearance through inversion and real wheel contact. Do not treat derived torque agreement or a collision-free drawing as hardware validation. The immutable assumptions and decisions are summarized in [decisions](../docs/decisions.md); accepted shared requirements remain in the existing repository records.

## Unified Motion Lab, 2026-10-10

The shared browser menu now separates independent mathematical simulation,
2D Pymunk physics and miscellaneous motion studies, with dark mode, Plotly
charts and a profile/data browser. Use Start Motion Lab.cmd at port 4186;
familiar browser launchers are aliases and the native debugger is preserved
separately. Full workflow, JSON contracts, MATLAB/SciPy agreement and current
verification are in the [unified workspace record](../docs/unified-motion-lab.md).

## Spring sketches and live GUI clarification, 2026-10-10

The current catalog retains the original spring and adds hip/knee pulley,
direct scissor, hip/knee bellcrank, direct-to-chassis and internal knee capture
mechanisms. Their [editable dimensions and laws](../docs/suspension-presets.md)
are experimental interpretations of the sketches. Compression, extension and
bilateral captured coil laws remain separate from direct/pullrod/ideal-rope
transmission. Pull-through input span growth compresses the coil; wrap or mount
direction determines the corresponding leg motion. Ideal rope has zero stretch,
100% efficiency and tension-only loading.

The browser GUI button now launches a live native Pygame/Pymunk window on the
simulation host desktop, stepping a newly built Space with the chosen profile.
Recorded browser engine playback remains explicitly separate and can be used
from a remote browser. Python/SciPy supports the spring catalog; MATLAB supports
only the original `legacy_tip` captured/direct combination. New Pymunk presets
apply actual point forces explicitly each timestep, while the original captured
tip spring keeps its native DampedSpring.

## Constant-lift lever and wheel adaptation, 2026-10-10

The user requested both the exact reference lever and a wheel-leg preset.
The standalone [constant-lift study](../docs/constant-lift.md) is available in
the Mathematical selector, Miscellaneous studies and `/counterbalance/`; it
has independent math/free dynamics, actual Pymunk angle/free runs, profile/run
JSON, data-library records and a model-specific live native GUI.

The ninth suspension preset, `gravity_balance`, attaches an upper-link point
to a downward vertical chassis mount. Zero-effective-span tension gives
constant generalized chassis support, with distributed link weight included.
Auto balance calibrates spring rate explicitly while retaining positive
physical coil free length. Ordinary Hooke preload remains a separate method.
Offset mounts or a finite effective free length break exact constant lift;
neutral gravity compensation alone provides no restoring ride-height stiffness.
The [retained reference sketch](../references/constant-lift-lever.png) and
derived equations describe an ideal study, not confirmed hardware packaging.
The combined 82 Python/33 JavaScript checks, real-backend browser workflows,
four live native model cases and durable launcher lifecycle pass. Complete
evidence and numerical limits are recorded in [validation](../docs/validation.md).

## Complete wheel suspension

The user chose the existing 2:1 folding leg with a restoring spring and damper.
The [architecture](../docs/suspension-architecture.md) uses a gravity stage plus
an independent hip-to-tip ride strut and a real chassis sensor polygon. The
lever's bridge and direct architecture URL load one configured physical run.
All 90 Python/33 JavaScript checks and five live native cases pass. Current
factory damping is an editable 500 N s/m; the knee controller is disabled.
