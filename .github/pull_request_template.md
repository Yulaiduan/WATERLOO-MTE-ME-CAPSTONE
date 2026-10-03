## What changed and why

Describe the problem and resulting behavior, or documentation/design question addressed.

## Contribution record

Link the appended entry in `ENTRY_TEMPLATE.md`. It must list exact paths,
interface changes, actual check results, and a three-sentence handoff. Follow
`AGENTS.md` regardless of which agent tool produced the contribution.

## Validation

List checks actually run and results. Check relative links for docs. Explain unavailable code, GPU or hardware checks.

- [ ] `python tools/check_entry.py --base origin/main --require-passed`
- [ ] `python tools/physics_gate.py --base origin/main`

State the detected scope. For preliminary research, record actual research checks
and canonical physics as **not applicable**. For physics/mixed changes, also run
and report `python simulation/run.py --headless-check` and
`python simulation/experiments/verify_backend.py`.

Failed applicable checks block publication and merge. A missing canonical model
blocks physics/mixed changes, while [preliminary research](../agent_skills/preliminary_research.md)
may proceed under its scoped checks. Do not claim an unavailable physics pass.
CPU repeatability does not validate a GPU.

## Shared impact

Identify affected interfaces, assets, dependencies, policy compatibility and consumer checks/migration. Write “None” when not applicable.

## Review

- [ ] Relevant documentation and index entries are current.
- [ ] Assumptions, proposals and measured evidence are distinguished.
- [ ] No secrets, unapproved partner material or raw generated artifacts included.
- [ ] Review requested from contributors responsible for affected areas.
