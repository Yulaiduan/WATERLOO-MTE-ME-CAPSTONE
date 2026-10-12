# Wheel / link sizing and force calculator

Owner: Andy Zhang with Codex. Updated: 2026-10-12. Status: experimental analytical study.

Run **Start Motion Lab.cmd** at the app root. Choose Miscellaneous → Wheel / link
sizing, torque & travel, or open <http://127.0.0.1:4186/force-plots/>. Sources here
are served directly; no new dependency or solver endpoint is needed.

The new sizing study precedes the preserved constant-torque force/animation
calculator. `link-sweep-model.js` owns geometry, conversions, integration and
enumeration; `link-sweep.js` owns controls, Plotly, selection and JSON/CSV.
See [the sizing model](../../docs/link-sizing.md) for definitions, equations,
sampled results and limits. Scripts/tests are retained under the app's existing
folders. `node scripts/verify_link_sweep.cjs` verifies the browser workflow;
`npm test` includes the independent sizing checks.

New config JSON uses `motion-lab-link-sweep/v1`, containing `config`, selected
metrics and an experimental scope declaration. Load it through this calculator's
Load configuration control. It is separate from a dynamic solver profile or
recording. CSV exports every feasible candidate with explicit units, torque
coordinate, averaging method, net load and wheel diameter. Session storage
remembers current inputs; JSON is the portable backup. Legacy force-calculator
widget state and data are unchanged. No cloud upload is performed.
