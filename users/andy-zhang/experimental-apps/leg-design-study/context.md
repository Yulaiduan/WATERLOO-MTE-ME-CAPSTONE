# Leg design report — continuation entry

Owner: Andy Zhang. Updated: 2026-10-14. Source base: `6c74cfd`.
Status: conditional experimental results; no accepted hardware selection.

The owner requested a standalone offline HTML design report and PDF, explicitly
excluding the new study from Motion Lab tooling. Open [index.html](index.html)
directly. The [README](README.md) covers optional reproduction; the
[handoff](context/README.md) records decisions and validation boundaries.

- [Design study and assumptions](docs/generalized-leg-study.md)
- [Math and optimization methods](docs/generalized-leg-math.md)
- [Independent 2D/Pymunk physics](docs/generalized-leg-physics.md)
- [Impact load envelope](docs/impact-load-envelope.md)
- [Validation](docs/validation.md) and [revision history](docs/revisions.md)
- [PDF](docs/generalized-leg-report.pdf) and [selected evidence](docs/generalized-leg-report-data.json)

The 200 mm wheel radius, 200 mm minimum / approximately 250 mm preferred usable
travel, and 300–350 mm total including all buffers are the owner's inputs.
Preserve Jonathan's conventions, the existing undamped models and the rejected
dual-rope design's IMPOSSIBLE status. This report does not change Motion Lab's
historical profiles, interfaces or design decisions.

## Alpha-zero inversion follow-up, 2026-10-14

Source base: `865b5f1`. Open [inversion-paths.html](inversion-paths.html) for the
new separate report and [study reasoning](docs/inversion-path-study.md) for
exact assumptions and conclusions. The strict search keeps phi0=0 and spans
26,461,800 geometry/window combinations. Equal 350 mm links and a 7:4 guide give
325/285 mm total/usable travel, 12.02 degree chord tilt and 9.66 mm bow on the
normal branch; local tangents vary 6.27–20.47 degrees. Inversion mirrors this
branch, with a vertical fold tangent. No phase-zero crossing window met the
illustrative quality limits, and all near-equal full sweeps fail the coplanar
200 mm-wheel clearance filter. Explicit lower-link indexing at phi0=-25 degrees
and guide 2:1 gives a true 12.5 degree line for equal links but still crosses the
hip; axial packaging remains unresolved. The previous spring/motor estimates
are not transferred to these new geometries.

## Force/travel follow-up, 2026-10-14

Source base `d1596e5`; publication is the commit adding [force-travel.html](force-travel.html).
Read [the detailed record](docs/force-travel-study.md), [selected evidence](docs/force-travel-results.json),
[original-model checks](docs/force-travel-math-checks.json) and [new engine checks](docs/force-travel-engine-checks.json).
The owner requested force and travel rankings for the slightly tilted invertible
ideal paths. The new screen uses peak useful Jz (worst force per direct hip Nm),
height-weighted RMS, explicit control range and 300/325/350 total heights.

Rounded 320/320 mm, guide 9:5, alpha=phi0=0 gives 325/285 mm, 10.313 degree chord,
9.179 mm bow and 57.832 Nm equivalent static hip peak at 110.3625 N. Its total
normal interval is 110–155.398 degrees; local tangents 5.049–19.302 degrees.
Near-equal local minimum 293.780/309.242, r1.786363 touches clearance, angle,
tangent-span and 5% mismatch bounds. Prefer the rounded option's allowance.
If indexing is accepted, 300/300, r2, phi0 -25 gives an exact 12.5 degree line,
similar peak 57.263 Nm and larger useful ROM 44.274 degrees; normal start 87.5
and shifted full envelope require changed ROM. This remains a separate relaxation.

All full coplanar inversion checks fail. New 3/4g values are held-load sensitivities,
not impacts; no new spring or motor rating is inferred. Five new tests, 10,248
V2/Andy 2D scalar checks and three actual fine Pymunk geometry sweeps pass;
coarse 2ms failures remain recorded. The old models/reports, live examples/GIFs,
and historical dual-rope IMPOSSIBLE status are preserved.

## Curved lateral-path follow-up, 2026-10-14

The owner cancelled R²/fixed-line optimization before publication and confirmed
25/50/75/100 mm sideways-travel comparisons. The current deliverable is
[curved-paths.html](curved-paths.html), its [PDF](docs/curved-path-report.pdf) and
[design/math record](docs/curved-path-study.md). Keep alpha=phi0=0, 325 mm total
vertical travel including assumed20+20 mm reserves, and285 mm useful.

Equal185/190/200/205 mm links at r1.9/1.8/1.7/1.6 permit approximately25/50/75/100 mm
normal lateral excursion. Balanced geometric seed190/190 mm9:5 gives49.981 mm
lateral travel,37.363 Nm equivalent45kg static hip peak and61.816 degree useful
hip ROM. These short cases fail normal coplanar220 mm clearance; the50 mm
normal-clearance alternative is285/285 mm,r1.85. Full near-equal coplanar
inversion still fails. Lateral mobility is not measured compliance; actual
spring/controller/geometric stiffness and contact remain unresolved.

The new grid enumerates2,953,002 windows, with hard constraints and separate
force/size leaders; no R² objective. Six new tests,10,788 original-model scalar
comparisons and three actual constrained geometry refinements pass. Prior
reports, spring/motor cases, Motion Lab examples/GIFs and IMPOSSIBLE decisions
remain separate and intact. Read validation/revisions before continuing.
