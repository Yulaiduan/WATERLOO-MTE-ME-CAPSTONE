# Passive block-descent studies

Owner: Yulai Duan, prepared with Codex. Published October 20, 2026.
Status: reproducible experimental single-leg fixtures and analytical screening.
No canonical robot, motor rating or hardware validation is claimed.

Start with the [sharing index](../../../../docs/design/simulation/descent-studies.md)
for figures, results and the held-hip/heave explanation. The current baseline is
Jon's 8.75 kg chassis share, alpha 20°, two 300 mm links, 2:1 coupling, 200 mm
wheel radius and fitted 5 N/mm spring. The older studies deliberately retain the
13 kg / 0° / 100 mm-wheel reference. Do not mix their timing results.

## Reproduce locally

Use Python 3.11 and Node.js on PATH. From the repository root, install this app's
dependencies in your chosen environment:

```sh
python -m pip install -r users/yulai-duan/experimental-apps/block-descent-study/requirements.txt
cd users/yulai-duan/experimental-apps/block-descent-study
python jon_single_leg_descent.py --check
python jon_single_leg_descent.py
python jon_descent_height_sweep.py
python analyze_profile.py
python jon_baseline_descent.py
python verify_publication.py
```

The final command independently runs the new 22-case baseline and its five plots;
it does not need the legacy runs first. Raw CSVs/model XMLs, source snapshots,
JSON checks and generated figures go only under ignored `results/`. The previous
commands reproduce the 11-case legacy fixture, ten-case legacy height sweep,
and geometry-only quintic analysis. Startup here means batch scripts, not a web
server; no localhost launcher is involved.

All 43 contact integrations and the analytical profile checks were rerun from
this portable layout before publication, against the retained physical metrics.
Exact portability verification is recorded in `publication-validation.json`.
The earlier curated evidence retains its original script hashes; changes to
paths/runtime discovery/docstrings are identified in `publication-provenance.json`.

Optional `--render` on the two legacy scripts generates 1x PNG frames. Rendering
requires a working MuJoCo graphics backend. `encode_jon_descent_video.swift` is a
macOS AVFoundation encoder, retained for the earlier video procedure; its
publication does not claim Windows or Linux encoding support. Generated videos
and raw runs stay local rather than in Git.

## Inputs and limitations

`inputs/` contains a pinned snapshot of Jon's V4 numerical source and textbook
preset from commit `e91897a`, the precomputed library reference, and a transcribed
October 19 parameter preset. It does not include private Discord screenshots or
chat archives. See [source provenance](inputs/README.md).

Moving femur/tibia/wheel masses 0.6/0.65/1.5 kg are assumptions. No suspension
motor, gearbox/rotor inertia, cable losses or calibrated tire/stop compliance is
included. The horizontal velocity and pitch constraints are fixtures. Heave-free
means one chassis vertical degree of freedom, not a free four-leg vehicle.
Finite moving masses introduce a load mismatch with the new massless-link fit;
the flat-ground control is essential when interpreting body movement.

Production components must not import this member experiment. Read the
[app context](context/README.md) before changing or interpreting its physics.
