# Frozen numerical references

These fixtures support reproducible checks; the browser application does not load them.

- `solver-kernel.js`: verbatim `solver-model` script extracted from Jon's V4 HTML at commit `5e52a1220d4ecc9881a80995cbd882df1bfc9be6`, original Git blob `1aef847b69c4cba4c63960870cea4fd37c59f16f`. Its parent HTML was normalized CRLF→LF; retained SHA-256 `37767388cfd20ae6fe7a03fd932a75f13660f773db5c875b6d902f3a35208cff`. It is numerical source evidence evaluated in a blank VM by `node ../verify.cjs`; inputs are source mm/degrees, outputs source geometry. No UI or helper code is executed.
- `dp3.json`: DP#3 snapshot from `Designs!A4:BW4`, `VSL state!B6`, source workbook Git blob `64fe5e25920468c932e0f82b8571d73f236ddf2c`, retained October 23, 2026.
- `candidate-gains.json`: the October 23 independent analytical study's five gain examples and declared assumptions. Unused additional fields retain their original interpretations; they do not imply hardware selection.

[Original V4 source](https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE/blob/5e52a1220d4ecc9881a80995cbd882df1bfc9be6/users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-pulley.html). These are frozen fixtures so later edits to Jon's working app do not silently redefine the dashboard baseline. Keep them unchanged unless deliberately introducing a separately versioned baseline and documenting why.
