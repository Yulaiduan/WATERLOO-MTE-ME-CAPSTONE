# Comparison workspace

Owner: Andy Zhang. Updated: 2026-10-10. Status: experimental browser data tool.
Use [Comparison](http://127.0.0.1:4186/?tab=compare) after starting the existing
project-local **Start Motion Lab.cmd**. The tab sits beside Profiles & data.
Source: [UI](../web/comparison.js), [pure data model](../web/comparison-data.js)
and [contract tests](../tests/comparison.test.js).

## Load, select and arrange

Import several run/profile JSON files, or select library records using
Load profiles / recordings. Profiles contain settings only: Load selected
(run profiles), or the library's Run profile action, explicitly calls the
matching solver and appends a new run. Add run uses already recorded data.
A profile is not silently treated as a dataset. All source records/configs
remain available for provenance and individual original-JSON download.

Click a plot to make it active. Search the right-side channel list, then click
a channel to add every loaded source with that matching channel/family/unit to
the active plot. Each plot has its own trace checkboxes; Plotly legend clicks
also toggle only that plot's trace. Show legend controls legend display without
changing visibility. Zoom, pan, reset and image export use local Plotly.

Split horizontally for side-by-side plots or vertically for stacked plots;
splits can nest. Limits are eight plots, 32 traces per plot, four separate unit
axes per plot and 64 source recordings. Time-based data and sample-index data
cannot share an x axis. Unknown-unit channels use explicit source-unit axes;
their appearance does not establish physical equivalence.

## Compact plotting controls

The comparison starts with compact headers, collapsed per-plot **Controls** and
collapsed **Sources & help**. Open Controls for splits, reference/mode selection,
trace visibility and legend settings; open Sources & help for imports, exports,
library loading and interpretation notes. **Hide channels** gives the sidebar's
width to the plots. **Focus plots** temporarily hides the app header/navigation,
sidebar, plot controls and legends; **Exit focus** or Escape restores the view
without changing selected data, traces or each plot's saved legend preference.
Charts are taller and can be resized vertically. Resize observers fit Plotly to
sidebar, focus and split-layout changes. Source provenance and numerical warnings
remain available; compact presentation does not discard data.

## Signed delta and statistics

Choose Signed delta and a reference recording for each plot. The convention is
**candidate minus reference**. Subtraction requires the same channel name,
mechanism family and documented units, plus recorded t/time in seconds.
Wheel and standalone-lever loads cannot be interchanged. Unknown-unit datasets
can be overlaid but do not qualify for physical deltas without documented units.

The sample grid is the union of both recordings' timestamps within their shared
time interval. Linear interpolation uses adjacent valid samples, never
extrapolates and never bridges missing values. Times must be finite and strictly
increasing; duplicates are rejected rather than silently reordered.

Statistics report maximum absolute delta, RMS, signed final delta, its time and
valid sample count. RMS is over these matching samples, not a time integral or
time-weighted RMS; differing sample densities affect it. Final means the last
valid shared sample, not an extrapolated endpoint.

Pymunk joint forces are step-averaged impulse/dt; mathematical loads are
instantaneous. Startup constraint initialization can dominate full-window maxima.
Inspect initial samples, state the comparison window and refine timestep before
interpreting force differences. Delta is model discrepancy, not a hardware error
or a proof that either implementation is correct.

## Portable workspace

Export comparison JSON uses schema motion-lab-comparison/v1. It retains full
original source records/results/configs, recursive split layout, each plot's
mode/reference/trace visibility/legend setting and the active plot. Import
validates the workspace and original records before restoring it. Normal
80 MiB JSON bounds apply to the actual exported file. Comparison exports use
compact JSON formatting so indentation cannot push an otherwise valid workspace
over the import limit. The browser library remains local to its origin;
downloaded JSON is the portable backup. No cloud upload or server file
persistence is implied.

## Reproducible suspension comparison

From the app root:

```sh
.venv/Scripts/python.exe scripts/compare_suspension_models.py
node scripts/verify_comparison_ui.cjs
```

The [comparison script](../scripts/compare_suspension_models.py) writes four
portable SciPy/Pymunk run records plus summary JSON under ignored
artifacts/model-comparison. It uses a 200 mm wheel, 273 mm links, 45° initial
pose, 30 mm / 250 ms quintic step and six seconds. It compares original tip
and replacement constant-lift profiles at 1/.5 ms, using the UI's union-time
sample convention. Full-window and after-50-ms force statistics remain separate.
Measured results and actual test scope are in [validation](validation.md).
The wheel core's previous full audit is retained without claiming it was rerun
for this browser-only comparison feature.
