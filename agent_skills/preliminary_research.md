# Preliminary research contributions

The owner authorized this policy on 2026-10-03 so research can be shared before
the team has an approved robot model. Research publication does not certify a
robot design, physical baseline or hardware performance.

## Scope

`tools/check_entry.py` classifies the complete diff from the fetched base,
including deleted paths. The preliminary category permits documentation and
compact evidence under `docs/`, research notes and equations under `database/`,
standalone calculations under `database/code_prototypes/`, and an explicit set
of contribution-policy, gate and regression-test files. Gate/policy changes keep
their owner human-review requirement. Routine research needs no teammate approval
after checks pass; see CONTRIBUTING.md. The path allowlist is in `preliminary_path`.

Changes to canonical assets, executable robot code, controllers, terrain/config,
dependencies, firmware, training, shared interfaces, deployment or unknown paths
require the normal physics checks. A mixed contribution also requires physics.
Production components must never import `database/code_prototypes/`; promote a
prototype into the owning component through a physics-validated contribution.

## Required evidence

1. Keep sources, units, assumptions, proposed status and limitations explicit.
   Do not call analytical agreement a hardware or canonical physics validation.
2. Run relevant calculations and verify retained results, script hashes and
   documentation links. Retain small reproducible evidence rather than raw runs.
3. Append the standard four-section contribution entry. Add these fields in the
   validation section, replacing the evidence text with actual results:

   ```markdown
   - **Validation Scope:** preliminary
   - **Research/Policy Validation:** Describe the actual commands and results.
   ```

   Leave the three canonical physics boxes unchecked and explicitly explain
   that they are not applicable to this contribution. Preserve earlier failures
   in the append-only log. The new declaration does not change an earlier result.
4. Run `python tools/check_entry.py --base origin/main --require-passed` and
   `python tools/physics_gate.py --base origin/main`. The latter runs gate
   regressions for preliminary work and reports canonical physics as
   **NOT APPLICABLE**. The direct robot commands still fail when no model exists.
5. Commit exact paths and push a personal branch using the normal hooks; open a
   PR and follow required CI and applicable critical-path human review. No hook bypass or fabricated check pass
   is part of this workflow.

The existing GitHub job names remain `Entry architecture` and `Headless physics`.
For preliminary changes the second name represents the scoped validation gate;
its diagnostics identify the exemption and do not claim a robot physics pass.
