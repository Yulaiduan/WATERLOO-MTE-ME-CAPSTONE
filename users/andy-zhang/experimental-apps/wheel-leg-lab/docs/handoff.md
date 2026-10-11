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

Historical position-input release (2026-10-10): all 27 Python tests passed, including an independent energy-model response and timestep refinement. Continue from the updated validation/model docs. The previous force runs remain valid legacy tests; they do not represent the user's corrected excitation.

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

## Historical eight-preset continuation (superseded defaults, 2026-10-10)

The user's latest clarification defines pull-through by increasing rod/cable
travel compressing the coil, with editable demo dimensions and selectable coil
law. At this release, eight presets ran through a common geometry/force kernel in independent
SciPy and actual Pymunk. Read [presets](suspension-presets.md) and the expanded
[validation](validation.md) before changing their signs or force sites.

The GUI button launches the actual live Pygame desktop solver on the host;
recorded browser playback is separate. Close that desktop window to stop it.
Native launch sessions/configs/logs/screenshots remain in ignored .preview.
The browser library/profile exports preserve the selected mechanism settings.

Historical release evidence: all 64 Python and 32 JavaScript tests passed. Preset browser and actual desktop API
checks pass; the MATLAB companion is explicitly limited to the original
captured/direct tip spring. A 40 mm hip drum with an 8 kN/m coil is passively
unstable around the demo ride pose, even with balanced initial preload.
Confirm real mounts, routing, travel, rates and component limits before
interpreting the demo as a selected suspension design.

## Historical constant-lift release (2026-10-10)

The user requested both the pictured lever and a wheel-leg adaptation. Both
now run independently in SciPy and actual Pymunk with JSON/library support,
Plotly charts and live desktop launch. Read [constant lift](constant-lift.md):
the coil tension varies, while ideal equivalent elastic lift is constant.
The default lever is 21.57463 N; the wheel shape support is 84.751637708 N,
including the stated chassis/link gravity contributions. These are demo values.

Automatic rate calibration preserves zero effective free length and a positive
physical coil length. This produces neutral gravity compensation rather than
a restoring ride-height spring. The complete 82 Python and 33 JavaScript tests,
both browser tools and four native cases pass; use the latest validation record.

## Historical two-stage follow-up (superseded factory, 2026-10-10)

At this stage, the user choice was interpreted as the 2:1 folding wheel-leg with a restoring spring and
damper. Open `/?tab=physics&architecture=constant-lift` or use the lever bridge.
The weight stage remains separate from the hip-to-tip ride strut, whose auto
free length sets zero initial elastic load. Both solvers reconstruct combined
pin/torque loads, with separate force/energy channels and four actual shapes.
Read [architecture](suspension-architecture.md) and the latest validation.
The complete 90 Python/33 JavaScript tests, architecture browser flow and five
native cases pass. Preserve archives and confirm physical packaging/contact
before promoting this ideal one-corner model.

## Continue from the corrected replacement model

The latest clarification replaces the original lower-tip spring with one
upper-r1/chassis-massblock spring/damper. Open the same architecture route.
Auxiliary is off, primary damping is 100 N s/m, chassis and 28/14 mm guide drums
are sensors, and the knee controller stays disabled. Elastic constant lift is
neutral; do not describe it as positive restoring ride stiffness.

Current nine-preset defaults use `point_force`; the old DampedSpring path is an
explicit restricted diagnostic. Read [mechanism audit](mechanism-audit.md) for
the repaired passive defaults and finite six-second envelope. Read the latest
[validation](validation.md) block for actual solver, browser, native-window,
MATLAB and launcher evidence rather than an older release's counts.

Guide material dots/spokes and tangent vectors follow recorded geometry. Unknown
baseline supplies only a tension difference; optional viewer baseline N/kgf is
independent of reference T₀ and is not applied to solver pin forces. Keep that
metadata outside solver config when exporting, loading or launching native GUI.
Preserve the archives and confirm hardware routing, measured tension, travel,
contact and structural limits before canonical promotion.
