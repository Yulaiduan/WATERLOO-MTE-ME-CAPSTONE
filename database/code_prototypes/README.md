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

- [Link-travel plot](plot_link_travel.py): renders the retained calculated geometry
  points, step/reserve thresholds and ride-angle sensitivity. Requires NumPy 2.4.6
  and Matplotlib 3.10.7 in a plotting environment; use
  `--output simulation/results/link-travel-chart`. The figure is retained with the
  requirement parameter record above after numerical and visual checks.

- [Parameter relationship charts](plot_parameter_relationships.py): mass/COM,
  spring force/preload/drum and range/drive sensitivities with retained CSV
  checks and numerical provenance. Requires the same plotting environment; use
  `--output simulation/results/parameter-relationships`. Read the
  [assumptions and chart explanations](../../docs/benchmarks/2026-10-02-requirement-parameter-screen/parameter-relationships.md).
