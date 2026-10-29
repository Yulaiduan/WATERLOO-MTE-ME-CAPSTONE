# VSL Solver V5 — fall recovery

Jonathan Xie's experimental calculator, 2026-10-24. V4 is preserved separately.

Double-click **[Open VSL Solver v5.cmd](Open%20VSL%20Solver%20v5.cmd)**.
It uses installed Python 3.10+ and opens
[V5](http://127.0.0.1:8768/v5/v5-fall.html). Keep its server window open.
The separate port permits V4 and V5 to run together. Repeated launches reuse V5.
No login/boot startup is installed. Direct [HTML](v5-fall.html) calculates offline;
the launcher is needed for automatic local Excel access.

The **mT (kg)** and **h (m)** masters sit below θ₂. Each supports dragging,
playback, bounds and direct entry. Editing mT changes chassis mass while retaining
moving-mass entries; prescribed force ×g values follow mass changes as in V4.
The controls from θ₂ through Analysis Mode remain pinned as a compact ribbon
while scrolling. Cycle time is in the θ₂ row; model and headlines scroll normally.

**Analysis Mode** has three always-visible choices: Global y/z, Wheel n/t, and
Fall height. The selected manual mode gets a full-width force-input panel; Fall
height uses the shared h input and displays the current trajectory load. In fall
mode the original force/torque diagrams, plots and headlines use instantaneous
Fz, Fy=0 and beta=0. Switching back restores manual loads/beta. The spring optimizer
retains its static prescribed-load objective. With a manual mode selected, changing
h leaves the original static graphs unchanged.

The collapsible Fall recovery section is always a **5×4 grid**, regardless of
Analysis Mode. Rows are τ₂, net a_z/g (with Fz in N), v_z, d_z, and elapsed time. Columns are
θ₂, time, peak magnitude versus alpha, and peak magnitude versus h. Both sweep
columns use master bounds and braking-stroke peaks. Displacement versus h is
constant; velocity versus alpha is constant when the catch decelerates monotonically.
There are no elapsed-time substitutions. Narrow windows can pan the four columns
horizontally instead of compressing or reordering the grid.

Finite values autoscale by default. **Scale to include zero** makes zero the
boundary for one-sided curves; mixed-sign curves retain both sides. Exact zero
ticks/guide lines are labelled, and acceleration adds a 1g guide when in view.
The visible **Plot absolute magnitudes** toggle changes the fall pointwise/time
plots; sweep peaks already use magnitudes. Both settings persist in configurations.

Velocity terminates at zero. The dashed endpoint step and hollow marker show the
instantaneous switch from braking to holding, ending net a_z/g at zero and Fz at
1mg. Read [why hip braking works even with beta=0](v5-braking-note.md), including
the distinction from wheel braking and the zero-alpha example. The equations
describe an ideal instantaneous switch, not a smooth post-stop response.

Master controls from θ₂ through the selected force panel pin to the viewport
when scrolled past, with a visible pinned indicator and their original page
space retained. Cycle time is at the end of the θ₂ row; headlines/model are excluded.
ζ displays one decimal, with positive values highlighted and negative values subdued.

## Model and signs

Read [the equations and limits](v5-model.md). The full entered total mass is
assigned to this modeled leg; the second leg balances pitch/horizontal reactions.
The study uses vertical translation of a point mass, massless links, fixed pitch,
β=0, an ideal tension spring/cable and an instantaneous constant motor torque.
Positive motor torque is CCW on Link2; braking during increasing θ₂ is negative.
Velocity is negative downward; net acceleration is positive upward. d_z remains
the V4 upward wheel-relative travel, which means chassis height changes by −d_z.

The constant-torque energy result attains the minimum possible peak torque only
when the full catch is feasible. The app rejects dead centres/reversal, early
stops, negative contact force and infinite-time endpoints. Other torque schedules
are not optimized. Peaks and feasibility are sampled; no physical safety rating,
strength, finite controller response, power/thermal or impact validation is implied.

## Configuration library

[v5-configs.xlsx](v5-configs.xlsx) starts as an exact copy of the user's current
V4 workbook. V5 loads this copy automatically; it does not overwrite V4.
Loading a copied V4 row uses the V5 default h=0.25m and master bounds until that
row is explicitly saved with V5 settings. Row Save captures live inputs and
fall settings; Save Excel persists the library. Fall outputs are included only
when the current study has finished and is feasible. Existing rows are retained.

V5 uses separate browser preferences/drafts. A restored draft keeps its original
revision; conflicting workbook edits require a deliberate reload. Excel saves
show progress and time out visibly rather than leaving the UI silently busy.
The V5 workbook gains the new fall columns on its first explicit V5 Excel save.
The Designs and VSL state sheets retain the established library format.

## Checks

Run `node verify-fall.cjs`, `node verify-analysis.cjs`, `node verify-ui.cjs` and
`python verify_excel.py` in this folder.
The fall checks use independent constant-acceleration and time-domain integration
references, conservation of energy, signs, geometry, alpha/height/mass sweeps,
invalid regimes, nonmutation and exact V4 static-model preservation.
Excel checks mutate temporary workbooks only. The current grid checks render all
twenty SVG charts in both analysis modes and all four scale/magnitude combinations,
verify the holding switch against independent static equilibrium, and check the
restored displacement/velocity sweeps. See [fall checks](v5-verification.json),
[analysis checks](v5-analysis-verification.json) and [grid checks](v5-ui-verification.json).
The cleanup's actual Opera layout could not be inspected because computer use
stopped when the browser URL could not be verified; SVG/data checks do not replace
that browser visual check. Versioned script/style URLs ensure a refresh requests
the updated controls rather than reusing older assets.

The [local server](vsl_server.py) uses only Python's standard library. The
[fall model](fall-model.js), [fall-load adapter](fall-analysis.js) and [fall UI](fall-ui.js) use browser/Node built-ins.
No dependency installation is required.

The fifth fall row plots elapsed contact time versus theta2 and time (y=x),
and total catch time versus alpha and fall height using their master bounds.
Time uses seconds and remains available in every Analysis Mode.
