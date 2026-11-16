# Springs handoff

Jonathan Xie with Codex, 2026-10-28. Local catalogue preparation for VSL v5.

## 1. Scope and objective

Capture the supplied McMaster standard compression, extension and torsion
categories. Read the existing v5 static spring interface. No VSL code or
configuration workbook changes, physical spring choice, commit or push.

## 2. Files and interface

The workbook is under `../outputs/2026-10-28-mmc-springs/`. Normalized gzip JSON,
coverage and persistent IDs are under `../data/`; source evidence is under
`../data/raw/`. Authoring and verification code is under `../scripts/`.
The machine data uses explicit engineering-unit keys and preserves source text.

## 3. Validation

The source contains 2,120 MC, 4,719 ME and 558 MT part numbers, with individual
specification arrays for every part. Detailed final file checks are recorded in
`../validation.json`. Canonical robot physics is not applicable to this isolated
supplier-data workspace. No native Excel UI or physical hardware test is claimed.

## 4. Next work

Use v5 cable payout extrema over the chosen theta2 range, not the sidebar's
endpoint span difference, when checking spring travel. Map installed length and
initial tension separately from p0. Reject or review incomplete/inconsistent
ratings and nonstandard spring laws before optimizing geometry for each discrete
catalogue k. Direct torsion needs a separate torque/angle and mounting model.

## Pulley screening — 2026-11-11

See [the dated research](../research/2026-11-11-pulleys/README.md) and its screening-results.json. SG20 equivalent C0 is only 1.7 kN versus the supplied 5.374 kN radial envelope. Allen A3343-XHL is a compact 28.35 mm / 7.25 mm bore lead with a breaking-only rating; Ronstan RF48000HL is a 40 mm alternative with a current 1000 kg working rating and mandatory hub clamping. Confirm test/load convention and drawing. Rope bend life remains a separate constraint: Marlow's general Dyneema guidance is 8:1. No hardware was selected. Current saved geometry uses r_s=14.2875 mm and r_h about 83-120 mm; the November 5 distributed-mass model supersedes old saved mass assumptions. No v6 or Excel edits, commit or push. Reproduce arithmetic/snapshot extraction with python scripts/pulley_screen.py from the springs root.

## DP9 supplier expansion — 2026-11-11

[Additional supplier research](../research/2026-11-11-suppliers/README.md) supersedes the earlier pulley note's saved-geometry context for spring selection: DP9 chassis54 kg, links296.3 mm, working120-180 deg, unloaded inversion target-50 deg, r_s12.7 mm and r_h50-95 mm. Added382 rated nominal >=60 J compression candidates in four new catalogue tabs. Original tabs and links preserved. New V6 fits were not run; current importer remains MC/ME only and needs explicit supplier support. Long-life energy can be lower than maximum operating energy; short high-rate die springs are not assumed to meet inversion stroke. Reproduction/validation are in the dated note. All changes remain local to springs; no solver or solution-workbook edits, commit or push.

Delivery uses outputs/2026-11-11-suppliers/spring-catalogue-expanded.xlsx because the original was locked. It contains all original tabs plus ST/BT/MI/SW. The original V6 input path remains unchanged.
