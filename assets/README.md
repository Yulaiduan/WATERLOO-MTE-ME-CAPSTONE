# Canonical robot assets

**Status: scaffold; existing local models have not been moved.** Reusable models, meshes and physical parameters belong here.

## Locked baseline

Every change here requires human code-owner review. Do not change the model and
its expected values just to make a failed check pass. `manifest.json` currently
contains no robot, so both physics commands deliberately fail. Register a reviewed
MJCF model and its independently checked physical baseline before enabling them.

Manifest schema 1 requires `files` (relative asset path to SHA-256, covering all
payload files) and `models` (one entry per executable robot MJCF). Each model entry
has `path`, `body_masses_kg` (every named non-world body) and `joints` (every named
joint, each with `type`, `limited` boolean and two-number `range`). Joint ranges
are in m for slide joints and rad for angular joints. For free/unlimited joints,
record the compiled range and `limited: false`; it is not an enforced limit.
The baseline comparison uses absolute tolerance 1e-12 and zero relative tolerance.

All includes, meshes and textures must be inside this directory and hashed.
External/parent-relative paths and symlinks are rejected. Record source, approval,
units, frames and assumptions in the model's adjacent README. URDF sources need
a reviewed MJCF conversion; the validator does not silently skip them.

Add `robots/<robot-name>/` with reviewed imports. Keep one canonical source per shared model/parameter set, recording units, frames, assumptions, provenance and revision. Document derived formats and simplified geometry; conversion scripts belong with their owning component.

[Simulation](../simulation/README.md) and [training](../training/README.md) reference these assets rather than copying them. Firmware may consume explicitly exported, reviewed parameters, without needing to parse simulator assets.

Keep small text assets in Git; agree on Git LFS or artifact storage before adding large binaries. Retain stable references/checksums for externally stored assets. Partner materials require agreed sharing permission. Documentation figures remain adjacent to their topic under `docs/.../assets/`; generated runs do not belong here.

[Repository architecture](../README.md#repository-architecture)
