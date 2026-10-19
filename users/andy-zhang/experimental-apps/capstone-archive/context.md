# Historical Capstone workspace — portable archive context

Owner: Andy Zhang. Updated: 2026-10-19. Status: preserved source/evidence, not an active app.

Read [README.md](README.md), [AGENTS.md](AGENTS.md) and
[context/README.md](context/README.md). This package is under the member's
experimental-apps folder so a laptop clone can inspect history without access
to the PC or sibling Capstone_Old folder.

| Package | Inventory | Restoration |
| --- | --- | --- |
| Original 2026-10-10 snapshot | [archive-manifest.json](archive-manifest.json), 668 files / 103 ZIP parts | `python restore_archive.py --output NEW_DIRECTORY` |
| 2026-10-12 local development source supplement | [development-history-2026-10-12.json](development-history-2026-10-12.json), 21 source/editing/research/QA files / 86,103 original bytes | `python restore_development_history.py --output NEW_DIRECTORY` |
| 2026-10-19 PC transfer supplement | [development-history-2026-10-19.json](development-history-2026-10-19.json), 14 superseded source/report/check files / 1,519,499 original bytes | `python restore_development_history.py --source development-history-2026-10-19.json --output NEW_DIRECTORY` |

Both restorers use Python's standard library, validate exact bytes/SHA-256,
write only to a new directory and never execute archived code. The supplement
is separate; the original 668-file snapshot and payload hashes are unchanged.
Paths in the supplement preserve the source's repository-relative location.
Historical editing helpers may mutate old versions if executed: read as evidence
and prefer current maintained modules/tests, never replay a patch helper.

The original local archive preserves installed dependencies, caches and old
process state. These are intentionally excluded from transfer because a laptop
recreates its own environments/builds. Raw current output is ignored; reviewed
findings and Git/contribution history are retained with the maintained apps.
Public project context is summarized in Markdown, not private chat/account exports.

The October 19 supplement preserves the cancelled fixed-15-degree corridor
study and two browser inspection scripts. Schema v2 compresses each file before
base64 storage; the restorer accepts both v1 and v2 and retains its old default.
The package preserves bytes, not runnable integration or renewed numerical
validation. Continue from [the PC handoff](../pc-handoff.md) and the maintained
curved-path/RMS studies; do not reinstate the cancelled method by restoring it.

For development, use [Motion Lab](../wheel-leg-lab/context.md) or
[Terrain Atlas](../terrain-mobility-atlas/context.md), following
[laptop-handoff.md](../laptop-handoff.md). These are independent experiments and
do not replace shared requirements, canonical robot assets or validation gates.
