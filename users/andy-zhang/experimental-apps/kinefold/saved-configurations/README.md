# Saved Kinefold configurations

Owner: Andy Zhang with Codex. Captured: 2026-10-24, from app-folder library
revision 20 at source commit `156ba08`. Status: experimental portable settings.

These are exact `kinefold/project-v3` copies of the one named design and the
current working draft. They include geometry, view, solver controls and optional
interaction settings. The live `profiles/library.json` remains local and is not
modified by this publication. Raw simulation rows, exports, screenshots, logs,
browser backups and installed environments remain ignored.

| File | Captured state | Validation status |
| --- | --- | --- |
| [VSL V4 nominal, alpha zero](vsl-v4-nominal-alpha0.json) | Named design: alpha 0 degrees, theta2 135 degrees, 300/300 mm links, 200 mm wheel radius, 8.75 kg chassis, zero other masses; V4 coil; prescribed-height 150 mm square over 6.5 s | Matches the repository's saved VSL V4 nominal mechanical parameters. The October 23 local paired run completed with 656 matched samples and approximately 0.00594036 mm maximum chassis difference; that run is historical evidence, not a new physics check for this publication. |
| [October 24 working draft](2026-10-24-working-draft.json) | Same original name/ID, alpha 0 degrees, upper and lower masses 1 kg each, wheel and knee compound masses zero, actual terrain-contact mode; other settings retained exactly | Preserved unfinished input. The contact solver requires positive wheel mass and massless links/compound, so this setup is unsupported. Its zero-rise square input also needs review before prescribed-height use with moving link masses. It is not a passing contact or dynamic design. |

## Load on another computer

Pull the repository, launch [Start Kinefold.cmd](../Start%20Kinefold.cmd), and
use the app's **Import** button to select one JSON file from this folder.
Use **Save as...** to give an imported copy a separate named-library identity.
Both snapshots intentionally retain their original shared ID; saving the draft
directly as the named design would replace that named nominal design.

Imports use the existing project validation. A schema-valid configuration can
still be unsupported by a particular dynamics mode. Resolve the draft's actual
mass/model requirements explicitly before running it; no substitute wheel
mass, changed link masses or input transition was chosen during preservation.
These tracked snapshots are manual handoffs, not automatic library syncing.

## Verification and limits

Both snapshots parse as finite JSON, exactly match their captured source
projects and round-trip through the app's existing project importer. The nominal
parameters were checked against the tracked VSL V4 library, and the existing
contact validator rejects the preserved draft as expected. No new simulation,
browser import, hardware or canonical robot validation is claimed here.
Read the [app context](../context/README.md) and
[contact model](../terrain-contact.md) before modifying a configuration.
