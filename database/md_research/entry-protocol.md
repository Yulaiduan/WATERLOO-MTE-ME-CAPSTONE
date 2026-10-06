# Entry architecture protocol

Status: shared GitHub protocol; canonical physics baseline pending.
Live enforcement: [repository rules](https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE/rules).
Updated: 2026-10-06. Owner request: enforce an orderly contribution format and
reduce the effort needed for independent agents to understand one another.

## Gates

1. `AGENTS.md` establishes shared entry instructions for every agent. `CLAUDE.md`
   is a compatibility pointer for tools that discover that filename.
2. `tools/check_entry.py` checks approved paths, required files, script docstrings,
   blocked artifacts, file size and the append-only contribution log against the
   merge base. It checks the working tree locally and the checked-out commit in CI.
3. `.githooks/pre-commit` checks the staged snapshot. `.githooks/pre-push` checks
   each exact commit being pushed in a temporary checkout, including physics.
   Each clone must install the hooks; local hooks can be bypassed.
4. `.github/workflows/simulation-ci.yml` runs architecture and the scoped validation
   gate on pushes and PRs. The job names remain unchanged. Preliminary research
   runs gate regressions; executable robot changes require canonical physics.
5. Required GitHub checks protect `main`; routine PRs require zero approvals.
   CODEOWNERS requests human review only on critical paths as a team procedure.
   CI runs after a push, so it prevents merging failed contributions only when
   those repository rules are active. It cannot prevent every bad branch push.

## GitHub rollout

The owner requested publication and shared enforcement on 2026-10-01. The
initial documented plan included one approval and code-owner review. On
2026-10-06, live ruleset 24282754 was verified to already require zero approvals,
no code-owner approval and no last-push approval; PR #4 was mergeable despite
automatic requests to Andy/Jiaan. The owner asked to remove unnecessary waiting.
The current routine policy matches those live settings:

- Require PRs and resolved conversations; teammate approval is optional for routine work.
- Dismiss stale reviews after changes; no last-push approval is required.
- Require `Entry architecture` and `Headless physics`, with the branch up to date.
- Block branch deletion and force pushes; do not grant routine bypasses.
- Keep human review for canonical assets, shared interfaces, checks and agent rules;
  enforcement changes need owner review. This is a team procedure, not path-specific
  GitHub enforcement. CODEOWNERS requests reviewers only on these critical paths.

An agent may merge a routine PR when the user authorizes merging and all checks
pass. A request only to push/open a PR does not authorize merging. This review
policy does not relax physics publication requirements or add bypass actors.

The first protocol-only installation is explicitly exempt from robot validation:
the target branch must not yet contain the contribution log, the canonical asset
manifest must be empty, and no robot assets/controllers/environments may be added.
This exception closes after installation. Under the owner's 2026-10-03 policy
update, subsequent changes use the complete-diff scope described below. An
unchanged member-branch creation needs no new run.

## Preliminary research before a canonical robot

The owner explicitly requested a lasting path for preliminary research because
an approved robot model may remain unavailable for an extended period.
[The research procedure](../../agent_skills/preliminary_research.md) permits
documentation, compact evidence, isolated analytical prototypes and reviewed
contribution-policy changes without a canonical robot. Sources, assumptions and
actual calculation checks remain required; the log marks physics not applicable.

`validation_scope` in `tools/check_entry.py` uses every changed/deleted path, not
the author's label. Its narrow allowlist excludes assets, runtime/configuration,
dependencies, firmware, training, deployment and shared interfaces. Unknown or
mixed changes require full physics. `tools/physics_gate.py` runs gate regressions
for preliminary contributions; robot changes retain both actual physics checks.
The same classifier is used for staged/working-tree checks, exact pushed commits
and CI. Required job names and branch protection are unchanged; routine review
is optional under the owner's 2026-10-06 policy above.

Fork owners control their own settings. PRs from forks must still pass these
repository checks and applicable critical-path human review before entering `main`. First-time fork workflow
runs may need maintainer approval; that is separate from approval to merge.
Owner review remains a team requirement for enforcement changes, including
workflow and validator edits. No routine ruleset bypass actors are configured.

Sources: [GitHub code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners),
[protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

## Canonical physics contract

`assets/manifest.json` lists every approved executable MJCF model, its relative
path, hashes of all files it depends on, body masses in kg, and each scalar joint's
type, limit flag and range (m or rad). A compiled model must match that baseline.
Robot URDFs require a reviewed MJCF conversion with provenance; never silently
skip an unsupported model. No canonical robot exists in this branch yet, so
physics validation deliberately fails. Test fixtures exist only in temporary
test directories and cannot satisfy this gate.

The backend suite runs two fresh, identical zero-control rollouts of each model
and compares the full integration state at every step, checks finite values and
MuJoCo warnings, and reports timings. This validates a basic CPU repeatability
case, not task behavior, all controllers, GPU acceleration or hardware fidelity.
Add controller/contact scenarios and backend-specific tolerances before claiming
coverage of them. Exact equality is required only between these two runs in the
same environment; it is not a cross-platform floating-point guarantee.

## Migration and edge cases

- Existing `docs/`, `firmware/`, `training/`, `deploy/` and `shared/` stay in place.
  New agent summaries live in `database/`; reference old documents without copying.
- Terrain presets move conceptually to `simulation/config/presets/`. The existing
  Notion source summary remains authoritative for source values. Missing physical
  parameters remain unresolved; no arbitrary presets are generated.
- Existing uncommitted local simulations are not imported by this protocol.
- Deleted files and both sides of a rename belong in the contribution entry.
- Empty commits need no new entry. New branches compare against `origin/main`;
  an unavailable base or detached HEAD blocks local contribution validation.
- Every changed tracked blob is capped at 1 MiB. Store larger approved assets
  through an agreed external artifact workflow with stable checksums.
- Personal branches end in `/work`, and topic branches use sibling final names.
  A bare member ref would prevent Git from creating branches beneath that prefix.
- Ignore rules do not remove files already tracked. The gate checks tracked and
  nonignored new files too. It is not a comprehensive secret scanner or a proof
  of engineering quality; human review remains necessary.
- Append-only logs can conflict across branches. Keep both new entries and rerun
  against the fetched base. Log rotation requires a reviewed protocol change.
- Reading every database/skill file each loop is the explicit owner policy. Keep
  those files short; a later index-only policy would need an agreed rule change.

## Open inputs

Approved canonical robot and mass/joint specification; two missing collaborator
accounts; confirmed subsystem ownership; GPU backend selection and benchmarks.
