# Torque Coupling

Owner Jonathan Xie. Updated 2026-11-15. Local analytical VSL explorer.

Open `Open Torque Coupling.cmd` with installed Python 3, then visit
<http://127.0.0.1:8772/>. The launcher opens the app URL in the default browser and starts a hidden server
when needed. It reuses an existing matching server. Startup errors remain visible;
server logs are saved in the system temporary directory as torque-coupling-server.log.
Alternatively open `index.html` directly. All charts run offline without packages.

Two controls provide minimum, current and maximum values for qdc and qfe.
Initial ranges are 1–3 with current values 2. Typing a current value outside the
bounds expands that control's range. Bounds must be positive with min < max.
Drag the 3D surface to orbit, scroll to zoom, hover for sampled values, and use
Reset view to restore the camera. Teal/orange surface traces match the two
cross-sections. Ratio edits retain the current camera.

## Model and conventions

q_ab=2 is fixed. q_dc=r_d/r_c; q_fe=r_f/r_e. All ratios are dimensionless.

    c1 = -1 + (2 - 1/qdc)/qfe
    c2 = 1/(qdc*qfe)
    omega6 = c1*omega2 + c2*omega4
    c3 = k = -c1/c2 = qdc*(qfe-2) + 1
    tauH = tau2 + c3*tau4

The coupling is signed. It can be negative despite all ratios being positive.
For example qdc=3,qfe=1 gives k=-2. At qdc=1,qfe=1, k=0.
The zero locus is qfe=2-1/qdc.

The parallelogram uses delivered wheel torque tauW=tau4/c2, with motor
limits |tau2|<=130 Nm and |tau4|<=23.6 Nm. Hip effort is tauH=tau2+c3*tau4.
Each coefficient card shows its formula in terms of the two belt ratios.
The dotted centre line has tau2=0. All torque coordinates use Nm.

The three coefficients have prominent cards above the graphs. The numeric
equations inside the parallelogram update live, including the sign of c3.
For c3>0, positive drive torque adds positive generalized CCW hip effort.
With equal links and alpha=0, hip–wheel distance is 2L*sin(theta2) on 0–180°.
Increasing theta2 lengthens the leg on 0–90° and shortens it on 90–180°.
These are effort tendencies, not imposed motion under every external load.

The model assumes ideal constant-ratio belts and fixed chassis pitch. It omits
ground contact, friction, gravity, spring loads, motor speed limits and inertia.
The envelope is an analytical peak-torque illustration, not a robot rating.

## Files

`model.js` owns the equations; `app.js` draws the canvas/SVG views.
`server.py` uses only the Python standard library. No CDN, installation, network
service, workbook writes or browser storage is used.

See [app context](context/README.md) for validation and handoff.
