> V6 note: these inherited model notes use the old per-leg mT notation. In V6 all those mass terms mean mL=mT(robot)/4; payload cases use (mT+payload)/4.

# V5 belt AB sizing handoff

This file defines first-order fall-duty inputs for a belt-sizing calculation.
Read this alongside [the V5 model](v5-model.md), [the geometry shortlist](../../belts/report.md)
and [the verification](v5-belt-verification.json). The app does not select a belt width.
The fall section has eight rows by four columns; its last three rows are signed
AB tension difference (N), Link2-relative belt circulation speed (m/s), and
Link2-relative transmitted power (W). The alpha sweep holds spring numerical parameters fixed, without refitting.
The sweep columns show braking-stroke peak
magnitudes, each computed over the same trajectory rather than multiplying peaks.

## Definitions and reference frame

Let q=theta2 in radians and J=dd_z/dq in m/rad, with positive compression qdot.
The full entered mass translates vertically; links/pulleys are massless in the
fall approximation, beta=0, Fy=0, and chassis pitch alpha is fixed during a catch.
Pulley a is fixed to the chassis. Its absolute angular speed is zero; its speed
relative to Link2 is omega_a_rel=-qdot. Do not substitute the animation cycle time.

    qdot = -vz/J                                  rad/s
    vab = (ra/1000) qdot                           m/s
    deltaTab = TU-TL                               N
    Pab = deltaTab * vab                           W
    tau_a_belt = -(ra/1000) deltaTab                Nm
    tau_a_belt * omega_a_rel = Pab

ra/rb are pitch radii in mm. The circulation sign is chosen so vab is positive
for increasing theta2, consistent with the geometric U/L strand labels. U/L stay
on their geometric sides; either can become tight. Signed Pab is the pulley-a
belt-port power in the rotating Link2 frame. The opposite pulley port has -Pab.
It is neither the fixed shaft's absolute power (zero) nor the hip motor's power,
and is not a prediction of belt heat loss. Hip motor torque tau2 is not pulley-a
belt tooth torque.

For this massless, vertical-load model, the tibia moment gives

    deltaTab = -Fz * (C_global_y - B_global_y) / rb.

The same AB tangent/tension function as the existing FBD solver returns TU/TL.
Its current preload convention is TU=Tab0+max(deltaTab,0),
TL=Tab0+max(-deltaTab,0). Thus preload shifts both span tensions without changing
deltaTab or Pab. This convention is an idealized load model, not a measured
installation-tension or elastic belt calculation. Negative tension is not used.

## Export and reproduction

Use **Export fall study CSV** below the plots. Comment lines record fall height,
full parameters (mm/deg/kg/N) and the belt reference frame. The CSV includes:

| Column | Meaning |
|---|---|
| time_s, theta_deg | Touchdown-relative time and pose |
| T_ab_U_N, T_ab_L_N | Both span tensions, including entered Tab0 |
| delta_T_ab_N | Signed U-minus-L difference |
| v_ab_rel_m_per_s | Belt circulation relative to Link2 |
| P_ab_link2_W | Pointwise deltaT times relative speed |
| qdot_rad_per_s | Physical joint compression speed |
| phase | braking or the same-time endpoint holding state |

Additional columns retain motor torque, net acceleration, Fz, velocity, travel
and kinetic energy. Holding has speed/power zero and its load is recomputed using
Fz=mg, rather than retaining the last braking tension. Peak sweep plots exclude
the holding marker; take maxima of absolute values across braking rows.

In code, VSLFall.study returns the enriched current rows and alpha/height peaks.
For a standalone trajectory, call VSLFall.withBelts(p,VSLFall.solve(p,h));
VSLFall.beltState(p,row) is the common per-pose calculation. The original solve
function remains the unchanged mechanical catch calculation. Invalid AB pitch
geometry leaves belt signals undefined and reports a warning; do not replace these
gaps with a zero load.

## What the sizing calculation still needs

These histories are useful load/speed inputs, not a complete belt specification.
Retain tight/slack tensions, pitch/profile, pulley tooth counts and pitch radii,
centre distance, wrap/teeth engaged, belt pitch length, candidate width, preload,
fall/reversal frequency and required service life. Use the exact belt-family
manufacturer rating procedure, including appropriate load/service factors and
installation requirements. High load at zero speed still needs capacity even
though Pab=0; peak tension and peak speed need not coincide. Do not treat all
PowerGrip, HTD and Poly Chain products as interchangeable tooth profiles.

The existing [Gates Poly Chain design manual](https://www.gates.com/content/dam/documents-library/catalogs/poly-chain-gt-carbon-drive-design-manual-en.pdf)
includes low-speed design-load calculations, service factors, tooth-engagement
and installation-tension guidance. That document covers its stated 8M/14M
families; obtain the applicable 5M guidance if choosing 5M. Its safety policy also
requires an independent backup for applications relying on the belt to stop a
mass; discuss applicability with the manufacturer for this suspension catch.

The fall model includes chassis deceleration through Fz; do not add that inertia
a second time. It excludes belt compliance/tooth-load sharing, moving-link/pulley
inertia, physical touchdown impulse, structural flexibility and finite actuator
response. It does not establish that a fall is the worst case among all other
vehicle operations or certify a safe belt size.
