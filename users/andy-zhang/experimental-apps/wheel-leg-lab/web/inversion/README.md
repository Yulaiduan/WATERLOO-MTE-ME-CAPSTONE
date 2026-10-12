# Invertible suspension bench

Served at `/inversion/` by the app-local Motion Lab server. `app.js` uses
`/api/inversion/defaults`, `/preview`, `/math` and `/pymunk`, Plotly and D3.
Inputs are SI in JSON, displayed in mm/degrees/N/Nm. The two designs are a
single-cap dual-rope knee pulley with two explicit routing pulleys and a
symmetric knee bellcrank anchored50mmfromJ1 on the femur.

Physical ground mode has wheel/chassis contacts with held chassis pitch.
Independent angular mathematics and matched Pymunk comparison hold J1 without
floor contact. Torque is an actual input; there is no hidden position motor.
Profiles/results are portable JSON and integrate with the shared library/native
GUI. Housing placement, rope winding/groove history and3Dclearance remain demo
assumptions; see the app's current validation and invertible-design record.
