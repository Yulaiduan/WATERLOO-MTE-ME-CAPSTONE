# Continuing both chats' work

Author: Andy Zhang with Codex. Updated: 2026-10-10. Status: experimental. Import base: `0b55ff6`; current revision is in Git history.

## Rough-animation chat

Retained current outputs: straight 2:1 moving-belt leg, independent coaxial drive, tilted invertible line, left mirror, two-position timing change, fixed 4:1 left-working approximation and fixed-ratio mathematical path family. The latest constraint is a permanently fixed guide pulley. The earlier reindexing demo is preserved as a superseded alternative, with its wheel/hip overlap and coordinated timing requirement visible.

The exact equal-link straight path, ellipse for unequal 2:1 links, timing-offset tilted line, and chassis-referenced wheel speed cancellation are geometric results. The 4:1 / 250 mm / 168.449 mm study has short near-linear strokes and substantial transition/joint-travel costs. No collision envelope, belt tooth design or hardware travel is established.

## Wheel/link-ratio chat

Retained current outputs: adjustable force/motion calculator, actual Pymunk spring fixture, native/debug object inspector, recorded remote preview with traveling disturbance, dual N/kgf displays and the reference equation cross-check. The model separates force capacity from required support torque and from effective suspension stiffness/damping. Required travel equal to wheel radius is provisional.

The clear reference image includes Fy r_w and distinct T₀/T force terms. Its two reported motor moments are conditionally reproduced with equal 400 mm links and a 200 mm radius; the implemented fixture defaults remain 273 mm links. T₀ is belt tension but its magnitude/span role and r_B remain unavailable. The ideal angular guide cannot supply detailed belt-bearing loads. Free hub loading and bottom loading with locked drive are selectable different models.

## Position-input correction, 2026-10-10

The user clarified that the disturbance is position, not force. The Pymunk default is now a prescribed wheel-height step and dynamic floating chassis with pitch held. Height command/achievement and chassis response are separate traces; driver force, pins, torques and acceleration are measured outputs. The editable 30 mm / 250 ms smooth-rise demo values are assumptions. Alternatives fix the hip or wheel; force/torque inputs remain labeled diagnostic. Recorded remote cases are regenerated from this solver and can be reproduced with `scripts/record_position_preview.py` before the build.

All 27 Python tests pass, including an independent energy-model response and timestep refinement. Continue from the updated validation/model docs. The previous force runs remain valid legacy tests; they do not represent the user's corrected excitation.

## How to continue

Run setup/build from the app root, then its start launcher. Inspect the gallery, detailed bench and Pymunk space before editing. Use the [coordinate map](model.md), [decisions](decisions.md) and [validation record](validation.md). Source and reference fixtures are portable; generated output remains local. Shared requirements and canonical assets retain their existing authority.

Next confirm real pulley radii/route and belt tension, physical spring/motor limits, structural properties and wheel/chassis clearance. Extend contact/terrain physics only as a deliberately validated new model, not by treating the scrolling input graphic as a road collision. If an experiment becomes team runtime, follow promotion and canonical validation instead of importing member code into production.

## Workspace reorganization, 2026-10-10

This toolkit moved with the Git repo into the Capstone checkout root; its relative
app folder and port 4186 are unchanged. The user confirms the floating-chassis
fixture with prescribed wheel height. Original loose files remain in sibling
Capstone_Old and the [restorable archive](../../capstone-archive/README.md).
The [atlas/workbench](../../terrain-mobility-atlas/README.md) runs on port 4175,
sharing that port with this app's optional legacy geometry launcher. Both
relocated apps pass actual start/reuse/scoped-stop/restart; helpers archive state
and previous logs instead of deleting them.

## Unified Motion Lab, 2026-10-10

The shared browser menu now separates independent mathematical simulation,
2D Pymunk physics and miscellaneous motion studies, with dark mode, Plotly
charts and a profile/data browser. Use Start Motion Lab.cmd at port 4186;
familiar browser launchers are aliases and the native debugger is preserved
separately. Full workflow, JSON contracts, MATLAB/SciPy agreement and current
verification are in the [unified workspace record](unified-motion-lab.md).
