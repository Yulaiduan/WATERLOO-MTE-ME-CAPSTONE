# Entry architecture protocol

Status: shared GitHub protocol; canonical physics baseline pending.
Live enforcement: [repository rules](https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE/rules).
Updated: 2026-10-08. Owner request: enforce an orderly contribution format and
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
   gate on engineering/enforcement pushes and PRs. Collaboration-only updates
   under users/context/docs/database and the root README/contribution documents
   do not trigger it. The job names remain unchanged. Preliminary policy work
   runs gate regressions; executable robot changes require canonical physics.
5. Teammates push directly to `main` after local validation. GitHub blocks force
   pushes and deletion of `main`; PRs and passing statuses are not required before
   publication. CI checks the complete push against its previous remote tip and
   reports failures after publication. Local hooks supply pre-push validation;
   CODEOWNERS requests critical-path review only when an optional PR is used.

## GitHub rollout

The owner requested publication and shared enforcement on 2026-10-01. The
initial documented plan included one approval and code-owner review. On
2026-10-06, live ruleset 24282754 was verified to already require zero approvals,
no code-owner approval and no last-push approval; PR #4 was mergeable despite
automatic requests to Andy/Jiaan. The owner asked to remove unnecessary waiting.
That policy retained required PRs and the two required status checks.

On 2026-10-08, the owner requested the team's agreed direct-to-main workflow,
using the supplied team discussion as context. PR #6 had already merged the
shared context and member app folders. The updated policy is:

- Normal team work uses `main`, with validated direct pushes and no required PR.
- Keep member folders for experiments and shared handoffs; existing engineering
  components and accepted records stay in place. Personal branches/PRs are optional.
- Ruleset 24282754 keeps `deletion` and `non_fast_forward` protection on `main`,
  and removes `pull_request` and `required_status_checks`. No bypass actors are added.
- Keep `Entry architecture` and `Headless physics` CI; run them on engineering/enforcement pushes
  against `github.event.before`, covering multi-commit updates. CI reports failures
  after publication rather than preventing the direct push. Local checks still apply.
  The follow-up member-workspace policy below narrows the CI triggers.
- Keep human review for canonical assets, shared interfaces, checks and agent rules.
  Enforcement changes need owner authorization/review; an explicit owner request
  can authorize the policy change without a separate author or PR.

An agent needs user authorization to merge an optional PR. This policy does not
relax physics publication requirements or grant new collaborator access.

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
the author's label. Its narrow allowlist excludes canonical assets, shared runtime/configuration,
dependencies, firmware, training, deployment and shared interfaces. Unknown or
mixed changes require full physics. `tools/physics_gate.py` runs gate regressions
for preliminary contributions; robot changes retain both actual physics checks.
The same classifier is used for staged/working-tree checks, exact pushed commits
and CI. Job names and shared robot physics requirements are unchanged; the owner's
2026-10-08 direct-push policy above replaces the former PR/status-check barrier.

Fork owners control their own settings. PRs from forks must still pass these
repository checks and applicable critical-path human review before entering `main`. First-time fork workflow
runs may need maintainer approval; that is separate from approval to merge.
Owner authorization/review remains a team requirement for enforcement changes,
including workflow and validator edits. No ruleset bypass actors are configured.

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
- Optional personal branches end in `/work`, and topic branches use sibling final names.
  A bare member ref would prevent Git from creating branches beneath that prefix.
- Ignore rules do not remove files already tracked. The gate checks tracked and
  nonignored new files too. It is not a comprehensive secret scanner or a proof
  of engineering quality; human review remains necessary.
- Append-only logs can conflict across branches. Keep both new entries and rerun
  against the fetched base. Log rotation requires a reviewed protocol change.
- Reading every database/skill file each loop is the explicit owner policy. Keep
  those files short; a later index-only policy would need an agreed rule change.

## Shared chat context and member apps (2026-10-08)

The requested layout adds `context/` for shared orientation and member-selected
ChatGPT/Codex summaries, and `users/<member>/experimental-apps/` for developing
tools with their own model/setup/handoff context. Existing database research and
canonical components stay in place. Root AGENTS.md routes agents to relevant
member/app context; it does not require reading every chat history.

The original scaffold's structural validator accepted these two roots and required
their entry documents. Initially only `.md` paths there joined preliminary scope. Executable apps,
configs, dependencies and launchers retain physics classification, including
mixed/deletion changes; no app-only gate is introduced. CODEOWNERS routes nested
AGENTS.md and the ChatGPT instruction template to the owner. At introduction,
CI jobs, robot baseline checks, GitHub protection and review rules were unchanged;
the later direct-push rollout above supersedes the branch/PR requirement.

This is manual sharing of versioned files, not live chat/account-memory sync.
See [the workflow](../../context/README.md) and [app scaffolds](../../users/README.md).
Owner authorization/review applies to validator and instruction changes before publication.

## Unified member experiments without CI (2026-10-08)

The owner's follow-up team discussion clarifies the purpose: all members' tools
and exploratory work are available together on `main`, organized by folder, so
teammates do not switch branches to use each other's work. The former canonical
robot requirement for isolated member apps is superseded.

- `workspace` scope covers changes confined to member app source/configs/dependencies,
  launchers and experimental models, plus Markdown context/scaffolds and the log.
  Only basic structure/log checks apply; no app execution, regression suite or
  canonical robot is needed merely to share this work. Record tested/untested status.
- Experimental model files may stay inside an app belonging to a registered
  member. They cannot supply the canonical robot baseline or be imported by
  production components. Existing artifact/credential/size checks still apply.
- CI ignores pushes/PRs confined to users/context/docs/database, README.md,
  CONTRIBUTING.md and ENTRY_TEMPLATE.md. Shared engineering/enforcement and mixed
  updates still run CI. No GitHub ruleset changes are needed for this refinement.
- Any changed/deleted canonical component path still selects its physics gate,
  including moving shared code into a member app. Promoting an app into shared
  engineering components requires their validation and migration record.

## Open engineering inputs

Approved canonical robot and mass/joint specification; two missing collaborator
accounts; confirmed subsystem ownership; GPU backend selection and benchmarks.
