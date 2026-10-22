# VSL Solver v4

Use [Open VSL Solver v4.cmd](Open%20VSL%20Solver%20v4.cmd) for the calculator
and automatic default Excel-library loading. Python3.10+ standard library only.
See [setup and library instructions](../README.md), [equations](v4-model.md),
[current baseline workbook](v4-configs.xlsx), and [app context](../context/README.md).

Checks: `node verify-pulley.cjs --output`, `node verify-library.cjs`,
`node verify-fit.cjs --output`, `python verify_excel.py`. Each uses local assets and writes no user workbook;
only the first optionally updates its compact verification JSON.
Earlier13kg fitting scripts, JSON and plots are historical research fixtures.
No hardware or canonical-robot validation is implied.

Current fitting and torque conventions are described in the [model](v4-model.md).
