# Andy Zhang — experimental apps and toolkits

Updated: 2026-10-10. Status: member experimental tools; no canonical robot validation implied.

Create one folder per tool using the [app template](../../_template/experimental-app/README.md).
Keep app-specific context with that app and link it from this index.
Follow the [experimental app workflow](../../README.md), including applicable
engineering gates and a project-local restart launcher for any localhost server.

| App | Purpose | Status | Verified startup |
| --- | --- | --- | --- |
| [Motion Lab](wheel-leg-lab/README.md) | Unified mathematical/Pymunk/study/data browser, with Plotly and dark mode | Experimental; 32 JS + 37 Python tests, MATLAB agreement and browser checks | Start Motion Lab.cmd at 4186; familiar launch names are aliases |
| [Terrain Mobility Atlas](terrain-mobility-atlas/README.md) | Former loose atlas, numerical terrain workbench, historical linkage and force calculator | Experimental; 49 model tests, build and browser checks pass | App-local port-4175 launcher passes lifecycle checks |
| [Legacy Capstone archive](capstone-archive/README.md) | Complete source/docs/data/historical-output backup from the nondeleting reorganization | 668 files restored with exact hashes; dependencies/caches stay local | Python standard-library restoration to a new directory; no server |
