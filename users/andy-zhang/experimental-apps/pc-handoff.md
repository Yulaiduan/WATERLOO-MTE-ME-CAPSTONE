# Return Capstone development to the PC

Owner: Andy Zhang with Codex. Updated: 2026-10-19.
Status: source/context transfer; PC runtime setup is not certified by this audit.
Source base: `e91897a`; this handoff is published in the subsequent commit.

## Start here

The maintained code, reports, dependency manifests, launchers and engineering
context already live in this repository. Andy's four workspaces are linked in
[README.md](README.md) and [context.md](context.md). Keep the complete checkout:
the report verifiers also use the original Jonathan solver and sibling Motion
Lab modules. Shared records stay in their owning folders and arrive in the same
pull; no duplicate app or canonical robot is created for the PC.

From the existing PC checkout, inspect `git status --short --branch` and
`git remote -v` first. For a clean `main` tracking this repository:

```sh
git fetch origin
git merge --ff-only origin/main
git config --local core.hooksPath .githooks
git status --short --branch
```

If there are local edits, another branch or divergence, preserve that work and
follow [Git hygiene](../../../agent_skills/git_hygiene.md). Repository onboarding
remains in [docs/setup.md](../../../docs/setup.md). The previous
[laptop handoff](laptop-handoff.md) retains verified dependency installation,
fresh-clone and Windows launcher evidence; its October 12 continuation snapshot
is historical. Do not copy a virtual environment or installed Node dependencies
between computers. Rebuild from each app's manifests when needed.

## Current code and continuation map

| Work | Entry point | Continuation |
| --- | --- | --- |
| Offline leg design | [Leg design context](leg-design-study/context.md), [RMS report](leg-design-study/rms-link-comparison.html), [sweep brief](leg-design-study/docs/next-sweep-brief.md) | Latest Andy study is RMS/equal/upper-long/lower-long comparison, published at `3908c3b`; preserve prior reports and assumptions |
| Motion Lab | [Context](wheel-leg-lab/context.md), [merged linkage](wheel-leg-lab/docs/merged-linkage.md) | Existing mathematical and Pymunk benches include editable geometry and original Jonathan reference calculations; the offline reports remain separate |
| Terrain Atlas/workbench | [Context](terrain-mobility-atlas/context.md) | Maintained atlas, reduced terrain model and historical linkage; measured and synthetic inputs remain distinct |
| Historical source | [Archive context](capstone-archive/context.md) | Original 668-file snapshot, October 12 supplement and newly preserved October 19 supplement |
| Shared controls | [Andy's project context](../../../context/users/andy-zhang/README.md) | Curated controls discussions, unresolved interfaces and source links |
| New upstream solver | [Jonathan's solver README](../../jonathan-xie/experimental-apps/vsl-solver/README.md), [V4 model](../../jonathan-xie/experimental-apps/vsl-solver/v4/v4-model.md), [context](../../jonathan-xie/experimental-apps/vsl-solver/context/README.md) | Fetched at `e91897a`, titled “V4 VSL Solver (constant force pulley)”; retained in its existing member folder |

The Jonathan solver's app-local `AGENTS.md` is absent at the audit base. No solver
edits, execution or new validation were performed here; resolve that missing
required entry file before dependent work on that app. Its recorded tests remain
the original author's evidence, not tests rerun for this transfer.

For Andy's current report, retain max/min link length <=1.25, alpha=phase=0,
200 mm wheel radius and the explicitly assumed 20+20 mm reserves inside 325 mm
total/285 mm useful height. Hip RMS and relative-knee RMS can rank designs
differently. Equal 190/190 mm at guide 1.8 remains a useful comparison; reverse
180/225 mm at 1.7 is a compact lower-long example, not an accepted hardware choice.
Read [RMS study](leg-design-study/docs/rms-link-study.md) for actual objectives
and evidence. Physical axial/chassis/tire clearance, moving masses, real spring
and motor duty, contact and impacts remain unresolved. Preserve the historical
dual-rope design's **IMPOSSIBLE / rejected** status and undamped position-input
models; no new search or model change is requested by this transfer.

## Windows entry points

| App | Existing manual launcher | Preview after local startup |
| --- | --- | --- |
| Motion Lab | [Setup Motion Lab.cmd](wheel-leg-lab/Setup%20Motion%20Lab.cmd), then [Start Motion Lab.cmd](wheel-leg-lab/Start%20Motion%20Lab.cmd) | [Motion Lab](http://127.0.0.1:4186/) |
| Terrain Atlas | Follow its README's `npm ci` / `npm run build`, then [Start Terrain Atlas.cmd](terrain-mobility-atlas/Start%20Terrain%20Atlas.cmd) | [Atlas](http://127.0.0.1:4175/), [workbench](http://127.0.0.1:4175/workbench/) |
| Latest offline report | [Open RMS Comparison.cmd](leg-design-study/Open%20RMS%20Comparison.cmd) | [Static HTML](leg-design-study/rms-link-comparison.html); no server/runtime needed |

Existing start/stop launchers and URLs are unchanged. Startup, rebuilds and
restart on the destination PC still need verification there; this publication
does not start services or install login/boot tasks. Browser-saved profiles and
runs require explicit JSON download/import on the respective computers. Git
transfers the source defaults and reviewed context, not browser storage or
private chat/account history.

## Source preservation audit

The starting checkout was clean at `3908c3b` and fast-forwarded to `e91897a`.
There were 555 tracked files under Andy's experimental apps before this update
and no nonignored untracked files. A targeted scan of app artifact folders found
the cancelled fixed-15-degree study and two historical browser inspection
scripts that were not tracked. The new
[October 19 archive](capstone-archive/development-history-2026-10-19.json)
preserves all 14 files: 1,519,499 original bytes, compressed into 520,678 bytes
with per-file sizes and SHA-256. It includes the offline report, PDF, selected
JSON evidence, source, checks and opener. The study was superseded by the curved
path request; restoring it does not restore it as the recommended design.

From the archive app, restore into a new directory for inspection:

```sh
python restore_development_history.py --source development-history-2026-10-19.json --output restored/pc-transfer-2026-10-19
```

The old default command still restores the unchanged October 12 package.
Neither command executes the archived scripts. Historical scripts may depend
on older sibling modules/paths; their retained numerical claims were not rerun.
Original local files remain untouched. Dependencies, caches, generated app
bundles, logs, raw screenshots/runs and private material remain outside Git.

Actual transfer checks: all 14 new files restored byte-for-byte against local
originals; all 21 older supplement files restored against their retained hashes.
The restorer rejected existing destinations, path traversal, a wrong checksum
and an unknown encoding before writing output. App suites, report calculations,
PC startup/restart and canonical physics were not rerun for this preservation
update. Repository publication checks are recorded in the contribution log.

## PC continuation prompt

```text
Continue Capstone on this PC from the shared repository's latest main.
Inspect the checkout and preserve local changes before updating. Follow root
AGENTS.md, read all tracked database/ and agent_skills/ files, CONTRIBUTING.md
and the latest contribution entry. Read
users/andy-zhang/experimental-apps/pc-handoff.md and context.md, then the selected
app's README.md, AGENTS.md and context/README.md before changing it.
Use the existing member folders and linked shared sources. Keep the offline
leg reports separate from Motion Lab and preserve prior rejected designs.
If launching an app, inspect installed runtimes, rebuild its local dependencies
as needed and verify its existing manual launcher and restart on the PC.
Keep Motion Lab at 127.0.0.1:4186 and Atlas/workbench at 127.0.0.1:4175.
Record actual tests and remaining limitations, update app context and append
the contribution log, then run the required scoped checks before publishing.
```
