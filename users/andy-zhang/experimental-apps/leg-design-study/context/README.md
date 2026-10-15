# Design report handoff

Andy Zhang with Codex, 2026-10-14. Source base: `6c74cfd`; publication is the
commit adding this folder. Read [the context index](../context.md).

The initial implementation was checked inside a development Motion Lab study.
The owner then clarified that delivery must be an offline static HTML webpage
and PDF, without adding the study to Motion Lab tooling. The unshipped UI/API
integration was removed; equations, selected evidence, tests and design history
are retained here. Earlier browser/backend checks in validation are development
history, not claims about controls on the static page.

The compact bounded peak-search example is L2=180, L3=340 mm, qab=1.775 and
alpha=4.375 degrees. A 325 mm total capacity with 20 mm at each end gives 285 mm
usable travel. Both link bounds are active; a larger-link search lowers torque
at the cost of size and drift, so this is a conditional compromise, not a global
minimum. Peak and RMS objectives select different designs.

The physical example assumes m1=8.3, m2=m3=.35, m5=.10 and m6=.90 kg (10 kg
per leg), with 11.25 kg sensitivity for a 45 kg robot. The screenshot's zero
moving masses remain an analytical limit. The hip-bellcrank spring fit is
4.3698 N/mm and 213.95 N installed preload; its one-second 285 mm stroke needs
6.449 Nm peak / 3.641 Nm RMS direct hip-input torque, 1.605 rad/s and 6.573 rad/s².
The guide ratio and optional motor gearing are separate power mappings.

All nine spring topologies are generalized and checked against the existing
2D force laws and actual Pymunk stepping. Both movement directions are checked.
Three/four/five-g held-load sensitivities do not predict impact events; spring
packaging, drivetrain inertia, thermal duty, impact stroke and contact sharing
remain unresolved. No damping, hardware, canonical robot or GPU validation is
claimed. Historical dual-rope remains IMPOSSIBLE / rejected.

## Alpha-zero angled-path search, 2026-10-14

New source base `865b5f1`; publication is the commit adding
[inversion-paths.html](../inversion-paths.html). Read the
[decision/math/search record](../docs/inversion-path-study.md),
[selected data](../docs/inversion-path-results.json) and
[actual engine evidence](../docs/inversion-engine-checks.json).
This is the owner's separate overnight report, without Motion Lab integration.

The strict alpha=phi0=0, ratio/near-equal-length search enumerates 26.46 million
windows. Useful angled normal branches exist, but symmetry forces a vertical
fold tangent and opposite tilt after inversion. The equal 350 mm 7:4 example
has 325 mm total/285 usable, 12.02007 degree chord and 9.65874 mm bow; it fails
<=2% bow and its tangents exceed 10–15 degrees. Longer 450 mm tested branches
bow about 6.16 mm, at active size/angle bounds. No full near-equal sweep clears
a coplanar 200 mm wheel; an axial stagger needs measured geometry.

The separately labelled phase relaxation retains alpha=0, uses guide 2:1,
phi0=-25 degrees and equal links for an exact 12.5 degree line. Near-equal
275/250 mm gives 343.099 mm height, 1.544 mm bow and tangents 10.762–12.859 degrees;
minimum hip distance is only 25 mm. Do not silently replace the strict request
with this indexing change or claim a collision-disabled run proves packaging.

Five new numerical tests and 8,784 original-V2/browser scalar comparisons pass.
Five actual constrained Pymunk angular sweeps pass at 1/0.5 ms and converge;
all 2 ms coarse path checks fail the 0.1 mm tolerance and remain recorded.
The earlier height-inverse endpoint-roundoff failure is also retained. No
spring, motor, contact/impact, hardware or canonical robot certification is
added. Preserve historical IMPOSSIBLE dual-rope status and the prior report.

## Force and buffered travel, 2026-10-14

Source base `d1596e5`. Continue from [the force/travel record](../docs/force-travel-study.md)
and [offline report](../force-travel.html). The new owner request ranks force
and useful height; it does not authorize moving this report into Motion Lab.
The strict grid evaluates 11,478,060 windows and separately compares 2%/3% bow;
two local constrained refinements and 11,070 fixed-indexed windows are retained.

Recommended study seed: equal 320 mm links, 9:5 guide, alpha=phi0=0, normal
theta2 110–155.398 degrees, 325 total /285 usable. It gives 1.908 N/Nm worst
vertical force gain and 57.832 Nm static equivalent-load hip peak at the
45 kg four-corner case, without a spring. A fixed phi0=-25 degree indexed
300/300 mm 2:1 alternative is an exact 12.5 degree line and has a wider ROM.
Refined minima touch several constraint bounds; none proves a hardware optimum.

Five new numerical tests plus the prior 17 pass; 10,248 original-V2/Andy 2D
comparisons pass. Three actual full angular Pymunk refinements pass at 1/0.5ms,
while all 2ms path checks fail and remain recorded. Geometry agreement is not
motor-force, impact or collision certification. All full coplanar near-equal
inversions fail clearance; axial/chassis geometry remains unknown. Preserve
prior spring/motor results as separate cases and dual-rope IMPOSSIBLE status.

## Ratio-generated curved paths, 2026-10-14

Continue from [the current curved-path record](../docs/curved-path-study.md) and
[offline report](../curved-paths.html). The owner cancelled the unpublished
fixed15/R² method and confirmed all25/50/75/100 mm lateral-travel comparisons.
Numerical source base93fed9f; publication follows the separate concurrent Motion
Lab work. This contribution does not alter that app or embed the report there.

Keep alpha=phi0=0. The normal325 mm total height includes20 mm reserves at both
ends, leaving 285 mm useful. Equal185r1.9,190r1.8,200r1.7,205r1.6 mm examples
permit24.887/49.981/76.479/101.052 mm lateral excursion. Use190/190mm9:5 as the
balanced geometric seed; the285/285mm,r1.85 branch is the normal220-clearance
comparison. All full near-equal coplanar inversions still fail. Full endpoint
drift is zero by symmetry despite lateral excursion, and Jx vanishes at the fold.

Actual horizontal compliance requires effective spring/controller and geometric
stiffness; blocked vertical movement or wheel contact can prevent the coupled
sideways movement. Do not infer selected springs, motor ratings or no-slip
rolling.16 numerical tests,10,788 originalV2/Andy2D comparisons and three actual
Pymunk geometry sweeps pass. Preserve older numerical reports, live examples,
all historical failures and rejected dual-rope IMPOSSIBLE status.

## Unequal-link owner correction, 2026-10-15

Continue from [the current record](../docs/unequal-inversion-study.md) and
[HTML/GIFs](../unequal-inversion.html). Source aaed324 is the initial broad
unequal report; before shared publication the owner imposed max(length)/min<=1.25
and confirmed upper-long is allowed.160/475 mm is now excluded/superseded.

New compact upper-long set200/170,r2;200/175,r1.875;205/185,r1.75;215/175,r1.7
provides roughly25/50/75/100 mm sideways travel over 325/285 mm height. The
2:1 unequal case is an ellipse, not the equal-link vertical line. Full ideal
q100-260 height inverse passes. All upper-long folds put C inside AB, so
wheel/upper-rod projection overlap needs an axial wheel/link layout; guide
pitch surplus alone is not clearance. Unknown tire/rod width, stack, chassis,
outer pulley and structure remain open; no physical inversion is certified.

The 6.60-million-window search keeps separate upper/lower-long force/size
leaders and no R2 objective. 23 tests,7,440 V2/Andy2D scalar checks and three
positive-mass actual Pymunk sweeps pass at 2/1/0.5/0.25 ms. Engine has no gravity,
forces or collision shapes: geometry only. Read current validation and
revisions, preserve all older reports, spring/motor cases and IMPOSSIBLE status.

## Equal controls and next-sweep brief, 2026-10-15

Continue from [next-sweep-brief.md](../docs/next-sweep-brief.md) and
[the new offline comparison](../design-sweep-brief.html). Current upper-long
recommendations were examples satisfying that orientation request, not proven
force winners. Upper examples have1.1-5.0% higher peaks than similar rounded equal designs,
while saving0-4.9% total link sum but increasing
the longest single link. Keep equal190/190,r1.8 as a50 mm baseline.

The parameterization S=L2+L3,d=(L2-L3)/S separates scale and signed imbalance;
|d|<=1/9 is the exact1.25x limit. At r2, fixed S gives identical vertical
motion/torque/ROM; D=S*d controls lateral motion and fold offset. Original
100-165 screenshot ROM does not give325 mm for the recent short cases; compare
165/170/175 caps explicitly. New proposed ranges and hard versus assumed
constraints are in the brief, with a copyable next-sweep prompt. No new large
grid has been run; thirteen analytical cases and4,838 V2/Andy checks pass.
Earlier Pymunk results remain scoped to their original cases; actual axial
packaging, moving masses, stiffness, impacts and thermal duty remain open.
