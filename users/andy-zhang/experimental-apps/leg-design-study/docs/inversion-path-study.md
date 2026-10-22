# Alpha-zero angled paths and full inversion

Author: Andy Zhang with Codex. Date: 2026-10-14. Source base: `865b5f1`.
Status: conditional experimental kinematic screening, not a hardware selection.
Read the separate [offline report](../inversion-paths.html) or its
[12-page PDF](inversion-path-report.pdf). The earlier [design study](generalized-leg-study.md)
and Motion Lab remain independent and retain their existing results.

## Decision

Changing the guide ratio and equal or nearly equal link lengths can create an
approximately straight, angled **normal suspension branch** at zero mounting
angle. It cannot create the same exact 10–15 degree line through the fold when
the original assembly phase is also zero. The folded tangent is vertical and
the inverted branch mirrors the normal branch's tilt.

A useful simple-ratio example is **L2=L3=350 mm, ra/rb=105/60=7:4**,
alpha=phi0=0. Its theta2 window is 115–155.512438 degrees. It gives 325 mm total
vertical capacity, 285 mm usable after 20 mm reserves at each end, a 12.020066
degree endpoint-chord tilt, and 9.658736 mm maximum orthogonal bow. Local
tangents vary 6.26968–20.47412 degrees. This is a conditional compromise if
roughly 10 mm bow is acceptable; it **fails** the illustrative 2% straightness
preference and does not keep every tangent inside 10–15 degrees.

The ideal guide can continue into the inverted branch with a finite positive
vertical Jacobian. A coplanar 200 mm-radius wheel cannot pass the hip in this
near-equal-link layout. Axially separated wheels and links might avoid that
projected collision, but axial offsets and chassis geometry are unknown. Do
not call an ideal guide sweep a physically demonstrated inversion.

## Request, inherited parameters and assumptions

The owner requested a broad search from the original screenshot for 10–15
degree offset paths, alpha=0, different pulley ratios, equal or slightly
unequal links, and full inversion. The owner was unavailable after this request;
no response was assumed to approve a changed architecture.

- Offset is measured from **global vertical**, consistent with the earlier
  suspension-path discussion. It is not the lower-link angle above horizontal.
- The strict search retains **phi0=0** as in the explicitly assumed screenshot
  baseline. Assembly/belt indexing is shown separately as a relaxation.
- Full ideal inversion means theta2=100–260 degrees, with continuous normal-to-
  inverted motion, both signs of wheel-centre height, and a positive vertical
  Jacobian. This extends the old normal-only profile range without changing
  its validator or saved profiles.
- Normal capacity is 300/325/350 mm **including all buffers**; 20 mm at each end
  leaves 260/285/310 mm usable. The preferred usable target remains roughly
  250 mm and the minimum remains 200 mm. These geometric reserves are not
  impact-compression or spring-stroke allocations.
- Separate 300/325/350 mm windows crossing hip height allocate 20/35/50/65/80%
  of height above the hip. Their total is distinct from the much larger full
  inversion envelope; the 350 mm example's full envelope spans about 1296 mm.
- Screenshot baseline: L2=L3=250 mm, ra=100/rb=60 mm, guide 5:3;
  rc=rd=re=rf=35 mm, qcd=qef=1, rw=200 mm; alpha=0, beta=13.5 degrees;
  theta2=100–165 degrees, captured theta2=100.135 degrees; Fy=Fz=100 N;
  m1=10 kg at fixed A, other masses zero; g=9.81 m/s2, r5I=35 mm.
  The phase and unseen belt preloads are explicitly zero assumptions.
- Beta sets contact/load orientation; it does not tilt the wheel-centre locus.
  The wheel-drive ratios do not alter this locus either. Only guide qab,
  link lengths, mounting alpha and assembly phase enter its geometry.
- A 20 mm projected rim/hip gap is an illustrative packaging assumption:
  wheel-centre distance must be at least 220 mm. It is a conservative planar
  filter, not a complete three-dimensional interference calculation.

## Exact geometry and the obstruction

Retain Jonathan's variables, +y right and +z up. Let q=theta2 in radians,
a=L2, b=L3, r=qab=ra/rb, t=q-pi, and k=r-1. At alpha=phi0=0:

```text
x = a cos(t) - b cos(k t)
z = a sin(t) + b sin(k t)
dx/dq = -a sin(t) + k b sin(k t)
dz/dq =  a cos(t) + k b cos(k t)
```

The horizontal coordinate is even about q=pi and height is odd. Hence any
symmetric full inversion has zero lateral endpoint displacement and a vertical
chord. At the fold, C=(a-b,0) and C'=(0,a+k b). Its tangent is vertical, with
finite positive speed for the searched positive links and r>1. Equal links
put the wheel centre at the hip; this is a collision concern, **not** a
zero-Jacobian kinematic singularity.

An exact straight tilted segment would, by analytic continuation of these
trigonometric equations, also have to accommodate this vertical tangent.
In the searched positive-ratio domain the only nondegenerate exact straight
path is r=2, a=b, which is vertical. Different angular frequencies introduce
curvature; unequal links at r=2 produce a thin ellipse rather than a line.

Near the fold:

```text
x = (a-b) + (b k^2-a)t^2/2 + O(t^4)
z = (a+b k)t - (a+b k^3)t^3/6 + O(t^5)
```

Setting r=1+sqrt(a/b) cancels the leading lateral curvature, making a locally
straighter **vertical** transition. It cannot generate the requested nonzero
central tilt. An asymmetric crossing window can have a tilted endpoint chord
while retaining a vertical tangent and substantial internal bow.

The distance identity is:

```text
|C|^2 = a^2 + b^2 - 2ab cos(r t)
```

Every phase-zero full sweep includes |C(pi)|=|a-b|. With |L2/L3-1|<=15% and
L3<=450 mm this distance is at most 67.5 mm, below the 220 mm projected
exclusion. Therefore all near-equal designs in this domain fail coplanar full
inversion clearance, regardless of how attractive the normal branch looks.
An axial stagger changes the collision geometry and needs a separate model.

## Search and ranking

[inversion_search.py](../inversion_search.py) enumerates **26,461,800 distinct
geometry/window combinations**, half normal windows and half crossing windows:
482 guides x 61 link ratios x 30 lower-link scales x 15 windows per family.
Counts include rejected capacity/geometry combinations; they are not a count
of buildable hardware designs.

| Variable | Exact domain |
| --- | --- |
| L3 | 200–450 mm at 10 mm spacing, plus 275/325/375/425 mm |
| L2/L3 | 0.85–1.15 at 0.005 spacing |
| Guide ra/rb | 1.4–2.6 at 0.0025 spacing plus exact 5/3; rb=60 mm |
| Normal start | theta2=100/105/110/115/120 degrees |
| Normal endpoint | Solved for exact target height, no later than 175 degrees |
| Total capacity | 300/325/350 mm |
| Crossing windows | Each total at 20/35/50/65/80% above-hip allocation |
| Strict alpha / phi0 | 0 / 0 degrees |

Floating grid coordinates are rounded before deduplication. Initial capacity
and circle-separation filters are vectorized; guide circles require
L2>ra+rb, but real belt wrap, tooth counts, bearings and link sections are not
selected. Positive vertical Jacobian is required; the normal leaders also
check the full inversion envelope and normal-branch distance>=220 mm.

Endpoints use 28-step coarse height bisection, followed by precise scalar root
solving for finalists. The coarse screen evaluates 33 poses; bucket leaders
retain 32 entries, of which the first 16 receive 2001-pose dense checks. The
retained 61-point branch and 81-point full curves are for display; headline
metrics use the denser calculations. An independent review used 20,001 poses.
This is a bounded deterministic search, not a certificate of global optimality.

A candidate must have a 10–15 degree absolute endpoint-chord tilt. Rank maximum
orthogonal deviation from that chord first, tangent span second, link sum third.
Equal, within 5%, within 10%, within 15%, capacity and scale buckets expose the
tradeoffs. A separate illustrative quality threshold is <=2% chord bow and
<=15 degree tangent span; it is not an accepted team requirement.

| Coarse outcome | Count |
| --- | ---: |
| Normal combinations | 13,230,900 |
| Crossing combinations | 13,230,900 |
| Normal requested-angle candidates | 2,011,471 |
| Normal angle, geometry and clearance passes | 870,568 |
| Normal passes also meeting illustrative quality | 8,080 |
| Crossing requested-angle candidates | 50,990 |
| Crossing candidates meeting both quality limits | 0 |
| Full projected coplanar inversion clearance passes | 0 |

The 8,080 quality count is **coarse**, not a dense certification of every pass.
For example, the selected equal-link 350 mm-capacity boundary case has 2.000592%
dense bow, just outside 2%; its classification is not silently rounded to pass.
The exact symmetry proof is stronger than a grid failure for an exact tilted
line. The approximate crossing-window result remains bounded to this search.

## Selected designs

All strict rows have alpha=phi0=0. Bow is maximum orthogonal chord error.
Margins below are normal-branch wheel-centre distance minus 200 mm radius;
they must reach 20 mm to pass the illustrative filter.

| L2/L3 mm | Guide | Total mm | Chord tilt deg | Bow mm | Tangent span deg | Rim/hip margin mm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 450/450 | 1.7925 | 325 | 10.0685 | 6.1624 | 8.9126 | 197.31 |
| 459/450 | 1.8050 | 325 | 10.0009 | 6.0969 | 8.8318 | 208.69 |
| 350/350 | 1.7675 | 325 | 10.0770 | 8.0443 | 11.7348 | 30.31 |
| 350/350 | 1.7500 (7:4) | 325 | 12.0201 | 9.6587 | 14.2044 | 55.72 |
| 400/400 | 1.7500 (7:4) | 325 | 12.7472 | 8.9807 | 13.0709 | 138.92 |
| 322.5/375 | 1.7375 | 325 | 10.0278 | 7.7304 | 11.6006 | 79.70 |
| 300/300 | 1.8175 | 325 | 10.0215 | 9.8250 | 16.2990 | 28.13 |

Read [retained selected evidence](inversion-path-results.json) for exact windows,
all 16 selected rows, three simple-ratio cases and five diagnostic
examples. The original_scale_325 row is diagnostic, with a negative normal
wheel/hip margin and a non-monotone full envelope; it is not an acceptable
fully invertible branch candidate. Crossing rows likewise fail the requested
straightness and clearance filters. The report shows individual path/tangent curves and a guide sweep.
The 450 mm winners lie at the upper size bound and near the lower tilt bound:
lower bow is purchased with size. A slight mismatch changes the best result
only modestly; it does not solve full inversion clearance.

The 350/350 mm, 7:4 branch is the recommended **example**, not a selected robot
part. It retains equal links and a simple ideal ratio, with moderate normal
branch clearance. If <=2% bow is essential, the larger 450 mm examples are more
appropriate starting points. If every tangent must stay inside 10–15 degrees,
none of these summary chord angles should be mistaken for that stronger claim.

The best 325 mm crossing examples in the retained equal/near-equal buckets have
about 23.94/23.92 mm bow, roughly 7.25% of chord, and about 33.6/33.5 degrees
of tangent variation. Their endpoint chord tilts reach the target, but their
internal paths do not meet the straightness criteria.

## Explicit alternative: assembly indexing, alpha still zero

If lower-link belt/assembly indexing may change, keep r=2 and a=b=L but allow
phi0. The exact wheel-centre locus is:

```text
d = phi0/2
C = 2L sin(t-d) [-sin(d), cos(d)]
```

Phi0=-20 to -30 degrees gives an exact 10–15 degree line with alpha=0.
This is a deliberate relaxation of the request for the angle to arise only
from ratio and link length. It indexes the lower link; mounting alpha rotates
both links and their frame, so the knee trajectory differs even if the
wheel-centre line happens to coincide.

- 250/250 mm, r=2, phi0=-25 degrees, theta2=160–200 degrees:
  325.998 mm vertical height, 12.5 degree exact line, zero ideal bow.
- 275/250 mm, r=2, phi0=-25 degrees, theta2=160–200 degrees:
  343.098838 mm vertical height, 11.895157 degree chord,
  1.544204 mm bow, local tangents 10.762369–12.859192 degrees.

Both pass continuously through hip height, but their minimum wheel-centre/hip
distances are 0 and 25 mm. Phase improves straightness, **not** coplanar wheel
clearance. These are alternatives for explicit indexing and unresolved axial
packaging, not covert changes to the strict search.

## Torque, dynamics and verification boundaries

The signed torque curves use the inherited fixed-A Fy=Fz=100 N algebraic load,
zero moving masses, no spring, and Jonathan's convention. They do not reuse
the earlier 10 kg supported-chassis motor result. Relative-knee angle has
derivative -qab, so tau_knee=-tau_hip/qab; speed is multiplied by -qab.
Any additional motor reduction is separate. Lower torque in another coordinate
is accompanied by greater speed and does not create ideal energy savings.

Actual new checks:

- Five numerical tests cover the original equations, finite-difference
  derivatives, parity/fold identities, phase lines, symmetric/asymmetric
  inversion and exact capacity without endpoint clipping.
- The delivered Node browser verifier compares this app and original Jonathan
  V2 at all 61 retained poses in 24 cases: **8,784 comparisons**, maximum
  discrepancy **3.9790393e-13** mm/Nm.
- Independent read-only review recomputed 24 cases at 20,001 poses. Endpoint,
  full-inversion and radius classifications agree; dense bow sampling differs
  by at most 4.4e-6 mm. This is an independent analytical review, not hardware.
- Actual Pymunk stepping checks five full inversion fixtures with positive
  masses, real pivots/gears/motor and a two-second quintic angular trajectory.
  Only initial poses are assigned. Positions are compared against independent
  V2 geometry at the **actual** upper-link angle, with pin, guide and tracking
  errors retained. The fixture has gravity/contact zero and no collision shapes.
- All five 2 ms path errors exceed the unchanged 0.1 mm tolerance (0.112–0.164 mm).
  All 1 ms and 0.5 ms runs pass and converge; finest errors are 0.028–0.041 mm.
  [Engine evidence](inversion-engine-checks.json) preserves all refinements,
  resolved configs, model/verifier hashes and version information.
- A first zero-buffer height-driven engine attempt hit endpoint root-bracketing
  roundoff. The independent angular fixture avoids that inverse-height
  dependency; the original height solver and tolerances were not changed.

No new spring constants or motor ratings are transferred to these geometries.
The earlier [spring/physics study](generalized-leg-physics.md) remains its own
fixture. Spring routing through inversion, gravity/contact loads, impact,
strength, belt tension, axial interference, tooth counts and actual inversion
control need separate work. No canonical robot, GPU or hardware check is claimed.
The historical dual-rope design remains **IMPOSSIBLE / rejected**.

## Reproduction and continuation

From this app folder, using the already pinned Python 3.13 environment and
Node.js 22:

```sh
.venv/Scripts/python.exe inversion_search.py --output docs/inversion-path-results.json
.venv/Scripts/python.exe -m unittest -v test_inversion_search
.venv/Scripts/python.exe scripts/verify_inversion_geometry.py
.venv/Scripts/python.exe scripts/build_inversion_report.py
node scripts/verify_inversion_report.cjs
```

On other operating systems use `.venv/bin/python`; not tested here. Viewing the
HTML/PDF needs no runtime or server. Use [Open Inversion Report.cmd](../Open%20Inversion%20Report.cmd)
on Windows. Search timing is informational; selected geometry and metrics are
deterministic, while the retained elapsed-time field may vary on reproduction.

Sources: Jonathan's [V1](../../../../jonathan-xie/experimental-apps/vsl-solver/v1/v1-kinematics.html),
[V2](../../../../jonathan-xie/experimental-apps/vsl-solver/v2/v2-quasi-static.html),
[V2 model record](../../../../jonathan-xie/experimental-apps/vsl-solver/v2/v2-model.md),
this app's [model](../model.js), [physical model](../generalized_leg.py),
[search](../inversion_search.py), and [actual-engine verifier](../scripts/verify_inversion_geometry.py).
The [revision map](revisions.md) and [validation record](validation.md) retain
continuation context; find the publication commit with the app's Git history.

Next choose explicitly between approximate mirrored working branches, a
lower-link indexing relaxation, or a changed architecture. Measure axial
wheel/chassis separation and the desired normal/inverted joint limits before
claiming physical inversion. Keep this report separate from Motion Lab tooling.
