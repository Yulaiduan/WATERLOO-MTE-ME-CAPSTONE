# GPU job deployment

**Status: scaffold; no provider, image, runner or launch command configured.** GPU images, environment configuration, submission and artifact transfer belong here.

Add `images/`, `jobs/` and `scripts/` as needed. Launch a pinned repository commit with dependency/image versions, training config, seed, resources, runtime/cost limit and artifact destination. Invoke the existing [training](../training/README.md) entry point; do not copy training or simulation implementations into job scripts.

Use provider secrets or the local environment for credentials and commit only safe config examples. Record GPU/driver/backend compatibility. Add verified provision, smoke-run, submit, inspect, cancel, download and cleanup procedures when implemented. Save checkpoints and manifests to durable approved storage; machine-local scratch is not a retained result.

Full GPU jobs are explicitly launched, not automatic on every pull request. Firmware flashing remains in [firmware](../firmware/README.md); on-robot policy deployment requires a separately selected runtime.

[Repository architecture](../README.md#repository-architecture)
