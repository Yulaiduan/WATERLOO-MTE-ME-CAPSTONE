# Research prototypes

Keep small research snippets here, labelled experimental. Each script needs a
module docstring with its purpose, invocation, inputs/units, outputs, dependencies
and limitations. It must write generated files to ignored `results/`. Never
import this folder into production components. Promote useful work into its
owning component with tests and remove redundant copies.

- [Requirement parameter screen](requirement_parameter_screen.py): standalone
  NumPy calculations for geometry, spring assistance, slope and range, with
  [assumptions and selected evidence](../../docs/benchmarks/2026-10-02-requirement-parameter-screen/README.md).
  Use `--output simulation/results/requirement-parameter-screen` from the root;
  explicitly promote reviewed compact evidence into the dated record.

These prototypes use the [preliminary research workflow](../../agent_skills/preliminary_research.md)
until promoted into executable robot components.
