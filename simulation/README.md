# Local simulation

**Status: scaffold in this branch; existing local MuJoCo work has not been imported.** Environments, viewers, controllers, diagnostics and experiments belong here.

Preserve existing local `run.py`, `experiments/` and other working paths during import. Include the actual dependency manifest and verified setup, viewer and headless-check commands. Raw output goes in ignored `results/`; selected small evidence goes into dated documentation benchmarks.

Use canonical [robot assets](../assets/README.md) and [shared contracts](../shared/README.md). Expose a documented environment API for [training](../training/README.md): reset/step behavior, observations/actions, timestep, termination and seeding. The viewer must be optional for headless execution.

Keep cloud jobs in [deploy](../deploy/README.md). Validate any accelerated backend against local behavior; a GPU alone does not establish physics acceleration or equivalence.

[Repository architecture](../README.md#repository-architecture)
