# Jonathan Xie — experimental apps and toolkits

Status: Leg Solver v1 kinematics and v2 quasi-static forces are implemented and locally checked; no canonical robot validation claimed.

Create one folder per tool using the [app template](../../_template/experimental-app/README.md).
Keep app-specific context with that app and link it from this index.
Follow the [experimental app workflow](../../README.md), including applicable
engineering gates and a project-local restart launcher for any localhost server.

| App | Purpose | Status | Verified startup |
| --- | --- | --- | --- |
| [Leg Solver](leg-solver/README.md) | General VSL geometry, wheel coupling and prescribed-load quasi-static forces | Separate v1/v2 HTML; numerical and static-HTTP browser checks pass | Self-contained HTML; direct offline launch not tested by browser tool |
