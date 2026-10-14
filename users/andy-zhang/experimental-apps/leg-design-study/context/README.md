# Design report handoff

Andy Zhang with Codex, 2026-10-14. Source base: `6c74cfd`; publication is the
commit adding this folder. Read [the context index](../context.md).

The initial implementation was checked inside a development Motion Lab study.
The owner then clarified that delivery must be an offline static HTML webpage
and PDF, without adding the study to Motion Lab tooling. The unshipped UI/API
integration was removed; equations, selected evidence, tests and design history
are retained here. Earlier browser/backend checks in validation are development
history, not claims about controls on the static page.

The compact bounded peak-search example is L2=180, L3=340 mm, qab=1.775 and
alpha=4.375 degrees. A 325 mm total capacity with 20 mm at each end gives 285 mm
usable travel. Both link bounds are active; a larger-link search lowers torque
at the cost of size and drift, so this is a conditional compromise, not a global
minimum. Peak and RMS objectives select different designs.

The physical example assumes m1=8.3, m2=m3=.35, m5=.10 and m6=.90 kg (10 kg
per leg), with 11.25 kg sensitivity for a 45 kg robot. The screenshot's zero
moving masses remain an analytical limit. The hip-bellcrank spring fit is
4.3698 N/mm and 213.95 N installed preload; its one-second 285 mm stroke needs
6.449 Nm peak / 3.641 Nm RMS direct hip-input torque, 1.605 rad/s and 6.573 rad/s².
The guide ratio and optional motor gearing are separate power mappings.

All nine spring topologies are generalized and checked against the existing
2D force laws and actual Pymunk stepping. Both movement directions are checked.
Three/four/five-g held-load sensitivities do not predict impact events; spring
packaging, drivetrain inertia, thermal duty, impact stroke and contact sharing
remain unresolved. No damping, hardware, canonical robot or GPU validation is
claimed. Historical dual-rope remains IMPOSSIBLE / rejected.

## Alpha-zero angled-path search, 2026-10-14

New source base `865b5f1`; publication is the commit adding
[inversion-paths.html](../inversion-paths.html). Read the
[decision/math/search record](../docs/inversion-path-study.md),
[selected data](../docs/inversion-path-results.json) and
[actual engine evidence](../docs/inversion-engine-checks.json).
This is the owner's separate overnight report, without Motion Lab integration.

The strict alpha=phi0=0, ratio/near-equal-length search enumerates 26.46 million
windows. Useful angled normal branches exist, but symmetry forces a vertical
fold tangent and opposite tilt after inversion. The equal 350 mm 7:4 example
has 325 mm total/285 usable, 12.02007 degree chord and 9.65874 mm bow; it fails
<=2% bow and its tangents exceed 10–15 degrees. Longer 450 mm tested branches
bow about 6.16 mm, at active size/angle bounds. No full near-equal sweep clears
a coplanar 200 mm wheel; an axial stagger needs measured geometry.

The separately labelled phase relaxation retains alpha=0, uses guide 2:1,
phi0=-25 degrees and equal links for an exact 12.5 degree line. Near-equal
275/250 mm gives 343.099 mm height, 1.544 mm bow and tangents 10.762–12.859 degrees;
minimum hip distance is only 25 mm. Do not silently replace the strict request
with this indexing change or claim a collision-disabled run proves packaging.

Five new numerical tests and 8,784 original-V2/browser scalar comparisons pass.
Five actual constrained Pymunk angular sweeps pass at 1/0.5 ms and converge;
all 2 ms coarse path checks fail the 0.1 mm tolerance and remain recorded.
The earlier height-inverse endpoint-roundoff failure is also retained. No
spring, motor, contact/impact, hardware or canonical robot certification is
added. Preserve historical IMPOSSIBLE dual-rope status and the prior report.
