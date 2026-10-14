# V2 quasi-static model and usage

Author: Jonathan Xie with Codex. Updated: 2026-10-14. Status: experimental analytical solver.

Open [v2-quasi-static.html](v2-quasi-static.html) in a browser. All code and styles
are embedded, with no packages, server or external data required. The original
[v1-kinematics.html](v1-kinematics.html) remains a separate program, updated with
the two requested travel-direction angles.

## Clarified names, angles and inputs

The user confirmed that **C is the wheel centre / tibia endpoint**, and **P is
the wheel contact patch** in v2. In v1, P keeps its original meaning as the tibia
endpoint. V2's displacement, endpoint stroke and travel-angle outputs track C
relative to C at extension; β locates P relative to C. Both C and P paths appear
in the mechanism drawing, with the current β held fixed along each drawn path.

Global y points rearward/right; z upward; out-of-plane x/w points toward the
vehicle's left. The local frame rotates clockwise by α. β is clockwise from −z
toward −y, as explicitly confirmed by the user. In global (y,z):

```text
n = [sin(beta), cos(beta)]          inward radial unit vector
t = [cos(beta), -sin(beta)]         tangential unit vector
P = C - rw*n
Fcontact = Fn*n + Ft*t
Mw = rw*Ft/1000                     Nm, positive CCW
```

Geometry and pitch radii use mm, angles degrees, masses kg, forces N and torques
Nm. All force components are signed; positive Fn is inward/compressive. A negative
Fn is an outward prescribed force; unilateral tire contact is not enforced. Forces are prescribed inputs,
not automatically inferred from m1. Gravity is −z, with editable g = 9.81 m/s².
Setting masses or g to zero removes gravity loads. Default m1 = 10 kg, the other
masses = 0, Fn = 98.1 N, Ft = 0, β = 0 and all preloads = 0 are demonstration
values, not a selected design or an assumed relation enforced by the solver.

The original link directions remain: theta2 points B→A and theta3 points C→B,
measured CCW from +u. C = B - L3[cos(theta3), sin(theta3)]. Pulley a is grounded;
b is rigidly attached to tibia; d/e is a rigid independent compound pulley;
c is locked at theta4 = 0; f is fixed to the wheel. All belts are open/nonslipping.

Travel angles use the user's updated choice:
gamma_uv = atan2(du,dv), gamma_yz = atan2(dy,dz), in degrees −180 to +180.
The first argument is horizontal, so zero denotes upward vertical travel.
Zero displacement makes direction undefined; the table shows — and exported
CSV uses an empty cell. Graphs break at zero displacement and angle branch cuts.
Live rows 3 and 6 show these angles alongside their constant values at compression.

## Equilibrium and belt model

Define delta_i = T_i,U - T_i,L. U/L are fixed carrier-side labels, corresponding
to upper/lower in the standard folded pose. For a→b and c→d, U is on the CCW
carrier normal; for e→f, U is on the CW carrier normal. Labels rotate with the
carriers rather than switching whenever the projected screen heights reverse.
Exact common external tangents set both the directions and points of application
of each span force. This matters for bearing forces when radii differ.

The requested preload allocation is used explicitly:

```text
T_i,U = T_i,0 + max(delta_i, 0)
T_i,L = T_i,0 + max(-delta_i, 0)
```

It specifies fixed slack-side tension; it is not a belt-elasticity constitutive
law. Torque fixes tension difference, while this allocation fixes the common
tension level and therefore the bearing loads. Preload changes pin reactions,
but does not change ideal holding torque. No negative/compressive belt tensions
are introduced. Zero preload is treated as the ideal limiting assumption.

Wheel and compound pulley moment balance, with radii in mm, gives:

```text
delta_ef = rw*Ft/rf
delta_cd = -(re/rd)*delta_ef
tau4 = rc*delta_cd/1000 = -q_cd*q_ef*Mw
```

The force Fw transmitted from wheel to tibia is the complete wheel balance,
not just the normal force: Fw = Fcontact + W6 + Fef,on6. About B on the tibia,
delta_ab = -[(C-B)×Fw + ((C-B)/2)×W3]/rb. The remaining reactions are:

```text
F32 = Fw + W3 + Fab,on3
F25 = -(Fcd,on5 + Fef,on5 + W5)
F12 = -(F32 - F25 + W2)
F14 = -Fcd,on4
tau2 = -[B×(F32-F25) + (B/2)×W2]/1000
```

Fij means force from body i on body j: Link 3 receives F23 = -F32, Link 2 receives
F52 = -F25, and the wheel receives F36 = -Fw. The model computes the extra chassis
support force/couple at A as well. m1 is concentrated at fixed A and contributes
to this chassis support, not to the suspension-motor torque.

An independent virtual-work expression checks the torques at each live pose:

```text
K = 1 - q_ab + q_ef*(q_ab - q_cd)
tau2 = -(Fcontact·dC/dq + sum(Wi·dRi/dq) + Mw*K)
tau4 = -Mw*q_cd*q_ef
```

Here q = theta2 in radians and centre positions use metres. Every displayed FBD
also directly checks its two force balances and moment balance. Motor torques
are the torques applied to the moving link/rotor; the chassis receives their
opposites. Positive is CCW/red; negative CW/blue.

## Masses and recorded inertias

m2 and m3 are at their slender-rod midpoints, m5 at B, m6 at C; mT is the sum of
m1, m2, m3, m5 and m6. Rod-centroid inertias I2 = m2*L2²/12 and I3 = m3*L3²/12
and rim inertias I5 = m5*r5I², I6 = m6*rw² use metres and kg. Compound pulley's
effective rim radius r5I is explicit/editable because a split between its two
physical radii was not supplied. Inertias are displayed/stored only, with no
acceleration or dynamic torque. No separate m4 is introduced; the requested
actuator/chassis lump is m1 at A.

## Interface and sweep semantics

The first row is the θ₂ master, with numeric minimum θ₂ᵉ, maximum θ₂ᶜ and
current pose. The next row pairs α and β. Two force columns follow: global Fy/Fz
on the left and wheel Fn/Ft on the right. Exactly one **Driving** checkbox is on;
its column is filled darker and editable, while the other pair is derived.

```text
Fy = Fn*sin(beta) + Ft*cos(beta)
Fz = Fn*cos(beta) - Ft*sin(beta)
Fn = Fy*sin(beta) + Fz*cos(beta)
Ft = Fy*cos(beta) - Fz*sin(beta)
```

Switching conventions preserves the current physical vector. A beta sweep holds
the selected components fixed, so global forces remain fixed in Fy/Fz mode and
rotate in Fn/Ft mode. This distinction also applies during playback and CSV
export. All seven displayed masters have min/max/current boxes; only the five
independent masters are enabled (θ₂, α, β and the selected force pair). Resuming
one freezes all others. Alpha is allowed 0–45°, beta 0–90°, and forces are signed.
A sidebar value outside a window expands it; the master current box clamps to
the chosen window. Derived force windows expand to display converted components.
The cycle period illustrates parameter playback, not a physical velocity.

Headline cards show tau2, tau4, total tight-span Tab and its upper/lower side,
and dz with final hz. Balanced belt tension displays upper = lower. Total mass
remains in the sidebar. Figure checkboxes independently hide/show motor couples
and the selected global or radial/tangential wheel-force decomposition.

Below these controls, FBDs for Links 2/3 share the first row and Links 4/5/6
share the second row. These five FBDs with all applied span forces, weights, bearing
reactions and motor couples. Links 2–5 use local u/v, wheel 6 uses global y/z.
Each force table lists magnitude and rho measured CCW from that diagram's
horizontal positive axis, modulo 360°. Zero-force direction is undefined.
Arrow lengths/opacity rise with magnitude and cap for legibility; values stay exact.

Four rows of three graphs sweep theta2 (90–180°), working-range dz, beta
(0–90°) and alpha (0–45°), in that order.
Angle sweeps vary their x variable while holding the other independent inputs
fixed. The dz row evaluates the same theta2 loading sweep over theta2e..theta2c,
plotting it against signed wheel-centre vertical displacement. The columns
are motor torques tau2/tau4, tight-span total belt tensions, and magnitudes of
F12/F14/F25/F32/Fw. Signed torques are solid for positive and dotted for negative;
the absolute-value checkbox preserves those sign styles. Tight belt span is
solid when U, dotted when L; its value includes preload. Hover shows both span
tensions. Windows determine the highlighted ranges. The dz loading axis normally runs
0..hz (reversed/signed travel is kept); interior extrema extend it when needed.
Bottom graphs are Angles vs theta2, Angles vs dz, then C displacements vs theta2.
The angle/dz domain covers all travel over theta2=90..180, including negative dz;
vertical dotted lines mark 0 and hz. Full-domain branches are pale and working
theta branches dark, because projected height shading alone cannot distinguish
multiple poses at the same dz. Curves remain ordered by theta, with all sampled
inverse branches reported on hover; no monotone height inverse is assumed.
Constant travel is padded ±0.5 mm only for display. Domains/inverse branches
are sampled and may miss narrow features at extreme ratios. The envelope and
wheel-coupling explanation follow these rows.

V2 JSON schema is `general-vsl/v2-quasi-static`: geometry, masses, loads, preloads,
master windows, pose, driven choices, loadMode (nt/yz), torque display mode and
optional arrow visibility settings are saved. Older v2 files default to nt mode. Import
also accepts v1 parameter JSON, adding explicit v2 demo defaults. CSV exports
all four sweeps, parameters/windows, explicit x/x_unit fields (mm for dz, degrees
for angle sweeps), resolved Fn/Ft/Fy/Fz, dz and exact current/window boundaries,
both span tensions, motor torques, travel angles and force-vector components.
Comment metadata lines begin with `#`; undefined or invalid-geometry results are
blank rather than fabricated zeros.

## Global headline maxima

Per the user's final clarification, maxima cover theta2e..theta2c and the beta
master minimum..maximum simultaneously, with alpha at its current value. Alpha's
master window is not part of this search. The selected Fn/Ft or Fy/Fz pair stays
fixed, so beta-dependent force conversion follows the existing driving convention.
The current four cards remain; the second row has equal-size values and a peak
pose for each quantity. Tau2/tau4 keep the sign at the largest absolute value;
Tab is total tight-span preload + absolute tension difference, with U/L side;
dz is the largest magnitude, with signed travel available in the tooltip.

The new embedded VSLPeaks model uses analytic sinusoidal beta candidates at each
theta: both bounds plus every in-range stationary angle. It then bisects theta
intervals, bounding unseen maxima by the larger endpoint magnitude plus
M*(interval width in radians)^2/8, where M bounds the second theta derivative of
the signed objective for every beta. Maximizing absolute values uses both signs.
This avoids missing an interior beta peak or relying on a fixed sampling grid.

For k = abs(1-q_ab), F = hypot(driving force components),
a = m2/2 + m3/2 + m5 and b = m3/2 + m6, conservative M values are:

```text
tau2: [F*(L2+L3*k^3) + g*((a+b)*L2+b*L3*k^3)]/1000
tau4: 0
Tab difference: L3*k^2*[F+g*(m6+m3/2)]/rb
dz: L2+L3*k^2
```

Units use mm/N/Nm with theta derivatives in radians. The bound applies to the
unrounded magnitude; cards round normally. Search tolerance is 0.001 in each
quantity's displayed unit. After at most 20,000 refinements per quantity, any
unclosed gap is explicitly displayed as an estimate. Each reported value is
attained at its stored pose. Ties may have multiple valid poses. Floating-point
limits still apply. Core equilibrium/kinematics are unchanged.

Maxima are cached by current alpha, relevant geometry/masses/forces, theta/beta
bounds and Tab preload. Moving current theta/beta or changing only alpha-window
bounds reuses the result; changing current alpha recomputes it. Force-window
endpoints are not swept. JSON and CSV keep their existing schema; maxima are
derived display results rather than a new input or export column.

`node verify-global-maxima.cjs` passes 29,863 assertions, including random actual
FBD parity, attained peak poses, conservative domain upper bounds, interior
extrema, negative travel, preloads, collapsed windows, estimate fallback, both
driving conventions and the fixed-alpha wrapper. Existing quasi-static checks
remain passing. No dynamics or hardware validation is introduced.

## Validation and limits

`node verify-kinematics.cjs` passes 3,853 assertions including atan2 quadrants and
undefined extension direction. `node verify-quasi-static.cjs` passes 16,044
assertions over 240 varied geometries/loads/poses, including exact single-load
examples, all five FBDs, whole-system balance, span force/tangent moment balance,
action/reaction pairs, finite-difference virtual work, preload/m1 torque invariance,
fast/full sweep parity and invalid geometry; plus 91 paired loading-convention
comparisons, force-norm and global-sweep invariance, signed loads, fractional
endpoints, negative dz, multibranch inverses and a zero-width height domain. Maximum tested force residual is
9.722e-13 N; moment residual 3.624e-13 Nm; analytic virtual-work torque discrepancy
3.979e-13 Nm. These are numerical consistency checks, not hardware measurements.

Browser verification and repository checks are recorded in [app context](context/README.md).
No inertia integration, acceleration, spring/damper, ground rolling constraint,
unilateral contact/friction feasibility, impact, strength or 3D clearance is solved.
Overlapping pitch circles disable statics until repaired. Curves are finite-sampled;
extreme ratios can hide narrow features. Canonical robot physics is not applicable
to this isolated analytical member app.

Sources: the user's mechanism description and explicit gravity/contact/point-name/
atan2 clarifications (2026-10-13); [Engineering Statics equilibrium](https://engineeringstatics.org/Chapter_05-equations-of-equilibrium.html)
and [SDP/SI timing-belt handbook](https://www.sdp-si.com/D820/PDFS/Technical-Section.pdf)
for background. Mechanism-specific equations and preload allocation are derived
or specified here; these sources do not validate the hardware design.
