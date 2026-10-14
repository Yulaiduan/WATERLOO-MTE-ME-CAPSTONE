# Motion Lab — portable development context

Owner: Andy Zhang. Updated: 2026-10-14. Status: experimental, not canonical physics.
Latest feature base: `2353a6f` — wheel/link sizing and torque sweep.

Latest correction (2026-10-14): [general linkage tooling](docs/merged-linkage.md)
is merged into the original Math/Physics suspension bench and numerical backends.
The separate editor at c8b3c8b is superseded. Select editable geometry within the
existing form; source statics remain a labelled fixed-A audit alongside dynamic
spring/position response. See validation and the contribution log for release evidence.

Read [README.md](README.md), [AGENTS.md](AGENTS.md) and the detailed dated
[context/README.md](context/README.md). This file is an entry point to existing
records, not a competing model specification. Laptop setup and transfer are in
[the member handoff](../laptop-handoff.md).

## Current state to preserve

- Wheel/link sizing starts at **200 mm radius, 400 mm diameter, 200 mm usable
  lift**, confirmed by the user. It sweeps equal-link length/start-angle windows
  and compares peak, mean, RMS and CV under an explicit constant net load.
  Degree/mm buffers/custom ROM convert at a reference link; actual flat-ground
  chassis clearance is independent of the end reserve. Read [link-sizing](docs/link-sizing.md).
- Motion Lab is the main menu at port 4186. Math/Physical, Misc studies,
  Comparison and Profiles & data share its local workspace. Source includes all
  seven retained motion studies and the original force calculator.
- Wheel excitation is prescribed **position**, not force: floating chassis heave
  is an output. The current replacement suspension is one undamped upper-link/
  chassis unit with auxiliary strut and knee controller disabled by default.
- Dual-rope invertible knee-pulley design is **IMPOSSIBLE / rejected**, by the
  user's 2026-10-12 disposition. Preserve its historical model/source and data.
  The symmetric knee bellcrank is separate. The user withdrew the unloaded-full-
  contraction correction; do not silently reinstate the reverted variant.
- Fold q from downward vertical and theta from horizontal are complementary in
  the sizing study. Other model/viewer conventions differ; consult the exact
  [model](docs/model.md) and [glossary](GLOSSARY.md) before changing equations.

## Source and history map

| Work | Owning files/records |
| --- | --- |
| Sizing calculator | `web/force-plots/`, [model and verification](docs/link-sizing.md), `tests/link-sweep.test.js` |
| Main menu/library/comparison | `web/motion.js`, `web/library.js`, `web/comparison.js`; [workflow](docs/unified-motion-lab.md) |
| Wheel numerical models | `physics.py`, `math_model.py`, spring/runtime modules; [model](docs/model.md) |
| Invertible models | `inversion.py`, `invertible_spring.py`, `web/inversion/`; [model/status](docs/invertible-suspension.md) |
| Original chat/design decisions | [handoff](docs/handoff.md), [decisions](docs/decisions.md), [dated context](context/README.md) |
| Actual current/historical checks | [validation](docs/validation.md), [mechanism audit](docs/mechanism-audit.md), repository contribution log |

Use installed Python 3.13 and Node.js 22 with npm. On Windows, run **Setup Motion
Lab.cmd** once per new clone, then **Start Motion Lab.cmd** / **Stop Motion
Lab.cmd**. The app's `.venv`, node_modules, builds and process records are local
and recreated; copying the PC environment is unnecessary. MATLAB is optional
for legacy comparisons and is not required for normal startup/development.

Download selected profiles/runs with **Download JSON** in Profiles & data before
transferring custom browser data. Sizing uses its own **Save configuration JSON**
and **Load configuration** controls. Defaults/source work on the laptop without
those exports. Private chat transcripts are not part of this public workspace.

## Labelled alpha-zero examples, 2026-10-14

Source report `12e227c`. The owner explicitly requested Motion Lab visualizations
and GIFs after the offline report. Open study=design-examples or /design-examples/
for five labelled cases and ten working/full-inversion clips. Read
[the record](docs/design-examples.md) and [GIF index](web/design-examples/gifs/README.md).
The report remains offline, and backend/sizing models and saved profiles remain
unchanged. Fixed assembly indexing is labelled as a relaxed constraint; red
wheel/hip overlap is projected clearance, not solved contact. Preserve the
historical dual-rope IMPOSSIBLE status.
