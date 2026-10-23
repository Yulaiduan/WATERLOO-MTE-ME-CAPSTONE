# Energy-only drop height to braking torque

Andy Zhang / Codex, 2026-10-23. Experimental chassis-only work screen, not a
trajectory integration, peak rating, hardware test or post-arrest guarantee.

Open **Energy only · drop height → braking torque** in either dynamic tab.
It calculates immediately in the browser from the same saved mechanism, spring
and optional motor profile, including the original massless-wheel V4 baseline.
It works independently of terrain/prescribed mode and requires no dynamics run.

The live equation table is visible directly inside the calculator, above its
Plotly chart. It lists each quantity, equation/source, numerical value and unit,
including positive spring/cogging storage and the resulting joint/shaft torque.
Edit the height, clearance, stop reserve and available torque above the table;
mass, gravity and spring geometry come from the saved mechanism. **2 m drop
example** changes only the calculator drop height to2000mm, preserving the
mechanism, landing geometry and dynamic controller commands.

The default **50mm residual underbody-to-ground clearance** is different from
**50mm underside offset below hip A**. The former is the requested remaining
ground gap; the latter defines where the chassis underside is relative to A.
An explicit editable1° compression-stop reserve is an illustrative margin.
Zero reserve allows a clearly labeled mechanical-boundary calculation.

## Geometry and work

The saved landing opening fraction f gives
`q0 = tc + f*(te−tc)` (default f=2/3). With the wheel centre held at radius above
stationary flat ground, hip height is `h(q)=rw−Cz(q)` and underbody clearance is
`h(q)−undersideOffset`. The selected endpoint is the earlier of `tc−reserve`
and the target-clearance crossing on monotonic compression.

Using radians for Δq and metres for height, define:

- Drop energy: `K0=m1*g*H=½*m1*v²`, with `v=sqrt(2*g*H)`.
- Gravity released in compression: `G=m1*g*(h0−hend)`.
- Spring released: `S=Uspring(q0)−Uspring(qend)`; negative means absorbed.
- Cogging released: `C=Ucog(q0)−Ucog(qend)` with the fixed motor phase.
- Constant joint resisting magnitude: `τ=max(0,(K0+G+S+C)/Δq)`.
- Motor-shaft resisting magnitude: `τ/N` for active ideal reduction N.

Compression increases q, so the corresponding braking command is **negative**.
Available torque in this calculator is always **joint-side**, independent of the
dynamic command-basis setting. No controller input is automatically changed.

The inverse endpoint drop capacity is
`Hcap=(τavailable*Δq−G−S−C)/(m1*g)`.
A negative value is reported unavailable rather than silently clipped to zero.
This is a sufficient selected-endpoint work screen, not the true global maximum
over intermediate spring/cogging barriers. It assesses initial arrest only;
rebound and holding after arrest still need a controller/trajectory assessment.

For the V4 baseline with H=100mm and1° reserve, q0=121.666667°, qend=164°,
end clearance315.382413mm and Δq=.738856050rad. The spring absorbs29.644002342J,
compression gravity supplies29.638623504J and the drop supplies8.58375J.
The resulting resisting magnitude is11.6103416383Nm;20Nm gives172.214939136mm
endpoint capacity. With the spring disabled the same screen requires51.7318271992Nm.
Here the mechanical reserve limits travel well before the50mm clearance target.

For the same baseline at **H=2000mm**, the drop supplies171.675J. Compression
gravity supplies29.638623504J and the spring stores29.644002342J, leaving
171.669621162J for the motor over0.738856050rad. Required constant hip braking
magnitude is **232.345151887Nm**. Ideal shaft demand is that value divided by
reduction N; it is not a transient peak, continuous rating or hardware-survival
claim. The arrest endpoint remains315.382413mm above ground because the stop
reserve, rather than the50mm residual-clearance target, limits usable travel.

## Assumptions and storage

### Peak motor and gearbox screening

An optional saved `energyConfig.screening` compares a selected motor/reduction
against this same work calculation. Manual mode omits this block and retains
the existing editable available joint torque. Selecting a catalog component
does not edit `motorConfig`, controller commands or captured dynamic results.
Motor choices use these transcribed maximum/peak shaft ratings (2026-10-23
catalog snapshot); no continuous rating or measured braking capability is implied:

| Flipsky motor | Peak shaft torque (Nm) |
| --- | ---: |
| 6374 190KV | 8 |
| 6384 170KV Battle Hardened | 9 |
| 6354 140KV Battle Hardened | 7 |
| 6384 140KV | 9 |
| 6374 140KV Battle Hardened | 8 |
| 7070 110KV Battle Hardened | 9.5 |
| 6368 140KV Battle Hardened | 5 |
| 63100 140KV Battle Hardened | 10 |
| 80100 130KV | 17 |

The63100 source specifies maximum torque for at most30s. Other peak durations
are unspecified in this snapshot. An edited peak value is an explicit override.
No candidate inertia, cogging or friction value is inferred from these ratings.

| EG23 gearbox | Reduction N | Nominal output (Nm) | Momentary output (Nm) | Listed forward efficiency |
| --- | ---: | ---: | ---: | ---: |
| EG23-G5-D10 | 5 | 28 | 56 | 96% |
| EG23-G10-D10 | 10 | 10 | 20 | 96% |
| EG23-G20-D10 | 20 | 30 | 60 | 94% |
| EG23-G50-D10 | 50 | 25 | 50 | 94% |

Sale20:1 and used50:1 listings are the same mechanical models and are deduplicated.
The unusual10:1 torque rating is retained exactly, not interpolated. The family
table calls the first output rating nominal, while product pages call it maximum
permissible. Momentary duration and a suitable BLDC shaft/adapter are unverified.

For ideal screening, `motorJointPeak = N*peakShaft` and
`effectiveJoint = min(motorJointPeak, gearboxMomentary)`. Direct drive has N=1
and no gearbox limit. Custom reduction supports a separate joint-side momentary
limit; blank means unassessed and prevents an overall pass. Nominal output is
shown separately. Forward efficiency is reference data only: it does not establish
backdrive behavior and is not applied as a braking-energy credit.

Candidate N also changes cogging phase in the temporary work calculation when
the saved passive motor model is enabled; the saved amplitude/period/phase are
explicitly retained as assumptions. Disabled passives stay zero. The candidate
does not infer the selected Flipsky motor's cogging waveform. All result cards,
shaft conversions and the curve use this same candidate calculation.
The separate dynamic-case landing work estimate always uses the actual saved
motor reduction/cogging through `landingEstimate`; catalog selections do not
change the guidance next to the simulation target search.

At the2m baseline, all four listed gearboxes fail their momentary-output screen:
even the largest limit60Nm is below232.345Nm. A motor's ideal geared torque can
exceed demand while the gearbox still fails. Neither a catalog-screen pass nor
the energy balance certifies motor/controller regenerative braking, DC-bus energy
handling, impact peaks, temperature, strength or post-arrest holding.

Public product references: Flipsky
[6384](https://flipsky.net/products/flipsky-bldc-belt-motor-battle-hardened-6384-140kv-170kv-190kv-4000w-for-electric-skateboard),
[6354](https://flipsky.net/collections/motor/products/flipsky-bldc-belt-motor-battle-hardened-6354-140kv-190kv-2450w-for-electric-skateboard),
[6374 Battle Hardened](https://flipsky.net/collections/motor/products/flipsky-bldc-belt-motor-battle-hardened-6374-140kv-170kv-190kv-3500w-for-electric-skateboard),
[7070](https://flipsky.net/collections/motor/products/flipsky-sensored-outrunner-brushless-dc-motor-battle-hardened-7070-110kv-140kv-170kv-4200w),
[6368](https://flipsky.net/collections/motor/products/flipsky-sensored-brushless-dc-motor-battle-hardened-6368-140kv-170kv-190kv-2700w-for-electric-skateboard),
[63100](https://flipsky.net/products/flipsky-sensored-outrunner-brushless-dc-motor-battle-hardened-63100-140kv-170kv-190kv-5500w),
[80100](https://flipsky.net/products/brushless-dc-motor-80100-130kv-7000w-for-electric-bike-electric-skateboard-go-cart)
and the [EG23 family](https://www.omc-stepperonline.com/nema-23-eg-series-planetary-gearbox).
The6374 190KV8Nm value is a marketplace specification snapshot and is distinct
from the6374 140KV winding. These are source links, not new stock/price checks;
private workbook URLs and unrelated spreadsheet data are not bundled in the app.

### Model scope and persistence

This screen retains the full chassis m1*g*H without impact-loss credit. Wheel
impact energy is excluded. Rotor starts/ends at rest, so its endpoint kinetic
change is zero; inertia still changes actual impact trajectories and peaks.
Motor/joint friction is given no energy credit. The path must be vertical and
straight (equal links,2:1 guide), with massless moving links/compound pulley,
positive m1/g, no extra prescribed loads and a valid spring cable route.
Unsupported geometry, slack recovery or unavailable stroke is shown explicitly.

Optional saved `energyConfig` holds drop height, clearance target, stop reserve
and available joint torque. Old profiles remain unchanged until edited; Remove
calculator block restores absence. Shared opening/underside controls explicitly
edit the landing case geometry. Energy-only settings do not stale physical
simulation results or alter their engine hashes. Full project and calculation
JSON exports stay inside the app exports/ folder.

The work relation is the rotational work–energy theorem, with constant resisting
work τΔq; see [OpenStax University Physics10.8](https://openstax.org/books/university-physics-volume-1/pages/10-8-work-and-power-for-rotational-motion).
Source spring geometry/energy remains the unchanged V4 reference, and geared
cogging potential follows [motor-model.md](motor-model.md).
