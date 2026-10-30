# Motor losses, jumping and terrain heave

Andy Zhang with Codex,2026-10-30. Experimental finite-link quarter model;
editable assumptions, not motor selection or hardware validation.

## What changed

Both Dynamic tabs now expose gearbox input-equivalent inertia beside motor
rotor inertia and reduction. Low/medium/high Apply buttons explicitly insert
editable shaft-loss examples; they preserve entered gearing/inertia and do not
rewrite old designs automatically. Saved mechanism, actuator presets, screens,
system flow and paired captures retain the new optional inertia field.
See [motor laws and compatibility](motor-model.md).

Per the owner's clarification, **cogging is included in constant Coulomb
resistance**, independent of angle. The study sets separate periodic cogging
amplitude to zero. Viscous drag depends on speed. The legacy periodic detent
option remains under Advanced for existing designs.

Both contact engines now integrate Coulomb and viscous energy loss separately
at every physics step. These Plotly traces sum to the existing aggregate loss;
they are not counted twice in the work balance. Sampled motor diagnostics use
the current actual state, preserving bounded shaft/joint efficiency conversion.

## Equations

For positive reduction N=omega_motor/omega_joint, hip angle q in radians,
shaft Coulomb estimate Fc, viscous coefficient b and smoothing speed epsilon:

```text
Jdrive,joint = N² (Jmotor + Jgear,input)
tauC,joint   = -N Fc tanh(N qdot / epsilon)
tauV,joint   = -N² b qdot
Ploss,C      = Fc tanh(omega_motor / epsilon) omega_motor >= 0
Ploss,V      = b omega_motor² >= 0
Eloss        = integral(Ploss,C + Ploss,V) dt
Kdrive       = 1/2 Jdrive,joint qdot²
```

Away from the near-zero transition, Coulomb magnitude is N Fc and its direction
opposes motion. It does not depend on q. This is the requested dissipative
cogging approximation, not static stiction or a measured magnetic waveform.

The full finite-link equations use the existing configuration-dependent mass
matrix and COM Jacobians in [automatic comparison](automatic-comparison.md).
Inertia changes acceleration and impact momentum. It stores kinetic energy;
it is not itself a friction loss. The work ledger is:

```text
Delta K = motor work + gravity released + spring released
          - Coulomb loss - viscous loss - additional joint damping
          + terrain/external work - impulse accounts
          + position correction + signed numerical residual
```

The same friction that consumes useful launch work helps remove landing energy.
No artificial rule forces a jump result below a landing result. Jump height is
observed all-body COM rise above takeoff; landing drop is wheel-bottom clearance
before first contact, so the two height definitions are different.

## Retained assumptions

| Input | Explicit value |
| --- | --- |
| Chassis / corner |45kg total /11.25kg per leg |
| Upper rod / lower rod / wheel |1kg /1kg /0.5kg per corner |
| Gross equivalent |55kg; original V4.5 profile remains35kg chassis /45kg gross |
| Geometry / alpha |V4.5 equal300mm rods; alpha20deg;100–165deg hip range |
| Jump / drop targets |2m COM rise /2m wheel-bottom drop |
| Underside below hip / minimum clearance |50mm /50mm |
| Wheel contact |Free disc, mu0.8, zero restitution |
| Ratios |10:1,20:1,40:1; additional high-gain test2:1 |
| Shaft torque / speed |17Nm example /6000rpm no-load example |
| Gearbox output cap |250Nm example |
| Motor / gear input inertia |0.000825 /0.000100kg m² examples |
| Shaft Coulomb including cogging / viscous |0.05Nm /0.0008Nm s/rad examples |
| Shaft smoothing |0.5rad/s; narrower than the UI example's10rad/s |
| Motoring / braking / regen power |5kW /5kW /5kW examples |
| Regen acceptance / energy |Enabled /5kJ example |
| Transmission efficiency |1, isolating explicit friction without duplicated efficiency loss |
| Main dt / output / iterations |0.25ms /200Hz /120; selected repeats at0.125ms |

Spring k and reference preload scale the existing V4 chassis-support law by
`(11.25/8.75)*cos(alpha)`; the existing local mounting/route rotates with the
same mechanism transform. This is approximately gravity compensation, not exact
constant chassis force and not an added landing soft stop. Link/wheel weight is
included in dynamics, but the support scaling targets chassis mass only.

Every drive number above is an editable illustration, not a selected motor or
verified gearbox. Continuous torque, thermal duty, current/Kt compatibility,
measured torque-speed maps, bus acceptance, actual inertia and drag remain
unverified. Continuous limits are null in these captures: the2s peak-duration
field does not invent a continuous rating or reduce torque after2s. The short
terrain tests therefore do not establish sustained thermal capability.

## Actual jump and landing results

The main matrix contains52actual engine executions. Reference retains finite
rods/wheel and the same torque-speed/power limits but sets drive inertia/drag
to zero. Inertia adds both moments. Losses then adds the medium shaft drag.

| Reduction | Reference jump A / P (m) | Inertia only A / P (m) | Inertia + drag A / P (m) |
| --- | ---: | ---: | ---: |
|10:1 |0.977 /0.975 |0.820 /0.817 |0.814 /0.811 |
|20:1 |1.347 /1.347 |0.916 /0.912 |0.902 /0.898 |
|40:1 |1.013 /1.010 |0.522 /0.519 |0.500 /0.497 |

A=analytical;P=native Pymunk. None reaches the2m jump target. More reduction
does not monotonically improve jumping: available joint torque is capped while
reflected inertia/viscous drag grow with N² and available joint speed falls.

With inertia+drag, all three ratios arrest the2m landing before compression
bottom-out in both engines under this rigid model. At20:1 the main minimum
underside clearances are about667/669mm and motor removal about59/56J per
corner; friction removes about0.89/0.93J. These are first-arrest observations,
not proof of recovery, structural strength or tire survivability.

Much of the landing energy is removed during the ideal zero-restitution
collision. At20:1, the first post-contact kinetic energy is about68/64J with
drive inertia versus175/172J without it. The analytical contact account is
about211J with inertia; the native signed coupled-constraint account is about
215J and cannot be called independently measured tire absorption. Do not credit
that entire amount to the motor, friction or spring, or treat it as hardware-safe.
The PNGs show post-contact work separately from the impact and numerical accounts.

The zero-drive-inertia40:1 landing reports a bottom-out event in both engines;
the coarse native run also exceeds the numerical constraint guard and is not
scored as a resolved physical outcome. The coarse
zero-drive-inertia20:1 native run arrests but exceeds the study's1mm maximum
constraint guard at1.058mm: it remains numerically unresolved in the main plot,
rather than a false physical pass/failure. The0.125ms repeat resolves the guard
and confirms arrest in both engines. No constraint threshold was relaxed.

## Terrain: world height versus tracking error

The noiseless controller knows the actual model state and passives and has no
sensor/current delay. Its finite-gain feedback is clipped by the captured
motor torque-speed/power and gearbox limits. Acceleration follows the full
physical inertia; no arbitrary acceleration clamp is added. This is an ideal
information/actuation assumption, not mathematically perfect or optimally tuned
control. Chassis x/pitch are fixed: results concern heave, not roll/tip stability.

Main terrain assumptions are400mm/s,600mm period, seed481 and25% cycle
variation for rough cases. They are explicitly synthetic amplitude overrides,
not new values attributed to the terrain source sheet. Evaluation is the common
1.5–4.5s window,601samples, after initial lead and over two nominal periods.
Kp=5000N/m and Kd=350Ns/m in both engines.

|20:1 with inertia+drag |Tracking RMS A / P (mm) |Tracking variance A / P (mm²) |
| --- | ---: | ---: |
| Flat |0.0037 /approximately0 |approximately0 /approximately0 |
|50mm smooth bumps |2.398 /2.399 |5.689 /5.696 |
|15mm RMS seeded roughness |1.698 /1.698 |2.872 /2.873 |
|Same roughness plus5% grade |1.793 /1.792 |2.862 /2.862 |

All16main terrain cases complete the common window without compression stops,
underside contact or numerical-guard failures. Motor saturation fraction is0;
the ideal controller compensates the known drag within its available authority.
On5% grade, the reference intentionally rises20mm/s: raw world-height variance
is about305mm² while tracking-error variance is only2.86mm². The plots show
both; raw uphill rise is not labelled poor terrain rejection.

Additional150mm bumps at1.2m/s give tracking RMS about5.32/5.33mm for10:1 and
15.40/13.69mm for40:1 at the same ordinary gains, without torque saturation.
This illustrates inertia/controller tradeoffs, not a universally best ratio.

A separate same-gain high-feedback test uses Kp=1e6N/m and Kd=5000Ns/m.
At2:1, torque is limited to34Nm, saturation occupies33/34% of the1–3s window
and tracking RMS is0.91/0.87mm. At40:1, both0.125ms runs reach compression
stops with almost continuous saturation and roughly105/120mm RMS error; these
are failed tracking cases, not successful stability results. The coarse native
40:1 trace terminates at the penetration guard and is visibly incomplete.
Gains are not separately optimized for each inertia, so this is a controller
sensitivity test, not a proof of the minimum achievable error for each motor.

## Validation and reproduction

Retained evidence contains72actual runs:52main,8jump/landing half-step,
2rough-terrain half-step,4fast-terrain,4high-gain and2high-gain half-step.
Each capture includes exact request, actual frames/rows and source SHA256;
cache guards reject changed source/config/filter identities.

At20:1 with losses, halving dt changes jump rise0.9017→0.9004m analytical and
0.8980→0.8975m native. Landing residuals reduce1.095→0.547J and1.848→0.928J.
Roughness RMS changes1.6984→1.6977mm and1.6983→1.6978mm; corresponding residuals
halve0.256→0.129J and3.172→1.586J. Residuals stay labelled numerical, not physical
absorption. Rigid-impact/stop peak forces still have no finite hardware bound.

From the app folder, using its installed Python environment:

```text
python nonideal_study.py --write-config .preview/my-loss-settings.json
python nonideal_study.py --config .preview/my-loss-settings.json --output .preview/my-new-study
python nonideal_study.py --config .preview/my-loss-settings.json --dt .000125 --output .preview/my-refinement --ratio 20 --effect losses --case jump --case landing
python verify_nonideal_study.py --real
```

Edit the generated strict JSON before execution; it exposes masses, alpha,
reduction, inertia, friction, limits, terrains, controller gains and numerical
settings. Use a new app-local output folder after changing settings/source.
Requests can be submitted to the existing guarded dynamics API with their exact
`actuatorConfig`; ordinary project-v3 imports do not contain these hardware
controller limits. Saving a motor block alone does not enable a bounded ride
controller in an ordinary dynamic run. The Automatic comparison/replay panel
already captures those limits explicitly.

Raw runs/PNGs/specifications/data archives stay in ignored app folders and are
attached natively to Andy's Codex Studies in Notion. No live profile, source
app, canonical robot, shared simulation or external hardware data is rewritten.
Use [Start Kinefold.cmd](Start%20Kinefold.cmd) to restart4191.
