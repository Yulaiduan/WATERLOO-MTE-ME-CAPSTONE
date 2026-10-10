# Continuing both chats' work

Author: Andy Zhang with Codex. Updated: 2026-10-09. Status: experimental. Import base: `0b55ff6`; current revision is in Git history.

## Rough-animation chat

Retained current outputs: straight 2:1 moving-belt leg, independent coaxial drive, tilted invertible line, left mirror, two-position timing change, fixed 4:1 left-working approximation and fixed-ratio mathematical path family. The latest constraint is a permanently fixed guide pulley. The earlier reindexing demo is preserved as a superseded alternative, with its wheel/hip overlap and coordinated timing requirement visible.

The exact equal-link straight path, ellipse for unequal 2:1 links, timing-offset tilted line, and chassis-referenced wheel speed cancellation are geometric results. The 4:1 / 250 mm / 168.449 mm study has short near-linear strokes and substantial transition/joint-travel costs. No collision envelope, belt tooth design or hardware travel is established.

## Wheel/link-ratio chat

Retained current outputs: adjustable force/motion calculator, actual Pymunk spring fixture, native/debug object inspector, recorded remote preview with traveling disturbance, dual N/kgf displays and the reference equation cross-check. The model separates force capacity from required support torque and from effective suspension stiffness/damping. Required travel equal to wheel radius is provisional.

The clear reference image includes Fy r_w and distinct T₀/T force terms. Its two reported motor moments are conditionally reproduced with equal 400 mm links and a 200 mm radius; the implemented fixture defaults remain 273 mm links. T₀ is belt tension but its magnitude/span role and r_B remain unavailable. The ideal angular guide cannot supply detailed belt-bearing loads. Free hub loading and bottom loading with locked drive are selectable different models.

## How to continue

Run setup/build from the app root, then its start launcher. Inspect the gallery, detailed bench and Pymunk space before editing. Use the [coordinate map](model.md), [decisions](decisions.md) and [validation record](validation.md). Source and reference fixtures are portable; generated output remains local. Shared requirements and canonical assets retain their existing authority.

Next confirm real pulley radii/route and belt tension, physical spring/motor limits, structural properties and wheel/chassis clearance. Extend contact/terrain physics only as a deliberately validated new model, not by treating the scrolling input graphic as a road collision. If an experiment becomes team runtime, follow promotion and canonical validation instead of importing member code into production.
