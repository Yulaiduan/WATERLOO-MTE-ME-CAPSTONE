# MD and RF catalogue additions — 2026-11-13

Updated workbook: `../../outputs/2026-11-13-md-rf/spring-catalogue-expanded.xlsx`.
The eight existing sheets are preserved byte-for-byte in their original XML;
MD and RF are appended. Existing catalogue files are not overwritten.

## Coverage

- MD: 52 McMaster-Carr part/package entries with nominal E_T >=60 J, screened
  from 793 distinct part numbers in the Color-Coded Die Springs listing.
  Individual and package part numbers remain separate purchase options.
  These represent 29 distinct rate/travel/free-length/hole combinations.
  Nominal energy 63.45–164.96 J; free length 76–203.2 mm.
- RF: 164 orderable FOX part numbers, including SLS and standard steel springs.
  All pass the nominal >=60 J screen. Nominal energy 88.27–402.41 J;
  free length 108.712–209.55 mm. FOX springs here are rear-shock compression
  springs, not tooling die springs.

Sources:
- https://www.mcmaster.com/products/die-springs/
- https://tech.ridefox.com/bike/general-info/918/2020+-sls-and-standard-steel-rear-shock-spring-information

## Definitions and limitations

E_T = k × min(published travel, F_max/k)^2 / 2000, with N/mm and mm,
assuming a linear compression spring with zero force at its free length.
For MD the published maximum force, rate and compressed length bound screening.
Rounded source values can disagree slightly, so energy uses the smaller limit.
Travel and l_min retain the supplier's stated compressed-length endpoint.
Installation hole and shaft sizes are not actual coil OD/ID and are kept separate.

FOX does not give an independent force rating in this table. F_max is DERIVED
as rate × marked spring travel. l_min is free length minus marked travel;
it is not measured solid height or a certified working minimum. FOX states SLS
shock travel must be LESS than the marking on the spring. Reserve preload and
stroke margin: RF E_T is an upper ceiling, not guaranteed operating capacity.
Where rounded mm and inch travel disagree, use the smaller converted travel.
Original descriptions, internal part numbers and compatibility cells are retained.
Unknown OD, wire dimensions, independent force/cycle ratings and price are blank.
Rows identify this review requirement; no VSL fit or fatigue qualification is claimed.

## Checks and refresh

All 216 new energy results were compared with independent calculations.
Representative force changes recalculated E_T correctly on both tabs, then were
restored. No formula errors were found. Both new sheets were rendered and reviewed.
Native hyperlinks and combined frozen panes are present. Original package parts
were compared during append; only global registries/styles were extended.
Validation records sit beside the workbook. Native desktop Excel was not exercised.

Normalized records: `data/md-rf-springs.json`; ID map: `data/md-rf-id-registry.json`.
Captured public source data: `data/raw/2026-11-13-md-rf/` (ignored by Git).
The retained `scripts/add_md_rf.py` prepares payload/build/merge files using saved
captures in `.work/md-rf-20261113/`. Do not reorder IDs on refresh; reuse the ID map.
The added tabs follow the prior supplier-addition schema and contain metric and
imperial values, E_T directly before k, package prices where supplied and links.
V6 currently imports MC/ME only; MD/RF require a future importer change to be searched.
