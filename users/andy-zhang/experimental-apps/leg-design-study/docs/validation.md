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

## Curved lateral-path report, 2026-10-14

Source model base `93fed9f`; isolated workspace scope. The owner cancelled the
unpublished fixed-line/R² proposal and confirmed 25/50/75/100 mm sideways-travel
comparisons. See [the replacement record](curved-path-study.md). Historical
reports/models and all earlier failures remain intact.

- `curved_path_search.py`: 2,953,002 enumerated windows; 33-pose coarse counts,
  continuous selected extrema and 2001-pose integrals. 29 detailed cases and
  32 compact leaders retained, with objective/ROM/excursion evidence. Final
  search run 14.719 seconds; not a cross-machine performance benchmark.
- `python -m unittest -v test_curved_paths test_force_travel test_inversion_search`:
  **16/16 pass**, including six new derivative/symmetry/flat-baseline/buffer/
  work/compliance-map/extrema/acceptance tests. Original models unchanged.
- Independent read-only Sol 6.1 high audit of all 29 selected cases agrees:
  lateral metrics within 7.11e-14 mm, slope 1.07e-14, useful ROM 1.08e-12 degrees,
  signed/robust side-load peaks 1.43e-14 Nm. All turn/clearance/inverse flags
  match. Source hashes verified; expanded 90/95 degree envelopes consistent.
- `node scripts/verify_curved_report.cjs`: **10,788** original Jonathan V2 /
  Andy 2D scalar comparisons pass, max **2.2737368e-13 mm/Nm**. Installed Edge
  passes JavaScript-disabled local reading, seven sections/six SVG, four
  shortlist rows and exact embedded JSON, finite plots, no external requests
  or page errors, 390 px layout, PDF link/signature and print callback/CSS/export.
- `scripts/verify_curved_geometry.py`: three actual positive-mass Pymunk 7.3.0
  angular fixtures pass at **2/1/0.5 ms** and converge. Fine path errors
  **0.016781..0.018228 mm**. Actual pivots/gears/motor, only initial poses
  assigned; zero gravity/forces and no collision shapes. Geometry evidence
  does not validate compliance, load, contact, impact or packaging. Earlier
  longer-case coarse failures remain documented; thresholds were not relaxed.
- `scripts/build_curved_report.py`: **7 pages, 29,539-byte PDF**, 11,175 extracted
  text characters, SHA256
  `13a4a80c05d96e95c9379c2bffa925bca1818522875ea04ae5e2fbbf2dc4942d`.
  HTML **840,110 bytes**, SHA256
  `756a3f2d3d64a757143234723d97859539c6f31589b81342aa3f4ba668b4ad75`.
  Both regenerate byte-identically. All PDF pages rendered and visually
  reviewed; final changed layouts rechecked. Poppler's nonfatal Symbol
  display-font message remains; no observed missing glyph, overlap or clipping.
  HTML plots and mobile reading reviewed. Raw QA artifacts stay ignored.
- 85 relative links in the affected app/parent documentation pass; finite
  evidence and calculation/engine source hashes match. Manual **Open Curved
  Path Report.cmd** returns exit 0 from an unrelated directory. No server,
  network or installed runtime is needed for viewing.

The first evidence export exceeded the repository's 1 MiB limit; retained
display samples were reduced to 31 per interval, keeping dense calculations
and continuous extrema unchanged, and the complete search was rerun. Compact
leader metrics were then added after review and final evidence regenerated.
Superseded R² work stays only in ignored local artifacts, not publication.
Concurrent Motion Lab edits are preserved and excluded from this contribution.

All compact cases fail normal coplanar 220 mm clearance; larger alternatives
clear only the normal branch. Every full near-equal coplanar inversion fails.
Actual horizontal stiffness requires spring/controller/geometric stiffness
and contact inputs. No spring refit, dynamic/thermal motor rating, physical
inversion, hardware, GPU or other-OS behavior is certified. Canonical physics
is **NOT APPLICABLE**. Unchanged Motion Lab/Atlas lifecycle and complete app
suites were not rerun for this static report; previous setup evidence remains.

## Unequal-link inversion report, 2026-10-14

Source base `1a3fb7e`; workspace scope. See [the design record](unequal-inversion-study.md)
for search bounds, exact geometric proof, assumptions and recommendations.

- `unequal_inversion_search.py`: **11,535,210** windows,24 compact leaders,
 22 detailed cases; continuous final extrema and2001-pose force integrals.
  Final run40.549 s is execution history, not a benchmark. All four calculation
  source hashes match retained provenance. No older model/search code changed.
- `python -m unittest -v test_unequal_inversion test_curved_paths test_force_travel test_inversion_search`:
  **22/22 pass**, including six new unequal-link tests. First run had one test
  harness error: `wide_reverse` accidentally matched the grid-ID prefix. The
  classifier now requires numeric `wNN_`; all22 were rerun unchanged otherwise.
- Independent read-only Sol6.1 high audit verifies all22 cases with original
  trig, bracketed derivative extrema, scalar inversion and SciPy quadrature.
  Max height1.14e-13 mm, ROM1.38e-12 deg, peak1.64e-13 Nm; RMS-J quadrature
  difference5.59e-9 m/rad. All inverse/segment/pitch-circle/guide flags agree.
  Report review corrected holding-magnitude sign wording, explicit3g/4g
  multipliers, torque-RMS versus heating scope and a UTF8/locale encoding issue.
- `node scripts/verify_unequal_report.cjs`: **8,184** original Jonathan V2 /
  Andy2D scalar checks across22 cases pass, max **2.84217094e-13 mm/Nm**.
  Installed Edge passes JS-disabled local reading, six sections/five SVG,
  four shortlist rows/exact embedded JSON, four locally loaded800px GIFs,
  manifest hashes, finite body/figures,390px layout, PDF link/signature and
  print callback/CSS/export. Five requests, all local `file:`; no external
  requests or page errors. Browser QA stays ignored in `artifacts/unequal-report/`.
- `scripts/verify_unequal_geometry.py`: three actual positive-mass Pymunk7.3.0
  fixtures clear25/50/100 pass all **2/1/0.5/0.25 ms** path/pin/guide/tracking
  checks and converge. Finest path errors **0.006819/0.005918/0.008080 mm**.
  Actual pivots/gears/motor generate motion; only initial poses assigned.
  Zero gravity/forces and no collision shapes mean geometry-only evidence,
  not validated force, compliance, physical inversion, contact or impact.
- `scripts/build_unequal_visuals.py`: four800x640,80-frame GIFs,253,143 /
  268,859 /278,077 /280,977 bytes. Actual Pillow frame durations sum6000 ms
  each (alternating70/80 ms), and GIF/source hashes match the manifest.
  Initial96-color per-frame export exceeded1 MiB; shared64-color palette and
  differential frames fixed size without changing geometry. Full fold frames
  for all four, plus the50mm start/fold views, were visually reviewed.
- `scripts/build_unequal_report.py`: **6 pages,24,173-byte PDF**,10,173 extracted
  text characters, SHA256
  `5803cdbc7de1e1e5ac5bb261a2a2a2538be9a5dfce171d2cef81bf72482103f1`.
  HTML **660,300 bytes**, SHA256
  `b95980f5ad0fc7ea842e2e68821fae0f30fd3b3ae0fa58847a7a842d1b137660`.
  Both regenerate byte-identically. All six final PDF pages rendered with
  Poppler and visually reviewed, along with mobile HTML and GIF figures.
  Poppler emits its nonfatal Symbol display-font message; no observed missing
  glyph, overlap or clipping. The manual **Open Unequal Inversion Report.cmd**
  returns exit0 from an unrelated directory. No server/runtime/network is
  needed to read the report; retain the adjacent GIF folder when sharing.

Physical inversion is **unvalidated**: projected rods overlap and the lower
rod crosses the hip atfold. The stronger wheel/guide pitch-circle screen
does not know actual flanges, shafts, chassis, rod thickness or axial stack.
No new spring, motor, loaded dynamics, hardware, GPU or other-OS claim is made.
Canonical robot physics is **NOT APPLICABLE**. Unchanged Motion Lab/Atlas
lifecycles and full app suites were not rerun; previous setup evidence remains.


## Owner 1.25x correction and upper-long report, 2026-10-15

The preceding broad unequal study is historical evidence at revision `aaed324`.
Before shared publication, the owner clarified upper may be longer but
max(length)/min<=1.25. The current HTML/PDF/data/GIFs replace those broad
recommendations; see [the current record](unequal-inversion-study.md).

- `unequal_inversion_search.py`: **6,601,338** enumerated windows,24 compact
  leaders,20 detailed cases, all satisfying max/min<=1.25. L2,L3=150-400 mm
  step5, upper/lower-long force/size families separate, no R2 objective. Final
  run12.409 s; source hashes match. No compact full coplanar wheel-clearance
  pass is claimed; the current quartet is upper-long with axial layout needed.
- Numerical command with test_unequal_inversion/test_curved_paths/
  test_force_travel/test_inversion_search: **23/23 pass**, including seven
  unequal-specific tests and explicit owner-limit/upper-long-fold checks.
- Independent read-only Sol6.1 high audit agrees across all20 cases, source
  hashes and current HTML embedded JSON. Max height1.14e-13 mm, excursion
  2.85e-14 mm, J5.69e-14 mm/rad, segment distance2.45e-14 mm, useful ROM
  1.49e-12 deg, hip peak1.14e-13 Nm; RMS-J quadrature difference6.68e-9 m/rad.
  All inverse/projection/owner-limit flags agree. Prose review tightened the
  speed tradeoff to a given pose; peak speed depends on minimum Jz.
- `node scripts/verify_unequal_report.cjs`: **7,440** originalV2/Andy2D scalar
  comparisons across20 cases pass, maximum **1.70530257e-13 mm/Nm**. Every
  case passes the explicit1.25x assertion; all four recommendations are upper-
  long and have wheel-centre/upper-segment distance0 atfold. Installed Edge
  passes JS-disabled local reading,6 sections/5 SVG/4 rows/exact JSON/4 local
  GIFs,390px layout, print callback/CSS/export and PDF signature/link. All five
  requests are local `file:`; no page error/external request. Current raw QA
  overwrites ignored captures, not curated evidence or prior validation history.
- `scripts/verify_unequal_geometry.py`: actual positive-mass Pymunk7.3.0 motor/
  pivot/gear sweeps upper25/50/100 pass all **2/1/0.5/0.25 ms** path/pin/guide/
  tracking thresholds and converge. Finest path errors **0.010445/0.009186/
  0.008988 mm**. Only initial poses assigned; no gravity/forces/collision
  shapes. This validates geometry, not loaded torque or physical inversion.
- Four new upper25/50/75/100 GIFs are800x640,80 frames, actual6000 ms each;
  sizes260,494/263,682/266,655/267,760 bytes. Source/output hashes match.
  Earlier clearNN GIFs are replaced in the current folder and preserved in
  revisionaaed324. Labels and all four fold frames, plus50mm start, reviewed.
- Current PDF is **6 pages,24,419 bytes**,10,394 extracted text characters,
  SHA256 `1624bf876a7eec7fa56598d5eb86cc2715bced2e22869a6388d3e90a2f211d4f`.
  HTML is **607,635 bytes**, SHA256
  `dc463abc28d452777c7403e5bc59cd7646ddf48ee5c4fc0d62983473688c132b`.
  Both regenerate byte-identically. All six PDF pages rendered/reviewed;
  final force wording/date rechecked, along with mobile HTML/GIF figures.
  Poppler nonfatal Symbol display-font message persists with no observed
  glyph/overlap/clipping defect. The first corrected PDF build rejected raw
  inequality markup; escaping the less-than signs fixed it. A transient builder
  quote syntax error was fixed before any successful report build; no math
  tolerance or model was changed. Manual CMD returns exit0 from an unrelated
  directory and opens the current static report.

All current cases meet the owner length limit, but physical full inversion
is **unvalidated**: wheel centres lie on upper AB atfold, requiring actual
axial wheel/link separation. Guide pitch spacing is not wheel/chassis/outer
hardware clearance. No new motor/spring rating, loaded contact/impact, hardware,
GPU or other-OS certification. Canonical robot physics is NOT APPLICABLE.
Unchanged Motion Lab/Atlas lifecycles/full app suites were not rerun. Prior
historical evidence and IMPOSSIBLE decisions remain intact.


## Equal/unequal comparison and proposed sweep brief, 2026-10-15

Source base14f53f1; workspace-only analytical comparison/planning. See
[next-sweep-brief.md](next-sweep-brief.md) and the separate
[offline brief](../design-sweep-brief.html). All older reports, models and
curated GIFs remain unchanged. No new large sweep is claimed.

- `scripts/compare_link_lengths.py`:13 retained analytical cases: eight
  published examples, three height-feasible fixed-size/guide controls and two
  additional guide-feasible S380,r2 controls.32 retained metric comparisons
  reproduce exactly.501 independent r2 identity samples agree within
  5.68434e-14 mm/rad-unit quantities. The equal195/195,r1.7 control's actual
  capacity324.800 mm is retained as a0.200 mm numerical threshold failure,
  explicitly not a robust practical superiority claim. The185/185,r2 control
  has5 mm pitch surplus and fails the assumed10 mm; the added190/190 vs205/175
  r2 pair meets that screen. Source/helper/input hashes match.
- `node scripts/verify_sweep_brief.cjs`: **4,838** original JonathanV2/Andy2D
  scalar comparisons across13 cases pass, maximum **1.70530257e-13 mm/Nm**.
  Exact r2 peak/ROM equality, full guide-feasible control flags and retained
  failures are checked. Independent read-only Sol6.1 high review agrees with
  the comparisons, S/d parameterization, reciprocal1.25 limit, implied length
  bounds and no-universal-torque-benefit interpretation. The owner explicitly
  confirmed25/50/75/100 mm comparisons; +/-2.5 tolerance remains an assumption.
- Installed Edge verification passes JavaScript-disabled local-file reading,
  four sections/two SVG/four comparison rows/exact embedded JSON, finite
  plots/body,390px layout, PDF link/signature, print callback/CSS/export.
  One local `file:` request, no external requests/page errors. Screenshots
  and browser-print PDF stay ignored under `artifacts/sweep-brief/`.
- `scripts/build_sweep_brief.py`: **4-page,14,322-byte PDF**,8,563 extracted
  text characters; SHA256
  `6d22037eba7071cb156c5c6e88ce4d2fd80904980d25eb5bba71bcdd77e804a3`.
  HTML **357,822 bytes**, SHA256
  `9635dddc880e5db94a0e69d8e781d6169db31b44a413e4f607e40f63e7e7aa06`.
  Both regenerate byte-identically. All pages rendered with Poppler and
  reviewed; final changed requirements/validation pages rechecked, plus
  mobile HTML. Poppler's nonfatal Symbol font message persists with no
  observed glyph, overlap or clipping defect. Manual **Open Sweep Brief.cmd**
  exits0 from an unrelated directory and opens the local static file.

No new Pymunk, loaded spring/motor, contact/impact, physical inversion,
hardware, GPU or other-OS verification is claimed. Original model equations,
services, dependencies and prior validation scope are unchanged. Proposed
ranges, objective choices, ride position, actual ROM and physical inputs need
selection before another large sweep. Canonical physics is NOT APPLICABLE.
