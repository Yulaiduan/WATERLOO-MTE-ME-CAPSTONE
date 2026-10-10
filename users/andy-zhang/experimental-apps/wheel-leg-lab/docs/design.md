# Toolkit design

Author: Andy Zhang with Codex. Updated: 2026-10-10. Status: exploratory engineering interface.

The toolkit keeps both chats' outputs discoverable through the gallery while preserving a separate model for each question. Raw animation fragments remain editable source, the force calculator demonstrates geometric tradeoffs, the detailed bench exposes continuous mechanics/control, and Pymunk exposes an actual rigid-body space. Each view states its assumptions instead of borrowing validation from another layer.

The Pymunk screen keeps input controls alongside the mechanism, live joint force components/resultants, separate torque channels and trace plots. Engine debug draw is the default; annotated geometry remains optional. Playback, markers and readouts use one saved run even if input controls have changed. A traveling prescribed-height profile below the mechanism, a displacement arrow and commanded-height marker show the disturbance at the same recorded time. The wheel follows the input while the floating chassis responds through the suspension. The profile is a boundary command, without solved terrain contact. Legacy diagnostic force/torque modes use application arrows.

Position steps, square waves and bump pulses use mm amplitude and finite rise/fall times; the smooth C2 ramp avoids velocity/acceleration jumps. Linear ramps remain selectable with a peak-load warning. Force/torque impulse area belongs only to legacy diagnostic modes. Full CSV and run JSON preserve SI data and assumptions; kgf is a display/reference conversion. The remote page offers two retained position step/square cases with measured joint/driver loads and chassis motion for small-screen inspection, not a Python engine running inside the page.

The historical timing-switch animation remains visible but labeled as incompatible with the later permanently fixed-pulley constraint. The fixed 4:1 example shows both short working strokes and the full transition so the path approximation does not conceal large excursion and knee travel.

Desktop and mobile layouts, native GUI inspection, offline resources and repeatable startup are checked locally. The styles are app-owned; pages need no private chat session or external account. See [validation](validation.md) and [decisions](decisions.md).

## Unified Motion Lab, 2026-10-10

The shared browser menu now separates independent mathematical simulation,
2D Pymunk physics and miscellaneous motion studies, with dark mode, Plotly
charts and a profile/data browser. Use Start Motion Lab.cmd at port 4186;
familiar browser launchers are aliases and the native debugger is preserved
separately. Full workflow, JSON contracts, MATLAB/SciPy agreement and current
verification are in the [unified workspace record](unified-motion-lab.md).

The shared Math/Physics controls now expose [eight suspension presets](suspension-presets.md),
coil behavior and independent direct/rod/ideal-rope transmission. Demo dimensions
are labeled editable, and drawings use the actual recorded force sites with
coil travel/load/energy charts. A topology selection resets mechanism geometry;
saved profiles preserve explicit edits. The native button opens a live desktop
solver on the host, while recorded browser playback remains separately labeled.

The [constant-lift study](constant-lift.md) appears in both mathematical tools
and Miscellaneous studies. Its plots distinguish varying coil tension and
moment from equivalent lift, and compare ideal compensation with an ordinary
finite-free-length coil. Its wheel adaptation is the ninth suspension preset.
Each model keeps its own runnable profiles and native solver geometry.
