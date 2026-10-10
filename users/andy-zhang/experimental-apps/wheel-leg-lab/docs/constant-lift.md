# Constant-lift gravity compensation

Owner: Andy Zhang. Updated: 2026-10-10. Status: user-requested standalone lever study and wheel-leg adaptation, with editable ideal geometry; not selected hardware.

## Browser entry and provenance

The Mathematical Model tab offers **Constant-lift lever** alongside the guided
wheel suspension and detailed linkage models. The same study is available under
Miscellaneous studies and directly at `/counterbalance/`. Use the existing
**Start Motion Lab.cmd** and [port-4186 menu](http://127.0.0.1:4186/); no separate
server or launcher is required. The wheel-leg Mathematical and Physical tabs
also offer the ninth suspension preset, `gravity_balance`.

The [user-provided reference sketch](../references/constant-lift-lever.png)
motivated the study. Its geometry and equations below are implemented explicitly
in [counterbalance.py](../counterbalance.py). Dimensions and masses are editable
demonstrations rather than measurements extracted from the image. Related
primary literature distinguishes ideal zero-effective-free-length balancing
from ordinary coils: [Altenburger, Scherly and Stadler, 2016](https://link.springer.com/article/10.1186/s40648-016-0051-5).
The [IISc-hosted static-balancing paper](https://mecheng.iisc.ac.in/suresh/me254/HandoutsPapers/J68SangameshJMR.pdf)
is retained as further reading; no claim here depends on retrieving that PDF.

## Exact standalone lever

World y points up and theta is measured from horizontal. The fixed pivot is
`O=(0,0)`, the fixed anchor is `A=(0,H)`, the spring attachment is
`B=R(cos(theta),sin(theta))`, and the lever tip/payload is
`C=L(cos(theta),sin(theta))`. The spring span `d` satisfies

```text
d² = H² + R² - 2 H R sin(theta)
dd/dtheta = -H R cos(theta)/d
T_elastic = k d
M_spring = T_elastic H R cos(theta)/d = k H R cos(theta)
F_equivalent = M_spring/(L cos(theta)) = k H R/L.
```

The constant quantity is **equivalent upward force at C**. Spring tension
changes with span, and spring moment changes with `cos(theta)`; neither is
constant. At a vertical lever, `L cos(theta)=0`, so the vertical-force conversion
is undefined even though the algebra has a finite limit. Outputs include
`equivalent_defined`; plots leave singular values empty rather than treating a
zero numerical placeholder as a valid force. A spring attachment meeting the
anchor is also a geometric singularity and is rejected.

For a rigid point payload `m_payload` and uniform lever `m_lever`, exact static
gravity balance requires

```text
k H R = g [m_payload L + m_lever L/2]
k_auto = g L (m_payload + m_lever/2)/(H R).
```

The illustrative defaults are L=400 mm, R=200 mm, H=200 mm, payload=2 kg,
lever=0.4 kg and g=9.80665 m/s². Automatic stiffness is 215.7463 N/m and
equivalent support is 21.57463 N. The lever and rigidly carried point payload
form one dynamic aggregate body with exact combined COM and inertia. No extra
spring/rope/drum mass or friction is introduced.

## Effective spring law versus physical coil

`law=zero_effective` means input tension is proportional to the full geometric
span. It does **not** mean a manufactured coil has zero physical free length.
The standalone emulation reports `coil_length=physical_free_length+d`, with a
positive physical free length (150 mm by default). Suitable ideal preload or
cable-offset routing must produce this extension-to-span relationship; actual
packaging and a real spring implementation remain unspecified.

`law=ordinary` uses tension `k*max(d-effective_free_length,0)`, with a selectable
nonzero effective free length. It can go slack and generally leaves a residual
angle-dependent holding torque. Its equivalent elastic lift is
`kHR/L * max(1-effective_free_length/d,0)`, not a constant. The automatic rate
continues to be the zero-effective reference; it does not make an ordinary coil
exactly balanced. Damping adds a velocity-dependent load and is excluded from
the static constant-elastic-lift identity.

An exactly calibrated undamped compensator is **neutrally balanced**: every
allowed pose is an equilibrium and there is no restoring ride-height stiffness.
An initial velocity persists in the ideal free model; damping can stop motion
at another pose but does not select a ride height. This mechanism cancels gravity;
it is not a complete suspension. Ride-height control, restoring stiffness,
damping and travel reserve require separate design choices.

## Independent and actual physical runs

**Free** mode integrates lever dynamics with SciPy DOP853, using exact pivot
inertia and passive spring/gravity moments. **Prescribed angle** mode computes
finite C2 angle step/square/pulse motion and required driver torque from its
analytic derivatives. The Pymunk counterpart uses an actual PivotJoint and,
only in prescribed mode, an unlimited ideal SimpleMotor commanded by
interval-average angular velocity. The dynamic body is not teleported onto the
reference angle. Joint forces and motor torque are recovered from momentum
balance and checked against public constraint impulses.

Motor tracking has timestep lag. The default 30° / 250 ms step has about 0.225°
maximum tracking error at 1 ms; the focused refinement test requires less than
0.06° at 0.25 ms. Explicit point-spring integration, energy/work residuals and
sharp load peaks likewise require refinement. Free runs end at travel bounds
before a stop-impact model; Pymunk detects a bound crossing after its finite
step. No tire contact, coil bind, rope stretch, transmission friction, structural
stress or hardware limit is certified.

The study has its own backend selector, same-profile math/Pymunk comparison,
JSON profile/run controls, Plotly static/dynamic plots and integration with
Profiles & data. Backend names are `counterbalance_math` and
`counterbalance_pymunk`, separate from wheel-leg records. APIs are
`GET /api/counterbalance/defaults`, `POST /api/counterbalance/math` and
`POST /api/counterbalance/pymunk`. The native GUI envelope is
`{model:'counterbalance',config:...}` sent to `POST /api/native-gui`; it launches
an actual live lever simulation on the host desktop. Browser recorded playback
is labeled separately. These lever profiles are not wheel-height profiles or
MATLAB companion configurations.

From the app root, the standalone CLI accepts either a raw profile or a config
wrapper:

```sh
.venv/Scripts/python.exe counterbalance.py --backend math --output .preview/lever-math.json
.venv/Scripts/python.exe counterbalance.py --backend pymunk --config profile.json --output .preview/lever-physical.json
.venv/Scripts/python.exe -m unittest -v test_counterbalance
```

## Guided wheel-leg adaptation

The `gravity_balance` preset connects a downward chassis mount
`A=(0,-H)` relative to the hip to an upper-link point at distance R from that
hip. Its default upper fraction is 0.5, giving R=136.5 mm for L=273 mm; H=150 mm.
Relative upper-link geometry is `B=(R cos(theta),-R sin(theta))`, so the same
span identity applies. Hip-to-wheel separation is `h=2L sin(theta)`, yielding

```text
Q_spring = k H R cos(theta)
F_chassis_equivalent = Q_spring/(dh/dtheta) = k H R/(2L)
F_gravity_required = g [m_chassis + 0.75 m_upper
                         + 0.25 (1+e/L) m_lower].
```

For the current illustrative fixture masses, required generalized chassis
support is 84.751637708 N. Automatic rate calibration resolves
k=2260.043672222 N/m. Wheel mass affects imposed support reaction and energy;
it is not added to this shape-coordinate gravity demand because wheel height
is prescribed. Zero-effective automatic balance **calibrates stiffness** and
retains positive physical coil free length, rather than silently changing free
length as the ordinary Hooke preload routine does. Saved metadata records the
resolved stiffness, effective/physical lengths and constant-lift eligibility.

The direct-extension emulation uses `coil_length=physical_free_length+span`
with default physical free length 230 mm. Compression pull-through uses
`coil_length=physical_free_length-span`; its free length must exceed the required
span throughout travel. Ideal rope remains tension-only, zero-stretch and 100%
efficient. In both cases the ideal engaged input elastic law can be `T=k*span`.

Exact constant elastic lift requires zero effective input free length, a purely
downward vertical chassis mount and a compatible tension-producing coil/routing.
Moving the mount horizontally, choosing a finite effective free length or
editing the routing breaks the identity. Automatic calibration then balances
the initial pose only, not every angle. The default construction is a neutral
gravity compensator, so restoring suspension behavior must be added separately.

The integrated suite passes 82 Python tests (71 wheel-leg and 11 lever) and 33
JavaScript tests. Browser checks exercise both lever APIs, profile/run JSON,
the shared library and all nine wheel presets. Actual native prescribed/free
lever runs pass live stepping, window restoration and graceful close, alongside
captured-knee and gravity-balance wheel models. Fresh start/reuse/scoped-stop/
restart of the durable launcher passes from outside the app directory. Full
evidence and tolerances are retained in [validation.md](validation.md).
These are ideal mathematical/solver checks, not acceptance of the image's
hardware or a canonical CAMEL robot.
