# Toolkit design

Author: Andy Zhang with Codex. Updated: 2026-10-09. Status: exploratory engineering interface.

The toolkit keeps both chats' outputs discoverable through the gallery while preserving a separate model for each question. Raw animation fragments remain editable source, the force calculator demonstrates geometric tradeoffs, the detailed bench exposes continuous mechanics/control, and Pymunk exposes an actual rigid-body space. Each view states its assumptions instead of borrowing validation from another layer.

The Pymunk screen keeps input controls alongside the mechanism, live joint force components/resultants, separate torque channels and trace plots. Engine debug draw is the default; annotated geometry remains optional. Playback, markers and readouts use one saved run even if input controls have changed. A traveling force/torque profile below the mechanism and an application arrow show the disturbance at the same recorded time. That profile is not terrain geometry.

Square inputs have independent ramp slopes, timing and duty cycle. Impulse input is a finite pulse with specified area. Full CSV and run JSON preserve SI data and assumptions; kgf is a display/reference conversion. The remote page offers two retained cases for small-screen inspection, not a Python engine running inside the page.

The historical timing-switch animation remains visible but labeled as incompatible with the later permanently fixed-pulley constraint. The fixed 4:1 example shows both short working strokes and the full transition so the path approximation does not conceal large excursion and knee travel.

Desktop and mobile layouts, native GUI inspection, offline resources and repeatable startup are checked locally. The styles are app-owned; pages need no private chat session or external account. See [validation](validation.md) and [decisions](decisions.md).
