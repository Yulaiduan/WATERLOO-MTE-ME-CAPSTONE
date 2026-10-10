# Animation sources

Owner: Andy Zhang. Updated: 2026-10-09. Status: exploratory kinematics and recorded fixture playback.

Seven editable HTML fragments retain the current motion studies from the rough-animation chat. `pymunk-remote-preview.html` retains the current recorded force/impulse playback from the wheel/link-ratio chat. Build portable pages with `python scripts/build_animations.py` from the app root; the generated pages are ignored under `web/animations/` and `web/recorded/`.

The gallery labels timing reindexing as an earlier alternative, because the later user constraint prohibits moving/reindexing the grounded pulley. The fixed 4:1 example approximates short left-side strokes; it is not an exact straight full inversion. None of these geometric visuals proves joint clearance, belt contact, spring performance or robot terrain capability.
