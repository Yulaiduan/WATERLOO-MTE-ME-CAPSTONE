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
