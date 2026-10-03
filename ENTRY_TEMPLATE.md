# Agent Contribution Log

Append a copy of the four sections below for every contribution before a commit
or PR. Begin each appended entry with `## Entry: YYYY-MM-DD — member — task`.
Keep this template and existing entries unchanged. Resolve concurrent append
conflicts by retaining both entries. The validator checks append-only history,
required fields and exact path coverage; reviewers verify truth and completeness.
Earlier failed attempts remain recorded honestly. Publication requires all three
checks in the latest appended entry to pass, plus a fresh run of the actual gates.

## 1. Scope & Objective

- **Target Subsystem:** [e.g., /simulation/src/controllers]
- **Associated Issue/Task:** [e.g., Issue #14 - PID Tuning]

## 2. Structural Modifications

- **Files Modified/Added:** [List exact paths; include deletions and both sides of renames]
- **API/Interface Changes:** [State explicitly if any function signatures or variables changed]

## 3. Local Validation Checklist

- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

## 4. Compute Saving Handoff State

*Provide a concise, 3-sentence summary of the new state here. This is what other
agents will read to save token spend when inheriting this environment context.*

---

<!-- CONTRIBUTIONS -->

## Entry: 2026-10-01 — Yulai Duan workspace — agent-neutral entry architecture

## 1. Scope & Objective

- **Target Subsystem:** Repository architecture, agent procedures and simulation validation.
- **Associated Issue/Task:** Implement the owner's Entry Architecture Protocol and make it independent of agent vendor or tool.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths listed below; no existing files deleted.
- `.githooks/pre-commit`
- `.githooks/pre-push`
- `.github/CODEOWNERS`
- `.github/pull_request_template.md`
- `.github/workflows/simulation-ci.yml`
- `.gitignore`
- `AGENTS.md`
- `CLAUDE.md`
- `CONTRIBUTING.md`
- `ENTRY_TEMPLATE.md`
- `README.md`
- `agent_skills/README.md`
- `agent_skills/git_hygiene.md`
- `agent_skills/notion_ingestion.md`
- `agent_skills/physics_validation.md`
- `assets/README.md`
- `assets/manifest.json`
- `database/README.md`
- `database/brainstorming_tex/README.md`
- `database/code_prototypes/README.md`
- `database/md_research/entry-protocol.md`
- `database/md_research/team.md`
- `docs/README.md`
- `docs/design/simulation/terrain-training-spec.md`
- `docs/setup.md`
- `simulation/README.md`
- `simulation/config/presets/README.md`
- `simulation/experiments/verify_backend.py`
- `simulation/requirements.txt`
- `simulation/run.py`
- `simulation/src/controllers/README.md`
- `simulation/src/environments/README.md`
- `simulation/src/viewers/README.md`
- `tools/README.md`
- `tools/check_entry.py`
- `tools/pre_push.py`
- `tools/tests/test_gates.py`
- **API/Interface Changes:** Added the shared AGENTS entry protocol, thin CLAUDE compatibility pointer, contribution validator, staged/push hooks, two required simulation commands, asset manifest schema 1 and CI jobs named Entry architecture and Headless physics; no existing simulator code was imported.

## 3. Local Validation Checklist

- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Validation evidence: fresh Python 3.11.16 environment installed with pinned MuJoCo
3.14.0 and NumPy 2.4.6 on macOS. All 14 regression tests pass, including temporary
fixture repeatability, mass/joint mismatch rejection, missing models, staged
snapshot isolation, branch naming and append-only log checks. Both real physics
commands exit 1 with “BLOCKED: no canonical robot”; no robot physics pass is claimed.
Working-tree and staged-snapshot architecture checks pass for 42 files and 37
changed paths; relative Markdown links, workflow YAML and hook shell syntax pass.
GitHub Actions has not run, and protection remains disabled. Hooks are provided for
installation per clone; shared worktree Git configuration was left unchanged.
Five personal branches exist locally and have not been pushed.

## 4. Compute Saving Handoff State

The repository now has a shared agent protocol, personal branch convention, structured handoff log, validation hooks and a headless CI definition.
Local regression tests pass, while actual robot validation is blocked by the missing canonical model and physical baseline.
Next supply the reviewed model and confirmed reviewer assignments, complete the physics checks, then publish the branch and activate GitHub protection after review.

---

## Entry: 2026-10-01 — Yulai Duan workspace — publish and enforce on GitHub

## 1. Scope & Objective

- **Target Subsystem:** Shared GitHub contribution enforcement for member branches and forks.
- **Associated Issue/Task:** Owner clarified that the protocol must be installed on GitHub and apply to every contributing agent.

## 2. Structural Modifications

- **Files Modified/Added:** `tools/physics_gate.py`, `tools/check_entry.py`, `tools/pre_push.py`, `tools/tests/test_gates.py`, `tools/README.md`, `.github/workflows/simulation-ci.yml`, `.github/CODEOWNERS`, `.githooks/pre-commit`, `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `docs/README.md`, `docs/setup.md`, `database/md_research/entry-protocol.md`, `database/md_research/team.md`, `agent_skills/git_hygiene.md`, `ENTRY_TEMPLATE.md`.
- **API/Interface Changes:** Added a one-time protocol-only installation gate that closes when the target branch contains the contribution log; external fork branch convention and configurable upstream base; owner review for enforcement changes. Repository settings require both CI jobs and code-owner approval on main, with no bypass actors.

## 3. Local Validation Checklist

- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

The robot baseline is absent, so these boxes remain unchecked. The owner-requested
initial protocol installation is eligible for the explicit bootstrap gate; it
adds no canonical robot or controller and makes no physics validation claim.
All 15 local regression tests pass, including proof that the bootstrap exception
cannot apply after the protocol is installed or when robot assets/controllers
are added. GitHub CI must pass before initial installation; shared protection is
then activated. Subsequent changed contributions require actual physics results.

## 4. Compute Saving Handoff State

The owner requested the protocol on GitHub so every member and fork contributor uses the same rules.
The installation adds required checks, code-owner review and personal branches without claiming a robot validation result.
Supply the canonical model and confirmed specialist assignments next, and preserve the enforced review process for all later changes.

---

## Entry: 2026-10-03 — Yulai Duan — requirement parameter research

## 1. Scope & Objective

- **Target Subsystem:** Research documentation and reproducible analytical experiments.
- **Associated Issue/Task:** Owner requested publication of the research on link length, wheel mass, COM, spring preload and requirement-oriented simulation inputs.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no deletions.
- `ENTRY_TEMPLATE.md`
- `database/README.md`
- `database/md_research/requirement-parameter-research.md`
- `docs/README.md`
- `docs/benchmarks/README.md`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/README.md`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/geometry.csv`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/spring_fits.csv`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/spring_curve.csv`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/slopes.csv`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/range_cases.csv`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/summary.json`
- `simulation/README.md`
- `simulation/experiments/requirement_parameter_screen.py`
- **API/Interface Changes:** Adds an independent NumPy analytical experiment invoked with `--output DIR`, writing five CSV files and a summary JSON. No production interfaces, canonical assets, controllers, dependencies or validation rules change.

## 3. Local Validation Checklist

- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

The analytical experiment runs successfully under Python 3.11.16 and NumPy 2.4.6.
Its potential-energy derivative check agrees within 1.402e-8 N m, and ideal
kinematic cancellation and knee/hip power mapping checks pass. The retained
numerical results reproduce the original study; the changed script docstring is
reflected in the updated SHA-256 in summary.json. Relative document links and
table column counts are checked separately from physics.

The entry architecture check passes for 53 files and 14 changed paths; numerical
result comparison, saved-script hash, relative links, table columns and diff
whitespace checks also pass.

Both required physics commands were run on 2026-10-03 and exit 1 with
`FAIL: BLOCKED: no canonical robot in assets/manifest.json. Supply a reviewed model and physical baseline.`
The repository manifest has no models. These are actual failures, not waived or
passed tests; earlier local educational-demo checks do not satisfy this gate.
Publication remains blocked under the current repository procedure pending a
reviewed canonical baseline or an explicit owner exception for this research contribution.

## 4. Compute Saving Handoff State

The research is packaged on a separate personal topic branch with public citations, explicit assumptions, a reproducible analytical experiment and compact results.
The independent research checks pass, but both repository physics commands fail because the canonical robot manifest is empty.
Preserve that failure record and obtain a reviewed robot baseline or an explicit research-publication exception before pushing; no merge or validation-rule change is authorized here.

---

## Entry: 2026-10-03 — Yulai Duan — preliminary research publication policy

## 1. Scope & Objective

- **Target Subsystem:** Contribution policy, validation gates and preliminary research.
- **Associated Issue/Task:** Owner explicitly requested a lasting rule change allowing preliminary research on GitHub before an approved robot model exists, and authorized write access.

This owner-authorized policy supersedes the original all-contributions physics
requirement in the historical template and entries above. Their recorded failures
remain unchanged. Physics validation is not applicable to an allowlisted research
or contribution-policy diff; it remains mandatory for runtime/assets/dependencies,
unknown paths and mixed changes.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below, including both sides of the prototype move.
- `.github/pull_request_template.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `ENTRY_TEMPLATE.md`
- `README.md`
- `agent_skills/README.md`
- `agent_skills/git_hygiene.md`
- `agent_skills/physics_validation.md`
- `agent_skills/preliminary_research.md`
- `database/code_prototypes/README.md`
- `database/code_prototypes/requirement_parameter_screen.py`
- `database/md_research/entry-protocol.md`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/README.md`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/summary.json`
- `simulation/README.md`
- `simulation/experiments/requirement_parameter_screen.py`
- `tools/README.md`
- `tools/check_entry.py`
- `tools/physics_gate.py`
- `tools/tests/test_gates.py`
- **API/Interface Changes:** Adds complete-diff validation scope selection and preliminary validation declarations; the existing entry/gate CLI and required CI job names stay compatible. Moves the standalone analytical prototype from simulation/experiments to database/code_prototypes without changing numerical behavior. No robot, controller, production dependency or canonical baseline changes.

## 3. Local Validation Checklist

- **Validation Scope:** preliminary
- **Research/Policy Validation:** All 23 gate regression tests pass under Python 3.11.16, NumPy 2.4.6 and MuJoCo 3.14.0; the research calculation reproduces its retained CSV results exactly and the moved script hash is updated.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

The three canonical-physics boxes are not applicable to this research/policy
contribution and do not claim successful robot validation. Both direct commands
were already run and failed honestly in the previous entry; the missing canonical
model is unchanged. New regressions cover research after bootstrap, policy-only
updates, mixed/runtime/dependency/asset/unknown changes, moves/deletions, mandatory
evidence, rejection of false physics-pass declarations and validation failures.
The scoped gate runs these regressions rather than manufacturing a robot result.

Working-tree entry validation passes for 54 files and 28 changed paths with
scope `preliminary`; the scoped gate passes all 23 tests and reports canonical
physics NOT APPLICABLE. Relative Markdown links, table columns, retained script
hash and diff whitespace checks pass.

## 4. Compute Saving Handoff State

Preliminary research and contribution-policy changes now have a scoped publication path with evidence declarations and gate regressions, while executable robot and mixed changes retain canonical physics requirements.
The parameter study is included with unchanged numerical results and its standalone script moved into the research prototype area.
Publish this reviewed change through the existing PR checks and code-owner process, then use the same research path for future preliminary contributions without claiming a validated robot.

---
