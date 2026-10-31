# ODrive8325 gearing for a1.5m drop

Andy Zhang with Codex,2026-10-31. Experimental recommendation based on source
commit59e658a,not a global hardware optimum or verified drop-survival rating.

## Recommended starting combination

**ODrive M8325s100KV + HTG90-G20 +1.6:1 gearbox-to-hip belt =32:1 total.**
This is the lowest practical tested ratio satisfying the declared10% endpoint
work-reserve rule while passing both rigid-contact landing models, a half-step
check and a lower assumed motor-speed-envelope check. It is landing-focused;
terrain/jumping performance is not optimized or rerun here. The final belt is
ideal in this model; pulley packaging, belt strength and an ODrive rotor-to-19mm
gearbox-input adapter still require design. No named live design is overwritten.

| Quantity | Selected32:1 |
| --- | ---: |
| Peak forward hip torque,η=.97 | 206.11Nm |
| Braking hip torque with no gearbox-loss credit | 212.48Nm |
| Model braking cap at low speed,assumed reverseη=.9 | 236.09Nm |
| Free-air continuous forward hip torque | 103.05Nm |
| Assumed no-load hip speed,4800rpm shaft | 150rpm |
| Reflected drive inertia,estimated/assumed | .60528kgm² |
| Conservative endpoint work reserve | 13.19% |

Compared with40:1,the selected ratio has36% less N²-reflected drive inertia
and25% greater assumed no-load joint speed. Those relations do not establish a
measured acceleration or loaded-speed rating. The catalogue's gearbox inertia
is missing,so this is not a calibrated inertia ranking between product families.

## Selection scope and primary specifications

The existing157-row SO catalogue was screened algebraically,not simulated
exhaustively. At N32 and allowed final belt1..3,eight source rows have known
efficiency and enough stated gearbox peak/nominal torque for the assumed motor
caps; some are sale/used/shaft variants of the same product. Unknown ratings
remain unassessed. Five choices received actual runs: AB90-G10+B2(N20),
AB90-G10+B3(N30),HTG90-G20+B1.6(N32),AEP90-G20+B1.6(N32),HTG90-G20+B2(N40).

[ODrive specifications](https://docs.odriverobotics.com/v/latest/hardware/odrive-motors.html)
checked2026-10-31 give M8325s100KV,Kt.083Nm/A,80A peak for3s and40A free-air
continuous:6.64/3.32Nm shaft torque. The selected controller's actual voltage,
current and modulation limit are not established.4800rpm is an assumed48V
envelope;3600rpm is a sensitivity check,not a second manufacturer rating.

[HTG90-G20](https://www.omc-stepperonline.com/htg-series-90mm-20-1-helical-planetary-gearbox-backlash-5arcmin-for-servo-motors-ip65-htg90-g20)
and its [datasheet](https://files.omc-stepperonline.com/HTG90-G20_Full_Datasheet.pdf)
state20:1,97% efficiency,112Nm nominal permissible/224Nm momentary torque,
6000rpm maximum input,19mm input bore and141mm length. Its nominal torque
margin and forward efficiency favor it over the tested AEP90-G20's75Nm/92%.
Both N32 minimum-clearance/peak-speed results are tied here: the assumed reverse efficiency and drive
J are the same,gearbox torque caps do not bind,and mass is held fixed.
HTG's true mass/J are missing; no purchase-ready mounting or global superiority
claim follows. The source112/224Nm gearbox caps act before the1.6 belt.

Other exact source pages checked:
[AB90-G10](https://www.omc-stepperonline.com/ab-series-90mm-10-1-helical-planetary-gearbox-backlash-5arcmin-for-servo-motors-ip65-ab90-g10-d19),
[AEP90-G20](https://www.omc-stepperonline.com/aep-series-90mm-20-1-helical-planetary-gearbox-backlash-7arcmin-for-servo-motors-ip65-aep90-g20).
The [AB90 datasheet](https://files.omc-stepperonline.com/AB90-G10-D19_Full_Datasheet.pdf)
also states3.7kg mass; the fixed45kg chassis budget must include the actual
chosen transmissions. HTG mass/packaging are not inferred from AB90.

## Design assumptions and energy criterion

Same V4.5 geometry:45kg chassis plus four sets of1kg upper link,1kg lower link
and.5kg wheel =55kg gross. Alpha0°,wheel-bottom drop1.5m,initial leg fully open
at100°,compression stop165°,50mm minimum underside clearance and underside50mm
below hip. Use2° compression-stop reserve for the energy screen:100→163°,
63°=1.099557rad. The mechanical stop has
305.29mm underside clearance,so the50mm threshold does not grant extra stroke.
Changing the landing opening fraction changes this recommendation; the older
two-thirds-open pose has less braking travel and must be recalculated.

Per quarter,Mq=13.75kg. Keep all moving-body drop energy and the exact grounded
gravity/spring endpoint changes:

```text
E_drop = Mq*g*h =202.331J
E_req  = E_drop + Ug(q0)-Ug(q1) + Us(q0)-Us(q1) =206.403J
tau_average = E_req / (q1-q0) =187.715Nm
W_no_loss =6.64*N*(q1-q0)
N_min_for_10pct_reserve =1.10*E_req/[6.64*(q1-q0)] =31.097
```

The10% work reserve and2° stop reserve are explicit engineering assumptions,
not certified safety factors. This screen credits neither unknown impact
absorption,nor Coulomb/viscous help,nor reverse gearbox dissipation. It is a
necessary endpoint-work condition,not proof that a finite torque-speed curve
can absorb every possible transient. Actual finite-link/contact runs assess the
captured controller separately,under the rigid-impact qualification below.

Normal assumed shaft Coulomb/cogging=.05Nm,viscous=.0008Nms/rad,smoothing=.5rad/s,
periodic cogging0. Rotor J=.0004910893437kgm² is estimated; gearbox input-equivalent
J=.0001kgm² is assumed,additional hip J0. Jref=N²(Jmotor+Jgear). The extra belt
has no added compliance,mass,inertia or loss. Source forward efficiency plus
explicit drag may overlap. Reverseη=.9,per-actuator5kW motoring/braking and5kJ
regen acceptance are placeholders. The V4 routed coil's existing mass/alpha
scaling is retained as approximate support,not exact gravity compensation.
The exaggerated17.75×J/drag demonstration is not used.

## Actual bounded comparison

| Choice | No-loss work reserve | Drive J kgm² | Assumed no-load hip rpm | Minimum clearance A/P |
| --- | ---: | ---: | ---: | ---: |
| AB90-G10 ×2 =20 | −29.25% | .23644 | 240 | 655.73/658.66mm |
| AB90-G10 ×3 =30 | 6.12% | .53198 | 160 | 718.38/718.53mm |
| HTG90-G20 ×1.6 =32 | 13.19% | .60528 | 150 | 722.74/722.83mm |
| AEP90-G20 ×1.6 =32 | 13.19% | .60528 | 150 | 722.74/722.83mm |
| HTG90-G20 ×2 =40 | 41.49% | .94574 | 120 | 731.94/731.94mm |

All ten base executions pass the model's arrest,at least.5s post-arrest
observation,whole-run clearance,no compression stop and known source speed
checks. This is why clearance alone is insufficient for selecting the ratio:
N20 passes the rigid model despite failing the endpoint-work rule. No loaded
terrain speed or jump target is certified by this landing table.

Four selected-case refinements/sensitivity runs bring the total to14. Halving
dt.00025→.000125 gives N32 minimum clearance722.83/723.09mm. Using3600rpm instead
of4800rpm gives719.06/718.37mm. All remain resolved/pass,with peak shaft samples
below the6000rpm gearbox cap. N32 nominal peak sampled shaft rpm2591/2778;
these are output samples,not guaranteed impulse-scale extrema. Nominal first
arrest.58525/.58950s; the observation continues to1.5s. Extension-stop events
at the fully open starting/recovery pose are retained; no compression stop occurs.

## Rigid-impact limitation is material

N32 reaches touchdown at about5.425m/s. The analytical first contact removes
172.09J and leaves30.24J of all-body-plus-rotor KE from202.33J before contact.
Native Pymunk's coupled contact/constraint solve removes171.37J and leaves31.15J
from202.51J. Thus about85% disappears at the rigid touchdown solve. Native
constraint loss is not isolated tire loss. The motor then removes about30J by
first arrest; that is not evidence that a real tire/structure absorbs172J safely.

Half-step ledger residuals reduce from.414→.206J analytical and.949→.475J native.
No numerical residual is credited as useful absorption. Rigid impact has no
physical contact duration,so motor-command torque is not the peak inertial gear,
belt or structural impact torque. A compliant contact model/measured tire data
is needed before treating the virtual landing as real1.5m-drop capability.

## What still prevents a hardware optimum

- Measured motor/gearbox inertia and directional loss map,including breakaway drag.
- The selected drive's48V torque-speed/current envelope,peak duration/cooling,
  battery/regenerative or brake-resistor power and energy acceptance.
- Tire/leg compliance,damping and impact duration; gearbox/belt/coupler shock
  load capability,backlash,mounting and actual transmission mass.

Use32:1 as a conditional prototype starting ratio. More margin favors a higher
ratio; faster leg response favors lower reflected J. The existing unknowns can
change the hardware choice,and full-vehicle pitch/roll/load sharing is not modeled.

## Reproduce and retained evidence

The ignored data ZIP on [Andy's Codex Studies](https://www.notion.so/402b26c7416c8167b41cdb20705fecd6)
contains `.preview/drop15_8325.py`,its exact source hashes/settings,all14 compact
records/CSV,and raw captures only for the selected N32 option. Extract its
contents into the matching app's `.preview` folder. With the app environment and
PYTHONPATH at the app root,run the provided script from the app root with a fresh
output directory; choose `--candidate n32-htg20`, `--dt .000125` or `--rpm 3600`
for the bounded repeats. The audit and Plotly export scripts are included.

Two PNGs and the data ZIP stay app-local ignored/native Notion,never Git or
Downloads. Exact pairs,current model/runner hashes,selected raw metrics,
no-pin flags and local links are checked. No new app physics/UI/dependencies,
GUI interaction or live profile edits were required. No thermal,hardware,
impact-strength,GPU or canonical robot validation is implied.
