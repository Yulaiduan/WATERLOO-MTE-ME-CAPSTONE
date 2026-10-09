# Repository validation tools

Use Python 3.11 and the [simulation environment](../simulation/README.md).

| Command | Purpose |
| --- | --- |
| `python tools/check_entry.py --base origin/main` | Check working-tree structure and log coverage |
| `python tools/check_entry.py --staged --base origin/main` | Check exactly what a commit will contain |
| `python tools/check_entry.py --base origin/main --require-passed` | Require the validation declarations applicable to the complete diff |
| `python -m unittest discover -s tools/tests -v` | Gate regression tests; temporary synthetic models only |
| `python tools/physics_gate.py --base origin/main` | Run preliminary gate regressions or required robot physics checks |

`pre_push.py` is invoked by the Git hook and reads ref updates from Git. It
validates committed tips in temporary clones, then removes those clones. Install
hooks with `git config --local core.hooksPath .githooks`. Activate the virtual
environment before committing/pushing, or set `CAMEL_PYTHON` to its interpreter.

These tools need a local Git checkout and a fetched `origin/main`. Hook paths are
relative so linked worktrees can each use their version. No hook bypass should be
used to publish work that fails validation. The push hook requires the applicable
scoped gate. [Preliminary research and contribution-policy changes](../agent_skills/preliminary_research.md)
run gate regressions and report canonical physics as not applicable. Only
Markdown under `context/` and `users/` is preliminary. Runtime, assets,
dependencies, unknown paths and mixed changes still require both robot
physics commands. Classifying a path as research never certifies its scientific results.
App code/configs/dependencies/launchers under `users/` retain those physics checks.

External forks use `--base upstream/main` and `CAMEL_BASE_REF=upstream/main`
after fetching this repository as their upstream. The initial protocol-only
installation is explicitly identified and cannot install robot assets or
controllers; it does not claim a physical validation pass. Once the target branch
has `ENTRY_TEMPLATE.md`, the exception no longer applies.
