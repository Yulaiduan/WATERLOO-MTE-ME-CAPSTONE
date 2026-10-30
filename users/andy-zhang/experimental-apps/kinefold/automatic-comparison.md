# Automatic actuator comparison

Andy Zhang with Codex, completed 2026-10-30. Experimental quarter-model study; no hardware
selection or canonical robot validation is implied.

## Use

Open tab **06 Actuator studies → Automatic comparison**. V4.5 is the default
captured reference: 8.75 kg chassis, two 1 kg uniform rods, 0.5 kg wheel and
zero compound-pulley mass. The original geometry, mounting alpha and spring are
retained. Select the current saved mechanism explicitly to study another design.
The independent inertia quick calculator remains available in the second view.

Default targets are a **2 m wheel-bottom drop**, a **2 m all-body COM rise above
takeoff**, and **50 mm minimum chassis-underbody clearance**. The underside is
separately assumed 50 mm below the hip. Both dimensions are editable. Physical
compression stops can exhaust travel while underbody clearance is still greater
than 50 mm; the comparison never invents additional braking stroke.

Choose captured terrain or the original 150 mm height / 150 mm plateau / 150 mm
gap square. The terrain moves horizontally under a vertically floating chassis;
chassis x and pitch are fixed, wheel spin is free. This is a one-leg quarter
model, not an assessment of full-vehicle pitch/roll stability or propulsion.

Run captures a copy of the mechanism, source revision, terrain, targets,
assumptions and numerical budget. Editing Studio afterward does not change that
job. Start/cancel/resume-result controls are explicit. Open latest stored result
recovers the most recent job after refresh/restart without rerunning physics. Saving comparison settings
writes `profiles/actuator-comparison.json`; it does not apply hardware or torques
to either Dynamic tab. Exports remain in the app's `exports/` folder.

## Screening and evidence

Every selected exact motor/SO gearbox SKU receives a preliminary geometry,
work, inertia and torque/speed screen. A bounded analytical shortlist then runs
landing, jump and terrain; a smaller native Pymunk shortlist cross-checks the
same captured cases. Default budgets are six analytical candidates and two
Pymunk candidates, with an editable bounded wall-time limit.

Screen-pass, dynamic pass/failure, numerical failure, indeterminate and not-run
are different states. Ranking cannot turn a failed or unrun case into a pass.
The shortlist is computationally bounded: this is not an exhaustive dynamic
search or proof of a global optimum. Even six successful dynamic cases mean
**conditional success under entered assumptions**, not a verified hardware pass.

Landing assesses chassis arrest, clearance and mechanical-stop order plus the
observed recovery period. Jump assesses first-flight all-body COM rise rather
than treating rotor/internal kinetic energy as useful ballistic energy. Terrain
reports ride-height error relative to the grade-following baseline, acceleration, contact fraction and travel reserve
against editable demonstration thresholds, with torque/current RMS information
where the underlying data exist. Interval mean contact forces and sampled peaks
are not impact-strength bounds.

## Finite-link equations

The new contact branch has four physical bodies: chassis, upper rod, lower rod
and freely spinning wheel. Pymunk uses three native pivots, an ideal angular
belt constraint and hip end stops. There is no redundant direct wheel/chassis
guide. The analytical engine independently uses coordinates `(h, d, psi)`, where
`h` is world hip height, `d(q)` is the straight wheel-guide coordinate, and `psi`
is wheel spin. Uniform-rod COM Jacobians supply all translating/rotating inertia
and gravitational potential. The original massless-link branch is retained.

For `j = dd/dq`, moving-body COM offsets `r_i(q)`, lower angular-rate factor
`k3 = 1 - ra/rb`, and reflected drivetrain inertia `Jref`:

```text
Mhh = total body mass
B(q) = sum_i m_i dz_i/dq
C(q) = sum_i m_i |dr_i/dq|² + Iupper + Ilower*k3² + Jref
Mhd = B/j; Mdd = C/j²; Mpsi,psi = Iwheel
H' = (B'j - Bj') / j³
D' = (C'j - 2Cj') / j⁴
M vdot = [ -Mtotal*g + Fz - H'*vd²,
           (tauSpring + tauMotor + tauPassive)/j - g*B/j
             + Fwheel·guideAxis - 0.5*D'*vd²,
           wheelRimTorque ]
```

The same captured alpha rotates every COM/Jacobian and the existing spring
route. The spring is not retuned when masses or alpha change. Rod kinetic and
gravity energies enter both engines' full work ledgers. Native constraint
correction/force splitting and analytical position projection are signed
numerical accounts, separate from physical friction or recoverable spring
storage. Refine dt before interpreting energy or impact values.

Both zero link masses or two positive uniform-rod masses are supported. Mixed
zero/positive links, compound mass, custom inertias, curved guide paths and
non-2:1 equal-link geometry remain explicitly unsupported in actual-contact
mode. No epsilon masses are inserted.

## Motor, gearbox and controller assumptions

```text
Jref = N²(Jmotor + Jgear,input) + Jadditional,output
motoring: tauJoint = etaForward*N*tauShaft
braking:  tauShaft = etaReverse*tauJoint/N
tauDrag,joint = tauC*tanh(N*qdot/epsilon) + b*qdot
```

The input-equivalent gearbox inertia already represents its internal train.
An additional output inertia means external hardware, not a second copy of that
same train. Efficiency does not scale inertia. Housing/motor mass is reported
for comparison, but must already fit the captured chassis mass budget; the
study does not silently add it.

The actuator uses an assumed current/torque plateau with speed rolloff, known
SKU torque/speed caps and editable motoring, braking and regeneration power and
energy limits. Actual delivered torque, not an unlimited request, enters work
integration. Shaft mechanical power is an electrical-sizing proxy; winding
resistance/inductance, copper losses and voltage/current dynamics are not solved.
The entered DC bus labels the assumed envelope rather than deriving a measured
speed curve from incomplete data.

Jump uses bounded extension then coast. Landing uses bounded airborne hold,
compression braking and post-arrest recovery. Terrain uses the same documented
ride-height feedback law for every candidate. Gains are editable study inputs,
not an optimized controller for each motor. Peak duration and RMS torque are
not a temperature model. Current is unavailable unless Kt/current convention
compatibility is explicitly assumed.

Preliminary low/medium/high drag starts at 1/3/8% of usable joint peak as
Coulomb resistance and the same fraction at 10 rad/s as viscous resistance.
Constant detent resistance is a dissipative worst-case cogging envelope;
position-periodic conservative cogging remains a different shared motor option.
Measured total efficiency plus measured separate drag could double count loss.

## Core missing hardware metrics

The retained [Pure Motor Rev2 / SO source sheet](https://docs.google.com/spreadsheets/d/1ttHpUltfZHpnzD9DO-fUXWn_x426xmtnoujWum3Lag4/edit)
contains 14 motors and 157 exact gearbox listings. All 14 motor speed curves are
missing; 11 motors lack continuous torque and 10 lack direct Kt. Rotor inertias
are estimated from assumed components, not measured. 145 gearboxes lack input
inertia and 14 lack efficiency. Unknown values remain null in the catalog.

Before choosing hardware, obtain:

- Measured torque versus speed at the intended bus voltage and controller limits.
- Verified rotor inertia and input-equivalent gearbox inertia.
- Kt with peak/RMS phase-current convention, winding resistance and inductance.
- Continuous torque/current, allowed peak duration, cooling and thermal duty data.
- Braking torque versus speed, regeneration limits and battery/resistor energy acceptance.
- Forward/backdrive efficiency, drag/cogging, backlash/compliance and gearbox shock limits.
- Mechanical shaft/mount compatibility for the exact SKU pair.

The public [Motor Response Modeling discussion](https://chatgpt.com/share/6ae409b5-46f8-83e9-a7be-d25636d9ee78)
was readable through its public hydration data after the earlier private link
failed. Its ideal `Nopt = sqrt(Jleg/Jmotor)` is a rest-acceleration result under
constant torque and no load/speed caps. It is not a fastest-stroke or multi-case
hardware optimum; this comparison adds finite-link contact and bounded cases.

## API and persistence

Same-origin `POST /api/actuator-comparison` uses the existing
`X-Kinefold-Request: coupled-dynamics` guard. Actions are `defaults`, `load`,
`save`, `start`, `status`, `cancel`, `results`, `detail` and `export`.
An owned app-venv subprocess performs physics; the standard-library server does
not import SciPy, NumPy or Pymunk at startup. The job shares the normal dynamics
lock. Captures, progress, detailed trajectories and logs live beneath ignored
`.preview/actuator-comparisons/`. Cancellation and shutdown target only that
owned child. No arbitrary executable or filesystem path is accepted from HTTP.

The optional `kinefold/actuator-limits-v1` contact-only `actuatorConfig` block is
additive. Omitting it preserves the existing ideal torque commands. This study
does not add it to saved project-v3 or silently migrate saved physical designs.

Start/restart using the existing project-local [Start Kinefold.cmd](Start%20Kinefold.cmd)
at `http://127.0.0.1:4191/?tab=actuator`. No boot/login automation is installed.

## Validation and current findings — 2026-10-30

New checks pass: 7 finite-contact groups, 21 actuator/source/job groups and 88
comparison DOM/API/Plotly assertions. Worker legacy validation passed 43 contact,
case, analytical, work and motor groups. Parent checks also passed 6,152 quick
calculator, 1,389 catalog, 3,789 dynamic Plotly, 530 contact-work, 712 Energy UI,
4,490 energy workspace, 48 preset UI and 34 project/library groups/assertions
as labelled by their suites. These are numerical and DOM checks; no live UI,
hardware, GPU or full-robot review is claimed.

A real HTTP job screened 2,198 exact pairs (2,041 numerically resolved; 157 lack
one motor's source peak) and ran 12 finite cases: two selected pairs, three cases,
two engines. The 228 s initial batch used dt 0.000125 s, a 3 s observation and
50 Hz output. An earlier larger batch was cancelled with partial results retained.
Paired crosschecks now run early in the schedule. The final report recomputes
all 12 assessments with explicit output-interval acceleration and replays the
two native landings after correcting stop-event detection. Original results
and payloads remain backed up; review/source hashes identify that reassessment.

| Motor / exact gearbox | Analytical COM jump | Native COM jump | Landing | Terrain window |
| --- | ---: | ---: | --- | --- |
| Flipsky 80100 130KV / AB90-G10-D19 | 0.8862 m | 0.8841 m | both fail: compression stop | both pass entered thresholds |
| Flipsky 80100 130KV / AEP90-G10-D19 | 0.8674 m | 0.8654 m | both fail: compression stop | both pass entered thresholds |

No selected pair passes all three targets. No all-case fast screen passes the
2 m targets under these assumptions; unrun rows remain untested. Other entries
may be investigated by changing selection, assumptions or budget. Passing the
short terrain window does not establish a full terrain cycle, high-speed or
whole-robot capability. The moving 150 mm square at 100 mm/s produces about
0.0245 mm RMS world ride-height error in this stiff ideal guided fixture. This
is simulated control performance, not tire, compliance or hardware fidelity.

A native stop impulse can reverse velocity immediately. The previous sign-based
check missed that real event and falsely labelled a native landing successful;
it now uses the actual RotaryLimitJoint impulse, with a retained regression.
The analytical model detects the corresponding stop. Sampled clearance is not
an impact bound: actual per-step events decide bottom-out.

The separate 250 Nm ideal command fixture gives about 1.7062 m analytical versus
1.7057 m native COM rise at dt 0.000125 s. Static holding agrees with retained
Jon V4 equations, including finite rod weights; alpha20 is checked independently.
Airborne COM follows gravity despite internal leg/rotor motion. Finite-link
kinetic and gravity identities, stop momentum and free-wheel terrain contact
are verified, not merely two identical implementations compared together.

Landing refinement dt 0.00025 to 0.000125 reduces analytical ledger residuals
4.65 to 2.33 J at alpha0 and 4.17 to 2.09 J at alpha20; native residuals reduce
6.14 to 3.07 J and 5.74 to 2.87 J. Native penetration reduces about 0.464 to
0.073 mm (alpha0) and 0.470 to 0.076 mm (alpha20). Residuals remain numerical
uncertainty. The 1 mm penetration guard is unchanged. Native combined constraint
accounting is signed, includes impulses/bias/splitting, and cannot be presented
as measured physical absorption.

Acceleration metrics use output-interval differences of actual chassis velocity
when the engine has no pointwise acceleration; impulsive peak acceleration stays
unresolved. Source-speed overshoot fails an observed case even if torque has
already been limited to zero. Regen energy also caps the final integration step.
Motor/gearbox mass stays within the fixed chassis budget. The examples use an
assumed 48 V / 6,000 rpm envelope, 5 kW power/regen limits, 5 kJ regen acceptance,
nominal estimated rotor inertia, zero missing gearbox inertia, unknown efficiency
0.9, reverse efficiency 0.9 and medium 3% preliminary drag. All are editable;
current remains unassessed without verified/explicitly assumed Kt conventions.

All 40 scientific Plotly PNGs and full captured data are exported into the app
folder and attached to Andy's Codex Studies in Notion. They are scientific plots,
not screenshots. Actual 4191 HTTP defaults/origin guards/assets, launcher
start/reuse/restart from another cwd and unchanged profile-library hash are
checked. The known pre-existing broad Jon HTML whole-file hash mismatch remains
separate; no source hash or assertion is weakened to hide it. Canonical robot
physics is not applicable to this isolated member workspace.

## Saved motor/gearbox replay — 2026-10-30

Open tab06 **Automatic comparison → Open latest stored result**, filter by saved
motor and exact gearbox SKU, and select a row. Its Landing, Jump and Terrain
buttons load a recorded analytical/Pymunk pair. **Play**, pause, speed and scrub
control one clock across both animations. **Open in Analytical tab** and **Open in
Pymunk tab** show that same read-only capture in tabs02/03; **View both together**
returns to the pair. **Return to live design** restores the existing live controls.
Neither action changes the active mechanism, motor, case or profile library.

Every view uses actual recorded frames, wheel indices, moving terrain and spring
stroke from the captured case. One fixed camera encloses both complete trajectories.
At clock t, each engine displays its last recorded frame with timestamp <= t;
there is no interpolation across contact/stop events. The displayed actual sample
time can precede the common clock. Different end times are labelled explicitly,
with a finished engine holding its final recorded frame. Status badges describe
the physical case assessment, not whether playback succeeded. The native desktop
viewer remains a separate live-design workflow; this shared clock controls the
browser replay views.

For an unrun row/case, **Run captured case in both engines** runs just that pair
using its frozen study inputs. Existing saved payloads are authoritative. When
neither payload exists, generation requires the captured default-generator source
hashes to match; an incompatible source change requires a new study. Source/runtime
identity and warnings are retained. Cached exact frames remain replayable without
the physics environment. Replay calculations are stored separately from the
original comparison; its immutable table and export remain the original batch.
Additional actual assessments and plots appear in the captured replay. Reopening
a running case resumes monitoring its existing owned worker. Monitoring errors
keep cancellation reachable, and stale responses cannot replace a newer case.

The guarded comparison endpoint adds `replay`, `run-replay`, `replay-status`,
`replay-result` and `replay-cancel`. Selection accepts only the original safe
job ID, exact captured candidate ID and `landing|jump|terrain`; clients cannot
submit replacement physical settings. `kinefold/comparison-replay-v1` contains
the frozen project/candidate, matched payloads, actual frames/rows, assessments,
settings hash and source identity. New jobs live in ignored
`.preview/actuator-replays/`, share the dynamics lock, run an owned app-venv child
with a bounded timeout, and preserve cancellation/failure/orphan states. They
never update the original study's latest pointer or active Studio library.

Validation:16 service/validation groups pass with `--real`, including six actual
temporary runs (three cases × two engines), source guards, settings identity,
lock/cancel/timeout/shutdown/orphan handling and persisted reuse.212 shared-player
and48 handoff/DOM/API/Plotly assertions pass with three real captured bundles;
115 automatic-comparison UI assertions pass. Both animations render actual
mechanisms, tab switching preserves the clock, scrubbing is exact, terrain moves
and the free wheel spins. A previously unrun Flipsky6384 170KV Battle Hardened /
HTG90-G20 pair also completed all three cases through guarded HTTP, with151
rows/frames per engine and identical non-engine payload settings. Reopening uses
its persisted cache. Original study a52d2ac28caf4bc6968814610af1be29 and profile
library SHA b580c793d96ce2c3fa912490e1d11f8a3fff11854dd7a065d462cc61482fb511
remain unchanged. PNG/GIF previews are rendered from actual saved frames, not
UI screenshots. Live pointer/layout review and hardware fidelity are unverified.
