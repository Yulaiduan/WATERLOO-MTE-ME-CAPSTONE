# Physics validation

First classify the contribution with `python tools/physics_gate.py --base origin/main`.
For eligible [preliminary research](preliminary_research.md), canonical physics is
not applicable; the gate runs regression checks instead. The instructions below
apply to executable robot, asset, configuration, dependency and mixed changes.

1. Use the pinned environment from `simulation/requirements.txt`. Do not import
   viewers during headless checks or require a GPU for CPU validation.
2. Treat `assets/` as locked. Inspect `assets/manifest.json`, provenance, hashes,
   body masses (kg), joint ranges (m/rad) and reference source before edits.
3. Run `python simulation/run.py --headless-check`, then
   `python simulation/experiments/verify_backend.py`. Record actual outputs and
   versions in the contribution log. Zero drift means exact repeated integration
   state in this environment, not identical trajectories on every machine.
4. Missing models/dependencies, unsupported formats, non-finite state, warnings,
   manifest mismatch and drift must exit nonzero. Never tick a blocked checklist.
5. Add meaningful scenario tests for changed controllers, contacts and limits.
   An identical but incorrect rollout can still be deterministic.
6. Acceleration claims require a selected backend, warm-up, equivalent physics,
   hardware/config/versions, repeated timing and declared error tolerances. The
   current suite measures CPU baseline throughput only. GPU status is unverified.

See the [MuJoCo simulation reference](https://mujoco.readthedocs.io/en/stable/programming/simulation.html).
