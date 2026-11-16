# Additional spring suppliers, DP9 reference

2026-11-11. Preliminary supplier catalogue expansion for Jonathan Xie's VSL work. The expanded workbook has four new two-character tabs and 382 additional nominal linear compression springs. Existing MMC tabs, values, formulas and links are preserved.

## Scope and sources

| Tab / ID prefix | Supplier | Added rows | Source scope |
|---|---|---:|---|
| ST | STEINEL | 187 | SZ8005, SZ8010, SZ8020, SZ8030, SZ8040 and SZ8045; installation holes up to 63 mm |
| BT | Berger Tools, Special Springs brand | 33 | Blue B-series ISO 10243 springs; installation holes up to 63 mm |
| MI | MISUMI | 35 | SWM medium-load series; nominal OD 40, 50, 60 and 70 mm |
| SW | Swift Springs USA | 127 | Captured standard coilover tables, seating ID up to 2.5 inches |

All added records have nominal E_T >=60 J, free length <=254 mm, a supplier force limit, spring rate and operating/usable stroke. Minimum length is derived from free length minus that stroke and is explicitly distinguished from solid height. This is a selected compact subset, not an exhaustive capture of these manufacturers' catalogues or a stock-availability guarantee. All new parts are compression springs.

Primary/direct supplier sources:

- [STEINEL light springs](https://www.steinel.com/en/produkte-dienstleistungen/federn/systemfedern/online-katalog/system-springs/SZ8010), [medium springs](https://www.steinel.com/en/produkte-dienstleistungen/federn/systemfedern/online-katalog/system-springs/SZ8020), and [catalogue extract, version 08.2025](https://www.steinel.com/fileadmin/user_upload/STEINEL-CE-Springs-system-springs_en.pdf). Each row links to its actual family table.
- [Berger blue die-spring catalogue](https://www.berger-tools.co.uk/Die_Springs/B_Blue_Die_Spring_Iso10243_Medium_Load/). The public page loads its [full part table](https://www.berger-tools.co.uk/ajax_table-2019.asp?Do=SeriesTable&SeriesID=1). The supplier identifies the brand as Special Springs. Each part links to its product selection page.
- [MISUMI SWM rating table, printed pages 1419-1420](https://my.misumi-ec.com/pdf/press/18e_pr1419.pdf). The dated source is retained; confirm current availability/drawing when ordering. Individual part links use the supplier's part selector.
- [Swift standard coilover catalogue](https://www.swiftsprings.com/pages/standard-coilover-springs-1-88id). The page includes multiple seating IDs and lengths. Part numbers identify the selected row; the link opens the shared catalogue. Published usable stroke and maximum load are both retained.

Eibach, Cane Creek, Renton Coil Spring, Lee Spring and ASRaymond were also investigated. No rows from them were added in this pass: the captured information was incomplete for an operating-rated entry, inaccessible, or described block/solid limits rather than an established operating envelope. This is not a claim that they lack suitable products. For example, [Eibach's published ERS table](https://eibach.com/product/0500.225.0650) supplies block height/load, but those were not silently treated as safe repeated working limits. The old Renton MTB PDF was unavailable. Swift also supplies UTV and motorcycle ranges, but these additions use its documented standard coilover data rather than vehicle-fit descriptions.

## DP9 / newest v6 synchronization

The November 11 campaign uses DP9 “11/11 POR”: chassis 54 kg (13.5 kg sprung chassis share per leg), component inputs m2=0.92, m3=1.89, m5=0.59 and m6=2.7 kg, equal 296.3 mm links, alpha=0 and working theta2=120-180 degrees. Payload cases are 0 and 70 kg. Search bounds are r_h=50-95 mm, r_s=12.7 mm, S_v<=150 mm, |S_u|<=30 mm and unloaded inversion target -50 degrees. Clearance S_v-r_h must be at least 25.4 mm.

Nested compression group S0056-S0060 retains the preceding groups. Best saved S0056 has r_h about50 mm, S_v75.4 mm and S_u12.6012 mm. It pairs 96485K436 outside 96485K249. The outer spring is approximately124.61 mm OD and304.8 mm free length, illustrating the packaging concern. Its saved working cable-payout stroke is49.92 mm and inversion stroke92.83 mm. These are read-only saved-model references, not new fits or hardware measurements.

Energy alone does not establish the same torque balance, working stroke or inversion travel. A 60 J die spring may have only20-40 mm usable stroke at several kilonewtons. A new selection must refit geometry/preload and verify all case-specific force, length, energy, cable and nesting constraints. The high-rate short die springs will often be unsuitable for the same one-to-one cable/piston route unless geometry or transmission changes. Published fatigue/stroke bands also matter.

## Examples and tradeoffs

| Part | Source | OD / ID mm | Free length mm | Rated / usable stroke mm | k N/mm | Nominal E_T J |
|---|---|---|---:|---:|---:|---:|
| B50-076 | BT | OD48.8; ID unknown | 76 | 28.5 | 168 | 68.23 |
| B40-127 | BT | OD37.5; ID unknown | 127 | 47.6 | 62.7 | 71.03 |
| SWM40-125 | MI | nominal OD40 / ID20 | 125 | 40 | 78.5 | 62.72 |
| SWM50-125 | MI | nominal OD50 / ID25 | 125 | 40 | 123 | 97.60 |
| 060-250-100 B | SW | ID63.5; OD not confirmed | 152.4 | 119.38 | 17.5127 | 123.20 |

The Swift example is a useful long-stroke lead at a rate closer to the current MMC examples, rather than an accepted solution. It uses a supplier-listed max load2077.32 N, which conservatively limits nominal deflection slightly below the119.38 mm usable-stroke entry. Confirm barrel OD, current stock and installed preload before selecting it. Its public product page has shown sold-out status; catalogue inclusion does not imply immediate availability.

The compact B50-076 stores68.23 J at the maximum operating envelope but only30.32 J at the supplier's long-life stroke. Long-life energy is recorded independently throughout the die-spring tabs. There are126 additions with a known long-life envelope also above60 J:87 ST,14 BT and25 MI. Swift does not provide the same long-life rating band in the captured table. A blank long-life figure is unknown.

## Data definitions and workbook layout

First columns match the linear-spring convention: catalogue ID, supplier part number, clickable supplier part/catalogue link, E_T (J), k (N/mm), usable/rated travel, rated F_max, l_min, l_max, free length, initial force and nominal OD. IDs retain their source prefix plus four digits. Other columns contain nominal ID, spring type, supplier/family, long-life ratings/energy, nominal force at usable deflection, deflection needed for60 J, installation dimensions, rectangular wire dimensions, maximum physical stroke, price/currency/package quantity when published, material, ends, winding, standards, tolerances, temperatures, rating basis, notes, URLs, retrieval date and original supplier values. Imperial conversions follow the source/metric section.

Compression energy is calculated as E_T=k*x^2/2000 with k inN/mm and x=min(usable/rated travel,F_max/k) inmm. All new springs have zero free-state initial force. This is nominal energy from free length to the conservative intersection of stated operating travel and force limits; it is not guaranteed energy after dimensional/rate tolerances or energy released over a specific installed VSL stroke. Nominal l_min follows stated travel; the force limit may impose a slightly longer minimum length because of supplier rounding.

STEINEL reports installation hole/pin dimensions. They are retained in separate columns and are not substituted for actual OD/ID. Berger publishes approximate OD; guide-rod diameter is not treated as measured ID. MISUMI's D/d drawing dimensions are labelled nominal. Swift's seating ID is retained; OD remains unknown except for B3 rows explicitly described with3 inch OD. Unknowns are blank, not zero. Published maximum stroke is not substituted for Swift's shorter usable stroke. Rectangular-wire dimensions are not used to invent an ID.

Future V6 ingestion needs an explicit update: the inspected read_catalogue function still reads only the original first two sheets (MC/ME) and builds McMaster-specific links. Adding tabs does not automatically make these382 parts searchable in V6. The first12 fields and normalized JSON provide a starting interface, but the adapter must identify supplier/type by headers, preserve non-MMC URLs and keep missing dimensions unknown. This task does not modify solver code or saved solutions.

## Reproduction and validation

Normalized records: ../../data/additional-springs.json. Stable new IDs: ../../data/additional-id-registry.json. Saved public source snapshots: ../../data/raw/2026-11-11-suppliers/. Scripts: ../../scripts/expand_suppliers.py, build_supplier_tabs.mjs and merge_supplier_tabs.py.

Run the normalizer with the saved source directory. The authoring script requires the bundled @oai/artifact-tool runtime and a workspace package junction. Use a pre-expansion workbook snapshot as original.xlsx in its work directory; the original-only builder remains an MMC-only rebuild path. The merge adds artifact-authored sheets without round-tripping the existing source tabs. Keep the pre-expansion backup for a clean rebuild rather than adding duplicate supplier tabs.

Validation completed:382 independently computed energy values checked against recalculated workbook values; representative force changes recalculated energy correctly on all four tabs; no formula-error cells found; every new tab rendered and visually checked; expanded workbook reimported successfully. Added604 native hyperlinks and combined row/identifier freezes. All original worksheet XML and native link parts remain byte-identical. The four global package registries/styles are extended; all other original parts are untouched. Validation JSON records accompany this note.

The original catalogue could not be replaced because it is locked by another application. The finished expanded copy is saved at ../../outputs/2026-11-11-suppliers/spring-catalogue-expanded.xlsx, with all original tabs preserved. The original file remains unchanged and a pre-expansion backup is retained. V6 still points to the original path and needs its supplier importer extended before using the new rows. No native Excel UI, new VSL fit, hardware test, commit or push is claimed.
