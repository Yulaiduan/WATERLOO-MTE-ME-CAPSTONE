# Toolkit architecture

Author: Andy Zhang with Codex. Updated: 2026-10-10. Status: member experiment.

One loopback-only Python server serves the Pymunk API and all web routes. `motion_input.py` computes displacement/velocity/acceleration trajectories in SI. `physics.py` builds the actual space and records solver states; `debug_view.py` captures engine draw callbacks and object descriptions. `debug_gui.py` calls the same builder/input helper in a live Pygame viewer. Browser Pymunk motion is recorded playback, not a second physical model.

`scripts/record_position_preview.py` regenerates the embedded floating-chassis step/square traces and actual debug primitives. It decimates display frames and retains trace-bucket extrema; full solver exports remain available in the main bench.

The seven rough-motion HTML fragments and retained remote playback live under `animations/`. `scripts/build_animations.py` wraps them using local app-owned styles and a standalone state adapter, replacing D3's CDN reference with the local library. Generated `web/animations/` and `web/recorded/` remain ignored. The gallery links them to `/force-plots/`, the editable static calculator source.

The detailed continuous-mechanics solver is isolated under `src/linkage/`, with browser workers and ml-matrix. Vite builds its `linkage/index.html` into ignored `web/linkage/`, using a `/linkage/` asset base. The main Python server can serve those static bundles without importing that solver or sharing live physical state with it. See [detailed mechanics](linkage-model.md).

Python and Node dependencies are pinned in requirements/package manifests and npm's lockfile. The server and Windows launchers resolve paths from their own files. Port-specific PID/creation-time records prevent stopping a different app; 4186 is the unified toolkit, and 4175 preserves legacy geometry routes. No code in canonical simulation imports this member toolkit.

Experiments and all runtime exports go under ignored `artifacts/` or `.preview/`. The selected screenshot equations are compact reference sources, not canonical physical data. Private transcripts, environment binaries, node_modules and frame dumps are excluded from publication.
