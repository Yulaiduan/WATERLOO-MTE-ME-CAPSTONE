# Detailed linkage handoff

Author: Andy Zhang with Codex. Updated: 2026-10-09. Status: experimental.

Start from equal links, guide ratio 2, zero phase and two 1:1 wheel-drive stages. q is from downward vertical; phi is independent chassis wheel-drive input. Vary ratios to inspect moving-carrier coupling. Enter measured masses, COM and inertias before interpreting loads; defaults are estimates. Physical spring and virtual impedance gains remain separate. Local poles require a valid equilibrium and unsaturated branch; a free wheel phase may remain nondecaying.

Build with npm run build and open /linkage/ through the [project-local launcher](../README.md). Run npm test for its 24 model tests. Optional independent energy verification uses python scripts/validate_linkage_reference.py with the analysis requirements installed. See [model](linkage-model.md), [validation](validation.md) and [both-chat continuation](handoff.md). No terrain, tire contact or team robot validation is claimed.
