# Repository validation tools

Use Python 3.11 and the [simulation environment](../simulation/README.md).

| Command | Purpose |
| --- | --- |
| `python tools/check_entry.py --base origin/main` | Check working-tree structure and log coverage |
| `python tools/check_entry.py --staged --base origin/main` | Check exactly what a commit will contain |
| `python tools/check_entry.py --base origin/main --require-passed` | Also require checked physics declarations |
| `python -m unittest discover -s tools/tests -v` | Gate regression tests; temporary synthetic models only |
| `python tools/physics_gate.py --base origin/main` | Required CI/push physics gate, including one-time protocol installation |

`pre_push.py` is invoked by the Git hook and reads ref updates from Git. It
validates committed tips in temporary clones, then removes those clones. Install
hooks with `git config --local core.hooksPath .githooks`. Activate the virtual
environment before committing/pushing, or set `CAMEL_PYTHON` to its interpreter.

These tools need a local Git checkout and a fetched `origin/main`. Hook paths are
relative so linked worktrees can each use their version. No hook bypass should be
used to publish work that fails validation. Structural checks can pass while
physics remains blocked; the push hook requires both.

External forks use `--base upstream/main` and `CAMEL_BASE_REF=upstream/main`
after fetching this repository as their upstream. The initial protocol-only
installation is explicitly identified and cannot install robot assets or
controllers; it does not claim a physical validation pass. Once the target branch
has `ENTRY_TEMPLATE.md`, the exception no longer applies.
