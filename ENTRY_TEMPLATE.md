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

## Entry: 2026-10-08 — Andy Zhang — shared chat context and experimental app structure

## 1. Scope & Objective

- **Target Subsystem:** Shared context, member experimental workspaces and contribution structure.
- **Associated Issue/Task:** User requested a structure for sharing regular ChatGPT/Codex context across teammates and keeping developing apps/toolkits with each member.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no deletions or existing app imports.
- `.github/CODEOWNERS`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `ENTRY_TEMPLATE.md`
- `README.md`
- `agent_skills/preliminary_research.md`
- `context/README.md`
- `context/start-here.md`
- `context/templates/README.md`
- `context/templates/app-context.md`
- `context/templates/chat-handoff.md`
- `context/templates/chatgpt-project-instructions.md`
- `context/users/README.md`
- `context/users/ali-muizz/README.md`
- `context/users/andy-zhang/README.md`
- `context/users/jiaan-li/README.md`
- `context/users/jonathan-xie/README.md`
- `context/users/yulai-duan/README.md`
- `database/README.md`
- `database/md_research/entry-protocol.md`
- `docs/README.md`
- `tools/README.md`
- `tools/check_entry.py`
- `tools/tests/test_gates.py`
- `users/README.md`
- `users/_template/README.md`
- `users/_template/experimental-app/AGENTS.md`
- `users/_template/experimental-app/README.md`
- `users/_template/experimental-app/context/README.md`
- `users/ali-muizz/README.md`
- `users/ali-muizz/experimental-apps/README.md`
- `users/andy-zhang/README.md`
- `users/andy-zhang/experimental-apps/README.md`
- `users/jiaan-li/README.md`
- `users/jiaan-li/experimental-apps/README.md`
- `users/jonathan-xie/README.md`
- `users/jonathan-xie/experimental-apps/README.md`
- `users/yulai-duan/README.md`
- `users/yulai-duan/experimental-apps/README.md`
- **API/Interface Changes:** Add context/users member summaries and users/member/experimental-apps scaffolds, reusable chat/app templates and agent routing. The validator accepts context and users roots, requires their entry documents and classifies only Markdown there as preliminary; app code/configs/dependencies/launchers, mixed changes and runtime deletions retain physics validation. No robot, simulator, dependencies, shared engineering interfaces or GitHub protection changes. Nested AGENTS.md and the ChatGPT instruction template route to owner review.

## 3. Local Validation Checklist

- **Validation Scope:** preliminary
- **Research/Policy Validation:** All 27 gate regressions pass with no skips under Windows Python 3.13.12, MuJoCo 3.14.0 and NumPy 2.4.6; four added tests cover context/app Markdown, executable and mixed scope, runtime moves and artifact/model restrictions. All 225 relative Markdown file links resolve, and git diff --check passes. Entry/scoped/staged gates run before publication; GitHub CI additionally checks the pinned Python 3.11 environment. Official OpenAI Projects/AGENTS.md guidance checked on 2026-10-08; docs distinguish file sharing from live chat/account-memory sync.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical physics is NOT APPLICABLE to this documentation/scaffold and policy
contribution; no executable app or canonical model is imported. Synthetic gate
fixtures are not robot validation. The existing empty canonical baseline still
blocks applicable executable app contributions; an app-only gate would be a
separate owner-reviewed policy change. Owner review is required before merging
the validator and agent instruction changes; no bypass or review removal is made.

## 4. Compute Saving Handoff State

The repository has a shared context entry packet, public member handoff folders and five experimental app workspaces with app-local context templates.
The sharing workflow uses reviewed Markdown summaries, Git publication and selected ChatGPT uploads or Codex file reads, while canonical engineering records stay authoritative.
Review the protocol/validator changes with Yulai before merging, then have each member add selected context and import apps only through the applicable validation gates.

---

## Entry: 2026-10-08 — Andy Zhang — finalize member scaffold formatting

## 1. Scope & Objective

- **Target Subsystem:** Member context and experimental app documentation.
- **Associated Issue/Task:** Final staged whitespace review caught extra blank lines at EOF in generated member pages; remove them before publication.

## 2. Structural Modifications

- **Files Modified/Added:** `context/users/ali-muizz/README.md`, `users/ali-muizz/README.md`, `users/ali-muizz/experimental-apps/README.md`, `context/users/andy-zhang/README.md`, `users/andy-zhang/README.md`, `users/andy-zhang/experimental-apps/README.md`, `context/users/jonathan-xie/README.md`, `users/jonathan-xie/README.md`, `users/jonathan-xie/experimental-apps/README.md`, `context/users/yulai-duan/README.md`, `users/yulai-duan/README.md`, `users/yulai-duan/experimental-apps/README.md`, `context/users/jiaan-li/README.md`, `users/jiaan-li/README.md`, `users/jiaan-li/experimental-apps/README.md`, `ENTRY_TEMPLATE.md`
- **API/Interface Changes:** None; trim trailing blank lines only. Preserve prior entries and record the final staged whitespace finding.

## 3. Local Validation Checklist

- **Validation Scope:** preliminary
- **Research/Policy Validation:** The preceding 27-test gate run and 225-link check remain applicable; final diff/entry/scoped checks run before publication. Initial tracked-file whitespace checking passed, but the subsequent staged check included new files and reported trailing empty lines in these 15 member pages; those lines are removed by this follow-up.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical physics remains NOT APPLICABLE to the documentation/policy contribution.
Owner review of the full PR remains required before merge.

## 4. Compute Saving Handoff State

All generated member pages now end with one newline rather than an extra empty line.
The new shared context and app structure is otherwise unchanged and retains the existing executable physics gate.
Publish the verified branch and complete Yulai's owner review before merging into main.

---

## Entry: 2026-10-08 — Andy Zhang — README chat-context quickstart

## 1. Scope & Objective

- **Target Subsystem:** Root README contributor quickstart.
- **Associated Issue/Task:** User requested the regular ChatGPT export/Codex import guidance near the top of the repository README.

## 2. Structural Modifications

- **Files Modified/Added:** `README.md`, `ENTRY_TEMPLATE.md`.
- **API/Interface Changes:** None. Add the reviewed handoff workflow, two copyable prompts, folder destinations and conditional GitHub web-chat publishing guidance before repository architecture.

## 3. Local Validation Checklist

- **Validation Scope:** preliminary
- **Research/Policy Validation:** All 25 relative README file links resolve, Markdown code fences are balanced, the quickstart precedes repository architecture, and git diff --check passes. The complete entry/scoped/staged checks and exact-push gate run before publication. Product guidance uses the official OpenAI plugin/project documentation reviewed in this conversation on 2026-10-08.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical physics is NOT APPLICABLE to this README-only addition and the full
preliminary-scoped PR. No runtime, model or dependency changes are introduced.

## 4. Compute Saving Handoff State

The README now provides a chat-context quickstart immediately after the project introduction.
Members can copy a ChatGPT export prompt and a Codex import prompt, with explicit destinations and the limits of naming a repo in a web chat.
Use these prompts to publish reviewed handoffs through member branches and PRs; the existing PR still requires owner review of its earlier enforcement changes.

---

## Entry: 2026-10-08 — Yulai Duan with Codex — direct-to-main team workflow

## 1. Scope & Objective

- **Target Subsystem:** Contribution workflow, shared context and member workspace guidance.
- **Associated Issue/Task:** Owner requested the direct-to-main workflow agreed in the supplied team discussion: shared context and member experiments, without mandatory branches or PRs. PR #6 is already merged and supplies the folders.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no deletions or app imports.
- `.github/CODEOWNERS`
- `.github/workflows/simulation-ci.yml`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `ENTRY_TEMPLATE.md`
- `README.md`
- `agent_skills/git_hygiene.md`
- `agent_skills/preliminary_research.md`
- `context/README.md`
- `context/start-here.md`
- `context/users/README.md`
- `context/users/ali-muizz/README.md`
- `context/users/andy-zhang/README.md`
- `context/users/jiaan-li/README.md`
- `context/users/jonathan-xie/README.md`
- `context/users/yulai-duan/README.md`
- `database/README.md`
- `database/md_research/entry-protocol.md`
- `database/md_research/team.md`
- `docs/README.md`
- `docs/setup.md`
- `shared/README.md`
- `tools/README.md`
- `tools/check_entry.py`
- `tools/pre_push.py`
- `tools/tests/test_gates.py`
- `users/README.md`
- `users/ali-muizz/README.md`
- `users/andy-zhang/README.md`
- `users/jiaan-li/README.md`
- `users/jonathan-xie/README.md`
- `users/yulai-duan/README.md`
- **API/Interface Changes:** Validators accept main alongside optional personal branches. Direct-main pre-push validation uses Git's advertised remote tip, and main CI uses the push event's previous tip so the complete outgoing change is checked. Align README prompts, onboarding and member indexes with direct pushes. Ruleset 24282754 is updated as part of publication to retain deletion/non-fast-forward protection and remove mandatory PR/status-check rules. CI now reports after publication; local validation and critical-path human review remain team procedures. This explicit owner request authorizes the enforcement change. Robot models, dependencies, runtime interfaces and physics classification are unchanged.

## 3. Local Validation Checklist

- **Validation Scope:** preliminary
- **Research/Policy Validation:** All 31 gate regressions pass without skips using Python 3.11.16, MuJoCo 3.14.0 and NumPy 2.4.6, including direct-main remote-tip selection, optional branch compatibility and rejected main creation/deletion/non-fast-forward updates. All 231 relative Markdown links resolve and code fences are balanced; git diff --check passes. Working/staged architecture checks and the exact-push scoped gate are required before publication. GitHub CI and live rules are verified after publishing.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this contribution-policy change.
The regression suite uses temporary fixtures and does not certify a CAMEL robot.
The existing local Capstone working tree is separate and is not imported.

## 4. Compute Saving Handoff State

Normal team work now uses main and validated direct pushes, with optional branches and PRs when useful.
The existing users and context folders organize personal experiments and shared findings while the same local checks and physics classification remain applicable.
Pull the published main, install the tracked hooks per clone, and inspect post-push CI because it cannot block a bad direct update before publication.

---

## Entry: 2026-10-08 — Yulai Duan with Codex — unified member experiments without CI

## 1. Scope & Objective

- **Target Subsystem:** Member experiment publication, validation scope and CI triggers.
- **Associated Issue/Task:** Follow-up owner-supplied team discussion clarifies that members want their exploratory tools together on main in dedicated folders, without switching branches or requiring CI/canonical robot validation to store them. Shared engineering and enforcement retain their applicable checks.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no existing app or engineering-code imports.
- `.github/pull_request_template.md`
- `.github/workflows/simulation-ci.yml`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `ENTRY_TEMPLATE.md`
- `README.md`
- `agent_skills/git_hygiene.md`
- `agent_skills/physics_validation.md`
- `agent_skills/preliminary_research.md`
- `context/README.md`
- `database/md_research/entry-protocol.md`
- `database/md_research/team.md`
- `docs/README.md`
- `docs/setup.md`
- `tools/README.md`
- `tools/check_entry.py`
- `tools/physics_gate.py`
- `tools/tests/test_gates.py`
- `users/README.md`
- `users/_template/experimental-app/AGENTS.md`
- **API/Interface Changes:** Add workspace scope for isolated registered-member apps and Markdown context/scaffolds, including experimental models. The scoped gate checks declarations without executing apps, physics or regressions. Basic structure/log/artifact checks remain; unknown paths and changes/deletions involving shared runtime/assets retain physics scope. Both push and PR CI ignore collaboration-only paths plus the contribution log, while mixed engineering/enforcement updates still trigger CI. Align agent routing, quickstart, app templates and protocol history; all member folders remain on main. No GitHub protection, collaborator access, canonical models, runtime interfaces or dependency pin changes.

## 3. Local Validation Checklist

- **Validation Scope:** preliminary
- **Research/Policy Validation:** All 36 gate regressions pass without skips with Python 3.11.16, MuJoCo 3.14.0 and NumPy 2.4.6. Regression coverage includes no automatic workspace execution, experimental model placement, non-physics declarations, unknown locations and mixed/deleted shared engineering paths. Workflow YAML parses successfully and all 16 push/PR trigger cases pass: collaboration-only changes skip, shared/mixed changes run. All 231 relative Markdown links resolve, code fences are balanced, and git diff --check passes. Working/staged checks, a disposable source-sharing checkout and the exact committed snapshot are checked before publication; GitHub CI is inspected after the policy update.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this contribution-policy change.
The tests use temporary fixtures and do not certify a team robot or member app.
No existing local Capstone work is imported.

## 4. Compute Saving Handoff State

All member experiments and selected context stay together on main, organized by folder and accessible with one pull.
Workspace-only publication now uses basic structure/log checks without CI, automatic app execution or a canonical robot, with tested/untested status recorded honestly.
Shared engineering and enforcement still trigger CI, and moving an experiment into a canonical component requires its normal validation and migration record.

---

## Entry: 2026-10-09 — Andy Zhang with Codex — import both wheel-leg chats

## 1. Scope & Objective

- **Target Subsystem:** Andy Zhang's isolated Wheel Leg Lab and member engineering context.
- **Associated Issue/Task:** User explicitly requested publishing all current rough animations and wheel-to-link-ratio simulations from both chats under their experimental apps, with design decisions and documentation.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths follow; generated pages, environments, raw frame/GIF output, logs and full traces are excluded.
- `ENTRY_TEMPLATE.md`
- `README.md`
- `context/users/andy-zhang/2026-10-09-codex-wheel-leg-lab.md`
- `context/users/andy-zhang/README.md`
- `docs/README.md`
- `users/README.md`
- `users/andy-zhang/experimental-apps/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/.gitignore`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/AGENTS.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/GLOSSARY.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Open Pymunk GUI.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Setup Pymunk.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Start Geometry Preview.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Start Pymunk Linkage.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Start-Pymunk.ps1`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Stop Geometry Preview.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Stop Pymunk Linkage.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Stop-Pymunk.ps1`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/coaxial-wheel-leg.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/fixed-ratio-left-leg.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/left-tilted-leg.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/leg-path-family.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/linear-leg.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/pymunk-remote-preview.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/tilted-invertible-leg.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/two-position-left-leg.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_view.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/architecture.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/decisions.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/design.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/equation-cross-check.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/handoff.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/linkage-architecture.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/linkage-handoff.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/linkage-model.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/linkage-validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/model.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/equation_checks.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/licenses/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/licenses/d3-LICENSE.txt`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/licenses/ml-matrix-LICENSE.txt`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/licenses/playwright-LICENSE.txt`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/licenses/vite-LICENSE.txt`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/linkage/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/linkage/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/package-lock.json`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/package.json`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/references/equations-1.png`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/references/equations-2.png`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/references/equations-complete.png`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/requirements-analysis.txt`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/requirements.txt`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/build_animations.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/check_docs.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/search_fixed_pulley_geometry.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/validate_linkage_reference.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify-force-plots.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_pymunk.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_suite.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/server.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/src/linkage/charts.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/src/linkage/main.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/src/linkage/model.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/src/linkage/style.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/src/linkage/view.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/src/linkage/worker.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_equation_checks.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/fixtures/linkage/sympy-reference.json`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/linkage.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/vite.config.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/D3-LICENSE.txt`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/d3.min.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/force-plots/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/style.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/viewer-state.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/viewer.css`
- **API/Interface Changes:** Add the member-local toolkit only; canonical assets/shared runtime are unchanged. The unified loopback service preserves the 4186 Pymunk route and serves gallery, force plots, detailed linkage and recorded playback. A separately tracked 4175 launcher preserves original geometry routes. Source/build/tests and launchers use project-relative paths and pinned dependencies. Add curated context from both chats, coordinate glossary, model/design/decision/architecture/validation/handoff docs and conditional reference-equation checks. Historical timing reindexing is retained but marked incompatible with the later fixed-pulley constraint.

## 3. Local Validation Checklist

- **Validation Scope:** preliminary
- **Research/Policy Validation:** App build passes; 24 JavaScript model tests and 19 Pymunk/reference tests pass. Three independent SymPy/SciPy cases agree after regenerating fixtures. Offline browser checks pass for all seven rough studies, fixed-ratio error under 0.768 mm, calculator, detailed entry, recorded disturbances, Pymunk controls, units and full exports. Native engine debug drawing passes. Both 4186 and 4175 launchers pass start/reuse/scoped-stop/restart from C:\Windows; their intended routes respond HTTP 200. Repository gate regressions run 36 cases with 34 passing and two MuJoCo-dependent fixtures explicitly skipped in the current global environment; canonical physics is not claimed. Relative-link/fence, structure/log and staged checks are run before publication.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this member toolkit and documentation import. The shared manifest stays empty and unchanged. Initial browser import harness failures (vertical SVG visibility wait and old-port allowlist) were corrected and rerun; they are recorded in the app validation notes. Hardware, collision/contact, belt-bearing loads, GPU and other operating systems remain unverified.

## 4. Compute Saving Handoff State

Both authorized chats are packaged in Andy Zhang's Wheel Leg Lab with source, portable setup and scoped documentation.
The gallery preserves historical alternatives while the current fixed-pulley constraint and the separate fixture/control models remain explicit.
Continue from the app README and validation record, confirming missing belt/component inputs and hardware/contact behavior before promotion into canonical code.

---
## Entry: 2026-10-10 — Andy Zhang — correct Pymunk excitation to position

## 1. Scope & Objective

- **Target Subsystem:** Andy Zhang's Wheel Leg Lab member experiment.
- **Associated Issue/Task:** User correction: input is a position step, not applied force; retain both chats' published studies and update mechanics/design context.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no deletions.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/GLOSSARY.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/pymunk-remote-preview.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_view.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/architecture.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/decisions.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/design.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/equation-cross-check.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/handoff.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/model.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/motion_input.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/record_position_preview.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_pymunk.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_equation_checks.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_position_input.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/index.html`
- **API/Interface Changes:** Default target is position with a floating chassis and kinematic wheel-height carriage. Add metre amplitude, ramp shape, fixed-hip preload design load, signed driver force, command/achieved height, tracking, chassis displacement and explicit integral units. Step/square/bump trajectories use finite smooth or linear ramps; force/torque modes remain explicit legacy diagnostics. The native viewer uses the same driver; recorded step/square cases and their reproduction script replace the old force recordings. Existing geometry/calculator/JavaScript model interfaces remain intact. Correct floating preload so a prescribed-wheel force bias changes fixture reaction rather than spring equilibrium.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** 27 Python tests pass, including independent RK4 energy-response and timestep refinement; historical force/reference tests explicitly select force mode. At 1/0.5/0.25 ms, position tracking errors decrease 0.15887/0.07931/0.03963 mm and angle errors decrease 0.19835/0.09011/0.04298 degrees against the independent 48.02864444 degree reference. Tested momentum/torque residuals are below 1e-7. Build, Pymunk browser controls/exports, seven-study/offline/mobile playback browser suite and official native renderer (three shapes/seven constraints) pass. Recorded playback stays below 1 MB and source is reproducible. Manual 4186 launcher passes scoped stop/restart/reuse from C:\Windows; actual backend and routes respond. All 281 Markdown links resolve and fences balance. Repository structure/log and staged workspace gates are run before publication; no canonical app or gate-regression execution is required for this isolated scope.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this member-app-only correction; canonical assets/shared runtime remain unchanged. The floating chassis boundary and illustrative 30 mm / 250 ms input are documented assumptions. The initial browser fixture-switch preset failed its expected zero bias and was corrected; a new force-bias invariance comparison differed by 0.8 nm at the original sub-nanometre tolerance, then passed with declared solver-appropriate 0.1 micrometre / 1e-5 N tolerances. Linear ramp joins, stops, real unilateral tire contact, belt bearing loads and hardware performance remain limited or unverified.

## 4. Compute Saving Handoff State

Pymunk now treats the user's disturbance as wheel position and measures chassis response and fixture/pin loads.
The default floating chassis, finite ramps and regenerated remote recordings distinguish input motion from suspension outputs while retaining the earlier studies and diagnostic load modes.
Continue from the member app README/model/validation notes, refine timestep for peak loads and confirm real contact/belt/hardware inputs before canonical promotion.

---

## Entry: 2026-10-10 — Andy Zhang — nondeleting Capstone reorganization and complete legacy archive

## 1. Scope & Objective

- **Target Subsystem:** Andy Zhang member experimental apps and curated context.
- **Associated Issue/Task:** Owner explicitly requested moving all loose old Capstone files into Capstone_Old, making Capstone the Git repo itself, preserving original files and backing up the old source/apps/content under his GitHub member folder.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no tracked deletions.
- `ENTRY_TEMPLATE.md`
- `context/users/andy-zhang/2026-10-10-workspace-reorganization.md`
- `context/users/andy-zhang/README.md`
- `users/README.md`
- `users/andy-zhang/README.md`
- `users/andy-zhang/experimental-apps/README.md`
- `users/andy-zhang/experimental-apps/capstone-archive/.gitignore`
- `users/andy-zhang/experimental-apps/capstone-archive/AGENTS.md`
- `users/andy-zhang/experimental-apps/capstone-archive/README.md`
- `users/andy-zhang/experimental-apps/capstone-archive/archive-manifest.json`
- `users/andy-zhang/experimental-apps/capstone-archive/context/README.md`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/README.md`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0000.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0001.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0002.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0003.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0004.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0005.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0006.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0007.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0008.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0009.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0010.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0011.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0012.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0013.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0014.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0015.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0016.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0017.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0018.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0019.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0020.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0021.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0022.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0023.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0024.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0025.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0026.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0027.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0028.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0029.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0030.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0031.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0032.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0033.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0034.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0035.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0036.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0037.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0038.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0039.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0040.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0041.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0042.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0043.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0044.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0045.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0046.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0047.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0048.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0049.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0050.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0051.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0052.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0053.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0054.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0055.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0056.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0057.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0058.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0059.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0060.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0061.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0062.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0063.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0064.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0065.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0066.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0067.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0068.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0069.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0070.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0071.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0072.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0073.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0074.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0075.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0076.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0077.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0078.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0079.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0080.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0081.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0082.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0083.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0084.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0085.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0086.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0087.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0088.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0089.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0090.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0091.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0092.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0093.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0094.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0095.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0096.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0097.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0098.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0099.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0100.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0101.part`
- `users/andy-zhang/experimental-apps/capstone-archive/payload/legacy-workspace-0102.part`
- `users/andy-zhang/experimental-apps/capstone-archive/restore_archive.py`
- `users/andy-zhang/experimental-apps/capstone-archive/scripts/create_archive.py`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/.gitignore`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/.references/awesome-design-html-LICENSE.txt`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/.references/design.posthog.html`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/.references/robot-design-notes/diagram-0.png`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/.references/robot-design-notes/diagram-1.png`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/.references/robot-design-notes/diagram-2.png`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/.references/robot-design-notes/diagram-3.png`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/.references/robot-design-notes/diagram-4.png`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/AGENTS.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/README.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Start Capstone.cmd`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Start Force Plots.cmd`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Start-Capstone.ps1`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Start-Force-Plots.ps1`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Stop Capstone.cmd`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Stop-Capstone.ps1`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/THIRD_PARTY_NOTICES.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/context/README.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usfs-trail-design-guide.provenance.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0000.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0000.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0100.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0100.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0200.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0200.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0300.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0300.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0400.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0400.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0500.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0500.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0600.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0600.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0700.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0700.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0800.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0800.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0900.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-0900.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-1000.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-samples-1000.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-service.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/sources/usgs-service.request.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/synthetic-boreal-forest-100m.csv`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/synthetic-boreal-forest-provenance.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/synthetic-class3-slope-cycle-1000m.csv`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/synthetic-class3-slope-cycle-100m.csv`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/synthetic-class3-slope-cycle-provenance.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/synthetic-example-summary.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/synthetic-gravel-100m.csv`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/synthetic-gravel-provenance.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/synthetic-maintained-trail-100m.csv`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/synthetic-maintained-trail-provenance.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/terrain-archetypes.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/usfs-trail-benchmarks.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/usgs-shenandoah-provenance.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/usgs-shenandoah-transect-1000m.csv`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/data/terrain/usgs-shenandoah-transect-100m.csv`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/ARCHITECTURE.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/DECISIONS.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/DESIGN.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/HANDOFF.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/IMPORT-2026-10-10.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/VALIDATION.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/linkage/ARCHITECTURE.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/linkage/HANDOFF.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/linkage/MODEL.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/linkage/VALIDATION.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/terrain-data-and-profile-specification.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/terrain-simulation-development-plan.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/workbench/ARCHITECTURE.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/workbench/DECISIONS.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/workbench/DESIGN.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/workbench/HANDOFF.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/workbench/VALIDATION.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/README.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/linkage-ui/desktop.jpg`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/terrain-evidence/measured-transect.png`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/terrain-evidence/slope-cycle.png`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/terrain-evidence/synthetic-cycles.png`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/terrain-preview.jpg`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/ui-iteration-1/posthog-reference.jpg`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/ui-iteration-1/terrain-desktop.jpg`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/ui-iteration-1/terrain-laptop.jpg`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/ui-iteration-1/terrain-mobile.jpg`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/ui-iteration-1/verified-profile.csv`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/workbench-ui/atlas-desktop.jpg`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/workbench-ui/workbench-graph.jpg`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/evidence/workbench-ui/workbench-terrain.jpg`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/index.html`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/linkage/index.html`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/package-lock.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/package.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/public/countries.geojson`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/public/design/terrain-rover.svg`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/public/force-plots/D3-LICENSE.txt`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/public/force-plots/d3.min.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/public/force-plots/index.html`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/scripts/build_terrain_evidence.py`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/scripts/validate_linkage_reference.py`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/scripts/verify-force-plots.cjs`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/scripts/verify_import.cjs`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/data.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/linkage/charts.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/linkage/main.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/linkage/model.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/linkage/style.css`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/linkage/view.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/linkage/worker.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/main.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/model.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/style.css`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/workbench/charts.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/workbench/engine.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/workbench/main.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/workbench/style.css`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/workbench/terrain.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/src/workbench/worker.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/tests/fixtures/linkage/sympy-reference.json`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/tests/linkage.test.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/tests/model.test.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/tests/workbench.test.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/vite.config.js`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/workbench/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Start-Pymunk.ps1`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Stop-Pymunk.ps1`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/handoff.md`
- **API/Interface Changes:** Flatten the local existing checkout while retaining Git metadata/history/remote; archive the former loose workspace and empty nesting container without deleting files. Publish Terrain Mobility Atlas/workbench/historical linkage/force plots with project-local original-port launchers, model/design context, pinned Playwright verification and PATH-based Node analysis lookup. Add the owner's expressly requested historical source/evidence/output archive as 103 sub-MiB ZIP parts, exact per-file hashes and a standard-library nonoverwriting restore tool; original raw outputs are historical preservation, never active/canonical imports. Installed dependencies, bytecode, process logs/state and rebuildable dist are local-only. Update member indexes/handoff and make app start/stop helpers archive old logs/state instead of deleting them. Canonical code/assets and shared enforcement are unchanged.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Original inventory and post-move verification match all 4534 file SHA-256 values and all 431 directories. A separate restoration of the GitHub payload matches all 668 included file hashes; all 103 ordered ZIP parts are at most 900000 bytes. Imported atlas/workbench/linkage npm tests pass all 49 cases, Vite builds all three entries and local force page, and Playwright lockfile/audit reports 98 packages with zero vulnerabilities. Browser verification passes atlas controls, observed-USGS background-worker run, finite plots, mobile workbench, historical linkage route, force/travel averages and offline force controls; relocated Pymunk backend/controls/export browser checks also pass. Both app-local 4175/4186 launchers pass start/reuse/scoped-stop/restart from an unrelated Windows folder, with state/log history retained; the force launcher passes too. Relocated Python imports Pymunk 7.3.0. All 391 relative Markdown links resolve and fences balance; structure/log/staged workspace checks and diff hygiene run before publication. No automatic canonical execution or gate regressions are required for this member-only scope.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE: this is an owner-requested archive/member-app organization with no shared runtime/asset change. Original files are byte-verified in the local sibling archive; historical raw outputs are explicitly preserved at the owner's request and not used as new validation. The initial scoped-stop attempt compared a PowerShell-decoded date as a string and refused safely; comparing UTC DateTime values then verified and stopped only the correct servers. Imported CRLF text initially failed whitespace checks; working-copy text was normalized to LF without altering original/archive bytes and extra EOF blank lines were removed. A draft documentation command was rejected by automatic command review; the same authorized file edits were completed through structured patches. No original was deleted, no unrelated process stopped and no validation/size rule bypassed. Hardware, canonical robot, GPU, tire/belt structural suitability and old payload-script execution remain unverified.

## 4. Compute Saving Handoff State

Capstone is now the Git checkout itself and all original loose workspace files remain intact in sibling Capstone_Old with matching hashes.
Andy's experimental app index links the maintained terrain atlas/workbench, Wheel Leg Lab and a fully verified 668-file GitHub historical backup, with dependencies/caches/logs preserved locally.
Continue from each app's context and verification record, use the project-local 4175/4186 launchers and preserve archive hashes before any future cleanup or canonical promotion.

---

## Entry: 2026-10-10 — Andy Zhang — unified Motion Lab, mathematical model and Plotly data GUI

## 1. Scope & Objective

- **Target Subsystem:** Andy Zhang's experimental motion apps and app-local documentation.
- **Associated Issue/Task:** User requested one browser UI/launcher for mathematical simulation, Pymunk physics and motion studies, dark mode, JSON profiles/data and an always-available actual Pymunk visual GUI; authorized GPT-6.1 Sol subagents.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no tracked files deleted.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/README.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/README.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Start Capstone.cmd`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Start Force Plots.cmd`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Stop Capstone.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/.gitignore`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Open Native Pymunk Debugger.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Open Pymunk GUI.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Setup Motion Lab.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Setup Pymunk.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Start Geometry Preview.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Start Motion Lab.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Start Pymunk Linkage.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Start-Pymunk.ps1`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Stop Geometry Preview.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Stop Motion Lab.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Stop Pymunk Linkage.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Stop-Pymunk.ps1`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/leg-path-family.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/animations/pymunk-remote-preview.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/architecture.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/decisions.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/design.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/handoff.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/model.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/unified-motion-lab.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/licenses/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/licenses/plotly-LICENSE.txt`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math/wheel_leg_ode45.m`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math_model.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/package-lock.json`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/package.json`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/requirements-analysis.txt`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/requirements.txt`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/build_animations.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify-force-plots.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_motion_lab.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_pymunk.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_suite.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/server.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/src/linkage/charts.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/src/linkage/main.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/src/linkage/style.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_math_model.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/library.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/data-browser.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/force-plots/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/library.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/mathematical/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/physics/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/style.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/theme.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/viewer.css`
- **API/Interface Changes:** Add shared main menu/themes and mathematical/physical/study/data sections. Add independent SciPy scalar-energy model and verified MATLAB ode45 source while retaining distinct two-coordinate linkage and actual Pymunk models. Add /api/math/simulate and /api/pymunk/simulate with per-solver locks; preserve /api/simulate. Add versioned JSON profile/run/study imports, append-only browser IndexedDB library, MATLAB column-to-row support, separate detailed comparison-mode tables, full exports and study-state restoration. Quantitative charts use pinned locally generated Plotly runtime with zoom/pan/reset/image output; SVG mechanism/engine drawings remain. Add same-origin run/profile/theme/ready messages and actual recorded-engine viewer; mathematical poses are never represented as Pymunk. Canonical Motion Lab command aliases unify familiar browser launch names; native/legacy standalone helpers and source remain retained. Pin SciPy/NumPy and align optional analysis versions. No canonical/shared-engineering import or asset changes.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** 37 Python tests pass (27 physical/reference/position plus 10 independent mathematical cases); 32 JavaScript tests pass (24 detailed mechanics plus 8 JSON/data contracts). Independent energy, equilibrium, force/moment closure, clipping, inertia and stop/refinement cases pass; Pymunk angle errors decrease 0.19835/0.09011/0.04298 degrees at 1/0.5/0.25 ms toward the SciPy reference. Actual MATLAB R2025b Update 3 batch step agreement is within 8.40e-8 degrees and 1.18e-6 N knee load; locked-square/clipped-impedance case also agrees, and aggressive travel events terminate consistently. Unified browser checks pass real APIs, model comparison, actual three-shape engine GUI, Plotly zoom/theme persistence, profile/full-run JSON, IndexedDB reload, malformed/read-only imports, study JSON/restore and mobile. Legacy calculator/Pymunk/study suites pass; detailed Plotly geometry/response/poles/Bode and exports/embedding were independently checked. Native live renderer advances three shapes/seven constraints. Production Vite/gallery build passes with local Plotly; npm installation audit reports zero vulnerabilities and pip check has no broken requirements. Canonical launcher passes start/reuse/scoped-stop/restart from C:\Windows and familiar Pymunk/geometry/Capstone/force aliases reuse it. All 406 relative Markdown links resolve and fences balance; diff hygiene and repository working/staged gates run before publication. Recorded remote data JSON remains exact. All five authorized child workers used GPT-6.1 Sol and were marked done after completion.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this member-app UI/model contribution. Octave, hardware, tire contact, stress/explicit belt-span bearing loads and whole-vehicle behavior remain unverified. Browser library is local to its origin; JSON exports provide portable backups. Initial UI harness used a descendant selector for the Plotly container and a fixed-time wait on profile loading; selectors/condition waits were corrected and cold profile loading avoids an unwanted default run. GUI export schemas were reconciled with the common importer and MATLAB/study formats explicitly tested. Initial Vite external-script warning was removed by awaiting the locally generated classic runtime before detailed rendering. A loose SciPy comparison showed 5.86e-5 degree error against an overly tight 1e-5-degree threshold; the declared 1e-4-degree tolerance passes. Inline shell source/documentation edits rejected by command review were completed safely with structured patches/local editing helpers. No failed check was treated as canonical validation and no enforcement bypass was used.

## 4. Compute Saving Handoff State

Motion Lab at port 4186 now hosts independent mathematical simulation, actual Pymunk physics, motion studies and the persistent profile/data browser behind one themed menu and launcher.
Plotly provides data inspection while JSON exports preserve full runs or explicit study settings, and the GUI button always displays actual engine states from the corresponding physical wheel-height profile.
Continue from the unified workspace/model/validation docs, retain the historical sources and archive, and confirm physical inputs/contact/belt/hardware before any canonical promotion.

---

## Entry: 2026-10-10 — Andy Zhang — suspension presets, constant-lift studies and live desktop GUI

## 1. Scope & Objective

- **Target Subsystem:** Andy Zhang's isolated Wheel Leg Lab / Motion Lab app and design context.
- **Associated Issue/Task:** User requested the actual live Pymunk desktop GUI, eight spring mechanisms based on supplied sketches, selectable compression/extension/captured coils and direct/rod/ideal-rope transmission. User then requested both the pictured constant-lift lever and its wheel-leg adaptation, continuing the authorized GitHub publication and unified UI work.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no tracked source file deleted.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Stop-Pymunk.ps1`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/counterbalance.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_counterbalance_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_view.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/architecture.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/constant-lift.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/decisions.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/design.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/handoff.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/model.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-presets.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/unified-motion-lab.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/equation_checks.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math/wheel_leg_ode45.m`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math_model.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/native_suspension.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/native_viewer.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/references/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/references/constant-lift-lever.png`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/references/pull-through-capture.png`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/references/suspension-layouts.png`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_counterbalance_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_motion_lab.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_native_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_pymunk.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_suspension_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/server.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/spring_mechanisms.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/suspension_runtime.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_counterbalance.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_gravity_balance.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_math_model.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_spring_mechanisms.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_suspension_physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/library.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/style.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/data-browser.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/library.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/mathematical/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/physics/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/style.css`
- **API/Interface Changes:** Add nine editable suspension presets and common SI geometry/passive force laws. Preserve native legacy DampedSpring; new presets apply actual point forces with measured force/torque ledgers. Add positive physical coil lengths, unilateral engagement, ideal lossless/inextensible tension-only rope and pull-through direction mapping. Add zero-effective-length gravity compensation, explicit automatic rate calibration, elastic/total equivalent support and residuals. Add independent SciPy and actual Pymunk standalone lever study, prescribed angular position/free dynamics, Plotly ideal-versus-ordinary comparisons and model-specific JSON/library backend IDs. Add /api/spring-presets, /api/counterbalance/defaults, /api/counterbalance/math and /api/counterbalance/pymunk. Add owned native launch/status/show APIs; wheel or counterbalance envelopes select fixed installed desktop viewers, solve live, restore/reuse an identical live profile and report failures. Recorded browser playback remains separately named. Keep the original port-4186 manual CMD launcher; fix its scoped stop's DateTime comparison. Retain supplied design images and update model/design/validation/handoff documents. MATLAB accepts expanded legacy profiles but explicitly rejects unsupported new mechanisms. No shared engineering runtime, assets or gate changes.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All 82 Python tests pass: 27 original physical/reference/position, 15 independent SciPy, 12 kernel, 10 preset-physics, seven wheel gravity-balance and 11 standalone-lever cases. All 33 JavaScript tests pass. Actual force/torque impulse balances, virtual work, unilateral passivity, neutral gravity balance, genuine hip-pulley passive instability, shape geometry and timestep/energy refinement pass. All nine wheel presets converge toward independent SciPy; the constant-lift final-angle errors decrease 0.015813/0.006590/0.002969 degrees at 1/.5/.25 ms, and elastic-lift drift decreases 0.004108/.001032/.000259 N. Standalone ordinary-coil free-angle errors decrease .060354/.030213/.015115 degrees; conservative energy drift decreases .003478/.001728/.000861 J. Prescribed lever tracking refines from .225 degrees at 1 ms to below .06 degrees at .25 ms. Actual browser suites pass all nine wheel presets and both lever backends, calibrated/static plots, JSON profiles/full runs, library/model-specific load/playback, zoom/theme/mobile and the existing motion/calculator/Pymunk workflows. Actual native API tests pass knee capture, wheel compensation, prescribed lever and free lever: verified Windows HWND ownership, real advancing steps, loops, three engine shapes, respective 6/6/2/1 constraints, visible restore, exact-profile reuse and graceful zero-exit close. Official headless native renderers pass; generated logs/frames stay ignored. Actual project-local CMD launcher passes fresh start/reuse/scoped-stop/restart from C:\Windows and preserves 127.0.0.1:4186. Markdown links/fences, diff hygiene and repository working/staged scoped gates run before publication. Earlier MATLAB R2025b comparisons remain legacy-only; expanded legacy-profile parsing was checked in this turn. Authorized reused child workers were marked done after completion.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this member-app contribution. No hardware, real cable/coil packaging or limits, tire contact, stress/buckling, whole vehicle, GPU or other desktop OS validation is claimed. Exact constant elastic support is gravity compensation with neutral static stiffness, not restoring suspension. Initial parallel browser traffic produced the expected solver-busy response and the standalone harness passed when rerun sequentially. Stop safely refused a DateTime-as-string comparison; UTC DateTime values now preserve fractional creation ticks. Native checks first observed a closing state before process exit and compared a venv wrapper PID with the actual GUI PID; they now wait for zero exit and verify the live window's actual PID. A native lever readout key was reconciled with its schema and rerendered. A central-difference rounding threshold was corrected to the declared 1e-8 tolerance; all final checks pass. No failed check was represented as a hardware/canonical pass, no historical file was deleted and no hook was bypassed.

## 4. Compute Saving Handoff State

Motion Lab now hosts nine wheel suspension presets and the exact constant-lift lever, with independent equations, actual Pymunk solving, Plotly data and portable model-specific JSON.
Its GUI buttons launch, restore and reuse live desktop solvers on the host while recorded browser playback stays explicit, and the durable project-local launcher preserves port 4186.
Continue from the constant-lift/preset/model/validation docs, preserve the original archives and confirm real hardware/contact/routing and required restoring stiffness before canonical promotion.

---

## Entry: 2026-10-10 — Andy Zhang — complete constant-lift folding-leg suspension

## 1. Scope & Objective

- **Target Subsystem:** Andy Zhang's isolated Motion Lab wheel suspension experiment.
- **Associated Issue/Task:** User requested integration of the constant-lift lever into a suspension architecture and explicitly selected the existing 2:1 folding wheel-leg with a restoring spring and damper. Continue the authorized source/docs publication and durable preview.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; historical files remain intact.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/architecture.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/constant-lift.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/decisions.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/design.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/handoff.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/model.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-architecture.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/unified-motion-lab.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math/wheel_leg_ode45.m`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math_model.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/native_suspension.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_counterbalance_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_native_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_suspension_architecture_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/server.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/spring_mechanisms.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/suspension_architecture.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/suspension_runtime.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_suspension_architecture.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/style.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/style.css`
- **API/Interface Changes:** Add optional passive hip-to-original-tip ride strut alongside the upper-link gravity compensator. Separate captured/compression/extension law, stiffness, damping and automatic zero-at-pose free length; sum actual body point forces and moments in Pymunk and generalized forces/energies in independent SciPy. Export per-stage elastic/damper forces, support, energies and actual auxiliary geometry. Add a massless chassis sensor polygon only for this architecture, preserving existing chassis mass/pitch inertia. Add /api/suspension-architecture/defaults with editable 200 mm wheel/2:1 leg, primary damping zero, ride k8000/c500, no knee controller. Add cold one-run deep entry /?tab=physics&architecture=constant-lift, main/Physical buttons and embedded/standalone lever bridge. Add dual coils, actual mount/bracket/chassis labels and 15 Plotly charts. JSON/library-to-math keeps both stages. Global native launch now uses the active iframe's profile instead of a different inactive study/viewer; explicit record/child configs remain authoritative. Actual native renderer displays four engine shapes and both force paths. MATLAB parses auxiliary-off legacy exports and rejects enabled ride strut. No canonical/shared component changes or new startup services.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All 90 Python tests pass (prior82 plus eight architecture cases), and all33 JavaScript tests pass. Architecture cases cover equilibrium/zero initial ride elastic force, restoring signs, passive damping, real point-force/pin/torque closure, unchanged sensor mass/inertia, manual-preload equilibrium caveat, exact unchanged trajectories for nine auxiliary-disabled presets, and independent energy/timestep refinement. Final-angle errors vs SciPy decrease .009763/.005147/.002635 degrees at1/.5/.25ms; finest final J2/driver/guide/aux differences are about.0450N/.0166N/.00309Nm/.0511N. Conservative actual-body energy drift decreases .002542/.001250/.000619J. Real architecture browser tests pass cold single configured run, four actual shapes/dual paths, restoring and damping channels, zero initial ride elastic load, Math1e-7N/physical.02N constant-primary-support tolerances, JSON/library-to-math import with ride damping500, 15Plotly charts, native flat wheel-profile/show reuse, lever bridges, dark/mobile. Existing counterbalance and unified suites pass, including Math350mm versus inactive Misc400mm native-profile isolation. Native actual five-case API suite passes including complete two-stage suspension with four shapes/six constraints, real HWND/PID ownership, solver step advancement/loops, visible restore, exact-profile reuse and graceful zero exit. Official architecture headless render passes. Expanded auxiliary-off legacy MATLAB R2025b profile still parses, and new force laws/auxiliary stage remain explicitly unsupported. All relative Markdown links/fences and diff hygiene pass; working/staged repository gates run before publication. Original project-local CMD passes fresh start/scoped-stop/restart from an unrelated Windows directory and keeps port4186. Source workers were given exclusive final edit windows and marked done after completion.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this member-app contribution. Tire/soil contact, full vehicle pitch/roll, packaging/clearance, friction, real spring capture and structural/hardware ratings remain unverified. Source controls label demo settings and captured bilateral behavior. The initial browser draft used the old100Ns/m damping, an incorrect wheel_radius key and an over-tight physical constant-lift tolerance; factory500/radius and the measured.02N finite-step tolerance now pass, while SciPy retains1e-7N. Library load uses its matching backend before explicit JSON import into Math. A queued chassis label/camera bound and duplicate engine rectangle were corrected against the actual new polygon. No failed test was treated as canonical acceptance; no historical file, archive or unrelated process was removed.

## 4. Compute Saving Handoff State

The constant-lift concept now forms a complete passive two-stage suspension on the existing 2:1 folding leg with floating chassis and prescribed wheel height.
Weight compensation, ride restoration and damping have separate visible geometry/data, while both solvers and the live desktop GUI carry their combined pin and torque loads.
Continue from the suspension-architecture and validation records, use the project-local restart launcher and preserve archives while confirming real mechanical packaging/contact before promotion.

---

## Entry: 2026-10-10 — Andy Zhang — replacement suspension, guide visualization and passive mechanism audit

## 1. Scope & Objective

- **Target Subsystem:** Andy Zhang's isolated Motion Lab / Wheel Leg Lab member experiment.
- **Associated Issue/Task:** Latest user clarification replaces the original lower-tip spring with one r1-to-chassis spring/damper, requests visible 2:1 guide belt markers/tension vectors, and explicitly requests an Astra audit of mechanisms whose chassis fell. Continue authorized documentation and direct publication; preserve original archives.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths for this correction are listed below; the preceding entry records the earlier unpublished architecture contribution.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/architecture.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/constant-lift.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/decisions.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/design.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/handoff.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/mechanism-audit.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/model.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-architecture.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-presets.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/unified-motion-lab.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/guide_belt.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math/wheel_leg_ode45.m`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math_model.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/native_guide_belt.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/native_suspension.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/native_viewer.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_native_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_passive_stability_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_pymunk.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_suspension_architecture_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_suspension_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/spring_mechanisms.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/suspension_architecture.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/suspension_runtime.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_equation_checks.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_guide_belt.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_math_model.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_mechanism_stability.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_native_guide.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_position_input.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_replacement_suspension.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_suspension_physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/guide-belt.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/guide-belt.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/mathematical/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/physics/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/style.css`
- **API/Interface Changes:** The architecture factory now disables the auxiliary strut, uses primary damping100 N s/m and one upper-link/chassis force pair, and enables a massless chassis sensor plus28/14mm guide sensors. Browser and native views show actual anchors/bracket, moving no-slip belt dots, body rotation/pivots and torque-derived DeltaT arrows. Guide viewer baseline in N/kgf stays independent of sheet T0 and solver config; absolute span forces remain unknown without an assumption and inferred guide bearing forces are not applied to engine pin loads. Add guide geometry helpers/tests and wheel_leg native envelope with separately validated guide_visualization; native reuse keys include viewer assumptions. All nine spring presets now default to common explicit point_force integration. Restricted native_legacy remains opt-in with a splitting-bias warning; historical reference tests explicitly preserve old settings. Both config resolvers seed catalog geometry/rate/damping only when absent and retain explicit overrides. Curate legacy20k/d500, hip pulley80mm/d500, hip crank80mm/d500, knee pulley/capture d500 and knee crank24k/d1000; remaining settings retain their documented rates. Both backends export passive_stability with mean/one-sided vertical stiffness, initial balance residual, classification and local scope; both benches display it and preserve JSON provenance. MATLAB parses the integration selector and updated legacy rate/damping, while unsupported mechanisms/laws/auxiliary stage remain rejected. Update14 app documents with corrected architecture, before/after audit, assumptions, migration, historical evidence and reproducible validation. No canonical assets, shared runtime/interfaces, rules or checks changed.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** App-local unittest discovery passes114 tests in299.557s, including six new stability tests and108 full six-second backend cases (nine presets x30/45/60deg x step/square x SciPy/Pymunk),30mm displacement with250ms quintic ramps. All108 complete with finite state, no stop/slack/actuator torque, force/moment closure below1e-7 and positive signed support; minimum49.65184N in chassis_direct30deg square Pymunk. Final30deg square angle errors at1/.5/.25ms refine: legacy .465685/.262895/.133506deg, hip pulley .003096/.001546/.000773, hip crank .000498/.000240/.000117, knee crank .012975/.006191/.003024. Astra independently checked1404 valid mechanism/mode/routing/law/pose/speed combinations: no negative dissipation or compressive rope force, virtual-power residual<=6.9e-13W, energy-gradient residual<=1.64e-7Nm;54 impossible coil lengths reject explicitly. All43 JavaScript tests pass. Five current live browser suites pass: passive stability/provenance, all-nine presets on both backends, full Pymunk controls/exports/offline/mobile, corrected architecture deep-entry/library/guide/native-envelope flow, and unified Motion Lab menus/comparison/data. Actual five-case native API suite passes knee capture, gravity balance, six-shape/six-constraint replacement and prescribed/free lever: owned Windows HWND/PID, advancing1500+steps, loops, show/reuse and zero-exit close; replacement viewer baseline is saved outside config. Final corrected native GUI is running and snapshot inspected. MATLAB R2025b updated1.2s legacy profile agrees at matched times with SciPy within2.5674e-8deg and1.0209e-6N J2 load, and explicitly rejects zero-effective law; both integration selector strings parse without changing the independent ODE. Actual project-local CMD passes scoped stop/start/reuse from an unrelated Windows directory; prior fresh-start/restart evidence remains valid and port4186 is preserved. In-app final architecture preview is verified and retained. All14 changed-doc relative links/fences and git diff hygiene pass. Working/staged structure and scoped publication gates are run before publication; raw runs/screenshots remain ignored.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical physics is NOT APPLICABLE to this member-app contribution. The original audit reproduced unstable hip pulley/hip bellcrank and repeated-input lower-stop escape in older tip/knee-crank settings. The first expanded candidate sweep caught marginal60deg knee pulley/capture and30deg knee-crank cases; final damping500/1000 revisions pass the full envelope without tolerance loosening or a hidden controller. The old knee-crank24k/d500 configuration converges before escape but lacks converged six-second behavior; this is retained as a limitation rather than a proof that SciPy's bounded result is wrong. Native DampedSpring splitting bias remains an explicitly selectable diagnostic. Exact constant lift is neutral, not a unique restoring ride height. Edited profiles, tire/soil contact, whole-vehicle dynamics, spring/cable packaging, structural ratings, hardware and other desktop OS/GPU performance remain unverified. Guide-bearing loads are outside the GearJoint model. Historical tests now declare historical settings, not weakened assertions; no failed intermediate check was counted as final success, no original file was deleted, and no hook is bypassed.

## 4. Compute Saving Handoff State

Motion Lab now defaults to the requested single upper-link/chassis replacement unit with visible2:1 guide material marks, torque-derived tension vectors and independent viewer assumptions.
The revised nine-preset demos pass the documented108-case envelope and display local restoring/neutral/unstable diagnostics, while exact constant lift stays neutral and native_legacy remains an advanced diagnostic.
Continue from the mechanism-audit, suspension-architecture and validation documents, use the project-local Start Motion Lab.cmd at port4186, and preserve archives while confirming real routing/contact/component limits before canonical promotion.

---

## Entry: 2026-10-10 — Andy Zhang — saved-run comparison workspace and undamped end-force lever

## 1. Scope & Objective

- **Target Subsystem:** Andy Zhang's isolated Motion Lab member app.
- **Associated Issue/Task:** Move the standalone constant-lift study into Miscellaneous, retire the detailed-linkage main tab, add end-force interaction/equations, create multi-profile/channel comparison with independent plot visibility and horizontal/vertical splits, and run/show SciPy-versus-Pymunk deltas. User explicitly clarified the single-link lever needs no controller or damping.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; source/history and existing records retained.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/counterbalance.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_counterbalance_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/architecture.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/comparison-workspace.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/constant-lift.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/unified-motion-lab.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/compare_suspension_models.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_comparison_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_counterbalance_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_lever_force_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_motion_lab.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_native_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_suspension_architecture_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/server.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_counterbalance.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_counterbalance_force.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/comparison.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/library.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/comparison-data.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/comparison.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/comparison.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/style.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/data-browser.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/library.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/mathematical/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/physics/index.html`
- **API/Interface Changes:** Mathematical navigation now exposes the current 2D SciPy suspension only. Constant-lift lever uses one persistent Misc frame; detailed linkage stays available as an explicitly archived Misc study/direct route. Legacy Math deep links and saved profiles route to the matching retained study. Add top-level Comparison plus library actions; profile loading runs its supported solver explicitly and appends a recorded result. New comparison modules implement multiple source records, searchable right-hand channels, independent per-plot visibility/legend, up to eight recursively split plots, distinct unit axes, reference selection and signed candidate-minus-reference deltas. Validate known matching channel/family/units and increasing sample time; interpolate only within overlap without crossing missing values. Report max/RMS/final/sample count, export/import full-source comparison JSON with layout/visibility/provenance and portable 80 MiB limits. Existing source datasets are preserved. Run both now opens paired overlay/delta panels. Standalone lever defaults to free motion, damping0, one pivot and no motor. Add force mode, force_amplitude_N, ramp_shape and portable force_history intervals; apply actual tip force Fy and moment Fy L cos(theta) in both independent math and Pymunk, with force/power/work/energy diagnostics. Add bounded stateless /api/counterbalance/advance using SciPy and explicit t/theta/velocity state. Browser press/hold controls use 100ms chunks paced to wall time, preserve velocity on release, release/pause on blur/inactive tab and cap each session at20s. Explicit Place at rest is a user-visible state reset, not control. Prescribed motor mode stays an explicit diagnostic and old tests request it. Update native force drawing/readouts, model-specific JSON validation, seven docs, browser regressions and a reproducible wheel-comparison script. No shared runtime/assets/interfaces or enforcement changes.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All19 affected Python lever tests pass (11 historical tests plus8 force/live tests). All56 JavaScript tests pass, including12 new comparison/interpolation/layout/provenance tests and force-history JSON roundtrip. Live browser suites pass verify_lever_force_ui, verify_comparison_ui, verify_motion_lab, verify_counterbalance_ui and verify_suspension_architecture_ui. Coverage includes real up/down input, coast on release, rest placement, portable force-history replay, native routing, inactive-frame pause/resume, one Misc instance, profile rerun, matched model deltas, independent channels/legends, both split directions, comparison JSON roundtrip, Plotly zoom, theme, mobile and retired-linkage compatibility. Actual five-case native API suite passes window ownership, advancing live steps, loop, restore/reuse and graceful zero exit; prescribed lever case now explicitly selects its diagnostic mode. New end-force native headless rendering passes1000 actual steps, three shapes and one PivotJoint. A2N/.3s pulse with50ms rise/fall starts at.1s and ends a1s SciPy run at51.55276285deg; release angular velocity .50101018rad/s persists without damping and external-energy residual is4.6e-10J. Force-pulse final-angle errors versus Pymunk refine .26191165/.13057446/.06519184deg at1/.5/.25ms with force/moment closure below1e-8. The new reproduction script ran both unchanged wheel models at1/.5ms using200mm wheel,273mm links,45deg,30mm/.25s quintic step,6s. Max chassis discrepancies are .5892305/.2894302mm for original tip and .3246738/.1512563mm for replacement constant lift. Full-window J1 startup maxima remain7.21089N/48.60924N and do not halve; after50ms J1 maxima decrease3.61330 to1.79449N and.227748 to.114630N respectively. UI and script share union-of-timestamps interpolation and sample RMS; the default displayed pair has6000 matched samples. The in-app Comparison tab is populated with actual paired runs/deltas and retained for the user. Updated project-local launcher passes stop/start from C:/Windows, keeping127.0.0.1:4186. Documentation relative links/fences and diff hygiene pass; scoped working/staged/publication checks run before push. Parallel source workers used isolated managed worktrees; needed native evidence was copied before requesting recoverable archive. No raw runs/logs/screenshots/dependencies are committed.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE. The previous114-test nine-mechanism wheel audit was not rerun because its core was unchanged; it remains historical evidence, not a new claim. Current wheel comparisons are the measured cases above. Pymunk pin reactions average solver impulses; math loads are instantaneous, and startup differences are reported rather than hidden. No hardware/contact/structural or global-stability claim is made. An undamped balanced lever stays where placed at rest but coasts if released with velocity; there is no automatic brake. Live force changes have up to one100ms chunk latency and may run slower under host load; state is not sped up to compensate. Early harness failures came from a new home button count, a collapsed control and reading mobile width before Plotly responsive layout settled; final assertions remain strict and pass. Parent-script CRLF changes were normalized without semantic edits. The comparison workspace uses browser storage/downloads, not cloud upload; original detailed-linkage source and archives remain intact.

## 4. Compute Saving Handoff State

Motion Lab now separates the current wheel mathematical/physical models from the undamped single-link lever in Miscellaneous and retains the older detailed study as an archive.
Comparison loads saved profiles or recorded data into independently configurable split Plotly panels with checked units, signed deltas and portable full-source workspace JSON.
Continue from comparison-workspace, constant-lift and latest validation records, preserve the distinction between undamped rest and moving release, and use the existing project-local launcher at port4186.

---

## Entry: 2026-10-10 — Andy Zhang — compact comparator plotting UI

## 1. Scope & Objective

- **Target Subsystem:** Motion Lab saved-run comparator.
- **Associated Issue/Task:** During the preceding implementation the user requested a much tighter UI, hideable text/buttons and larger plots. Preserve their open comparison while updating the layout.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/comparison-workspace.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_comparison_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/comparison.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/comparison.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/library.js`
- **API/Interface Changes:** Compact the comparator header/navigation and channel rows. Sources/help and per-plot Controls are collapsed by default; controls retain splitting, mode/reference, trace visibility, removal and legend functions. Add Hide/Show channels and Focus plots with Exit/Escape restoration. Focus temporarily hides interface chrome and legends without mutating source data or saved per-plot visibility. Enlarge and vertically resize charts, observe geometry changes for Plotly fitting, and compress delta readouts. Comparison JSON downloads now request compact formatting through a backward-compatible optional downloadJSON argument; actual download size matches its80MiB import guard. No numerical solver or data schema changed.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Updated real-browser comparison harness passes compact chart positioning, collapsed controls, sidebar toggle, focus/restore, independent trace/legend visibility, both split directions, export/import, actual profile rerun, zoom/theme/mobile. All22 comparison/library unit tests pass after the optional export-format change. In-app Focus and Escape were visually checked. The open comparison was backed up before refresh and restored; original results/layout/visibility are retained alongside subsequent channel selections. Its initial indented JSON was87,116,203bytes and exceeded the80MiB importer; compact export is55,032,085bytes, below the bound, with identical source results verified. Original backups remain intact. The earlier feature's19Python/56JavaScript and native/browser evidence remains scoped above; no solver retest is claimed for this presentation-only change. Documentation and diff checks pass; repository gates are rerun for the complete combined contribution before publication.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE. A first compact-UI harness attempt tried selecting a library item after closing its containing disclosure; sequencing was corrected, preserving the visibility assertion. Restoring the earlier indented workspace exposed the formatting-size mismatch, now fixed with compact export rather than a raised import limit or dropped data. Transient controls/sidebar/focus state is presentation-only; portable workspace JSON retains plots, sources and their data-visibility settings. No original source or user dataset was deleted.

## 4. Compute Saving Handoff State

The comparator now prioritizes larger plots, with source/help details and individual plot controls available on demand.
Sidebar and focus toggles resize Plotly while preserving selected channels, legends and numerical comparisons, and the user's open comparison has been restored.
Use Sources & help for portable compact JSON, Controls for plot configuration and Exit focus or Escape to return to the compact workspace.

---

## Entry: 2026-10-10 — Andy Zhang — Capstone controls conversation context

## 1. Scope & Objective

- **Target Subsystem:** Andy Zhang's shared member controls context.
- **Associated Issue/Task:** The user requested a scan of Capstone robot-controls chats and publication of organized context notes, explored topics, floating problems and questions in context/users/andy-zhang. Curate available project excerpts, targeted earlier conversation retrieval and current repository evidence while preserving their different evidentiary status.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `context/users/andy-zhang/README.md`
- `context/users/andy-zhang/2026-10-10-chatgpt-controls-overview.md`
- `context/users/andy-zhang/2026-10-10-chatgpt-controls-topics.md`
- `context/users/andy-zhang/2026-10-10-chatgpt-controls-open-questions.md`
- `context/users/andy-zhang/2026-10-10-chatgpt-controls-model-reference.md`
- `context/users/andy-zhang/2026-10-10-chatgpt-controls-sources.md`
- **API/Interface Changes:** None. Add five linked, dated Markdown notes and an entry section in Andy's README. Record twelve core project-thread excerpts, separately attributed earlier context, fifteen open questions and illustrative equations. Distinguish historical knee-spring discussions, current passive prescribed-wheel-motion experiments and proposed outer/MIT whole-robot control. Preserve earlier handoffs and all app/canonical files. No raw private transcripts, account exports, partner correspondence or unrelated personal context are imported.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Targeted Markdown validation passes across the five notes and member README: 99 relative links/anchors resolve, code and display-math fences balance, and all files have final newlines. Git diff whitespace check passes. Independent analytical review confirms the illustrative fixed-MIT plant, spring-energy derivatives, coordinate/Jacobian mapping and moving-base equation under their stated assumptions; review clarifications distinguish inertial chassis motion from relative extension, loaded geometric stiffness and net support from active force. Independent coverage review found no major missing topic in the available core excerpts. Source and public-project scope were reviewed against base 7c5cbc76efd36876e829803efc49578bea24f7fa; full-transcript/image coverage limits are explicit. The commands python tools/check_entry.py --base origin/main, python tools/check_entry.py --base origin/main --require-passed and python tools/check_entry.py --staged --base origin/main all pass (482 files, seven changed paths, workspace scope). python tools/physics_gate.py --base origin/main exits successfully and reports canonical physics NOT APPLICABLE, with no app execution or gate regressions.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this Markdown-only member context contribution. No controller implementation, simulator run, hardware test, new performance result or current vendor-capability verification is claimed. Existing Motion Lab numerical/GUI/launcher evidence remains in its owning records and was not rerun. Publication uses the connected GitHub tools with the locally checked staged tree and an expected-head ref update; no shared history is rewritten.

## 4. Compute Saving Handoff State

Andy's member README now links a controls overview, explored topics, fifteen open questions, an illustrative modeling reference and a dated source map.
The packet preserves plant-boundary, outer-command, impedance/damping, geometry, simulation, sensing and timing questions while separating proposals from the current passive app and disclosing incomplete transcript retrieval.
Continue from the overview and the selected open questions, and record accepted engineering decisions in their existing owning documents with supporting evidence.

---

## Entry: 2026-10-11 — Andy Zhang — smooth physical playback and architecture setup previews

## 1. Scope & Objective

- **Target Subsystem:** Motion Lab wheel-model browser playback and architecture selection.
- **Associated Issue/Task:** User reported laggy 2D physical playback and requested a system preview when selecting a linkage architecture before clicking Run.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_playback_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_setup_preview_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/server.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/setup_preview.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_setup_preview.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/style.css`
- **API/Interface Changes:** Cache recording bounds, input extrema and decimated disturbance samples once per loaded run. Move existing Plotly cursor SVG paths with the pinned axis conversion while keeping raw/full layout shape coordinates current for zoom/redraw/export; remove repeated Plotly.relayout calls from playback. Keep animation/cursors on the display clock, throttle HTML readouts to15Hz during playback and refresh exact samples on pause/scrub/end. Pause inactive wheel tabs and closed recorded-viewer dialogs. Add POST /api/setup-preview and isolated setup_preview.py: validate/build initial body/anchor/coil geometry through the existing fixture builder, never Space.step, and return kind=setup-preview, solver_steps=0 without trace/load rows. Both benches debounce and cancel superseded setup requests, show initial architecture/geometry edits independently of prior results, hide unsolved loads and offer Show last recording without discarding edits. A completed run cancels setup state and restores normal playback/export. Update documentation and add three Python preview tests plus browser playback/setup regressions. Numerical solver equations, timesteps, recorded samples and original exports remain unchanged.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Three setup-preview Python tests pass, covering all9 catalog presets under a Space.step mock that raises if called, replacement upper/chassis sites and sensors, geometry edits, finite JSON and invalid-config rejection. All56 JavaScript tests pass. Six real-browser suites pass: verify_pymunk, verify_playback_ui, verify_setup_preview_ui, verify_suspension_ui, verify_suspension_architecture_ui and verify_motion_lab. They cover actual playback, all9 presets in both backends, setup selection without simulation requests or invented loads, cancelled/superseded preview state, returning to prior data without losing edits, exact scrub/pause/end values, wall-clock advance, inactive-tab pause, zoom/pan/theme, SVG export and main-shell/library/native routing. Comparative headless Edge1400x1000 instrumentation used identical six-second6000-row/668-frame profiles and four-second playback intervals: default11plot p95frame interval50.1→4.3ms, replacement12plot62.5→4.3ms; each38gaps>33ms→0. Mean callback CPU6.33→.782ms and8.25→1.149ms. Actual fixed code has0Plotly.relayout calls during playback, versus429/468 calls over4s. Every11/12cursor matches raw/full layout and axis-transformed SVG coordinates; zoom/pan/dark redraw and SVG export retain the selected marker, including the angle plot. Fixed renderer SHA2561efac9cbaae8a02c4b7812142db50a3b6b4f6535f4b9493fd9a6230d0caf5eaa and full raw benchmark evidence stay in ignored artifacts. Node syntax, Python compilation, edited Markdown links/fences and diff hygiene pass. The actual project-local stop/start CMD launchers restart the new server from an unrelated Windows directory at127.0.0.1:4186; a setup-only preview route is available at /physics/?loadOnly=1. Repository working/staged/publication gates run before push. Remote controls-context documentation ca5fb13 was integrated by fast-forward, with every local app edit verified byte-identical and both independent contribution entries retained.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE. Headless frame intervals measure this local comparative workload, not remote-display FPS or hardware performance. The earlier ablation only located the bottleneck; the reported final timings are the actual edited renderer. A benchmark harness initially exceeded Chromium inspector response-body cache while retrieving a large run; acquisition moved to APIRequestContext without changing the workload, and final checks passed. Cached bounds preserve the original complete recording extent; no raw results or solver sampling were decimated for performance. Setup geometry is not a simulated equilibrium/load report and cannot be exported as a recorded run. Pinned Plotly shape/axis internals need the retained cursor tests on a dependency upgrade. No shared assets, production physics, existing records or original archives were changed/deleted.

## 4. Compute Saving Handoff State

Wheel playback now avoids repeated chart rebuilds and recording-wide scans while retaining synchronized poses, cursor positions and exact paused readouts.
Both wheel-model tabs show separate zero-step architecture previews before Run and preserve the previous recording and edited controls without mixing their load data.
Use the project-local launcher and the new playback/setup browser checks before changing renderers, Plotly versions or preview/record state handling.

---

## Entry: 2026-10-11 — Andy Zhang — cylinder transmissions, tab memory and undamped constant lift

## 1. Scope & Objective

- **Target Subsystem:** Motion Lab browser suspension/lever preview and control memory.
- **Associated Issue/Task:** Show a cylinder, cable/rod routing and compressing end cap on the leg and an enlarged upper-right view; distinguish all three transmissions; retain unchanged form inputs across tabs; remove constant-lift damping and the optional extra tip strut. User feedback also requested a clearer cylinder placement and explanation of the old orange span.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/constant-lift.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-architecture.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-presets.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/unified-motion-lab.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_lever_force_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_playback_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_suspension_architecture_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_transmission_memory_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/setup_preview.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/spring_mechanisms.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/suspension_architecture.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_gravity_balance.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_math_model.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_replacement_suspension.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/spring-transmission.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/counterbalance/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/form-memory.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/spring-transmission.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/style.css`
- **API/Interface Changes:** Add spring-transmission SVG adapter using captured/setup coil length, resolved free length, input travel and engagement; keep explanatory package/routing dimensions separate from solver bodies. Show fixed seat, green moving cap, rod/rope/idler and rotating spring drum plus three200mm-reference/+20mm comparison diagrams; cache the static comparisons during playback. Place the cylinder above r1 after user feedback and remove the duplicate straight orange span. Setup-preview adds actual_rest_length and frame spring_slack while remaining zero-step/no-load. Add contract-matched form memory; wheel config/views persist in backend-specific session storage and Misc study inputs/disclosures restore after navigation. Explicit profile/study loads take precedence; fix loading a profile into an already-loaded study. Preserve guide geometry/visibility on preset changes. Set current gravity-balance factory/catalog damping0, auxiliary off, remove constant-lift damper controls and all extra-strut UI; retain historical solver APIs and saved run data. Update current docs and scoped regression checks. No shared assets/runtime/interfaces/rules are changed or original files deleted.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** 58 JavaScript tests pass. Full125 Python run initially passed123 and the complete108 six-second catalog backend cases, including current undamped constant lift with no stops/slack/nonfinite state/actuator and positive support. Two older assertions failed after the requested change: minimum absolute chassis movement and a damped error budget. The undamped isolation test now checks actual relative travel, low absolute chassis movement, zero dissipation and energy closure; the historical damping-ledger test explicitly selects damping100. All31 tests in the four affected Python modules pass on rerun; the full125 suite was not repeated. Current undamped1.2s/8mm Pymunk/SciPy final-angle errors refine .0315123/.0133835/.0061061deg at1/.5/.25ms, reported without calling them a6mdeg pass; explicit damping100 historical case refines .0158129/.0065896/.0029694deg. Seven actual browser suites pass transmission_memory, suspension_architecture, playback, setup_preview, lever_force, counterbalance and motion_lab. Coverage includes actual saved coil/cap travel/sign, three routes and rope idler, setup beforeRun, no unsolved forces, current damping0 and extra controls absent, N/kgf, live force/release, profile/library/native mock routing, tab/refresh/study numbers/checkboxes/sliders/views, contract mismatch exclusion, explicit import precedence, Plotly cursor/zoom/export/pause and mobile/theme. Native desktop-window lifecycle was not rerun; earlier live-window evidence remains historical. Actual project-local CMD stop/start/reuse from C:/Windows verifies the unchanged127.0.0.1:4186 preview. Node syntax, Python compilation, edited Markdown links/fences and diff hygiene pass; fetched-base working/staged/publication checks run before push. Raw traces/screenshots and environments remain ignored.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. Housing/idler/bracket drawings are massless explanatory packaging, not contact, cable inventory, solid-height, hardware or clearance validation; zero-effective balance still requires ideal offset/preload emulation. Old recorded runs retain their original config/data; new controls normalize constant lift to undamped and no auxiliary. Session memory is not portable JSON or a durable saved run. An early route-comparison harness selected incompatible automatic compression/direct preload, correctly rejected; it now uses captured coil behavior. Another harness expected a select absent from the actual ratio study and was corrected to its number/checkbox/slider controls. Playback initially restored the prior case's2x speed; its strict wall-clock test now explicitly selects1x, with no loosened bound. That failure was first suspected as concurrent CPU load before finding speed memory. A doc-edit command was issued from C:/Windows with a relative Python path, failed without modifying files, and was rerun from the app root; the launcher lifecycle itself passed. The in-app current preview was refreshed and visually checked with settings retained. Historical FPS measurements predate the additional cylinder overlay; current no-relayout/timing regression is the scoped claim.

## 4. Compute Saving Handoff State

The wheel preview now shows leg-mounted cylinder/rod/cable routing and an enlarged moving-cap cross-section, with separate diagrams explaining the three transmissions.
Current constant lift is undamped with no extra-tip spring option, while versioned contract-matched session/study memory keeps controls across navigation and explicit imports retain authority.
Continue from the updated preset/architecture/validation records, preserve original runs and legacy reproduction APIs, and use Start Motion Lab.cmd at port4186 with the transmission-memory and playback checks.

---

## Entry: 2026-10-11 — Andy Zhang — correct the three spring transmission assemblies

## 1. Scope & Objective

- **Target Subsystem:** Motion Lab spring transmission hardware choices and preview.
- **Associated Issue/Task:** User clarified three assemblies: normal bare inline spring, behavior-reversing cylinder/piston, and that piston pulled by rope attached at its end. Pulley mechanisms require cylinder plus rope; other layouts offer inline or rigid reversing piston.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-presets.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_suspension_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_transmission_memory_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/spring_mechanisms.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_math_model.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_spring_mechanisms.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_suspension_physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/spring-transmission.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/spring-transmission.js`
- **API/Interface Changes:** Keep existing direct/pullrod/ideal_rope JSON IDs and force law definitions. Hip/knee pulley and knee-capture catalog defaults now select compression/ideal_rope. Restrict current pulley UI to type3 and non-pulley UI to type1/type2; adapt old incompatible choices during current profile/session import while retaining legacy explicit solver fields and original recorded data. Restore config from its authoritative object, then only raw view controls/disclosures, preventing old remembered dropdowns from undoing migration. Remove all housing/piston-rod symbols from inline preview; reversing piston has a fixed-length rigid rod with moving end eye; rope starts at that outside eye, turns around an external idler and never goes through the coil/cap. Use these distinct assemblies in leg/enlarged/comparison views. Keep current undamped constant lift, removed aux UI, guide geometry and recorded force data. Update current docs and existing scoped tests; no shared assets/runtime/interfaces/enforcement or original archives are changed.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All60 JavaScript tests pass, including new SVG assembly/rod/cable attachment/travel checks. All40 affected Python tests pass across test_spring_mechanisms, test_suspension_physics, test_setup_preview and test_math_model. They check nine force/work/energy models, actual independent SciPy/Pymunk loads/refinement, historical inline-pulley versus reversing-piston external compliance, internal coil travel sign and legacy explicit routes. Updated pulley1.2s Pymunk/SciPy angle errors at1/.5/.25ms remain .0024606/.0012375/.0006206deg hip and .0089326/.0045268/.0022777deg knee/capture. Four browser suites pass verify_transmission_memory_ui, verify_setup_preview_ui, verify_suspension_ui and verify_playback_ui: all9 presets on both actual backends, distinct assembly drawings, rope/rod-eye attachment, setup without loads, recorded coil/cap motion, route restrictions, profile/session/view/tab memory, unaffected 2:1 guide and Plotly pause/zoom/export/mobile. Updated in-app preview is visually inspected and retained. Actual project-local CMD stop/start/reuse works from C:/Windows at127.0.0.1:4186. Node syntax/Python compilation, edited Markdown links/fences and diff hygiene pass; fetched-base working/staged/publication checks run before push. Raw screenshots/results/environments stay ignored.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated workspace. Housing/rod/idler mounting dimensions remain explanatory, not added solver contact/inertia, actual package fit, cable inventory or hardware/structural validation. Rope cannot push; incompatible coil/preload combinations still fail explicitly. New default routing preserves tested external compliance while internal coil motion reverses; old runs are not silently rewritten. Two initial Python comparison assertions assumed old knee-pulley defaults; their legacy reference cases now explicitly select extension/direct. One intermediate rerun had loaded the old assertion before the edit; final full40 affected tests pass with original numerical tolerances retained. An overly broad documentation table replacement briefly misclassified bellcranks, corrected to unchanged extension/inline before publication. The full125 tests,108 six-second envelope and native-window lifecycle were not rerun; earlier evidence retains historical scope.

## 4. Compute Saving Handoff State

Current previews distinguish a bare inline spring, a reversing rigid piston, and a piston whose external rod end is pulled by routed rope.
Pulley presets/UI now use the cylinder-plus-rope assembly while non-pulley layouts offer inline or rigid piston, with coil law independent and session/profile memory respecting migration.
Continue from the corrected preset/validation records and transmission-memory tests, preserve old recorded data and legacy solver IDs, and restart with Start Motion Lab.cmd at port4186.

---

## Entry: 2026-10-11 — Andy Zhang — remove the added piston pulley

## 1. Scope & Objective

- **Target Subsystem:** Motion Lab spring cylinder/cable mechanism drawing.
- **Associated Issue/Task:** User requested no second pulley on the piston assembly; cable must use the mechanism's existing hip/knee pulley.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-presets.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_transmission_memory_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/spring-transmission.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/spring-transmission.js`
- **API/Interface Changes:** Extend client-only drawCylinder options with routeRope and mechanismPulley. Generic cylinder/comparison symbols no longer add an idler. Main mechanism draws rope from the moving exterior rod eye directly to the existing modeled joint-pulley tangent and wrap, with material marks following recorded payout. Enlarged view explicitly repeats the same named hip/knee pulley, configured radius and recorded angle and labels it as the same part. Add main/detail joint metadata and assertions preventing unintended extra circles. Reposition the generic rope-lead label to avoid the rod-end label. Update current README/context/preset/validation records and the browser regression's output. No backend equations, constraints, spring law, data/profile schema, saved records, guide belt, hardware assets or original archives change.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All61 JavaScript tests pass, including no implicit cylinder pulley and an explicitly supplied same-joint close-up. Three actual browser suites pass verify_transmission_memory_ui, verify_setup_preview_ui and verify_playback_ui. Coverage includes exactly one main spring drum in hip/knee/capture presets, zero routing idlers, matching main/detail joint identity and radius metadata, no pulley in generic comparison symbols, actual recorded cap/coil motion and rod-end cable, all9 initial previews without solved loads, form/profile/tab memory and Plotly cursor/zoom/export/pause behavior. Latest transmission suite rerun captures the final non-overlapping labels and corrected diagram. In-app current preview was refreshed, visually inspected and retained. Actual project-local CMD stop/start/reuse succeeds from C:/Windows at127.0.0.1:4186. Node syntax, edited Markdown links/fences and diff hygiene pass; fetched-base working/staged/publication checks run before push. Raw screenshots and recordings remain ignored.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE. This presentation-only edit adds/removes no solver body, constraint or force; previous numerical/native tests remain historical rather than claimed reruns. The close-up is another view of the existing joint pulley, with schematic housing placement/visual scale, not a second hardware part. The separate2:1 guide still has its own existing two pulleys. A first contribution-log read used the app working directory; the existing root ENTRY_TEMPLATE.md was then read successfully before dependent edits. No required source remains inaccessible and no original file or dataset was deleted.

## 4. Compute Saving Handoff State

The piston assembly no longer has an added idler: its cable directly uses the existing mechanism hip/knee pulley.
Main view, enlarged view and generic comparisons now distinguish the single physical joint pulley from a repeated view, preserving recorded stroke, force data and settings.
Continue from the latest preset/validation record and the no-extra-pulley browser checks, and restart with the existing Start Motion Lab.cmd at port4186.

---

## Entry: 2026-10-11 — Andy Zhang — invertible dual-rope and symmetric knee suspension

## 1. Scope & Objective

- **Target Subsystem:** Motion Lab full-angle suspension study, Math/Physical UI, records and live native viewer.
- **Associated Issue/Task:** User requested a parallel femur compression cylinder with actual ±5° knee rope anchors, two smaller routing pulleys, one shared cap with one loaded rope at a time, a symmetric knee bellcrank mounted 50 mm from J1, and inverted-start femur-torque flips.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_inversion_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/invertible-suspension.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-presets.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/unified-motion-lab.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/inversion.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/invertible_spring.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/native_viewer.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_inversion_native.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_inversion_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/server.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_inversion.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/inversion-library.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/comparison-data.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/data-browser.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/library.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- **API/Interface Changes:** Add isolated inversion geometry, Pymunk ground-contact/fixed-J1 solvers and independent full-angle SciPy ODE. Add GET /api/inversion/defaults and POST /api/inversion/preview, /math and /pymunk; no original solver endpoint removed. Config uses explicit SI dimensions/masses, actual rope attachment offsets, routing geometry, coil preload/travel, finite torque pulse/slopes and timestep bounds; invalid overlap/exhausted travel fails. Native viewer accepts model=inversion with validated config and launches the fixed debug_inversion_gui.py program. New inversion_math/inversion_pymunk backend IDs retain explicit channel units and a separate comparison family; original saved data/schema remain unchanged. Add /inversion/ UI, two menu presets, separate remembered Math/Physical frames, Plotly plots, moving shared-cap detail, JSON/library routing and matched fixed-J1 Run both comparison. Immediate config publication prevents stale native launches; bounded busy retries preserve legacy Math execution. Actual force sites reproduce one spring energy's virtual torque and preserve preloaded dead-centre endpoint force. Ground chassis translation/heave is free with pitch held; fixed-J1 Math comparisons have no floor. Existing single-rope presets gain no piston idler. No shared assets, engineering runtime, dependencies or enforcement files change; no original archive is deleted.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All62 JavaScript tests and all16 scoped Python tests (test_inversion, test_replacement_suspension, test_setup_preview) pass, with retained tests for actual routing/one-cap switching, spring energy/force-site virtual work, symmetry, dead-centre force, zero-step preview, both real ground flips and fixed-J1 numerical refinement/energy closure. Five browser suites pass verify_inversion_ui, verify_motion_lab, verify_suspension_architecture_ui, verify_transmission_memory_ui and verify_comparison_ui; the inversion suite is rerun after the final server restart. Native endpoint calls are mocked only in browser tests; actual scripts/verify_inversion_native.py passes both desktop windows with4001 steps each,4constraints,8dual/5bellcrank shapes, owned HWNDs and graceful exit0. Ground default100Nm pulses flip at.3120s dual/.3325s bell with.25ms steps;.125ms flips at.3120/.332875s, with continued rebound/airborne motion recorded. Sampled default wheel penetration1.398/.793mm refines to.505/.749mm. Independent fixed-J1 energy residual<.001J and final angle error<.1deg at.125ms in the tested low-load cases. Actual project-local CMD start/stop/restart/reuse from C:/Windows preserves127.0.0.1:4186 and the inversion route responds200. Python compilation, JS syntax, edited Markdown links/fences and diff hygiene pass; fetched-base working/publication/staged checks run before push. Generated raw recordings/snapshots/logs/environments remain ignored.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. An earlier180ms dual pulse at1ms appeared to flip but failed refinement; the current240ms/.25ms demo is validated at.125ms. The fixed-J1.25ms error initially missed the.1deg budget; adding.125ms refinement passes without relaxing it. Routing overlap/intersection validation and nonzero preloaded dead-centre force were fixed after review and now have retained coverage. Browser checks found stale global native config and409 from a background legacy Math run; immediate config publication and bounded busy retry correct them. Initial browser automation could not click an embedded iframe in the in-app tool; actual Playwright iframe tests and the direct in-app study run pass. Contact peaks remain timestep dependent. Ideal shortest rope routes omit winding/groove/crossover history, stretch/friction/binding; massless packaging,3Dclearance, real coil solid height, hardware ratings and whole-vehicle self-righting are unverified. Chassis pitch is held; release is undamped with no hidden position hold. MATLAB remains legacy-tip-only. Previous full numerical/envelope audits retain historical scope and were not rerun for this feature.

## 4. Compute Saving Handoff State

The new full-angle bench contains a dual-rope common compression cap with actual offset anchors/two routing pulleys and a symmetric knee bellcrank anchored50mmfromJ1.
Both real ground demos start wheel-up/chassis-down and flip under applied femur torque, while independent SciPy/Pymunk comparison explicitly holdsJ1 without contact and the native button runs the actual engine on the host desktop.
Continue from docs/invertible-suspension.md and the scoped validation record, preserve original limited-angle/single-rope studies and saved data, refine timestep before interpreting contact peaks, and restart with the existing Start Motion Lab.cmd at port4186.

---

## Entry: 2026-10-11 — Andy Zhang — correct central rope feeds and knee-face pull

## 1. Scope & Objective

- **Target Subsystem:** Invertible dual-rope suspension geometry, loads and preview.
- **Associated Issue/Task:** User confirmed ropes pass through the centre between the small rollers, then flare outward to the actual ±5° knee face attachments, without wrapping around the knee outer rim.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_inversion_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/invertible-suspension.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-presets.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/unified-motion-lab.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/inversion.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/invertible_spring.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_inversion_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_inversion.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/inversion-library.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/library.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- **API/Interface Changes:** Correct default rope_routing to central_face and add SI rope_eye_offset; explicit outer_rim remains for prior profile reproduction. Current demo roller centres are ±15 mm and cap eyes ±2 mm, while session numbers stay remembered. Compute full moving-cap cable inventory with free centre spans or inner-side tangent/arcs on either roller, never a knee-rim arc. Solve each rope's cap demand, select the maximum for one shared compression cap, calculate real slack and lead-angle projection T=Fcap/cos(lead angle), and apply actual outgoing cable tension at force sites. Update main/close-up/native rope and yoke drawing, fixed roller locations and equations. Resolve old saved profiles without routing metadata to explicit outer_rim at execution/import/native bridges without modifying stored JSON/frames; direct API requests lacking the marker use current defaults. Document physical boundary, equations, correction and actual evidence. No original single-rope mechanism, bellcrank force law, shared component, canonical asset or enforcement file changes; no archive/data is deleted.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All18 scoped Python tests (test_inversion, test_replacement_suspension, test_setup_preview) pass. New retained assertions cover inside-gap cap eyes, no knee-rim arc, exact cable inventory/slack, cap/tension projection, angular-sweep energy gradients away from handoff ties and explicit legacy reproduction; actual force-site virtual work, ground flips and fixed-J1 SciPy refinement/energy still pass. All63 JavaScript tests pass, including non-mutating old/new profile route resolution. The real verify_inversion_ui browser suite passes central main/detail metadata, close-up rollers, every recorded frame without knee arcs, both real ground demos, JSON/library/current native config and independent fixed-J1 comparison. Actual verify_inversion_native.py desktop windows pass both4001-step cases, four constraints, expected8/5shapes and graceful exit0. Current default dual-rope k=7882.991939N/m; first flip at.316750s with.25ms and.316875s with.125ms. Retained35mm session spacing also flips at.313500s with central_face and k=7051.275905N/m. Actual app-local CMD stop/start/restart/reuse from C:/Windows preserves port4186. In-app main preview is refreshed and visually checked with remembered35mm inputs retained; latest browser PNG includes the central route and enlarged diagram. Python/JS syntax, edited Markdown links/fences and diff hygiene pass; fetched-base working/publication/staged checks run before push. Raw results/logs/screenshots/environments remain ignored.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. An initial test-line indentation caused a syntax error in the scoped unittest command; it was corrected before the passing18-test rerun, with original tolerances retained. A documentation patch did not match its context and applied no changes; targeted edits then updated the actual source text. Current ground first-flip time refines, but one-second undamped post-impact angles100.236/78.066/59.588deg at.5/.25/.125ms have not converged well, and contact peaks/later bounce are qualitative. Actual model/validation docs disclose the full table, rather than claiming settled pose or quantitative impact accuracy. Geometry omits axle/groove/rope-crossing/3D package clearance, stretch, friction and binding; parts are massless, chassis pitch held, and no controller/pose hold is added. Fixed-J1 comparison has no floor, MATLAB remains legacy-tip-only, and older broad envelope/browser evidence keeps its historical scope.

## 4. Compute Saving Handoff State

Current dual ropes feed through the centre gap and flare over the small rollers onto knee face anchors, with no outer-rim wrap in main, close-up or native views.
The one-cap solver uses actual cable inventory and lead-angle tension projection; both default and remembered35mm configurations flip under real femur torque, while saved prior profiles/frames remain reproducible.
Continue from the corrected invertible model/validation docs, preserve existing records and session numbers, interpret post-impact ground peaks cautiously until refined, and restart with Start Motion Lab.cmd at port4186.

---

## Entry: 2026-10-11 — Andy Zhang — tight wrapped ropes and knee-right inversion demo

## 1. Scope & Objective

- **Target Subsystem:** Invertible suspension transmission, angle limits, live/debug UI and data.
- **Associated Issue/Task:** User requested much tighter rollers, an angle-limited above/below-chassis demo with the knee staying on the right, then clarified that the cables must wrap around the knee pulley. The latest wrap clarification supersedes the earlier no-wrap interpretation.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/angle_stops.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_inversion_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/invertible-suspension.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-presets.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/unified-motion-lab.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/inversion.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/invertible_spring.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_inversion_native.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_inversion_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_angle_stops.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_inversion.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/inversion-library.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/library.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- **API/Interface Changes:** Add angle_limit_enabled/angle_min_deg/angle_max_deg to inversion configs; default |theta|45 and ±80 degree limits. Pymunk adds a real RotaryLimitJoint (five constraints), records signed averaged stop torque and fails runs crossing the knee to the left rather than clipping poses. Independent SciPy uses new angle_stops.py event integration, inelastic impact energy, held-stop reaction and release under inward acceleration. Defaults use400iterations to preserve the guide error budget. Add cable lead angle, stop torque and math impact-loss units/channels; physical mechanical_energy_minus_work_J explicitly includes unisolated constraint losses instead of claiming a closed stop-energy ledger. New central_wrap mode uses centre-fed roller tangents, common tangents and knee-rim arcs, with no straight span through pulley material; rim length and ±R angular derivative affect the one-cap inventory, tension and physical force sites. Current editable demo drum30mm/gap0.2mm/eyes±0.02mm fits existing120mm coil/rod and100mm eye mount; infeasible40mm wrapping travel is rejected. Current session migration adopts requested roller/pose/wrap settings while retaining unrelated dimensions/input fields. Original saved central_face/outer_rim profiles and frames retain reproduction, including explicit unrestricted angles for old profiles without stop metadata. UI shows derived gap that stays fixed during roller-radius edits, bounds, real wrap/stop indicators, alignment/stop readouts and ten Plotly charts. Native renderer uses computed paths and tracks every-step knee-right/bounds; original JSON/frames are not rewritten and absent historical channels are not fabricated. Update model/context/preset/workflow/validation docs and the root run-saved label. No canonical assets, shared runtime, dependencies, enforcement or original archives are changed/deleted.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All23 scoped Python tests pass (test_inversion, test_angle_stops, test_replacement_suspension, test_setup_preview). They verify actual knee-rim arcs/tangents, disk clearance, full cable inventory/slack, force-site virtual work and energy gradients, projection, impossible travel, archived no-wrap/outside routes, real above/below ground flips, right-side knees, stop reactions, independent impact/hold/release including zero-force rest without chatter, energy and low-load refinement. All63 JavaScript tests pass with old/new route/profile handling. Actual verify_inversion_ui passes wrapped main/detail geometry, tight gap, initial/bounds indicators, both presets, all recorded knees right, ten Plotly charts, portable JSON/library/current native envelope and fixed-J1 comparison. Actual verify_inversion_native.py passes both4001-step desktop windows with five constraints, expected8dual/5bell shapes, owned handles, every-step angle/knee-right checks and graceful exit0. Current dual k10848.294N/m, peak compression94.761mm/remaining coil25.239mm, maximum cable lead0.244deg and guide error3.35e-9rad. Dual first wheel-below times at.5/.25/.125ms are.3575/.3605/.36075s; final1s angles44.187/42.779/42.487deg. Reversed normal-start pulses reach wheel-above at.24175s dual/.23650s bell, with positive knee-right margins; bell wheel-below remains.39725s. Matched fixed-J1 half-second max angle deltas1.38600/.78804deg and math energy residuals4.62e-4/1.13e-5J retain the actual impact scope. App-local CMD start/stop/restart/reuse from C:/Windows preserves127.0.0.1:4186. In-app session migration, wrap preview and actual run are verified. Syntax/compilation, edited Markdown links/fences, diff hygiene and fetched-base working/publication/staged checks run before push. Raw runs/logs/screenshots/environments remain ignored.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. Initial stop impacts exceeded the old1e-8rad guide budget at100iterations;200/300 improved it but still missed, and400passes without loosening it. The intermediate 1mm/no-wrap bounded demo is documented as superseded after the user's rim-wrap clarification. Wrapping the40mm drum exhausted the existing mount travel, so the clearly editable30mm demo drum is used rather than clipping cable motion or inventing coil capacity. Small numerical angle-stop overshoot and timestep-dependent rigid-contact peaks remain in real data; runs crossing left fail. Shortest ideal cable paths permit lift-off/contact-branch changes and omit captured groove/winding history, cable diameter/fit, stretch/friction, stop compliance,3Dclearance and actual actuator ratings. Chassis pitch remains held; this is not whole-vehicle self-righting, a hidden controller or a settled-pose guarantee. Math ideal impacts have no finite instantaneous peak torque; Pymunk reports impulse/dt. High-torque impact comparisons do not inherit the separate low-load.1deg claim. Older broad audits and unchanged MATLAB support remain historical/legacy-tip-only.

## 4. Compute Saving Handoff State

Current dual ropes feed through a0.2mm ideal roller gap and wrap the30mm knee drum through real tangent/rim geometry, with one shared cap and nearly axial pull.
Both new mechanisms use editable±80deg real stops and start at45deg magnitude, keeping the knee right while real femur torque moves the wheel above/below the chassis; independent math models matching rigid stops and impact loss.
Continue from the latest invertible model/validation records, preserve archived profiles/data and unrelated settings, refine contact timestep before interpreting peaks, and restart with Start Motion Lab.cmd at port4186.

---

## Entry: 2026-10-11 — Andy Zhang — unloaded fully contracted dual-rope reference

## 1. Scope & Objective

- **Target Subsystem:** Member invertible suspension cable geometry, conservative spring law and browser/native profile handling.
- **Associated Issue/Task:** User corrected the rope attachments to the cylinder-facing left side when the links are parallel, requesting no spring force at full contraction. Retain actual knee-rim wrap, tight rollers and knee-right limits.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_inversion_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/invertible-suspension.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/inversion.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/invertible_spring.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/native_viewer.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_inversion_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_inversion.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/inversion-library.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/library.js`
- **API/Interface Changes:** Add rope_neutral_pose=folded/straight. Current dual ropes use anchors phi+pi±delta and full cable inventories at theta0; default preload0 gives compression/cap force/tensions/energy/torque0 there. Opening either way compresses the common cap and produces closing torque in both solvers and native drawing. Rod default130mm keeps its eye outside the unloaded120mm coil. Bellcrank retains10mm preload and original behavior. Current dual auto_rate matches gravitational torque magnitude at the calibration pose, explicitly not signed gravity equilibrium; label and equations follow the selected reference. Permit initial angle0 for reference studies; invalid inverted floor overlap remains rejected. Browser/Python saved-profile resolvers preserve missing-marker historical straight phase/preload/rod without mutating original records. Current session migration changes phase/preload and old demo rod only; unrelated controls remain remembered. Update tests, model/context/validation docs and unloaded/slack labels. No canonical model, shared runtime, dependency, enforcement, archive or stored original run changes/deletions.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All25 scoped Python tests pass via .venv/Scripts/python.exe -m unittest -q test_inversion test_angle_stops test_replacement_suspension test_setup_preview. Tests include exact unloaded contraction and real stationary Pymunk/SciPy rows, left-side offsets, opening-force sign, archive reproduction, cable inventory/slack, conservative energy/force-site virtual work, low-load timestep refinement, both actual ground flips, and separate200Nm stop cases. All63 JavaScript tests pass with native/library phase/default compatibility. Actual node scripts/verify_inversion_ui.cjs passes final source/server: session migration with custom0.7kg femur retained,130mm rod/zero preload, zero-degree unloaded preview and left anchors, current rim geometry, both flips, ten Plotly plots, portable JSON/library, tab memory, native request envelope and matched fixed-J1 comparison. Actual .venv/Scripts/python.exe scripts/verify_inversion_native.py passes both4001-step desktop windows with five constraints,8/5shapes, every-step right-side knees/angle bounds and graceful exit0. Current dual k13542.156N/m, default peak compression40.270mm/remaining coil79.730mm, lead below0.095deg and guide error4.89e-15rad. First wheel-below at.4195/.4190/.4190s with.5/.25/.125ms; undamped1s angles-18.285/-18.436/-18.400deg show rebound. In-app migrated preview and actual4001-sample run are verified, with new flip time. Actual project-local CMD stop/start/restart/reuse from an unrelated directory responds at127.0.0.1:4186 with folded/zero-preload backend defaults. Edited Python AST, JavaScript syntax, Markdown links/fences and diff hygiene pass. Fetched-base working/publication/staged checks run before push; raw screenshots/configs/frames/logs stay ignored.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. An intermediate zero-preload profile failed existing120mm-rod eye clearance; explicit130mm demo rod restores clearance without relaxing validation. A relative-path edit command ran from the launcher-test directory and found no source, made no changes, then was rerun from the app directory. Initial browser rendered-status wait timed out during shared-solver busy responses; the harness waits for a non-busy math API result and final browser runs pass. Initial migration seeding before reload was overwritten by the existing pagehide saver; one-shot document initialization verifies real migration while preserving custom mass. No numeric tolerance was loosened. Exploratory300Nm/default-step runs overshot the80deg stop by1.061deg and exceeded the1e-8rad guide budget; they are not accepted accuracy evidence. Validated default100Nm and separate200Nm fixtures do not certify arbitrary edited inputs. Normal ride gravity and this closing spring may act in the same direction, so magnitude calibration is not passive height support. Shortest ideal routing, cable diameter/groove/winding/3Dfit, compliant impacts and real actuator hardware remain unverified. Earlier wide audits and MATLAB retain historical/legacy-tip-only scope.

## 4. Compute Saving Handoff State

The current dual-rope preset is unloaded at full contraction, with left-facing anchors and full cable inventory referenced to theta0; both actual solvers and the native renderer share this corrected law.
Opening compresses the coil and produces closing torque, while saved old profiles/frames retain their original straight-phase law and current unrelated settings remain remembered.
Continue from the latest invertible model/validation docs, preserve prior records, refine edited high-torque impacts before interpreting peaks, and restart with Start Motion Lab.cmd at port4186.

---

## Entry: 2026-10-11 — Andy Zhang — revert unloaded contraction correction

## 1. Scope & Objective

- **Target Subsystem:** Member invertible suspension model and preview.
- **Associated Issue/Task:** User explicitly withdrew the last change (1ecff9f), saying it was wrong. Restore the preceding7bbbceb model while preserving tight rollers, knee-rim wrap and right-side angle limits.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_inversion_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/invertible-suspension.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/inversion.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/invertible_spring.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/native_viewer.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_inversion_ui.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_inversion.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/inversion-library.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/library.js`
- **API/Interface Changes:** Restore the15 app paths changed by1ecff9f to7bbbceb, with focused browser session rollback and updated context/validation notes. Remove the temporary rope_neutral_pose model field,180deg phase shift,zero-preload contraction reference and magnitude-only calibration. Restore phi±delta anchors,phi=pi inventory,10mm preload,120mm rod, original initial-angle limits and signed gravity calibration. Model, native bridge/debugger and library sources are byte-identical to7bbbceb. At browser startup, remove the temporary neutral marker, restore reverted demo preload/rod/zero-angle values, and preserve unrelated controls. Existing contribution entries remain byte-for-byte; no history reset/force push, data rewrite or file deletion. Temporary folded runs remain historical JSON/frames; reproducing their removed solver configuration requires its historical Git revision. No canonical/shared component, dependency, asset or enforcement changes.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All23 scoped Python tests pass via .venv/Scripts/python.exe -m unittest -q test_inversion test_angle_stops test_replacement_suspension test_setup_preview. All63 JavaScript tests pass with npm test. Actual node scripts/verify_inversion_ui.cjs passes added folded-session rollback assertions (10mm preload,120mm rod,45deg start,neutral marker removed,custom0.7kg femur preserved), then the original two ground flips, actual wrapped diagrams, ten Plotly charts, JSON/library/tab memory/native request envelopes and fixed-J1 math/Pymunk comparison. Five core/model/native/library files are byte-identical to7bbbceb, and changed Python AST/JavaScript syntax, Markdown links/fences and git diff hygiene pass. Actual app-local CMD stop/start/restart/reuse from an unrelated directory verifies restored backend defaults at127.0.0.1:4186. In-app controls show restored10mm/120mm/k10848.294N/m and the actual run is verified. Fetched-base working/publication/staged checks run before commit/push; raw evidence remains ignored. Previous native-window evidence belongs to7bbbceb and is not rerun or relabeled as a new desktop test.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. This rollback restores a previously tested experimental model, not a hardware baseline. Existing limitations in cable winding/groove/contact history, rope diameter/fit,3Dclearance, fixed chassis pitch and timestep-dependent rigid impacts remain. Original saved records are preserved; the withdrawn folded variant is not silently rerun as another model. Previous failures remain in the append-only contribution history.

## 4. Compute Saving Handoff State

The user withdrew the unloaded-contraction correction, and current mechanics again match7bbbceb with wrapped cables, tight rollers and knee-right stops.
Browser session migration restores only the reverted demo values and strips the removed field while preserving unrelated inputs and all stored recordings.
Continue from the restored model/current rollback validation note, preserve append-only history and original data, and restart with Start Motion Lab.cmd at port4186.

---

## Entry: 2026-10-12 — Andy Zhang — label invertible pulley design impossible

## 1. Scope & Objective

- **Target Subsystem:** Wheel Leg Lab dual-rope design status and documentation.
- **Associated Issue/Task:** User explicitly requested commit/push and the label impossible for the invertible pulley design. Apply it to the dual-rope knee-pulley proposal, preserving its source and historical data.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_inversion_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/invertible-suspension.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/suspension-presets.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/inversion.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/inversion/index.html`
- **API/Interface Changes:** Label the dual-rope preset IMPOSSIBLE/archive in both wheel-model selectors and the inversion selector. Add a dual-only status notice inside the preview/recorded mechanism panel; the symmetric knee bellcrank is not labeled impossible. Native dual-rope caption/onscreen status and fresh dual-rope run/preview scope text mark the historical ideal simulation. Update app README, model/preset/validation notes and app/web context, attributing the status to the user's2026-10-12 decision. No failure explanation/proof is invented. Preserve backend/config IDs, mechanics, units, defaults, algorithms, recorded values, saved profiles/frames, source and archives. No shared component/asset/enforcement change or file deletion.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** JavaScript syntax checks pass for web/app.js and web/inversion/app.js; edited Python AST and Markdown link/fence checks pass. Solver-function AST comparison against fetched origin/main confirms config/build/step/coordinates/simulate and other mechanics functions unchanged; only package/preview human status text differs. Actual scoped Playwright rendering check passes dual-only visible IMPOSSIBLE banner and preset label, bellcrank exclusion, and the Math/Physical wheel selectors; no dynamics run. Ignored screenshot evidence is artifacts/inversion-ui/impossible-status.png. Actual API previews show the dual-only status and zero solver steps; bellcrank scope has no impossible label. Actual app-local CMD start/stop/restart/reuse from an unrelated directory passes at127.0.0.1:4186. The in-app preview is refreshed and the impossible label visibly verified. Fetched-base working/publication/staged checks run before commit/push, with hooks enabled. This is a status-only update: numerical physics suites and native windows are not rerun, and prior test evidence is not treated as physical feasibility approval. Raw screenshots/logs/environments remain ignored.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

An initial diff-hygiene check reported trailing blank lines in three app docs; they were removed and the final diff check passes.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. Impossible is the user's design disposition, not a new independently derived theorem or hardware test result. The retained ideal numerical model can still run for reference; its earlier successes do not override the rejected physical design. Existing geometric/rope-winding/contact/3Dfit and hardware limitations remain in the source records.

## 4. Compute Saving Handoff State

The dual-rope invertible knee-pulley design is labeled IMPOSSIBLE in the browser/native viewer and documentation, with its idealized simulation retained as history.
The symmetric knee bellcrank and ordinary2:1guide are separate, while numerical mechanics, saved records and backend IDs remain unchanged.
Continue from the latest status note without treating historical numerical passes as buildability evidence, preserve source/data, and restart with Start Motion Lab.cmd at port4186.

---

## Entry: 2026-10-12 — Andy Zhang — wheel/link sizing and torque sweep

## 1. Scope & Objective

- **Target Subsystem:** Motion Lab member wheel/link calculator.
- **Associated Issue/Task:** User requested configurable wheel-based lift, extension/preload and compression/clearance buffers, degree/mm conversion at an entered link length, and link/angle sweeps comparing average and peak torque. User confirmed200mm radius /400mm diameter /200mm nominal lift.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/link-sizing.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/build_animations.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_link_sweep.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/link-sweep.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/force-plots/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/force-plots/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/force-plots/link-sweep-model.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/force-plots/link-sweep.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/force-plots/link-sweep.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- **API/Interface Changes:** New app-local analytical calculator, served directly at /force-plots/, preserving the existing constant-torque study and solver APIs/data. Equal-link2:1guided geometry uses foldqfrom downward vertical,theta=90deg−q. Buffers are minimum unused height/angle reserves,customROMmay be mm/degrees,nominal lift tracks radius. Chassis depth/minimum air gap enforce independent flat-ground clearance. Enumerate lengths/start placements including limiting endpoints; reject malformed/nonfinite/oversized searches. Exact uniform-travel or uniform-angle mean/RMS/CV,peak/minimum hip-equivalent or half-sized relative-knee torque; separate magnitude/flatness rankings,winner cards,Plotly,selected geometry/reference-link inspection,all-candidate CSV. Calculator-specific motion-lab-link-sweep/v1JSON and session/study memory remain separate from solver profiles/recordings. No shared interface,asset,dependency,enforcement or agent rule changes. Default20mm reserves/gap,200mm chassis depth and100Nnet load are explicitly demo assumptions; spring preload/assistance and link weight/dynamics are not invented.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** npm test passes70tests including seven sizing checks against existing linkage Jacobian,finite height derivative,work conservation,knee scaling and20,000-point independent quadrature for both weightings; unit roundtrips,clearance/ROM/buffer feasibility,exact endpoints,ranking/tradeoff and malformed/infeasible searches pass. node scripts/verify_link_sweep.cjs passes actual standalone/embedded browser controls,custom degreeROM,conversions,coordinates/weightings,selection/objectives,ground-gap enforcement,empty search/no stale selected export,CSV/JSON import/export,refresh/study memory,Plotlyzoom/dark,360pxlayout,local-only assets and zero browser errors. Existing node scripts/verify-force-plots.cjs passes its complete original analytical/UI/animation suite. npm run build passes Vite/gallery. Actual project-local CMD stop/start/stop/restart/reuse from unrelatedcwd verifies sizing page/model at127.0.0.1:4186; retained launcher has readable failures and independent installed runtimes. JavaScript/Python syntax,Markdownlinks/fences and diff hygiene are checked before publication; fetched-base working/publication/staged checks run with hooks enabled. Ignored raw screenshots/exports/logs remain local. Python/native/dynamic wheel solvers are unchanged and not rerun; no hardware/canonical physics claim.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member analytical workspace. A browser rerun caught millimetre conversion rounding excluding an exact feasibility endpoint; precision handling was fixed and the full sizing browser suite then passed. Initial sampled100Nhip example finds120mm links for minimum peak23.9165N m/mean19.5773N m,while600mm boundary links minimizeCVwith119.9833N mpeak. These are scoped sample optima,not hardware selections. Spring law/preload,distributed link weight,dynamics,speed/strength,tire/terrain effects and real3Dclearance remain unverified; preserve prior physics failures and historical records.

The first commit attempt stopped before committing because the hook's default python3 resolved to the Windows Store alias. Retry uses the existing supported CAMEL_PYTHON environment override pointing to installedPython3.13,with the normal hooks enabled; no hook or enforcement change/bypass is made.

## 4. Compute Saving Handoff State

Motion Lab's wheel/link calculator now sweeps configurable equal-link lengths and angle windows for the confirmed200mm-radius/200mm-lift starting case, with degree/mm reserves and independent chassis air gap.
Exact constant-net-load torque statistics separate minimum peak/mean from flatness, with candidate inspection,CSV/configJSON and remembered inputs; original mechanics and solver data remain unchanged.
Continue from docs/link-sizing.md and the latest validation, enter real load/chassis/spring constraints before selecting hardware, refine boundary winners, and restart with the actual app-root Start Motion Lab.cmd at127.0.0.1:4186.

---

## Entry: 2026-10-12 — Andy Zhang — portable app context and laptop development handoff

## 1. Scope & Objective

- **Target Subsystem:** Andy's experimental apps, development history archive and cross-machine setup.
- **Associated Issue/Task:** User requested confirmation that Capstone apps/development history/context.md files live in member experimental-app folders, plus a prompt to pull the repository and continue development on a laptop without the PC.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/README.md`
- `users/andy-zhang/experimental-apps/context.md`
- `users/andy-zhang/experimental-apps/laptop-handoff.md`
- `users/andy-zhang/experimental-apps/capstone-archive/README.md`
- `users/andy-zhang/experimental-apps/capstone-archive/context.md`
- `users/andy-zhang/experimental-apps/capstone-archive/development-history-2026-10-12.json`
- `users/andy-zhang/experimental-apps/capstone-archive/restore_development_history.py`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/README.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/context.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Start-Capstone.ps1`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Stop-Capstone.ps1`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Start Terrain Atlas.cmd`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/Stop Terrain Atlas.cmd`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context.md`
- **API/Interface Changes:** Add root context.md for all three actual member apps and an umbrella context/history index plus verified clone/setup/continuation prompt. Preserve original context folders,model/decision/validation/handoff records,full Git history and canonical/shared repository layout. Audit confirms apps already colocated; no source/root move or deletion needed. Add independent capstone-historical-source/v1JSON supplement with21previously ignored source/Markdown research/editing/QA files,86,103original bytes,relative paths,base64,size/SHA-256,and standard-library restore to a new directory; never execute payloads and leave original668-file archive untouched. Raw current solver output/caches/process/account data stay local; browser JSON transfer is documented separately. Atlas startup discovers installedNodeonPATH and scoped stop validates its recorded executable/PID/time/app/Vite/port. New Start/Stop Terrain Atlas.cmd wrap standalone4175helpers; familiar Capstone/ForcePlotsaCMD aliases still target Motion Lab4186. Update helper readiness/stop messages to name the correct standalone launchers. Existing state format remains compatible; no physics/model/dependency/shared asset/interface/enforcement/agent rule changes.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** New full GitHub clone at2353a6f reproduces all40commits; local branches have zero unpublished commits outside origin. No copied app dependencies: fresh npm ci/build succeeds for both apps,all70MotionLab and49AtlasJS tests pass; newly createdMotionLabvenv installs all pinnedPythonpackages,pipcheckreports no broken requirements,and server/physical/math/inversion modules import. Fresh-cloneMotionLab independently passes real app-local CMD start/stop/restart/stop at its supported alternate4175port and returns sizing page/identity; the existing main4186server remains untouched. Updated actual canonicalAtlasCMD passes start/scopedstop/restart/reuse from unrelatedcwd atoriginal4175withall three production-route readiness checks; its proper launcher messages are verified afterward and Atlas is left running. Original103-part archive restores668files exactly from the freshclone; four ignored large terrainPDF/CSVinputs and six historical research/export sources match archivehashes. Supplemental21files restore with exactbytes/SHA-256,match untouched localoriginals,and reject an existingdestination without overwrite. LocalCapstoneOld remains present. MarkdownURL-decoded links/fences,PythonAST,PowerShellparser and diffhygiene pass. Fetched-base working/require-passed/scoped/staged publication checks run with normal hooks and installedPython via supportedCAMEL_PYTHON. New laptop/otherOS/native/GPU/MATLAB/canonicalphysics are untested; prior verification retains its scope. Temporary clone/restored files/environments/builds remain ignored under app-local .local-data; no payloadsource executed or originaldeleted.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this member workspace/context/archival contribution. An initial ad-hoc Markdown check treated existing percent-encoded space links as literal paths; URL-decoding corrected the harness and the final link check passes, with no source-link change required. A launcher review caught old stop/restart text pointing at CMD aliases that now target MotionLab; messages now name Start/Stop TerrainAtlasand lifecycle/restart is verified. Archived helper scripts are frozen historical evidence with obsolete edits/paths possible,not maintained runnable modules or new validated simulations. The public repo carries engineering context and history,not private Codex chats or automatic browser storage synchronization.

The initial staged diff-hygiene check flagged Windows CRLF in the newly generated supplemental JSON container. Its container was normalized to LF and the staged diff check passes; base64 payloads and all21original source hashes are unchanged.

## 4. Compute Saving Handoff State

All three published Andy apps remain under users/andy-zhang/experimental-apps with context.md entry points,linked original development records and a portable laptop setup/continuation prompt.
Fresh clone/build/dependencies,119JavaScript tests,668original and21supplemental file restorations and independent app launcher lifecycles pass here; actual laptop and otherOS validation still belong to that machine.
On the laptop pullmain and read experimental-apps/context.md then laptop-handoff.md,keep current200mm-radius sizing and rejecteddual-rope status,preserve shared records,import any wantedbrowserJSON,and publish future validated changes through the existing scoped protocol.

---

## Entry: 2026-10-12 — Andy Zhang — actual laptop development environment

## 1. Scope & Objective

- **Target Subsystem:** Andy's Motion Lab and Terrain Atlas member workspaces.
- **Associated Issue/Task:** Reconstruct the complete development environment on the owner's laptop, verify original localhost routes and restart, preserve current sizing/model decisions, and publish validated setup context to main.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/laptop-handoff.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/model.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/context/README.md`
- `users/andy-zhang/experimental-apps/terrain-mobility-atlas/docs/VALIDATION.md`
- **API/Interface Changes:** None. Record actual laptop reconstruction and continuation in existing app context/history. Correct stale Atlas context to Start/Stop Terrain Atlas.cmd and stale current replacement-suspension prose to damping zero. Existing source/defaults, manifests/lockfiles, launcher contracts, rejected dual-rope IMPOSSIBLE status, rollback, position input and 200 mm radius / 400 mm diameter / 200 mm lift sizing remain unchanged. Installed runtimes, venv, node_modules, generated assets, process state/logs and raw QA exports stay local; no machine-specific paths, copied PC environment or boot automation enter Git. Existing repository hooks are installed locally, with persistent supported CAMEL_PYTHON override selecting installed Python 3.13.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Empty laptop Capstone directory receives non-shallow full clone at c6a79b5 (41 commits), main tracking origin/main; git fsck --full passes. Windows 11 Home x64 detected. Signed official Python 3.13.12 installer succeeds; official Node 22.23.3 Windows ZIP SHA-256 matches release manifest; npm 10.9.9 and fresh Windows CMD runtime resolution verified. Setup Motion Lab.cmd installs pinned Python packages, npm ci and both local builds pass, pip check passes, Motion Lab 70 plus Atlas 49 JavaScript tests pass, both npm installs report zero audit vulnerabilities. Motion browser sizing/force/portable/unified suites pass; Atlas verify_import.cjs passes controls, measured-USGS worker run, finite plots, mobile workbench and linkage route; desktop map capture confirms outlines/cells with no page errors. Native debugger headless check steps Pymunk and renders three shapes/six constraints. Both real app-local CMD start/scoped-stop/restart/reuse workflows pass at original 4186/4175 from outside app directories; listener disappearance and laptop-root/server identity verified. Markdown local links/fences and diff hygiene pass. Fetched-base working/require-passed/scoped/staged publication checks use normal hooks and installed Python; detailed app test evidence stays with each app.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member setup/context contribution. The first unified browser check timed out waiting for a mathematical recording while restart verification overlapped it; the stable-server rerun passes unchanged, without relaxed assertions/timeouts. PowerShell's bare python can resolve an existing Cygwin extensionless file; Windows CMD resolves installed Python 3.13 and hooks use supported CAMEL_PYTHON, with explicit python.exe / py -3.13 / app venv commands documented for PowerShell. No hardware, MATLAB, visible native-window, GPU or other-OS certification is claimed; experimental numerical checks do not validate a canonical robot.

The first working-tree entry check rejected Windows CRLF in the contribution log. Normalizing its working copy to repository LF preserves the entire previous log as an exact byte prefix; final checks use the existing enforcement unchanged.

The next working-tree checks exposed the same fresh-clone CRLF conversion across untouched tracked text, falsely classifying shared runtime as changed and invoking the missing-canonical-robot gate. Set this clone's core.autocrlf=false and normalized only Git-index LF text files to LF, preserving contents and the exact seven-path Git diff. Enforcement, assets and shared runtime source remain unchanged; rerun the actual workspace checks rather than bypassing them.

Full Motion Lab .venv/Scripts/python.exe -m unittest discover -v passes all 139 tests in 578.836 seconds, including the 108-backend-case six-second passive envelope and independent solver refinement. Minimum prescribed support is 49.65184 N in that tested envelope; these are member fixture/model checks, not real unilateral contact or hardware validation. Complete raw test logs remain ignored under .preview.

## 4. Compute Saving Handoff State

The laptop now has a full-history main checkout, installed Python 3.13.12 and Node 22.23.3/npm 10.9.9, separate rebuilt app dependencies and enabled repository hooks.
Motion Lab at 127.0.0.1:4186 and Atlas/workbench at 127.0.0.1:4175 remain running locally with verified manual restart and no desktop dependency.
Continue from the 200 mm radius/400 mm diameter/200 mm lift sizing tool with editable degree/mm buffers and ROM, preserve IMPOSSIBLE dual-rope and undamped position-input decisions, and read the updated laptop/app validation context before the next development request.

---

## Entry: 2026-10-12 — Andy Zhang — wheel-centre angles and individual torque curves

## 1. Scope & Objective

- **Target Subsystem:** Motion Lab wheel/link analytical sizing study.
- **Associated Issue/Task:** User requested upward angles from wheel-centre horizontal, individual profile torque curves, peak/ranking explanation and a torque-versus-travel metric; user clarified the existing equal-link 2:1 hip-to-knee guide.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/link-sizing.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_link_sweep.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/link-sweep.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/force-plots/link-sweep-model.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/force-plots/link-sweep.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/force-plots/link-sweep.css`
- **API/Interface Changes:** App-local theta display points upward from wheel-centre horizontal, complementary to retained internal q. Wheel-centre horizontal references/arcs, table/cards/hover angles and explicit link/actuator ROM preserve existing geometry and buffer conversions. Individual curves compare each length's best window, top30 or distinct winners; selected profile highlighted/clickable, large plots explicitly disclose300 evenly spaced samples. Add ideal work, actuator ROM and usable-lift/RMS torque metrics, fourth lift ranking and named CSV columns. v1 config remains compatible with old inputs; new lift objective requires updated calculator. Direct hip actuator torque remains2FLcos(theta), relative knee FLcos(theta), with twice knee angular motion and equal work; no unspecified extra gearing is invented. Fix diagram radius padding so wheels are not clipped. No shared interfaces/assets/dependencies/rules, native/dynamic models or rejected dual-rope decisions change.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** npm test passes72cases; new independent geometry/endpoints/virtual-work, exact feasibility/peak and lift/RMS ranking checks pass. Existing sizing browser suite passes upward theta/reference origins/arcs,97individual default curves, curve selection, top30/winners, disclosed300-profile sampling, fourth objective, coordinates/averages, conversions/ROM, clearance, JSON/CSV, refresh/study memory, Plotly zoom/dark and360pxlayout with no errors/external requests. Existing verify-force-plots.cjs passes original force/Jacobian/control/animation/UI suite. npm run build and JS syntax pass. Actual app-root Stop/Start Motion Lab.cmd restart and reuse from unrelated working directory verifies updated source and health at original4186. Angle/curve captures were visually inspected; ignored raw exports/screenshots stay local. Markdown links/fences, diff hygiene and fetched-base working/require-passed/scoped/staged checks use installedPython3.13 and normal hooks before publication. Source/default200mmradius/400mmdiameter/200mmlift and dynamic model decisions remain unchanged.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member analytical workspace. First browser rerun caught an outdated text assertion for custom35degreeROM after the UI explicitly separated link/actuator ROM; the assertion now checks both values and the full suite passes unchanged tolerances/timeouts. Visual QA found the end wheel clipped at the SVG top; radius padding fixes the retained geometry display. Lift/RMS is a dimensionful travel/torque score, not energy efficiency; both hip/knee do20J in the100N/200mm demo despite different torque/speed. Python/native/whole-robot/hardware/GPU/MATLAB are unchanged and not rerun for this analytical update.

## 4. Compute Saving Handoff State

Sizing angles now point upward from wheel-centre horizontal, with individual profile torque curves and a lift/RMS ranking at the same4186route.
The current demo still selects120mmlinks for minimum peak/mean/RMS, with hip23.91652Nmpeak and19.96664NmRMS, half knee torque and twice knee angular ROM by virtual work.
Continue from docs/link-sizing.md with real load, spring, motor-speed/duty and clearance constraints, preserve rejected dual-rope/undamped position-input models, and refresh or restart with Start Motion Lab.cmd.

---

## Entry: 2026-10-13 — Jonathan Xie — General VSL Solver v1 kinematics

## 1. Scope & Objective

- **Target Subsystem:** Jonathan Xie's isolated leg-solver member app.
- **Associated Issue/Task:** User requested a self-contained interactive HTML solver in the member experimental-apps folder, with tunable geometry/belt ratios, motion, plots and wheel rotation for a locked drive input. User explicitly confirmed three open belts, b attached to tibia, independent d/e and proximal link angle vectors. Work is saved locally; no hosting, commit or push requested.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/jonathan-xie/experimental-apps/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v1-kinematics.html`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-kinematics.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver.cmd`
- **API/Interface Changes:** New dependency-free, browser-local standalone HTML; all solver/style/UI code embedded. Positive pitch radii/mm and degree inputs; driven ratio/dimension triplets and swaps; angle sliders; animated exact open-belt tangent/wrap geometry with material dots, wheel and dotted foot path; all live angles and local/global displacement/stroke; full-domain angle/displacement plots with working-range boundaries, hover and series toggles. Derived locked-input coefficient K = 1 - q_ab + q_ef(q_ab - q_cd); signed endpoint strokes distinguished from sampled interior extrema. JSON general-vsl/v1-kinematics parameter import/export and metadata-bearing sweep CSV. Windows launcher opens the adjacent static HTML without a server. No shared assets, interfaces, dependencies, runtime or agent rules changed.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** node verify-kinematics.cjs passes 3,838 assertions, both embedded script syntaxes, independent closed-form geometry, three carrier constraints over 60 ratio combinations, finite-difference sensitivities, frame/length invariants, zero-spin degeneracies, exact belt lengths, boundary continuity and rigid surface material velocities on both wraps. Actual in-app browser static-HTTP preview verifies SVG/plots, all four triplet driven dimensions, exact one-selection behavior, swap, decimal key-by-key typing, angle sliders/manual inputs, invalid/reversed/zero-width ranges, overlap notice, wheel spin/cancellation, displacement reference resets, pause/play and scrubbing. CSV/JSON downloads and JSON reimport pass; CSV has 901 finite demo rows, exact extension zeros and 435.593224745812 mm endpoint travel. Screenshot inspected, no browser warnings/errors. Decimal typing and coincident axis-label issues found in browser QA are fixed. Both repository structure/handoff checks (including --require-passed) pass with 524 files, 7 changed paths and workspace scope; the scoped gate reports physics NOT APPLICABLE; git diff --check and six app Markdown links pass. Initial checks exposed clone CRLF conversion: normalize index-LF text checkouts/log to LF and local core.autocrlf=false, preserving all text and the full prior Git log prefix. Final Git diff remains only seven intended paths; no enforcement or canonical source change. Canonical physics is not applicable.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member analytical app. Direct file-URL navigation is blocked by the browser tool's HTTP/HTTPS-only policy; no bypass was attempted. Offline file opening and the .cmd launcher are not claimed as browser-verified; static HTTP checks exercised the identical standalone HTML with no network dependencies. Mobile layout, hardware, manufacturing teeth/wrap, spring/forces/torques, collisions and wheel/ground rolling remain unverified. Envelopes/graphs use finite sampling and disclose that limit. Other members' work is preserved.

## 4. Compute Saving Handoff State

General VSL Solver v1 is saved locally in the requested member app folder, with standalone HTML, model notes, Windows file launcher and numerical checks.
The confirmed proximal angle convention reproduces the downward 2:1 straight path; locked-input wheel spin depends on K, while signed h values and sampled interior envelopes remain distinct.
Open v1-kinematics.html manually in a browser, save parameter JSON for studies, preserve v1 when adding kinetics and confirm forces/spring/actuator coordinates before deriving the next version.

---

## Entry: 2026-10-13 — Jonathan Xie — Leg Solver v2 quasi-static forces and v1 travel angles

## 1. Scope & Objective

- **Target Subsystem:** Jonathan's isolated leg-solver member workspace.
- **Associated Issue/Task:** User requested live/final gamma_uv and gamma_yz in v1 and its angle plot, preserving v1 separately; a new v2 quasi-static app adds masses, prescribed wheel-contact forces, belt preload/tensions, motor holding torques, five FBDs, five mutually exclusive master sliders and nine sweeps. User confirmed atan2 angles, gravity in -z, C as wheel centre/P as contact patch and beta clockwise from -z toward front/-y. Local save workflow continues; no publication requested.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/jonathan-xie/experimental-apps/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v1-kinematics.html`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-kinematics.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-quasi-static.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/v2-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver v2.cmd`
- **API/Interface Changes:** Separate dependency-free standalone HTML versions. V1 adds atan2 travel angles (undefined at zero displacement, split curves at singularities/wraps, CSV blanks) and six-row live/final table. V2 uses exact tangent span forces and specified fixed-slack preload allocation, complete wheel-on-tibia pin reaction, all five body equilibria and independent virtual-work torque checks. C/P naming change is explicit; displacement plots retain wheel-centre travel. Mass/gravity and recorded rod/rim inertias add no dynamics; effective compound rim radius is explicit. Prescribed Fn/Ft remain independent of m1; m1 at fixed A affects chassis support only. Exclusive theta2/alpha/beta/Fn/Ft playback, editable windows, colour/intensity force and motor arrows, FBD force/rho tables, total mass, torque cards, nine current-input sweeps with signed/dashed styling and absolute option; original kinematic plots/envelope remain. V2 JSON schema includes all loads/windows/pose and accepts v1 JSON; sweep CSV includes three axes, both span tensions and force components. No shared runtime, assets, dependencies or agent rules changed. Existing v1 launcher is copied unchanged; the new v2 launcher opens its adjacent HTML.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** node verify-kinematics.cjs passes 3,853 assertions, including atan2 quadrants/extension direction and both v1 script parses. node verify-quasi-static.cjs passes 13,483 assertions across 240 varied geometries/masses/loads/poses: all five FBDs, exact tangent moment balances, tension allocation, action/reaction, whole-system support, independent numerical virtual work, preload/m1 torque invariance and fast/full sweep parity; all v2 scripts parse. Maximum force residual 9.722e-13 N, moment 3.624e-13 Nm, analytic virtual-work discrepancy 3.979e-13 Nm. Actual loopback-HTTP browser checks verify five angle curves, six live/final rows, five FBDs, nine sweeps/three desktop columns, exclusive master playback and frozen other variables, custom beta20..60 and alpha45 windows, manual current inputs, invalid windows/geometry, negative Ft, preloads, zero loads, driven triplets, finite SVGs, signed/absolute dash styling, mass updates and JSON study/pose restoration. Browser logs have no warnings/errors; desktop1600/default narrow588 layouts inspected and screenshots retained outside Git. Actual v2 CSV has1,083rows/27columns over three axes, finite numeric values, correct undefined gamma blanks, torque/preload invariants; saved JSON restores the exact study. Fourteen app Markdown links verified. Both repository structure/require-passed checks pass (528 files, 10 changed paths, workspace scope); the scoped gate reports canonical physics NOT APPLICABLE and git diff --check passes. The original envelope updates during alpha playback; v1 CSV gamma blanks/final values are checked. All nine delivered files match the requested app copy byte for byte; ZIP contents are verified.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated analytical member app. No dynamics, inertia torque, spring/damper, wheel-ground rolling, friction/contact feasibility, strength or hardware validation is introduced. Inertias are recorded only. Zero preload is an ideal limiting assumption; curves are finite-sampled and arrows cap for readability. Direct file opening/launchers remain manual and are not claimed as browser-verified because the tool permits HTTP/HTTPS only; identical static HTML is browser-tested. Construction tests caught an accidentally renamed belt-centre property, default gamma curve visibility, missing alpha caption and change-only master input handling; all are fixed and rerun, with failure history in context. The task-local documentation helper initially encountered Git's sandbox ownership check; the verified revision was supplied from the allowed repository command without changing global trust settings. No unrelated work, enforcement or Git security settings changed.

## 4. Compute Saving Handoff State

Updated v1 remains separate and functional; v2 adds the requested quasi-static load/FBD/torque/tension solver with clarified C/P and contact directions.
Motor holding torques agree with independent virtual work, all five FBDs close numerically, and the five master controls plus all eleven plots update from current inputs.
Continue from v2-model.md and app context, keep prescribed loads distinct from fixed-A sprung mass, and add passive/active spring response only in a later explicitly defined model; all work remains local with no commit or push.

---

## Entry: 2026-10-13 — Jonathan Xie — V2 loading controls and vertical-travel plots

## 1. Scope & Objective

- **Target Subsystem:** Jonathan's isolated leg-solver member app.
- **Associated Issue/Task:** User requested eight direct v2 refinements: complete theta2 master fields, belt-tension/dz headlines, switchable global and wheel force conventions, paired masters, diagram visibility, compact FBD rows, loading-versus-dz plots and angles-versus-dz. Preserve v1 and quasi-static assumptions. Local save only; no commit, push or hosting requested.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/jonathan-xie/experimental-apps/leg-solver/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-quasi-static.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/v2-model.md`
- **API/Interface Changes:** Theta2 minimum/maximum/current values sync extension/compression/pose. Alpha and beta share a row. Left Fy/Fz and right Fn/Ft columns have exclusive driving selection, preserved physical vector on switching, automatic orthogonal conversion, faded disabled derived controls and exclusive playback. All forces are signed; outward normal loads are prescribed rather than contact-feasibility predictions. Header cards show tau2/tau4, total tight-span Tab + upper/lower and dz; mass remains in sidebar. Separate figure toggles hide motor couples and driving force decomposition. FBD rows are 2/3 then 4/5/6. Twelve loading graphs add a working dz row under theta2; angle/dz joins the final three-graph row. Parametric paths preserve nonmonotonic branches, negative travel, exact fractional theta boundaries and 0/hz markers. Additive JSON schema retains old v2 support and saves loadMode/six windows/view settings. CSV now has four sweeps, 31 columns, x/x_unit, resolved force components and dz. V1 SHA256 is unchanged from the accepted prior version; no shared runtime/assets/dependencies/rules modified.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** node verify-quasi-static.cjs passes 16,044 assertions, including prior 240 varied equilibrium cases plus 91 equivalent loading-convention comparisons, signed forces, force norm/global sweep invariance, fractional endpoints, negative/reversing travel, multiple height roots and constant-height bounds. node verify-kinematics.cjs passes 3,853 assertions; all embedded scripts parse. Existing maximum residuals remain 9.722e-13 N, 3.624e-13 Nm and 3.979e-13 Nm virtual-work discrepancy. Actual static HTTP browser verification covers min/max/current theta controls, four headlines, force conversion/mode-switch torque invariance, derived control disabling, exclusive playback, visibility toggles, FBD order, twelve loading plots and three kinematic plots, negative travel and finite SVGs. Numeric current clamping displays the clamped value. JSON restores driving mode and legacy v2 files; actual exported CSV has 1,448 rows/31 columns over four sweeps, audited for finite values, resolved conversions, fixed global forces, exact dz reference/bounds and mm/deg metadata. Desktop and 390px responsive structure inspected; viewport reset, browser warning/error logs empty, screenshots retained outside Git. V1 hash unchanged; all nine delivered app files and ZIP entries match the requested folder byte-for-byte. Repository structure/require-passed checks pass (528 files, 10 changed paths, workspace scope); the scoped gate reports canonical physics NOT APPLICABLE; git diff --check and 15 local Markdown links pass. Documentation LF normalization fixes the first whitespace-check failure, preserving text and all prior log entries.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated analytical workspace. No dynamics, springs, contact/friction feasibility or hardware validation added. Height extrema/inverse branches remain sampled; zero-width axes use a display-only +/-0.5 mm pad. Static HTML was tested over HTTP; direct file opening and Windows launchers remain manual. Initial task-local helper failed on default Windows text encoding before assembling UI; explicit UTF-8 fixed it. The prior nonnegative-Fn test changed to nonfinite validation plus signed-convention equivalence, without weakening equilibrium tolerances. Prior uncommitted v1/v2 work is preserved.

## 4. Compute Saving Handoff State

V2 now supports both force input conventions and direct vertical-travel studies with all eight requested UI/layout refinements saved locally.
The driving pair controls beta-sweep semantics; switching preserves current force, while multi-valued height paths retain each sampled theta branch.
Continue from v2-model.md and app context, keep v1 separate and add suspension-response/dynamics only after a later explicit model definition; no commit or push performed.

---

## Entry: 2026-10-13 — Jonathan Xie — Collapsible v2 result sections

## 1. Scope & Objective

- **Target Subsystem:** Jonathan's isolated leg-solver member app.
- **Associated Issue/Task:** User requested arrow buttons to hide/show rows and sections beginning with FBDs. Local v2 update only.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html`
- `users/jonathan-xie/experimental-apps/leg-solver/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/README.md`
- **API/Interface Changes:** Fifteen expanded-by-default disclosure arrows for the full FBD section, five individual FBDs, four loading-sweep rows and five final result cards. Keyboard-accessible buttons expose aria-expanded/aria-controls. Hidden content remains mounted and live; the torque display option remains outside the collapsible FBD body. No parameter/export/model API changes. Both embedded solver blocks and v1 remain unchanged; existing uncommitted work is preserved.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All embedded JavaScript parses. Actual HTTP browser checks pass for all 15 collapse/reopen controls, independent FBD hiding, Enter/Space activation, continued pose updates while hidden (reopened at theta2=140 degrees), retained 21 SVGs and available torque option with FBDs hidden. Browser warnings/errors empty; screenshot retained outside Git. Solver blocks verified byte-identical; no new numerical tests needed for this reversible visibility change. Nine-file app delivery and ZIP refreshed and compared byte-for-byte. Canonical physics not applicable.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this member UI-only update. No mechanics/dynamics assumptions changed. Direct offline file opening remains manual; browser QA used identical standalone HTML over HTTP. Collapse states reset to expanded on reload; parameter saves retain their previous schema.

## 4. Compute Saving Handoff State

V2 now has arrow buttons beside result section/card titles, beginning with FBDs, and defaults to expanded.
Collapsing hides only the view, preserving current plots, values and control state for reopening.
Refresh the saved v2 HTML to load the change, continue using the existing model notes, and preserve v1; no commit or push performed.

---

## Entry: 2026-10-14 — Jonathan Xie — V2 global headline maxima at current alpha

## 1. Scope & Objective

- **Target Subsystem:** Jonathan's isolated leg-solver app.
- **Associated Issue/Task:** User requested a second equally prominent headline row for global absolute maxima, retaining torque signs. Final steering searches all theta2 × beta combinations inside their ranges with alpha fixed at its current value. Local update only.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-global-maxima.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v2-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/README.md`
- **API/Interface Changes:** New embedded VSLPeaks helper and four global headline cards under current values. Exact sinusoid beta candidates plus theta interval bounds search all combinations, targeting a 0.001-unit magnitude gap and displaying estimates if limited. Current alpha and driving forces are fixed; alpha-window bounds do not enter the user-facing search. Signed torque winners, total tight Tab/side and absolute dz include peak poses. Cached results update on relevant loads/geometry/bounds/current alpha. No existing solver, JSON/CSV input interface, shared runtime or v1 change.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** verify-global-maxima.cjs passes 29,863 assertions: formula/FBD parity, closed-form extrema, conservative domain bounds, attained poses, interior beta peaks, negative dz, preload, collapsed ranges, limit fallback, both force conventions and current-alpha-only searches. Existing verify-quasi-static.cjs passes 16,044 assertions; all embedded scripts parse. Browser verifies eight headline cards with equal 19px values, bounds/force-convention changes and torque signs; theta/beta pose movement and alpha-window changes preserve maxima, while current-alpha changes recompute them. Peak pose alpha equals current alpha, warning/error logs empty, screenshot retained. Core solver blocks verified unchanged; delivered ten-file bundle/ZIP verified byte-for-byte. Canonical physics not applicable.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated analytical app. No dynamics or hardware claim. Search bounds are analytical with numerical roundoff limits; unresolved iteration-limit gaps are shown explicitly. A sinusoid test fixture was corrected to put its intended interior extremum inside the tested beta interval; no tolerances weakened. Offline launchers remain manual; identical standalone HTML tested over HTTP. Prior uncommitted changes preserved.

## 4. Compute Saving Handoff State

V2 now displays a second equal-size global maximum row for tau2, tau4, Tab and dz across theta2/beta at the current alpha.
Each card includes a peak pose, keeps the requested torque sign and reports remaining search uncertainty when necessary.
Refresh v2, use the new numerical checker and updated model notes, preserve v1 and keep all work local; no commit or push performed.

---

## Entry: 2026-10-14 — Andy Zhang — Offline generalized leg design report and reproducible sizing

## 1. Scope & Objective

- **Target Subsystem:** Andy's isolated leg-design-study member workspace; Markdown navigation from existing apps.
- **Associated Issue/Task:** User requested Jonathan V1/V2 conventions combined with wheel/link sizing, two optimization methods, unequal links and variable guide ratio/alpha, independent 2D/Pymunk checks for all nine springs, one spring/motor example, documented assumptions and revision history. Final user steering requires standalone offline static HTML and PDF, with no new Motion Lab tooling. Use 200 mm wheel radius, 200 mm minimum / approximately 250 mm preferred usable travel, 300–350 mm total including buffers, and 40–45 kg whole-robot sensitivity. Publish validated work directly to main.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/README.md`
- `users/andy-zhang/experimental-apps/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/.gitattributes`
- `users/andy-zhang/experimental-apps/leg-design-study/.gitignore`
- `users/andy-zhang/experimental-apps/leg-design-study/AGENTS.md`
- `users/andy-zhang/experimental-apps/leg-design-study/Open Design Report.cmd`
- `users/andy-zhang/experimental-apps/leg-design-study/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/generalized-leg-math.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/generalized-leg-physics.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/generalized-leg-report-data.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/generalized-leg-report.pdf`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/generalized-leg-study.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/impact-load-envelope.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/revisions.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/validation.md`
- `users/andy-zhang/experimental-apps/leg-design-study/generalized_leg.py`
- `users/andy-zhang/experimental-apps/leg-design-study/index.html`
- `users/andy-zhang/experimental-apps/leg-design-study/model.js`
- `users/andy-zhang/experimental-apps/leg-design-study/package.json`
- `users/andy-zhang/experimental-apps/leg-design-study/requirements-report.txt`
- `users/andy-zhang/experimental-apps/leg-design-study/requirements.txt`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_design_report.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_generalized_leg.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_offline_report.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/test_generalized_leg.py`
- `users/andy-zhang/experimental-apps/leg-design-study/tests/design-study.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`

- **API/Interface Changes:** No existing Motion Lab API, browser tooling, model or saved-profile interface changes. Removed the unshipped development integration and restored server.py and tracked web/ source to base 6c74cfd. New single static HTML file has inline styles, 22 SVG figures, selected numerical evidence, local PDF link and print button; it reads with JavaScript disabled and needs no server or installed runtime. Optional Python/Node reproduction is isolated here, importing existing member spring laws without canonical/shared consumers. Root-relative .cmd opens the local report. New AGENTS.md only points to existing root rules and owner-requested delivery context; no policy/enforcement change. App-local .gitattributes marks the PDF binary for correct Git handling. Models, manifests, compact selected JSON, a 16-page PDF/generator and dated design/revision/validation records are retained; raw runs, venvs and captures remain ignored.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** After relocation, Node22.23.3 analytical tests pass13/13; Python3.13.12 physical tests pass12/12; verify_generalized_leg.py passes all9 full1s spring trajectories plus1 generalized fixed-A case at2/1ms. Independent review found no material mechanics/coordinate/direction discrepancy. Earlier source verification passed Jonathan3853/16044/29863 assertions, combined85JS and34existingPython tests; prior embedded/browser checks are explicitly development history, not shipped controls. Actual Edge file:// test passes JavaScript-disabled reading,12sections/22SVG,6objective/16Pareto/9spring/9engine rows, exact JSON parity, no external requests/page errors,390px layout, print callback/CSS and local PDF link/signature. All16PDF pages rendered/visually reviewed; standalone Python3.13 regeneration is byte-identical,65081bytes,22772extractedcharacters,SHA2561a3c1fd72c739d07d948c612a13f8f5df4bb0508aff436c3190f6150c7ac6d7b. Optional pinned dependencies install and pip check passes. Source hashes distinguish pre-relocation computation from delivered adapters. Relative Markdown links pass. Motion Lab original build and CMD stop/restart pass after removing integration; original4186 health and4175Atlas/workbench return200; removed report endpoint returns404. Offline report launcher executes successfully from an unrelated directory. Actual laptop runtimes/services use local paths; hooks installed and full history retained.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. No hardware, GPU, other-OS, impact/contact/rolling, strength, thermal, coil-bind or 3D packaging validation is claimed. Conditional compact example180/340mm,qab1.775,alpha4.375deg gives325total/285usablemm; boundary and larger-tibia alternatives are explicit. Fixed-A robust static scores, supported-chassis dynamics and impact-equivalent held-load sensitivity are distinct. Historical dual-rope remains IMPOSSIBLE/rejected. Earlier microgram-mass/under-resolved engine failures and unshipped input-step bugs remain documented; no physics tolerance was weakened. A constant-drive chart's initially indistinguishable rounded ticks were repaired with display-only padding. Staged whitespace inspection caught CRLF endings in three new Markdown files and the evidence JSON, plus PDF text-diff noise; LF normalization and an app-local binary PDF attribute resolve those packaging issues without changing results. Initial combined edit/venv shell command was policy-rejected; separate explicit edits and environment creation succeeded without a bypass or lost files.

## 4. Compute Saving Handoff State

Open leg-design-study/index.html directly or Open Design Report.cmd for the offline report and adjacent PDF; existing Motion Lab and Atlas remain independent local services.
The report records the compact bounded candidate, complete assumptions, per-profile torque curves, Pareto/boundary tradeoffs, all nine spring checks and one-second motor plus load-factor sensitivities.
Continue from this app's context and revision map, retain Jonathan's conventions and rejected historical status, and obtain actual packaging, moving masses, spring limits and motor duty before promoting these conditional calculations to hardware decisions.

---

## Entry: 2026-10-14 — Andy Zhang — Offline alpha-zero angled-path and inversion search

## 1. Scope & Objective

- **Target Subsystem:** Andy's isolated leg-design-study member workspace.
- **Associated Issue/Task:** Owner requested many equal/near-equal-link designs with alpha=0 and different guide ratios, approximately linear 10–15 degree paths and full inversion, from Jonathan's screenshot parameters. Continue autonomously overnight and deliver another separate offline HTML/PDF report, document assumptions and revision context, validate and publish to main. Retain the 200 mm wheel radius, 300–350 mm total including buffers, prior report and rejected historical dual-rope status.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/leg-design-study/Open Inversion Report.cmd`
- `users/andy-zhang/experimental-apps/leg-design-study/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/inversion-engine-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/inversion-path-report.pdf`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/inversion-path-results.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/inversion-path-study.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/revisions.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/validation.md`
- `users/andy-zhang/experimental-apps/leg-design-study/index.html`
- `users/andy-zhang/experimental-apps/leg-design-study/inversion-paths.html`
- `users/andy-zhang/experimental-apps/leg-design-study/inversion_search.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_inversion_report.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_inversion_geometry.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_inversion_report.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/test_inversion_search.py`

- **API/Interface Changes:** No Motion Lab tooling, localhost endpoints, original numerical model, saved profiles or canonical/shared consumers change. New isolated search extends ideal V2 geometry into full inversion without changing existing validators. Separate static HTML has embedded SVG/evidence, companion PDF and a manual app-relative CMD launcher; the earlier HTML adds a navigation link only. Retained selected JSON, five tests, actual angular Pymunk verifier, deterministic renderer and original-V2/browser verifier support reproduction. App context/design/revision/validation documents record bounded search, explicit phase relaxation and unresolved physical packaging; no new spring or motor rating is transferred to these geometries.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Python 3.13.12 search enumerates 26,461,800 unique geometry/window combinations; 33-pose quality counts and 2001-pose selected metrics distinguished. Five numerical tests pass; independent original-V2 review checks 24 cases at 20,001 poses, agreeing on classifications and bow to 4.4e-6 mm sampling difference. Node 22.23.3/Edge verifier passes 8,784 original-model scalar comparisons, maximum 3.979e-13 mm/Nm, 12 sections / 9 SVG / 16 candidate rows, exact embedded evidence, JavaScript-disabled file reading, zero external requests/errors, 390 px layout, PDF link/signature and print callback/CSS/export. Actual Pymunk five inversion fixtures pass/converge at 1/0.5 ms; all 2 ms path checks fail unchanged 0.1 mm threshold and remain retained. Final 12-page 40354-byte PDF and 749707-byte HTML regenerate byte-identically; all PDF pages and key HTML/mobile figures reviewed. Existing report browser verifier passes 12 sections / 22 SVG after its navigation-only change; old numerical JSON unchanged.85 relative Markdown links, current source hashes and finite evidence pass. Manual launcher runs successfully from unrelated directory. Fetch confirms base 865b5f1 and installed .githooks. Canonical physics NOT APPLICABLE.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. No contact/impact, ground-flip, wheel/chassis interference, belt hardware, spring inversion routing, structural/thermal, GPU, other-OS or hardware acceptance is claimed. An initial zero-buffer height-inverse attempt hit endpoint-bracketing roundoff; the independent angular fixture avoids that dependency without changing the old solver or tolerances. Coarse 2 ms errors 0.112–0.164 mm exceed 0.1 mm; 1/0.5 ms runs pass and converge. Poppler emits a nonfatal Symbol display-font message; actual rendered pages were reviewed with no observed missing glyph/clipping. An ad-hoc evidence check initially assumed script-attribute order; order-independent extraction then passes both reports. Strict phase-zero symmetry makes the full fold tangent vertical, approximate normal/inverted branches mirror, and all near-equal full sweeps fail projected coplanar-wheel clearance. Assembly indexing is explicitly a changed constraint; historical dual-rope remains IMPOSSIBLE/rejected.

## 4. Compute Saving Handoff State

Open leg-design-study/inversion-paths.html or Open Inversion Report.cmd for the new offline report and 12-page PDF, while retaining the earlier design report.
The equal 350 mm 7:4 example gives 325/285 mm total/usable travel, 12.02-degree chord and 9.66 mm bow on its normal branch; longer tested links reduce bow, while strict full inversion has mirrored tilt and unresolved wheel clearance.
Continue from inversion-path-study.md and the revision/context map, choose explicitly whether approximate mirrored branches or assembly indexing is acceptable, and establish axial packaging and actual load/spring routing before hardware sizing.

---

## Entry: 2026-10-14 — Andy Zhang — Labelled Motion Lab design examples and animation GIFs

## 1. Scope & Objective

- **Target Subsystem:** Andy's isolated Motion Lab member app; linked design-report revision context.
- **Associated Issue/Task:** Owner requested labelled Motion Lab visualizations and animation GIFs for the leading alpha-zero path options. Select the three summary options, exact indexed straight-line alternative and original screenshot reference. This explicitly authorizes the new visualization entry while preserving the separate offline report/PDF, existing sizing tool, spring/physics models and historical IMPOSSIBLE status. Source report is main revision 12e227c.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/revisions.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/design-examples.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/requirements-animation.txt`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/build_animations.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/build_design_examples.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/encode_design_gifs.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/export_design_examples.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_design_examples.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/design-examples.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/data.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/exact-line-indexed-inversion.gif`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/exact-line-indexed-working.gif`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/longer-links-inversion.gif`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/longer-links-working.gif`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/manifest.json`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/near-equal-indexed-inversion.gif`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/near-equal-indexed-working.gif`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/screenshot-reference-inversion.gif`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/screenshot-reference-working.gif`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/simple-guide-inversion.gif`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/gifs/simple-guide-working.gif`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/model.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/renderer.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/design-examples/style.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`

- **API/Interface Changes:** New /design-examples/ static page and Miscellaneous study=design-examples entry; no server or numerical backend API changes. Five read-only exact report cases provide shared-scale working/full-inversion canvas views, fixed guide/phase labels, wheel-centre angle ray, play/pause/restart/scrub, filtering, theme/memory and projected-clearance flags. Ten curated GIF illustrations use the same renderer and stay below the 1 MiB blob cap; raw frames/logs stay ignored. Build extracts source-hashed selected evidence and adds gallery navigation; optional export uses locked Playwright and app-local Python/Pillow. The global native GUI action for this kinematic study explains the supported fixture boundary without silently launching the unrelated old wheel model. Existing native launches, saved solver profiles, original models/defaults and offline reports are preserved. Parent/app context and revision/validation records document the later owner request and limitations.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Python 3.13.12 / Node 22.23.3 on this laptop. npm run build passes; npm test passes 76/76, including four new tests. Exact selected config/metric/source-hash parity and 3,010 original-Jonathan-V2 poses pass across five cases and both ranges; mirrored folds and fixed-phase exact-line identity checked. Actual Edge browser passes five cards/two modes, endpoint/midpoint scrubbing, playback, filtering/toggles, all ten HTTP GIF signatures, menu selection/restored settings, dark mode and 390 px layout, with zero page errors/external requests. Kinematic native-GUI action sends no native-launch POST. Optional pinned Pillow 12.3.0 install and pip check pass. All ten GIFs validate 48 frames, 600x720 pixels, 4.8-second infinite looping; representative frames and browser views reviewed and fold labels repaired. Final re-export is byte-identical; GIF/renderer/data hashes match manifest, total 2,589,694 bytes, largest 311,008 bytes. One hundred relative documentation links pass. Actual app-root Stop/Start Motion Lab.cmd from unrelated directory removes listener and restarts successfully; new page returns 200 at 4186. Canonical physics NOT APPLICABLE.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this member visualization workspace. No new spring/motor/Pymunk/contact simulation, physical inversion, 3D packaging, hardware, GPU or other-OS validation is claimed. The 4.8-second animation is an illustrative prescribed theta2 cycle, not an actuator requirement. Phase alternatives keep fixed lower-link assembly indexing and are labelled as relaxing the original phase-zero constraint. Red wheel/disk overlays mark the projected 200 mm wheel plus assumed 20 mm gap, without inventing axial offsets or contacts. Historical dual-rope remains IMPOSSIBLE/rejected. An initial browser harness used a Frame method on a FrameLocator; the corrected API passes. An ad-hoc link check used the lexical parent of Path('.'); resolving the app path then passes. No mathematical or physics tolerance was changed. Existing Python physics backends and their full suites were not rerun because no backend changed; actual UI geometry parity and app lifecycle are the current evidence.

## 4. Compute Saving Handoff State

Open Motion Lab at 4186 with tab=studies&study=design-examples, or the direct /design-examples/ route, and download either GIF for each labelled case.
The same renderer draws three leading options, an exact indexed line and the screenshot reference, with working/full-inversion views and explicit fixed-phase/projected-clearance limitations.
Continue from docs/design-examples.md and the sibling report revision map, preserve all existing solver/profile and IMPOSSIBLE decisions, and use the actual report calculations before proposing physical spring/motor or packaging changes.

---

## Entry: 2026-10-14 — Andy Zhang workspace — force and useful travel for alpha-zero legs

## 1. Scope & Objective

- **Target Subsystem:** users/andy-zhang/experimental-apps/leg-design-study; isolated offline report and experimental force/kinematic screening.
- **Associated Issue/Task:** Owner request to find the best force/travel and link lengths among slightly tilted, ideally invertible paths; preserve original alpha/phase conventions and provide the reasoning/report later. Continue from d1596e5 and keep reports outside Motion Lab tooling.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no existing files deleted.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/Open Force Travel Report.cmd`
- `users/andy-zhang/experimental-apps/leg-design-study/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/force-travel-engine-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/force-travel-math-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/force-travel-report.pdf`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/force-travel-results.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/force-travel-study.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/revisions.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/validation.md`
- `users/andy-zhang/experimental-apps/leg-design-study/force-travel.html`
- `users/andy-zhang/experimental-apps/leg-design-study/force_travel_search.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_force_report.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_force_geometry.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_force_report.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/test_force_travel.py`

- **API/Interface Changes:** New independent force-first grid/refinement, five tests, original-model and actual-Pymunk geometry verifiers, compact selected evidence, offline HTML/nine-page PDF builder and app-relative manual CMD opener. No existing model, Motion Lab/Atlas API, solver UI, saved profile, live example/GIF, spring/motor calculation or canonical consumer changes. App/parent context and revision/validation records link the new force/travel screen, active bounds, fixed-indexing relaxation and unresolved physical inversion. Ranking is direct hip force per Nm with explicitly different knee/speed and work mappings, not electrical efficiency.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Python3.13.12 /Node22.23.3. New strict search enumerates11,478,060 geometry/window combinations (51-pose coarse quality counts,2001-pose selected acceptance), plus11,070 separate fixed-indexed combinations;21 selected cases retained. Two grid-seeded SLSQP refinements succeed and pass dense constraints.22/22 Python tests pass (5 new force,5 inversion,12 generalized). Independent read-only review of21 cases agrees on peakJ to7.22e-15m/rad, RMSJ5.91e-9m/rad and continuous bow3.81e-6mm with unchanged classifications. Original Jonathan V2 and Andy2D statics pass10,248 scalar comparisons, max3.410605e-13mm/Nm. Actual three positive-mass Pymunk angular sweeps pass1/0.5ms and converge; all2ms path checks fail unchanged0.1mm threshold and remain recorded. Installed Edge verifies JavaScript-disabled file reading,9 sections/7 SVG/four shortlist rows, exact JSON, no external requests/page errors/nonfinite plots,390px layout, PDF signature/link and print callback/CSS/export. Nine-page39,966-byte PDF and769,141-byte HTML regenerate byte-identically; all PDF pages rendered and visually reviewed, final changes rechecked. Relative documentation links and finite/source-hash checks pass; manual app-relative CMD opener exits0 from an unrelated directory. Raw captures/logs stay ignored; canonical physics NOT APPLICABLE.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. No real impact/contact, 3D wheel/chassis clearance, structural strength, spring refit, dynamic/thermal motor rating, GPU, hardware or other-OS certification is claimed. Full coplanar inversion fails every shortlisted near-equal case. New3/4g values are held-load sensitivities. The historical dual-rope stays IMPOSSIBLE/rejected; previous models and estimates stay separate. Initial evidence export rejected a NumPy boolean; explicit scalar conversion fixed export and the complete search was rerun. The browser harness figure count was corrected to the actual seven figures; no numerical tolerance changed. Poppler emits its nonfatal Symbol display-font message; completed reviewed pages have no observed missing glyph or clipping. Unchanged Motion Lab/Atlas lifecycle and complete app suites were not rerun for this static report.

## 4. Compute Saving Handoff State

Open leg-design-study/force-travel.html or its nine-page PDF for the force-first ranking, total/useful travel comparisons, individual torque/force curves and control/load sensitivities.
Rounded320/320mm9:5 atalpha=phi0=0 gives325/285mm height and57.832Nm equivalent static hip peak at45kg; indexed300/300mm2:1 phi0=-25 gives an exact12.5degree line with wider control/speed range, while local minima touch constraint boundaries.
Continue from docs/force-travel-study.md, resolve axial/chassis clearance and actual load/mass/shaft/spring inputs before physical inversion or motor selection, and preserve all previous reports, live examples/GIFs and IMPOSSIBLE decisions.

---

## Entry: 2026-10-14 — Andy Zhang workspace — merge Jonathan v2 as separate Motion Lab linkage

## 1. Scope & Objective

- **Target Subsystem:** users/andy-zhang/experimental-apps/wheel-leg-lab; isolated analytical UI/model integration.
- **Associated Issue/Task:** Current owner request to cross-check Jonathan's v2 against the referenced v1 and merge all linkage/loading features into Motion Lab Math and 2D Physical as a separate design. Base 93fed9f; no relevant open GitHub issue.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no existing files deleted.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/.gitignore`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Start-Pymunk.ps1`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/jon-linkage-cross-check.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/unified-motion-lab.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/jon-linkage/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/jon-linkage/bridge.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/jon-linkage/embedded-api.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/jon-linkage/style.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/build_animations.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/build_jon_linkage.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_jon_linkage.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/jon-linkage.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/comparison-data.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/data-browser.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/library.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`

- **API/Interface Changes:** New source-built /jon-linkage/ route and shared Math/Physical model=jon-v2 editor. Three original analytical scripts are preserved byte for byte, with source hashes; the UI adapter adds atomic snapshots/restoration, same-origin messages, theme/session recovery and nonmutating analytical sweep evaluation. Library backend jon_v2 accepts original v1/v2 JSON in mm/deg/kg/N/Nm, retains full parameters/windows/driven selections and exports four sweep tables with explicit units/provenance. Comparison overlays use sample indices and retain time-delta rejection; native/recorded Pymunk actions explain the separate quasi-static boundary. Startup now checks the new generated page. No original Jonathan source, dynamic/spring/native backend, shared/canonical API, dependency, asset, enforcement or prior IMPOSSIBLE decision changed.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Installed app-local Python 3.13.12 / Node 22.23.3. npm run build passes; 80/80 Node tests pass, including four new source/library/sweep checks. Original Jonathan checks pass 3,853 kinematic, 16,044 quasi-static and 29,863 bounded-maxima assertions with original residual limits. All three generated analytical scripts and model hashes match original source exactly. Actual Edge verify_jon_linkage.cjs passes full parameter/FBD/sweep/headline presence, editable unequal geometry/masses/preloads/angles/signed loads, 31-pose original-model parity, force-convention torque invariance, shared Math/Physical state, background master pause, original JSON/31-column CSV, four-sweep library/provenance, nonmutating profile reevaluation, refresh, bad-window atomicity, invalid-draft rejection, dark/mobile and no native/external requests/page errors. Existing verify_motion_lab.cjs passes real SciPy/Pymunk APIs, original menu/library/comparison/recorded playback/Plotly/mobile with mocked native launch endpoints. Actual app-root CMD reuse/scoped stop/start from unrelated directory passes; listener disappears and new linkage returns HTTP 200 after restart at 4186. Desktop/diagram/mobile captures visually reviewed; artifacts ignored. Whitespace and 103 relative documentation links pass. Exact staged check_entry.py --base origin/main --require-passed passes: 612 files, 22 changed paths, workspace scope. physics_gate.py --base origin/main passes and reports canonical physics NOT APPLICABLE. The default working-tree check flags seven concurrent unlogged corridor paths in the separate leg-design-study app; staged validation and exact outgoing-commit hooks exclude that unfinished work without changing it.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this member workspace. No dynamic general-linkage Pymunk/spring/acceleration/contact/rolling, 3D packaging, hardware, GPU or other-OS validation is claimed; existing full Python/native solver suites were not rerun because those backends are unchanged. Initial browser sweep-ID count included tooltips; an SVG-specific selector corrects the harness. Visual review found inherited automatic vertical margins centring the source main column in an enlarged iframe; top alignment and a layout assertion fix it. Shell python initially resolved to a nonlaunchable Cygwin entry; installed app-local Python supplies the build/hooks. Concurrent untracked leg-design-study corridor files are preserved and excluded from this exact staged contribution; validation uses its isolated snapshot when full working-tree entry coverage includes that unfinished work. No solver tolerance was changed.

## 4. Compute Saving Handoff State

Open Motion Lab at 4186 with tab=math&model=jon-v2 or tab=physics&model=jon-v2 for the same separate three-belt editor and all original v2 parameters, FBDs, sweeps and bounded maxima.
Save full linkage profiles through the existing library and analytical sweeps inside the editor; original v1/v2 JSON imports and source CSV remain compatible, while quasi-static playback is not a dynamic Pymunk run.
Continue from docs/jon-linkage-cross-check.md and jon-linkage/README.md, rebuild after upstream source edits, preserve the original spring/inversion fixtures and rejected dual-rope status, and resolve actual dynamics/contact inputs before adding a physical counterpart.

---

## Entry: 2026-10-14 — Andy Zhang workspace — ratio-generated curved paths and lateral travel

## 1. Scope & Objective

- **Target Subsystem:** users/andy-zhang/experimental-apps/leg-design-study; isolated offline curved-path report and numerical screening.
- **Associated Issue/Task:** Owner cancelled the unpublished fixed15/R² proposal and requested curved paths permitting horizontal travel/compliance through guide-ratio changes, then confirmed25/50/75/100 mm comparisons. Retain alpha=phi0=0,325 mm total including assumed20+20 mm reserves. Numerical base93fed9f; preserve concurrent Motion Lab work and publish this report separately.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no existing files deleted.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/Open Curved Path Report.cmd`
- `users/andy-zhang/experimental-apps/leg-design-study/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/curved-paths.html`
- `users/andy-zhang/experimental-apps/leg-design-study/curved_path_search.py`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/curved-path-engine-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/curved-path-math-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/curved-path-report.pdf`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/curved-path-results.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/curved-path-study.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/revisions.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/validation.md`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_curved_report.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_curved_geometry.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_curved_report.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/test_curved_paths.py`

- **API/Interface Changes:** New independent curved-path grid, six tests, original-V2/Andy2D and actual-Pymunk geometry verifiers, compact evidence, seven-page PDF/static HTML renderer and app-relative CMD opener. Separate normal excursion bands, force/size leaders, effective ROM, lateral/vertical coupling and normal220 clearance scenarios replace the abandoned unpublished R² approach. No existing model, shared/canonical API, dependency, Motion Lab service/UI/example/GIF or prior spring/motor calculation changes. Historical dual-rope remains IMPOSSIBLE/rejected. App/parent context, reasoning, revision and validation records retain assumptions and continuation.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Python3.13.12 /Node22.23.3. Search enumerates2,953,002 windows;33-pose coarse counts, continuous selected extrema,2001-pose integrals;29 detailed cases and32 compact objective leaders.16/16 numerical tests pass (six new plus five force/five inversion). Independent original-V2 read-only review of29 cases agrees on lateral metrics7.11e-14mm, slope1.07e-14, usefulROM1.08e-12deg and signed/robust side-load peaks1.43e-14Nm; all flags match.10,788 originalV2/Andy2D scalar comparisons pass, max2.273737e-13mm/Nm. Three actual positive-mass Pymunk angular fixtures pass2/1/0.5ms and converge; fine path errors0.016781..0.018228mm. Installed Edge verifies JavaScript-disabled offline reading,7 sections/6 SVG/four shortlist rows, exact JSON, finite plots, no external requests/page errors,390px layout, PDF signature/link and print callback/CSS/export. Seven-page29,539-byte PDF and840,110-byte HTML regenerate byte-identically; all PDF pages and key HTML/mobile figures visually reviewed, final changed layouts rechecked.85 relative links and calculation/engine hashes pass; app-relative manual CMD opener exits0 from unrelated directory. Exact-snapshot entry/require-passed/scoped gate and staged checks are run before publication; canonical physics NOT APPLICABLE.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. Short cases fail normal220 coplanar clearance, and every full near-equal coplanar inversion fails. Actual stiffness requires spring/controller/geometric stiffness and contact inputs; no measured compliance, spring selection, dynamic/thermal motor rating, physical inversion, real impact, hardware, GPU or other-OS validation is claimed.3/4g values are held-load multiples. First evidence export exceeded1MiB; display samples reduced to31 with dense metrics unchanged, then search/evidence regenerated. Compact leader metrics added after review. Poppler retains its nonfatal Symbol display-font message; reviewed pages have no observed missing glyph or clipping. Superseded unpublished R² files stay ignored locally. Concurrent unrelated Motion Lab edits are excluded; publication checks use an isolated exact snapshot rather than those unfinished working-tree edits. Unchanged complete app suites/lifecycle were not rerun for this report.

## 4. Compute Saving Handoff State

Open leg-design-study/curved-paths.html or its seven-page PDF for25/50/75/100mm curved lateral movement with alpha=phi0=0,325mm total/285mm useful height and individual force/control plots.
Equal185/190/200/205mm links with r1.9/1.8/1.7/1.6 give about25/50/75/100mm sideways excursion;190mm9:5 is the balanced compact geometric seed, while285mmr1.85 is the normal220-clearance50mm comparison.
Continue from docs/curved-path-study.md, resolve measured axial/chassis/contact and effective stiffness before physical inversion or actuator selection, and preserve prior reports/models/examples, historical failures and IMPOSSIBLE decisions.

---

## Entry: 2026-10-14 -- Andy Zhang workspace -- merge Jon tooling into original Math and Physics solvers

## 1. Scope & Objective

- **Target Subsystem:** users/andy-zhang/experimental-apps/wheel-leg-lab; isolated Motion Lab suspension bench.
- **Associated Issue/Task:** Owner corrected c8b3c8b: merge Jonathan v2 features into the original physics/math tool and validate its equations against his code. Supersedes the standalone copied-editor approach; preserve original defaults, springs, APIs, profiles, viewer and sibling design reports.

## 2. Structural Modifications

- **Files Modified/Added:** Exact changed paths below, including deletion of the previous standalone editor, builder/verifier/test and its superseded document.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/.gitignore`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/Start-Pymunk.ps1`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_gui.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/debug_view.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/jon-linkage-cross-check.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/merged-linkage.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/model.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/unified-motion-lab.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/generalized_suspension.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/jon-linkage/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/jon-linkage/bridge.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/jon-linkage/embedded-api.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/jon-linkage/style.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/linkage_geometry.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/math_model.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/native_guide_belt.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/physics.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/build_animations.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/build_jon_linkage.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/build_jon_models.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/jon_reference_fixtures.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_jon_linkage.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_merged_linkage.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/setup_preview.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/spring_mechanisms.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_generalized_linkage.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/jon-linkage.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/merged-linkage.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/comparison-data.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/data-browser.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/jon-profile.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/library.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/linkage-tools.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/linkage-tools.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/mathematical/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/physics/index.html`

- **API/Interface Changes:** Existing math/pymunk profiles and endpoints gain optional linkage_design=general with separate link lengths, all six carrier pitch radii, mounting/phase, optional compound mass/rim inertia, signed world/normal-tangent force inputs, beta bounds, preload reference fields and driven selections. Original geometry remains default; general dynamics uses independent direct-angle SciPy and actual unequal Pymunk bodies/pivots/gears with original spring laws/position driver. New dynamic angle/motor/energy channels and measured Newton-Euler diagnostics; unity/cancellation handled explicitly. Exact Jonathan model scripts are source-built with hashes for the existing bench's five-FBD/sweep/maxima audit. Source v1/v2 JSON maps mm to SI profiles; analytical sweeps save read-only datasets without invented time. UI preserves edits made during pending Run and fills newly introduced reference defaults when replaying old results. The separate jon_v2 backend/editor/menu route is removed; old query resolves to the ordinary bench. Native/setup/debug consumers support actual general geometry. No shared/canonical API, dependency, asset, rule, original Jonathan source, offline report or historical rejected inversion decision changes.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Installed app-local Python3.13.12 / Node22.23.3. npm build passes and81 Node tests pass. Original Jonathan suites pass3853/16044/29863 assertions with force/moment/VW maxima9.722e-13N/3.624e-13Nm/3.979e-13Nm; generated model scripts/hashes match source exactly. Broader original/general Python run113 tests passes, including original nine-preset108-backend-case envelope; expanded nine generalized tests pass source parity288 varied poses, independent fixed-A holding torque, geometry/force/inertia, all nine spring Jacobians, potential gradient/angular closure, original2:1 recovery, unity/cancellation/invalid cases and actual-body conservative energy. General Pymunk final-angle errors1/.5/.25ms:0.0006268464/0.0001868328/0.0000622246deg; physical energy drift0.0097574/0.0048918/0.0024492J converges, SciPy drift<1e-8J. New installed-Edge integration passes actual Math/Pymunk APIs,3belts/5FBDs/15plots/8headlines, all parameters, exports/library/native-profile dispatch (mocked), pending-run preservation, refresh/theme/mobile and no page errors/external requests. Existing verify_motion_lab and verify_setup_preview_ui pass. Actual native headless renderer passes1200 steps/6shapes/9constraints; screenshots visually reviewed and crowded legends corrected. Durable app-root Stop/Start CMD lifecycle at4186 passes.107 relative links and whitespace pass; default and --require-passed check_entry pass627 files/44 changed paths/workspace, and physics_gate reports canonical physics NOT APPLICABLE. Final general/spring regression passes21 tests and durable CMD stop/start/reuse from an unrelated directory confirms closed listener and HTTP200 original preview/reference bundle at4186. Staged/exact-tip publication checks run before commit and push.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this member workspace. Fixed-A source holding/preload bearing loads are separate from moving-chassis spring/acceleration dynamics; physical belts/bearing forces, motor-shaft freedom, rolling/unilateral contact,3D packaging, hardware,GPU,other-OS and MATLAB general linkage are unvalidated. Original unrelated lever/inversion full suites were not rerun. Initial GearJoint residual used symmetric scaling; second-body torque convention corrects it. Initial new conservative case hit a dissipative stop; retained test asserts interior travel/no impact at2000N/m, without loosening tolerance. Browser harness fixes open collapsed controls, inspect native config envelope and use trusted-parent profile messages. Historical separate-editor contribution/log and independent sibling work are preserved in shared history; this is a normal corrective commit.

## 4. Compute Saving Handoff State

Open Motion Lab at4186 on the original Math or2DPhysics bench and choose Geometry > Editable links / three carrier belts for the merged controls, dynamics and source audit.
Read docs/merged-linkage.md for exact coordinate conversion, energy/constraint equations, source hashes, JSON/data contracts, positive dynamic masses and the fixed-A versus floating-support distinction; original equal-link defaults and spring/native workflows remain available.
Continue with Start Motion Lab.cmd, rebuild when Jonathan source changes and rerun the retained parity/refinement checks before extending physical belt/contact/motor modeling; preserve independent reports and the rejected dual-rope status.

---

## Entry: 2026-10-14 -- Andy Zhang workspace -- preserve bounded-search failure diagnostics

## 1. Scope & Objective

- **Target Subsystem:** users/andy-zhang/experimental-apps/wheel-leg-lab; merged audit output.
- **Associated Issue/Task:** Final source review found the unconverged maximum-search note reading a nonexistent gap field; show the source error bound and verify iteration-limit behavior before publication.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no deletions.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/linkage-tools.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_merged_linkage.cjs`
- **API/Interface Changes:** Audit reads Jonathan's actual error field when a maximum is an unconverged estimate. No solver equations, configuration, endpoints or source changes; browser verification forces zero search iterations and checks a numerical remaining bound instead of an undefined placeholder.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Installed Edge merged verifier passes full original-backend workflows plus forced iteration-limit numerical-bound display, with no page errors/external requests. Previously recorded source, Python, Node, launcher and native checks retain their scope; exact final staged and outgoing-tip hooks run before publication. Whitespace passes.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE. This fixes reference result presentation only; the merged model's documented physical limitations remain unchanged.

## 4. Compute Saving Handoff State

The original Math and Physics benches retain the merged general geometry and source audit described in the preceding entry.
Unconverged headline estimates now report Jonathan's attained value and actual remaining error bound; the retained browser test reproduces the limit case.
Rebuild after upstream source changes and continue from docs/merged-linkage.md without interpreting the fixed-A reference as measured dynamic or hardware performance.

---

## Entry: 2026-10-14 -- Andy Zhang workspace -- refresh maxima after beta-window edits

## 1. Scope & Objective

- **Target Subsystem:** users/andy-zhang/experimental-apps/wheel-leg-lab; merged reference audit.
- **Associated Issue/Task:** Follow-up final review identified beta-bound-only edits retaining cached headline maxima. Recompute within the actual edited box and verify attained poses, preserving the published merge and original solvers.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no deletions.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/linkage-tools.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_merged_linkage.cjs`
- **API/Interface Changes:** Reference cache identity includes beta search bounds. Current audit states theta2/beta search domain and fixed alpha; bound labels describe headline search rather than full-domain plotting. General dynamic readout calls the wheel constraint output drive reaction, preserving the original lower-link label in original mode. No solver, source-reference equations, configuration keys or endpoint changes.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Installed Edge verify_merged_linkage.cjs passes full original Math/Pymunk workflows and a new beta-window-only edit from0..90 to20..30 degrees with all four attained peak beta poses inside the new bounds, then restored full range. Forced zero-iteration numerical error-bound display, controls/plots/FBDs/exports/library/native dispatch (mocked), refresh/theme/mobile and no page errors/external requests also pass. Both JavaScript files parse and whitespace passes. Earlier numerical/native/launcher checks retain their scope; this changes UI caching/labels only. Fetched published base1a431c8; final staged default entry check and exact outgoing require-passed/scoped gate run through the installed mandatory hooks before publication.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE. This fixes which validated reference box is displayed, with no changed dynamic equations or new hardware/contact claim. The first merge is already published; this correction uses a new normal commit and does not rewrite shared history.

## 4. Compute Saving Handoff State

Refresh the original Math/Physics benches for the merged tooling; changing beta bounds now recalculates all headline maxima and displays the selected search domain.
The browser verifier retains both bounded-pose and iteration-limit checks alongside the original-backend workflows, while numerical/native results remain in docs/validation.md.
Continue from docs/merged-linkage.md and preserve fixed-A reference versus moving-chassis dynamics, original defaults and the rejected dual-rope status.

---


## Entry: 2026-10-14 -- Andy Zhang workspace -- unequal-link invertible paths

## 1. Scope & Objective

- **Target Subsystem:** users/andy-zhang/experimental-apps/leg-design-study; offline member design report.
- **Associated Issue/Task:** Owner requested good unequal-leg curved paths through inversion, retaining alpha=phase=0, wheel R200 and325 mm total normal travel including buffers. Search separate force/size and projected-clearance families, deliver labelled examples/GIFs and PDF, document decisions without adding Motion Lab controls.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no deletions.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/Open Unequal Inversion Report.cmd`
- `users/andy-zhang/experimental-apps/leg-design-study/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/revisions.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/clear100.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/clear25.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/clear50.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/clear75.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/manifest.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-inversion-engine-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-inversion-math-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-inversion-report.pdf`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-inversion-results.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-inversion-study.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/validation.md`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_unequal_report.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_unequal_visuals.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_unequal_geometry.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_unequal_report.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/test_unequal_inversion.py`
- `users/andy-zhang/experimental-apps/leg-design-study/unequal-inversion.html`
- `users/andy-zhang/experimental-apps/leg-design-study/unequal_inversion_search.py`
- **API/Interface Changes:** New isolated unequal-link grid, tests, actual constrained geometry verifier, report/GIF generators and original-model/offline-browser verifier. Adds camel/unequal-inversion/v1 selected-evidence schema and camel/unequal-inversion-gifs/v1 manifest inside this app only. No production endpoint, model, dependency, lockfile, saved-profile or shared interface changes. New manual app-relative CMD opens a static local file; no server or startup task is installed. Earlier reports/models and rejected dual-rope IMPOSSIBLE status are unchanged.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Python3.13.12/NumPy2.5.3/SciPy1.18.1 search enumerates11,535,210 windows, retains24 compact leaders/22 detailed cases; all source hashes match.22 numerical tests pass (six new); first harness misclassified wide_reverse as numeric grid ID, fixed classifier and reran all22 without changed criteria.8,184 original JonathanV2/Andy2D scalar comparisons pass, maximum2.84217e-13 mm/Nm. Independent read-only Sol6.1 high audit agrees across22 inverse/clearance/ROM/force cases; prose corrections explicitly preserve holding-magnitude sign,3g/4g scaling, RMS-duty limitations and UTF8. Actual positive-mass Pymunk7.3.0 pivot/gear/motor sweeps clear25/50/100 pass unchanged path/pin/guide/tracking thresholds at2/1/0.5/0.25 ms and converge; finest path errors0.006819/0.005918/0.008080 mm. Zero forces/gravity and no collision shapes: geometry only. Installed Edge passes JS-disabled file reading,6 sections/5 SVG/4 rows/exact JSON/4 local GIFs,390px layout, print callback/CSS/export, PDF link/signature, no external request/page error. Four800x640 GIFs each have80 frames and6000 ms verified duration; source/output hashes match, each<1MiB. Initial GIF size failure fixed with shared palette/differential frames. Six-page24,173-byte PDF and660,300-byte HTML regenerate byte-identically; all final PDF pages, mobile HTML and GIF start/fold figures visually reviewed. Poppler nonfatal Symbol display-font message persists with no observed glyph/layout defect.117 relative links, finite evidence, source/manifest hashes and whitespace pass. Manual launcher exits0 from unrelated directory. Fetched origin/main1a3fb7e and hooks remain .githooks; final working/staged/outgoing checks run before publication. No unchanged Motion Lab/Atlas lifecycle or complete app-suite rerun is claimed.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE. Lower-long designs pass ideal height inversion and assumed thin-upper-link/guide-pitch-circle wheel screens, but rods overlap and the lower link crosses the hip in side projection atfold. Actual axial stack, forks, outer pulleys, chassis, tire/rod dimensions, strength, loaded dynamics/contact/impact, springs, thermal motor duty, hardware, GPU and other-OS behavior remain unvalidated.

## 4. Compute Saving Handoff State

Open unequal-inversion.html for the four labelled paths/GIFs and its six-page PDF;160/475 mm,r1.42 is the50 mm seed and160/480,r1.35 is the75 mm lower-static-torque alternative, both325/285 mm total/useful height.
Read docs/unequal-inversion-study.md for exact equations, stronger pitch-circle screen, upper-long rejection, search bounds, separate ranking objectives, source hashes and actual validation; physical inversion still requires a packaged axial design.
Preserve older reports, Motion Lab models/services, motor/spring cases and IMPOSSIBLE decisions; continue with measured outer/axial/chassis geometry and duty before hardware sizing, using normal validated direct-to-main publication.

---


## Entry: 2026-10-15 -- Andy Zhang workspace -- constrain unequal links within1.25x

## 1. Scope & Objective

- **Target Subsystem:** users/andy-zhang/experimental-apps/leg-design-study; offline constrained upper-long report.
- **Associated Issue/Task:** During the initial report's local commit, the owner clarified that upper may be longer but max(link length)/min<=1.25. Supersede160/475 mm, search compact upper/lower-long families, rebuild current report/PDF/GIFs and preserve the earlier broad evidence in local revisionaaed324 rather than pushing it alone as the recommendation.

## 2. Structural Modifications

- **Files Modified/Added:** Exact complete outgoing paths plus deleted prior-revision GIF paths below. The Open launcher is included because it is added by the preceding outgoing commit; clearNN GIFs are deleted from the current tree and remain in aaed324.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/Open Unequal Inversion Report.cmd`
- `users/andy-zhang/experimental-apps/leg-design-study/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/revisions.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/clear100.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/clear25.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/clear50.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/clear75.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/manifest.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/upper100.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/upper25.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/upper50.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-animations/upper75.gif`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-inversion-engine-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-inversion-math-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-inversion-report.pdf`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-inversion-results.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/unequal-inversion-study.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/validation.md`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_unequal_report.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_unequal_visuals.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_unequal_geometry.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_unequal_report.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/test_unequal_inversion.py`
- `users/andy-zhang/experimental-apps/leg-design-study/unequal-inversion.html`
- `users/andy-zhang/experimental-apps/leg-design-study/unequal_inversion_search.py`
- **API/Interface Changes:** App-local evidence schema camel/unequal-inversion/v2 includes explicit maximum_length_ratio1.25 and per-case length_ratio/owner_length_ratio_pass. Separate upper/lower-long force/size leaders replace the earlier broad-clearance recommendation. Current upper25/50/75/100 GIFs replace clearNN current files; offline report paths and manual launcher remain stable. No production endpoint, model, dependency, lockfile or shared interface change; no Motion Lab controls are added.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** New6,601,338-window grid retains24 leaders/20 detailed cases; all satisfy1.25x,325/285 mm height and continuous full height inverse.23 numerical tests pass, including explicit owner-limit and upper-long-fold cases.7,440 originalV2/Andy2D scalar comparisons pass, max1.70530e-13 mm/Nm. Independent read-only Sol6.1 high audit agrees across all20 cases and source hashes; max ROM discrepancy1.49e-12 deg and peak1.14e-13 Nm. Three actual positive-mass Pymunk motor/pivot/gear sweeps upper25/50/100 pass all2/1/0.5/0.25 ms unchanged path/pin/guide/tracking limits and converge; finest path errors0.010445/0.009186/0.008988 mm. Zero gravity/forces/collision shapes: geometry only. Installed Edge verifies JS-disabled offline6 sections/5 SVG/4 rows/exact JSON/4 local GIFs,390px layout, PDF link/signature and printing; no external request/page error. Four800x640,80-frame GIFs have actual6000 ms durations, source/output hashes match and each<1MiB; reviewed all fold frames and50mm start. Six-page24,419-byte PDF and607,635-byte HTML regenerate byte-identically; all PDF pages/mobile HTML/GIFs reviewed, final pose-specific speed wording rechecked. Poppler's nonfatal Symbol font message persists with no observed glyph/layout defect. A transient renderer quote error and unescaped inequality markup were fixed before successful build; no equation/tolerance changed.119 relative links, finite evidence, UTF8/source hashes and whitespace pass. Manual launcher returns0 from unrelated directory. Fetched origin/main1a3fb7e; staged/outgoing checks and installed hooks remain mandatory. Unchanged Motion Lab/Atlas lifecycle/full app suites are not rerun.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE. Current upper-long folds put wheel centre C inside upper AB, so physical inversion needs measured axial wheel/link separation and is unvalidated. Guide pitch spacing is not wheel/chassis/outer hardware clearance; no compact coplanar clearance pass, new spring/motor rating, loaded impact/contact, hardware, GPU or other-OS certification is claimed. All older reports/models, historical failures and rejected dual-rope IMPOSSIBLE decisions remain intact.

## 4. Compute Saving Handoff State

Current unequal-inversion.html/PDF/GIFs enforce max/min<=1.25 and show upper-long200/170,r2;200/175,r1.875;205/185,r1.75;215/175,r1.7 for approximately25/50/75/100 mm sideways travel over325/285 mm total/useful height.
Start from200/175,15:8 for the50 mm CAD study or205/185,7:4 for75 mm; the unequal2:1 case is an ellipse and the earlier160/475 recommendation is superseded before shared publication.
Read docs/unequal-inversion-study.md, validation and revisions for exact assumptions/proofs/evidence; resolve actual axial/chassis/tire/outer-pulley geometry before physical inversion or hardware sizing, preserving all prior model and IMPOSSIBLE decisions.

---


## Entry: 2026-10-15 -- Andy Zhang workspace -- equal-link controls and next-sweep brief

## 1. Scope & Objective

- **Target Subsystem:** users/andy-zhang/experimental-apps/leg-design-study; separate offline comparison and optimization brief.
- **Associated Issue/Task:** Explain what slightly unequal links offer versus comparable equal links, summarize current owner design requests and propose variables/methods for the next sweep. Preserve equal/upper-long/lower-long eligibility, owner max/min<=1.25, alpha=phase=0, R200 and325 mm total buffered height. Do not run another large search in this contribution.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/Open Sweep Brief.cmd`
- `users/andy-zhang/experimental-apps/leg-design-study/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/design-sweep-brief.html`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/design-sweep-brief.pdf`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/equal-link-comparison-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/equal-link-comparison.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/next-sweep-brief.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/revisions.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/validation.md`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_sweep_brief.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/compare_link_lengths.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_sweep_brief.cjs`
- **API/Interface Changes:** Adds app-local camel/equal-link-comparison/v1 selected evidence, original-model verifier and offline HTML/PDF builder/manual CMD. Adds fixed-total-length/guide controls and a proposed S/d/r/window Pareto search brief; updates app context/revision links. No production interface, dependency, equation, Motion Lab control/service or old report/GIF changes. Historical dual-rope IMPOSSIBLE/rejected decisions remain intact.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Python3.13.12 comparison retains13 analytical cases, reproduces32 published metric comparisons exactly and checks501 r2 identity samples within5.68434e-14 mm/rad-unit quantities. Independent original JonathanV2/Andy2D verifier passes4,838 scalar checks, max1.70530257e-13 mm/Nm; source hashes match. Retains equal195/195,r1.7 capacity324.800 mm as a0.200 mm numerical threshold failure and185/185,r2 guide surplus5 mm as an assumed10 mm screen failure; added190/190 vs205/175,r2 controls both meet that screen. Read-only independent Sol6.1 high audit agrees with comparisons, reciprocal1.25 limit and parameterization. Installed Edge passes JavaScript-disabled file reading,4 sections/2 SVG/4 rows/exact embedded JSON,390px layout, finite values, PDF link/signature, print callback/CSS/export,1 local file request and0 external requests/page errors. Four-page14,322-byte PDF and357,822-byte HTML regenerate byte-identically; all final PDF pages and mobile HTML rendered/reviewed. Poppler nonfatal Symbol display-font message has no observed glyph/overlap/clipping defect. Manual Open Sweep Brief.cmd exits0 from unrelated directory.126 relative links, UTF8, finite evidence, source hashes and whitespace pass. Fetched origin/main14f53f1 and installed .githooks; required working/staged/outgoing checks remain part of publication. No new large search, Pymunk run, full Motion Lab/Atlas lifecycle, loaded spring/motor or physical inversion test is claimed.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. Physical wheel/link/chassis/outer-pulley clearance, real masses/inertia, stiffness/contact, impacts, hardware, GPU and other-OS behavior remain unvalidated. Proposed bounds and20+20 mm reserves are assumptions; current short designs depend on extending the normal stop beyond the screenshot's165 degrees.

## 4. Compute Saving Handoff State

Read design-sweep-brief.html and docs/next-sweep-brief.md for the equal/unequal comparison, current owner choices, ROM sensitivity, separate objectives and copyable next-sweep request; no new large grid was run.
Use equal190/190,r1.8 as the50 mm force/travel baseline and200/175,15:8 as a path/guide-packaging alternative, preserving both and lower-long controls in the next study.
Compare165/170/175 stop scenarios with signed d including zero and both orientations, resolve physical packaging and duty before spring/motor sizing, and preserve all prior reports/models/IMPOSSIBLE decisions under normal validated direct-to-main publication.

---


## Entry: 2026-10-15 -- Andy Zhang workspace -- RMS and reverse lower-long1.25x

## 1. Scope & Objective

- **Target Subsystem:** users/andy-zhang/experimental-apps/leg-design-study; offline RMS comparison.
- **Associated Issue/Task:** Compare equal/different link RMS and test owner's reverse r2=1.25*r1, interpreted upper L2=1x/lower L3=1.25x, separate from pulley guide ratio. Retain R200, alpha=phase=0,325 mm total height/20+20 assumed reserves, sideways25/50/75/100 bands and165/170/175 cap scenarios. Compare hip/knee coordinates and declare static versus dynamic weighting.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/Open RMS Comparison.cmd`
- `users/andy-zhang/experimental-apps/leg-design-study/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/revisions.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/rms-link-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/rms-link-engine-checks.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/rms-link-report.pdf`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/rms-link-results.json`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/rms-link-study.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/validation.md`
- `users/andy-zhang/experimental-apps/leg-design-study/rms-link-comparison.html`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_rms_report.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/compare_rms_links.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_rms_geometry.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_rms_links.cjs`
- **API/Interface Changes:** Adds app-local camel/rms-link-comparison/v1 selected evidence, bounded RMS grid, original-model RMS verifier, actual unloaded geometry verifier, separate static HTML/PDF renderer and manual CMD. Updates app/context/revision/validation records. No canonical model, production endpoint, dependency, lockfile, Motion Lab control/service or previous report/GIF changes. Historical dual-rope IMPOSSIBLE status remains intact.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Python3.13.12/NumPy2.5.3/SciPy1.18.1 bounded582,471-window grid retains36 hip-RMS leaders and52 detailed analytical cases;118,071 height/guide/inverse and15,940 lateral-band scenario passes. Original JonathanV2/Andy2D7,702 scalar checks pass, overall9.89075e-12 mm/Nm, independent height-RMS4.54037e-12 Nm and quintic-time static RMS9.89075e-12 Nm. Adaptive quadrature versus existing height estimate differs<=7.59076e-7 Nm; doubled time resolution<=6.25278e-13 Nm. Fixed-S/r2 identities, owner1.25 limit and source hashes pass. Actual Pymunk7.3.0 motor/pivot/gear sweeps for3 new reverse cases pass unchanged path/pin<0.1 mm,guide<1e-4 rad,tracking<0.01 rad at2/1/0.5/0.25 ms and converge; finest path0.00754746/0.00847097/0.00736111 mm. Zero gravity/forces/collision shapes: geometry only. Installed Edge passes JS-disabled local file reading,4 sections/3 SVG/exact JSON,390px layout,finite values,PDF link/signature,print callback/CSS/export;1 local and0 external requests/page errors. Four-page13,673-byte PDF and726,713-byte HTML regenerate byte-identically; final rendered pages/mobile reviewed. Page2 spacing and one rounded knee digit corrected during QA; Poppler nonfatal Symbol font message has no observed glyph/layout defect. Manual app-relative CMD exits0 from unrelated directory. UTF8,strict finite JSON,relative links,<=1MiB new blobs and whitespace pass. Fetched origin/mainc92880d; installed hooks and required working/staged/outgoing checks remain mandatory. No unchanged full Motion Lab/Atlas lifecycle/suite rerun is claimed.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated workspace. RMS search optimizes only massless-link static hip height-weighting, not global/knee/motor optimum. Quintic results are static torque along normalized time, without acceleration torque. Physical inversion/axial wheel/chassis/outer-hardware clearance, loaded spring/motor/contact/impact/thermal behavior, actual compliance, hardware/GPU and other OS remain unvalidated.

## 4. Compute Saving Handoff State

Read rms-link-comparison.html and docs/rms-link-study.md for matched450 mm/exact50 mm lateral controls, bounded hip-RMS leaders, actuator mapping, duty assumptions and actual validation.
Lower200/250 with guide1.711530895 gives33.508 Nm hip RMS versus equal225/22535.433, but equivalent knee19.578 versus19.408 reverses that benefit; rounded180/225,17:10 is a compact reverse example with49.10 mm sideways/30.835 Nm hip RMS.
Preserve all older reports/models/IMPOSSIBLE decisions, compare exact actuator coordinate and real packaging/duty before springs/motors, and publish only through normal validated direct-to-main hooks.

---

## Entry: 2026-10-17 — Jonathan Xie — VSL V3 hip tension horn

## 1. Scope & Objective

- **Target Subsystem:** Jonathan's isolated leg-solver member app.
- **Associated Issue/Task:** Add compact hip tension horn spring inputs, full90–270 travel, master graph domain toggle, labeled geometry/initial tension, full-range equivalent support and residual motor torque while preserving V1/V2. Local save only.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-spring.html`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-spring.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/plot-v3-sample.py`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver v3.cmd`
- `users/jonathan-xie/experimental-apps/leg-solver/.gitignore`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-full-range.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-full-range.svg`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-hip-horn-geometry.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-hip-horn-geometry.svg`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-verification.json`
- `users/jonathan-xie/experimental-apps/leg-solver/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/README.md`

- **API/Interface Changes:** Add standalone v3-spring HTML and general-vsl/v3-spring JSON schema. Global Sy/Sz, hornR/eta, effective ell0, added preload p, k and enable flag define a unilateral tension spring. tauG=-V2 holding tau2; tauS=dU/dtheta2; new tau2=tauG-tauS is residual demand, applied CCW motor=-tau2; tau4 unchanged. Actual Link2 FBD/reaction and virtual-work checks include spring. Full-domain theta/height graphs toggle90–180/90–270; motion/headline bounds remain independent. Four torque series and six new CSV columns; legacy imports disable spring/preserve nt defaults. Fixed-alpha global peaks use conservative smooth/slack spring interval bounds; alpha-box peak API rejects enabled-spring multi-alpha searches. No existing V1/V2 or shared engineering code changed.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** V3 passes28616 assertions over450 varied poses and14 bounded peak cases; max force3.22e-13 N/moment7.11e-14 Nm/energy-derivative5.94e-9 Nm. Existing V1/V2 checks pass3853/16044/29863 assertions. Dense18001-point sample reproduces support0.977968–1.022031 and1.25254 Nm working residual; a first check exposed previous coarse-minimum sampling, corrected against finer unchanged-parameter data. Actual browser verifies270 motion,180/270 theta/height graph domains, A/B, preload, spring off/slack, V3 JSON restoration, legacy nt migration,23 finite SVGs and empty warnings/errors. Actual CSV1444x37 has residual identity<=1.01e-12 Nm and exact applied-motor sign. PNG/SVG geometry/full-range figures visually reviewed and adjusted for label spacing. Local standalone manual CMD provided; HTTP preview checked200, direct file/default-browser launching remains manual. No hardware/canonical physics claim.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated analytical member app. Spring force/stroke ratings, damping, strength, friction and real inversion are unvalidated; projected overlap is excluded per user instruction. Fetched origin/main and fast-forwarded the clean checkout to3908c3b, preserving V1/V2; no commit/push.

## 4. Compute Saving Handoff State

Use v3-spring.html and v3-model.md for the compact direct hip horn, parameter conventions and residual-demand signs.
The sample is an approximate ±2.20% fit over100–165°, reverses spring torque near246.874° and reaches about25.16 Nm residual near268° overfulltravel.
Keep V1/V2 unchanged, use the V3 checker and manual offline launcher, and resolve physical spring ratings before treating this exploratory fit as hardware.

---

## Entry: 2026-10-18 — Jonathan Xie — VSL V4 finite hip pulley

## 1. Scope & Objective

- **Target Subsystem:** Jonathan's isolated leg-solver member app.
- **Associated Issue/Task:** Replace direct spring with finite-radius fixed hip idler and remote spring; literal90-degree preload, local coordinates, optional driven scale, force headlines/multiples and plot bounds. Local save only; preserve V1/V2/V3.

## 2. Structural Modifications

- **Files Modified/Added:** Complete working-diff paths below include carried-forward, unchanged V3 artifacts from the previous local task.
- `ENTRY_TEMPLATE.md`
- `users/jonathan-xie/experimental-apps/leg-solver/.gitignore`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver v3.cmd`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver v4.cmd`
- `users/jonathan-xie/experimental-apps/leg-solver/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/plot-v3-sample.py`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-full-range.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-full-range.svg`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-hip-horn-geometry.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-hip-horn-geometry.svg`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-spring.html`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-verification.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-pulley.html`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-verification.json`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-pulley.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-spring.cjs`

- **API/Interface Changes:** Adds general-vsl/v4-pulley standalone HTML/JSON; local Su/Sv,nu,rh,rs,k,p0 and nullable springDriven. Finite tangency plus continuous wrap sets cable payout and tauS=Fs*cprime/1000; tau2=tauG-tauS, applied motor=-tau2. Nominal driver includes total mass and dimensionally required L2. Literal invalid90-degree tangency is flagged per user choice. Adds Fs/maxFs/pe, Current xg force entry, display-domain controls and43-column CSV; legacy imports disable new spring. Shared interfaces and prior versions unchanged.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** V4 passes57,524 assertions over600 varied poses and24 bounded maximum cases; independent payout/energy derivatives, tangent/unit direction, virtual work, FBD/pin/frame reaction balance, point-limit A/B exact cancellation, exclusive/all-independent drivers and graph domains. Max force4.69e-13 N, moment7.82e-14 Nm, energy derivative2.11e-7 Nm, payout derivative5.96e-8 mm/rad. Actual browser verifies input layout, total-mass force multiples, all plot options,23 finite SVGs, HTML subscripts, V4 save/reload and V3 migration, literal invalid-reference recovery, no warnings/errors. Actual CSV1446x43 residual identity<9.60e-13 Nm and exact applied sign. Tests corrected cross-realm assertion and13kg fixture; browser caught/fixed sweep-domain metadata and narrow force-column overflow. Manual offline launcher provided; identical HTML verified over temporary HTTP, file-launch automation untested. V1/V2/V3 hashes preserved. Required entry/scope/whitespace/link checks run after saving, with results reported in the task. No canonical/hardware acceptance.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace. Friction, bending, spring stroke/rating, strength, damping, real slack recovery and loaded inversion are unvalidated. Projected overlap is excluded per user instruction. Fetched origin/main; no commit/push.

## 4. Compute Saving Handoff State

Use v4-pulley.html and v4-model.md for the finite-radius idler, literal preload and residual-demand conventions.
The default p0=0 is intentionally not balanced; point-limit exact matching additionally needs p0=k*abs(Sv-rh), while finite rs uses the actual cable geometry.
Preserve all previous versions, run verify-pulley.cjs for changes and retain the chosen invalid90-degree reference guard before physical spring/stroke sizing.

---

## Entry: 2026-10-18 — Jonathan Xie — V4 applied CCW torque and preload fit

## 1. Scope & Objective

- **Target Subsystem:** Jonathan's isolated leg-solver member app.
- **Associated Issue/Task:** Make tau2 actual applied CCW motor, collapse hip panel, linear motor/percent plot and percentage headlines; diagnose and fit confirmed13kg finite-idler sample. Local code update only.

## 2. Structural Modifications

- **Files Modified/Added:** Complete current diff including carried-forward V3/original V4 artifacts below; earlier version files are unchanged by this revision.
- `ENTRY_TEMPLATE.md`
- `users/jonathan-xie/experimental-apps/leg-solver/.gitignore`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver v3.cmd`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver v4.cmd`
- `users/jonathan-xie/experimental-apps/leg-solver/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/plot-v3-sample.py`
- `users/jonathan-xie/experimental-apps/leg-solver/tune-pulley-sample.py`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-full-range.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-full-range.svg`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-hip-horn-geometry.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-hip-horn-geometry.svg`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-spring.html`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-verification.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-pulley.html`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-sample-13kg-fitted.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-sample-13kg-point-rule.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-tuning.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-tuning.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-tuning.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-verification.json`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-pulley.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-spring.cjs`

- **API/Interface Changes:** V4 tauG=unassisted applied CCW motor, tauS=-Fs*cprime/1000 physical spring couple, tau2=tauG-tauS=tau2Applied; previous displayed demand signs reverse, physical motor/FBD solution unchanged. CSV keeps43 columns with updated signs; JSON adds torqueConvention=applied-ccw. Linear dual trace uses tau2 Nm and100*tau2/abs(tauG) at same pose, singular reference undefined; global percent uses torque-peak pose. Adds collapsed state control, tiny-value precision, model/report/presets/reproducible fit script and compact evidence. No shared runtime/interface or V1-V3 modifications.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** 83,803 assertions pass over600 varied poses,24 bounded peak cases, applied-sign/preload slope/percent checks and26004 full embedded-model sample poses reproducing independent SciPy fit evidence. Force4.69e-13N,moment7.82e-14Nm,energy-derivative2.11e-7Nm,payout derivative5.96e-8mm/rad maxima. Four independent65001-point sweeps retain product-only25.51484%, point-preload0.800255%, local minimax0.000392529% and roundoff-exact point limit. Fit uses explicit Su[-5,5],rh[85,105],p0[0,200] bounds and1301-point objective; not global optimality. Production CSV handler capture1446x43 has residual identity<=9.46e-13Nm and exact tau2/applied equality. Actual browser passes preload rise, collapse/reopen, fitted import, tiny values, zero-tauG undefined percent, expanded/clamped linear traces,23 finite SVGs and no warnings/errors. CSV harness initially used CommonJS reserved exports binding; corrected to exportCode without weakening checks. Manual file launcher is unchanged; identical HTML tested over temporary HTTP, default-browser launch not automated. Required scope/entry/link/whitespace checks run after save and reported in task. Initial entry check rejected a missing separator after the validation-field colon; corrected formatting only, without changing evidence or gate logic.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated analytical workspace. Real spring/cable tolerances, friction, bending, stroke/rating, strength and dynamics remain unvalidated; no physical accuracy claim. V1/V2/V3 hashes preserved; no commit or push.

## 4. Compute Saving Handoff State

Use v4-pulley.html and revised v4-model.md for actual applied CCW signs, linear dual-axis residual plot and same-pose percentages.
Load v4-sample-13kg-fitted.json with all spring drivers off; v4-tuning.md explains product scaling plus matching preload and the finite-radius correction.
Preserve V1-V3, retain literal90-degree tangent guard and distinguish ideal numerical fit from hardware tolerances before spring selection.

---

## Entry: 2026-10-18 — Jonathan Xie — V4 10mm textbook and mg compensation

## 1. Scope & Objective

- **Target Subsystem:** Jonathan's isolated leg-solver member app.
- **Associated Issue/Task:** Add10mm-radius textbook fit and bounded finite matching control; user clarified graph/headline percentage as effective support error relative to1mg, separate from raw applied CCW motor torque. Local save only.

## 2. Structural Modifications

- **Files Modified/Added:** Full current diff includes carried-forward V3/original V4/local refinement artifacts; V1/V2/V3 HTML remains unchanged by this task.
- `ENTRY_TEMPLATE.md`
- `users/jonathan-xie/experimental-apps/leg-solver/.gitignore`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver v3.cmd`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver v4.cmd`
- `users/jonathan-xie/experimental-apps/leg-solver/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/plot-v3-sample.py`
- `users/jonathan-xie/experimental-apps/leg-solver/tune-pulley-sample.py`
- `users/jonathan-xie/experimental-apps/leg-solver/tune-pulley-textbook.py`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-full-range.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-full-range.svg`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-hip-horn-geometry.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-hip-horn-geometry.svg`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-spring.html`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-verification.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-pulley.html`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-sample-13kg-fitted.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-sample-13kg-point-rule.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-textbook-10mm.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-textbook-10mm.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-textbook-verification.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-textbook.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-tuning.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-tuning.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-tuning.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-verification.json`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-pulley.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-spring.cjs`

- **API/Interface Changes:** Adds VSLFit.fit bounded sampled numerical rh/Su/p0 calculation holding k/Sv/rs/nu and leg geometry, with multistart2D Nelder-Mead and affine Chebyshev preload elimination. New fit button turns all nominal drivers off and reports checked error; invalid current reference may be repaired by valid fitted geometry. Default/Reset/textbook uses13kg,rs10 fit. VSLStatic.compensationPercent=100*(spring support ratio-1); zero weight/Jz undefined, independent of prescribed Fz. Separate linear torque/compensation graphs and same-pose headline error replace residual/tauG normalization. Signs remain actual CCW tau2=tauG-tauS, tau2Applied=tau2. Adds reproducible SciPy fit, report, complete preset and compact PNG/JSON; no shared runtime or canonical model changes.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** 91,128 analytical/model/fitter assertions pass:600 varied poses,24 bounded torque peak cases, both0.1/10mm browser fit algorithms and held parameters, 0.9/1/1.1mg maps to-10/0/+10%, zero stiffness/mass fit rejection,6501 embedded textbook samples plus26004 comparison samples. Independent seven-start SciPy/SLSQP1001-angle minimax and65001-angle verification retain Su7.1579230735,rh89.416035166,p0149.918334501,0.06208975% max support error,0.037294803Nm max motor,pe195.954394N,maxFs963.065307N. Browser181-angle fitter/6501-pose verification achieves0.06219%; bounded sampled local fit, not continuous/global certificate. Actual browser verifies fit from invalid reference draft, held k/Sv/rs/nu, nominal drivers off, textbook reset, independent raw/compensation graphs, proper±10% labels, collapse/reopen, Fz independence, zero-weight undefined result,24 finite SVGs and no warnings/errors. Existing production CSV43-column sign/identity capture still passes. Figures visually inspected; old CSV harness reserved binding and missing log-field space were corrected without weakening checks. V1-V3 hashes preserved. Scope/entry/link/whitespace checks run after saving and reported in task; manual offline launcher unchanged, browser QA uses identical HTML over temporary HTTP.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated analytical member app. No hardware strength/rating/stroke, tolerance, cable bending/friction or dynamic validation claimed. Exact matching is only established for the specified point-pulley limit; finite fit is approximate. No commit/push.

## 4. Compute Saving Handoff State

Use v4-pulley.html with its new10mm textbook default and v4-textbook.md/JSON for explicit assumptions, joint rh/Su/p0 fit and reproduction.
Percent now means effective support/mg minus one; raw applied CCW motor torque is a separate graph and unchanged in physical meaning.
Keep nominal drivers off for finite fitted examples, refit after held-value changes, retain the literal90deg guard and preserve V1-V3.

---

## Entry: 2026-10-19 — Andy Zhang workspace — preserve source and return to PC

## 1. Scope & Objective

- **Target Subsystem:** Andy's experimental app context and historical source archive.
- **Associated Issue/Task:** User requested updating and pushing all Capstone code, context and documentation for moving the workflow back to the PC. The clean checkout fast-forwarded from 3908c3b to fetched e91897a; existing maintained source was already published. Preserve remaining app-local historical source and provide a current PC continuation map.

## 2. Structural Modifications

- **Files Modified/Added:** Exact outgoing paths below; no deletions or changes to original ignored source.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/README.md`
- `users/andy-zhang/experimental-apps/capstone-archive/README.md`
- `users/andy-zhang/experimental-apps/capstone-archive/context.md`
- `users/andy-zhang/experimental-apps/capstone-archive/context/README.md`
- `users/andy-zhang/experimental-apps/capstone-archive/development-history-2026-10-19.json`
- `users/andy-zhang/experimental-apps/capstone-archive/restore_development_history.py`
- `users/andy-zhang/experimental-apps/context.md`
- `users/andy-zhang/experimental-apps/laptop-handoff.md`
- `users/andy-zhang/experimental-apps/pc-handoff.md`

- **API/Interface Changes:** Archive-only restore_development_history.py adds optional --source PACKAGE.json and capstone-historical-source/v2 per-file gzip-base64 decoding, while preserving the v1 default package, original sizes/SHA-256, path checks and new-directory-only behavior. New 14-file supplement preserves the superseded fixed-15-degree study's source, static HTML/PDF, selected JSON evidence and checks plus two historical browser inspection scripts. Update PC handoff, app/archive indexes and historical laptop pointer. No production API, model, dependencies, launcher, port, shared policy or canonical asset changes; Jonathan's fetched solver remains in its owning folder.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Python 3.13.12 restoration round trips pass for all 14 new files against untouched local originals and all 21 old supplement files against retained size/SHA-256. Existing destinations are rejected for both versions; traversal, checksum mismatch and unknown encoding each fail before output creation. New package is 520,678 bytes for 1,519,499 original bytes, below the 1 MiB blob limit. All 85 local Markdown links resolve and fences balance; git diff --check passes. Initial clean main and full-history checkout verified; fetched and fast-forwarded to e91897a, .githooks installed. Required working/staged/outgoing entry and scoped-gate commands run before publication. No archived payload code is executed. App/model suites, numerical searches, browser/native/GPU checks and destination-PC startup/restart are not rerun or certified by this source-transfer update.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated archive/context contribution. The entry read found missing users/jonathan-xie/experimental-apps/leg-solver/AGENTS.md at the fetched base; dependent work on that app stopped, no solver files were changed or executed, and the PC handoff records the missing file. Current browser profiles, installed environments, caches, generated bundles, raw runs/logs and private account/chat data are not transferred through Git. Historical numerical claims remain dated evidence, and the cancelled fixed-15-degree method remains superseded.

## 4. Compute Saving Handoff State

Read users/andy-zhang/experimental-apps/pc-handoff.md for the latest PC continuation map, existing launchers, source boundaries and copyable prompt.
All maintained app code is already in main; the new 14-file archive supplement retains otherwise ignored historical source/report work with verified exact restoration, while both older packages and originals stay intact.
Update the PC checkout while preserving local edits, rebuild only the needed local environments and verify actual startup there before claiming runtime readiness; retain current RMS/curved-path studies and all rejected-design history.

---

## Entry: 2026-10-19 — Andy Zhang workspace — suspension actuator sizing and Jon V4

## 1. Scope & Objective

- **Target Subsystem:** Motion Lab experimental sizing UI and Jonathan V4 integration.
- **Associated Issue/Task:** User requested pulling the latest Motion Lab, adding constant-lift suspension/link/chassis-driven torque-speed bands and feasibility contours using Flipsky motors and EG23 gearboxes, filling the supplied motor workbook, matching its compact formatting, integrating Jon V4 and leaving a note about his missing AGENTS.md. Clean main fast-forwarded from c6a79b5 to 5d9dfa2. User explicitly asked to ignore the missing app instruction file for now after its protocol blocker was explained.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths below; no deletions.
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/actuator-sizing.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_motion_lab.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_sizing.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/server.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/test_vsl_integration.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/sizing.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/vsl_integration.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/motion.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/sizing/app.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/sizing/catalog.json`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/sizing/index.html`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/sizing/model.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/sizing/style.css`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/sizing/vsl-bridge.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/sizing/vsl-theme.css`
- `users/jonathan-xie/experimental-apps/leg-solver/context/2026-10-19-agent-entry-note.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/README.md`

- **API/Interface Changes:** Add main tabs ?tab=sizing and ?tab=vsl. Basic sizing includes explicit constant-lift spring law, unequal-link fixed-2:1 geometry, prescribed-heave inertial terms, hip/knee power-preserving conversion, 54 conditional catalog combinations, nominal/momentary torque-speed envelopes and mass/link utilization boundary. Catalog is verified Google Sheets readback (nine Flipsky rows and six gearbox listings), not live sync; native Gearboxes A1:AH7 was added with compact 8pt/9pt formatting, explicit units, source hyperlinks and caveats. CSV refresh, calculation JSON/demand CSV and browser library exports retain inputs/catalog provenance. /vsl-v4/ serves original sibling V4 HTML and explicit documentation/preset allowlist, adding only theme and bridge scripts; original inline scripts and all V1-V4 source files are preserved. V4 transfers 181 fixed-A quasi-static applied-CCW hip samples with speed derived from its actual Jz, rejects singular/reversing height branches and records source SHA-256. It remains separate from basic chassis mass contours; no inferred V4 contact force or dynamics. Add requested AGENTS housekeeping note, no replacement agent rules. Existing launchers/port4186 and canonical engineering components remain unchanged.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** npm run build passes. npm test passes all89 tests (eight new sizing cases verify independent potential derivatives, COM inertia, hip/knee power invariance, current/power/gear bounds, map consistency, CSV validation and invalid inputs). python -m unittest -v test_vsl_integration passes3 tests for original-script preservation, narrow resource access and preset bytes. Jon's original node verify-pulley.cjs passes91,128 assertions. Actual node scripts/verify_sizing.cjs passes54 combinations,101 basic poses,181 exact V4 source torque/speed comparisons, fixed-spring mass changes, explicit retuning, coordinate conversion, invalid values, invalid/valid CSV refresh, reset, JSON export, library save, tab state, native-GUI guard, singular V4 rejection, source transfer, shared themes and390px responsiveness without page errors. Original node scripts/verify_motion_lab.cjs passes live solver APIs, comparisons, library/import/reload, recorded playback, mocked native GUI and mobile workflows. Desktop/mobile screenshots inspected. Start Motion Lab.cmd tested from unrelated CWD: verified existing-server reuse, scoped stop, restart and actual health plus V4 route200 on127.0.0.1:4186. Spreadsheet readback confirms6 rows, nominal torques28/10/30/25, source links, notes and8pt/9pt fonts; Google-rendered verification unavailable because browser is not signed in. Markdown links and git diff --check pass; required entry/scoped publication gates run after log save. Initial numeric HTML step mismatch fixed with bounded fractional inputs; mobile test now waits for asynchronous Plotly resize. First broad browser regression was interrupted by the separate server restart test, then passed when rerun sequentially. Two authoring helpers used a wrong CWD and made no edits; corrected paths succeeded. No physics or thermal claims inferred from these checks.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to these isolated member workspaces. Motors' continuous thermal limits, phase-current convention, loaded voltage drop, peak duration, controller/battery regeneration, rotor/reflected inertia, tire contact, mechanical adapter fit and real spring packaging remain unverified. Marketing max values and gearbox momentary values are not continuous ratings. Missing Jon AGENTS.md remains recorded for his next session; the user's task-specific waiver does not change shared agent rules.

## 4. Compute Saving Handoff State

Open the unchanged project-local Start Motion Lab.cmd and use Suspension & actuator sizing or Jon V4 from the main navigation at port4186.
Read docs/actuator-sizing.md for formulas, sheet provenance, explicit CSV refresh and the separation between basic heaving-chassis assumptions and V4 fixed-A prescribed loads; transfer V4 again after editing it.
The next engineering work is measured motor/controller thermal and voltage characterization, adapter and spring packaging, actual motion duty/contact inputs, and Jonathan's reviewed app AGENTS.md publication; no canonical robot validation has been substituted.

---

## Entry: 2026-10-20 — Yulai Duan — passive block-descent studies for sharing

## 1. Scope & Objective

- **Target Subsystem:** Isolated passive-descent member experiment and curated research evidence.
- **Associated Issue/Task:** User requested publishing the recent study batch and explicitly authorized push/merge. Start from current main 307aae0, preserving the older local checkout and unrelated team work. Explain how chassis descent supplies missing reach without implying controlled landing or restored ride height.

## 2. Structural Modifications

- **Files Modified/Added:** Exact outgoing paths below; no deletions.
- `ENTRY_TEMPLATE.md`
- `context/users/yulai-duan/2026-10-20-codex-descent-studies.md`
- `context/users/yulai-duan/README.md`
- `docs/README.md`
- `docs/benchmarks/2026-10-18-jon-descent-heights/README.md`
- `docs/benchmarks/2026-10-18-jon-descent-heights/assets/height-profiles.png`
- `docs/benchmarks/2026-10-18-jon-descent-heights/results.json`
- `docs/benchmarks/2026-10-18-jon-single-leg-descent/README.md`
- `docs/benchmarks/2026-10-18-jon-single-leg-descent/assets/descent-closeup.png`
- `docs/benchmarks/2026-10-18-jon-single-leg-descent/assets/descent-profile.png`
- `docs/benchmarks/2026-10-18-jon-single-leg-descent/results.json`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/README.md`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/assets/01-descent-comparison.pdf`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/assets/01-descent-comparison.png`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/assets/02-chassis-reaction.pdf`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/assets/02-chassis-reaction.png`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/assets/03-grounded-versus-airborne.pdf`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/assets/03-grounded-versus-airborne.png`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/assets/04-geometry-and-travel.pdf`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/assets/04-geometry-and-travel.png`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/assets/05-drift-and-clearance.pdf`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/assets/05-drift-and-clearance.png`
- `docs/benchmarks/2026-10-19-jon-baseline-descent/results.json`
- `docs/benchmarks/README.md`
- `docs/design/simulation/assets/descent-profile-feasibility.pdf`
- `docs/design/simulation/assets/descent-profile-feasibility.png`
- `docs/design/simulation/assets/descent-profile-results.json`
- `docs/design/simulation/descent-studies.md`
- `docs/design/simulation/obstacle-profile.md`
- `users/yulai-duan/experimental-apps/README.md`
- `users/yulai-duan/experimental-apps/block-descent-study/.gitignore`
- `users/yulai-duan/experimental-apps/block-descent-study/AGENTS.md`
- `users/yulai-duan/experimental-apps/block-descent-study/README.md`
- `users/yulai-duan/experimental-apps/block-descent-study/analyze_profile.py`
- `users/yulai-duan/experimental-apps/block-descent-study/context/README.md`
- `users/yulai-duan/experimental-apps/block-descent-study/encode_jon_descent_video.swift`
- `users/yulai-duan/experimental-apps/block-descent-study/inputs/README.md`
- `users/yulai-duan/experimental-apps/block-descent-study/inputs/screenshot-baseline.json`
- `users/yulai-duan/experimental-apps/block-descent-study/inputs/spring-reference.json`
- `users/yulai-duan/experimental-apps/block-descent-study/inputs/v4-model.md`
- `users/yulai-duan/experimental-apps/block-descent-study/inputs/v4-pulley.html`
- `users/yulai-duan/experimental-apps/block-descent-study/inputs/v4-textbook-10mm.json`
- `users/yulai-duan/experimental-apps/block-descent-study/inputs/verify-pulley.cjs`
- `users/yulai-duan/experimental-apps/block-descent-study/jon_baseline_descent.py`
- `users/yulai-duan/experimental-apps/block-descent-study/jon_descent_height_sweep.py`
- `users/yulai-duan/experimental-apps/block-descent-study/jon_descent_source_reference.cjs`
- `users/yulai-duan/experimental-apps/block-descent-study/jon_single_leg_descent.py`
- `users/yulai-duan/experimental-apps/block-descent-study/publication-provenance.json`
- `users/yulai-duan/experimental-apps/block-descent-study/publication-validation.json`
- `users/yulai-duan/experimental-apps/block-descent-study/requirements.txt`
- `users/yulai-duan/experimental-apps/block-descent-study/verify_publication.py`

- **API/Interface Changes:** No shared runtime/assets/controllers/interfaces change. Import the four study records into an isolated member toolkit with pinned inputs, dependencies, context and portable paths/Node/font discovery. Keep original compact result provenance and add a reproduction comparison plus team sharing index. Publish selected PNG/PDF evidence; exclude raw runs/logs/video/private chat/screenshots. Batch scripts write only ignored app-local results; no localhost service or startup automation.

## 3. Local Validation Checklist

- **Validation Scope:** preliminary
- **Research/Policy Validation:** Reran 11 legacy single-leg cases, ten legacy height cases, 22 new-baseline cases and analytical quintic screening from the portable app with Python 3.11.16, MuJoCo 3.14.0, NumPy 2.4.6, Matplotlib 3.10.9 and Pillow 12.3.0. verify_publication.py passes 796 physical-metric comparisons with zero error; passive-trace SHA-256 and analytical values match; all nine PNG figures are pixel-identical. Source spring, geometry, Jacobian, energy, airborne ODE and timestep/contact checks pass as recorded. Entry architecture passes for all 754 repository files and 51 changed paths; preliminary gate passes all 36 regression tests. Initial link check found four missing companion links in the copied model note, corrected to pinned GitHub originals; initial whitespace check found a trailing blank log line, corrected. Recheck links/whitespace and exact staged/outgoing snapshots before publication. Canonical robot, full vehicle, hardware, motor/gearbox and cross-platform optional rendering/AVFoundation encoding are not certified.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to these isolated member experiments and curated research paths. Fixture integration checks are experimental evidence, not an approved robot baseline. Local original studies stay intact; no force push or policy/protection bypass is used.

## 4. Compute Saving Handoff State

Start at docs/design/simulation/descent-studies.md for plots, fixture explanations and dated records, then read the portable app README for reproduction.
The new 8.75kg/20deg/200mm-wheel held-hip 100/150mm cases land at 275/299ms; 250/300mm exceed the remaining 156.6mm stroke, and heave restores contact through chassis descent/stop hits without establishing controlled recovery.
Next resolve masses/support load, define landing/braking objectives and add actual drivetrain limits plus four-leg load sharing before choosing hardware; publication-validation.json records the exact reproduced evidence.

---

## Entry: 2026-10-21 — Jonathan Xie — VSL version folders, automatic exit angle and Excel config library

## 1. Scope & Objective

- **Target Subsystem:** Jonathan's isolated VSL member calculator and path-only sibling consumers.
- **Associated Issue/Task:** User requested inverse drive ratios, rw200mm, total mass8.75kg, force ×g preservation, working-range maximum-required ζ, version folders and an explicit local Excel config library. Keep p₀ extrapolated at90° if wrap is absent there; still reject a90° pin inside/on S. Local changes only; no commit or push requested.

## 2. Structural Modifications

- **Files Modified/Added:** Exact changed paths including both sides of moves:
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/leg-design-study/context/README.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/force-travel-study.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/generalized-leg-math.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/generalized-leg-physics.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/generalized-leg-study.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/inversion-path-study.md`
- `users/andy-zhang/experimental-apps/leg-design-study/docs/revisions.md`
- `users/andy-zhang/experimental-apps/leg-design-study/index.html`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_design_report.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/build_inversion_report.py`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_curved_report.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_force_report.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_inversion_report.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_rms_links.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_sweep_brief.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/scripts/verify_unequal_report.cjs`
- `users/andy-zhang/experimental-apps/leg-design-study/tests/design-study.test.js`
- `users/andy-zhang/experimental-apps/pc-handoff.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/actuator-sizing.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/docs/merged-linkage.md`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/build_jon_models.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/jon_reference_fixtures.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/scripts/verify_sizing.cjs`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/design-examples.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/tests/merged-linkage.test.js`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/vsl_integration.py`
- `users/andy-zhang/experimental-apps/wheel-leg-lab/web/sizing/vsl-bridge.js`
- `users/jonathan-xie/experimental-apps/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/.gitignore`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver v2.cmd`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver v3.cmd`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver v4.cmd`
- `users/jonathan-xie/experimental-apps/leg-solver/Open Leg Solver.cmd`
- `users/jonathan-xie/experimental-apps/leg-solver/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/2026-10-19-agent-entry-note.md`
- `users/jonathan-xie/experimental-apps/leg-solver/context/README.md`
- `users/jonathan-xie/experimental-apps/leg-solver/plot-v3-sample.py`
- `users/jonathan-xie/experimental-apps/leg-solver/tune-pulley-sample.py`
- `users/jonathan-xie/experimental-apps/leg-solver/tune-pulley-textbook.py`
- `users/jonathan-xie/experimental-apps/leg-solver/v1-kinematics.html`
- `users/jonathan-xie/experimental-apps/leg-solver/v2-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-full-range.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-full-range.svg`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-hip-horn-geometry.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-hip-horn-geometry.svg`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-spring.html`
- `users/jonathan-xie/experimental-apps/leg-solver/v3-verification.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-model.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-pulley.html`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-sample-13kg-fitted.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-sample-13kg-point-rule.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-textbook-10mm.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-textbook-10mm.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-textbook-verification.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-textbook.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-tuning.json`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-tuning.md`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-tuning.png`
- `users/jonathan-xie/experimental-apps/leg-solver/v4-verification.json`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-global-maxima.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-kinematics.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-pulley.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-quasi-static.cjs`
- `users/jonathan-xie/experimental-apps/leg-solver/verify-spring.cjs`
- `users/jonathan-xie/experimental-apps/vsl-solver/.gitignore`
- `users/jonathan-xie/experimental-apps/vsl-solver/Open VSL Solver v4.cmd`
- `users/jonathan-xie/experimental-apps/vsl-solver/README.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/context/2026-10-19-agent-entry-note.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/context/README.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v1/Open Leg Solver.cmd`
- `users/jonathan-xie/experimental-apps/vsl-solver/v1/README.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v1/v1-kinematics.html`
- `users/jonathan-xie/experimental-apps/vsl-solver/v1/verify-kinematics.cjs`
- `users/jonathan-xie/experimental-apps/vsl-solver/v2/Open Leg Solver v2.cmd`
- `users/jonathan-xie/experimental-apps/vsl-solver/v2/README.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v2/v2-model.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v2/v2-quasi-static.html`
- `users/jonathan-xie/experimental-apps/vsl-solver/v2/verify-global-maxima.cjs`
- `users/jonathan-xie/experimental-apps/vsl-solver/v2/verify-quasi-static.cjs`
- `users/jonathan-xie/experimental-apps/vsl-solver/v3/Open Leg Solver v3.cmd`
- `users/jonathan-xie/experimental-apps/vsl-solver/v3/README.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v3/plot-v3-sample.py`
- `users/jonathan-xie/experimental-apps/vsl-solver/v3/v3-full-range.png`
- `users/jonathan-xie/experimental-apps/vsl-solver/v3/v3-full-range.svg`
- `users/jonathan-xie/experimental-apps/vsl-solver/v3/v3-hip-horn-geometry.png`
- `users/jonathan-xie/experimental-apps/vsl-solver/v3/v3-hip-horn-geometry.svg`
- `users/jonathan-xie/experimental-apps/vsl-solver/v3/v3-model.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v3/v3-spring.html`
- `users/jonathan-xie/experimental-apps/vsl-solver/v3/v3-verification.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v3/verify-spring.cjs`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/Open Leg Solver v4.cmd`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/Open VSL Solver v4.cmd`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/README.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/config-library-columns.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/config-library-model.js`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/tune-pulley-sample.py`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/tune-pulley-textbook.py`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-configs.xlsx`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-default-library.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-model.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-pulley.html`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-sample-13kg-fitted.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-sample-13kg-point-rule.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-textbook-10mm.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-textbook-10mm.png`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-textbook-verification.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-textbook.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-tuning.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-tuning.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-tuning.png`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-verification.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/verify-library.cjs`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/verify-pulley.cjs`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/verify_excel.py`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/vsl_server.py`

- **API/Interface Changes:** Rename leg-solver→vsl-solver and place each version in v1/v2/v3/v4. V4 qdc=rd/rc and qfe=rf/re; all physical radii/legacy driven imports retain meaning. Automatic fixed CW exit rotation is selected from analytic wrap extrema; 90° extrapolated payout cancels the constant routing offset in spring force/torque. Snapshot library adds stable DP IDs, explicit row Save/Load, selection/order/color/pin and 75 columns. Local Python stdlib HTTP bridge on127.0.0.1:8767 supports explicit XLSX saves, revisions, atomic replacement, prior-version backup and optional Tk Browse; normal launch reads v4-configs.xlsx. Standalone file HTML still calculates without Excel. Sibling readers/links point to version folders; Motion Lab serves the library-model dependency and hides the standalone Excel UI in its embedded frame. No shared runtime/assets/controllers/policies change.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Initial entry check rejected a missing required Entry header, and the first whitespace check exposed CRLF churn in path-only consumers; corrected the new header and preserved original consumer line endings before final recheck. Staged tests pass: V1 3853, V2 statics16044/global29863, V3 28616, V4 91128 model assertions; 15037 library/ratio/mass/ζ checks and eight stdlib XLSX tests. V1–V3 HTML SHA256 preserved. Artifact Tool authors/recalculates/renders/inspects the initial75-column XLSX with one8.75kg baseline; no formula errors. Browser checks mass10kg→Fz98.1N at1g, qdc2→rd70/rc35, immutable row saves/load, group move, shading, pin/collapse, separate workbook Save Excel and unsaved cross-workbook draft recovery. Positive ζ62.735147° over100–270° retains wrap and displays extrapolated p₀; defaultζ−53.305793° stays horizontal. All24 SVGs finite, browser warning/error logs empty. Manual launcher starts from an unrelated working directory and repeated launch reuses server. Final repository path/link, entry/gate and installed-start checks are recorded in the delivery; native Tk picker and full Motion Lab GUI/engine suites not rerun. Numerical checks are experimental consistency, not hardware acceptance.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member workspace and path-only sibling migration. No canonical assets or physical baseline changes.

## 4. Compute Saving Handoff State

Start from users/jonathan-xie/experimental-apps/vsl-solver/README.md and its root Open VSL Solver v4.cmd; direct HTML cannot automatically sync local Excel.
The default8.75kg finite10mm-pulley fit is approximate (about±0.1262% support error), with p₀330.869283N, r_h62.2269495mm and S_u9.38777673mm; ζ changes routing, not torque.
Use Row Save to capture a design and Save Excel to persist the library, preserve historical13kg fixtures and V1–V3 conventions, and resolve actual spring/cable/friction/3D and hardware constraints separately.

---

## Entry: 2026-10-21 — Jonathan Xie — flexible spring minimax fitting and physical hip torque signs

## 1. Scope & Objective

- **Target Subsystem:** Isolated VSL V4 member calculator, configuration state and model notes.
- **Associated Issue/Task:** User requested Driving checkboxes for all seven spring inputs, arbitrary fitted subsets, peak-motor minimization with warnings, compact controls and physical signed hip torques. User confirmed minimizing max absolute tau2 at current loads, retaining physical sign reversals and tau4's own drive-shaft convention. Preserve the prior local folder/library work and existing user workbooks.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths in this continuation:
- `ENTRY_TEMPLATE.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/README.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/context/README.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/README.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/config-library-columns.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/config-library-model.js`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-flex-fit-verification.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-model.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-pulley.html`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-verification.json`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/verify-fit.cjs`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/verify-library.cjs`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/verify-pulley.cjs`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/verify_excel.py`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/vsl_server.py`

- **API/Interface Changes:** Checked springDriving flags hold k/rh/Sv/rs/p0/nu/Su; unchecked values fit, with defaults holding k/Sv/rs/nu. The retired nominal driver no longer adjusts live fields; legacy resolved values still load. VSLFit.fit minimizes sampled peak absolute motor tau2 at fixed current alpha/beta/loads using interval/polygon linear k/p0 minimax and bounded multistart geometric search, followed by6501-pose verification. A background worker keeps the interface responsive; stale input changes discard results. No-free-variable, low-freedom, search-bound, zero-tension and ideal point-radius warnings appear beneath the fit button. Physical tauG=-old tauG and tau2=-tauG-tauS preserve motor/spring forces and energy. JSON/library snapshots persist all seven flags; legacy saved tauG outputs migrate idempotently. Excel files are not rewritten automatically; Save Excel persists the migrated representation. Remove two old buttons and duplicate sidebar alpha/theta controls; preserve phi0 and identify master endpoints. Legacy support-error fitting remains only for historical numerical evidence.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** 91128 V4 tangency/energy/FBD/peak assertions pass with the new gravity sign; 15041 library/ratio/mass/exit/migration assertions,3680 flexible-fit assertions and nine XLSX unit tests pass. Test zero through seven free inputs, exact one/two-linear-variable point cases, exact held-value preservation and physical signed balance/load reversal. Normal8.75kg finite10mm fit peaks at0.02377072Nm, verified6501 poses; all-free search reaches flagged ideal rs0 with roundoff residual. Real browser background fits, one-free and none-free warnings, all-seven-free point warning,75-column row mask save/load and separate-workbook round trip pass. Staging first exposed an incorrectly encoded test string and nonexistent worker script ID; both repaired before installation. Existing baseline workbooks and prior member edits are preserved. Final source/link/entry/gate checks and installed launch verification are reported in delivery. These are numerical/member-app checks; no physical spring, hardware or full Motion Lab engine validation claimed.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member app; no shared assets, runtime, policy or physical baseline changes.

## 4. Compute Saving Handoff State

Open the existing root VSL V4 launcher; checked spring Driving values stay fixed and unchecked values fit only when requested, with all selections saved in config snapshots.
Hip signs now obey tau2+tauG+tauS=0 with each positive CCW on Link2, while actual motor torque is unchanged and tau4 retains its drive-shaft sign.
Use the result box and bounds tooltip, retain rs as Driving for a chosen real pulley, and explicitly Row Save/Save Excel after fitting or migrating a legacy library; numerical search is bounded and sampled, not a global or hardware certificate.

---

## Entry: 2026-10-22 — Jonathan Xie — support error autoscaling and signed kg axis

## 1. Scope & Objective

- **Target Subsystem:** VSL V4 hip pulley support-error chart.
- **Associated Issue/Task:** Fit the actual error range and show signed kg-equivalent and percent support differences.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-pulley.html`
- `users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-model.md`
- `users/jonathan-xie/experimental-apps/vsl-solver/context/README.md`
- **API/Interface Changes:** Support chart fits finite sampled min/max with8% padding, including one-sided curves; constant/empty series receive finite fallback bounds. Left ticks show Δkg=m_total*error_percent/100, right ticks percent, with both in hover. Negative kg means support below target weight. Raw torque, spring model, saved state and workbooks retain their behavior.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** All embedded scripts parse. Focused rendered-chart checks pass for mixed-sign, positive-only, negative-only, constant-zero/nonzero and undefined zero-mass data, including −1kg=−10% at10kg. Live browser default spans−0.146320% to+0.146318%, rather than±10%; hover at100° shows−0.01104kg (−0.1261%) for8.75kg. Browser visual and console checks, repository entry/gate and whitespace checks complete before delivery. No physical model or workbook change; canonical robot tests not run.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member-app chart change.

## 4. Compute Saving Handoff State

The V4 support chart now autoscales and shows the same signed error in kg on the left and percent on the right.
The conversion is Δkg=Feq/g−m_total, so a negative value means deficient equivalent spring support.
Keep zero-weight/Jacobian undefined handling and separate raw-torque scaling; saved configurations and Excel require no migration.

---

## Entry: 2026-10-22 — Andy Zhang — Kinefold mechanism builder and front-left conventions

## 1. Scope & Objective

- **Target Subsystem:** New isolated Kinefold member app, first mechanism-builder and conventions workspaces.
- **Associated Issue/Task:** User requested a separately named combination-tool foundation using Motion Lab UI and Jon VSL v4 mechanism/cable spring, left grouped design inputs/right preview, complete toggleable conventions and x-forward/y-left/z-up coordinates.

## 2. Structural Modifications

- **Files Modified/Added:** Exact paths:
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/README.md`
- `users/andy-zhang/experimental-apps/kinefold/.gitignore`
- `users/andy-zhang/experimental-apps/kinefold/AGENTS.md`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/Start Kinefold.cmd`
- `users/andy-zhang/experimental-apps/kinefold/Stop Kinefold.cmd`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/context.md`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- `users/andy-zhang/experimental-apps/kinefold/conventions.js`
- `users/andy-zhang/experimental-apps/kinefold/index.html`
- `users/andy-zhang/experimental-apps/kinefold/model.js`
- `users/andy-zhang/experimental-apps/kinefold/preview.py`
- `users/andy-zhang/experimental-apps/kinefold/reference-v4.js`
- `users/andy-zhang/experimental-apps/kinefold/reference.json`
- `users/andy-zhang/experimental-apps/kinefold/style.css`
- `users/andy-zhang/experimental-apps/kinefold/variables.js`
- `users/andy-zhang/experimental-apps/kinefold/verify.cjs`
- **API/Interface Changes:** New `kinefold/mechanism-v1` JSON snapshot and self-contained browser app. Retain Jon V4 analytical blocks with LF-normalized source hashes; map old global y/z to new x/z by x=-old_y, z=old_z and old+x to new+y. All axial torque signs obey the right-hand rule. Expose V4 linear-coil/constant-lift reference and a distinct ideal constant-cable-force law; mass-following weight/global/contact modes, three belt preloads, exact finite-idler routing, side/isometric geometry, layer controls and kinematic playback. No source app, canonical asset, shared runtime, enforcement or accepted robot baseline is changed. App-local AGENTS.md is an inherited experiment scaffold, not a shared enforcement change.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** `node verify.cjs` passes 2000 assertions for source parity after LF normalization, 150 varied geometry/load cases, applied force/moment signs, FBD/virtual-work balance, both spring laws, energy finite differences and validated JSON; zero geometry error and max cable-energy derivative discrepancy1.74e-9Nm. Initial harness runs exposed an incorrect relative source path and Windows EOL assumptions, corrected without loosening numerical limits. Actual browser checks cover geometry edits, isometric/load layers, ideal constant force, pose scrub/play, mass10kg->Fz98.1N, global/contact conversion, invalid tangent feedback, empty pose rejection, independently expandable conventions/dictionary search, real JSON download/import and reload persistence; console warnings/errors empty. Windows project-local launcher starts from unrelated directories, reuses, stops only its scoped authenticated server and restarts at4191; assets HTTP200 and Python compile checked in final validation. Current desktop inspected; mobile, hardware and complete Motion Lab dynamic/native suites not run. Repository structure/log, require-passed, workspace gate and whitespace/link checks run before delivery. These are experimental consistency checks only.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated new member app and Markdown index/log; no robot physical baseline is changed.

## 4. Compute Saving Handoff State

Kinefold is a separate dependency-free app at users/andy-zhang/experimental-apps/kinefold, with grouped mechanism inputs, live geometry and a complete conventions tab.
Restart with its Start Kinefold.cmd at127.0.0.1:4191; preserve V4 coil versus constant-force distinctions, fixed-hip/prescribed-load limits, JSON schema and the proper front-left coordinate rotation.
Read its context/README.md and source provenance before future terrain/dynamics additions; Motion Lab's V4 embeds Jon's original math while its separate dynamic benches solve different fixtures, and that comparison stays out of the product.

---

## Entry: 2026-10-22 — Andy Zhang — Kinefold x-left preview and right-hand-rule illustrations

## 1. Scope & Objective

- **Target Subsystem:** Kinefold preview camera, conventions and app context.
- **Associated Issue/Task:** User requested the whole mechanism preview flipped so +x points left and +z up, with matching conventions and torque directions.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/conventions.js`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- **API/Interface Changes:** Side and oblique projections reverse horizontal screen coordinates; labels/dimensions remain readable. +y points toward the viewer in the left-side view and positive +y torque appears counterclockwise. Mirrored convention overview, counterclockwise torque arc and searchable definitions agree. Physical coordinates, analytical equations and JSON schema retain their meanings. Corrects the initial verbal description of y pointing into the screen.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Existing `node verify.cjs` passes 2000 assertions with unchanged geometry/force results. JavaScript parsing succeeds. Actual browser inspection shows the complete flipped mechanism, x-left/z-up axes, correct dot/out-of-screen y marker and counterclockwise torque illustration; baseline numerical cards remain unchanged. Prior project-local launcher start/reuse/stop/restart verification remains applicable because launcher/runtime files are unchanged. Final repository entry/require-passed/workspace and whitespace checks run before delivery. No hardware, terrain or dynamics validation is claimed.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member UI/convention correction.

## 4. Compute Saving Handoff State

Kinefold now draws the entire mechanism with forward +x to the left and +z up.
The front-left leg remains in its physical frame, with +y toward the viewer and positive +y torque counterclockwise in side view.
Continue with the existing app-root launcher at127.0.0.1:4191 and preserve these camera/coordinate distinctions in future preview changes.

---

## Entry: 2026-10-22 — Andy Zhang — Kinefold launcher staging correction

## 1. Scope & Objective

- **Target Subsystem:** Kinefold launcher text and validation handoff.
- **Associated Issue/Task:** Complete validation/publication of the requested mechanism builder and x-left preview.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/Start Kinefold.cmd`
- `users/andy-zhang/experimental-apps/kinefold/Stop Kinefold.cmd`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- **API/Interface Changes:** Launcher text normalized to LF; commands, host, port and application behavior unchanged. Use the hooks' existing CAMEL_PYTHON environment override for this command because python3 resolves to a Windows Store alias. No hook bypass or shared enforcement change.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Initial staged whitespace check flagged launcher CRLF lines and the attempted commit stopped at the python3 Store alias before validation. Normalize only the two owned launchers, recheck real start/reuse/stop/restart and staged whitespace, then run the configured staged and pre-push gates with installed Python via CAMEL_PYTHON. Existing 2000 numerical assertions, UI/JSON verification and final repository workspace checks remain applicable; source/physics are unchanged.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member launcher/text correction.

## 4. Compute Saving Handoff State

The new Kinefold launchers now satisfy the repository's staged whitespace policy.
Use installed Python via the existing CAMEL_PYTHON override when this PC's python3 points to the Store alias; do not modify or bypass hooks.
The app remains at127.0.0.1:4191 with the full x-left/right-hand-rule preview and convention corrections.

---

## Entry: 2026-10-22 — Andy Zhang — Kinefold UI inspection and exact belt/pulley indicators

## 1. Scope & Objective

- **Target Subsystem:** Isolated Kinefold builder and conventions UI.
- **Associated Issue/Task:** User requested autonomous UI refinements keeping tab1 mechanism-only/tab2 conventions, x-left/z-up, then requested geometric correctness, a grid, belt rotation indicators and wheel/pulley index axes.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/README.md`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- `users/andy-zhang/experimental-apps/kinefold/index.html`
- `users/andy-zhang/experimental-apps/kinefold/style.css`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/conventions.js`
- `users/andy-zhang/experimental-apps/kinefold/preview-geometry.js`
- `users/andy-zhang/experimental-apps/kinefold/preview.py`
- `users/andy-zhang/experimental-apps/kinefold/verify-drawing.cjs`
- **API/Interface Changes:** New dependency-free preview-geometry module derives exact belt loops/material movement and all six pulley plus wheel index axes from the unchanged V4 model. Calibrated mm grid follows camera zoom/pan. Correct orthographic isometric projection; omit invented wheel thickness and label the remote coil housing schematic. Add viewport-sized rendering, readable part labels, Mechanism/Full travel/Spring detail framing, zoom/pan, independent layers, parameter navigation and direct variable-help links. Conventions gain global search, section navigation,81 individual entries and a same-scale baseline topology diagram. Existing JSON gains only optional view-layer booleans with backward-compatible defaults; model parameters, physical coordinates, torque signs and reference solver blocks are unchanged. The local server allowlist adds preview-geometry.js.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** `node verify.cjs` passes2000 existing checks and `node verify-drawing.cjs` passes1123 new index/radius/orthogonality and independent no-slip material-velocity checks on both wraps of all3 belt stages; max velocity error1.75e-7mm/rad. JS parsing passes. Actual SVG side-view ratios are1.500008 for each300mm link versus200mm wheel radius, and2.000025 for wheel radius versus100mm grid, consistent with0.001px SVG rounding. Browser verifies7 index axes,32 default material markers, pose-dependent belt payout, baseline wheel K0 cancellation, zoom125%,40/30px pan, belt hiding with all indices retained, group shortcuts, input-help search,theta2 alias and81-entry dictionary/topology. Console errors/warnings are empty. App-local server stop/start passes with the new asset whitelist; final asset/link, staged whitespace and repository workspace checks precede publication. Mobile/hardware/source-app dynamic suites are not rerun; this is analytical/view consistency only.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member UI/model-view change; no shared runtime, policy or physical baseline changed.

## 4. Compute Saving Handoff State

Kinefold keeps the requested builder/conventions split and x-left/z-up frame, with calibrated geometry, exact belt material markers and pulley/wheel index axes.
Use its current launcher at127.0.0.1:4191, inspect tiny parts with Spring detail or zoom/pan, and use input ? links and top-level reference search for definitions.
Preserve the distinction between ideal geometry and the schematic remote coil housing, and rerun both numerical suites when changing carrier-relative belt or body-angle mappings.

---

## Entry: 2026-10-22 — Andy Zhang — Kinefold static and quarter-model dynamic tabs

## 1. Scope & Objective

- **Target Subsystem:** Kinefold solver workspaces and local service connection.
- **Associated Issue/Task:** User requested a third Jon VSLv4 static tab, analytical dynamics and2D Pymunk dynamics, with explicit quarter-model indicators.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- `users/andy-zhang/experimental-apps/kinefold/index.html`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/solvers.js`
- `users/andy-zhang/experimental-apps/kinefold/style.css`
- `users/andy-zhang/experimental-apps/kinefold/preview.py`
- **API/Interface Changes:** Five accessible tabs and direct query URLs. Static results use current builder parameters through unchanged V4 core for signed torques,181-pose sweep, sampled peak, belt tensions and FBD residuals. Dynamic tabs embed existing independently configured Motion Lab SciPy/Pymunk benches, each with quarter-model badge, fixture boundaries and coordinate/input notice. Same-origin guarded POST /__kinefold_solvers starts/reuses the sibling durable launcher and verifies app/root health. No automatic V4-to-dynamic parameter conversion, shared-engine change or canonical model claim.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** JS parsing and existing3123 numerical/drawing assertions pass. Browser static baseline shows tau2-0.027Nm, Fs570.491N, sampled peak0.063Nm and zero-to-displayed-precision FBD residuals; connected dynamic frames and quarter-model notices render with no browser errors. Real1s analytical and Pymunk API runs each return1000 rows/112 frames with finite JSON. Analytical warnings empty; Pymunk reports its existing explicit-force timestep and ideal-rope caveat. Initial0.05s probe rejected by existing range validation, corrected to1s. Project-local Kinefold stop/start and lazy verified Motion Lab startup/reuse pass; final restart and repository gates run before delivery. No full source-engine regression, hardware or canonical physics validation is claimed.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member app integration.

## 4. Compute Saving Handoff State

Kinefold now has five tabs, with its V4 static workspace using builder inputs and two working quarter-model dynamic reference benches.
Dynamic benches retain their own setup and coordinate conventions, explicitly distinguish their fixtures from V4 routing, and start through the sibling durable launcher when opened.
Continue from the app README, preserve quarter-model indicators and avoid implying automatic builder-to-dynamic equivalence until an explicit mechanical mapping is implemented and verified.

---

## Entry: 2026-10-22 — Andy Zhang — Kinefold live static import refresh

## 1. Scope & Objective

- **Target Subsystem:** Kinefold static workspace and scope wording.
- **Associated Issue/Task:** Finish solver-tab integration with current builder inputs even when importing directly on the static tab; use GPT-6.1 Sol development with parent architecture review.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/index.html`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- **API/Interface Changes:** Selected static workspace receives the current primitive parameter snapshot after builder updates/imports. Global footer and opening descriptions reflect the five workspaces. V4 core, JSON schema and independent dynamic fixtures are unchanged.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** `node --check app.js`, `node verify.cjs` (2000 assertions) and `node verify-drawing.cjs` (1123 assertions) pass. Actual browser file import while static stays selected changes mass/pose to10kg/145deg and immediately shows Fz98.1N, hip torque -6.014Nm, spring tension678.474N and sampled peak7.044Nm. Restored8.75kg/132.5deg baseline. Browser warnings/errors empty; reloaded page shows corrected footer. Required entry/workspace gates run before publication. Launchers/services are unchanged from the start/restart-verified preceding entry; no hardware, full engine regression or canonical physics validation claimed.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member app correction.

## 4. Compute Saving Handoff State

The static tab now follows imported designs immediately without requiring a tab switch.
The five-tab UI retains independent quarter-model dynamics, and its footer accurately describes experimental models.
Preserve the current builder-to-static event boundary and do not imply automatic V4 dynamic routing or hardware validation.

---


## Entry: 2026-10-22 — Andy Zhang — Shared Kinefold designs and native coupled solvers

## 1. Scope & Objective

- **Target Subsystem:** Isolated Kinefold project library and fixed-hip mechanism solvers.
- **Associated Issue/Task:** User requested00 Designs with saved configurations/profiles and static, analytical and genuine2D Pymunk workspaces all using the mechanism builder model; GPT-6.1 Sol workers develop with parent architecture review.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/.gitignore`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/Setup Kinefold.cmd`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- `users/andy-zhang/experimental-apps/kinefold/conventions.js`
- `users/andy-zhang/experimental-apps/kinefold/designs.js`
- `users/andy-zhang/experimental-apps/kinefold/dynamic_model.py`
- `users/andy-zhang/experimental-apps/kinefold/dynamics.py`
- `users/andy-zhang/experimental-apps/kinefold/index.html`
- `users/andy-zhang/experimental-apps/kinefold/preview.py`
- `users/andy-zhang/experimental-apps/kinefold/project-store.js`
- `users/andy-zhang/experimental-apps/kinefold/requirements.txt`
- `users/andy-zhang/experimental-apps/kinefold/solver-style.css`
- `users/andy-zhang/experimental-apps/kinefold/solvers.js`
- `users/andy-zhang/experimental-apps/kinefold/style.css`
- `users/andy-zhang/experimental-apps/kinefold/variables.js`
- `users/andy-zhang/experimental-apps/kinefold/verify-projects.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify_dynamics.py`
- **API/Interface Changes:** Versioned project-v2 snapshots include exact mechanism parameters, view and shared solver profile; legacy mechanism-v1 migrates explicitly. Browser-local named library supports save/copy/rename/load/delete/undo and portable JSON without results. Native same-origin POST /api/dynamics accepts engine/params/runConfig and invokes this app's bounded .venv CLI; no sibling service/iframe remains. Both dynamic engines use the finite-idler mechanism, fixed hip A, locked theta4, prescribed loads, explicit moving masses and inertias, and travel-limit termination. Pymunk is actual constrained rigid bodies; preview distinguishes ideal belts/indices from actual linkage overlay and sampled residuals. Source apps, retained V4 core and canonical components are unchanged.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Existing3123 numerical/drawing assertions,14 project/library scenario groups,6 Python dynamics tests, all JS parsing and Python compilation pass. Source-static parity maximum2.84e-14Nm; holding drift max4.33e-5deg; dt.002/.001/.0005 Pymunk trajectory errors decrease. Real0.3s native API runs return31rows/31frames for both engines; actionable missing-environment503 and cross-origin403 verified. Browser checks verify library/profile persistence, complete-project export/import on static, duplicate/rename/delete/undo via accessible dialogs, shared holding torque, both engines holding, Pymunk release trajectory/scrub/export and stale results. Native prompt/confirm failed in IAB and were replaced with in-page dialogs; an initial fetch overlapped deliberate lifecycle restart and was retried. Explicit load/import now synchronously persists validated working state (typing stays debounced) and pagehide flushes, fixing an immediate-reload race; actual immediate reload preserves both loaded example and restored baseline. Actual app-local Setup plus Start reuse/Stop/restart from unrelated cwd pass at4191. Required repository entry/workspace gates run before publication. No hardware, terrain contact, floating chassis or canonical physics claim.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member app implementation.

## 4. Compute Saving Handoff State

Kinefold now stores named complete designs and uses one shared mechanism/profile for static and both native fixed-hip quarter-model dynamics.
Start the app with its existing launcher at4191; run Setup Kinefold.cmd once for its own pinned Python3.12+ solver environment, and export project JSON as a portable backup.
Preserve explicit inertia assumptions, timestep refinement, actual Pymunk residual reporting and the distinction between this fixed-hip test and terrain or whole-vehicle behavior.

---


## Entry: 2026-10-22 — Andy Zhang — Vertical chassis dynamics and exact V4 square input

## 1. Scope & Objective

- **Target Subsystem:** Native Kinefold floating quarter-model dynamics, saved profiles and world-frame preview.
- **Associated Issue/Task:** User corrected both dynamic models to vertically guided floating chassis, exact V4 baseline masses and150mm-high/150mm-wide square wheel input, with no guide rods or direct copied reference tabs.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- `users/andy-zhang/experimental-apps/kinefold/conventions.js`
- `users/andy-zhang/experimental-apps/kinefold/designs.js`
- `users/andy-zhang/experimental-apps/kinefold/dynamic_model.py`
- `users/andy-zhang/experimental-apps/kinefold/dynamics.py`
- `users/andy-zhang/experimental-apps/kinefold/index.html`
- `users/andy-zhang/experimental-apps/kinefold/project-store.js`
- `users/andy-zhang/experimental-apps/kinefold/solvers.js`
- `users/andy-zhang/experimental-apps/kinefold/variables.js`
- `users/andy-zhang/experimental-apps/kinefold/verify-projects.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify_dynamics.py`
- **API/Interface Changes:** Existing native dynamics endpoint now consumes floating-chassis profiles and returns dynamics-v2 world rows/frames, requested/applied input, vertical wheel-input reaction and explicit exact-square events. No gravity-sized support is applied twice. Genuine Pymunk chassis motion uses an ideal condensed linkage, explicitly distinguished from an all-body linkage simulation. Project-v3 migration preserves original geometry, old browser keys and archived fixed-hip profiles; positive-mass legacy designs receive a declared10mm transition. Native equilibrium heading, settings, dictionary and world-grid preview are updated. Source apps, retained V4 reference core and canonical components are unchanged.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Existing3123 model/drawing assertions,18 project-state scenarios,6 floating dynamics groups, JS parsing and Python compilation pass. Full unmodified V4 baseline6.5s browser/native API runs in both engines return656rows with5exact150mm jumps and duration termination; h/v continuous across jumps. Independent heave acceleration error1.14e-13m/s², source-static parity2.84e-14Nm, baseline cross-engine heave difference0.004197mm, energy residuals4.26e-14J/1.67e-6J; finite-rise errors halve with dt refinement. Browser verifies exact masses/profile export, preserved legacy config, native equilibrium baseline, worldframe/no-rods playback and actual end scrub. Actual Start reuse/Stop/restart from unrelated cwd passes at4191. Input transition budget is bounded; range clamping is limited to1e-10rad numerical roundoff, with explicit failure beyond. Required repository checks precede publication. Hardware, collision terrain, tire fidelity and four-leg behavior remain unverified. Unrelated Laptop Access launchers are preserved and excluded.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member app correction.

## 4. Compute Saving Handoff State

Both dynamic engines now move the chassis vertically under the same saved mechanism and exact150mm square baseline, with no invented link masses or rotor inertia.
Use the app-local launcher at4191 and project-v3 exports; old fixed-hip data remains preserved and migration is explicit.
Retain exact jump accounting, world-frame geometry, independent heave plots and the honest condensed-linkage Pymunk scope when extending the experiment.

---


## Entry: 2026-10-22 — Andy Zhang — V4 static-limit validation of floating dynamics

## 1. Scope & Objective

- **Target Subsystem:** Kinefold experimental floating-chassis analytical and Pymunk validation.
- **Associated Issue/Task:** User requested running both dynamic solvers as static and checking agreement with Jon's VSL v4.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- `users/andy-zhang/experimental-apps/kinefold/static-validation.md`
- `users/andy-zhang/experimental-apps/kinefold/validate_static.py`
- **API/Interface Changes:** None. Added standalone validation against original hash-verified Jon HTML analytical blocks executed directly by Node. No runtime/UI/profile, source app, launchers or canonical component changes. At beta0 the source gets total vertical force Mg and matching horizontal force; offset rim-vs-centre support is explicitly corrected by tauJon-tauFloating=rw*R*sin(beta)*K, R=Mg-FzExtra. Scope is hip torque, spring law, geometry, derived support and actual held chassis pose; belt/pin forces and independently measured contact reaction are not asserted.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** App .venv Python validate_static.py --output .preview/static-validation.json passes:63 direct beta0 cases plus9 support-moment-corrected offset cases,144 actual one-second integrations and4 expected-motion negative controls; every run ends by duration. Original source and retained-block hashes verified, independent original FBD residuals and centre geometry checked. Max holding-torque error5.684e-14Nm, spring error3.411e-13N, centre error1.137e-13mm; chassis drift7.958e-13mm analytical/0mm Pymunk, angle drift3.126e-13/2.842e-13deg and derived support error2.274e-13N. Baseline132.5deg requires -0.027168833380Nm,570.491044815N cable force and85.8375N support. Zero-torque baseline moves as expected because V4 assistance is approximate; uncorrected offset support also moves, while corrected holding runs pass. Initial harness import ordering and an incorrect no-event assumption for scheduled zero-height boundaries were fixed before the full clean run; no tolerance relaxed. Python compilation, Markdown links, diff whitespace and required repository entry/workspace checks precede publication. No server/browser/profile state touched; launcher lifecycle was not rerun because none changed. Hardware/contact/all-body linkage and canonical robot physics remain unvalidated.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member app validation.

## 4. Compute Saving Handoff State

Both floating engines match original V4 statics in63 directly equivalent cases and9 offset cases after the explicitly documented support-location moment correction.
Reproduce with app .venv Python validate_static.py and read static-validation.md; baseline zero hip torque is intentionally not exact equilibrium.
Preserve the distinction between actual held heave pose, derived ideal support/spring readouts and unverified belt/pin/contact forces when extending the experiment.

---

## Entry: 2026-10-22 — Andy Zhang — Complete native static analytical plots

## 1. Scope & Objective

- **Target Subsystem:** Kinefold experimental equilibrium presentation.
- **Associated Issue/Task:** User requested Conventions last and all Jon VSL v4 static analytical plots in the shared-design native Kinefold interface.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- `users/andy-zhang/experimental-apps/kinefold/equilibrium-data.js`
- `users/andy-zhang/experimental-apps/kinefold/equilibrium-diagrams.js`
- `users/andy-zhang/experimental-apps/kinefold/equilibrium-plots.md`
- `users/andy-zhang/experimental-apps/kinefold/equilibrium.css`
- `users/andy-zhang/experimental-apps/kinefold/equilibrium.js`
- `users/andy-zhang/experimental-apps/kinefold/index.html`
- `users/andy-zhang/experimental-apps/kinefold/preview.py`
- `users/andy-zhang/experimental-apps/kinefold/solvers.js`
- `users/andy-zhang/experimental-apps/kinefold/verify-equilibrium-diagrams.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify-equilibrium.cjs`
- **API/Interface Changes:** Stable tab IDs/query/help links and project-v3 profile schema remain unchanged. UI order is00 Designs,01 Builder,02 Equilibrium static,03 Analytical,04 Pymunk,05 Conventions. New native equilibrium data/plot/diagram modules replace the old static renderer; all17 source charts, four diagnostic axes, five FBDs and finite-idler detail use current builder parameters. Independent windows never mutate physical inputs. JSON/CSV exports include project/ranges/source context, null gaps and signed source quantities. New assets are added to the localhost allowlist. The retained V4 source, dynamics engines, source apps and canonical components are unchanged.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** node verify-equilibrium.cjs passes9404 assertions/266 independent hash-verified original-source cases, all17 manifest entries, zero-weight/gravity/Jacobian support gaps and8 multi-root travel queries. node verify-equilibrium-diagrams.cjs passes11757 assertions/45 cases: world force residual5.24e-13N, moment7.11e-14Nm, arc endpoint1.43e-14mm. Existing2000 model/1123 drawing assertions and18 project-state groups pass; JS parsing, Python compilation and diff whitespace pass. CUA verifies00..05 ordering/Home/End/help URLs, all4sweeps, expanded90–270° windows, linked angle visibility, readable5FBD/spring detail, selected-static high-ratio10kg145° import freshness, JSON17chart/all-axis coverage and contextual CSV. Exact pre-test140.8954° backup/profile restored and reloaded; console empty. Actual center-travel hover returns one pose; multi-root coverage is automated. SVG hover uses actual screen CTM after the review identified letterboxing. Launcher reuse/Stop/restart/reuse from unrelated cwd and all new assets/stable routes HTTP200 pass. Source reference hashes unchanged; no dynamics or hardware validation rerun/claimed. Parent architecture/coverage/browser review approved. Required repository workspace checks precede publication; unrelated ignored Laptop Access launchers preserved/excluded.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member app presentation.

## 4. Compute Saving Handoff State

Equilibrium now contains all17 original static charts in native expandable categories, with shared builder inputs, independent diagnostic windows and exact world-frame FBD/spring illustrations.
Use app-local Start Kinefold.cmd and4191; read equilibrium-plots.md for series/source anchors, scientific gap/sign conventions and contextual export format.
Preserve immutable reference equations, sampled-versus-bounded distinctions and shared-design invalidation when extending plots; floating dynamics and saved project profiles are unchanged.

---

## Entry: 2026-10-22 — Andy Zhang — Matched dynamic analysis, desktop playback and app-folder profiles

## 1. Scope & Objective

- **Target Subsystem:** Kinefold experimental dynamic presentation and local persistence.
- **Associated Issue/Task:** User requested matching categorized dynamic plots/comparison, a horizontally moving square floor, actual desktop Pymunk window, and all profiles/exports kept within Capstone instead of Downloads.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/.gitignore`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- `users/andy-zhang/experimental-apps/kinefold/designs.js`
- `users/andy-zhang/experimental-apps/kinefold/desktop_viewer.py`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-analysis.js`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-analysis.md`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-results.css`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-results.js`
- `users/andy-zhang/experimental-apps/kinefold/equilibrium-plots.md`
- `users/andy-zhang/experimental-apps/kinefold/equilibrium.js`
- `users/andy-zhang/experimental-apps/kinefold/exports/README.md`
- `users/andy-zhang/experimental-apps/kinefold/index.html`
- `users/andy-zhang/experimental-apps/kinefold/preview.py`
- `users/andy-zhang/experimental-apps/kinefold/profile_service.py`
- `users/andy-zhang/experimental-apps/kinefold/profiles/README.md`
- `users/andy-zhang/experimental-apps/kinefold/project-store.js`
- `users/andy-zhang/experimental-apps/kinefold/solvers.js`
- `users/andy-zhang/experimental-apps/kinefold/verify-dynamic-analysis.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify-projects.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify_profiles.py`
- `users/andy-zhang/experimental-apps/kinefold/verify_viewer.py`
- `users/andy-zhang/experimental-apps/kinefold/viewer_service.py`
- **API/Interface Changes:** New native dynamic analysis/results modules provide17 matching plots, exact-time/event-side same-snapshot comparison, contextual exports and shared playback. Same-origin bounded /api/viewer owns one fixed-script Pymunk/Tk results-playback process; /api/profiles provides atomic revision-checked app-folder designs/working copies and unique exports. Existing browser data remains backed up unchanged; project-v3 schema/stable tabs and dynamics equations are unchanged. All export callers now write exports/ through the service; new profiles/ and exports/ READMEs track purpose while generated JSON/CSV remains ignored. No source app/canonical changes; unrelated ignored Laptop Access launchers preserved.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** node verify-dynamic-analysis.cjs --real passes2788 assertions incl64 independent Python input-law probes, actual default6.5s runs/656 exact pairs and maxheaveerror0.00419668mm; wronghash/profile/params/eventside and partialcoverage checks pass. Existing3123 model/drawing assertions and27 project/disk-state groups pass;11 Python profile tests pass (atomicreplace failures/conflicts/corruption/immutablebackup/6MiBexports/pathsize/g0). Nativeisolated GUI tests pass7; mainnon-GUI run passes5/skips2, supplemented byactualparent desktopUI inspection of window/controls/floor. JSparse/Pythoncompile/whitespace pass. Actualsame-origin APIs rejectforeignOrigin403 andunsafepath400. CUA verifies17matchingplots/enginepair/shared2.48scursor/comparisonfieldcursor/floorplay/nativeopen/noerrors; current140.8954° posepair656rows each. Migration/saveas/reload/delete/import leavesexact2nameddesigns andworking/profile deeply equal originalbrowserbackup. All8 actualexports (5JSON/3CSV,3.027MBcomparison/3.283MBstatic) parse insideapp exports/, noneDownloads. Parent movedonly5knownolderKinefoldQA downloads intoapp.preview/recovered-downloads. AppStop/start/reuse from unrelatedcwd at4191 passes afterserviceintegration; server remainsrunning. Parentarchitecture/browser/native/disk QA approved. Requiredexact-snapshot repository gates/hooks precedepublication; no newengine/hardware/collision/fullvehicle validation claimed.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member app presentation/persistence.

## 4. Compute Saving Handoff State

Both native dynamic workspaces now compare one captured mechanism/profile with categorized plots, event-aware errors, synchronized movingfloor and a genuine closable Pymunk desktop results-playback window.
Use app-local Start Kinefold.cmd at4191; profiles/library.json stores exactnamed/workingdesigns, exports/ stores everyartifact, and originalbrowserkeys/backup remain preserved.
Retain exacteventside alignment, condensed-linkage scope, atomicrevision checks and fixed-root process/file APIs; read dynamic-analysis.md and appcontext for actualevidence and limitations.

---

## Entry: 2026-10-22 — Andy Zhang — Actual terrain contact and free-wheel motion

## 1. Scope & Objective

- **Target Subsystem:** Kinefold experimental terrain-contact dynamics and presentation.
- **Associated Issue/Task:** User requested actual wheel spin/terrain collision after referring to Motion Lab, then explicitly selected an editable1.5kg wheel, effective friction0.8, zero bounce and freely backdrivable drive.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/contact-render.js`
- `users/andy-zhang/experimental-apps/kinefold/contact-ui.js`
- `users/andy-zhang/experimental-apps/kinefold/contact_dynamics.py`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- `users/andy-zhang/experimental-apps/kinefold/conventions.js`
- `users/andy-zhang/experimental-apps/kinefold/designs.js`
- `users/andy-zhang/experimental-apps/kinefold/desktop_viewer.py`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-analysis.js`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-analysis.md`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-results.css`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-results.js`
- `users/andy-zhang/experimental-apps/kinefold/index.html`
- `users/andy-zhang/experimental-apps/kinefold/preview.py`
- `users/andy-zhang/experimental-apps/kinefold/profile_service.py`
- `users/andy-zhang/experimental-apps/kinefold/project-store.js`
- `users/andy-zhang/experimental-apps/kinefold/solvers.js`
- `users/andy-zhang/experimental-apps/kinefold/terrain-contact.md`
- `users/andy-zhang/experimental-apps/kinefold/verify-contact-drawing.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify-dynamic-analysis.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify-projects.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify_contact.py`
- `users/andy-zhang/experimental-apps/kinefold/verify_profiles.py`
- `users/andy-zhang/experimental-apps/kinefold/verify_viewer.py`
- `users/andy-zhang/experimental-apps/kinefold/viewer_service.py`
- **API/Interface Changes:** Optional project-v3 contactConfig selects prescribed-height or terrain-contact without changing legacy snapshots that omit it. Same-origin dynamics/viewer endpoints dispatch by mode to a fixed contact script, rejecting analytical contact. The contact model has actual chassis/wheel bodies, circular shape/friction, moving world terrain, exact massless straight-linkage constraint, free-drive indices, interval contact impulses and explicit unsupported-geometry/inertia guards. Native plots/browser/desktop share actual result transforms and mesh; unavailable benchmark acceleration/work diagnostics remain null. A deliberate demo action preserves working design as a named backup before creating the separate complete contact profile. Designs/conventions document scope and new variables. Original source apps, reference equations, canonical components, shared rules and dependencies are unchanged.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** App verify_contact.py passes8 groups: full6.5s R200 demo; flat normal100.552499227N vs10.25*9.81N; spin28.6478897565deg/s vs100/200rad/s and frictionless0; unchanged baseline spring570.491044815N/holding hip torque-0.027168833380Nm; maximum penetration0.004186895mm; dt convergence; R100/H150 jam stops at0.51275s rather than tunnelling; tilted/nonunit-drive initial indices and spring virtual-work mapping. verify-contact-drawing.cjs passes666 assertions including independent belt material velocities; verify-dynamic-analysis.cjs39 assertions; verify-projects.cjs29 groups; verify_profiles.py12 tests; existing verify.cjs2000 and verify-drawing.cjs1123 assertions pass. Viewer suite passes8/skips3 GUI cases, supplemented by actual Tk/Pymunk contact controls/auto-close test PASS1; null slip and explicit prescribed-mode dispatch regressions pass. Initial viewer validation failure for contactConfig=None was fixed and rerun clean. JS parsing/Python compilation/whitespace pass. Parent browser QA verifies651 actual-contact samples/6.5s, flat spin, moving world mesh, physical gap bridging, mode guards, blank friction rejection, correct Designs/conventions copy and no console warnings/errors. Original2 named designs remain deeply equal; separate exact-working backup and contact demo make4 named designs, current working equals demo after reload. Legacy baseline paired benchmark656 exact rows/max heave error0.00419668mm remains unchanged. Actual7.44MB JSON/396k CSV parse inside app exports/, none Downloads. Manual native visual inspection was occluded and is not claimed; actual automated Tk GUI test passed. Project-local Stop/start/restart/reuse from unrelated cwd passes4191; final server/result retained without restart. Parent architecture/browser review approved; ignored .preview/contact-gap-bridging-final.png records4.3s bridge. Required exact-snapshot repository checks/hooks precede publication; unrelated ignored Laptop Access launchers and all profile/export data are excluded.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated experimental member app; no hardware or full-vehicle validation is claimed.

## 4. Compute Saving Handoff State

Pymunk terrain-contact mode now physically spins the free wheel against translating square terrain, preserves massless straight-linkage geometry, permits gap bridging/separation and stops excessive penetration explicitly.
Use app-local Start Kinefold.cmd at4191 and read terrain-contact.md for supported geometry, force/index conventions, interval contact diagnostics and native playback limitations; original prescribed-height paired analysis remains separate and unchanged.
Preserve optional contactConfig compatibility, exact saved baseline/backup profiles and null unavailable diagnostics when extending this experimental two-body model; manual native visual QA was occluded while automated actual Tk GUI and browser QA passed.

---

## Entry: 2026-10-23 — Andy Zhang — Independent contact engines, jump and landing assessment

## 1. Scope & Objective

- **Target Subsystem:** Kinefold experimental single-leg actual-contact dynamics, case control and analysis.
- **Associated Issue/Task:** User requested the analytical engine solve the same actual terrain/free-wheel problem as Pymunk, shared Terrain stability/Jump/Landing cases, braking-torque and energy-method assessment. User supplied editable chassis underside offset50mm below hip A.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/analytical_contact.py`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/case-ui.js`
- `users/andy-zhang/experimental-apps/kinefold/contact-render.js`
- `users/andy-zhang/experimental-apps/kinefold/contact-scenarios.md`
- `users/andy-zhang/experimental-apps/kinefold/contact-ui.js`
- `users/andy-zhang/experimental-apps/kinefold/contact_cases.py`
- `users/andy-zhang/experimental-apps/kinefold/contact_dynamics.py`
- `users/andy-zhang/experimental-apps/kinefold/contact_study.py`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- `users/andy-zhang/experimental-apps/kinefold/conventions.js`
- `users/andy-zhang/experimental-apps/kinefold/designs.js`
- `users/andy-zhang/experimental-apps/kinefold/desktop_viewer.py`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-analysis.js`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-analysis.md`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-results.css`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-results.js`
- `users/andy-zhang/experimental-apps/kinefold/index.html`
- `users/andy-zhang/experimental-apps/kinefold/preview.py`
- `users/andy-zhang/experimental-apps/kinefold/profile_service.py`
- `users/andy-zhang/experimental-apps/kinefold/project-store.js`
- `users/andy-zhang/experimental-apps/kinefold/solvers.js`
- `users/andy-zhang/experimental-apps/kinefold/terrain-contact.md`
- `users/andy-zhang/experimental-apps/kinefold/verify-dynamic-analysis.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify-projects.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify_analytical_contact.py`
- `users/andy-zhang/experimental-apps/kinefold/verify_contact.py`
- `users/andy-zhang/experimental-apps/kinefold/verify_contact_cases.py`
- `users/andy-zhang/experimental-apps/kinefold/verify_contact_comparison.py`
- `users/andy-zhang/experimental-apps/kinefold/verify_profiles.py`
- `users/andy-zhang/experimental-apps/kinefold/verify_viewer.py`
- `users/andy-zhang/experimental-apps/kinefold/viewer_service.py`
- **API/Interface Changes:** Optional strict project-v3 caseConfig preserves old snapshots when omitted and is saved/captured/hashed with geometry, material and run settings. Independent analytical_contact.py uses reduced SPD mass/contact impulses without importing Pymunk; Pymunk separately integrates actual bodies/contacts. Shared contact_cases.py holds geometry/controller/energy/assessment laws. Both modes use physical unilateral inelastic travel stops, explicit case initial conditions/hold/braking/cutoff, real spin/contact, phase/events and separate motor/chassis/wheel/spring/gravity/stop energy fields. /api/dynamics dispatches both actual-contact engines; bounded same-origin /api/contact-study invokes only the fixed landing-assessment script. Assessment trials stop at first arrest/failure, not later settled safety. Both native dynamic tabs share categorized case controls, outcome mismatch warnings, matching captured comparisons and app-folder exports. Native playback receives the complete saved case and actual mesh. New assets join the fixed allowlist; no dependencies, canonical/shared components, source apps or immutable V4 reference are changed.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** Main verify_contact.py8 groups, verify_contact_cases.py9 groups and verify_analytical_contact.py11 groups PASS. Independent checks match flat normal100.5525N, free spin28.6478898deg/s and zero friction spin0; held ballistic landing and compensation; spring-off100Nm extension work113.44640138J; zero-torque jump negative control; zero-brake bottom-out failure/100Nm arrest; exact chassis half-mv-squared; initial intersection, reversed-endpoint and tilted-energy guards; underside-truncated usable stroke; sustained bottom-out support and tilted-stop momentum/refinement. R100/H150 jam controls stop at1mm in both engines. Independent analytical import contains no Pymunk. verify_contact_comparison.py actual2s cases match201 timestamps/hash/profile and refine maximum heave difference Jump2.24675/1.38403/1.09242mm and Landing4.85817/1.69714/0.910564mm atdt.0005/.00025/.000125. Energy residuals remain explicit numerical diagnostics; no tight-conservation or continuous peak-torque claim.46 comparison assertions,31 project groups,13 profile tests,666 contact drawing,2000 model and1123 drawing assertions PASS. Native suite9PASS/4GUI skips, supplemented by actual Tk/Pymunk jump pause/scrub/replay/auto-close PASS1 and browser native open/status/close. Parse/compile and whitespace PASS. Parent browser QA verifies Jump20Nm,100mm Landing20Nm, shared saved cases/energy toggle/staleness, readable plots/underside point/stationary floor,10-trial Pymunk bracket10.9375failing/12.5passingNm, and honest200mm energy-sized22.6905Nm disagreement (analytical arrest/Pymunk bottom-out). Final6.5s terrain pair651 exact common rows/max heave error0.00416921764mm, spin RMS0.232471deg/s,17,768,364byte comparison export parses inside app exports/, console empty. All4 named designs and working snapshot deeply equal the captured pre-QA backup after UI restore; exact restoration of a later unsaved baseline observed only by name is not claimed. Assessment-only early stopping tested against full first-arrest criterion in both engines;10-trial searches8.63s analytical/1.29s Pymunk return identical tested brackets. Ordinary full runs unchanged; later rebound/settling safety explicitly outside search criterion. Initial clearance test expectation was updated to the new initial-intersection rejection and rerun clean. Start/Stop/restart/reuse via actual app-local launchers from unrelated cwd passes4191; no server/profile mutation after final QA. Parent architecture/browser approval received. Required exact-snapshot workspace gates/hooks precede publication; generated profiles/exports/screenshots and unrelated ignored Laptop Access launchers remain excluded.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated member experiment; no hardware, tire-compliance, whole-vehicle or peak motor-rating certification is claimed.

## 4. Compute Saving Handoff State

Both native dynamic tabs now solve one captured actual-contact mechanism with independent engines and shared Terrain/Jump/Landing controls, physical stops, explicit hold/braking, energy accounting and tested first-arrest torque brackets.
Use app-local Start Kinefold.cmd at4191 and contact-scenarios.md for exact controller/search scope, numerical refinement and outcome disagreement; profiles and all exports remain app-local, with original named designs unchanged.
Preserve optional-case compatibility, independent integration, real spin/contact and explicit ledger residuals; energy-average sizing and first-arrest search do not certify peak torque, settled safety or near-boundary engine agreement.

---

## Entry: 2026-10-23 — Andy Zhang — Unified mechanism studio and offline Plotly charts

## 1. Scope & Objective

- **Target Subsystem:** Kinefold experimental member-app presentation and navigation.
- **Associated Issue/Task:** Merge saved designs, mechanism builder and equilibrium into one workspace, with static plots below the RHS mechanism preview; use Plotly for all data charts while preserving numerical engines and saved profiles.

## 2. Structural Modifications

- **Files Modified/Added:**
- `ENTRY_TEMPLATE.md`
- `users/andy-zhang/experimental-apps/kinefold/README.md`
- `users/andy-zhang/experimental-apps/kinefold/app.js`
- `users/andy-zhang/experimental-apps/kinefold/context/README.md`
- `users/andy-zhang/experimental-apps/kinefold/conventions.js`
- `users/andy-zhang/experimental-apps/kinefold/designs.js`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-results.css`
- `users/andy-zhang/experimental-apps/kinefold/dynamic-results.js`
- `users/andy-zhang/experimental-apps/kinefold/equilibrium.css`
- `users/andy-zhang/experimental-apps/kinefold/equilibrium.js`
- `users/andy-zhang/experimental-apps/kinefold/equilibrium-plots.md`
- `users/andy-zhang/experimental-apps/kinefold/index.html`
- `users/andy-zhang/experimental-apps/kinefold/plotly-runtime.js`
- `users/andy-zhang/experimental-apps/kinefold/plotly.css`
- `users/andy-zhang/experimental-apps/kinefold/preview.py`
- `users/andy-zhang/experimental-apps/kinefold/solvers.js`
- `users/andy-zhang/experimental-apps/kinefold/studio.css`
- `users/andy-zhang/experimental-apps/kinefold/terrain-contact.md`
- `users/andy-zhang/experimental-apps/kinefold/vendor/PLOTLY-LICENSE.txt`
- `users/andy-zhang/experimental-apps/kinefold/vendor/README.md`
- `users/andy-zhang/experimental-apps/kinefold/vendor/plotly-basic-4.1.2.min.js.gz`
- `users/andy-zhang/experimental-apps/kinefold/vendor/plotly-manifest.json`
- `users/andy-zhang/experimental-apps/kinefold/verify-dynamic-plotly.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify-equilibrium-plotly.cjs`
- `users/andy-zhang/experimental-apps/kinefold/verify-plotly-runtime.cjs`

- **API/Interface Changes:** Four top tabs (studio, analytical, Pymunk, conventions); legacy designs/static URL aliases select studio inner sections. Shared KinefoldPlotly lifecycle renders all data charts, resolves theme colors, preserves zoom/cursors and purges removed hosts. Fixed read-only vendor route verifies/decompresses pinned official Plotly basic4.1.2 from a398299byte gzip asset; no CDN, package install, gate changes or oversized raw blob. Existing contextual JSON/CSV exports remain app-local; default camera downloads removed. Geometry/FBD/convention illustrations stay SVG. No engine, reference equation, project schema, profile contents or source-app changes.

## 3. Local Validation Checklist

- **Validation Scope:** workspace
- **Research/Policy Validation:** New static trace14, dynamic Plotly2535 and shared Plotly lifecycle11 assertions PASS, including sign/strand dash semantics, null/wrap/event-side gaps, zero-mass display ranges, theme cursor retention, hidden-chart cursor caching and reinserted-host lifecycle. Existing static/source9404 assertions/266 cases/17 charts/8 multibranch queries, dynamic comparison46, project-state31 groups, model2000 and drawing1123 assertions PASS. JS parsing, Python compilation, HTML four-tab/nested-library/static structure and whitespace PASS. Actual project-local Stop/Start/reuse from unrelated C:/Users/zhang passes4191. All new assets HTTP200; vendor GET and HEAD match exact raw length1198523 and SHA256; gzip/source/license provenance tracked. Parent initial browser review passes merged layout, readable single-column plots, point-click pose changes, zoom and Play/pause with deferred static refresh. Parent final browser/architecture approval: merged four-tab layout and readable RHS single-column plots; static point-click, drag zoom and series toggles; legacy static/designs aliases; builder Play/pause with settled refresh; dynamic comparison selectors and0.37s cursor retained through light/dark/light theme, engine switch and collapsed comparison reopening. Actual6.5s100mm/20Nm Landing pair651 exact common rows, both arrested, sampled maximum heave difference1.84191mm;13,148,659byte comparison JSON parses in app exports/. No console warnings/errors. Current working and all4 named designs deeply equal .preview/pre-plotly-studio-library.json revision57 after temporary pose changes were restored, without import. Final screenshots .preview/merged-studio-final.png and .preview/merged-static-plotly-final.png remain ignored. No numerical engine changes or broad physics reruns are needed for this presentation-only workspace contribution. Generated profile/export/screenshot data and unrelated ignored launchers remain excluded.
- [ ] Executed `python simulation/run.py --headless-check` cleanly.
- [ ] Executed `python simulation/experiments/verify_backend.py` with zero drift.
- [ ] Physics limits (mass, joint constraints) verified against canonical `/assets/`.

Canonical robot physics is NOT APPLICABLE to this isolated presentation-only member workspace; no new physical validation is claimed.

## 4. Compute Saving Handoff State

Kinefold now has one Mechanism studio with a compact expandable saved-profile library, builder controls, mechanism preview and categorized equilibrium directly beneath that preview.
All data plots use locally pinned Plotly with offline loading, linked pose/time interactions and existing app-folder data exports, while numerical engines and SVG engineering illustrations are retained.
Use project-local Start Kinefold.cmd at4191; preserve four-tab URL aliases, exact saved profiles, event/null gaps and current-pose labeling when extending the presentation.

---
