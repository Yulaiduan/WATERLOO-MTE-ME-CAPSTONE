# Shared contracts and utilities

**Status: conventions only; schemas and reusable packages not implemented.** This is the compatibility boundary for firmware, simulation and training.

Add language-neutral definitions under `interfaces/` as agreed: joint identifiers/order, SI units, frames, timestamps, observations/actions, commands/telemetry, limits, frequency and compatibility version. Add portable utilities only when multiple components need them.

Consumers can generate or implement Python and embedded bindings from the same contract. Document reproducible generation and checks. Shared code must not import simulators, cloud SDKs or board drivers; firmware must not require Python at runtime.

Breaking changes need a version change, affected-consumer updates and validation in one contribution, or a documented backwards-compatible transition. Define policy metadata so exporters and inference consumers agree on normalization, order, scaling and timing.

Physical models/parameters belong in [assets](../assets/README.md); component-specific defaults stay with their component.

[Repository architecture](../README.md#repository-architecture)
