# Canonical robot assets

**Status: scaffold; existing local models have not been moved.** Reusable models, meshes and physical parameters belong here.

Add `robots/<robot-name>/` with reviewed imports. Keep one canonical source per shared model/parameter set, recording units, frames, assumptions, provenance and revision. Document derived formats and simplified geometry; conversion scripts belong with their owning component.

[Simulation](../simulation/README.md) and [training](../training/README.md) reference these assets rather than copying them. Firmware may consume explicitly exported, reviewed parameters, without needing to parse simulator assets.

Keep small text assets in Git; agree on Git LFS or artifact storage before adding large binaries. Retain stable references/checksums for externally stored assets. Partner materials require agreed sharing permission. Documentation figures remain adjacent to their topic under `docs/.../assets/`; generated runs do not belong here.

[Repository architecture](../README.md#repository-architecture)
