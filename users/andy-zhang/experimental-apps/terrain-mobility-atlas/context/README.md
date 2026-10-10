# Terrain Mobility Atlas context

Owner: Andy Zhang. Updated: 2026-10-10. Imported from the former loose Capstone
workspace during the owner's requested nondeleting reorganization.

## Models and boundaries

The atlas screens 1,057 deterministic synthetic cells against chosen vehicle
capacity envelopes. Country outlines are geographic context, not terrain
measurements. Margin is normalized headroom, not probability or route access.
The workbench uses a prescribed spatial height profile/speed and a reduced
two-mass vertical suspension with unilateral compliant tire force; it excludes
whole-vehicle pitch/roll, propulsion, credible step climbing and structural loads.
Its measured USGS transect and synthetic profiles keep distinct provenance.

The historical `/linkage/` entry has a fixed-pivot guide/independent drive model.
The current prescribed-wheel-height/floating-chassis Pymunk bench is maintained
in [Wheel Leg Lab](../../wheel-leg-lab/README.md), not in this app.
Internal calculations use m, kg, s, rad, N and N m; UI converts mm, degrees,
percent grade and rpm explicitly. Unknown terrain/components remain unknown.

## Source and restoration

Source, tests, lockfile, modest runtime data, notices and design/model documents
are imported here. Larger data/PDF and original outputs are present in the local
working copy and ignored; the complete byte-preserving backup is the
[archive app](../../capstone-archive/README.md). A fresh clone can restore that
package to a separate new directory to inspect any original large evidence.
The runtime directly imports the retained small USGS CSV/provenance; large
evidence and frame dumps are not required to build or start the app.

## Setup and checks

Use installed Node.js and npm: `npm ci`, `npm test`, `npm run build` from this
app, then Start Capstone.cmd. Original routes are `/`, `/workbench/`, `/linkage/`
and `/force-plots/` at 127.0.0.1:4175. This port is shared with Wheel Leg Lab's
optional legacy geometry launcher; only one app can own it at a time. The
main Wheel Leg Lab port 4186 can run simultaneously.

The imported model tests, build, browser routes and restart lifecycle are
checked during this reorganization and recorded in docs/IMPORT-2026-10-10.md.
Historical validation records retain their dates and limitations. No canonical
robot or hardware validation is claimed.
