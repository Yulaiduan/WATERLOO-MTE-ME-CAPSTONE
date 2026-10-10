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
