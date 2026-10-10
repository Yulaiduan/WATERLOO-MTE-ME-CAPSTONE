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

The unified app rebuilds and runs with app-local Python/Node dependencies and no machine-specific runtime paths. Its 32 JavaScript and 37 Python tests pass. The independent MATLAB companion also agrees with SciPy in verified batch cases. App-local browser and launcher results are recorded in [validation](../docs/validation.md); canonical robot physics is not applicable to this member toolkit. The shared manifest remains empty and unchanged.

Continue by confirming pulley radii and T₀ value/role, actuator hardware, spring preload/characterization, clearance through inversion and real wheel contact. Do not treat derived torque agreement or a collision-free drawing as hardware validation. The immutable assumptions and decisions are summarized in [decisions](../docs/decisions.md); accepted shared requirements remain in the existing repository records.

## Unified Motion Lab, 2026-10-10

The shared browser menu now separates independent mathematical simulation,
2D Pymunk physics and miscellaneous motion studies, with dark mode, Plotly
charts and a profile/data browser. Use Start Motion Lab.cmd at port 4186;
familiar browser launchers are aliases and the native debugger is preserved
separately. Full workflow, JSON contracts, MATLAB/SciPy agreement and current
verification are in the [unified workspace record](../docs/unified-motion-lab.md).
