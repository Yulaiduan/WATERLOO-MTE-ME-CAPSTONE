# Unequal-link curved paths through inversion

Andy Zhang with Codex, 2026-10-14. Status: experimental analytical screening,
not an approved mechanical design. Source base `1a3fb7e`; publication is the
commit adding `unequal-inversion.html`. No Motion Lab source is changed.

Read the [offline HTML](../unequal-inversion.html), [six-page PDF](unequal-inversion-report.pdf),
[selected results](unequal-inversion-results.json), [original-model parity](unequal-inversion-math-checks.json),
[actual engine checks](unequal-inversion-engine-checks.json) and
[four GIFs/manifest](unequal-animations/README.md). Keep the HTML and adjacent
`docs/unequal-animations/` directory together when sharing offline.

## Decision and assumptions

The owner asked for good unequal-length invertible paths, following the curved
path study. Broaden the link mismatch beyond its earlier equal/within 5% tiers.
Keep the original Jonathan variable/convention model: upper L2, lower L3,
guide `r=ra/rb`, alpha=0 and original assembly phase phi0=0. No fixed 15-degree
line, R² score or new mounting/index angle is used. Wheel radius stays 200 mm.

The requested approximately 325 mm total vertical travel includes buffers.
The owner did not specify their split; retain the explicitly assumed 20 mm at
each end, leaving 285 mm useful. Full inversion means the ideal height map is
one-to-one on q=100–260 degrees and crosses q180; normal operation is a 325 mm
window below the fold, ending at or before175 degrees. These angular limits
are study assumptions, not measured stops. The full envelope has substantially
more than 325 mm height. It is not a ground-flip trajectory.

| Label | Upper /lower mm | Guide r | Normal sideways mm | Useful hip ROM deg | Peak /height-RMS hip Nm | Minimum wheel–hip pitch gap mm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clear25 | 175 /495 | 1.50 | +24.902 | 49.401 | 44.047 /37.520 | 30.0 |
| clear50 | 160 /475 | 1.42 | +50.165 | 55.806 | 38.552 /33.173 | 29.8 |
| clear75 | 160 /480 | 1.35 | +74.451 | 60.157 | 35.633 /30.798 | 39.0 |
| clear100 | 175 /485 | 1.30 | +101.407 | 61.822 | 34.947 /30.081 | 32.0 |

All four have 325/285 mm total/useful normal height. Start with **160/475 mm,
r1.42** for approximately50 mm sideways travel. The 160/480 mm,r1.35 option
trades more sideways movement for lower vertical-load torque. Neither is a
global optimum or physically certified inversion. Rounded comparisons retain
more pitch-circle allowance than several grid minima; manufacturing feasibility
still needs tooth counts, belt pitch, flange dimensions, strength and CAD.

Torque uses a pure vertical equivalent corner load 110.3625 N (45 kg x9.81/4),
massless moving links, no spring or inertia. This is a consistent comparison
case, not a motor rating. The screenshot's mixed Fy/Fz 100 N initial condition
remains in the original report; the force comparison deliberately isolates
vertical load and separately retains |Fx/Fz|<=0.3 sensitivity.

## Exact geometry and the important clearance distinction

With `a=L2`, `b=L3`, `t=q-pi`, `k=r-1`, angles in radians and lengths in mm:

```text
B = (a cos(t), a sin(t))
C = (a cos(t)-b cos(k t), a sin(t)+b sin(k t))
Jx = -a sin(t)+k b sin(k t)
Jz =  a cos(t)+k b cos(k t)
|C|² = a²+b²-2ab cos(r t)
```

Therefore the minimum hip-to-wheel-centre distance over an interval containing
the fold is `|a-b|`. Equal/near-equal links necessarily bring the wheel close
to the hip. A sufficiently longer lower link keeps it away. For b>=a, wheel
centre distance to the **thin upper segment AB** is at least b-a, equality at
fold. To verify rather than infer this from hip distance alone, project C on
the unit vector along AB: `p=a-b cos(rt)`. Closest-segment distance is `|C|`
when p<=0, `b |sin(rt)|` when 0<p<a, and b when p>=a. Each is >=b-a.

This argument fails for an upper-long design. At the fold with a>b, C=a-b is
**inside AB**. For 400/175 mm,r1.5, the hip distance 225 mm appears acceptable
for a point exclusion, but the wheel centre lies on the upper rod. Its
wheel-rim/thin-upper-segment gap is -200 mm. This rejected diagnostic is retained.

Three screening levels stay explicit:

1. **Ideal height inverse:** continuously positive Jz>=5 mm/rad across full
   q100–260, with derivative extrema checked, not just sampled positive signs.
2. **Wheel/point and thin-upper-segment projection:** b-a>=220 mm, assuming
   R200 plus20 mm reserve. The 150/375 mm,r1.45 diagnostic passes this but has
   only 3 mm guide pitch-centre surplus and overlaps the hip pitch circle.
3. **Stronger wheel/guide pitch-circle projection:** with rb 60 mm and ra=60r,
   require b-a>=220+60r and b>=280. Separately require
   `a-60(r+1)>=10 mm` assumed guide pitch-centre surplus. All four rounded
   recommendations pass these assumed screens throughout the envelope.

These are pitch radii, **not outer/flange/shaft/chassis dimensions**. At the fold
for b>a, C is opposite B across A and lower segment BC contains the entire
upper segment AB. The lower rod passes through the hip in side view. An axial
stagger, fork or offset is still necessary even when wheel/guide pitch circles
clear. Actual rod width, tire shape/deformation, axial stack, housings, belts,
chassis and tolerances are unknown. Thus **physical full inversion is
unvalidated for every row**; collision-disabled Pymunk cannot certify it.

Symmetry remains `x(-t)=x(t), z(-t)=-z(t)`. Full endpoint lateral drift is zero,
but lateral excursion is nonzero. Jx=0 at the fold and Jz=a+(r-1)b>0. The local
inversion tangent is vertical, despite curved normal motion. All recommended
normal paths are monotone sideways without a reversal.

## Search priorities and control range

The reproducible grid enumerates **11,535,210** geometry/window combinations:

- L2=130–350 mm and L3=150–650 mm, both step 5; |L2-L3|>=10 mm.
- r1.2–2.6 step 0.005 plus exact 5/3; rb 60 mm; alpha=phi0=0.
- Normal q start100–140 step 5 degrees; solve end height exactly 325 mm,
  reject end>175; full inverse domain100–260.
- Normal lateral excursion25/50/75/100 +/-2.5 mm, either direction, with no
  sideways reversal. No R²/straightness objective is used.
- Hard height/inverse/guide checks precede ranking. Keep geometry-only,
  thin-segment220 and hip-pitch-circle families separate. Minimize useful
  peak Jz and total link sum **separately**, with no blended weighted score.
- 33 coarse poses retain 8 candidates per bucket; 146 finalists receive exact
  selected extrema checks and 2001-pose integrals. 24 compact leaders and 22
  detailed cases retain recommendations, minima and rejected diagnostics.

Coarse counts before applying the lateral bands are 4,548,341 height/guide/
inverse passes, 4,372,300 unequal/monotone, 1,754,372 point/segment candidates,
701,674 hip-pitch candidates. They are not numbers of target-band winners or
manufacturable robots. Finite bounds, steps and candidate pool retention do
not establish a global optimum. Final recorded runtime 40.549 s is local
execution history, not a cross-machine benchmark.

For example, the 50 mm pitch-circle force leader 155/460 mm,r1.385 has 36.432 Nm
peak and 21.9 mm hip pitch gap. Rounded 160/475,r1.42 increases peak to 38.552 Nm
while increasing that gap to 29.8 mm. In the 100 mm family, the size leader
170/470,r1.29 has 33.562 Nm and 22.6 mm gap; force leader 160/615,r1.23 has 33.046 Nm
but a 775 mm link sum. That small torque gain is not enough by itself to select
the much longer lower link. The displayed rounded 175/485,r1.3 offers 32 mm
pitch gap with 34.947 Nm peak.

Effective useful ROM is height-based:
`qlow=z^-1(zstart+20)` and `qhigh=z^-1(zend-20)`.
For 160/475,r1.42, total q100–164.692103, useful ROM 55.806183 degrees. Do not
subtract 20 degrees because the buffer is 20 mm, or assume the full inversion
ROM is the normal useful control window. JSON retains all exact bounds.

## Force, speed and compliance interpretation

Using J in metres/radian, virtual work gives
`tau_hip=Fx Jx+Fz Jz` up to applied/holding sign convention. The report shows
positive holding magnitude for upward load. Peak useful Jz sets worst vertical
force per hip Nm; lower torque needs greater joint speed for the same vertical
speed. The charts show every profile, height-weighted RMS, speed at constant
vertical 0.25 m/s and a robust both-sign |Fx/Fz|<=0.3 load envelope.

Relative-knee torque is `-tau_hip/r`; knee speed is `-r times hip speed`, so
power is preserved. The half-torque relation applies only to guide 2:1.
Optional motor reduction and wheel-drive coupling are separate mappings.
Ideal useful lift work is always 110.3625  x0.285=31.4533125 J. Lower peak or
average torque is mechanical advantage, not energy efficiency. Height-RMS is
a thermal proxy only under constant vertical speed; actual duty needs time-
weighted current/torque, losses, speed and inertia. Held 3/4g load scaling does
not predict impact force, required suspension stroke or acceleration.

Curved motion permits coupled horizontal/vertical travel, not independent
horizontal compliance. For a stable effective stiffness, local
`C=J J^T/K_eff` has rank one; controller/spring/geometric stiffness, contact,
tire behavior and rolling/scrub conditions are still required. Jx vanishes at
the fold. No new spring constant or motor rating is transferred from older
geometries. Historical dual-rope remains **IMPOSSIBLE /rejected**.

## Reproduction and evidence

From this app with the existing Python 3.13/Node 22 environment:

```sh
.venv/Scripts/python.exe unequal_inversion_search.py --output docs/unequal-inversion-results.json
.venv/Scripts/python.exe -m unittest -v test_unequal_inversion test_curved_paths test_force_travel test_inversion_search
.venv/Scripts/python.exe scripts/verify_unequal_geometry.py
node scripts/verify_unequal_report.cjs --math-only
.venv/Scripts/python.exe scripts/build_unequal_visuals.py
.venv/Scripts/python.exe scripts/build_unequal_report.py
node scripts/verify_unequal_report.cjs
```

Report rendering consumes retained evidence and does not silently rerun the
search. The grid time field is run-specific; the HTML/PDF from fixed evidence
regenerate byte-identically. GIF font fallback can change rendering on another
OS. Read [validation](validation.md) for actual commands and limitations.

- 22 tests pass, including 6 new unequal-specific tests. Initial test harness
  treated diagnostic `wide_reverse` as a `wNN_` grid ID; classifier fixed and
  all 22 rerun, without changing numerical criteria.
- 8,184 scalar checks across 22 cases agree with original Jonathan V2 geometry/
  statics and Andy2D statics, maximum 2.84217e-13 mm/Nm. Source hashes match.
- Independent read-only Sol 6.1 high audit checks all 22 cases with original
  trigonometry, bracketed derivative extrema, scalar inverse and independent
  SciPy quadrature. Max ROM error 1.38e-12 deg, peak 1.64e-13 Nm, RMS-J
  quadrature difference 5.59e-9 m/rad. All acceptance/clearance flags agree.
- Three actual positive-mass Pymunk fixtures (clear25/50/100) pass unchanged
  path/pin 0.1 mm, guide 1e-4 rad and tracking 0.01 rad limits at 2/1/0.5/0.25 ms,
  with path error converging to 0.006819/0.005918/0.008080 mm. Actual constraints
  generate motion; only initial poses assigned. Forces/gravity zero and no
  collision shapes: geometry validation only, not load/contact/inversion proof.

The first GIF export exceeded 1 MiB; a shared 64-color palette and differential
frames reduced each to about 0.25–0.28 MB. GIF timing uses alternating 70/80 ms
delays for an exact 6 s loop. No source data or geometry was reduced for size.
No server/lifecycle, hardware, GPU, thermal duty or other-OS verification is
claimed. Canonical robot physics is NOT APPLICABLE for this member workspace.
