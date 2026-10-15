# Andy's experimental apps — development context entry point

Owner: Andy Zhang. Updated: 2026-10-14. Status: portable member experiments.
Audit base: `2353a6f`; see Git history for the publication of this handoff.

This directory contains Andy's app/tool workspaces and offline design report. Each has
a `context.md` entry point linking its existing detailed context and development
records. The Capstone checkout remains the shared repository root; team records
in `docs/`, `database/`, `context/` and the engineering components retain their
canonical locations. They are included by the same clone and linked below.

| Workspace | Context to read | What is retained |
| --- | --- | --- |
| Offline leg design report | [leg-design-study/context.md](leg-design-study/context.md) | Static HTML/PDF, selected evidence, generalized equations and revision history; later labelled pose examples/GIFs are separately available in Motion Lab |
| Motion Lab / Wheel Leg Lab | [wheel-leg-lab/context.md](wheel-leg-lab/context.md) | Current source, simulations, calculators, seven motion studies, tests, setup/start/stop launchers, model/decision/validation/handoff history |
| Terrain Mobility Atlas / workbench | [terrain-mobility-atlas/context.md](terrain-mobility-atlas/context.md) | Atlas, reduced terrain workbench, historical linkage and force calculator, data provenance, source/tests/lockfile, design/decision/validation history |
| Legacy and supplemental source archive | [capstone-archive/context.md](capstone-archive/context.md) | Exact 668-file original snapshot plus 21 later local development source/QA/editing files; verified restorers, never executed as current code |

Read [laptop-handoff.md](laptop-handoff.md) for a verified clone/setup procedure,
the storage audit, current continuation state and a ready-to-paste laptop prompt.
The maintained [app index](README.md) gives entry points and experimental status.

## Shared development history

- [Repository contribution log](../../../ENTRY_TEMPLATE.md): append-only exact
  changes, tests/failures, assumptions and three-sentence handoffs.
- [Andy's general project context](../../../context/users/andy-zhang/README.md):
  curated controls discussions and source maps, with dated conversation summaries.
- [Reorganization record](../../../context/users/andy-zhang/2026-10-10-workspace-reorganization.md):
  provenance of the nondeleting import and legacy backup.
- [Shared project context](../../../context/start-here.md) and
  [research](../../../database/README.md): accepted/shared records stay separate
  from experimental defaults.
- Full Git history: `git log --all --date=short --oneline`, or scope it with
  `git log -- users/andy-zhang/experimental-apps/`. Normal cloning retains history;
  do not use a shallow clone when historical revisions are needed.

Git transfers source and these public engineering summaries, not private Codex
chat/account history or installed runtime environments. Browser profiles/runs
need explicit JSON download/import. Rebuild ignored dependencies and generated
assets locally; no desktop path, PC server or old local archive is required.

## Latest offline force/travel study, 2026-10-14

The owner requested force and travel ranking for the slightly tilted invertible
ideal legs. Open [leg-design-study/force-travel.html](leg-design-study/force-travel.html)
and read its [design record](leg-design-study/docs/force-travel-study.md).
Rounded 320/320 mm links with guide 9:5 retain alpha=phi0=0; fixed-indexed
300/300 mm 2:1 at phi0=-25 degrees is the exact-line alternative. Both examples
have 325 mm total /285 mm usable height. Full physical inversion still needs
resolved axial/chassis clearance; all coplanar near-equal sweeps fail.
Report/optimization stays offline, separate from Motion Lab's earlier labelled
examples/GIFs. Prior spring/motor estimates and IMPOSSIBLE decisions stay intact.

## Current curved-path study, 2026-10-14

The owner replaced the unpublished R²/straight-corridor method with curved
paths allowing25/50/75/100 mm sideways travel through ratio changes. Open
[the new offline report](leg-design-study/curved-paths.html) and
[design record](leg-design-study/docs/curved-path-study.md). Alpha and original
phase both remain zero;325 mm total vertical height includes20+20 mm reserves.
Equal190 mm links at9:5 give approximately50 mm lateral excursion, but short
cases require unresolved axial packaging;285 mm,r1.85 is the normal coplanar
clearance comparison. Actual stiffness/contact and full physical inversion
remain unresolved. Earlier published reports, Motion Lab examples and rejected
IMPOSSIBLE decisions are preserved.

## Unequal-link invertible paths, 2026-10-14

The latest [offline report and four GIFs](leg-design-study/unequal-inversion.html)
and [design record](leg-design-study/docs/unequal-inversion-study.md) broaden
the curved search to unequal links. Lower-long160/475 mm,r1.42 gives about50 mm
sideways travel with325/285 mm total/useful height, alpha=phase=0. It passes
ideal height inversion and assumed wheel/guide pitch-circle clearance; rods
still overlap atfold and need an axial/forked mechanical layout. The six-page
PDF retains the parameters, plots, screen proofs and numerical evidence.
No Motion Lab controls, old spring/motor estimates or IMPOSSIBLE decisions change.
