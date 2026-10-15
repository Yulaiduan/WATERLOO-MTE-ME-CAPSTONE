# Upper-long invertible paths within 1.25x

Andy Zhang with Codex, 2026-10-15. Experimental analytical screening; not an
approved mechanical design. Source base `aaed324` is the initial broad unequal
study. The owner then clarified that either link may be longer but the longer
must be at most 1.25 times the shorter. This record and the current report
**supersede the 160/475 mm recommendation**, which violates that constraint.
Historical broad-search results/GIFs remain in Git revision `aaed324` and its
contribution entry; they are not current recommendations.

Read the [offline HTML](../unequal-inversion.html), [six-page PDF](unequal-inversion-report.pdf),
[selected results](unequal-inversion-results.json), [original-model parity](unequal-inversion-math-checks.json),
[actual engine checks](unequal-inversion-engine-checks.json) and
[four GIFs/manifest](unequal-animations/README.md). Keep the HTML and adjacent
GIF folder together when sharing offline. No Motion Lab controls/models change.

## Owner constraints and recommendation

Keep alpha=0, original phase phi0=0, R200 mm and 325 mm total normal vertical
travel including buffers. Retain the explicitly assumed 20 mm at each end,
leaving 285 mm useful. The owner permits upper L2 longer than lower L3, with
`max(L2,L3)/min(L2,L3)<=1.25`. Do not confuse this **link-length ratio** with
the separate guide pulley ratio `r=ra/rb`. Cancelled R2/fixed-line ranking stays
cancelled; compare curved paths with 25/50/75/100 mm sideways excursions.

| Example | Upper /lower mm | Length ratio | Guide | Sideways mm | Useful hip ROM deg | Peak /height-RMS hip Nm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| upper25 | 200 /170 | 1.1765 | 2:1 | 24.620 | 59.318 | 40.305 /32.994 |
| upper50 | 200 /175 | 1.1429 | 15:8 | 49.772 | 60.829 | 38.523 /31.816 |
| upper75 | 205 /185 | 1.1081 | 7:4 | 76.313 | 61.460 | 37.504 /31.199 |
| upper100 | 215 /175 | 1.2286 | 17:10 | 99.949 | 62.199 | 36.888 /30.780 |

All have 325/285 mm total/useful height and monotonically increasing normal
horizontal movement. All retain continuously positive Jz across full q100-260
degrees, hence a unique height inverse through 180 degrees. They are ideal
inversions, not physically collision-free mechanisms or ground-flip trajectories.
Start CAD with **200/175 mm, guide 15:8** for approximately 50 mm horizontal
movement; compare 205/185 mm,7:4 if 75 mm is useful. Rounded guide ratios have
readable rational relations and remain unselected belt tooth/pitch hardware.

The force comparison uses 110.3625 N vertical equivalent corner load
(45 kg x9.81/4), massless moving links, no spring/inertia. This deliberately
isolates vertical load rather than silently carrying the screenshot's mixed
Fy=Fz 100 N. Side-load sensitivity is retained separately. These values are
neither motor ratings nor loaded physical-engine validation.

## Geometry and inversion

With a=L2,b=L3,t=q-pi,k=r-1; angles in radians, lengths in mm:

```text
B = (a cos(t), a sin(t))
C = (a cos(t)-b cos(k t), a sin(t)+b sin(k t))
Jx = -a sin(t)+k b sin(k t)
Jz =  a cos(t)+k b cos(k t)
|C|^2 = a^2+b^2-2ab cos(r t)
```

With r2, unequal links give **an ellipse**:
`x=(a-b)cos(t), z=(a+b)sin(t)`. The 2:1 guide becomes a straight vertical line
only when a=b. Thus 200/170 mm can give about 25 mm sideways travel without any
alpha or assembly indexing. Other ratios reshape the curve independently of
link mismatch. Full symmetry remains x(-t)=x(t), z(-t)=-z(t); full endpoint
sideways drift is zero despite nonzero excursion. Fold tangent is vertical.

At the fold q180, C=(a-b,0), B=(a,0). If a>b, `0<a-b<a`: C lies **inside the upper
segment AB**. Wheel-centre-to-upper-segment distance is zero, so the R200 wheel
has projected overlap with the upper rod at any absolute scale. Lower BC also
overlaps a portion of upper AB. An upper-long coplanar full inversion cannot
clear this wheel/rod overlap; passing a height inverse is not physical clearance.

For lower-long b>=a, distance to thin upper AB is at least b-a, equality
at the fold. Projection onto AB gives p=a-b cos(rt), with closest distance |C| if
p<=0, b|sin(rt)| if 0<p<a, and b if p>=a. Hip-centre distance minimum is |a-b|.
Under the 1.25 length bound, b-a<=0.25a. Just a 220 mm point/segment screen
(R200+20 assumed gap) needs a>=880,b>=1100 mm. With rb60 and ra60r, the stronger
wheel/hip pitch-circle condition is b-a>=220+60r; the required lengths grow
further. Neither compact upper-long nor lower-long search cases pass full
coplanar wheel clearance. This does not prove all scales of lower-long legs
impossible; it explains why compact near-equal designs need axial packaging.

Each recommended design passes the separately assumed 10 mm guide pitch-centre
surplus `a-60(r+1)`: 20/27.5/40/53 mm respectively. That does not certify outer
flange, shaft, belt, wheel or chassis clearance. Proposed next design work is
an explicit axial wheel/link stack, fork or offset with actual tire width,
rod thickness, housings, bearings and tolerances. No axial distance is invented.
Physical full inversion remains **unvalidated** for every retained case.

## Search and weighting

The new grid enumerates **6,601,338** geometry/window combinations:

- L2,L3=150-400 mm, step 5 mm; |L2-L3|>=5 mm and max/min<=1.25.
- Guide r1.2-2.6,step 0.005 plus exact 5/3; rb60 mm; alpha=phase=0.
- Normal start 100-140,step 5 degrees; end solves 325 mm height, <=175.
- Full inverse q100-260, Jz>=5 mm/rad; assumed guide pitch surplus>=10 mm.
- Normal lateral excursion 25/50/75/100 +/-2.5 mm, no sideways reversal.
- Hard constraints first. Upper-long/lower-long families stay separate;
  minimize useful peak Jz and total link sum **separately**, without a blended
  weighted score, R2 fit or fixed15-degree corridor.
- 33 coarse poses retain 8 candidates per bucket; finalists get continuous
  derivative-extrema checks and 2001-pose force integrals. Retain 24 compact
  leaders and 20 detailed cases (16 orientation leaders plus 4 rounded examples).

There are 1,211,631 coarse height/guide/inverse passes and 1,186,062 unequal
monotone candidates before lateral-band filtering; zero pass the full projected
wheel/segment or hip-pitch screen. Counts are geometry/windows, not manufactured
robots. Final run 12.409 s is execution history, not a cross-machine benchmark.
Finite bounds, steps and retained pools do not prove global/manufacturing optima.

At 50 mm, upper-long force leader 190/185,r1.815 gives 37.262 Nm; size leader
200/170,r1.88 gives 38.194 Nm. Rounded 200/175,r1.875 gives 38.523 Nm with a simple
15:8 relation. Lower-long force leader 180/210,r1.715 gives 36.126 Nm but reverses
which segment is longer. Both orientations are available in retained data;
the displayed quartet directly answers the upper-long request.

Useful control range is height-based, not a fixed degree subtraction:
`qlow=z^-1(zstart+20), qhigh=z^-1(zend-20)`.
For 200/175,15:8, total q100-174.083270; useful hip ROM 60.829277 degrees.
All four normal endpoints are close to the assumed 175 degree guard. Actual
stops/ROM/buffer tolerances need review; the study limits are not measured.

## Force, energy and compliance

With Jacobians in metres/radian, generalized applied load is Fx Jx+Fz Jz;
holding actuator torque has opposite sign. Plots show magnitude Fz Jz for
upward vertical load. Peak Jz sets worst vertical force per hip Nm. Smaller
Jacobian needs greater angular speed for a given vertical speed. Speed columns
assume constant vertical 0.25 m/s; side-load envelope uses either-sign
|Fx/Fz|<=0.3 as an explicitly assumed sensitivity.

Relative-knee torque is -tau_hip/r; knee speed is -r times hip speed. Half torque
applies only to guide 2:1. Motor gearing is another power mapping. Ideal useful
lift work remains 31.4533125 J per leg for all rows. Torque advantage is not
energy efficiency. Height-RMS equals time-weighted torque RMS only at constant
vertical speed without dwell; motor heating still needs drivetrain losses,
inertia and real duty. 3g/4g total supported loads multiply the static load term
by 3 and 4 respectively, without predicting impact response. Actual lateral
compliance needs spring/controller/geometric stiffness and contact/rolling;
allowed coupled motion alone does not determine stiffness. No new spring or
motor rating is inferred. Historical dual-rope stays **IMPOSSIBLE /rejected**.

## Reproduction and current evidence

From this app using the existing Python 3.13/Node 22 environment:

```sh
.venv/Scripts/python.exe unequal_inversion_search.py
.venv/Scripts/python.exe -m unittest -v test_unequal_inversion test_curved_paths test_force_travel test_inversion_search
.venv/Scripts/python.exe scripts/verify_unequal_geometry.py
node scripts/verify_unequal_report.cjs --math-only
.venv/Scripts/python.exe scripts/build_unequal_visuals.py
.venv/Scripts/python.exe scripts/build_unequal_report.py
node scripts/verify_unequal_report.cjs
```

23 tests pass, including explicit length-bound and near-equal upper-long fold
checks. 7,440 originalV2/Andy2D scalar checks across 20 cases pass, max 1.7053e-13
mm/Nm. Three actual Pymunk positive-mass motor/pivot/gear fixtures upper25/50/100
pass unchanged path/pin/guide/tracking limits at 2/1/0.5/0.25 ms and converge;
finest path errors 0.010445/0.009186/0.008988 mm. Zero gravity/force/collision
shapes make this geometry-only evidence. Four new labelled 800x640 GIFs have
80 frames and exact 6 s duration, with fixed wheel orientation and explicit
projection-overlap captions. Browser, PDF, source/hash and publication results
are in [validation](validation.md); past failures remain in that history.
No canonical robot, hardware, loaded dynamics, GPU or other-OS certification.
