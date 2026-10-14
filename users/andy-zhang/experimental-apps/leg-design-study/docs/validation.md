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

## Alpha-zero path and full-inversion follow-up, 2026-10-14

Source base `865b5f1`; isolated workspace scope. The earlier report/model and
Motion Lab are preserved. This new report is [inversion-paths.html](../inversion-paths.html),
with [design reasoning](inversion-path-study.md),
[search evidence](inversion-path-results.json) and
[actual engine checks](inversion-engine-checks.json).

- Python 3.13.12 `inversion_search.py` enumerated 26,461,800 unique
  geometry/window combinations in 46.279 seconds: 13,230,900 normal and the
  same number of crossing windows. Counts include rejected combinations.
  The 33-pose quality count is coarse; retained selected metrics use 2001 poses.
- `python -m unittest -v test_inversion_search`: **5/5 pass**, including
  direct V2 equations/finite differences, symmetry/fold, exact phase line,
  asymmetric-chord caveat and exact requested capacity without clipping.
- Independent read-only review recomputed all 24 displayed cases at 20,001
  poses, agreeing on endpoints, full-inversion and radius classifications.
  Maximum chord-error sampling difference is 4.4e-6 mm; scalar/vector parity
  discrepancy is <=1.42e-14 in column units. This is analytical evidence.
- `node scripts/verify_inversion_report.cjs`: **8,784 scalar comparisons**
  against this app and original Jonathan V2 pass; maximum discrepancy
  3.979039320256561e-13 mm/Nm. Installed Node 22.23.3 / Edge verifies file://
  reading with JavaScript disabled, 12 sections / 9 inline SVG figures,
  16 candidate rows, exact embedded JSON parity, no external requests or page
  errors, 390 px layout, PDF link/signature and print callback/CSS/export.
  Browser-print export is a check artifact, not the typeset companion PDF.
- `scripts/verify_inversion_geometry.py`: five actual Pymunk 7.3.0 angular
  inversion fixtures pass at **1 ms and 0.5 ms** and converge. The 0.5 ms
  maximum path errors range 0.027675–0.040564 mm. All **2 ms** runs fail the
  unchanged 0.1 mm path threshold (0.111885–0.163992 mm); all refinements,
  configs and source hashes are retained, rather than omitting coarse failures.
  Actual constraints generate motion; poses are assigned only at initialization.
  Gravity/contact/collision shapes are absent, so these are ideal-motion checks.
- The first zero-buffer height-driven attempt failed root-bracketing at a
  floating-point endpoint. The independent angular fixture avoids that height
  inverse; it does not modify the existing solver or weaken tolerances.
- `scripts/build_inversion_report.py`: final **12-page, 40,354-byte PDF**,
  17,300 extracted text characters, SHA256
  `d185e26a91ec43d9bc011d54a855db82b47ace2ab4c14929ec98e7bb8608a604`.
  All 12 pages were rendered with Poppler and visually reviewed; final changed
  pages were reviewed again. Poppler emitted a nonfatal Symbol display-font
  message; completed rendering shows no observed missing glyph or clipping.
  The HTML is 749,707 bytes with SHA256
  `7edfa7527c24b262305e1a878ad415c09fee2fa2aedfe4ac36da794d9e4fbf04`.
  Both outputs regenerate byte-for-byte from the retained evidence.
- `node scripts/verify_offline_report.cjs` still passes the earlier report after
  adding its navigation link: 12 sections / 22 SVG, unchanged embedded evidence,
  JavaScript-disabled local reading, zero external requests and original PDF.
- 85 relative Markdown links pass; search/model/engine hashes match current
  files; retained evidence is finite. The old report's numerical JSON matches
  HEAD exactly. New launcher executes with exit 0 from unrelated C:/Windows.

No canonical robot, hardware, GPU, other-OS, structural, actual ground inversion,
impact/contact or three-dimensional packaging validation is claimed. All strict
near-equal full sweeps fail the projected coplanar 200 mm wheel filter. The
historical dual-rope design stays IMPOSSIBLE / rejected; new spring/motor ratings
are not copied from the earlier geometry. Exact symmetry limits, approximate
branch candidates and explicitly changed assembly phase remain distinct.

## Force and useful-travel report, 2026-10-14

Source base `d1596e5`; workspace scope. All old numerical models, reports,
live Motion Lab examples/GIFs and historical IMPOSSIBLE decisions remain intact.
See [the new design record](force-travel-study.md) for assumptions and limits.

- Python 3.13.12 `force_travel_search.py` evaluates **11,478,060** strict
  geometry/window combinations and **11,070** separate indexed combinations.
  Final run 51.885 seconds; 51-pose quality counts and 2001-pose selected
  acceptance distinguished. Two local SLSQP refinements succeed in 14 iterations
  and pass dense checks. Twenty-one selected accepted or diagnostic/reference
  cases are retained; source hashes match current files, and evidence is finite.
- `python -m unittest -v test_force_travel test_inversion_search test_generalized_leg`:
  **22/22 pass**, including five new independent force/buffer/quadrature/peak/
  power/acceptance tests and the previous seventeen. No model tolerance changed.
- Independent read-only review recomputes all 21 cases: peak J agreement
  7.22e-15 m/rad, RMS J 5.91e-9 m/rad, continuous versus sampled bow at most
  3.81e-6 mm; all acceptance classifications agree. Refined 5% mismatch boundary
  and the 330 mm 7:4 diagnostic's 3.004279% bow failure are confirmed.
- `node scripts/verify_force_report.cjs`: installed Node 22.23.3 /Edge passes
  **10,248** original Jonathan V2/existing Andy 2D scalar comparisons, maximum
  **3.410605e-13 mm/Nm**. Actual file:// reading passes with JavaScript disabled,
  9 sections /7 inline SVG, four shortlist rows and exact embedded JSON.
  No external requests, page errors, nonfinite figure data or 390 px overflow.
  PDF link/signature, print callback/CSS and browser print export also pass.
  Browser captures/print outputs stay ignored; no Motion Lab controls were added.
- `scripts/verify_force_geometry.py`: three new full angular Pymunk 7.3.0
  fixtures pass at **1/0.5 ms** and converge. Positive bodies, actual pivots/
  gears/motor and Space.step; only initial poses assigned. Fine errors
  0.025886–0.033781 mm. **All 2 ms path checks fail** (0.104650–0.136571 mm)
  the unchanged 0.1 mm tolerance and remain in compact evidence. These are
  zero-gravity/contact, collision-shape-free geometry checks, not motor-force
  or physical inversion certification.
- `scripts/build_force_report.py`: final **9-page, 39,966-byte PDF**, 12,734
  extracted text characters, SHA256
  `bdbda4e5ac4533cb2ef47740645a3a6c281eb4667bb20f21305709a826769281`.
  HTML is **769,141 bytes**, SHA256
  `cca70bfbd6529308635e8abf8c82ad2cc12f912ab1192d374fabad0d002971d0`.
  Both regenerate byte-for-byte. All nine PDF pages were rendered with Poppler
  and visually reviewed; final changed layouts/plots reviewed again. Poppler's
  nonfatal Symbol display-font message remains, with no observed missing glyph,
  clipping or overlap. Browser charts and offline/mobile reading reviewed.
- Relative documentation links pass, and the manual **Open Force Travel
  Report.cmd** returns exit 0 from an unrelated directory. Viewing needs no
  server or installed runtime. Motion Lab/Atlas lifecycles and full unchanged
  app suites were not rerun for this static report; previous setup evidence is
  retained. Canonical robot physics is **NOT APPLICABLE**.

The first JSON export rejected a NumPy boolean; explicit scalar conversion
fixed export and the complete search was rerun. Report harness SVG count was
corrected to the seven actual figures; no numerical limit was relaxed.
New 3/4g values are equivalent held-load sensitivities, not simulated impacts.
Full coplanar inversion still fails for every shortlist row; unknown axial/
chassis geometry, strength, actual impact, springs, thermal motor duty, hardware,
GPU and other-OS behavior are not certified.
