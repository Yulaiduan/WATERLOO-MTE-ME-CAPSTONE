# Git hygiene

Use up-to-date `main` for normal team work and push validated changes directly.
Personal/topic branches from `database/md_research/team.md` are optional for
parallel or longer work. Inspect `git status` before switching or updating.
Stop if detached. Preserve all local changes.

Install hooks once per clone from its root:

```sh
git config --local core.hooksPath .githooks
```

For a clean `main`, fetch `origin` and fast-forward to `origin/main` before editing.
For an optional personal topic branch, integrate the fetched `origin/main`.
Rebase only unpublished commits. Merge the fetched base into a published personal
branch to avoid rewriting remote history. Never automatically stash, reset,
clean, force-push, or resolve conflicts by dropping the other side.

Before each commit append to `ENTRY_TEMPLATE.md`, stage exact intended paths,
and run `python tools/check_entry.py --staged --base origin/main`. The pre-commit
hook checks the staged snapshot, so unstaged fixes cannot hide staged failures.
Before pushing, fetch the base and run `python tools/physics_gate.py --base origin/main`.
It runs the checks for the complete diff's scope, as described in
[preliminary research](preliminary_research.md). The pre-push
hook validates every pushed commit tip in an isolated temporary checkout and
allows `main` and approved personal branches. Direct `main` updates compare against
Git's advertised remote tip, covering every outgoing commit rather than an empty
diff against an already updated `origin/main`. It blocks branch deletion, tags,
non-fast-forward updates and unsupported branch names.
It ignores unrelated unstaged edits and never changes the working tree.

For renames list both paths; for deletions list the deleted path. On a shared-log
conflict retain both appended entries and rerun checks. If the base has moved,
integrate it and check again. If `origin/main` is missing, fetch it before work;
do not silently compare against an empty tree. Empty commits need no new entry.

Push directly with `git push origin main` after checks pass. If remote `main`
has moved, fetch and integrate it, retain every independent log entry and rerun
checks before retrying. Never force-push to make a rejected update succeed.

Hooks are installed locally and can be bypassed. Member app/context-only pushes
use basic structure/log checks without executing apps, physics or gate regressions.
CI skips collaboration-only changes and runs for shared engineering/enforcement,
using the push event's previous tip as its base; it reports failures after
publication and cannot block a bad direct update. GitHub blocks force pushes and
deletion, without requiring PRs or passing statuses before publication. Routine
work needs no teammate approval. Optional PRs need user merge authorization and
passing checks. Canonical assets, shared interfaces, checks and agent rules retain
human review; enforcement changes need owner authorization/review, which an
explicit owner request can provide without a separate author or PR. CODEOWNERS
requests critical reviews on optional PRs. Report failures honestly and keep
blocked work local. A missing robot model does not block isolated member apps or eligible preliminary
contribution; its physics status is explicitly not applicable. Do not use
`--no-verify` to bypass this protocol.

For a fork, add this repository as `upstream`, fetch its `main`, and use
`contributors/<github-login>/<topic>` (or your assigned member branch). Set
`CAMEL_BASE_REF=upstream/main` for local hooks and pass `--base upstream/main` to
manual checks. Integrate upstream changes before submitting the PR. GitHub checks
compare against this repository's `main`, regardless of settings in your fork.
The initial protocol-only installation has a narrowly scoped bootstrap exception
in `tools/physics_gate.py`; it stops applying after the protocol reaches the base.
