# Git hygiene

Use your branch from `database/md_research/team.md`; parallel tasks use
`members/<member>/<topic>` and separate worktrees. Inspect `git status` before
switching or updating. Stop if detached or on `main`. Preserve all local changes.

Install hooks once per clone from its root:

```sh
git config --local core.hooksPath .githooks
```

For a clean personal topic branch, fetch `origin`, then integrate `origin/main`.
Rebase only unpublished commits. Merge the fetched base into a published personal
branch to avoid rewriting remote history. Never automatically stash, reset,
clean, force-push, or resolve conflicts by dropping the other side.

Before each commit append to `ENTRY_TEMPLATE.md`, stage exact intended paths,
and run `python tools/check_entry.py --staged --base origin/main`. The pre-commit
hook checks the staged snapshot, so unstaged fixes cannot hide staged failures.
Before pushing, fetch the base and run the two physics commands. The pre-push
hook validates every pushed commit tip in an isolated temporary checkout and
blocks protected branch updates, deletion, tags and non-personal branch names.
It ignores unrelated unstaged edits and never changes the working tree.

For renames list both paths; for deletions list the deleted path. On a shared-log
conflict retain both appended entries and rerun checks. If the base has moved,
integrate it and check again. If `origin/main` is missing, fetch it before work;
do not silently compare against an empty tree. Empty commits need no new entry.

Hooks are installed locally and can be bypassed; required CI and code-owner
review on `main` provide the shared merge gate. Report failures honestly and keep
blocked work local. Do not use `--no-verify` to bypass this protocol.

For a fork, add this repository as `upstream`, fetch its `main`, and use
`contributors/<github-login>/<topic>` (or your assigned member branch). Set
`CAMEL_BASE_REF=upstream/main` for local hooks and pass `--base upstream/main` to
manual checks. Integrate upstream changes before submitting the PR. GitHub checks
compare against this repository's `main`, regardless of settings in your fork.
The initial protocol-only installation has a narrowly scoped bootstrap exception
in `tools/physics_gate.py`; it stops applying after the protocol reaches the base.
