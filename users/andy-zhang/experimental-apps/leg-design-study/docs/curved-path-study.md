# Curved paths for lateral wheel movement

Andy Zhang with Codex, 2026-10-14. Numerical source base `93fed9f`;
publication follows the concurrent Motion Lab contribution without changing it.
Status: conditional experimental geometry, force and control screening.
Read [the static offline report](../curved-paths.html),
[seven-page PDF](curved-path-report.pdf) and [numerical evidence](curved-path-results.json).

## Current request and decisions

The owner cancelled the proposed R²/fixed-15-degree corridor method before it
was published and asked instead for similar curved paths that permit lateral
wheel travel/compliance through changes in guide ratio. The owner confirmed
comparison of **25, 50, 75 and 100 mm** sideways movement. The preceding height
clarification remains **approximately 325 mm total including buffers**. Retain
two explicitly assumed 20 mm height reserves, leaving **285 mm useful**.
These are geometric reserves, not measured impact or spring compression limits.

This new search keeps **alpha=0 and original fixed phase phi0=0**. It does not
use fixed indexing, free-angle fits, R² or a line-shaped corridor as a target.
The abandoned unpublished work remains only in ignored local artifacts; it is
not a deliverable. Existing published reports stay intact as dated evidence.
The new report adds no Motion Lab controls or services.

Sideways travel means **peak-to-peak x excursion over the normal 325 mm stroke**,
with a declared +/-2.5 mm target band. It is not an upper limit that would admit
the zero-excursion vertical baseline as a curved winner. Monotone lateral normal
motion is required; signed drift, excursion, total lateral variation and turning
points are still reported separately for normal, useful and full intervals.

## Practical comparison seeds

All examples have equal links, alpha=phi0=0, normal q start=100 degrees and
325/285 mm total/useful height. The force column uses the pure vertical
equivalent corner load **110.3625 N** (45 kg robot /4 corners), with massless
moving links to isolate geometry. This differs from the screenshot's simultaneous
Fy=Fz=100 N diagnostic. No spring assistance, inertia or motor rating is inferred.

| Target sideways mm | L2=L3 mm | Guide ra/rb | Actual normal excursion mm | Useful hip peak Nm |
| --- | ---: | ---: | ---: | ---: |
| 25 | 185 | 1.9 (19:10) | 24.886842 | 38.386971 |
| 50 | 190 | 1.8 (9:5) | 49.980751 | 37.363029 |
| 75 | 200 | 1.7 (17:10) | 76.478520 | 37.092977 |
| 100 | 205 | 1.6 (8:5) | 101.052336 | 35.887755 |

**Proposed balanced geometric seed: 190/190 mm and guide 9:5.** It gives
approximately 50 mm lateral movement with the required height and a useful
hip ROM of 61.8158 degrees. The 100 mm example offers more lateral movement
and slightly lower vertical-load peak torque, but stronger lateral/vertical
coupling can add rolling/scrub demand and side-load sensitivity.

With guide rb=60 mm, ra is 114/108/102/96 mm respectively. These are pitch-radius
relations, not selected pulley teeth, belt pitch, strength or manufacturing
tolerances. Equal links were chosen for understandable comparison; the bounded
force leaders allowing up to 5% mismatch are also retained.

## Why links can be shorter than 300 mm

The old near-300 mm recommendations were not travel-only minima. They combined
normal projected hip/wheel clearance >=220 mm (200 mm wheel radius plus assumed
20 mm gap), own-chord angle/bow and tangent-spread conditions. The new curved
search removes those straight-path conditions and separates the normal-clearance
scenario from pure geometry. Changing the guide ratio and allowing more joint
motion can give the required height with 185-205 mm links.

The compact examples **fail normal coplanar clearance**: minimum wheel-centre
distance from the hip is approximately 33.14/32.89/37.77/29.23 mm. This is not
compatible with a coplanar 200 mm-radius wheel near the hip. Larger normal
clearance-filtered force leaders are:

| Target sideways mm | Equal L mm | Guide | Normal lateral mm | Hip peak Nm |
| --- | ---: | ---: | ---: | ---: |
| 25 | 280 | 1.93 | 23.440910 | 53.839778 |
| 50 | 285 | 1.85 | 50.203998 | 52.673219 |
| 75 | 295 | 1.775 | 75.983587 | 52.264602 |
| 100 | 300 | 1.705 | 99.537787 | 51.286973 |

These clear the **normal branch only** under the assumed 220 mm centre exclusion.
All near-equal full coplanar inversions still fail. Actual axial/chassis/wheel,
shaft and belt geometry is unresolved. Do not claim axial packaging works just
because the model is two-dimensional and collision-disabled.

Wheel radius Rw=200 mm and each link length L are independent dimensions. A
capacity expression such as 2L is not the available stroke; both endpoint angles
and the guide relation determine it. The angular limits below are declared
study assumptions, not measured hardware stops.

## Original equations and ratio effects

Jonathan conventions are retained: q=theta2 is the hip-input angle, L2/L3 are
link lengths and r=ra/rb is the link-system guide. In the equations x is
Jonathan's global y coordinate; z is global z. At alpha=phi0=0, t=q-pi, k=r-1:

```text
x = L2 cos(t) - L3 cos(k t)
z = L2 sin(t) + L3 sin(k t)
Jx = -L2 sin(t) + k L3 sin(k t)
Jz =  L2 cos(t) + k L3 cos(k t)
```

Lengths are mm and derivatives above are mm/radian. Equal links at r=2 give
an exact vertical line. Reducing r below 2 bends the normal path laterally as
the leg retracts; r above 2 bends it the other way. The report isolates this
effect using fixed 300/300 mm links, q start=100 degrees and the same 325 mm
vertical stroke at r=1.5, 5/3, 1.8, 2 and 2.2.

Phase-zero symmetry gives x(-t)=x(t), z(-t)=-z(t). At the fold q=180 degrees,
Jx=0 while Jz=L2+(r-1)L3 is positive. Thus a full symmetric ideal inversion has
**zero endpoint horizontal drift** even though it moves substantially sideways
and returns. The inverted branch mirrors its lateral movement. Ranking full
paths by endpoint drift alone would incorrectly call these paths vertical.

Every near-equal full path has minimum hip distance |L2-L3| at the fold, far
below 220 mm. Ideal height inversion therefore does not establish physical
inversion, contact behavior or a ground flip. Preserve the historical dual-rope
**IMPOSSIBLE /rejected** decision.

## Lateral movement versus actual compliance

Jx/Jz measures local horizontal movement per vertical movement; tangent angle
is atan2(Jx,Jz). Maximum |Jx|, slope range, arc length and full turning points
are retained. The curves permit a coupled one-degree-of-freedom movement, not
independent horizontal suspension travel. At the phase-zero fold Jx=0, so
horizontal mobility vanishes locally despite regular vertical inversion.

For stable effective joint stiffness K_eff (Nm/rad) and J in metres/rad:

```text
Cartesian compliance C = J J^T / K_eff
Cxx = Jx^2/K_eff; Cxz = Jx Jz/K_eff; Czz = Jz^2/K_eff
```

This rank-one local relation assumes the coupled movement is free to occur.
K_eff must include spring/controller stiffness and load-dependent geometric
stiffness. A locked actuator or blocked vertical motion can block the allowed
sideways movement. No absolute horizontal spring rate is asserted without
actual spring routing, controller, preload/load and contact inputs. Tire
deformation, traction and wheel rotation determine rolling versus scrub. Wheel
spin cancellation alone does not enforce no-slip rolling.

## Force, ROM and efficiency

```text
tau_hip = -(Fx Jx + Fz Jz)              (J in metres/radian)
worst vertical force per hip Nm = 1/max(Jz)
tau_relative-knee = -tau_hip/r
relative-knee speed = -r hip speed
qdot = zdot/Jz
qddot = zddot/Jz - (dJz/dq) zdot^2/Jz^3
RMS_z(tau) = Fz sqrt[integral(Jz^2 dz)/H]
ideal lift work = integral(tau dq) = Fz H
```

The factor one-half between power-equivalent hip and relative-knee torque applies
only at r=2. Changing the guide changes both torque and speed mappings. An
additional motor gearbox is separate. For a 45 kg robot shared equally across
four corners, the useful 285 mm vertical lift always needs **31.453313 J per
leg** in this ideal model. Lower torque with more joint travel does not improve
ideal energy efficiency. Angle-average torque is FzH/ROM; height-RMS is useful
for a constant vertical speed but real thermal duty needs time weighting.

For the proposed 190 mm 9:5 seed, direct hip peak is 37.363029 Nm, height-RMS
approximately 31.08 Nm, and peak hip speed approximately 1.706 rad/s at an
illustrative 0.25 m/s constant vertical speed. The report compares signed
Fx/Fz=-0.3/0/+0.3 sensitivities and the sign-unknown robust bound
Fz max(|Jz|+0.3|Jx|). This ratio bound is an assumption, not measured traction.
3/4g values mean total held-load multiples, not additional g or actual impacts.
Actual springs, moving inertia, acceleration cycle, drivetrain losses and
thermal limits remain necessary before motor selection. Earlier spring/motor
ratings from different geometries are not transferred to these curves.

Effective ROM is calculated by inverse height:

```text
z(qend)-z(qstart) = 325 mm
z(qlow)-z(qstart) = 20 mm
z(qend)-z(qhigh) = 20 mm
useful hip ROM = qhigh-qlow
```

The 190 mm 9:5 case uses total q=100..174.484 degrees and useful
q=109.294..171.110, giving 61.816 degrees hip ROM. It is not a fixed angular
subtraction or a wheel-radius formula. Separate 185 mm r=1.8 start95 and start90
diagnostics expand the full envelope to 95..265 and 90..270 respectively. They
show sensitivity to the assumed start limit. Unlike exact r=2 at q=90, these
lower-ratio cases retain a finite positive full Jz. Do not claim the grid's
100 degree start is an unavoidable minimum or a hardware clearance result.

## Search and weighting

There is **no blended weighted objective**. First apply hard constraints; retain
separate force and size leaders. Force minimizes useful-stroke peak Jz, maximizing
worst pure vertical force per hip Nm. Size minimizes link sum under the same
band and feasibility conditions. RMS, ROM, side-load peaks and speed are compared
explicitly, not silently weighted. Rounded-ratio examples need not equal grid
minima, which often exploit the edge of the +/-2.5 mm lateral band.

| Variable/check | Domain/policy |
| --- | --- |
| L3 | 150-400 mm, step 5 |
| L2/L3 | 0.85-1.15, step 0.025; primary equal/within5% tiers |
| Guide | 1.3-2.6 step 0.005 plus exact5/3; rb=60 mm |
| Normal start/end | q100-140 step2.5; end solved for325 mm and <=175 |
| Full inverse | q100-260, min Jz>=5 mm/rad; selected continuous extrema |
| Pulley pitch | L2>60(r+1), ideal nonoverlap screening |
| Lateral band | 25/50/75/100 +/-2.5 mm normal excursion; monotone normal x |
| Packaging | Separate geometry-only flags vs normal min radius>=220 mm |
| Coarse/final | 33 coarse poses; continuous derivative-root extrema and 2001-pose integrals |

The grid enumerates **2,953,002 geometry/window combinations**, including
invalid ones. It has 1,259,761 height/pitch/full-inverse coarse passes,
1,240,806 monotone-lateral passes, and 408,161 of those clear normal220.
Coarse target-band passes are 67,338 /46,378 /32,116 /24,528 for 25/50/75/100
respectively. These count windows across length tiers, not distinct robots.
Thirty-two compact bucket leaders and 29 detailed cases are retained. Final
continuous acceptance checks each retained selected geometry; finite grid and
pool retention do not prove a global continuous or manufacturing optimum.

## Validation and reproduction

- [Original-model checks](curved-path-math-checks.json): **10,788** scalar
  comparisons against original Jonathan V2 geometry/statics and Andy 2D statics,
  max discrepancy **2.2737368e-13 mm/Nm**. Current source hashes match.
- Six new plus five force and five inversion numerical tests: **16/16 pass**.
  Independent derivatives, rank-one compliance map, continuous extrema,
  inverse-height buffers, work and retained acceptance are checked.
- Independent read-only Sol6.1 high audit of all29 cases agrees on excursion,
  drift/variation to7.11e-14 mm, slope1.07e-14, usefulROM1.08e-12 degrees and
  signed/robust side-load peak1.43e-14 Nm. All turns and clearance/inverse flags
  agree; 90/95 full envelopes are consistent. Compact leader metrics were
  retained following the review so objective results remain reviewable.
- [Actual Pymunk evidence](curved-path-engine-checks.json): three positive-mass
  full angular fixtures pass at2/1/0.5 ms and converge; fine path errors
  0.016781..0.018228 mm. Real pivots/gears/motor and Space.step generate movement;
  only initial poses are assigned. Zero gravity/forces, absent collision shapes:
  geometry evidence, not actual compliance, load, contact, impact or packaging.
- Installed Node22.23.3 /Python3.13.12. Installed Edge passes JavaScript-disabled
  file reading, seven sections/six SVG, exact embedded evidence/four shortlist
  rows, finite figures, no external requests/page errors, 390 px layout,
  PDF link/signature and print callback/CSS/export. All final PDF pages and
  relevant HTML/mobile figures are rendered and visually checked.
- Viewing needs no runtime/server/network. Canonical robot physics is
  **NOT APPLICABLE** to this member workspace. No actual springs, controller
  stiffness, hardware, physical inversion, GPU or other-OS validation is claimed.

From this app after installing its existing pinned Python/Node dependencies:

```sh
.venv/Scripts/python.exe curved_path_search.py
.venv/Scripts/python.exe -m unittest -v test_curved_paths test_force_travel test_inversion_search
.venv/Scripts/python.exe scripts/verify_curved_geometry.py
node scripts/verify_curved_report.cjs --math-only
.venv/Scripts/python.exe scripts/build_curved_report.py
node scripts/verify_curved_report.cjs
```

Use `.venv/bin/python` on macOS/Linux; those systems are untested. The browser
verifier uses sibling Wheel Leg Lab's locked Playwright and installed
Edge/Chrome. The renderer only consumes retained evidence and does not rerun
search or physics. Raw captures/renders/print exports stay ignored. The
[manual CMD opener](../Open%20Curved%20Path%20Report.cmd) uses its own directory.

Next resolve measured axial/chassis/wheel/belt clearances, acceptable rolling
and scrub, spring route, controller stiffness and motor load/duty/inertia.
Preserve earlier reports, original model decisions, undamped suspension,
existing Motion Lab examples/GIFs and dual-rope IMPOSSIBLE status.
