# Simulation entry point

The portable entry point for every agent is `simulation/run.py`. The same commands
run locally and in CI. Paths resolve from the script location, so another current
working directory does not change asset selection. No viewer is imported.

## Setup and validation

Use Python 3.11 with a virtual environment at the repository root:

```sh
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r simulation/requirements.txt
python simulation/run.py --headless-check
python simulation/experiments/verify_backend.py
python -m unittest discover -s tools/tests -v
```

On Windows activate with `.venv\\Scripts\\Activate.ps1`. An equivalent fresh
environment installed with uv was tested on macOS on 2026-10-01 using Python
3.11.16, MuJoCo 3.14.0 and NumPy 2.4.6. Linux CI remains to be run after rollout.

**Current result:** both real physics commands exit 1 with “no canonical robot”.
There is no approved model in `assets/manifest.json`; do not record that as a pass.
The regression suite uses temporary synthetic fixtures and passes independently.
After a reviewed model/baseline is registered, the entry command checks hashes,
masses, joint constraints and a finite 200-step rollout. The backend command runs
two fresh rollouts and requires exact equality at every integration step.

Successful output is JSON with model paths, physical totals, versions, platform,
step count, time and (for the backend suite) zero maximum drift. Failures exit
nonzero. This is a zero-control CPU smoke test; scenario/controller tests and GPU
equivalence checks must be added with those implementations. No acceleration
claim follows from CPU timing.

## Layout

- `config/presets/`: Notion-derived terrain and geometry definitions.
- `src/environments/`: standardized Gymnasium wrappers.
- `src/controllers/`: kinematic and dynamic control.
- `src/viewers/`: optional UI, visualization and debugging.
- `experiments/verify_backend.py`: canonical baseline and repeatability checks.
- `results/`: ignored raw outputs, when needed.

Start terrain design from [the source summary](../docs/design/simulation/terrain-training-spec.md).
Robot models belong in locked [assets](../assets/README.md). Interfaces live in
[shared](../shared/README.md). Existing local demos and viewers remain outside this
branch until reviewed and imported; the canonical runner does not alter them.

## Execution record

Keep concise execution evidence in [the contribution log](../ENTRY_TEMPLATE.md).
Long logs and raw trajectories stay in ignored results. Selected engineering
results belong in dated `docs/benchmarks/` records with code/config/asset hashes,
versions, seed, units, method, limits and provenance.
