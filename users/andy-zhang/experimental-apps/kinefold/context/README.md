# Kinefold context

Andy Zhang with Codex, 2026-10-22. Started from main `5e52a12`.
Experimental app; no canonical robot or hardware acceptance.

The user requested a separately named future combined motion/terrain/VSL tool,
starting with mechanism builder tab 1 and a conventions tab. The initial two workspaces are now joined by static and quarter-model dynamic
solver tabs, as requested later on the same date. Follow Motion Lab's app-owned
sage/cream shell; terrain remains outside the implemented scope.

Reference source: Jonathan's `vsl-solver/v4/v4-pulley.html`; retained solver,
statics and finite-idler spring blocks are unchanged and hashed in reference.json.
Kinefold's adapter maps source [y,z] to new [-y,0,z], equivalently x=-source_y,
z=source_z, and old +x to new +y. The left-side camera now places +x left and +z up, with +y toward the viewer;
positive +y torque and source-positive rotations appear counterclockwise.
This supersedes the initial x-right preview; physical coordinates, scalar
torque signs and saved designs retain their meanings.
β patch direction is from down toward forward: P-C = rw[sinβ,0,-cosβ].
Positive Ft points backward at β=0 and gives positive wheel τ_y.

V4's default 8.75kg/300mm/200mm-wheel baseline uses its linear coil and exact
finite-idler cable path. An explicitly selected ideal constant-force option
uses k=0 at the entered p0. The stored coil rate survives switching laws.
Weight-reference load follows all five masses; global/contact modes preserve
prescribed force values independently. Fixed-A masses and loads are static;
animation simply prescribes θ2. Remote spring housing is schematic.

No source-app comparison is presented in the product. Motion Lab's V4 iframe
serves Jon's original blocks (see its actuator-sizing record); its separate
SciPy/Pymunk suspension models instead move the chassis and include dynamics.
The owner requested that distinction as a chat answer, not as new tool content.

Validation: `node verify.cjs` passes 2,000 assertions: retained-source parity
(after LF normalization), varied unequal-link geometry, applied world forces,
right-hand-rule moments, FBD/virtual-work balance, both spring laws, energy
finite differences and rejected invalid/unknown JSON. Geometry error is zero;
maximum cable-energy derivative error is 1.74e-9 Nm. Initial harness path/EOL
assumptions failed and were corrected; no physical tolerance was relaxed.
Browser checks verify live length edits, side/isometric/layer controls, constant
force at 160 degrees, mass10kg -> Fz98.1N, global/contact conversion, invalid
idler errors, blank pose handling, playback, dictionary search, independent
section collapse, actual JSON download/import and reload persistence. Browser
warning/error logs are empty. The current desktop viewport was visually checked;
mobile/hardware/full source-app dynamic suites were not run.
Actual app-root launcher started from unrelated working directories, reused its
running instance, stopped only its authenticated service and restarted at the
same URL. All served assets return HTTP200; Python compilation and repository
structure/log/workspace gate checks are performed in final validation.
Canonical physics is NOT APPLICABLE to this isolated member experiment.
Restart: project-local Start Kinefold.cmd; stop with Stop Kinefold.cmd.
URL: http://127.0.0.1:4191/. Python standard library; no package setup.

## X-left preview correction — 2026-10-22

The user requested the entire mechanism preview to face +x left, with +z up.
Both side and oblique projections now flip horizontally, including links,
wheel, spring route, travel, load arrows and dimension geometry; text remains
readable. The left-side camera looks along -y, so +y points toward the viewer
and positive +y moments appear counterclockwise. The overview illustration,
torque arrow, axis markers and dictionary agree with this right-handed frame.
This also corrects the earlier verbal claim that +y would point into the screen.

The 2,000 existing numerical assertions still pass; source geometry/forces and
saved parameter meanings are unchanged. Live browser inspection confirms the
mirrored mechanism and counterclockwise torque illustration; current baseline
readouts remain 435.6mm travel, 570.5N cable force and -442.4mm wheel-centre z.

Final staged checks exposed CRLF-as-whitespace in the new launchers and a Git
hook resolving python3 to the Windows Store alias. The launcher files now use
LF and are rechecked through actual start/stop/restart; hooks use the existing
CAMEL_PYTHON override pointing to installed Python for the publication command.
No hook code, global interpreter setting or shared policy is changed.

## Mechanism inspection and geometrical preview — 2026-10-22

The user requested a UI reassessment against the original two-tab brief, then
specifically asked for geometrically correct previews, a grid, belt rotation
indicators and wheel/pulley index axes. Tab1 remains a mechanism builder and
Tab2 remains conventions; +x left/+z up and +y toward the side-view observer
are preserved. No solver chart, terrain run or optimizer is added.

The preview now uses its actual viewport, readable labels, calibrated mm grid,
Mechanism/Full travel/Spring detail framing, zoom, panning and exact index axes
for all six pulleys plus the wheel. Independent belt material markers use the
carrier-relative angular displacement and exact common-tangent perimeter.
The default wheel stays level because K=0. Pulleys/indices remain visible when
belts are hidden. The isometric camera uses orthogonal equal-length projection
rows; the illustrative wheel width was removed. The remote coil housing alone
remains explicitly schematic; length/radius/tangent geometry shares one scale.

Inputs have direct ? links to their definitions, the parameter column scrolls
independently and its group shortcuts keep the preview in view. Tab2 has top
search, section shortcuts, 81 individually explained variable entries and an
actual baseline topology drawing. Search handles theta2 and Unicode subscripts.

Verification: existing 2000 model checks plus1123 drawing checks pass. Independent
finite-difference velocities on both wraps of all3 belt stages agree with their
pulley surface velocities to1.75e-7mm/rad; index radii and perpendicular axes
are exact within numerical tolerance. Actual rendered side-view femur/wheel
and tibia/wheel radius ratios are1.500008; wheel/grid spacing is2.000025 for the
300mm links/200mm wheel/100mm grid (SVG coordinates round to0.001px). Browser
checks confirm seven axes,32 baseline material dots, pose-dependent belt travel,
zero baseline wheel index rotation, zoom, exact40/30px pan, independent layers,
parameter shortcuts and linked reference search. Browser warning/error logs are
empty. Mobile, hardware and full dynamic source-app suites are not run.
The app server was restarted after adding the new allowlisted browser module.

## Static and quarter-model dynamic tabs — 2026-10-22

The user's new request expands the earlier two-tab scope to five tabs: builder,
conventions, V4 static solver, analytical dynamics and2D Pymunk dynamics.
Static results use the live builder parameters and existing V4 core, including
spring law and load convention; 181 samples provide a labelled sampled peak.
Both dynamic tabs embed actual Motion Lab engines with persistent quarter-model
scope indicators and independent-input/coordinate notices. They do not silently
map the V4 finite-idler architecture into Motion Lab's different dynamic fixtures.
The tab navigation, keyboard order and direct query URLs cover all five entries.

The same-origin-only POST /__kinefold_solvers lazily calls the sibling durable
NoBrowser launcher, verifies app identity/root at4186, and returns readable
startup errors. Shared Motion Lab remains alive when Kinefold stops; its own
Stop launcher controls that service. Existing setup dependencies are unchanged.
Browser verifies static values and connected frames/badges; real one-second
API runs return1000 rows and112 frames from each engine. SciPy warnings are empty;
Pymunk retains its explicit-force timestep-refinement and ideal-rope caveat.
An initial0.05s probe was rejected by existing input validation;1s is accepted.
Existing3123 model/drawing assertions pass. No hardware/canonical physics claim.

## Static import freshness — 2026-10-22

The static workspace now refreshes immediately when a design is imported while
that tab remains selected. The existing V4 core and JSON schema are unchanged.
A real browser file import changed m1 to10kg and theta2 to145deg, immediately
showing Fz98.1N, hip torque -6.014Nm, tension678.474N and sampled peak7.044Nm.
The8.75kg/132.5deg baseline was restored after testing. Browser warnings/errors
were empty and all3123 existing model/drawing assertions passed.
The global footer and opening scope descriptions now reflect the solver tabs.
The user requested GPT-6.1 Sol development agents with the parent handling
architecture and review; that working preference was followed for this finish.
