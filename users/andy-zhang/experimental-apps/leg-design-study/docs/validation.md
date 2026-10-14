# Standalone design study validation

The following records the original development verification before delivery was separated from Motion Lab. Final offline delivery checks are appended below.

## Development integration history, 2026-10-14

Base `6c74cfd`; scope is the isolated member app. Original Jonathan V1/V2,
legacy 2:1 solvers, saved profiles and dual-rope IMPOSSIBLE status are retained.
The current [study](generalized-leg-study.md), [math](generalized-leg-math.md)
and [physics](generalized-leg-physics.md) specify the distinct fixtures,
coordinates, optimizer domains, mass allocation and numerical limitations.

- Original Jonathan verifiers, executed with installed Node 22: kinematics
  3,853 assertions; quasi-static 16,044; global maxima 29,863. The screenshot
  signed torques, belt tension, final travel and headline extrema reproduce.
- `npm test`: all 85 JavaScript tests pass, including 13 new tests for extracted
  original-V2 parity, generalized Jacobians, Andy's equal-link special case,
  mm/degree buffers, load envelopes, quintic time weighting, constrained scalar
  refinement and Pareto nondominance. `npm run build` passes.
- `.venv/Scripts/python.exe -m unittest -v test_generalized_leg`: 12 tests pass.
  These compare actual existing Andy geometry/laws and shared inertia/gravity
  limits, all nine spring force-site/energy identities, V2 rotor conventions,
  non-2:1/unequal/tilted dynamics, massless-body rejection, manual preload,
  signed coordinate/gearing power and actual Pymunk in both directions.
- `scripts/verify_generalized_leg.py` passes all nine full one-second spring
  trajectories plus a tilted, unequal, nonzero-wheel-spin fixed-A fixture at
  2 ms and 1 ms. Actual motor constraint impulses are independent of analytical
  torque; pose resets or copied analytical torque are not used. Comparisons
  use impulse magnitudes, and report pin, guide, tracking and torque errors.
- Existing Python `test_math_model test_spring_mechanisms test_gravity_balance`
  pass all 34 tests. Their legacy SciPy/Pymunk refinement remains convergent.
  The unchanged complete legacy/native/GUI suite was not rerun for this change.
- `node scripts/verify_design_study.cjs` passes actual Edge controls, default
  screenshot pose, force-convention switching, exact 325/285 search, signed and
  magnitude profile curves, selection, finite CSV/JSON, late Worker rejection,
  explicit physical mass allocation, both raising/lowering backend validations,
  all nine spring table entries, cycle plots, stale-result clearing and 390 px
  layout. No external asset requests or JavaScript page errors occur. Buffer
  unit switches preserve geometry, and the embedded Motion Lab route retains
  both converted buffers across a study switch. Reviewed desktop, selected
  mechanism, spring/engine curves and mobile captures stay ignored in artifacts/.

The actual browser request uses assumed reduction 10 and efficiency .85 and
returns backend `generalized-study`, with cycle shaft peak .758681 Nm,
RMS .428386 Nm, speed 16.052319 rad/s and acceleration 65.729532 rad/s2
(181 output samples). Its direct-input peak is 6.448789 Nm. The retained
201-sample report case differs only by displayed sampling of these extrema;
no hardware tolerance or certification is inferred. All chosen-direction and
all-nine held-midpoint actual Pymunk checks return passed. Detailed all-nine
full-motion evidence and fitted parameters are in the physics/report records.

The first browser integration attempt caught HTML step/min combinations that
rejected the displayed corner mass and drum radius before POST. The defaults
and bounds were corrected, an all-initial-controls validity assertion added,
and the actual full backend workflow then passed. Review also corrected the
compound rotor's absolute angular slope to 1-qcd and its phase origin to the
extension stop; dedicated V2 checks cover both. Earlier rejected microgram-mass
and under-resolved engine attempts remain documented in the physics record.
No failure is reclassified as passing by weakening a numerical tolerance.

Actual app-root CMD stop/start from outside the app confirms the updated server
and new endpoint at 127.0.0.1:4186. Atlas at 4175 was found stopped during this
session; its own Start/Stop Terrain Atlas.cmd successfully starts, stops and
restarts the production atlas/workbench/linkage routes. Both services use this
laptop's installed Python 3.13.12 / Node 22.23.3 and project-local dependencies.
No PC service, boot automation, canonical asset, enforcement or shared robot
runtime change is involved. Canonical robot physics is NOT APPLICABLE;
hardware/contact impact, thermal/strength ratings, GPU and other OS remain
outside this experimental validation.

The development HTTP integration also rejected non-object JSON, unknown actions
and zero reduction with explicit 400 errors. That unshipped integration was
removed after the owner's delivery clarification below.

## Final standalone delivery, 2026-10-14

The owner requested the design report/PDF as an offline static HTML webpage,
without adding the study to Motion Lab tooling. The report and its reproducible
models now live in the sibling `leg-design-study` workspace. Motion Lab's
`server.py` and tracked `web/` source match base `6c74cfd` exactly; only its
Markdown navigation mentions this report. Earlier interactive-study checks
above are development history, not controls delivered on the static page.

Recreated a project-local Python 3.13.12 environment using `requirements.txt`
and `requirements-report.txt`. Actual standalone checks:

- `node --test tests/design-study.test.js`: all 13 tests pass under Node 22.23.3.
- `.venv/Scripts/python.exe -m unittest -v test_generalized_leg`: 12 pass.
- `.venv/Scripts/python.exe scripts/verify_generalized_leg.py`: all nine full
  spring trajectories plus the generalized fixed-A case pass (10 scenarios).
- `.venv/Scripts/python.exe scripts/build_design_report.py`: 16-page, 65,081-byte
  PDF with 22,772 extracted text characters. SHA256
  `1a3c1fd72c739d07d948c612a13f8f5df4bb0508aff436c3190f6150c7ac6d7b`
  matches the independently authored/rendered report byte-for-byte. All 16 pages
  were visually reviewed; corrected figure labels and final provenance pages
  were reviewed again. Data retains selected series and metrics, not raw runs.
- Motion Lab's original build passes after removing the new integration; actual
  app-root CMD stop/restart from an unrelated directory succeeds at 4186.
  The removed report endpoint returns 404. Original health and Atlas workbench
  at 4175 return 200, using this laptop's paths and installed runtimes.

The PDF uses ReportLab 4.4.9, pypdf 6.10.0, Pillow 12.3.0 and charset-normalizer
3.5.2. Numerical pins are NumPy 2.5.3, SciPy 1.18.1, Pymunk 7.3.0, cffi 2.1.1
and pycparser 3.11. HTML/PDF reading needs none of these installed packages.

Independent read-only review found no material mechanics, torque-coordinate or
motion-direction discrepancy between the study, physics record, PDF and retained
evidence. The evidence's `physics.source_sha256` explicitly describes the
original computation sources; `physics.delivery_sha256` records the relocated
module/import adapter and verifier. The numerical model hash still matches the
original evidence exactly, all moved checks pass, and the PDF remains byte-identical.

`node scripts/verify_offline_report.cjs` passes against the delivered local
`file://` page in installed Edge. With JavaScript disabled, all 12 sections and
22 inline SVG figures render; there are no model inputs, frames or external
requests. Six objective rows, 16 Pareto alternatives, nine spring fits and nine
engine checks match the embedded evidence. Embedded JSON equals the retained
file exactly. The 390 px layout has no page overflow; navigation, local PDF
signature/link and print button/CSS pass. Desktop geometry, profile and motion
figures were visually reviewed. A constant drive-torque chart initially used a
tiny display pad with identical rounded axis labels; meaningful display-only
padding fixed the labels without changing its data. Browser captures and the
temporary print check remain outside publication.

The final HTML print layout was also visually reviewed; its browser print export
uses 19 pages, while the separately typeset companion report uses 16. The final
HTML was checked again after print-only spacing changes. All three repository
working-tree entry/require-passed/scoped-gate checks passed for 30 changed paths
in workspace scope; canonical robot physics is explicitly NOT APPLICABLE.
