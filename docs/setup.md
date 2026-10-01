# Setup and reproducibility

The repository is [Yulaiduan/WATERLOO-MTE-ME-CAPSTONE](https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE)
and is public. Ask the owner for collaborator access before pushing. Never place
access tokens, partner materials or machine-specific configuration in Git.

## New checkout

Clone into a new directory, not over an existing workspace:

```sh
git clone https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE.git
cd WATERLOO-MTE-ME-CAPSTONE
git status --short --branch
git remote -v
```

Every agent starts with [AGENTS.md](../AGENTS.md), then reads all tracked files
under [database](../database/README.md) and [agent_skills](../agent_skills/README.md).
If an agent tool does not discover this filename automatically, load it explicitly
in the session. All agent tools use the same protocol and validation commands.

## Personal branches and hooks

Use the branch assigned in [the team registry](../database/md_research/team.md).
Fetch `origin/main` before starting work. Create a missing personal branch from
that ref; use a topic suffix for simultaneous work. Do not switch over uncommitted
work or write to another member's branch.

```sh
git config --local core.hooksPath .githooks
```

This installs the tracked pre-commit and pre-push hooks for the clone. Activate
the Python environment before Git operations, or set `CAMEL_PYTHON` to its Python
executable. Read [Git hygiene](../agent_skills/git_hygiene.md) before rebasing or
resolving conflicts. Hooks can be bypassed, so GitHub required checks and review
apply to PRs into the shared branch, even when a contributor's local hooks are absent.

## Python validation

Follow [simulation setup](../simulation/README.md). The entry validator itself
uses only Python's standard library. Physics checks use pinned MuJoCo and NumPy.
An equivalent fresh environment installation and the regression suite were tested
on macOS on 2026-10-01. The actual physics gate is blocked because no canonical
robot/baseline has been supplied; that is an explicit failure, not a setup success.

Firmware compilers, training backends, GPU deployment and the robot runtime remain
unselected. Add verified build/run procedures to those components when selected.
The [rollout record](../database/md_research/entry-protocol.md) records the shared GitHub rules, remaining ownership assignments and missing
canonical model. Fork contributors use `contributors/<github-login>/<topic>`,
fetch this repository as `upstream`, and use `CAMEL_BASE_REF=upstream/main` for hooks.
