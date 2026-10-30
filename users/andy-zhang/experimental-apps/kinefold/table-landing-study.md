# Landing table comparison — 2026-10-30

Andy Zhang / Codex. Experimental actual-contact quarter-model calculations,
not hardware survival or a reproduction of an unavailable original derivation.
Source: the owner's supplied table (45 kg chassis; cases1a/1b alpha20 and
cases2a/2b alpha0; 1/1.5 m falls;65deg travel;97/146Nm; AB tensions5.2/7.4/3.1/4.06kN).

## Matched inputs and explicit missing-data assumptions

Both independent analytical/Pymunk engines use the same complete captured input:

- 45 kg **chassis**, shared equally between four legs:11.25kg per corner.
- Fully open held fall at theta2=100deg, compression boundary165deg: full65deg,
  zero stop reserve. Drop is the initial wheel-bottom gap above a stationary floor.
- Alpha0/20deg,300/300mm V4 links,200mm wheel radius,50/25mm AB pulley radii,
  original other pulley/horn/idler geometry and zero entered belt preloads.
- Massless rods and compound pulley; an explicitly assumed0.5kg free uniform-disc
  wheel per corner is required for actual contact. This fixture is therefore47kg
  gross if replicated four times. It is separate from the V4.5 finite-link design.
- Rigid floor, friction0.8, zero restitution; vertically floating chassis with
  fixed x/pitch. No motor speed/power/regen cap, rotor/gear inertia or drag.
  All torque values are ideal **joint** magnitudes conjugate to theta2.
- Two spring assumptions: **off**, and **scaled V4 assist**. The latter scales
  original k and90deg preload by `(11.25/8.75)*cos(alpha)` with the chassis-local
  horn/idler route unchanged. This is approximate gravity compensation retuned
  separately for each angle, not one unchanged spring across angles. No extra
  compression soft stop or damper is introduced. The screenshot supplies no
  spring tuning, moving masses, friction, belt preload or pulley sizes.
-50mm underside offset and50mm minimum clearance reference. Physical angular
  travel ends first, with about296/305mm underbody gap at the compression boundary.

These missing inputs are visible assumptions, not facts inferred from the table.
They are editable through the study CLI/configuration; the live library is untouched.

## Constant joint braking torque

Each row first applies the actual printed97/146Nm command, then searches a
bounded local failing/passing bracket. Values below are upper passing samples at
dt0.000125s. Fine bracket widths are not physical accuracy or a global minimum.

| Case | Drop / alpha | Table Nm | Scaled-assist analytical Nm | Scaled-assist Pymunk Nm | Spring-off analytical / Pymunk Nm |
| --- | --- | ---: | ---: | ---: | ---: |
|1a|1m /20deg|97|96.24|96.62|136.00 /136.16|
|1b|1.5m /20deg|146|144.78|144.78|184.19 /184.50|
|2a|1m /0deg|97|97.008|97.253|139.32 /139.66|
|2b|1.5m /0deg|146|145.92|145.92|187.97 /188.30|

Thus the table's torque row is consistent, to roughly1%, with this **assisted**
fixture. It is insufficient with the spring off: all eight printed-command
spring-off runs bottom out. This is conditional agreement, not proof of the
original table's full model. The image's numbers match `(45/4)*g*h/radians(65)`;
gravity released during compression is almost cancelled by scaled spring storage.

Printed97Nm is a significant rounding at zero reserve: both engines bottom out
in case2a, while97.28162256Nm (the unrounded table equation) arrests in both at
dt0.0001s. This very small margin cannot establish a hardware torque rating.
Whole-number common commands97/145/98/146Nm for assisted1a/1b/2a/2b, and
137/185/140/189Nm with the spring off, all arrest in both engines atdt0.0001s.

## AB belt load at the printed table torque

These peaks use the **printed97/146Nm commands**, not the independently searched
braking commands above. All values are kN, over1ms output intervals. Intervals
containing reported first-contact or angular-stop events are kept separately.

| Case | Table AB kN | Scaled-assist analytical | Scaled-assist Pymunk | Spring-off analytical / Pymunk |
| --- | ---: | ---: | ---: | ---: |
|1a|5.20|5.721|5.774|5.048 /5.106|
|1b|7.40|7.714|7.796|7.008 /7.095|
|2a|3.10|3.221|3.221|1.959 /1.960|
|2b|4.06|4.200|4.201|2.947 /2.949|

The assisted estimates are about3.4–11.1% above the image. Paired assisted
engines differ at most about1.1%. Tilt changes the lower-link force moment arm,
so similar joint torque does not imply similar belt tension. Missing original
geometry/preload and different interval/event definitions prevent an exact
attribution of the image's belt numbers.

Neither engine models elastic belt strands. For massless links and a free wheel,
the source moment convention can be reconstructed from actual wheel momentum:

`Fw = Fcontact + (0,-mw*g) - mw*Delta(vwheel)/Delta(t)`

`DeltaTAB = -cross(rBC,Fw)/rb`

The source x/z frame is used with metres, N and seconds. The lever is the mean
of the two interval endpoint vectors. Source strands are
`U=Tab0+max(DeltaTAB,0)` and `L=Tab0+max(-DeltaTAB,0)`; zero entered preload gives
the **minimum required tight strand** `abs(DeltaTAB)`. It is an interval inverse-
dynamics estimate, not a native belt-force sensor or an elastic shock peak.
The formula is not a substitute for finite-rod inverse dynamics or a driven
wheel's transmitted couple. Rigid impact/stop forces are timestep/window dependent;
do not present them as finite physical belt peaks.

## Energy, numerical checks and corrected classifications

Motor work uses each engine's integration accumulator, not an area inferred
from decimated plots. Spring storage is its exact potential difference; gravity,
kinetic, friction/contact and numerical residual terms remain distinct. The
spring mainly offsets extra compression gravity, leaving most drop energy for
the motor to remove. All18 Plotly PNGs include torque/belt overviews and each
case/spring's motion, braking, kinetic energy, work-versus-angle and residuals.

Case1b refinementdt0.00025 to0.0001 at a common145Nm assisted command reduces
whole-run residual6.171→2.457J analytical and8.932→3.560J native. At185Nm with
spring off,8.282→3.294J and9.082→3.615J. Residuals remain numerical uncertainty,
well above the precision of some zero-reserve search brackets. All16 fine-step
rounded-command cases pass the unchanged1mm penetration/constraint guards.

The study exposed two real false-success classifications at the compression
boundary. Analytical PGS floor/stop coupling and native groove endpoint impulses
could reverse chassis velocity before the old position/free-velocity predicates
noticed the stop. Events now follow actual meaningful stop impulses with existing
activation bands/significance cutoffs. Native scalar-rotor wheel impulse is
subtracted before identifying the groove endpoint reaction; finite-link native
hip-stop detection is retained. No force law, mass, integration constraint or
tolerance is changed. A stop-assisted arrest is a failed motor-only landing.
Pre-fix captures are retained locally; they are not the final published results.

Validation:29 analytical/case/finite groups and34 contact/case/motor/work groups
pass, including exact false-pass fixtures and ample-stroke/rotor/tilt negatives.
35 project/library groups,115 energy assertions,185698 tilted-energy assertions
and3 study groups pass. Four actual static engine/angle runs reproduce Jon V4's
AB span values within0.1N, with interval vertical momentum balance within0.001N.
An initially arbitrary0.0001deg cold-contact pose test failed native sag of about
0.00048deg; the new test instead checks10micrometre physical holding drift, while
the independent force/momentum tolerances remain unchanged. Source math/provenance
checks are not relaxed. The pre-existing broad whole-JonHTML hash mismatch remains
separate and is not claimed passed.

The retained final evidence contains240 actual engine executions: table commands,
bounded torque trials, full-output bracket checks, fine/coarse checks and the
unrounded97.2816Nm test. No UI pointer automation, GPU or hardware review is claimed.

## Reproduce and inspect

After app setup, from this directory:

```powershell
.venv/Scripts/python.exe table_landing_study.py --output .preview/my-table-study
.venv/Scripts/python.exe verify_table_landing_study.py
node verify-projects.cjs
```

CLI options expose dt, output rate, wheel mass, friction, duration, bounded search
iterations, individual case, spring assumption and engine. Captures are cached
only when the exact payload and physics-source hashes match; use a new output
folder after a source change. Exploratory trials use100Hz output but per-step
events; final bracket endpoints are rerun at the requested1000Hz output.

Ignored app exports and native Notion attachments contain18 PNGs, complete
primary/fine trajectories, per-engine source identities, local search evidence,
Plotly specs and16 portable project JSONs. A second small archive retains the
coarse refinement trajectories. Import a project as a separate named design;
no library entry or current mechanism was overwritten. Full opening is now an
accepted saved case value1, with the existing2/3 default unchanged.

Use [Start Kinefold.cmd](Start%20Kinefold.cmd) at
`http://127.0.0.1:4191/?tab=analytical` or`?tab=pymunk`; no login/boot automation.
Canonical robot physics is not applicable to this isolated member study.
