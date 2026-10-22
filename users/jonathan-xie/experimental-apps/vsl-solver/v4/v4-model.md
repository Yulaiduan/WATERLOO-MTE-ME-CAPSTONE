# VSL V4 — constant-radius hip pulley and preload

Author: Jonathan Xie with Codex. Updated 2026-10-21. Experimental analytical
member app; no hardware, strength, dynamic or spring-rating acceptance implied.

Open [v4-pulley.html](v4-pulley.html) directly or use
[Open Leg Solver v4.cmd](Open%20Leg%20Solver%20v4.cmd). Offline standalone HTML;
no server is needed for calculations. Use the root V4 launcher for the local
Python Excel bridge. V1/V2/V3 remain separate.

## Parameters and units

All geometry is mm, forces N, masses kg, torques Nm and UI angles degrees.
Derivatives below are per radian. A is hip, B knee, C wheel centre and P contact.
Theta2 points B→A, measured CCW from local +u. Local u/v rotate clockwise by
alpha relative to global y/z. The unchanged leg/belt/load equations are in the
[V2 model](../v2/v2-model.md); V4 retains its prescribed-force, quasi-static assumptions.

The spring panel has exactly these parameter rows:

| Row | Inputs | Meaning |
| --- | --- | --- |
| 1 | k, r_h, S_v | N/mm stiffness, mm horn radius, mm local pulley height; each has a Driving checkbox |
| 2 | r_s, p0 | mm idler radius, N spring force at theta2=90 degrees |
| 3 | nu, S_u | degree horn offset from B→A, mm local pulley horizontal offset |

Nu defaults to zero. Current8.75kg baseline uses r_h62.2269495mm,
S_u9.38777673mm, p₀330.869283N, k8N/mm, S_v100mm and r_s10mm.
P₀ is the90° reference force, not extra predeflection on a matched spring.
Physical spring free length and packaging length are not model inputs; real
spring stroke and cable tension still need checking. The outgoing direction
is fixed over working travel and follows local u/v when alpha changes.

## Finite-radius cable geometry

```
D = r_h [cos(theta2+nu), sin(theta2+nu)]       [local mm]
S = [S_u, S_v]
v = D-S; d = |v|; e = v/d; J e = [-e_v,e_u]
rho = r_s
n = (rho/d)e - sqrt(1-(rho/d)^2) J e
Q = S + rho n                              [incoming tangent point]
u_in = (Q-D)/sqrt(d^2-rho^2)                [unit pull direction at horn]
a = max(0,zeta)                            [radians CW]
Q_out = S + rho*[sin(a),cos(a)]
u_out = [cos(a),-sin(a)]
```

The incoming tangent uses the same clockwise branch throughout travel.
Let b(theta)=psi(theta)-pi/2+2*pi*N, with continuous psi. Choose integer N
so the maximum b over working travel is at most2*pi, as close to2*pi as
possible. Then zeta=-min b over that interval and applied a=max(0,zeta).
Final beta_wrap=b+a must stay in[0,2*pi]. This selects one outgoing direction
for the entire working range, not a direction that changes at each pose.
Wrap extrema include endpoints and common-tangent roots
S dot [cos(theta+nu),sin(theta+nu)] = r_h +/- r_s, evaluated analytically.
The reported zeta may be negative; the visual applied rotation then stays zero.
Zero wrap is a limiting tangent configuration, without a manufacturing margin.
If no one-turn route exists the design is rejected.

The90° payout uses this same continuous branch even if it falls outside the
retained wrap interval: p₀ is then an **extrapolated reference**, as requested.
This does not allow a90° pin inside/on the pulley. Adding a constant outgoing
rotation changes c(theta) and c(90) by the same r_s*a, so it changes neither
spring force nor torque. It only makes the selected cable route realizable.

```
c(theta2) = sqrt(d^2-rho^2) + rho*beta_wrap   [variable cable payout, mm]
D' = r_h [-sin(theta2+nu), cos(theta2+nu)]
c' = -u_in dot D' = -cross(D,u_in)           [mm/rad]
```

This includes BOTH the changing tangent span and changing wrap; replacing c by
the centre distance d for a finite pulley gives the wrong spring motion ratio.
For rho=0, c=d and the ordinary point-pulley result is recovered exactly.

The UI diagram shows the actual incoming tangent and wrap. The remote spring
and anchor are schematic: their drawn span is not an additional input or a
physical spring-length constraint. The small pulley centre marker may be enlarged
for visibility; torque uses the entered radius without visual scaling.

## Literal preload and spring torque

```
c0 = c(90 degrees)
Fs(theta2) = max(0, p0 + k*(c(theta2)-c0))   [N]
pe = Fs(theta2e)                           [actual extension-stop preload]
F_s,on2 = Fs*u_in                          [local N]
tauS = -Fs*c'/1000                         [Nm, physical CCW spring couple]
```

P0 is literally force at 90 degrees, even though the operating hard stop is
theta2e=100 degrees by default. The owner explicitly chose to flag invalid
90-degree reference geometry: if d(90)≤r_s for a finite pulley, there is no real
tangent and c0 is undefined. Operating clearance at 100 degrees does not repair
that reference. Change r_h/S_v/nu/S_u/r_s rather than extrapolating through the
pulley. Working-range pin/idler intersections and an impossible one-turn route are rejected;
a realizable exit is automatically redirected before testing wrap loss. For a zero
radius, a coincident reference has c0=0, but nonzero force at a coincident actual
operating pose has no direction and is invalid.

For k>0 an energy primitive is U=Fs^2/(2000*k) joules, with zero energy in slack
regions; dU/dtheta2=-tauS. For k=0 a constant-force primitive is
U=p0*(c-c0)/1000. Spring-off gives zero force/torque. Zero-tension regions are
an ideal unilateral limit; this static model does not predict how an unguided
slack cable would recover its route during real motion.

## Driving choices and numerical fit

Every spring input has a Driving checkbox. Checked means held during fitting;
unchecked means numerically fitted. Default held values are k, S_v, r_s and ν;
r_h, p₀ and S_u are fitted. All numeric fields remain editable as initial
estimates. There is no automatic product-based driver or three-variable limit.
The local vertical coordinate remains S_v (the earlier S_y/S_z names were retired).

**Fit driven variables to 1mg** minimizes the sampled maximum absolute applied
motor torque over working θ₂, with current α, β, driving forces and moving
weights fixed. It does not sweep the β window used by global headlines. At the
normal pure1mg load this is gravity balancing. If entered loads differ, it fits
those loads as confirmed by the user; it does not substitute1mg silently.

Any subset of the seven inputs can be fitted. Zero unchecked boxes evaluates
the current design and warns that nothing is free. One/two free inputs produce
a warning about limited freedom. Held values are preserved exactly. Physical
geometry and the literal90° tangent guard remain enforced. Changes to inputs
while the background fit runs discard its stale result.

For each geometry, the motor torque is affine in k and p₀ while the cable is
taut. Interval feasibility solves a single free linear coefficient; convex
polygon clipping solves two free coefficients for a trial peak error. A binary
search minimizes that error. Other free geometry variables use bounded,
multistart Nelder–Mead,181 objective poses and6501 verification poses. Analytic
payout extrema constrain nonnegative force between samples. The numerical
result is neither a certified global minimum nor hardware validation.

Bounds scale from current values and can be inspected in the result tooltip:
k≥0, r_h≥0.1mm, free S_v≥0.1mm, r_s≥0, p₀≥0, ν within±90° of its starting
value and S_u in a finite neighborhood. The result warns when a bound is active,
tension reaches zero or a denser check finds a larger peak. If r_s is free, a
zero-radius point limit is allowed mathematically and explicitly warned as
requiring positive radius in hardware. Keep r_s Driving checked for a real
chosen pulley. Multiple free variables may have equivalent solutions.

For the8.75kg,300/300mm,100–165°,k8,S_v100,r_s10,ν0 baseline, the default
three-variable fit gives approximately r_h61.979839mm, S_u9.286876mm,
p₀335.81448N and peak |τ₂|0.023771Nm. The old baseline remains in the library;
fitting changes the live solver only, until Row Save is clicked.

The old point relation remains a mathematical reference, not a live driver:

```
m_T = m1+m2+m3+m5+m6
k*r_h*S_v = 2*m_T*g*L2*cos(alpha)            [N mm]
```

It applies to equal links, q_ab2,φ₀=ν=S_u=r_s=0, no moving masses and a pure
1mg vertical contact load. It fixes scale but also needs matching preload.

In the point-pulley limit:

```
d^2 = r_h^2 + S_v^2 - 2*r_h*S_v*sin(theta2)
d' = -r_h*S_v*cos(theta2)/d
Fs = k*d     IF p0 = k*d(90) = k*abs(S_v-r_h)
tauS = +k*r_h*S_v*cos(theta2)/1000
tauG = -2*m*g*L*cos(alpha)*cos(theta2)/1000   [L mm]
```

Thus the product fixes torque scale, while p₀=k*d(90) removes the constant
force offset. The removed point-pulley button only set that preload; it did not
fit finite-radius tangency or offsets. The finite-radius fitter replaces it.

## Torque signs and frame reactions — revised 2026-10-21

```
tauG = -V2 holding tau2                     [physical CCW gravity/load torque]
tauS = -Fs*cprime/1000                       [physical CCW spring couple]
tau2 = -tauG-tauS                           [physical applied CCW hip motor]
tau2+tauG+tauS = 0
tau4 = V2 physical applied CCW drive torque [its own drive shaft]
F12_new = F12_v2 - F_s,on2
```

All three hip quantities share positive CCW on Link2. TauG is normally positive
and tauS normally negative in the normal support case. Physical load/geometry
reversals retain their actual signs; no absolute-value clamping is applied.
Only the definition of tauG changes in this release. Motor torque, spring torque,
frame forces and energy balance are physically unchanged. More preload still
raises tau2 on100–165° by Δp₀*cprime/1000, an angle-dependent change.

The femur receives the real tangent force at D; its FBD, pin reaction and motor
couple are recomputed. The direct femur spring leaves the tibia/wheel/belt load
equations unchanged. For a massless frictionless fixed pulley, chassis mount
force at S is `Fs*u_out-F_s,on2`. The remote fixed spring end receives
`-Fs*u_out` along the outgoing tangent line v=S_v+r_s. These mount reactions sum
to `-F_s,on2` and a moment `-tauS` about A. Including them restores V2's
complete-frame resultant support; they do not create an external net force.

The extra spring-force headline is column three on wide displays. Its upper
card gives current Fs. The lower card gives max Fs over the operating theta
bounds and pe=Fs(theta2e). These stay independent of plot zoom and expanded
range. Maximum Fs is found from analytic cable-payout extrema (including
endpoints); it does not sweep a single current pose. Torque headlines use the
applied CCW tau2. All torque plots retain tauG/tauS/tau2/tau4, with actual HTML
subscripts G and S in labels and displayed equations.

The middle Hip pulley geometry & support section is collapsible and starts
expanded. The owner clarified that the desired percentage is **effective mg
compensation error**, not residual motor divided by tauG. Its right column
therefore contains TWO separate linear graphs: applied tau2 in Nm and
100*(Feq/(m_total*g)-1) in percent. Zero means1mg; -10% means0.9mg and+10%
means1.1mg. The compensation axis fits its finite sampled min/max with 8%
padding; constant curves receive a small nonzero range. The left scale shows
signed effective mass error Δm = Feq/g − m_total = m_total*percent/100 (kg),
and the right scale shows percent. Negative kg means less equivalent spring
support than the target weight. The raw-torque axis scales independently. Zero weight or vertical
Jacobian makes compensation undefined. These signed plots ignore the optional
absolute-magnitude checkbox used by the older torque sweeps.

Current/global tau2 headlines append this compensation error labeled %mg.
The global percentage is at the torque-peak pose, not an independently searched
compensation-error maximum. With general loads/moving masses it need not equal
the residual motor divided by tauG. Tiny values retain significant digits.

The separate [13kg textbook study](v4-textbook.md) and its JSON retain the
earlier support-error fitting evidence. That algorithm is preserved only as
`VSLFit.fitSupport` for reproducible historical checks; the UI uses the new
raw-motor minimax objective described above. Its preset button is removed.

## Force inputs, graph controls and saved files

Each force master has an extra Current ×g box. Its value is that signed force
component divided by m_T*g. Editing a driving box to 0.9 sets that force to
0.9*m_T*g N exactly. If necessary its force bounds expand to include the entered
force. Derived force-column boxes are disabled. At zero total weight the g
entry is undefined and disabled. Editing mass or g preserves the active normalized components, rescales their
prescribed forces without changing spring inputs automatically. Saved-row Load instead
restores its saved forces exactly.

The graph options appear vertically in this order beneath the FBD block:

1. Plot absolute torque magnitude (off by default).
2. Expanded theta2 range (90–270 degrees), off by default.
3. Clamp horizontal ranges to user-defined bounds, on by default.

Clamping takes priority over expanded range. When on, theta-based plots and
the residual motor plot use theta2e/theta2c, beta/alpha use their master bounds, and height plots
use the corresponding parametric height domain, retaining interior extrema and
multiple branches. When off, theta uses 90–180 or 90–270, beta 0–90, alpha 0–45.
Zero-width bounds are padded up to half a degree (or half a mm for constant
height) for display. Physical motion/height envelopes/global headlines always
use operating bounds regardless of graph options. The r5,I parameter and
duplicate sidebar contact controls are removed; force/beta controls are masters.

JSON schema `general-vsl/v4-pulley` saves all spring variables; the historical nullable
springDriven, graph flags, force convention/windows and pose. New exports add
`torqueConvention: applied-ccw`; older V4 files keep their same mechanical state.
CSV tau2 and motor2_applied_CCW now agree, and tauG/tauS signs follow this revision. Legacy V1/V2/V3
files load geometry and force inputs with the new pulley spring disabled and
all spring variables independent; V3's direct spring is not silently mapped to
the new architecture. Missing legacy loadMode preserves the V2 nt default.
CSV has 43 columns, including payout, Fs, p0, pe, wrap angle, tangent length,
actual k, total weight, tauG/tauS/applied motor torque and existing belt/pin
results. It follows displayed graph domains and leaves undefined values blank.

## Defaults and checks

Defaults and Reset use L2=L3=300mm, q_ab2,
m1=8.75kg, moving masses0, rw200mm, g9.81,Fy0/Fz85.8375N, alpha=nu=0,
k8N/mm, S_v100mm, r_s10mm, S_u9.38777672815mm, r_h62.2269495119mm,
p₀330.869282809N, theta100–165deg and no nominal spring driver.
P_e=348.730560502N, maxFs=848.489854405N, sampled support error±0.126142%
and maximum applied correction0.062741136Nm. This is a numerical approximation.
The separate13kg JSON/report retains its earlier0.06208975% result.

The older [0.1mm study](v4-tuning.md) retains product-only, matching point
preload, finite fit and zero-radius exact reference cases. The nominal product
alone does not match preload, and finite tangency/wrap still require correction.

Run `node verify-pulley.cjs`; `--output` regenerates v4-verification.json.
91,128 assertions pass: 600 varied finite/zero-radius poses, independent payout
and energy derivatives, tangency, frame/pin/FBD/virtual-work balance, ideal A/B
cancellation, all driven choices using total mass, graph-domain combinations,
24 global-bound/force-maximum cases, slack/k=0 and cable-angle branch continuity.
Max force residual 4.69e-13 N, moment residual 7.82e-14 Nm, energy derivative
error 2.11e-7 Nm and payout-derivative error 5.96e-8 mm/rad. These are numerical
consistency checks, not canonical robot or hardware validation.

Historical browser checks covered parameter row layout, the retired exclusive drivers,
independent nu/S_u, total-mass force multiples, automatic force-window expansion,
default and expanded/clamped domains, HTML G/S subscripts, current/global Fs/pe,
point-limit cancellation and finite-radius deviation, V4 save/restore, safe V3
migration, 23 finite SVGs and empty warning/error logs. Actual CSV has 1,446
rows/43 columns, clamped domains, all finite numeric cells, residual identity
error below 9.60e-13 Nm and exact applied-motor sign in the original V4 build. This revision separately
checks applied-sign parity, preload slope and percentage singularities; the
independent four-case fitting calculation is checked by 26,004 full-model poses.
Actual revised browser checks verify collapse/expand, preload rise, fit import,
linear dual-axis traces, tiny headline values zero-weight compensation handling, textbook reset, finite numerical fitting
from invalid current point geometry, and independent linear compensation/torque
graphs with24 finite SVGs. Fitter regression covers both0.1mm/10mm, held
parameters, sampled-error agreement, rejected zero stiffness/weight and6501
full-model textbook poses.
Initial tests corrected
a cross-realm empty-array assertion and a mistaken 14-versus13 kg fixture;
no physical tolerance was relaxed. Browser inspection caught and corrected
sweep metadata overwritten with theta bounds and narrow force-column overflow.

The fixed-alpha motor maximum search retains analytic beta extrema and uses
conservative smooth/slack theta interpolation bounds for the finite pulley.
It targets 0.001 Nm/N/mm and shows estimates if limited. Graphs/height inverse
roots are sampled; narrow features can be missed. Friction, cable bending,
spring hysteresis/stroke/rating, structural strength and real hard-stop dynamics
remain unmodeled. Projected linkage overlap is outside scope, per owner request.

## Current drive reductions, load scaling and library

V4 names the inverse ratios q_dc=rd/rc and q_fe=rf/re. Thus
K=dtheta6/dtheta2=1-q_ab+(q_ab-1/q_dc)/q_fe and the contact-couple contribution
to motor4 is -Mw/(q_dc*q_fe). Existing files store physical radii; those
continue to mean the same geometry. Old qcd/qef driven selections are migrated.
V1–V3 HTML and conventions are unchanged.

Mass or g edits scale the active prescribed force pair (Fy,Fz or Fn,Ft) at fixed
component/(m_total*g). A remembered pair permits zero-mass round trips. Loading
a saved design restores its exact saved forces; it does not rescale that snapshot.

The config library and stdlib local Excel bridge are described in the
[app index](../README.md). Numerical saved outputs describe the saved pose/ranges;
they are not Excel formulas. Row Save refreshes outputs after Excel input edits.
`verify-library.cjs` checks inverse reductions, mass following, ζ extrema and
immutable snapshots; `verify_excel.py` tests workbook round trips and revisions.

## Saved-state migration

New JSON/row snapshots store all seven booleans in springDriving and mark
torqueConvention=physical-link2-ccw/v2. Historical snapshots load their resolved
physical values, default to the new four-held/three-fitted selection and invert
only their saved tauG output. Tau2, tauS, tau4 and physical geometry are retained.
Repeated migration is idempotent. Existing XLSX files are not rewritten on load;
Save Excel explicitly persists the new representation, and Row Save refreshes
their saved outputs. The library's fitted-variable column summarizes the mask.

`node verify-fit.cjs --output` exercises zero through seven free variables,
exact point-limit linear fits, held-value preservation, dense peak checks and
signed equilibrium. `verify-library.cjs` covers migration; `verify_excel.py`
covers mask/sign preservation in the XLSX state sheet.
