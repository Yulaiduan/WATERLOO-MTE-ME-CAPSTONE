# Wheel Leg Lab: both chat handoffs

Author: Andy Zhang with Codex. Date: 2026-10-09. Status: experimental. Import base: `0b55ff6`; publication revision is in Git history.

The user requested current animations and wheel/link-ratio simulations from **Create a rough animation** and **Optimize wheel-to-link ratio** under Andy's apps. [Wheel Leg Lab](../../../users/andy-zhang/experimental-apps/wheel-leg-lab/README.md) retains source, portable launchers, model/coordinate notes, decisions, tests and reference equations. This is curated engineering context, not a private transcript/account export.

The rough chat established the grounded 2:1 straight path and independent coaxial wheel drive, then explored tilted/mirrored inversion, timing-switching, fixed 4:1 short-stroke approximation and path families. The latest constraint prohibits guide reindexing; historical alternatives are labeled. Fixed 4:1 offers roughly 42 mm near-linear strokes with substantial transition/joint travel.

The ratio chat corrected tangential projection versus constrained support, separated support torque from suspension impedance, built Pymunk with a 200 mm wheel radius and 50 mm extension spring, added engine/native inspection, moving disturbances and N/kgf, and checked the belt equations. Two reference torques agree conditionally with inferred 400 mm links; r_B and T₀ value/span interpretation remain missing. Defaults are not shared hardware selections.

The imported models pass 24 JavaScript and 19 Python tests, independent energy comparisons and browser checks. Both 4186 and legacy 4175 launchers pass lifecycle checks. Canonical robot physics is not applicable to the member toolkit; shared assets remain unchanged. See [validation](../../../users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md) for actual results, corrected harness checks, skipped repository fixtures and limits.

Continue with app [context](../../../users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md) and [handoff](../../../users/andy-zhang/experimental-apps/wheel-leg-lab/docs/handoff.md). Confirm belt inputs, hardware, spring/motor limits, clearance and contact requirements before promotion into canonical code.
