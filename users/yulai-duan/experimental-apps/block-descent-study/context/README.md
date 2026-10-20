# Block-descent context

Yulai Duan with Codex; October 20, 2026. Publication base: `307aae0`.
Status: experimental studies, not a selected vehicle design or actuator rating.

The team question is whether a gravity-compensating spring also balances an
airborne leg, what finite descent profile follows a square obstacle, and whether
the suspension actuator drives or restrains that motion. Read the
[study index](../../../../../docs/design/simulation/descent-studies.md).

Legacy 13 kg/0° studies use a 100 mm wheel, 8 N/mm spring and 100–165° stops.
The new screenshot baseline uses 8.75 kg/20°, a 200 mm wheel, 5 N/mm spring and
100–180° stops. Both start at 135°. In the new model, spatial x represents Jon's
global y, and forward travel is −y; the opposite-direction draft is excluded.

Hip held means fixed vertical hip position with rotation free. Heave free adds
chassis vertical motion while pitch stays fixed and horizontal speed prescribed.
At 250 mm, 156.6 mm relative extension plus about 93.4 mm chassis descent restores
first floor contact. This is geometric reach, not settled ride recovery.

The new forward held-hip 100/150 mm cases land at 275/299 ms. Larger drops hit the
extension stop. Heave-free cases reach all floors, but have stop hits, recoil and
mass-mismatch drift. The flat-ground control sinks 352.4 mm over one second.
At 135° with hip held and wheel airborne, spring and moving-body gravity both
drive extension; +42.155 N m is the quasi-static holding torque, not a dynamic
motor requirement. The passive runs apply no suspension-motor torque.

Publication changes make paths, font lookup and Node discovery portable; they
do not intentionally change physical parameters, equations or integration.
The retained result files carry original study hashes; the app's publication
manifest compares reruns after this adaptation. No new controlled descent,
full-vehicle, GPU, measured masses, tire calibration or motor thermal test exists.

Next obtain CAD masses/stops, choose a contact-aware braking target, add the
candidate drivetrain inertia/limits, and test four-leg load redistribution.
Keep proposed next work separate from completed results and accepted decisions.
