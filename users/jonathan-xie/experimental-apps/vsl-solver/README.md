# VSL Solver

Jonathan Xie's experimental virtual scissor lift calculator. Lengths mm, angles
degrees, mass kg, force N, torque Nm. Analytical consistency is not hardware validation.

## Open V4

Double-click [Open VSL Solver v4.cmd](Open%20VSL%20Solver%20v4.cmd).
It starts a local Python 3.10+ helper and opens
[the calculator](http://127.0.0.1:8767/v4/v4-pulley.html).
The helper binds only to 127.0.0.1. Close its window to stop it; repeated launches
reuse the same server. Nothing is installed at login or boot.

The [HTML](v4/v4-pulley.html) can also run directly. Use the launcher for local
Excel save/load; a plain file tab cannot automatically read or overwrite a workbook.

## Versions

| Folder | Calculator | Model | Manual launcher |
| --- | --- | --- | --- |
| [v1](v1/README.md) | [Kinematics and equations](v1/v1-kinematics.html) | Equations in app | [Open](v1/Open%20Leg%20Solver.cmd) |
| [v2](v2/README.md) | [Quasi-static loads](v2/v2-quasi-static.html) | [Notes](v2/v2-model.md) | [Open](v2/Open%20Leg%20Solver%20v2.cmd) |
| [v3](v3/README.md) | [Direct horn spring](v3/v3-spring.html) | [Notes](v3/v3-model.md) | [Open](v3/Open%20Leg%20Solver%20v3.cmd) |
| [v4](v4/README.md) | [Remote spring / hip pulley](v4/v4-pulley.html) | [Notes](v4/v4-model.md) | [Open](v4/Open%20VSL%20Solver%20v4.cmd) |


## Flexible spring fit and physical hip torque signs — 2026-10-21

All seven spring inputs now have **Driving** checkboxes: checked values are
held; unchecked values are fitted. Defaults hold k,S_v,r_s,ν and fit r_h,p₀,S_u.
The single Fit button minimizes peak |τ₂| over working θ₂ at current α/β/loads,
with a result/warning box. Zero through seven fitted variables are supported;
old point-preload and textbook buttons are removed. Spring/mass descriptions
are compact; only φ₀ remains in the sidebar angle controls. θ₂ master bounds
are labeled θ₂ᵉ and θ₂ᶜ.

Hip signs are now **τ₂=−τG−τS**, all positive CCW on Link2. Only τG's definition
changes; actual motor torque is unchanged. τ₄ stays CCW on its own drive shaft.
Saved configurations migrate the gravity sign and preserve all physical values;
new checkbox selections persist through JSON, row Save/Load and Excel.
The usual8.75kg/10mm-idler fit now gives max|τ₂|≈0.023771Nm over100–165°.
This is a bounded sampled numerical minimum, not a proof of global optimality.
See [fit details](v4/v4-model.md) and [verification](v4/v4-flex-fit-verification.json).

## V4 current behavior — 2026-10-21

- Drive reductions are **q_dc = r_d/r_c** and **q_fe = r_f/r_e**. A value of 2
  means the downstream pulley radius is twice its input radius. Physical belt
  equations are unchanged; V1–V3 retain their original ratio conventions.
- Default wheel radius is **200 mm**, total mass **8.75 kg**. Changing total mass
  or gravity preserves the active load components' ×g values, including a
  zero-mass round trip. Forces are prescribed loads, not a ground-contact model.
- One automatically calculated **ζ** retains clockwise cable wrap over the
  working θ₂ range. Positive ζ rotates the spring exit CW; negative ζ is reported
  but drawn horizontally. The hypothetical 90° preload is extrapolated if its
  wrap is outside the selected route. A pin inside/on S at 90° is still invalid.
- Default k=8 N/mm, S_v=100 mm, r_s=10 mm, r_h=62.2269495 mm,
  S_u=9.38777673 mm, p₀=330.869283 N, 100–165°. The current input values are retained; the new Driving checkboxes
  govern only the explicit fit. The numerical fit has about ±0.1262% support error; it is
  approximate. The [earlier 13 kg textbook report](v4/v4-textbook.md) remains a
  separate historical study, not the current default.

## Configuration library and Excel

The left library opens/closes and can be pinned. **New DP** creates the next
unique number. **Row Save** captures all live inputs, bounds, driver/view choices
and key outputs. **Row Load** restores that snapshot and stars it. Editing the
live solver does not overwrite rows. Names, row order, multi-selection and eight
light shading options are supported; scroll horizontally for all 75 columns.
The first five columns stay visible. Library timestamps display Toronto time;
Excel timestamps are UTC.

**Save Excel** writes the entire library; **Load Excel** replaces it from disk.
[v4-configs.xlsx](v4/v4-configs.xlsx) loads automatically on normal launches and
starts with DP1, the 8.75 kg baseline. Paste an absolute local .xlsx path or use
Browse. Saving to a new filename creates a library. This is explicit sync, not
continuous autosave or SharePoint synchronization. Close Excel before overwriting
an open workbook. Concurrent external edits are rejected; reload first. One
`.vsl-backup.xlsx` file holds the previous successful version.

The Designs sheet exposes inputs and saved outputs. The VSL state sheet stores
complete snapshots; retain that sheet and the column headers. Editing an input
in Excel marks outputs stale: load its row into VSL, then Row Save to recompute.
The visible Save/Load cells in Excel are labels; use the actual buttons in VSL.
Unrelated existing workbooks are not overwritten. Unsaved browser-library edits
are recoverable using **Restore unsaved draft**, including a different workbook.
Each normal launch still reads the default workbook first. Row Load is explicit.

## Verification

From each version folder, its `verify-*.cjs` scripts run with Node.js without
packages. V4 adds `node verify-library.cjs` and `python verify_excel.py` (stdlib).
See [V4 checks](v4/v4-verification.json), [model notes](v4/v4-model.md) and
[app context](context/README.md). Numerical tests verify tangency, spring energy,
static balance, wrap extrema, inverse ratios, mass scaling and workbook state.
Native Browse uses Python's optional Tk dialog; paste a path if unavailable.
No spring friction, cable slack dynamics, strength, fatigue, 3D packaging or
canonical robot physics has been validated.
