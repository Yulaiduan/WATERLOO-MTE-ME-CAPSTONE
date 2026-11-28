# 11/28 POR spring retune

Reference S0110 is retained unchanged. New S0201/S0202 use DP20 with
m2=femur=1.98kg, m3=tibia=0.92kg, chassis54kg, knee0.59kg and wheel0kg.
Lengths L2=L3=296.3mm; q_ab=2; alpha=phi0=0; working120–190deg.

Fixed hardware: r_h=61.95415844870695mm, r_s=20mm, nu=0; physical springs
FOX803-04-154 (300lb/in,52.538050574N/mm) and803-04-151
(650lb/in,113.832442910N/mm). See [FOX specifications](https://tech.ridefox.com/bike/general-info/918/2020+-sls-and-standard-steel-rear-shock-spring-information).
Exactly one spring is active:300lb/in for0kg;650lb/in for70kg.
The2:1 remote block gives spring travel=cable payout/2 and spring force=2T.

| ID | Route | S_v mm | S_u mm | Spring p0 0kg N | Spring p0 70kg N | Worst residual Nm | Achievable theta2f deg |
|---|---|---:|---:|---:|---:|---:|---:|
| S0201 | Right, CW |102.871397483|19.226558880|1280.296448455|2673.112308583|0.327718398|-50.0000004|
| S0202 | Left, CCW |119.206153023|-17.475489565|1269.923962542|2651.441085763|0.293082598|-53.7705918|

Preloads are physical spring force at90deg. The outgoing cable is exactly+u
or-u with no extra exit rotation for the required working range. The left
solution uses the opposite tangent, verified independently in the browser.
Clearance is hypot(Su,Sv)-rh-rs:22.6985/38.5261mm, both above15mm.
The unloaded spring remains taut and rated from-50 to190deg. The70kg spring
is checked only120–190deg. All spring data/rates are fixed between payloads;
swap the spring rather than changing installed adjustments or geometry.

Search: fixed-horn two-dimensional differential evolution, exact linear minimax
preload fits, then constrained SLSQP refinement over both payloads. Previous
bounds retained: Sv<=300mm, center angle within70deg of+v, circle clearance
>=15mm, center-radius excess<=205mm. Both results also fit |Su|<30/Sv<150.
Results are best found nominal fits, not globally certified optima. Source FOX
force and energy limits are derived from marked travel; the inherited0.5mm
travel reserve is retained. S0201 reaches that conservative inversion bound at
-50deg; S0202 retains several degrees more inversion.

Validation:20001+critical poses per fit; exact cable/travel extrema;13,917
cross-checks of Python vs JS payout/lever, CW backward compatibility and physical
static torque; staged workbook reload/pane preservation and actual Spring Lab
left/right, force curves and mass-state reload. Existing31 solutions are retained.

All12 saved DPs have their old m2/m3 values swapped, including inactive masses.
A convention marker prevents a second swap on reload. DP20 overrides m2 to1.98.
Affected historical outputs are marked stale. DP20's Ideal Spring calculator
uses S0201's0kg equivalent cable k=13.1345126435N/mm and cable p0=640.148224227N.

Reproduce candidate search with `python -B scripts/retune_por1128.py` from
springs. It writes local candidate JSON only, not saved workbooks. The saved
solutions are in the existing V7 workbook group11/28 POR.
