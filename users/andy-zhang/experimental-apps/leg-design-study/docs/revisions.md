# Leg design revision map

Owner: Andy Zhang. Updated: 2026-10-14. Status: navigation for experimental
design history; Git and the repository contribution log retain exact changes.

| Revision / date | Design change | Continue from |
| --- | --- | --- |
| `2353a6f`, 2026-10-12 | Equal-link sizing for 200 mm wheel radius and 200 mm usable lift; buffers, peak/mean/flatness | [Link sizing](../../wheel-leg-lab/docs/link-sizing.md) and its original result scope |
| `7cfacbf`, 2026-10-12 | Actual laptop runtime/dependency reconstruction and both local app lifecycles | [Laptop handoff](../../laptop-handoff.md) |
| `3bbe964`, 2026-10-12 | Upward wheel-centre angle, individual torque curves, lift/RMS score, explicit hip/knee work mapping | [Link sizing](../../wheel-leg-lab/docs/link-sizing.md), [validation](validation.md) |
| `6c74cfd`, source baseline for 2026-10-14 | Jonathan V1/V2 and bounded global headline maxima available on main | [Jonathan V2 model](../../../../jonathan-xie/experimental-apps/leg-solver/v2-model.md) |
| 2026-10-14 generalized design study | Merge variable-ratio/alpha conventions with sizing, explicit control windows and spring/motor example; exact publication hash is the commit adding this row | [Design study](generalized-leg-study.md), [math](generalized-leg-math.md), [physics](generalized-leg-physics.md) |

Use `git log --oneline -- users/andy-zhang/experimental-apps/leg-design-study`
from the repository root to find the exact publication and later revisions.
Use `git show <revision>:<repository-relative-path>` for a read-only historical
comparison. The log's four-section entries identify exact changed paths,
commands, failures and handoffs; do not replace that append-only evidence with
this index.

Preserve the historical dual-rope model and its **IMPOSSIBLE / rejected** label,
the user-requested rollback, the legacy position-input fixtures and the
undamped single replacement spring. Generalized study assumptions do not
silently migrate older saved profiles or certify earlier hypothetical designs.

## Delivery correction, 2026-10-14

The owner requested the design report/PDF as a standalone offline static HTML
webpage and explicitly excluded this study from Motion Lab tooling. The initial
unpublished Motion Lab entry, API routes and interactive study were removed.
This folder retains the scientific models, selected evidence, report and
reproduction checks; the existing wheel sizing calculator stays unchanged.

## Alpha-zero path and full-inversion study, 2026-10-14

Source base `865b5f1` is the published earlier offline report. This follow-up's
publication is the commit adding `inversion-paths.html`; use the app's Git log
for its exact hash. The owner requested 10–15 degree approximately linear
paths from guide ratio and equal/near-equal link lengths at alpha=0, including
full inversion. [The new record](inversion-path-study.md) keeps phase0 strict,
compares 26.46 million normal/crossing windows, records the symmetry/clearance
limits, practical 7:4 branch and explicit assembly-indexing alternative.

New files contain the independent search, five tests, actual angular Pymunk
fixture, retained results, local HTML/12-page PDF generator and browser verifier.
The earlier report gets a navigation link only. The previous numerical model,
Motion Lab source/services and spring/motor results are unchanged. Canonical
robot validation is not applicable; unresolved physical inversion remains open.

## Labelled Motion Lab illustrations, 2026-10-14

The owner subsequently requested labelled examples and animation GIFs for the
leading path options. Source report revision is `12e227c`; publication is the
commit adding wheel-leg-lab/web/design-examples.
[The visualization record](../../wheel-leg-lab/docs/design-examples.md) owns the
new live drawings and ten curated GIFs, with exact retained cases and geometry
checks. The offline report/PDF, optimizer and physics models are not embedded
in Motion Lab; only the separately requested read-only mechanism examples are
added. Preserve fixed-phase/clearance limitations and historical decisions.

## Force and useful-travel ranking, 2026-10-14

Source base `d1596e5`; publication is the commit adding `force-travel.html`.
The owner requested the best force/travel tradeoffs for the slightly tilted,
invertible ideal designs. [The new record](force-travel-study.md) retains a new
11.48-million-window force-first grid, local refinement, total-height comparison,
explicit fixed-indexing relaxation and separate geometry/force validation.
The nine-page PDF/offline HTML do not alter Motion Lab controls, saved profiles,
existing examples/GIFs, old reports or spring/motor calculations.

Rounded 320/320 mm 9:5 is the phase-zero compromise; 300/300 mm 2:1 with fixed
phase -25 degrees is the exact-line alternative. Their ideal inverses do not
resolve full coplanar clearance. All assumptions, active bounds, rejected
diagnostics, held-load versus impact distinction and test failures stay recorded.

## Curved lateral mobility instead of R², 2026-10-14

Numerical source base `93fed9f`; publication is the commit adding
`curved-paths.html`. Before publication the owner cancelled the proposed
fixed15-degree corridor/R² search, then confirmed25/50/75/100 mm sideways
comparisons. Superseded untracked work was preserved only in ignored local
artifacts. It is not a published method or recommendation.

[The replacement study](curved-path-study.md) retains alpha=phi0=0 and325/285 mm
total/useful height. A2.953-million-window search compares curved normal paths,
force/size leaders, lateral coupling, normal-clearance alternatives, full
inversion and90/95-degree ROM sensitivities. New six tests, original-model and
actual-Pymunk checks accompany the standalone seven-page PDF/static HTML.
No old model/report, Motion Lab source/example/GIF, spring/motor rating or
historical IMPOSSIBLE decision is replaced. Resolve physical packaging and
effective stiffness before promoting permitted motion into a hardware claim.

## Unequal-link inversion, 2026-10-14

Source base `1a3fb7e`; publication is the commit adding
`unequal-inversion.html`. [The new record](unequal-inversion-study.md) searches
11.535 million unequal-link windows with separate geometry/segment/pitch-circle
families and peak-force/size objectives. The owner asked for good unequal
invertible paths; cancelled R²/fixed-line ranking remains cancelled.

Four rounded lower-long examples, labelled GIFs and a six-page PDF retain
alpha=phase=0 and325/285 mm normal height.160/475 mm,r1.42 is the50 mm seed.
New analytic upper-segment proof rejects upper-long false positives and the
stronger wheel/hip pitch-circle screen excludes point-only clearance cases.
Actual rods still overlap atfold; physical/axial packaging is unresolved.
Old reports, Motion Lab models/services, motor/spring cases and historical
IMPOSSIBLE decisions are unchanged. Tests/audit/parity/actual engine evidence,
failures/corrections and reproduction commands remain beside the report.
