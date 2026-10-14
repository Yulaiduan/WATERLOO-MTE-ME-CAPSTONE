# Labelled report examples in Motion Lab

Author: Andy Zhang with Codex. Date: 2026-10-14. Source base: `12e227c`.
Status: experimental prescribed-kinematics visualization and curated GIFs.

The owner explicitly requested labelled Motion Lab examples and animation GIFs
for the leading options in the overnight report. This follow-up adds that
visualization only. The offline HTML/PDF reports, optimization, original 2D/Pymunk
models and existing wheel/link sizing tool retain their own scope and contents.

## Open and compare

Start the existing app-local **Start Motion Lab.cmd**. Choose Miscellaneous
studies, then **Alpha-zero design examples**, or open
[the menu route](http://127.0.0.1:4186/?tab=studies&study=design-examples).
The [direct page](http://127.0.0.1:4186/design-examples/) is also supported.

Five examples are selected from the retained source report. Alpha is zero and
wheel radius is 200 mm throughout. Values in this table describe the reported
working window, not the larger full-inversion envelope.

| Label | L2/L3 mm | Guide | Fixed phi0 deg | Total / usable mm | Chord deg | Max bow mm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 01: simple guide | 350/350 | 1.75 (7:4) | 0 | 325/285 | 12.020 | 9.659 |
| 02: longer, straighter links | 450/450 | 1.7925 | 0 | 325/285 | 10.069 | 6.162 |
| 03: near-equal indexed alternative | 275/250 | 2 | -25 | 343.099/303.099 | 11.895 | 1.544 |
| 04: exact indexed line | 250/250 | 2 | -25 | 325.998/285.998 | 12.500 | 0 |
| 05: screenshot reference | 250/250 | 5/3 | 0 | 338.616/298.616 | 16.634 | 21.91 |

The usable values subtract the same assumed 20 mm reserve at each end.
The phase alternatives relax the original phase-zero constraint; the phase
remains fixed through playback. They do not reindex the hip pulley while moving.
They do not solve projected full-inversion wheel clearance.

The page offers working-window and full-inversion views, all/single-example
selection, play/pause/restart, scrubbing, guide-circle/belt visibility and a
projected exclusion-disk toggle. All five use one common mm scale per view;
filtering a single example enlarges the panel while preserving its scale
convention. Guide radii, L2/L3, alpha, phi0, chord angle/bow, theta2/theta3,
vertical travel and current rim/hip margin are labelled.

World +y points right, +z up; A is the fixed hip, B the knee, C the wheel centre.
Theta2/theta3 retain Jonathan's V2 convention. The theta3 ray/arc starts at the
wheel-centre horizontal, with signed above/below-horizontal angle. The wheel
has K=0; no rolling constraint or hidden wheel spin is imposed.

The ideal guide uses the exact report equations. Each view moves theta2 smoothly
with a sinusoidal 4.8-second forward/back cycle; this timing is illustrative and
is not a motor velocity/acceleration requirement. This page performs no spring,
torque, contact or Pymunk simulation. The native Pymunk button gives an explicit
supported-fixture message here, rather than silently launching the old equal-link
wheel fixture as if it represented the selected example. Existing native model
launches and saved solver profiles are preserved.

## GIF delivery and provenance

[Ten compact GIFs](../web/design-examples/gifs/README.md) provide working and
full-inversion clips for every example. They render through the **same canvas
function** as the live page; there is no separately approximated GIF mechanism.
Each has 48 frames, 600x720 pixels, 100 ms/frame, an infinite loop and one shared
96-color palette per clip. A/C labels combine around the fold to avoid overlap;
literal coincidence is labelled A=C. No raw PNG folders are published.

The [GIF manifest](../web/design-examples/gifs/manifest.json) records exact byte
sizes and SHA256 hashes, delivered renderer/data hashes and source revision.
All ten GIFs regenerate byte-identically. Together they are 2,589,694 bytes;
the largest is 311,008 bytes, below the repository's 1 MiB per-file cap. These are curated
illustrations, not simulation-run recordings or accepted physical baselines.

The red disk is a projected wheel-centre exclusion of radius 220 mm: the 200 mm
wheel plus an assumed 20 mm gap. The current rim/hip margin is |C-A|-200 mm.
The colour flag remains present when the disk is hidden. Close screen labels
are not a claim that distinct centres coincide. No chassis shape, axial offset,
real contact or spring routing is invented. The historical dual-rope design
retains its **IMPOSSIBLE / rejected** status.

## Source and reproduction

The owning calculations remain in the sibling
[offline study](../../leg-design-study/docs/inversion-path-study.md) and
[selected evidence](../../leg-design-study/docs/inversion-path-results.json).
`build_design_examples.py` extracts five exact configs/metrics into the local
[data module](../web/design-examples/data.js), including the source SHA256.
The pose adapter is checked against Jonathan's original V2 rather than an
assumed legacy angle mapping. No canonical component imports these member apps.

Viewing the app/GIFs needs no additional dependency. Optional export uses the
existing Node.js 22 / Playwright and Python 3.13 environment, plus pinned Pillow:

```sh
.venv/Scripts/python.exe -m pip install -r requirements-animation.txt
.venv/Scripts/python.exe scripts/build_design_examples.py
node --test tests/design-examples.test.js
node scripts/export_design_examples.cjs
node scripts/verify_design_examples.cjs
```

Run export while Motion Lab is available on its local port 4186.
`MOTION_ANIMATION_PYTHON` may select another Python executable explicitly;
otherwise the exporter uses the app's own venv, never the desktop PC.
Raw frames go to ignored `artifacts/design-gif-frames/`. The ordinary app build
regenerates the data module and gallery navigation, without silently exporting
GIFs or running a physical solver. Other operating systems remain untested.

## Actual checks

- Python 3.13.12 / Node 22.23.3 / Pillow 12.3.0 used on this laptop; optional
  dependency install and `pip check` pass.
- `npm run build` passes. `npm test` passes **76/76**, including four new tests.
- Selected configs/metrics and the source hash match retained evidence exactly.
  Geometry agrees with original Jonathan V2 at **3,010 poses** across all five
  examples and both ranges, including inversion. Tests cover the mirrored
  phase-zero fold and exact indexed straight line.
- Actual Edge browser verification passes five cards, both modes and endpoint/
  midpoint scrubbing, play/pause, filtering, guide/disk toggles, ten downloadable
  HTTP GIFs, embedded menu selection and setting memory, dark theme and 390 px
  layout. No external requests or page errors. The new study's native-GUI action
  makes no native-launch POST and explains the supported fixture boundary.
- Each GIF reopens with 48 frames, 600x720 dimensions, 4800 ms total and infinite
  looping. Representative start/midpoint/end frames and browser/mobile drawings
  were visually reviewed. Labels at coincident hip/wheel centres were repaired
  and clips regenerated. Raw captures stay ignored.
- Actual app-root Stop/Start Motion Lab.cmd from an unrelated directory removes
  the 4186 listener and restarts successfully; the new direct page returns 200.
  No server/API, math/physics backend, old sizing default or lockfile changed.

An initial browser harness used a Frame method on a FrameLocator; correcting
that harness API produced the passing integration checks. No numerical or
physics tolerance was weakened. Canonical robot/hardware/contact/GPU/other-OS
validation is not applicable to these visualizations.
