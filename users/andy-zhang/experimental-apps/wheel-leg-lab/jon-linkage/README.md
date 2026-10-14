# Jonathan v2 linkage integration

Owner: Andy Zhang. Updated: 2026-10-14. Status: experimental analytical design.

Motion Lab's Math and 2D Physical tabs offer **Jonathan v2 · separate belt linkage**.
They share one mounted editor, separate from the existing spring suspension and
invertible fixtures. Open `/?tab=math&model=jon-v2`, `/?tab=physics&model=jon-v2`
or `/jon-linkage/` at the existing loopback port 4186.

`npm run build` reads Jonathan's original
[v2 source](../../../../jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html)
and builds an ignored web page, preserving its three analytical model scripts
exactly. The source manifest records SHA-256 hashes; missing source or a changed
UI insertion interface fails the build. No second retained solver copy is created.

The original controls include unequal L2/L3, three independent belt ratios and
all six pulley radii, wheel radius, mounting/phase/working angles, signed contact
loads in global or normal/tangential coordinates, five masses, gravity, effective
compound-pulley inertia radius, three slack-side preloads and master windows.
Both motor torques, all belt tensions/pin loads, five FBDs, twelve load plots,
three geometry plots, bounded global maxima, presets and original JSON/CSV remain.
Read Jonathan's [model and conventions](../../../../jonathan-xie/experimental-apps/leg-solver/v2-model.md).

The adapter adds dark mode, shared tab state, session refresh recovery, full
parameter profiles in the existing library, import of original v1/v2 JSON and
four-sweep datasets with units/provenance. Save profiles with the tab's library
button; save sweeps inside the editor. Comparison can reevaluate saved profiles
without changing live controls. Parameter sweeps have no time channel: overlays
use sample indices and time deltas remain unavailable. Original CSV retains the
actual sweep abscissae and branches. Invalid drafts cannot overwrite valid memory
or export a new profile; overlapping pitch circles prevent saving force sweeps.

Lengths/radii are **mm**, angles **degrees**, masses **kg**, forces **N**, torques
**Nm**, inertias **kg·m²**. A is fixed; C wheel centre; P contact patch (v1's P
means wheel centre). Loads are prescribed independently of mass; inertias are
stored only. The cycle is parameter playback. No spring, acceleration, dynamic
Pymunk counterpart, unilateral tire contact, no-slip rolling, 3D clearance or
hardware/canonical robot validation is added. Native/recorded Pymunk buttons
explain this boundary when this design is active.

Run `node scripts/verify_jon_linkage.cjs` after building and starting the server.
Source-model tests remain in Jonathan's app. Current evidence is recorded in
[validation](../docs/validation.md).
