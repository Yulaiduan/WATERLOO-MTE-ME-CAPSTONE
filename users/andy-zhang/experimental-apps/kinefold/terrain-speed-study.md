# Terrain speed and added hip belt

Andy Zhang / Codex, 2026-10-30. Experimental quarter-heave study based on
main `aca73a1`; these are model results, not hardware or full-vehicle validation.

The owner requested faster terrain and an ODrive8325 example with an additional
configurable gearbox-to-hip belt. The app now accepts `hipBeltRatio` B=1..3 in
dynamic motor settings, saved actuator presets, automatic comparison assumptions
and the independent actuator calculator. Missing B retains1 and the original
snapshot's key shape. Select the motor, exact gearbox and B in Actuator studies,
capture a new study, then replay its paired case. Ordinary dynamic motor fields
add inertia/losses but do not automatically enable a hardware-limited controller.
Old captures keep their historical settings; changing B requires a new run.

## Reduction and hardware

Base `gearRatio` / captured actuator `ratio` denotes the gearbox alone.
`N = Ngear × B`; B2 means two gearbox-output turns per hip turn. Motor speed,
shaft-to-joint torque and Coulomb resistance use N; motor plus gearbox-input
inertia and viscous coefficient reflect through N². Additional hip-side inertia
is not reflected again. Gearbox source torque caps multiply B at the hip, and
its output-speed cap is checked at B times hip speed. Existing carrier belts,
spring geometry and builder dimensions are unaffected. See [motor equations](motor-model.md).

This example uses the same AB90-G10-D19 gearbox for both ODriveM8325s100KV and
Flipsky80100130KV, followed by B2: total20:1. The extra belt is assumed ideal,
rigid, lossless and massless; dimensions, mounting, compliance and strength are
unknown. No pulley layout is invented. The gearbox19mm input bore requires a
separately checked shaft adapter/mount; catalogue pairing does not prove fit.

[ODrive specifications](https://docs.odriverobotics.com/v/latest/hardware/odrive-motors.html)
checked2026-10-30 give100KV, Kt=.083Nm/A,80A peak for3s and40A continuous in free
air:6.64Nm peak and3.32Nm continuous. Current is phase amplitude. Forced-air60A
is not used. This example uses an explicitly assumed4800rpm ideal100KV×48V
no-load envelope, not a measured loaded curve or a selected controller's voltage
limit. The source approximate plateau/rolloff shape remains the captured model.
The Flipsky envelope is6240rpm=130KV×48V, with the gearbox6000rpm input cap.
Listed [AB90 gearbox](https://www.omc-stepperonline.com/ab-series-90mm-10-1-helical-planetary-gearbox-backlash-5arcmin-for-servo-motors-ip65-ab90-g10-d19)
limits remain100Nm nominal/300Nm momentary and efficiency.97, before the belt.

At rest the ODrive motoring cap is6.64×20×.97=128.816Nm at the hip. During
backdriven braking the assumed reverse efficiency.9 gives6.64×20/.9=147.556Nm;
the difference is gearbox dissipation, not free extra shaft power. Source motor
rotor inertia is a sheet geometry estimate,.000491089kgm²; gearbox input-equivalent
J=.0001kgm² is assumed. Reflected driveJ=.236436kgm², versus.370011 for the
Flipsky example. Shaft Coulomb/cogging=.05Nm constant resistance, viscous=.0008Nms/rad,
smoothing=.5rad/s and periodic cogging amplitude0. Listed efficiency and explicit
drag may overlap; they are not a calibrated loss map. Power/regen5kW and5kJ
acceptance remain placeholders. Controller, thermal duty, measured drive inertia,
losses and belt hardware are still missing inputs.

## Fair speed comparison

Only two motors and one gearbox are evaluated:16 terrain runs plus the ODrive
jump/landing pairs,20 runs total. Six additional ODrive timestep-refinement runs
check3m/s terrain, jump and landing. No catalogue-wide search or optimization.

All cases use45kg chassis/55kg gross,1kg upper and lower uniform rods and.5kg
wheel per corner, alpha20deg and65deg mechanical travel. Jump target/drop gap2m;
minimum underbody clearance50mm, underside50mm below hip. Landing starts fully
open to use the full65deg, as in the preceding controlled comparison. V4 routed
spring force/preload scale with chassis mass and cos(alpha), with unchanged local
route; this remains approximate gravity support, not exact cancellation.
Chassis motion is vertical only; the wheel spins freely against rigid frictional
terrain (mu.8, zero bounce). The same noiseless finite-gain feedback Kp5000N/m,
Kd350Ns/m uses actual state and is limited by motor torque/speed/power and inertia.

The terrain is one seeded15mm-RMS roughness proxy,600mm nominal period,
25% cycle variation, seed481, zero grade. Every speed traverses the identical1.8m
strip after the same.2m spatial lead; contour, cycle count, seed and phase are
checked. Duration=1.8/v and input delay=.2/v seconds. Metrics cover.6–1.8m at
every speed. Continuous statistics integrate piecewise-linear output samples
with true time weighting; contact/saturation fractions use time-weighted left-held
sample states. Metric interpolation never changes physics or animation frames.
Fast runs have less elapsed settling time; this is a finite-distance test, not
a statistically converged terrain endurance result.

| Speed (m/s) | Half-cycle time (ms) | ODrive RMS A / P (mm) | Flipsky RMS A / P (mm) |
| --- | --- | --- | --- |
| .4 | 750 | 1.688 / 1.688 | 1.698 / 1.698 |
| 1 | 300 | 1.747 / 1.750 | 1.880 / 1.884 |
| 2 | 150 | 1.859 / 1.868 | 2.454 / 2.466 |
| 3 | 100 | 1.869 / 1.879 | 2.593 / 2.605 |

A=analytical, P=Pymunk. All16 complete the common spatial window with no observed
contact loss, torque saturation or travel-stop event. ODrive sampled hip torque
at3m/s peaks around18.24Nm and shaft speed around414rpm, far below the assumed
4800rpm ceiling. These mild cases therefore expose tracking/inertia response,
not the maximum traversable speed. ODrive's lower estimated reflected inertia
is consistent with better tracking here; this is not proof of an optimal motor.
For an identical smooth spatial motion, speed scales velocity by v and required
acceleration by v². Corners/impacts do not have finite acceleration peaks in the
rigid idealization. These heave results do not assess pitch, roll or tipping.

## ODrive jumping, landing and numerical sensitivity

The2m jump target yields COM rise above takeoff.501876/.499394m (A/P), so the
target is not reached. Both2m landing runs arrest before bottom-out; observed
minimum clearance through first arrest is568.2/561.3mm. This is a first-arrest
assessment, not sustained recovery or impact-strength certification. The rigid
contact model removes substantial impact energy: analytical first contact loses
about184.7J per corner, while subsequent motor braking removes73.6J. Do not
interpret this landing outcome as the motor absorbing all drop energy or as a
hardware survival claim; compliant tire/structure absorption remains unknown.

Base dt=.25ms, output200Hz,120 native iterations. At dt=.125ms, ODrive3m/s RMS
becomes1.870735/1.875053mm, jump.501387/.499362m, and landing minimum
clearance570.1/562.0mm. Classifications are unchanged. Remaining landing
engine clearance difference is about8.2mm; agreement is not exact. Energy-ledger
residual magnitudes decrease: terrain.0374/.5174→.0197/.2586J,
jump1.5735/1.9513→.7843/.5104J, landing1.4130/2.7685→.7035/1.3956J.
Residuals remain numerical, never spring/motor absorption.

Four paired saved GIFs replay actual ODrive frames at1× physical time, one common
clock/camera, +x left/+z up, real horizontal terrain offset and wheel indices.
They span4.5/1.8/.9/.6s for.4/1/2/3m/s with a labelled.5s final reading pause.
There is no frame interpolation or seamless-physics claim across GIF loops.
Plotly PNGs, GIFs and a compact data ZIP are app-local ignored exports, attached
natively to Andy's Codex Studies in Notion. Raw frames are retained only for the
ODrive cases; every case keeps its exact request/metrics/source fingerprints.

## Reproduce and validate

From this app root, using its installed physics Python:

```text
python terrain_speed_study.py --write-config .preview/my-speed-settings.json
python terrain_speed_study.py --config .preview/my-speed-settings.json --output .preview/my-speed-run
python terrain_speed_study.py --config .preview/my-speed-settings.json --dt .000125 --candidate odrive-8325 --speed 3 --output .preview/my-speed-refinement
python verify_hip_belt.py
python verify_terrain_speed_study.py
```

Edit the strict generated settings before running; changed source/settings require
a fresh output folder. Legacy B1 and new B2 physics transformations, upstream
gearbox caps and finite-engine equivalence are checked. All26 actual source/config
identities and13 exact engine pairs pass. The live4191 HTTP engines reproduce the
saved3m/s B2 case deterministically; actual landing/jump/terrain captures pass the
existing synchronized replay/mirror DOM fixture. GUI/browser pointer operation,
hardware, full-body dynamics and GPU performance are not verified. Live profile
library is unchanged. Restart with [Start Kinefold.cmd](Start%20Kinefold.cmd).
