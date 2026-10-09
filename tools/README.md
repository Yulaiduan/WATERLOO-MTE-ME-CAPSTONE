# Repository validation tools

Workspace structure/log checks use Python's standard library. Shared physics and
gate-regression checks use Python 3.11 and the [simulation environment](../simulation/README.md).

| Command | Purpose |
| --- | --- |
| `python tools/check_entry.py --base origin/main` | Check working-tree structure and log coverage |
| `python tools/check_entry.py --staged --base origin/main` | Check exactly what a commit will contain |
| `python tools/check_entry.py --base origin/main --require-passed` | Require the validation declarations applicable to the complete diff |
| `python -m unittest discover -s tools/tests -v` | Gate regression tests; temporary synthetic models only |
| `python tools/physics_gate.py --base origin/main` | Select workspace, preliminary or shared robot validation |

`pre_push.py` is invoked by the Git hook and reads ref updates from Git. It
validates committed tips in temporary clones, then removes those clones. Install
hooks with `git config --local core.hooksPath .githooks`. Activate the virtual
environment before committing/pushing, or set `CAMEL_PYTHON` to its interpreter.

The validators accept `main` and optional member/contributor topic branches.
For direct `main` pushes, the hook compares against Git's advertised remote tip,
not just the fetched tracking ref. CI runs on shared engineering/enforcement pushes, including `main`;
main's jobs use `github.event.before` to validate the entire pushed diff rather
than comparing the new tip to itself. GitHub does not require a PR or passing
statuses before a direct push; local checks remain part of the contribution procedure.

These tools need a local Git checkout and a fetched `origin/main`. Hook paths are
relative so linked worktrees can each use their version. No hook bypass should be
used to publish work that fails validation. The push hook requires the applicable
scoped gate. [Preliminary research and contribution-policy changes](../agent_skills/preliminary_research.md)
run gate regressions and report canonical physics as not applicable. Changes
confined to member apps and Markdown context/scaffolds use `workspace` scope,
checking the structure and log without running regressions or importing apps.
App source/configs/dependencies/launchers and experimental models may stay with
their member app. Shared runtime, assets, dependencies, unknown paths and mixed engineering changes still require both robot
physics commands. Classifying a path as research never certifies its scientific results.
GitHub CI ignores collaboration-only updates under `users/`, `context/`, `docs/`
and `database/`, plus the root README, CONTRIBUTING.md and contribution log. A mixed
push touching shared engineering or enforcement still runs the applicable checks.

External forks use `--base upstream/main` and `CAMEL_BASE_REF=upstream/main`
after fetching this repository as their upstream. The initial protocol-only
installation is explicitly identified and cannot install robot assets or
controllers; it does not claim a physical validation pass. Once the target branch
has `ENTRY_TEMPLATE.md`, the exception no longer applies.
