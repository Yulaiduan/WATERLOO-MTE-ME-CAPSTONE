# VSL V4 â€” constant-radius hip pulley and preload

Author: Jonathan Xie with Codex. Updated 2026-10-18. Experimental analytical
member app; no hardware, strength, dynamic or spring-rating acceptance implied.

Open [v4-pulley.html](v4-pulley.html) directly or use
[Open Leg Solver v4.cmd](https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE/blob/e91897a9cf9bb36ff3f20afc4c92ea5315cc46b7/users/jonathan-xie/experimental-apps/leg-solver/Open%20Leg%20Solver%20v4.cmd). Offline standalone HTML;
no server or dependencies are needed to use it. V1/V2/V3 remain separate.

## Parameters and units

All geometry is mm, forces N, masses kg, torques Nm and UI angles degrees.
Derivatives below are per radian. A is hip, B knee, C wheel centre and P contact.
Theta2 points Bâ†’A, measured CCW from local +u. Local u/v rotate clockwise by
alpha relative to global y/z. The unchanged leg/belt/load equations are in the
[V2 model](https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE/blob/e91897a9cf9bb36ff3f20afc4c92ea5315cc46b7/users/jonathan-xie/experimental-apps/leg-solver/v2-model.md); V4 retains its prescribed-force, quasi-static assumptions.

The spring panel has exactly these parameter rows:

| Row | Inputs | Meaning |
| --- | --- | --- |
| 1 | k, r_h, S_v | N/mm stiffness, mm horn radius, mm local pulley height; each has a driven checkbox |
| 2 | r_s, p0 | mm idler radius, N spring force at theta2=90 degrees |
| 3 | nu, S_u | degree horn offset from Bâ†’A, mm local pulley horizontal offset |

Nu defaults to zero; the new10mm textbook fit supplies S_u=7.157923 mm and
p0=149.918335 N. P0 is an absolute reference force, not extra predeflection or
force added to an automatically balanced spring. The old zero-preload demo
remains a useful mismatch example in the0.1mm comparison report.
The spring's free/installed length is not an input. Cable length and the remote
spring's mount accommodate its physical size, subject to actual stroke/packaging.
The outgoing cable is along local +u from S's upper tangent; both S and this
direction follow the local axes when alpha changes.

## Finite-radius cable geometry

```
D = r_h [cos(theta2+nu), sin(theta2+nu)]       [local mm]
S = [S_u, S_v]
v = D-S; d = |v|; e = v/d; J e = [-e_v,e_u]
rho = r_s
n = (rho/d)e - sqrt(1-(rho/d)^2) J e
Q = S + rho n                              [incoming tangent point]
u_in = (Q-D)/sqrt(d^2-rho^2)                [unit pull direction at horn]
Q_out = S + [0,rho]                        [fixed upper exit tangent]
```

The cable travels Dâ†’Q, wraps clockwise to Q_out, and exits toward +u. Its wrap
angle beta_wrap follows the continuous branch selected at the 90-degree
reference, initially between 0 and 2*pi. Wrap loss or more than one turn is
rejected rather than silently switching cable sides. Using a continuous polar
angle psi of Q-S, beta_wrap=psi-pi/2+2*pi*N on that fixed branch.

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
90-degree reference geometry: if d(90)â‰¤r_s for a finite pulley, there is no real
tangent and c0 is undefined. Operating clearance at 100 degrees does not repair
that reference. Change r_h/S_v/nu/S_u/r_s rather than extrapolating through the
pulley. Working-range collisions and route loss are also rejected. For a zero
radius, a coincident reference has c0=0, but nonzero force at a coincident actual
operating pose has no direction and is invalid.

For k>0 an energy primitive is U=Fs^2/(2000*k) joules, with zero energy in slack
regions; dU/dtheta2=-tauS. For k=0 a constant-force primitive is
U=p0*(c-c0)/1000. Spring-off gives zero force/torque. Zero-tension regions are
an ideal unilateral limit; this static model does not predict how an unguided
slack cable would recover its route during real motion.

## Driven variables and ideal constant support

The mass used for the spring relation is total mass:

```
m_T = m1+m2+m3+m5+m6
k*r_h*S_v = 2*m_T*g*L2*cos(alpha)            [N mm]
```

L2 is essential: omitting link length would be dimensionally inconsistent.
For equal links L2=L3=L, the right side is 2*m_T*g*L*cos(alpha). Exactly one of
k/r_h/S_v can be driven, or all can be independent. Checking one clears the
others and disables its numeric box. Unchecking it leaves all three editable.
All three nominal drivers are initially off for the finite-pulley textbook fit. Mass, g, alpha or L2 changes recalculate the driven value.
Nu, S_u, p0 and r_s do not enter that nominal product, so editing them leaves
the critical three values unchanged. Impossible divisions/negative required
values or invalid geometry leave the previous valid solution visible.

This relation is a nominal design rule for equal links, q_ab=2, phi0=0,
nu=0, S_u=0, a pure upward wheel force m_T*g and zero moving masses. The actual
model still includes the entered moving weights and prescribed contact loads.
For arbitrary leg ratios/phase, the product is only a scaling reference using L2.
With k/r_h/S_v independent, changing alpha holds their entered values fixed;
with a driven value, alpha sweeps and live alpha changes recalculate it.

In the point-pulley limit:

```
d^2 = r_h^2 + S_v^2 - 2*r_h*S_v*sin(theta2)
d' = -r_h*S_v*cos(theta2)/d
Fs = k*d     IF p0 = k*d(90) = k*abs(S_v-r_h)
tauS = +k*r_h*S_v*cos(theta2)/1000
tauG = +2*m*g*L*cos(alpha)*cos(theta2)/1000   [L mm]
```

Thus the product fixes torque SCALE, while matching preload fixes the force
law. P0=0 does not automatically balance an unequal r_h/S_v geometry. The
sidebar reports k*d(90) and provides an explicit button to set that point-pulley
matching preload. It does not set p0 automatically. With finite r_s or adjusted
nu/S_u, this value is a reference, not a claim of exact balance. The actual
finite-radius curve remains in every torque plot.

## Torque signs and frame reactions â€” revised 2026-10-18

```
tauG = V2 holding tau2                       [required CCW motor without spring]
tau2 = tauG-tauS                             [required applied CCW motor]
physical applied CCW motor2 = tau2
tau4 = V2 physical applied CCW drive torque  [unchanged sign]
F12_new = F12_v2 - F_s,on2
```

TauG is the signed no-spring motor requirement, opposite the actual external
generalized load torque. TauS is the actual spring couple about the hip; it is
normally negative (CW). Therefore more preload increases applied tau2 in the
100â€“165-degree branch. While taut, delta(tau2)=delta(p0)*cprime/1000; this is
not a constant vertical translation because cprime depends on angle. This
revision flips the previous displayed tau2/tauG/tauS signs while preserving
the actual physical motor couple, force balance and saved geometric parameters.

The femur receives the real tangent force at D; its FBD, pin reaction and motor
couple are recomputed. The direct femur spring leaves the tibia/wheel/belt load
equations unchanged. For a massless frictionless fixed pulley, chassis mount
force at S is `Fs*[1,0]-F_s,on2`. The remote fixed spring end receives
`[-Fs,0]` along the outgoing tangent line v=S_v+r_s. These mount reactions sum
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
means1.1mg. The compensation axis spans at least±10% and expands for larger
errors; the raw-torque axis scales independently. Zero weight or vertical
Jacobian makes compensation undefined. These signed plots ignore the optional
absolute-magnitude checkbox used by the older torque sweeps.

Current/global tau2 headlines append this compensation error labeled %mg.
The global percentage is at the torque-peak pose, not an independently searched
compensation-error maximum. With general loads/moving masses it need not equal
the residual motor divided by tauG. Tiny values retain significant digits.

Read the [10mm textbook example](https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE/blob/e91897a9cf9bb36ff3f20afc4c92ea5315cc46b7/users/jonathan-xie/experimental-apps/leg-solver/v4-textbook.md), or Load parameters with the
[textbook preset](v4-textbook-10mm.json). The new **Fit rh,Su,p0 to1mg** button
holds k,Sv,rs,nu/leg geometry fixed, jointly calculates rh/Su/p0, turns off all
nominal critical drivers, and reports sampled error over the operating range.
It uses bounded multistart numerical fitting, not a closed-form or global
optimality claim. These three fitted outputs remain editable; refit after
held parameters, total weight, alpha or travel change. No exact finite-idler
identity is established here. The exact point rule/preload button remain valid
under their stated zero-radius/zero-offset assumptions.

The browser fitter eliminates p0 through affine Chebyshev interval feasibility
for each horn/offset pair, uses2D Nelder-Mead at181 angles and verifies6501
full-model poses. It returns its parameter bounds and sampled maximum error.
For the textbook it achieves about0.06219% versus the independent denser
SciPy reference0.06209%. Invalid current horn geometry may be repaired by the
fit, but the literal90-degree tangent guard is checked for every candidate.

## Force inputs, graph controls and saved files

Each force master has an extra Current Ã—g box. Its value is that signed force
component divided by m_T*g. Editing a driving box to 0.9 sets that force to
0.9*m_T*g N exactly. If necessary its force bounds expand to include the entered
force. Derived force-column boxes are disabled. At zero total weight the g
entry is undefined and disabled. Editing mass updates these normalized readouts
and any driven spring variable; it does not silently alter prescribed forces.

The graph options appear vertically in this order beneath the FBD block:

1. Plot absolute torque magnitude (off by default).
2. Expanded theta2 range (90â€“270 degrees), off by default.
3. Clamp horizontal ranges to user-defined bounds, on by default.

Clamping takes priority over expanded range. When on, theta-based plots and
the residual motor plot use theta2e/theta2c, beta/alpha use their master bounds, and height plots
use the corresponding parametric height domain, retaining interior extrema and
multiple branches. When off, theta uses 90â€“180 or 90â€“270, beta 0â€“90, alpha 0â€“45.
Zero-width bounds are padded up to half a degree (or half a mm for constant
height) for display. Physical motion/height envelopes/global headlines always
use operating bounds regardless of graph options. The r5,I parameter and
duplicate sidebar contact controls are removed; force/beta controls are masters.

JSON schema `general-vsl/v4-pulley` saves all spring variables, nullable
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

Defaults and Reset now use the requested10mm textbook example: L2=L3=300mm,
q_ab2,m1=13kg,moving masses zero,g9.81,Fy0/Fz127.53N,alpha=nu=0,k8N/mm,
Sv100mm,rs10mm,Su7.1579230735mm,rh89.4160351660mm,p0149.918334501N,
theta100–165deg and all nominal spring drivers off. Pe=195.954393852N and
maxFs=963.065307336N. Checked max support error0.06208975%, peak residual
0.037294803Nm. The textbook button restores this whole state.

The older [0.1mm study](https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE/blob/e91897a9cf9bb36ff3f20afc4c92ea5315cc46b7/users/jonathan-xie/experimental-apps/leg-solver/v4-tuning.md) retains product-only, matching point
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

Actual browser checks cover parameter row layout, exclusive/zero driven choices,
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

