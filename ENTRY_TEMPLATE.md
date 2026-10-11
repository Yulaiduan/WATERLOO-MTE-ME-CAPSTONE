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
