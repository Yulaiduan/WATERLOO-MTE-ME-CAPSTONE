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
