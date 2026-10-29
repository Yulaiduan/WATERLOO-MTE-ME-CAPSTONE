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
