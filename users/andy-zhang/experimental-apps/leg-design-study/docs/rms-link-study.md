# Equal versus reversed 1.25x links: RMS torque

Andy Zhang with Codex, 2026-10-15. Source base `c92880d`.
Status: bounded ideal static search and independently checked comparisons;
not selected hardware, physical inversion or dynamic motor validation.

Owner request: compare equal/different links for RMS and try reverse
`r2=1.25*r1`. Interpretation: r1 is upper L2, r2 is lower L3; the requested
reverse is L3/L2=1.25. This length ratio is separate from guide `r=ra/rb`.

Open [offline HTML](../rms-link-comparison.html),
[four-page PDF](rms-link-report.pdf), [results](rms-link-results.json) and
[independent checks](rms-link-checks.json), [actual engine checks](rms-link-engine-checks.json), or use
[Open RMS Comparison.cmd](../Open%20RMS%20Comparison.cmd).
Earlier reports remain unchanged and no Motion Lab controls are added.

## Answer and matched comparison

Neither family universally minimizes RMS. At guide2:1, fixed total link
length S gives identical vertical kinematics and vertical-load torque for
equal, upper-long and lower-long links. At other guide ratios a longer lower
link can lower hip RMS when the guide is retuned for the desired sideways
movement. This does not necessarily lower relative-knee or motor-shaft RMS.

All rows below have total link length450 mm, normal start100 degrees,
exactly +50 mm sideways movement,325 mm total vertical travel and assumed
20+20 mm reserves (285 mm useful). Alpha=phase=0; vertical load110.3625 N,
representing45 kg shared over four corners; massless moving links and no
spring, inertia, friction or losses. The same height task requires different
end angles and guide ratios; this compares complete kinematic choices.

| Upper/lower mm | Guide | Hip height-RMS Nm | Equivalent knee RMS Nm | Hip peak Nm |
| --- | ---: | ---: | ---: | ---: |
| 225/225 | 1.825724354 | 35.433 | 19.408 | 43.584 |
| 250/200 | 1.959861171 | 37.254 | 19.008 | 46.496 |
| 200/250 | 1.711530895 | 33.508 | 19.578 | 40.535 |

Reverse200/250 has5.43% lower hip RMS than equal225/225 and10.06% lower
than upper250/200. However, its equivalent knee RMS is about0.88% higher
than equal. The normal end angles are165.613/164.802/167.577 degrees.
The matched guide ratios are continuous numerical values, not finalized
pulley tooth counts. Larger useful angular travel and smaller vertical
Jacobian trade reduced hip torque for motion demand; ideal work is unchanged.

At fixed450 mm and guide2:1, all three have37.743 Nm hip RMS,18.872 Nm
equivalent knee RMS and47.264 Nm hip peak. Normal lateral movements are
0/+39.563/-39.563 mm for equal/upper-long/lower-long respectively. This clean
control isolates orientation: unequal links alone do not reduce vertical RMS.

The earlier selected equal cases have height-RMS31.716/31.078/30.971/30.177 Nm
for25/50/75/100 mm targets; the earlier selected upper-long cases have
32.994/31.816/31.199/30.780 Nm respectively. These are retained rounded
examples, not family RMS optima; exact values are in `previous_*` evidence.

## New bounded RMS search

Search582,471 combinations across:

- S=L2+L3=350..600 mm by5 mm.
- L2/L3=1,1.25,0.8: equal, upper-long1.25x and lower-long1.25x.
- Guide1.2..2.6 by0.01; normal start100..140 by5 degrees.
- Separate normal angle caps165/170/175 degrees.
- 325 mm total height,20+20 reserves,25/50/75/100 +/-2.5 mm normal lateral
  bands, with no normal lateral reversal.
- Assumed rb60 mm and upper-link pitch surplus>=10 mm; full100..260 height
  inverse with minimum Jz>=5 mm/rad. This is not outer-hardware clearance.

There are118,071 height/guide/inverse-screen passes and15,940 lateral-band
passes, counting angle scenarios separately. A65-pose coarse screen and
Simpson RMS estimate retain up to12 candidates per bucket; dense finalists
use continuous extrema and adaptive quadrature.36 bucket leaders are retained,
plus fixed-size controls, prior examples and two rounded reverse cases:
52 detailed analytical cases total. Only hip height-RMS is optimized; knee
and smooth-time values are evaluations of those choices. No global continuous
optimum or exhaustive mismatch-ratio search is claimed.

| Cap deg | Equal links mm; guide; hip RMS Nm | Upper1.25x | Lower1.25x |
| ---: | --- | --- | --- |
| 165 | 230/230;1.82;35.906 | 250/200;1.96;37.256 | 211.1/263.9;1.71;34.822 |
| 170 | 207.5/207.5;1.81;33.262 | 225/180;1.94;34.434 | 191.1/238.9;1.71;32.389 |
| 175 | 190/190;1.79;30.952 | 202.8/162.2;1.93;31.878 | 175.6/219.4;1.70;30.262 |

These50 mm leaders have different actual lateral values within the band.
At175, reverse48.06 mm versus equal52.36 mm gives2.23% lower hip RMS,
but reverse has15.5% longer maximum link and3.95% larger combined length.
Do not attribute the full difference to mismatch alone. At25 mm/cap175,
equal31.591 slightly beats reverse31.705 Nm: reversal is not universally best.
The numerical175-degree winners are close to the angle bound; tolerances,
real buffers and mechanical stops still need selection.

## Rounded reverse examples

- 180/225 mm, guide17:10:49.100 mm sideways, end173.402 degrees,
  hip RMS30.835 Nm, hip peak36.814 Nm, assumed pitch surplus18 mm.
  This is0.78% below the earlier190/190,r1.8 RMS31.078, but uses25 mm
  more combined length and a35 mm longer maximum link.
- 200/250 mm, guide12:7:49.201 mm sideways, end167.519 degrees,
  hip RMS33.550 Nm, hip peak40.599 Nm, pitch surplus37.143 mm.
  This larger rational-guide case is an alternative operating window, not a
  torque improvement over the compact180/225 example.

Both keep exact1.25 lower/upper ratio and full ideal height inverse. At the
reverse fold C lies beyond A by L3-L2, while the lower link crosses the hip
in side projection. A45-50 mm offset does not clear an R200 wheel; measured
axial stack/forks, wheel/tire/hub, chassis and pulley outer hardware are needed.
No physical inversion is certified. Normal lateral movement is permitted
motion, not measured compliance, which still depends on stiffness/contact.

## RMS definition and torque coordinate

```text
height RMS = sqrt((1/H) integral(tau(q(z))^2 dz))
time RMS   = sqrt((1/T) integral(tau(q(t))^2 dt))
tau_hip = Fz * Jz                    # holding magnitude, vertical-only limit
tau_knee = -tau_hip / guide_ratio    # alternative ideal actuator coordinate
relative_knee_speed = -guide_ratio * hip_speed
```

Height-RMS equals time RMS only at constant vertical speed without dwell.
Uniform joint-angle RMS differs. A common smooth quintic useful-height motion
`h/H=10s^3-15s^4+6s^5`, s=t/T, gives static hip RMS34.734/36.497/32.856 Nm
for the matched450 cases; reverse's advantage persists for this assumed duty.
The time is normalized because no inertia is included: this is not a dynamic
one-second lift or acceleration-torque prediction. Dwell and mission loads
are unspecified. Spring compensation and moving masses can change rankings.

The equivalent relative-knee values are alternative actuation mappings, not
an extra reducer or simultaneously independent actuators. A motor gearbox is
separate. Actual RMS current/heating must use the real actuator coordinate,
motor constant, gearing, efficiency, inertia and duty. A lower hip RMS with a
different guide is not automatically a lower knee or motor RMS. Ideal useful
lift work remains31.4533125 J; RMS torque is not energy efficiency.

## Actual verification and reproduction

From this app with existing Python3.13 /Node22:

```sh
.venv/Scripts/python.exe scripts/compare_rms_links.py
.venv/Scripts/python.exe scripts/verify_rms_geometry.py
node scripts/verify_rms_links.cjs --math-only
.venv/Scripts/python.exe scripts/build_rms_report.py
node scripts/verify_rms_links.cjs
```

- 52 cases pass7,702 original JonathanV2/Andy2D scalar comparisons. Independent
  original-V2 dense RMS checks agree within4.541e-12 Nm for height and
  9.891e-12 Nm for quintic time. Maximum overall scalar error9.891e-12 mm/Nm.
- Existing dense trapezoid height RMS agrees with adaptive quadrature within
  7.591e-7 Nm. Doubling quintic time resolution2001->4001 changes RMS by at
  most6.253e-13 Nm. Source hashes and exact r2 identities pass.
- Three actual positive-mass Pymunk7.3.0 full100..260 degree sweeps pass at
  2/1/0.5/0.25 ms with unchanged0.1 mm path/pin,1e-4 rad guide and0.01 rad
  tracking limits. Finest path errors are0.007547/0.008471/0.007361 mm for
  reverse180/225, matched450 reverse and the175-degree50 mm grid leader;
  all converge. Zero gravity/forces and no collision shapes: geometry only,
  not loaded RMS, hardware collision or dynamic motor validation.
- Installed Edge passes JavaScript-disabled local-file reading,4 sections,
  3 SVG/exact evidence,390px layout, PDF link/signature and print export.
  One local file request, zero external requests/page errors. QA files are
  ignored under `artifacts/rms-links/`.
- Four-page PDF and self-contained HTML regenerate deterministically. All
  pages and mobile HTML reviewed; reduced page2 plot/table spacing to protect
  footer clearance, corrected one rounded knee-RMS digit. Poppler retains
  its nonfatal Symbol display-font message without observed glyph defects.

No loaded dynamic spring/motor, impact/contact, hardware/GPU or other-OS
test is claimed. Prior engine validation remains scoped to its original cases.
Preserve historical models/reports and rejected dual-rope IMPOSSIBLE status.
Canonical robot physics is NOT APPLICABLE to this isolated workspace.
