# Actual wheel / terrain contact

The saved **Terrain contact / V4 + 1.5 kg free wheel** demo is separate from
the original prescribed-height bench. It retains the final V4 geometry, including
the **200 mm wheel radius**, m₁ = 8.75 kg and massless links/compound pulleys.
The user explicitly selected a 1.5 kg wheel, effective friction μ = 0.8, zero
bounce and freely backdrivable drive. Step height, plateau and gap are 150 mm;
terrain speed is 100 mm/s, first-contact delay 0.5 s, declared dt 0.00025 s.
These editable study assumptions are saved with the complete project.

## Why the old wheel did not collide or spin

The original Kinefold bench prescribes wheel-centre height and locks θ₄. With
baseline K = 0 the wheel index therefore remains fixed while the leg folds.
Its moving floor is an explanatory height driver, not collision geometry.

Motion Lab's ordinary [`physics.py`](../wheel-leg-lab/physics.py), lines159–170
and216–225, also uses sensor geometry and an optional bilateral moving carriage.
Its separate [`inversion.py`](../wheel-leg-lab/inversion.py), lines92–123, supplies
real circular-wheel/segment contacts but uses friction0 and positive link masses.
Kinefold reuses the contact/body concepts, not those tabs, masses or spring model.
Neither reference justified pretending the old height driver was terrain contact.

## Bounded physical model

Two actual Pymunk dynamic bodies represent chassis and wheel. The chassis has
vertical translation, fixed x and fixed pitch. The positive-mass wheel is a
uniform solid disc with I = ½m₆r_w², actual free rotation and a non-sensor circle.
A chassis-relative GrooveJoint exactly represents the massless straight wheel
path. Equal L₂/L₃ and r_a/r_b = 2 are required; α/φ₀ may rotate that line, provided
the complete working interval has a nonzero, monotonic path Jacobian. No small
substitute link masses, fake wheel inertia or hidden drive lock are inserted.

Curved paths, nonzero m₂/m₃/m₅, custom link/wheel inertias, an empty/singular
working interval, prescribed contact-component loads and nonzero input-rise
distance are rejected explicitly. Global additional wheel loads remain separate
from real gravity/contact. Weight-reference loading is not applied as extra mg.

Spring, hip and damping torque generate an equal/opposite internal guide force:
`F = (τ_S + τ_hip − c_q q̇)/(dC/dq · guide_axis)`. Gravity acts once on each real
body. The wheel's own weight increases ground support without becoming extra
chassis suspension demand. Contact impulses and wheel spin are solved by Pymunk.

The free massless drive backdrives through the exact ideal belts:

```text
θ₆ = K(θ₂ − θ₂ᵉ) + θ₄/(q_dc q_fe)
θ₄ = q_dc q_fe [θ₆ − K(θ₂ − θ₂ᵉ)]
θ₅ = (1 − 1/q_dc)(θ₂ − θ₂ᵉ) + θ₄/q_dc
```

World wheel-body angle + α gives the source-local θ₆ index. Pulley a stays fixed;
c follows θ₄, d/e follow θ₅ and f/wheel follow actual spin. Belt material travel
includes drive motion, with independent finite-difference no-slip checks.

## Real square mesh, corners and gaps

The saved world collision polygons translate toward −x (screen right) with the
actual kinematic ground body. They do not recenter under C or prescribe its height.
The wheel can roll, slip, separate or bridge a gap. Requested square geometry
does not imply that the centre must jump150 mm or descend fully into every gap.

Initial clearance includes the circular rim. For H < R, leading upper-corner
reach is √(2RH−H²); for H ≥ R the vertical face first meets the side at R. The
R200/H150 demo therefore starts with193.649 mm clearance plus speed×delay.
At150 mm gaps a400 mm diameter wheel bridges corners; that is expected geometry.

Effective pair friction is0.8, implemented without accidentally squaring it to0.64.
SI collision slop is explicitly0.001 mm. Forces are accumulated post-solve impulses
over each output interval divided by elapsed interval, not the last substep or a
certified continuous impact peak. The run stops with a partial result above1 mm
penetration, rather than pushing an impossible kinematic wall through the wheel.
Refine dt before interpreting corner loads. Chassis/body collision, compliant
tires, 3D clearance and four-leg/hardware behavior remain outside this model.

## UI, storage and validation

The Pymunk tab and studio library create the separate contact demo deliberately,
preserving original named designs and backing up an unsaved working snapshot.
An optional project-v3 `contactConfig` stores mode/friction/restitution/drive;
old projects without it remain byte-equivalent in their physical fields.
Both independent contact engines now compare the same captured profile; see [contact-scenarios.md](contact-scenarios.md). The original prescribed-height bench is a separate model. Contact charts
show actual spin, interval normal/tangential forces, slip, gap/penetration and
guide residual; unavailable prescribed-input/acceleration/work residuals stay null.
The browser and desktop window render returned actual mesh/body transforms.
The native window is results playback of an actual Pymunk run, not a web embed.

Run app `.venv` Python `verify_contact.py`: eight groups cover virtual work,
gravity, friction/no-friction controls, sharp corners, gap bridging, guards and
refinement. At dt0.00025 s the default completes6.5 s/26000 steps, first raised
contact0.5 s, max penetration0.004187 mm and guide residual0.000749 mm. Flat support
is100.552499 N versus100.552500 N expected; steady spin28.647890°/s versus28.647890
expected. Frictionless spin stays0 with−100 mm/s slip. R100/H150 tall-wall control
stops at0.51275 s after crossing the declared penetration limit. Refinement reduces
heave error0.02938→0.00834 mm and penetration0.06699→0.01675→0.004187 mm.

`node verify-contact-drawing.cjs` checks666 index/material-motion assertions,
including tilted mounting and nonunit drive ratios. Profile tests check optional
contact roundtrip and unchanged old records. The actual contact Tk automated
self-test exercises opening, pause/scrub/replay and auto-close; initial/no-contact
slip remains unavailable. Manual native visual inspection for this change was
occluded by another foreground app and is not claimed.


Optional hip rotor inertia is now supported by both independent engines, including
contact and travel-stop impulses. The analytical variable mass and native Pymunk
scalar rotor constraint are described in [motor-model.md](motor-model.md).
The native nonzero-inertia path is guarded to its verified ABI; it never changes
wheel mass or spin inertia to imitate hip inertia. Motor/gear/loss settings are
shared saved profile fields, distinct from freely backdriven wheel drive.
