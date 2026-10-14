# Generalized V2 suspension and motor study

Author: Andy Zhang with Codex. Updated: 2026-10-14. Status: experimental mathematical and rigid-body cross-checks, not accepted hardware or canonical robot validation.

[generalized_leg.py](../generalized_leg.py) adds a new isolated model. Jonathan's
[V2 model](../../../../jonathan-xie/experimental-apps/leg-solver/v2-model.md), Andy's
saved equal-link solvers and all historical profiles remain unchanged. The
dual-rope knee-pulley design remains **IMPOSSIBLE / rejected**; it is not among
the nine generalized spring mechanisms. A separately named
`symmetric_knee_bellcrank` variant is available without changing the old variant.

## Coordinates and two different fixtures

V2 geometry uses mm and degrees; computations use metres and radians. Global
horizontal/vertical coordinates are y/z. The master q is theta2 (B→A), with
theta3 = phi0 + (pi-q)(qab-1). A→B and B→C body axes have pi added. The local
frame rotates clockwise by alpha. Link lengths can differ and qab=ra/rb need
not equal 2. Absolute angular derivatives are:

| Body | d(angle)/dq |
| --- | ---: |
| Upper link | 1 |
| Lower link | 1-qab |
| Independent compound pulley | 1-qcd |
| Wheel | K = 1-qab + qef(qab-qcd) |
| Relative knee coordinate | -qab |

Compound/wheel phases use extension theta2e as zero, matching V2. The physical
guide ratio qab is not the absolute engine gear slope 1-qab. Zero absolute
slopes use locked-rotor constraints; Pymunk zero-ratio gear constraints are
invalid and are never used.

The fixed-A fixture reproduces Jonathan's prescribed force at P, its wheel
moment rw*Ft and moving-body weights. m1 is concentrated at fixed A and does
no suspension-motor work. It is not inferred from contact force. The supported
chassis fixture fully anchors wheel hub C and holds chassis pitch; A(q)=-C(q)
plus a constant offset. Chassis weight contributes once, while the hub support
force performs no translational work. Ordinary gravity and prescribed contact
force are not added twice. This fixture does not solve tire rolling or a
terrain contact trajectory.

For body positions R(q), constant angular slopes a', mass m and centroid
inertia I, the independent inverse dynamics is:

```text
M = sum(m |R'|^2 + I a'^2)
H = sum(m R' dot R'')
tau_q = M qddot + H qdot^2 + dV/dq - Qcontact - Qspring
Qspring = -Tinput d(ell)/dq
```

Direct hip actuation uses q. Relative-knee actuation uses derivative -qab,
so tau_knee=-tau_q/qab and omega_knee=-qab*qdot. For a reduction N,
omega_motor=N*omega_joint and tau_motor=tau_joint/(N*eta). Efficiency defaults
to explicitly assumed 1; the simple /eta convention is conservative motoring
torque in both signs, not a regenerative electrical model. Locked wheel-drive
tau4 is analytical, including compound/wheel angular inertia for non-unit
qcd/qef and nonzero K; its independent shaft reaction is not engine-validated.

## Nine actual spring geometries

Upper and lower attachments use their own L2/L3 and actual body frames. The
50 mm extension is a spring attachment beyond the knee, not an extra duplicate
robot definition. V2 rod masses remain distributed knee→hub; the old Andy
lower-link mass includes its extension, so their distributed lower masses
cannot be equated silently. Direct scissor, chassis, hip/knee bellcrank and
gravity-balance spans come from actual anchor separation. Hip payout derivative
is direction*r; knee/capture payout is direction*qab*r. Forces act at the
corresponding direct anchors or drum tangents on both bodies.

The existing passive coil law is reused; its old equal-link geometry is not
used by this model. All nine topologies have zero damping. Compression,
extension and captured coil signs remain explicit. Ideal rope tension cannot
be negative. Fitting minimizes residual static torque at 81 uniformly spaced
q samples, separately from the time-weighted trajectory RMS. It enforces
nonnegative rate, one-sided force signs, positive physical free length and
positive coil travel. No hardware force/stroke/solid-height rating was supplied;
`feasible` therefore means the ideal passive law and geometry, not coil
manufacturability or packaging approval. A non-2:1/unequal-link gravity-balance
fit does not inherit exact constant lift.

## Central 325 mm illustrative candidate

The root sizing study's bounded candidate is L2=180 mm, L3=340 mm, ra=106.5 mm,
rb=60 mm, alpha=4.375 degrees, phi0=0, theta2e=100 degrees,
theta2c=159.81088834775142 degrees, rc=rd=re=rf=35 mm and rw=200 mm. Total
vertical capacity is 325 mm, with 20 mm at each end leaving 285 mm usable.
The total-link length is 520 mm. L3 lies on the compact search bound; this is
a sampled tradeoff, not a global optimum. Endpoint lateral displacement is
-5.320 mm; the full-path excursion is 11.412 mm, so endpoint displacement alone
does not describe the path.

The user supplied a 40–45 kg robot/approximately 10 kg per-leg budget. The
physical example explicitly assumes m1=8.30, m2=m3=.35, m5=.10 and m6=.90 kg,
totaling 10 kg. The upper budget keeps moving masses and uses m1=9.55 kg,
totaling 11.25 kg. The original screenshot m1=10/other masses=0 is preserved as
an analytical limit; it cannot be an executable rigid-body baseline.

| Topology | Rate N/mm | Installed preload N | Coil stroke mm | Peak coil load N | Static residual RMS Nm |
| --- | ---: | ---: | ---: | ---: | ---: |
| legacy_tip | 5.915 | 155.786 | 68.059 | 558.377 | 3.404 |
| hip_pulley | 3.325 | 229.231 | 70.719 | 464.381 | .612 |
| knee_pulley | 4.222 | 258.288 | 62.763 | 523.247 | .612 |
| direct_scissor | .296 | 184.435 | 121.097 | 220.224 | .819 |
| hip_bellcrank | 4.370 | 213.948 | 67.784 | 510.150 | .337 |
| knee_bellcrank | 8.108 | 128.418 | 63.122 | 640.224 | 3.937 |
| chassis_direct | .181 | 108.939 | 191.918 | 143.751 | 1.384 |
| knee_capture | 4.222 | 258.288 | 62.763 | 523.247 | .612 |
| gravity_balance | 3.109 | 213.186 | 73.144 | 440.578 | 2.543 |

Among these fixed illustrative mounts, the hip bellcrank is a useful passive
example with the lowest residual RMS and a positive 35.253 mm physical free
length. It uses an 80 mm arm at 135 degrees and a chassis mount (120,50) mm.
This conditional comparison does not select a manufactured spring.

For a 1 s C2 quintic 285 mm vertical traverse with reduction/efficiency 1, its
motor-equivalent peak/RMS are 6.449/3.641 Nm; maximum q speed is 1.605 rad/s
and acceleration 6.573 rad/s². Compression raises C relative to A and lowers
the chassis when C is anchored. Exact time reversal raises the chassis;
signed speed reverses, and peak/RMS torque magnitudes are the same in this
undamped model. Both directions and a complete 2 s out-and-back cycle are
reported separately. At .5/1/2 s per direction, peak torque is approximately
23.939/6.447/2.111 Nm, speed 3.210/1.605/.803 rad/s and acceleration
26.292/6.573/1.643 rad/s² (101 time samples). These are conditional sizing
loads, not motor ratings.

## Impact load envelope is a different calculation

The user's 3–4g assumption is interpreted as TOTAL support, giving 294.3–392.4 N
at 10 kg or 331.088–441.45 N at 11.25 kg. The corresponding upward net
accelerations are 2–3g. A requested 4g NET upward acceleration instead means
5g total support. Stress cases hold geometry and apply equivalent extra
downward inertial load at chassis A, retaining the fitted 1g spring. They do
not multiply the smooth-motion torque or duplicate its ordinary inertia.

| Corner mass | 3g total: peak Nm | 4g total: peak Nm | 5g total: peak Nm |
| --- | ---: | ---: | ---: |
| 10 kg | 82.515 | 123.353 | 164.191 |
| 11.25 kg | 97.829 | 143.772 | 189.715 |

These values use reduction/efficiency 1. Geometry and coil deformation are
held at working poses, so impact compression, peak-versus-mean stopping force
and rebound are unresolved. Zero damping cannot prove impact dissipation.

## Actual verification and known failures

Run from the app root with its installed environment:

```sh
.venv/Scripts/python.exe -m unittest -v test_generalized_leg
.venv/Scripts/python.exe scripts/verify_generalized_leg.py
```

Twelve tests pass, including all nine geometries, laws, energy and generalized
force against the existing `spring_mechanisms.py` under equal links/qab=2;
independent `math_model.py` inertia/gravity/spring terms on their exact common
mass fixture; V2 rotor derivatives, screenshot fixed-A torque and m1 invariance;
unequal-link/tilted virtual work; relative-knee/reduction power mapping; and
actual Pymunk refinement in both directions. The legacy comparison sets lower
mass zero to exclude the incompatible extension COM convention explicitly.

The verification script passes ten scenarios: a full 1 s physical trajectory
for every spring with 2 ms→1 ms refinement, plus a tilted/unequal/nonzero-K
fixed-A fixture. All fine-step motor-impulse errors stay below the declared
absolute/relative tolerance and decrease under refinement. The engine sets
initial poses only, then applies actual point forces and solves pivots, gears
and a velocity motor through `Space.step`; no analytical torque is injected and
no body is reset onto the commanded path. Motor impulses are magnitudes, so
the overlay compares absolute engine/analytical torque and does not invent a
signed engine measurement. Guide/pin errors and an explicit timestep-scaled
tracking tolerance are reported. These ideal constraints do not reproduce
Jonathan's real belt span/bearing force allocation; those FBDs remain checked
by his separate solver.

An early microgram-mass regularization attempt failed badly (roughly .5 m pin
error and 54 Nm torque discrepancy) and was rejected. Zero dynamic masses now
raise an explicit error; the assumed nonzero allocation is separate. An early
250-iteration engine run under-resolved some initial constraint forces;
800 solver iterations resolve the reported tests. A compound rotor slope
mistakenly copied from its relative tibia angle was corrected to absolute
1-qcd and independently checked against V2. No failed attempt is reported as
passing evidence.

`study(payload)` accepts nested `config` or flat V2 keys, duration, sample_count,
buffers, actuator_coordinate, reduction, efficiency and an optional spring
object. `action="size"` returns analytical sizing; `action="validate"` adds
actual chosen-direction refinement and all-nine held-site checks. Raw results
stay in ignored local output. Module/runtime/tests remain inside this member
app; canonical physics is not applicable.
