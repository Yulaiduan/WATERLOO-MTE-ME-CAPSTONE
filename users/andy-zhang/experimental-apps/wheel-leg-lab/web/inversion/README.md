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

Current dual ropes feed through the centre gap and flare over the small rollers
onto knee face anchors, without wrapping around the knee rim. The enlarged
view repeats actual paths. JSON stores the route and eye offset; pre-correction
saved profiles explicitly reproduce outer_rim without modifying recorded data.

## Tight rollers and knee-right demo, 2026-10-11

Current demo: 1 mm clear roller gap, ±0.1 mm cap eyes and ±80° angle stops,
starting at |θ|=45°. The knee remains to the right while the wheel moves above
or below the chassis. Pymunk uses a real fifth constraint, not clipped playback;
independent SciPy uses rigid-stop events, inelastic impact loss and inward-load
release. Current default solver iterations are400. Lead alignment and signed
stop torque are recorded; mathematical impact loss has its own energy channel.
The gap stays fixed when editing roller radius. Session migration updates these
requested geometry/pose settings while retaining other dimensions/input values;
older saved profiles/recordings retain explicit unrestricted reproduction.
See the current invertible model and validation records for exact scope.

## Latest clarification: wrap the knee pulley, 2026-10-11

Current central_wrap replaces the no-wrap interpretation: centre-fed cables
flare over the tight rollers, follow common tangents and knee-rim arcs, then
end at the offset attachments. Cable length and force use those contacts;
the cable can lift off when its attachment faces the cylinder. Demo drum30mm,
ideal gap0.2mm and eyes±0.02mm fit the existing coil/mount and keep pull nearly
axial. Editable knee-right ±80° stops and |θ|=45° start remain. Older central_face
and outer_rim profiles/frames stay reproducible. The latest invertible model
and validation record supersede the earlier no-wrap and wider-gap descriptions.

## Current unloaded contraction,2026-10-11

Dual-rope defaults now use rope_neutral_pose=folded, anchors phi+pi±delta and
cable inventory at theta0. Zero preload gives zero spring force/tension at
contraction; opening compresses the coil. The editable rod is130mm so its eye
clears the unloaded120mm coil. Automatic k matches torque magnitude, not
gravity equilibrium. Missing neutral markers in saved profiles retain the
archived straight phase and saved preload; current sessions migrate only the
requested phase/preload and old demo rod. Older sections describe superseded
routing/reference dimensions. Both solvers/native rendering use the same phase.
