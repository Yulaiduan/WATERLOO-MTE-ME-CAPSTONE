# Gear reduction, real contact and chassis response

2026-10-30 experimental quarter-heave comparison, based on main `c623463`.
The owner requested floating-chassis response, a pinned-chassis force diagnostic
and a small gearbox tradeoff example. The wheel is never bound to the terrain.
These are reproducible model results, not measured motor response or vehicle limits.

## Use the new controls

In **02 Analytical** or **03 Pymunk**, choose **Terrain contact**, the
terrain/stability case, then the chassis fixture. **Floating chassis** measures
the actual ride motion. **Pinned chassis** fixes the hip height and reports the
signed force needed to hold it there, while the finite links and freely spinning
wheel continue to move, collide, slip and separate. No wheel-to-floor joint is
added. Jump, landing and the prescribed-height bench require floating chassis;
invalid edits are rejected before changing the saved design.

The pin-force plots appear in the categorized force results. Positive
`pinForceZN` means the fixture supplies upward support missing from the leg;
negative means the fixture holds down excess upward support. The inferred
chassis suspension support is `m1*g - pinForceZN`. This diagnostic does not
predict the floating trajectory: fixing the body changes the leg/contact motion
and makes the same height controller see zero body-height error.

Actuator studies also exposes optional **terrain-only floating target-height
step (mm)** and step time. Zero disables it. It changes the controller reference,
never the body position or wheel terrain height. A stationary actual-contact
floor now accepts input speed zero. Pinned chassis rejects a nonzero height step;
the all-case automatic comparison requires floating chassis and keeps pinned
tests separate. Optional fields preserve old project/capture shapes when absent.

## Three designs and common assumptions

All use ODrive M8325s 100KV and an additional ideal 2:1 gearbox-to-hip belt.
`N = gearbox ratio * hipBeltRatio`; the base gearbox ratio remains separate.

| Gearbox | Total N | Peak forward hip torque | Continuous forward hip torque | Assumed no-load hip speed | Reflected drive inertia |
| --- | ---: | ---: | ---: | ---: | ---: |
| AB90-G5-D19 | 10 | 64.41 Nm | 32.20 Nm | 480 rpm | 0.05911 kg m² |
| AB90-G10-D19 | 20 | 128.82 Nm | 64.41 Nm | 240 rpm | 0.23644 kg m² |
| AEP90-G20-D19 | 40 | 244.35 Nm | 122.18 Nm | 120 rpm | 0.94574 kg m² |

Peak forward values are torque before subtracting the separately applied drag,
at zero speed and within the 3 s peak allowance. No-load endpoints have zero
available motoring torque; they are not loaded operating speeds. Assumed reverse
efficiency 0.9 gives braking caps at 0.1 rad/s of 73.78 / 147.56 / 295.11 Nm.
The different exact gearbox SKUs have forward efficiencies .97 / .97 / .92,
so this is not a pure ratio-only comparison.

[ODrive specifications](https://docs.odriverobotics.com/v/latest/hardware/odrive-motors.html)
checked 2026-10-30 give 100KV, Kt .083 Nm/A, 80 A peak for 3 s and 40 A
continuous in free air, hence 6.64 / 3.32 Nm shaft torque. Forced-air ratings
are not used. The 48 V * 100KV = 4800 rpm envelope and plateau/rolloff shape
are explicit assumptions, not measured curves. The exact
[AB90 G5](https://www.omc-stepperonline.com/ab-series-90mm-5-1-helical-planetary-gearbox-backlash-5arcmin-for-servo-motors-ip65-ab90-g5-d19),
[AB90 G10](https://www.omc-stepperonline.com/ab-series-90mm-10-1-helical-planetary-gearbox-backlash-5arcmin-for-servo-motors-ip65-ab90-g10-d19)
and [AEP90 G20](https://www.omc-stepperonline.com/aep-series-90mm-20-1-helical-planetary-gearbox-backlash-7arcmin-for-servo-motors-ip65-aep90-g20-d19)
pages supply efficiency, torque and 6000 rpm input caps. Their 19 mm input bores
need an adapter/mount check; catalogue pairing does not establish compatibility.

The shared V4.5 geometry has 45 kg chassis / 55 kg gross, 1 kg upper and lower
uniform rods and 0.5 kg wheel per corner, alpha 20°, 65° travel, 50 mm minimum
underbody clearance and underside 50 mm below the hip. The captured V4 routed
spring preload/force scales with chassis mass and cos(alpha), with unchanged
local route; this is approximate support, not an exact gravity-compensation fit.
This study does not silently replace the selected profile's spring law.

Rotor J = .0004910893437 kg m² is a sheet geometry estimate. Missing gearbox
input-equivalent J = .0001 kg m² is assumed. Input J and viscous drag reflect
through N²; constant shaft Coulomb/cogging .05 Nm reflects through N. Shaft
viscous coefficient .0008 Nm s/rad and smoothing .5 rad/s are placeholders;
periodic cogging amplitude is zero. Listed efficiency plus explicit drag may
overlap. The extra belt is rigid, lossless and adds no mass/inertia. Reverse
efficiency .9, power limits 5 kW and regen acceptance 5 kJ remain editable.

The noiseless state-feedback controller uses the same Kp 5000 N/m and Kd
350 Ns/m for every candidate. Torque, speed, power, peak duration, reflected
inertia and drag remain active. Gains are not retuned per gearbox. Wheel contact
is rigid and unilateral, mu .8, restitution zero. Chassis x and pitch are fixed;
this is a quarter-heave test, not four-wheel body stability or roll/pitch control.

## Measured response on a stationary flat floor

At t = .1 s the desired chassis height rises by 25 or 100 mm. The chassis starts
from the same settled geometry, actual contact stays active, and no wheel-height
prescription is used. Values are analytical / Pymunk; time starts at the command.

| Total N | 25 mm 10–90% rise | 25 mm settling | 100 mm 10–90% rise | 100 mm settling | 100 mm overshoot |
| --- | ---: | ---: | ---: | ---: | ---: |
| 10 | 106.20 / 106.02 ms | 307.61 / 307.78 ms | 117.81 / 117.66 ms | 344.41 / 344.53 ms | 5.59 / 5.64% |
| 20 | 106.56 / 106.40 ms | 322.24 / 322.33 ms | 108.54 / 108.38 ms | 346.95 / 346.98 ms | 8.11 / 8.17% |
| 40 | 109.72 / 109.60 ms | 365.17 / 365.16 ms | 112.95 / 112.83 ms | 597.98 / 598.44 ms | 15.62 / 15.68% |

Settling means remaining within ±2% of the commanded displacement through the
2 s horizon, with at least .2 s final hold. This is ±.5 mm for the small step
and ±2 mm for the large step. Crossings interpolate saved samples only for the
metric, never for replay animation. All twelve step cases maintain loaded contact
and settle. These are whole-assembly closed-loop times, not intrinsic motor delay.

None of the 25 mm steps reaches its torque cap. For 100 mm, N10 saturates for
3.05% of the post-command 1.9 s window (~58 ms), N20 for 1.05% (~20 ms), and
N40 for 0%. Peak forward joint demand reaches 64.41 / 128.82 / 199.6 Nm.
Thus 20:1 helps the larger move by avoiding some clipping, while 40:1 brings
more reflected inertia and overshoot under the same gains. A gain-tuned hardware
comparison could change the ranking; the small step alone cannot reveal this tradeoff.

## Terrain response versus forward speed

One seeded roughness proxy: 15 mm RMS, 600 mm nominal period, 25% cycle
variation, seed 481, zero grade. Each speed traverses the exact same 1.8 m strip,
after a .2 m spatial lead; metrics evaluate .6–1.8 m. The spatial contour,
phase and complete request are checked, so increased speed shortens the available
response time rather than changing the terrain realization.

| Total N | RMS at 3 m/s, A / P | Loaded contact at 3 m/s, A / P | Highest passing tested speed | Next tested failure |
| --- | ---: | ---: | ---: | --- |
| 10 | .946 / .952 mm | 100 / 100% | 4 m/s | 6 m/s: contact |
| 20 | 1.873 / 1.882 mm | 100 / 100% | 3 m/s | 4 m/s: contact |
| 40 | 5.257 / 5.271 mm | 90.5 / 86.5% | 1 m/s | 3 m/s: contact and RMS |

The four tested speeds are 1, 3, 4, 6 m/s. Passing requires RMS ≤5 mm,
loaded-contact fraction ≥99%, travel reserve ≥2°, clearance ≥50 mm, no physical
stop, a complete window and numerically resolved output. These thresholds are
editable choices, not uncertainty bounds. No interpolation to a true maximum,
safe travel speed or globally optimal gear ratio is claimed.

Loaded-contact fraction counts saved output intervals with a positive compressive
normal impulse. It is sensitive near the threshold to discrete rigid-contact
resolution; it does not certify continuous tire loading. N20 at 4 m/s records
98.67 / 96.67% loaded intervals. At 6 m/s it is only 36 / 37%, and its maximum
actual wheel gap is about 20 mm: contact loss is real even though chassis RMS
remains only ~1.88 mm. Low body motion while airborne is not good tracking.
No terrain run reaches its torque cap. Here more peak Nm does not repair the
inertia/contact/controller response limit.

## Pinned-chassis diagnostic

At 3 m/s, signed pin-force RMS is 16.08 / 16.27 N for N10, 39.54 / 39.61 N
for N20, and 137.86 / 138.74 N for N40. Pre-terrain mean is within .001 N of
zero after the holding-torque fix below. N40 also loses contact; fixed chassis
height must not be interpreted as successful ride control.

The interval-average fixture impulse is independently reconstructed from the
whole modeled assembly's vertical momentum:

`I_pin = delta(P_z) + M_total*g*dt - I_external,z - I_ground,z`

`pinForceZN = I_pin/dt`, with positive z upward. Native Pymunk uses a world
PivotJoint on the chassis; analytical contact uses the constrained mass inverse
with hip height fixed throughout the solve. Neither pins the wheel. Ideal fixture
work is zero. Initial force is unavailable at t=0; baseline change uses the
first finite interval rather than inventing an initial force. Reaction spikes
are sampled interval means, not verified impact/structure peak loads.

## Validation and a corrected holding-torque edge case

Initial trials exposed an actuator bug: roundoff-sized positive joint speed
could classify a negative static holding command as braking, while the existing
near-zero shaft-speed guard then zeroed the available torque. This intermittently
dropped the analytical holding command and produced a false 3–5 N pin bias.
Below the existing 1e-12 shaft-speed cutoff, torque now uses the conservative
holding conversion; braking classification requires speed above that cutoff.
Regen, power, peak-duration and contact guards are unchanged. A realistic
finite-link, spring and hardware-capped flat-floor regression now passes both
engines with pin magnitude <.02 N. Earlier 42 preliminary executions are
superseded, retained separately and excluded from the final figures/archive.

Final evidence is 50 fresh executions: 36 base, 4 half-step pin/small-step,
4 half-step 4 m/s threshold checks and 6 large-step runs. All resolve. All 25
engine pairs have identical requests except engine, current source hashes and
recomputed raw metrics. Halving dt from .00025 to .000125 s preserves N10 pass /
N20 fail at 4 m/s. N20 small-step rise becomes 106.67 / 106.59 ms and settling
322.49 / 322.54 ms. Six actual localhost HTTP runs reproduce exact saved metrics
and settings for pinned, step and floating cases in both engines.

Focused Python tests cover constrained contact, signed pin budgets, free spin /
separation, near-rest holding, regen limits, optional-key compatibility, exact
spatial input, weighted metrics and speed classifications. JS checks cover
transactional invalid edits, persistence, Plotly pin groups and paired rendering.
No live pointer/browser, hardware, thermal, tire deformation, full-body stability,
GPU or canonical robot validation is implied.

## Reproduce and retain only a small example

From this app with its setup environment:

```powershell
.\.venv\Scripts\python.exe gear_response_study.py --write-config .preview/gear-response.json
.\.venv\Scripts\python.exe gear_response_study.py --config .preview/gear-response.json --output .preview/gear-response-new
.\.venv\Scripts\python.exe verify_pinned_contact.py
.\.venv\Scripts\python.exe verify_gear_response_study.py
node verify-pinned-ui.cjs
```

Use a fresh app-local output folder. Filters allow candidate, case, speed, engine
and dt refinements. To repeat the large step, change `heightStepMm` to 100 in a
new config and select `--case height-step`. A base run is capped at 36 executions.
Exact requests/settings/summary CSV remain for all designs; raw captures are
limited to one worked N20 design. Source/config guards reject incompatible resumes.

Six Plotly PNGs, three paired actual-frame GIFs and a compact settings/data ZIP
are in ignored `exports/`, with native attachments on
[Andy's Codex Studies](https://www.notion.so/402b26c7416c8167b41cdb20705fecd6).
GIFs use one clock/camera, actual terrain translation, +x left / +z up, 1× physical
time and a labelled .5 s final reading pause. Temporary frame caches are removed.
Raw/media are not committed and never sent to Downloads. The live profile library
is preserved; this runner uses portable saved baseline inputs rather than editing it.

## High-variance follow-up — 2026-10-30

Owner requested a rougher case to expose leg lag. Same ODrive/AB90-G10/B2
(total20), alpha20°, masses, approximate spring support, controller, seed481,
600mm period,25% cycle variation and3m/s; only nominal terrain RMS changes
15→60mm. The amplitude is4× and variance16× for the same generated cells.
Realized full-cell mean-removed RMS is59.09mm and peak184.86mm; these are not
wheel-path-window statistics. Four new actual runs: two engines at dt.00025
and a matched pair at dt.000125, all numerically resolved through.6s.

| Metric, .2–.6s common window | Analytical | Pymunk |
| --- | ---: | ---: |
| Chassis RMS height error | 6.195mm | 6.131mm |
| Peak absolute chassis error | 9.684mm | 9.778mm |
| Peak angle error versus level-body geometry | 3.823° | 3.902° |
| Maximum actual wheel gap | 6.694mm | 6.543mm |
| Loaded-contact intervals | 76% | 73% |
| Motor torque saturation | 0% | 0% |

The geometry reference solves `min circle-to-contour gap(q,h_target,t)=0`
inside the exact leg travel, including alpha, lateral wheel shift and finite
wheel radius. It is an offline diagnostic, not a joint command or wheel pin.
Positive angle error on the descending face means the leg has insufficient
extension to keep the chassis level. The first descent crosses140° about
6.211/6.140ms after the reference; interpolation uses2ms output samples.
Half-step results are6.191/6.212ms, with chassis RMS6.144/6.119mm and contact
75.5/74.5%. The case fails the original ride/contact criteria, without reaching
the motor cap. It shows coupled inertia/controller/contact response, not a
pure motor delay. Crest delays differ between bumps and whole-window correlation
does not establish a constant phase lag. The mild baseline's RMS was1.873/1.882mm.

Reproduce using the existing runner: generate a fresh config, set terrain.rmsMm=60
and retainFloatingSpeedsMps=[3], then select `--candidate gear-10 --case
floating-terrain --speed 3`; repeat in a fresh folder with `--dt .000125`.
The two final Plotly PNGs, one actual paired GIF and exact settings/raw/reference
CSV/scripts ZIP are app-local ignored exports and native Notion attachments.
Source hashes, requests, stored metrics and tangency residuals(<1e-7mm) pass;
no physics laws, UI settings or live profiles are changed by this follow-up.
Use25fps for the reviewed GIF:16frames,.6s physical time plus.5s final pause,
1100ms total. An initial30fps export quantized18 intervals to540ms rather than
600ms in GIF's10ms clock; it is superseded and excluded from delivery. Initial
plot footer/legend overlap was corrected before attachment. No GUI, hardware,
thermal, impact-strength or full-body stability validation is implied.

## Alpha-zero exaggerated response — 2026-10-31

Owner requested alpha0 and much greater inertia/friction to make lift-off
visible. Keep the same ODrive N20,60mm nominal terrain RMS,600mm period,3m/s,
seed481,25% cycle variation,masses and controller. Run a fresh normal alpha0
pair and an explicitly exaggerated pair, plus a half-step exaggerated pair:
six actual runs, all numerically resolved. Neither chassis nor wheel is pinned.

| Assumption | Normal | Exaggerated demonstration |
| --- | ---: | ---: |
| Gearbox input-equivalent J | .0001 kg m² | .01 kg m² |
| Total reflected drive J at hip | .236436 kg m² | 4.196436 kg m² (17.75×) |
| Shaft Coulomb/cogging | .05 Nm | .5 Nm (10×) |
| Shaft viscous coefficient | .0008 Nm s/rad | .016 Nm s/rad (20×) |

Motor rotor J,gear ratio/B2 and motor torque limits are unchanged. These large
gear-inertia/drag substitutions are artificial teaching inputs, not ODrive or
AB90 specifications. The source routed-spring model and its existing alpha
support scaling are reevaluated at0° for both normal and exaggerated runs.

Normal alpha0 already has49.31/57.04mm maximum wheel gap (A/P), chassis RMS
3.330/3.412mm,loaded intervals59/58%,no motor clipping or end-stop event. The
exaggerated case reaches313.26/313.33mm gap at t=.330s; chassis RMS is
106.73/106.19mm and peak height error147.00/146.68mm. It hits the compression
stop at.30660/.30700s and is torque limited77.5/83.0% of the.2–.6s window.
Loaded intervals are only1/1% in that window. This is an extreme failure
illustration: the incoming bump kicks the chassis upward, and the leg cannot
recover the required pose; the stop and saturation are retained, not hidden.
It is not a clean pure-delay experiment or a realistic motor prediction.

Half-step dt.000125 gives312.65/312.94mm peak gap, chassis RMS106.26/106.14mm
and compression stop.30676/.30675s. The large lift-off survives refinement;
individual stop-interval torques/contact fractions still depend on discrete
constraint resolution. Source hashes, exact paired settings, recomputed metrics,
free-wheel flags and offline circle/contour reference residuals pass. No guards
were relaxed. Native maximum position residual reduces.144→.072mm with dt;
maximum native penetration reduces.828→.548mm. No hardware certification.

An actual peak-gap PNG at.330s and a0.25× slow replay make the separation clear.
All poses remain actual saved states; the presentation wrapper changes only
labels/gap readout and adds the real peak timestamp. The17-frame GIF represents
.6s physics as2.4s playback plus a labelled.5s final pause=2900ms, with cumulative
10ms clock rounding. Original engine captures and app renderer are unchanged;
wrapper/executed-renderer/encoder hashes are retained. One Plotly normal/stress
comparison, peak PNG,GIF and compact exact-data/scripts ZIP are app-local and
native Notion attachments. The final encoder takes an installed Sharp path as
an explicit CLI argument; an earlier media export is superseded. No GUI or live
profile edits were used. Repeat with alphaDeg0 in the previous high-variance
config, then the three exaggerated shared values above, using fresh output
folders and the existing gear-10/floating-terrain/3mps filter.

Restart at <http://127.0.0.1:4191/?tab=analytical> with
[Start Kinefold.cmd](Start%20Kinefold.cmd); stop with
[Stop Kinefold.cmd](Stop%20Kinefold.cmd). The launcher is verified from an unrelated
working directory, including stop/start and repeated-launch reuse.
