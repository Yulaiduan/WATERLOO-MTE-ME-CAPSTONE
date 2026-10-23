# Offline Plotly runtime

Pinned official Plotly.js basic4.1.2, MIT licensed. The unmodified minified
distribution is stored with deterministic gzip compression as a normal vendor
dependency. `plotly-manifest.json` records the exact official URL, lengths and
SHA256 hashes; `PLOTLY-LICENSE.txt` retains its license.

Kinefold's standard-library preview server decompresses this fixed asset at
`/vendor/plotly-basic-4.1.2.min.js`. There is no CDN request, build, package install
or machine-specific runtime path. The basic bundle supplies all scatter/line
data charts used here. The compressed asset stays below the repository's1MiB
per-file limit; the rules are unchanged.

Default Plotly image download is disabled to keep artifacts out of Downloads.
Existing contextual chart JSON/CSV exports continue to use app-local exports/.
