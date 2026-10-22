# Andy Zhang — experimental apps and toolkits

Updated: 2026-10-22. Status: member experimental tools; no canonical robot validation implied.

For continuation on the PC, read [the current PC handoff](pc-handoff.md) and
[context.md](context.md). The [laptop handoff](laptop-handoff.md) retains earlier
setup evidence. Every app below has a
root `context.md` linking its preserved model/design/validation/development
records. Source, full Git history and archives travel with a normal clone;
dependencies are recreated locally and browser data transfers by JSON.

Create one folder per tool using the [app template](../../_template/experimental-app/README.md).
Keep app-specific context with that app and link it from this index.
Follow the [experimental app workflow](../../README.md), including applicable
engineering gates and a project-local restart launcher for any localhost server.

| App | Purpose | Status | Verified startup |
| --- | --- | --- | --- |
| [Kinefold](kinefold/README.md) | New mechanism builder with V4 cable suspension, front-left coordinates and illustrated conventions | Experimental geometry; 3,123 numerical checks plus browser/start-restart validation | Start Kinefold.cmd at 4191; installed Python only |
| [Offline leg design report](leg-design-study/README.md) | Jonathan/Andy equations, bounded link/window optimization, spring/motor example, plots and PDF | Experimental numerical study; separate from Motion Lab tooling | Open Design Report.cmd or index.html directly; no server |
| [Motion Lab](wheel-leg-lab/README.md) | Unified simulation/studies/library plus wheel/link sizing and torque sweep | Experimental; latest fresh-clone 70 JS tests and build pass; dated physics/native records remain in app docs | Start Motion Lab.cmd at 4186; familiar launch names are aliases |
| [Terrain Mobility Atlas](terrain-mobility-atlas/README.md) | Former loose atlas, numerical terrain workbench, historical linkage and force calculator | Experimental; fresh-clone 49 model tests and build pass | Start Terrain Atlas.cmd at 4175; Start Capstone.cmd is a Motion Lab alias |
| [Legacy Capstone archive](capstone-archive/README.md) | Original source/docs/data/output backup plus later local development source history | 668 original files, 21 October 12 source files and 14 October 19 historical source/report files | Python standard-library restoration to new directories; no server |
