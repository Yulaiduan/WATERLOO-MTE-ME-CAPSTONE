# Andy Zhang — workspace reorganization, 2026-10-10

The owner requested that the old loose Capstone workspace be archived without
deleting files and that Capstone become the repository itself. The old content
now lives in sibling Capstone_Old; the repo retains its remote, branch/history
and member folders at the parent checkout root.

All 4,534 original files have matching SHA-256 and all 431 original directories
remain. The emptied nested repo container was archived, not deleted. A complete
[source/evidence/output backup](../../../users/andy-zhang/experimental-apps/capstone-archive/README.md)
restores 668 files exactly; installed dependencies, caches, logs and rebuildable
dist remain local. Large original data/PDF/GIF/run/frame outputs are split ZIP
payloads to respect existing per-file limits; the source apps remain directly
editable and the archive scripts execute no payload code.

Maintained tools: [Terrain Mobility Atlas](../../../users/andy-zhang/experimental-apps/terrain-mobility-atlas/README.md)
at port 4175 includes terrain atlas, numerical workbench, historical linkage
and force calculator. [Wheel Leg Lab](../../../users/andy-zhang/experimental-apps/wheel-leg-lab/README.md)
at port 4186 includes both chats' motion studies and the position-input Pymunk
bench; the user confirms floating chassis with prescribed wheel height.

The imported atlas's 49 model tests, build, worker/UI/browser checks and both
relocated launcher lifecycles pass. Stop/start helpers archive state/log files
instead of deleting them. App-local launchers resolve their own folder; no login
automation, canonical asset change or hardware validation is implied.

Continue from the member app index and each app's context/validation records.
The optional Wheel Leg Lab geometry launcher shares port 4175 with the atlas;
use only one there. Preserve archive hashes and original local content when
performing any future cleanup.
