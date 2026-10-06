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

## Entry: 2026-10-03 — Yulai Duan — link length and upward travel chart

## 1. Scope & Objective

- **Target Subsystem:** Requirement parameter research and its retained figures.
- **Associated Issue/Task:** Owner requested a chart explaining the selected 234.4 mm minimum-link calculation and its relationship to the research data.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no deletions.
- `ENTRY_TEMPLATE.md`
- `database/code_prototypes/README.md`
- `database/code_prototypes/plot_link_travel.py`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/README.md`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/assets/link-length-travel.png`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/assets/link-length-travel.svg`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/assets/link-length-travel.json`
- **API/Interface Changes:** Adds an isolated plot reproducer with required `--output DIR`, writing PNG, SVG and provenance JSON. Matplotlib 3.10.7 is documented for the plotting environment only; no production dependency, robot model or simulation interface changes.

## 3. Local Validation Checklist

- **Validation Scope:** preliminary
- **Research/Policy Validation:** The plot reproducer runs with Python 3.11.16, NumPy 2.4.6 and Matplotlib 3.10.7; all nine retained geometry points agree within 1.43e-14 mm, and assertions verify the 234.394 mm minimum and 184.305 mm seed travel. The rendered figure was visually inspected.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical physics is not applicable to this figure/prototype contribution.
The chart labels the 30 mm reserve and joint poses as assumptions and the points
as calculated evidence. It makes no experimental regression, step-climb or
global optimum claim. Figure provenance retains source/script hashes and units.

Working-tree entry validation passes for 58 files and 32 changed paths, with scope
preliminary; the scoped gate passes all 23 regressions. Relative links, source and
script hashes, SVG structure, artifact sizes and diff whitespace checks pass.

## 4. Compute Saving Handoff State

The research record now shows link length against upward wheel travel with the 150 mm requirement, assumed 180 mm travel target and proposed 235–250 mm study interval.
A second panel shows how the minimum link changes at 45°, 50° and 55° ride poses while keeping the retraction stop at 75°.
Use the retained vector figure or isolated plotting script for reports, and validate terrain contacts and drive capability before treating this clearance screen as step-climbing performance.

---

## Entry: 2026-10-03 — Yulai Duan — chassis COM spring and range relationships

## 1. Scope & Objective

- **Target Subsystem:** Requirement parameter research, analytical sensitivity plots and simulation input guidance.
- **Associated Issue/Task:** Owner requested charts relating chassis assembly, COM offsets, spring force and other inputs to the required outputs.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no deletions.
- `ENTRY_TEMPLATE.md`
- `database/code_prototypes/README.md`
- `database/code_prototypes/plot_parameter_relationships.py`
- `database/md_research/requirement-parameter-research.md`
- `docs/README.md`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/README.md`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/parameter-relationships.md`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/assets/mass-com-relationships.png`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/assets/mass-com-relationships.svg`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/assets/spring-relationships.png`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/assets/spring-relationships.svg`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/assets/range-drive-relationships.png`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/assets/range-drive-relationships.svg`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/assets/parameter-relationships.csv`
- `docs/benchmarks/2026-10-02-requirement-parameter-screen/assets/parameter-relationships.json`
- **API/Interface Changes:** Adds an isolated plot/calculation script requiring `--output DIR` and using the existing documented plotting environment; no production dependency or robot interface changes. Outputs three PNG/SVG figures, curve samples and provenance JSON.

## 3. Local Validation Checklist

- **Validation Scope:** preliminary
- **Research/Policy Validation:** Under Python 3.11.16, NumPy 2.4.6 and Matplotlib 3.10.7, the calculation reproduces five retained 90% spring fits, all eight slope torque rows and five energy rows to below 1e-10 in column units. A separate contact-force/moment solve verifies the four COM boundaries within 1.2e-16 normal-load fraction; preload minima and torque-sign constraints pass. All three figures were visually inspected; 12 panels / 5,826 retained curve samples, source/script hashes, links, table columns, SVG structure and artifact size limits pass.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical physics is not applicable to these documentation/prototype changes.
The records distinguish proposed values, analytical sensitivities and untested
performance. No measured correlation, spring-induced range gain, step completion
or global hardware optimum is claimed. Sources were rechecked against the two
primary spring papers; their gains are not transferred to CAMEL.

The entry check passes for 68 files / 42 changed paths with preliminary scope;
the scoped gate passes all 23 regressions, and diff whitespace checks pass.

## 4. Compute Saving Handoff State

The study now charts chassis mass/placement, COM height/offsets, spring forces, preload objectives, drum sizing, electrical range budgets and slope drive/traction requirements.
The fixed-rate loaded preload minimum is 320 N if signed residual torque is allowed, or 274 N if the motor must never oppose the spring, explaining the earlier 272 N seed.
Use the proposed sweeps with actual CAD/terrain-frame COM and component data, then validate dynamic contact and electrical energy before optimizing the full robot.

---

## Entry: 2026-10-06 — Yulai Duan workspace — streamline routine review policy

## 1. Scope & Objective

- **Target Subsystem:** Contribution policy and review routing.
- **Associated Issue/Task:** Owner asked whether the simulation-results PR waits on Andy/Jiaan and requested a less time-consuming rule.

## 2. Structural Modifications

- **Files Modified/Added:**
- `.github/CODEOWNERS`
- `.github/pull_request_template.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `ENTRY_TEMPLATE.md`
- `README.md`
- `agent_skills/git_hygiene.md`
- `agent_skills/preliminary_research.md`
- `database/md_research/entry-protocol.md`
- `database/md_research/team.md`

- **API/Interface Changes:** No runtime or validator API changes. Remove blanket peer-review routing for routine paths and the shared contribution log; retain critical-path routing. Align routine merge instructions with the live zero-approval GitHub rule, while preserving user authorization for agent merges and human review for assets/interfaces/checks/agent rules, including owner review for enforcement. No ruleset, bypass, status-check or physics-gate changes.

## 3. Local Validation Checklist

- **Validation Scope:** preliminary
- **Research/Policy Validation:** GitHub ruleset 24282754 reports zero required approving reviews, code-owner approval false and last-push approval false, with both required checks and strict up-to-date checks retained. PR #4 reports CLEAN and optional automatic requests to Code-Andy/Jiaan124, with no submitted reviews; legacy main branch protection is absent (404). Targeted ownership routing and document-link checks verify routine paths have no automatic owners and critical paths retain routing. Scoped gate regressions and contribution checks are required before push; no simulation or physics claim is made by this policy change.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical physics is NOT APPLICABLE to this contribution-policy diff. Missing
canonical models still block applicable executable contributions. The original
one-approval rollout plan is preserved as history, and the current live settings
are documented explicitly; critical-path review is a team procedure, not a
path-specific GitHub approval requirement. Owner review of this enforcement
change remains required before merge.

Entry validation passes for 68 files / 10 changed paths with preliminary scope;
the scoped gate passes all 23 regressions. Seven routine and ten critical
ownership fixtures plus policy links pass focused checks.

## 4. Compute Saving Handoff State

PR #4 is mergeable without Andy/Jiaan approval under the already-active zero-approval rule; its requests were notifications, not a merge blocker.
This policy PR removes automatic review requests for routine work and aligns contribution instructions with CI-only routine merging, while retaining critical-path human review and all validation gates.
Complete owner review before merging this enforcement change; routine agents still need user authorization to merge and must not infer it from a push-only request.

---
