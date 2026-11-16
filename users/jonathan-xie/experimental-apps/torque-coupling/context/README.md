# App context

Updated 2026-11-15. Owner Jonathan Xie with Codex.

This tool explores k=-c1/c2 as qdc/qfe vary. q_ab=2, peak motor torques
130/23.6 Nm. Initial ratio domains 1–3. The user's requested torque coordinate
is now tauW=c2*tau4. Delivered wheel torque remains tau4/c2 and is explained in
the UI. Negative k is retained. No changes to VSL or its saved configurations.

2026-11-15 follow-up adds c3=-c1/c2 as an alias of k, three prominent coefficient
cards, and numeric equation labels inside the envelope. The horizontal coordinate
and dotted centre line now scale positively with drive torque. Positive generalized
CCW hip effort tends to compress on 90–180°, extend on 0–90°; c3 may change sign.

Source `model.js` is the model boundary. Surface is an orthographic canvas
projection with sampled hover, rotation and zoom; cross-sections and envelope
are SVG. No external dependencies. Launcher/server use port 8772, route /.

Validation on 2026-11-13: 15,129 numerical checks over a 41x41 ratio grid pass,
covering unsimplified coefficients and inverse envelope vertices. JS and Python
syntax checks pass. Actual local browser checks cover positive/negative/zero
coupling, live typed values, bound changes, invalid-bound rejection, range-slider
keyboard input, four linked plots, orbit and scroll zoom, reset, finite SVGs and
no browser warnings/errors. The durable Windows launcher starts the app and the
server restarts at the same URL. No hardware/contact/dynamic claims are made.
Whole-checkout entry/gate command was stopped after more than two minutes without output. App-specific checks passed; no whole-repository check pass or remote publication is claimed. Installed files matched the prepared sources and five local HTTP routes returned 200.
Follow-up validation on 2026-11-15: 16,810 numerical checks pass across 41x41 ratios, including c3=-c1/c2 and the positive-x envelope inversion. JS syntax passes. Actual browser checks confirm three prominent live coefficient cards, in-envelope numerical formulas with subscripts, positive/negative/zero c3 updates, finite SVGs and no warning/error logs. Changes remain local; no whole-checkout gate or remote publication was performed for this UI follow-up.

Latest 2026-11-15 correction supersedes earlier x-coordinate notes: tauW=tau4/c2 is now delivered wheel torque, while tauH=tau2+c3*tau4 remains unchanged. Coefficient cards show algebraic definitions. launcher.py starts/reuses a hidden local server and opens the HTTP URL through the OS browser association; the .cmd prefers py -3, then python.
Latest correction verified with 15,129 numerical envelope checks, JS syntax, isolated hidden-server cold start and reuse, and actual Windows .cmd execution returning successfully. Browser confirms all three formulas and delivered-wheel equations (at qdc=2,qfe=3: tauW=6*tau4, tauH=tau2+3*tau4), with no warning/error logs. Launcher starts the server in the background and opens the HTTP URL through Windows; double-click it in File Explorer, or use the direct app URL. No repository-wide pass or publication claimed.
