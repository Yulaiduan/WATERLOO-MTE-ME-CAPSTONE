# Continue Capstone development on a laptop

For the return to PC on 2026-10-19, use [pc-handoff.md](pc-handoff.md).
This document preserves the earlier setup audit; its dated continuation state
is superseded by the current app context and PC handoff.

Owner: Andy Zhang with Codex. Updated: 2026-10-12.
Status: fresh-clone reconstruction and actual Windows laptop setup verified.
Other operating systems remain untested. No PC service is required.
Audit base: `2353a6f`; the handoff's publication is the subsequent Git commit.

## What the laptop receives

Clone [Yulaiduan/WATERLOO-MTE-ME-CAPSTONE](https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE.git)
with full Git history. The shared Capstone directory is the repository root;
all three Andy apps are already under `users/andy-zhang/experimental-apps/`.
Each now has a linked `context.md`. [context.md](context.md) is the common entry
point; original detailed context/model/decision/handoff records are preserved.

At audit base 2353a6f the published app inventories were 173 Motion Lab files,
124 Terrain Atlas files and 111 archive files. Additional handoff/context and
portable-launcher files are added by this contribution. No live source or
shared record needed to move; no original local files were deleted or overwritten.

The clean GitHub clone reproduced all 40 commits at that base. The original
archive restored all 668 files with exact SHA-256. Its four ignored large
terrain PDF/CSV inputs and six historical search/export source files match
archive hashes. A separate supplement now preserves 21 later local scratch,
editing, research and QA source/Markdown files with exact hashes; these were
previously ignored. [Archive context](capstone-archive/context.md) explains both
packages and restorers. The original snapshot remains unchanged.

Installed Python/Node, app `.venv` / node_modules, built output, process logs,
current raw frames/runs and local editor/account state are not transferred by
Git. Rebuild dependencies locally. Reviewed development history lives in app
docs/context, [the contribution log](../../../ENTRY_TEMPLATE.md),
[member context](../../../context/users/andy-zhang/README.md) and Git revisions.
Private chat/account exports are not part of this public repository. Original
local Capstone_Old still exists for preservation but is unnecessary for setup.

## Clone or update

Run from a laptop directory chosen for the project; do not overwrite an existing
Capstone directory. These commands were checked with a fresh GitHub clone:

```sh
git clone https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE.git Capstone
cd Capstone
git status --short --branch
git remote -v
git config --local core.hooksPath .githooks
```

For an existing clean checkout of this remote on main:

```sh
git fetch origin
git pull --ff-only origin main
```

Inspect dirty/detached/other-branch checkouts first and preserve all local work,
following [Git hygiene](../../../agent_skills/git_hygiene.md). After laptop work
is pushed, pull on the desktop before making new changes; Git does not merge
uncommitted work or synchronize browser storage automatically.

## Windows setup and local startup

Verified runtime versions: Python 3.13.12, Node.js 22.20.0 and npm. Use installed,
durable runtimes. On another OS, inspect the dependency manifests and adapt the
venv executable path and manual launcher, then verify there; Windows `.cmd`/
PowerShell launchers are not promised to run unchanged on macOS/Linux.

For Motion Lab, from `users/andy-zhang/experimental-apps/wheel-leg-lab/`:

```sh
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
npm ci
npm run build
npm test
```

**Setup Motion Lab.cmd** wraps that first setup. Then double-click **Start Motion
Lab.cmd**, wait for Ready and open <http://127.0.0.1:4186/>. The sizing tool is
<http://127.0.0.1:4186/?tab=studies&study=ratio>. **Stop Motion Lab.cmd** stops only
the verified app process. Use these same launchers after laptop shutdown or
server closure; source/defaults are local, independent of the PC. MATLAB is
optional for the archived legacy comparison, not a startup requirement.

For Terrain Atlas, from `users/andy-zhang/experimental-apps/terrain-mobility-atlas/`:

```sh
npm ci
npm run build
npm test
```

Double-click **Start Terrain Atlas.cmd**, wait for Ready and open
<http://127.0.0.1:4175/> or <http://127.0.0.1:4175/workbench/>. Stop with
**Stop Terrain Atlas.cmd**. Node.js is discovered on PATH; stop validates the
executable recorded when starting, PID/time, app folder and fixed Vite arguments.
Legacy Start Capstone/Force Plots/Stop Capstone CMD names continue to open/stop
Motion Lab at 4186. Do not also start Motion Lab's optional port-4175 service
while the atlas owns 4175. Startup checks reject port conflicts and keep errors
readable in the launcher and `.preview/` logs. No boot/login task is installed.

## Restore optional history and browser data

From the archive app, these standard-library commands require unused output
directories and never execute archived source:

```sh
python restore_archive.py --output restored/legacy-workspace
python restore_development_history.py --output restored/development-history
```

The restored legacy directory has the original source/data/output layout. The
supplement retains repository-relative filenames. Prefer maintained app modules;
historical migration/patch scripts are evidence and can change obsolete code.

To carry custom browser data, on the PC select wanted records in Motion Lab's
Profiles & data and use **Download JSON**. On the laptop use **Import JSON**.
Sizing configurations use **Save configuration JSON** / **Load configuration**
inside the sizing calculator. Atlas vehicle profiles also have JSON export/import.
Transfer personal files separately; do not publish private content merely to
move it. A fresh laptop works with source defaults without any PC browser export.

## Current development constraints

The latest sizing case is confirmed 200 mm radius / 400 mm diameter / 200 mm
usable lift. Buffers/custom ROM convert mm/degrees at a reference link. Average
and peak torque and CV/flatness are separate objectives; net load and chassis
depth/gap defaults are experiments, not hardware selections. Read
[the sizing record](wheel-leg-lab/docs/link-sizing.md) before interpreting winners.
The current wheel disturbance is position; preserve the undamped replacement
architecture. The user marked the dual-rope invertible knee design IMPOSSIBLE;
preserve its historical status/source and the subsequent rollback. Bellcrank
and other presets remain separate. No approved canonical robot/hardware result
is implied by app reconstruction.

## Laptop Codex prompt

```text
Set up and continue my Capstone development entirely on this laptop.
Clone the full history of https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE.git
into a new local Capstone folder, or inspect my existing checkout and update
main with a fast-forward while preserving any local changes. Use this laptop's
filesystem and installed runtimes; the desktop PC does not need to be running.

Read root AGENTS.md, every tracked database/ and agent_skills/ file, CONTRIBUTING.md
and the latest ENTRY_TEMPLATE.md entry. Then read
users/andy-zhang/experimental-apps/context.md and laptop-handoff.md, followed by
each relevant app's context.md, README.md, AGENTS.md and context/README.md.
Preserve existing app/model decisions and historical records.

Detect the laptop OS and available Git, Python and Node runtimes. Set up each
app's own dependencies from its requirements/lockfile and rebuild generated
assets locally. On Windows use Python 3.13, Node.js 22, Setup Motion Lab.cmd /
Start Motion Lab.cmd for wheel-leg-lab, and npm ci / npm run build /
Start Terrain Atlas.cmd for terrain-mobility-atlas. Verify the actual local
Motion Lab at 127.0.0.1:4186 and Atlas/workbench at 127.0.0.1:4175, including
manual restart. Keep launchers in their project roots and preserve those URLs.
Adapt and verify the equivalent setup/launcher on a different OS. Do not copy
the PC's virtual environment or depend on its paths, browser or server.

Continue from the wheel/link sweep: confirmed 200 mm radius, 400 mm diameter,
200 mm lift; editable degree/mm buffers and ROM, peak/mean/flatness comparisons.
Keep the dual-rope invertible design's IMPOSSIBLE status and preserve the
undamped replacement suspension and position-input model. Read current model
and validation docs before changing mechanics. Import any JSON I supply through
the matching calculator or data-library controls; default startup needs no PC data.

Install the repository hooks. If python3 is unavailable, use their supported
CAMEL_PYTHON override with this laptop's installed Python; keep checks enabled.
Before publication append the contribution entry, run the repository's scoped
checks, commit exact paths and push validated team work to main. Keep current
development context with the app, link shared records, and preserve other work.
After setup, report the local folder, runtimes, actual tests and preview URLs,
summarize the current development state, and be ready for my next change.
```

## Actual audit evidence

### Actual laptop setup, 2026-10-12

The owner's laptop is Windows 11 Home x64 (10.0.26200). An empty Capstone
directory received a normal full-history clone at `c6a79b5`: 41 commits,
`main` tracking `origin/main`, non-shallow history and clean `git fsck --full`.
The existing Python 3.11 and Node 24 were preserved. Python 3.13.12 was installed
per user from the signed Python Software Foundation Windows installer; Node
22.23.3 / npm 10.9.9 was installed per user from the official Windows ZIP after
checking its SHA-256 against Node's release manifest. User PATH persists these
runtimes, and a fresh Windows CMD resolves Python 3.13.12 and Node 22.23.3.
PowerShell can resolve an existing Cygwin extensionless `python` first; use
`python.exe`, `py -3.13`, or the app's `.venv/Scripts/python.exe` there.
The existing supported `CAMEL_PYTHON` user environment override selects installed
Python 3.13 for repository hooks; `core.hooksPath` is `.githooks`.
This clone uses `core.autocrlf=false` and tracked text is restored to its Git
index LF format. Windows CRLF conversion otherwise makes the raw-byte workspace
validator classify untouched shared files as changes. No enforcement change is
needed; retain the existing contents and line-ending format on future clones.

**Setup Motion Lab.cmd** recreated its venv, installed the pinned requirements,
ran `npm ci` and rebuilt Vite plus all seven studies locally. `pip check` reports
no broken requirements; all 70 JavaScript tests pass.
The full Python unittest discovery also passes all 139 tests, including the
108-backend-case six-second passive envelope and independent refinement checks.
Sizing, original force
calculator, portable studies and unified Motion Lab browser suites pass on the
actual 4186 server. They cover conversions/ROM/objectives, JSON/CSV, memory,
offline assets, mobile layout and independent SciPy/Pymunk API runs. The native
debugger's `--headless-check` steps Pymunk and renders three shapes/six constraints.
Actual visible native windows, MATLAB, GPU and canonical robot physics are not
certified by this setup.

Atlas's lockfile-based `npm ci`, production build and all 49 JavaScript tests
pass. Its browser verification passes atlas controls, a measured-USGS workbench
worker run, finite plots, mobile workbench and historical linkage route. A fresh
desktop capture also shows the local geographic map and synthetic cells with no
page errors. Both dependency installs report zero npm audit vulnerabilities.

Actual project-local **Start/Stop Motion Lab.cmd** and **Start/Stop Terrain
Atlas.cmd** pass fresh start, scoped stop (listener disappears), restart and
matching-server reuse from outside the app directories. Both are left running
on this laptop at 127.0.0.1:4186 and 127.0.0.1:4175; the workbench and linkage
routes return the rebuilt production entries. Ignored logs/builds/environments
and QA exports stay local. No desktop service, copied venv, boot task or browser
data transfer was used. The first unified browser check overlapped a server
restart and timed out; its subsequent stable-server rerun passes unchanged.

Current continuation remains the 200 mm radius / 400 mm diameter / 200 mm lift
sizing tool with configurable degree/mm buffers and ROM. Preserve separate
peak/mean/flatness objectives, the undamped replacement suspension, position
input, the rollback and the dual-rope design's **IMPOSSIBLE / rejected** status.
This contribution corrects stale current launcher/damping prose only; no model,
default, manifest or lockfile changes are made. Publication checks and the
complete Python test result are recorded in the contribution log and app validation.

A new GitHub clone at base 2353a6f (no copied app dependencies) passes both
`npm ci` / build workflows and 70 Motion Lab plus 49 Atlas JavaScript tests.
Motion Lab's new venv installs all pinned packages, passes `pip check`, and
imports server/physical/mathematical/inversion modules. Original 668-file archive
and the 21-file supplement restore exactly. Native desktop, GPU, MATLAB,
canonical physics and actual laptop/other-OS operation are not rerun/certified
by this source-transfer audit. The fresh-clone Motion Lab start/restart was also
verified on its supported alternate port 4175, while the main PC instance at
4186 remained running. That temporary verification process was stopped.
The actual project-local standalone Atlas CMD start/scoped-stop/restart/reuse
passes from an unrelated working directory on its original port 4175 after
updating Node discovery and standalone CMD names. The maintained Atlas is again
running there; both launchers retain readable readiness/failure/stop instructions.
