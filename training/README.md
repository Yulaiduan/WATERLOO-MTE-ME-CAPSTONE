# Training and evaluation

Use [the terrain specifications and proposed curriculum](../docs/design/simulation/terrain-training-spec.md) to plan scenario coverage, payload sweeps, held-out evaluation and run manifests. Source envelopes are candidate tests, not accepted performance requirements; unresolved parameters must be defined before running them.

**Status: scaffold; framework and training backend not selected.** Algorithms, rewards, observation/action adapters, configs, evaluation and policy export belong here.

Add `configs/`, `src/`, `tests/` and a dependency manifest with implementation. Provide a verified small local/CPU smoke run before GPU launch. Keep training and evaluation separate; record seeds and evaluation conditions. Generated output belongs in ignored `runs/` and `checkpoints/`.

Consume the [simulation environment API](../simulation/README.md), canonical [assets](../assets/README.md) and [shared contracts](../shared/README.md). Do not copy the environment here. Document whether GPU acceleration applies to learning, physics, or both.

Retained runs and exports need a manifest: commit, resolved config, seed, dependencies/backend, assets revision and interface version. Policies also need observation order/normalization, action scaling/limits and control frequency. Consumers must check compatibility. Evaluate policies in simulation before separately reviewed hardware integration; microcontroller inference is not assumed.

Infrastructure and job submission belong in [deploy](../deploy/README.md).

[Repository architecture](../README.md#repository-architecture)
