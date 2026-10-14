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
