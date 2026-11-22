# DieMax additions — 2026-11-21

Latest workbook: `../../outputs/2026-11-21-dm/spring-catalogue-expanded.xlsx`.
Adds DM0001–DM0139. All ten previous sheets and their native links are preserved.
Existing catalogue copies and VSL/solution workbooks are not overwritten.

Source: user-supplied `IEM-DieMaxSprings.pdf`, PDF pages 8–25 (printed 6–23).
A snapshot is retained in `data/raw/2026-11-21-dm/` and the sheet hyperlinks open
that PDF at the relevant page. No unverified supplier product URLs are invented.

## Coverage and engineering definitions

524 unique spring part numbers were screened from 958 table rows: 434 standard
rectangular-wire parts repeated in inch/metric tables, plus 90 round-wire parts.
139 rectangular-wire parts meet nominal E_T >=60 J; 385 parts are below threshold.
The selected parts comprise 26 light, 37 medium, 44 heavy and 32 extra-heavy loads.
No round-wire part meets the threshold. No maximum-length filter was applied.
Nominal energies are 61.009–446.694 J, and free lengths are 64–305 mm.

For a part repeated in both tables, the metric table supplies canonical ratings;
the inch originals remain in Original supplier values. This avoids counting the
same part twice. Normalized imperial columns convert canonical values exactly.
Inch rates are lbf per **0.1 inch**, requiring a factor of 10 before lbf/in use.
Metric/inch rate differences for selected parts are under 0.35% after conversion.

Core travel is min(published maximum OPERATING travel, published operating force/k).
E_T = k × travel² / 2000 for N/mm, mm and J. l_max is free length; l_min is free
length minus that conservative travel. Long-life and average-life energy use the
same intersection rule with their respective source loads/travels. Total travel
to solid, published force at solid and derived solid height are separate fields;
these are not an allowable operating envelope. Load-class life categories do not
supply a numerical cycle-life guarantee. Preload consumes the deflection allowance.

Installation hole/rod dimensions are not actual coil OD/ID. OD/ID, wire dimensions,
price, package quantity and numerical fatigue life remain unknown, not zero.
Several diameter cells extract incorrectly from the PDF text layer (for example
13/6 instead of the visible 12.5/7 mm). Metric installation dimensions were read
from the visible tables, including 12.5/7 and 16/8.5 mm. Original extracted lines
are retained as evidence and do not override the corrected visible dimensions.

## Reproduce and validate

Run `python scripts/add_diemax.py PATH_TO_PDF` from the springs folder with pypdf.
It writes payload/build/merge work files in `.work/dm-20261121/`. Use the bundled
artifact-tool Node runtime for build.mjs (arguments: springs root, work folder),
then bundled Python for merge.py (argument: work folder). The persistent ID map
is `data/dm-id-registry.json`; normalized selected records are `data/dm-springs.json`.
Keep the ID map on refresh. The PDF snapshot and outputs are ignored by Git.

All 139 maximum/long-life/average-life energies were independently compared,
geometry bounds and source-link targets checked, a representative force edit
recalculated and restored, and the new worksheet rendered and reviewed. No new
formula errors were found. Package comparison preserves existing sheet XML and
native links byte-for-byte; only shared workbook/style registries are extended.
No native Excel UI, physical spring, fatigue qualification or VSL fit was tested.
No solver/importer change, Git commit or remote publication is part of this task.
