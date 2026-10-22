# Suspension and actuator sizing

Andy Zhang with Codex, 2026-10-19. Experimental analytical screen, not hardware
selection or canonical robot validation. Started from main `5d9dfa2`.

Use **Start Motion Lab.cmd**, then **Suspension & actuator sizing** at
<http://127.0.0.1:4186/?tab=sizing>. **Jon V4 · VSL solver** is a sibling main
tab at <http://127.0.0.1:4186/?tab=vsl>. Both use the shared theme, existing
launcher/server and browser library. No extra port, cloud credentials or service.

## Spreadsheet source

The user-requested [motor workbook](https://docs.google.com/spreadsheets/d/1ttHpUltfZHpnzD9DO-fUXWn_x426xmtnoujWum3Lag4/edit#gid=20261020)
now has `Gearboxes!A1:AH7`: four distinct EG23 10 mm-input ratios (5, 10, 20,
50) and two sale/packaging-damage listings of the same mechanical designs.
All 34 columns retain units, catalog limits, geometry, mass, price, sources,
retrieval date and interpretation notes. New headers use 8 pt, body 9 pt,
28 px data rows and the existing navy header style. Long caveats are also cell
notes. Other workbook tabs were preserved. Readback verifies values, links,
notes and formatting; Google-rendered visual verification was unavailable
because the in-app browser was not signed into Google.

The checked-in `web/sizing/catalog.json` was created from the **saved sheet
readback**, plus the nine Flipsky rows in `'Pure motors'!A1:AA38`. It is a dated
snapshot, explicitly not live synchronization. Download either tab as CSV from
Sheets and use the matching importer under Map bounds & spreadsheet refresh.
Exact headers/positive limits are validated; failed imports keep the old catalog.
Imports persist in session storage. Restore verified snapshot reverses them.
The calculation JSON and library record retain the catalog used for reproduction.

Manufacturer evidence:

- [EG23 family](https://www.omc-stepperonline.com/nema-23-eg-series-planetary-gearbox):
  nominal torque 28/10/30/25 Nm, rated/max input 3000/6000 rpm, radial/axial
  400/230 N. The 10:1 rating is deliberately not interpolated from 5:1.
- Individual model pages, linked in each sheet row, supply efficiency, inertia,
  dimensions and prices. Product wording calls the first torque “max permissible”;
  family wording calls it nominal. Momentary rating duration is unspecified.
- G10 mass is the family's 0.85 kg nominal; G5/G20/G50 use product net weights
  0.841/1.090/1.102 kg. Shipping weight is not used as component mass.
- Sheet Converted Kt is 8.27/Kv in the sheet's phase-peak convention. Flipsky
  maximum torque/current/power are not continuous ratings; vendor current and
  resistance conventions remain unverified. Source caveats stay visible.

## Basic model

One ideal zero-effective-free-length spring joins a point R along the upper
link to a chassis anchor H below the hip. It provides constant equivalent
vertical lift, not constant spring tension. Positive physical coil free length
requires suitable preload/routing; actual hardware packaging is not specified.
There is no damping or positive ride-height restoring stiffness.

The fixed guide ratio is 2:1. Let upper/lower lengths be a/b, theta rise from
horizontal, and S=a+b. Hip height above wheel hub is h=S sin(theta); wheel
horizontal position relative to hip is x=(a-b) cos(theta). The chassis translates
vertically without pitch. The wheel hub remains at fixed height and can translate
laterally without tire force. Rod COMs and inertia are included. Wheel rotational
inertia and motor/gearbox reflected inertia are excluded.

With M=(chassis+payload)/supporting corners, upper/lower masses mu/ml:

```text
Fgravity = g [M + mu(a/2+b)/S + ml*b/(2S)]
Qgravity = Fgravity*S*cos(theta)
k = Fspring*S/(H*R), R = attachment_fraction*a
span² = H²+R²-2HR*sin(theta)
Qspring = kHR*cos(theta), tension = k*span
A = mu*a²/4 + ml*(a-b/2)² + mw*(a-b)²
B = M*S² + mu*(a/2+b)² + ml*b²/4
Meff = A*sin²(theta) + B*cos²(theta) + (mu*a²+ml*b²)/12
Q = Meff*theta_ddot + 0.5*Meff_prime*theta_dot² + Qgravity-Qspring
theta_dot = vertical_speed/(S*cos(theta))
theta_ddot = (vertical_accel+S*sin(theta)*theta_dot²)/(S*cos(theta))
```

Hip output torque/speed are Q and theta_dot; ideal relative-knee actuation has
half the torque and twice the speed. Work is invariant. Screen both speed
directions, rest and ±acceleration at 101 poses. The design factor multiplies
torque, not speed. These are pointwise bounds, not a time trajectory or RMS
thermal duty calculation. Windows are limited to 1–85 degrees to avoid the
vertical Jacobian singularity.

Changing mass leaves spring support fixed. The explicit 90% button retunes
the spring. The map uses 27×27 mass/length cells and 41 poses per cell, retains
the lower/upper ratio, individual moving masses, anchor and physical spring k;
attachment radius scales with the upper link. Thus it is a length sensitivity
at fixed component masses, not automatic structural/mass optimization.

## Conditional motor bands

```text
omega_motor = ratio * omega_output
torque_output <= min(eta*ratio*Kt*I, eta*ratio*motor_max_torque,
                     eta*ratio*motor_max_power/omega_motor, gearbox_limit)
rpm_output <= min(Kv*bus_voltage*reserve, gearbox_input_limit)/ratio
```

Solid bands use nominal gear torque and rated input speed; dashed bands use
momentary gear torque and maximum input speed. The same assumed current applies
to both, capped by the sheet's vendor maximum. These are ideal current/power
upper bounds with an explicit speed reserve, **not measured loaded torque–speed
curves**. Resistive drop, motor continuous thermal limits, allowed peak duration,
controller/battery limits, regeneration and mechanical adapter fit are unresolved.
Bus voltage is an explicit scenario input; consult the selected winding's limits.
The map's utilization is max(torque/capacity, speed/speed_bound); the contour at 1
marks the conditional boundary. Colors saturate at utilization 2 but hover keeps
the real value. The 54 candidate rows include duplicate commercial listings.

## Jon V4 integration

`vsl_integration.py` serves the original sibling `v4-pulley.html` on a narrow
allowlisted route and injects only app-owned theme and bridge references. Its
four original inline scripts are preserved exactly. The HTML source hash is
embedded in the served page and saved in transfers. V1–V4 source files are not
copied or edited. `test_vsl_integration.py` checks exact script preservation,
resource allowlisting and preset bytes.

The main V4 tab retains its original parameter controls, finite-idler fitter,
FBDs, signed torque, compensation graphs and native JSON/CSV exports. It pauses
when leaving the tab and retains its mounted state. The bridge defaults to paused.
**Compare this V4 design with motors** takes 181 quasi-static poses and maps a
specified vertical hub speed with the actual Jz (mm/rad). Invalid geometry and
singular/reversing height branches are rejected. It sends actual applied CCW hip
tau2, with speed magnitude, directly to the sizing overlay and candidate table.
V4 is fixed-A with prescribed contact force: changing m1 does not automatically
change Fz. The bridge does not invent a chassis-load or dynamic model.

The overlay uses direct hip drive regardless of the basic model's hip/knee
selector. The sizing torque factor applies explicitly. Basic-model mass contours
remain separate; changing basic controls does not rewrite V4. Transfer again
after editing V4. Save V4 sweep stores parameters, source hash, units and samples
as a dataset in Profiles & data. These records have no fabricated time axis.

The missing sibling AGENTS.md was reported. The user asked to ignore it for this
task and leave a [handoff note](../../../../jonathan-xie/experimental-apps/vsl-solver/context/2026-10-19-agent-entry-note.md)
for Jonathan's next Codex session. No substitute agent rules were invented.

## Validation

- `npm run build`: existing app assets rebuilt successfully.
- `npm test`: 89 tests pass, including eight sizing tests with independent
  potential-energy derivatives, COM kinetic-energy checks, power invariance,
  current/power/gear limits, CSV handling and invalid-input checks.
- `python -m unittest -v test_vsl_integration`: three checks pass.
- Jon's `node verify-pulley.cjs`: all 91,128 original assertions pass.
- `node scripts/verify_sizing.cjs`: actual app navigation, 54 combinations,
  mass sensitivity/fixed spring, explicit retuning, hip/knee conversion,
  invalid input, JSON export, library saves, themes, mobile resizing, V4 transfer
  and 181 exact-source torque/speed comparisons pass without page errors.
- Original `verify_motion_lab.cjs` passes with the two added menu entries,
  including live SciPy/Pymunk APIs and existing JSON/library/comparison flows.
- Project-local launcher exercised from an unrelated working directory: verified
  reuse, scoped stop, restart and HTTP health plus V4 page delivery at port 4186.

Development failures: the first browser load found an HTML input step-base mismatch
for current; numeric controls now allow valid fractional inputs with explicit
bounds. The initial mobile test checked before Plotly's asynchronous resize;
it now waits for measured width to settle. A broad browser regression was
interrupted by the separate server restart check and is rerun sequentially.
No canonical physics, contact, real spring, thermal or hardware validation is claimed.
