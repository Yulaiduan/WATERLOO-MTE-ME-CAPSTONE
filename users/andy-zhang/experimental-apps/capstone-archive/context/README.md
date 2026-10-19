# Archive context

Owner: Andy Zhang. Updated: 2026-10-10. The user explicitly requested local
nondeleting reorganization and GitHub preservation of the former workspace.

The repo checkout now occupies the former parent Capstone directory; the old
loose workspace is in the sibling Capstone_Old directory. Every original local
file was hashed before moving and verified afterward. The emptied nested repo
container was moved into the archive as well rather than removed.

The payload copies all meaningful original source, notes, references, evidence
and historical outputs. Installed dependencies, bytecode, process logs/state,
dist and Git metadata are local-only categories. The manifest records exclusion
categories and full included-file hashes. Standard-library scripts concatenate
and validate the ZIP parts and extract only to a new directory without running
any payload code.

Preserve the original snapshot. New development belongs in the maintained apps,
which document their different models: a reduced terrain workbench versus the
ideal Pymunk linkage fixture. Restoration is verified for all 668 included files;
this does not certify their old numerical or hardware assumptions.

## PC transfer, 2026-10-19

[The new supplement](../development-history-2026-10-19.json) retains 14 later
ignored source/report/check files from the cancelled fixed-15-degree study and
two browser inspection helpers. Read [the archive index](../context.md) for
restoration and [the PC handoff](../../pc-handoff.md) for current work.
The restorer adds an optional `--source` argument and v2 gzip/base64 support;
its default v1 package, path/checksum checks and non-overwriting behavior remain.
No archived helper is executed during capture or restoration.
