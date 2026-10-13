# Legacy Capstone archive

Owner: Andy Zhang. Updated: 2026-10-10. Status: historical preservation, not an active simulation.

Portable continuation: [context.md](context.md) and [laptop handoff](../laptop-handoff.md).

## Supplemental development history, 2026-10-12

The original snapshot below is unchanged. A separate
[development source package](development-history-2026-10-12.json) preserves
21 later local research/editing/QA source and Markdown files (86,103 original
bytes) that previously lived in ignored artifact/staging folders. Its base64
records carry original repository-relative paths, sizes and SHA-256, preserving
bytes without making historical patch helpers runnable app dependencies.
Restore with `python restore_development_history.py --output restored/development-history`
to a new directory. Exact restoration was checked; no archived source was
executed and no original local files changed. Runtime caches, raw current output,
logs and private account/chat data are excluded. Read frozen source as evidence
and use maintained app modules/tests for development.

## Original legacy snapshot

The owner requested that the former loose Capstone workspace be archived locally
and preserved under his GitHub member workspace. This package preserves **668
source, documentation, reference, data and output files**, including the original
terrain atlas/workbench, pre-position-correction Pymunk bench, animation GIFs and
frames, screenshots, CSV runs, engineering searches and terrain-source PDF.
Nothing was deleted from the original local workspace.

The complete local archive also retains installed dependencies, bytecode,
server records/logs and the rebuildable production bundle. Those six categories
are excluded from this GitHub payload; dependency manifests and all substantive
source/evidence/outputs are included. The local original-file inventory records
4,534 original files and 431 directories with SHA-256 verification.

## Restore without overwriting

Requires Python's standard library; no package installation or network access:

```sh
python restore_archive.py --output path/to/a/new/legacy-workspace
```

The output directory must not already exist. The script checks every chunk,
the combined ZIP and every restored file against SHA-256. It leaves the assembled
`.archive-package.zip` beside the reconstructed files and executes no archived
scripts. The original filenames and bytes are preserved; historical scripts may
refer to their original local paths or earlier model assumptions.

The [archive manifest](archive-manifest.json) lists every included file and the
103 ordered ZIP parts. Each part is at most 900,000 bytes, respecting the
repository's 1 MiB per-file limit without changing the shared enforcement rules.
[Payload notes](payload/README.md) explain the split format.

## Maintained apps

- [Terrain Mobility Atlas](../terrain-mobility-atlas/README.md): atlas, numerical
  terrain workbench, historical detailed linkage and force plots, with startup
  at the original port 4175.
- [Wheel Leg Lab](../wheel-leg-lab/README.md): both chats' motion studies and the
  corrected prescribed-wheel-height/floating-chassis Pymunk bench at port 4186.

The historical archive does not replace these maintained apps or define the
team's canonical robot. Read [app instructions](AGENTS.md) and
[context](context/README.md) before changing its format.

## Verification

The original workspace move preserved all 4,534 file hashes and all 431
directories. A separate reconstruction from these 103 parts restored all 668
published files with exact hashes. Original files remained unchanged. App
startup/model tests are recorded with the maintained apps, independently of
archive byte preservation.
