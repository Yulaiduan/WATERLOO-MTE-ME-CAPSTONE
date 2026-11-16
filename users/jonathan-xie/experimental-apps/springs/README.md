# Springs catalogue

Jonathan Xie's spring-selection reference for the experimental VSL v5 backend.
Prepared 2026-10-28 from the public McMaster-Carr catalogue. This is a supplier
data snapshot and analytical unit conversion, not a selected or tested spring.

## Open the workbook

Open `outputs/2026-10-28-mmc-springs/mmc-spring-catalogue.xlsx`.
MC, ME and MT contain compression, extension and torsion records respectively.
The first three columns are the persistent catalogue ID, McMaster part number
and clickable part link. Metric engineering fields precede the normalized
imperial fields and original supplier attributes. Filters and frozen identifiers
support scanning the wide tables. ReadMe defines lengths, derived quantities,
source scope and the VSL mapping.

The supplied URLs contain 2,120 standard compression, 4,719 extension and 558
torsion part numbers: 7,397 in total. Extension includes cut-to-length stock,
overload-prevention and rubber products and assortment packs. These remain in
the catalogue with explicit screening statuses. The supplied compression URL is
the standard Compression Springs family; other compression families such as
precision, die, disc and rubber compression springs are outside that URL's scope.

Sources:

- [Standard compression springs](https://www.mcmaster.com/products/product-line~~springs-and-shock-absorbers~~2q3Rr81D/compression-springs-1~/compression-springs-1~~/)
- [Extension springs](https://www.mcmaster.com/products/product-line~~springs-and-shock-absorbers~~2q3Rr81D/extension-springs-1~/)
- [Torsion springs](https://www.mcmaster.com/products/product-line~~springs-and-shock-absorbers~~2q3Rr81D/torsion-springs-2~/)

## Reusable data

`data/mc-catalogue.json.gz`, `me-catalogue.json.gz` and `mt-catalogue.json.gz`
contain one JSON object per part with explicit metric and imperial numeric keys,
original listing fields, individual specification attributes, drawing URLs and
selection notes. A standard gzip reader can load these without Excel.
`data/id-registry.json` maps part numbers to catalogue IDs. Keep it during refreshes:
new part numbers receive new IDs and existing parts retain theirs.

Null means unknown or not applicable, never zero. `selection_status` and `notes`
identify missing ratings, cut stock, assortments, rubber and torsion model needs.
`coverage.json` records the observed source counts and detail-page coverage.
Compressed source captures are retained under `data/raw/` for reproducibility.

## VSL v5 connection

The inspected local source is `../vsl-solver/v5/v5-fall.html`, particularly
`VSLSpring.geometry`, `VSLSpring.interval` and `VSLSpring.state`.
V5 uses mm, N, degrees and motor torque in N m:

```text
Fs(theta2) = max(0, p0 + springK * [c(theta2) - c(90 deg)])
tauS = -Fs * dc/dtheta2 / 1000
```

`c` includes tangent span and pulley wrap. The sidebar's signed endpoint span
change `lc-le` is not the required cable-payout stroke when pulley radius is
nonzero. `p0` is the force reference at 90 degrees, sometimes extrapolated. It
is not McMaster initial tension and does not by itself specify installed length.

For a nominal extension spring on its extended branch:

```text
installed_length(theta2) = free_length + [Fs(theta2)-initial_tension]/k
```

Check this length and the manufacturer's force limit over the entire working
range, initially theta2=100 to 165 degrees. Do not assume the two endpoints
bound a nonmonotonic payout. V5's interval function evaluates internal extrema.
Forces below initial tension need the closed-coil / cable-slack installation law,
rather than extrapolation to a physically negative extension.

A selector should first reject impossible force, stroke, length, diameter,
attachment and environmental combinations. Then hold each available k and fit
the permitted geometry/preload variables, ranking the resulting residual torque
over the requested interval. Manufacturing tolerances require an uncertainty
study in addition to the nominal fit. Compression needs a mechanical arrangement
that supplies cable tension. Direct torsion requires a torque/angle and mounting
model, not substitution of N mm/rad into a N/mm field.

Torsional stiffness is derived as `T_max / radians(rated_deflection)`. Preserve
the supplier torque and angle separately. The listed shaft diameter is a mounting
limit and must not be mistaken for coil ID. Coil ID and mean diameter derived
from OD and wire diameter are explicitly labelled nominal derived quantities.
McMaster describes left-hand springs as winding clockwise toward the viewer,
and right-hand springs as winding counterclockwise toward the viewer. Preserve
the supplier drawing's viewing direction when assigning a mechanism torque sign.

## Rebuild and checks

The retained scripts use Python's standard library and the Codex spreadsheet
runtime's `@oai/artifact-tool` package. No repository dependency files or VSL
solver code were changed. In an environment providing those dependencies:

```text
python scripts/normalize_catalogue.py --input data/raw --output .work --registry data/id-registry.json
node scripts/build_catalogue.mjs .work outputs/2026-10-28-mmc-springs
python scripts/finalize_workbook.py outputs/2026-10-28-mmc-springs/mmc-spring-catalogue.xlsx .work/catalogue-payload.json
```

The normalizer preserves source ratings, including Not Rated values. The workbook
builder checks conversions and recalculation, renders every sheet and scans for
formula errors. The finalizer adds native hyperlinks because the authoring
engine cannot evaluate HYPERLINK, and verifies combined frozen rows/columns.
The validation record describes the actual completed checks.

Refresh requires revisiting the supplier's public UI; the scripts rebuild from
saved captures and do not provide an unattended scraper. Prices are a dated
snapshot in USD per package or each. Fatigue life, stress, strength, friction,
dynamic spring behavior and a physical installation remain unvalidated.

All changes for this request are local to this folder. No commit or push is part
of this delivery. Generated workbooks, captures and local dependencies are ignored
by Git; source data and scripts can be reviewed before publication.

## Small pulley research — 2026-11-11

[SG20, compact sheaves and VSL v6](research/2026-11-11-pulleys/README.md) records supplier load ratings, the current saved spring/horn geometry references, rope-centreline radius, Dyneema bend constraints and shaft support calculations. Preliminary screening only; all existing workbooks and solver files remain unchanged.

## Additional suppliers — 2026-11-11

The expanded copy at `outputs/2026-11-11-suppliers/spring-catalogue-expanded.xlsx` includes ST (STEINEL,187), BT (Berger/Special Springs,33), MI (MISUMI,35) and SW (Swift,127):382 selected compression springs with nominal operating-envelope energy >=60 J and free length <=254 mm. [Research and DP9/v6 context](research/2026-11-11-suppliers/README.md) explain travel/life limits, dimension provenance and reproduction. New records/IDs are in data/additional-springs.json and data/additional-id-registry.json. The original builder still regenerates only MMC; preserve the pre-expansion backup and use the supplier addition scripts for a complete rebuild. V6 currently reads only MC/ME; these new tabs require an explicit future importer update before V6 searches them.

The original MMC workbook was locked during delivery and remains unchanged. Open the expanded copy above to see the new supplier tabs.

## MD and RF additions — 2026-11-13

Latest expanded workbook: `outputs/2026-11-13-md-rf/spring-catalogue-expanded.xlsx`.
Adds MD (52 McMaster die-spring part/package entries) and RF (164 FOX rear-shock
springs), keeping nominal E_T >=60 J. All eight previous tabs are preserved.
FOX force is derived from rate and marked travel; energy is a nominal ceiling,
with preload/stroke margin still required. [Coverage, sources and limitations](research/2026-11-13-md-rf/README.md).
