# Load factors, impact travel and motor sizing

Andy Zhang with Codex, 2026-10-14. Status: proposed design envelope, not a measured
terrain shock spectrum or a hardware rating.

## Confirmed inputs and interpretation

The owner estimates a 40–45 kg robot and suggests 3–4g maximum suspension impact
response. Equal four-leg static support is 10–11.25 kg per leg. The study takes
`n` to mean **total vertical support force divided by static weight**, so
`Fz = n*m*g`, with g=9.81 m/s². A chassis upward acceleration of 4g instead
requires 5mg support; that separate stress case is shown rather than silently
using the two definitions interchangeably.

| Supported mass per leg | 1g total support | 3g total support | 4g total support | 5g total support |
| --- | --- | --- | --- | --- |
| 10 kg | 98.10 N | 294.30 N | 392.40 N | 490.50 N |
| 11.25 kg | 110.36 N | 331.09 N | 441.45 N | 551.81 N |
| 22.5 kg, illustrative two-leg support at 45 kg | 220.73 N | 662.18 N | 882.90 N | 1,103.63 N |

Equal sharing is a nominal assumption. Pitch/roll, centre of mass and contact
loss can shift much more than a quarter of vehicle weight to one corner.
The two-leg row is a useful sensitivity, not a claim that every impact is shared
equally by exactly two legs. The initial screenshot's Fy=Fz=100 N remains its
own prescribed-contact case; a mass-derived force is not added to it twice.

## Is 3–4g enough?

It is a reasonable *provisional scenario to investigate*, but no universal
3–4g maximum follows from wheel radius, vehicle mass or this geometry. Terrain
approach speed, drop height, available compression travel, tire compliance,
damping, bump stops and load sharing determine the response. A short shock
and a slowly applied force with the same peak can produce different deflection
and stresses. NASA's [shock-environment discussion](https://s3vi.ndc.nasa.gov/ssri-kb/static/resources/NASA-STD-7003A.pdf)
uses both the transient time history and response spectrum to characterize
shock; that is background for the need to specify a pulse, not an applicable
robot qualification standard or a source for a robot-specific g limit.

A simple energy calculation shows when 4g can be exceeded. Let a vertically
moving mass approach its nominal ride position with speed v, and let δ be the
remaining compression distance. Equivalent drop height is `h=v²/(2g)`.

- An ideal constant-force absorber needs average support factor
  `n_mean = 1 + h/δ` to arrest the motion over δ.
- For an ideal undamped linear **vertical** spring initially preloaded to mg,
  `0.5*k_z*δ² = 0.5*m*v²`, hence peak support
  `n_peak = 1 + v²/(g*δ) = 1 + 2h/δ`.

For example, 100 mm equivalent drop gives v=1.401 m/s. Arresting it in 50 mm
needs an ideal constant-force average of 3mg, while that preloaded linear spring
reaches **5mg peak**. To stay at 4mg in the linear approximation, 100 mm drop
needs at least 66.7 mm compression. If only 20 mm were available, the same
approximation gives 11mg. These are analytical illustrations, not Pymunk
predictions of the actual nonlinear linkage or justification for using a hard
stop as the absorber.

The design's 20 mm end reserve is a geometric exclusion buffer. It is not a
declaration that exactly 20 mm of compliant impact stroke is available. Pick a
ride pose, then evaluate the actual spring-energy rise and remaining travel
from that pose to the compression limit. The generalized spring's coil rate
is not its vertical wheel rate: its Jacobian and preload-dependent geometric
stiffness matter. Zero damping stores and returns energy; it cannot establish
settling or dissipation after impact.

## What the motor numbers mean

The example uses a smooth, 1-second useful-height trajectory, with zero endpoint
velocity and acceleration. It is a motion sizing assumption, not an instruction
for the motor to actively follow a millisecond impact. The inverse dynamics
adds inertia for that trajectory to the actual gravitational/spring load.
The 3g/4g/5g scenarios separately test effective vertical loading; they are
not a second multiplication of already included trajectory acceleration.

Peak joint torque, time RMS, angular velocity and angular acceleration are
reported separately. A spring supporting 1g can still leave a large transient
motor/gear/bearing load at 4g. A fast passive impact may back-drive the motor;
drive-current limits, drivetrain elasticity and control bandwidth determine
how much is actively resisted. For a reduction N=omega_motor/omega_joint,
speed and acceleration grow by N, while motoring torque divides by N times
efficiency; motor/gear inertia must additionally be included when specified.
An ideal output estimate with N=1 and efficiency=1 is not a selected motor.

Use the full speed–torque operating points, RMS duty and dwell, gearhead
intermittent/continuous limits, and driver regenerative/braking behavior before
buying hardware. See [maxon's RMS/load calculation guide](https://www.maxongroup.com/medias/sys_master/8815460712478.pdf)
and [gearhead data definitions](https://support.maxongroup.com/hc/en-us/articles/360012270480-Meaning-of-maxon-s-specified-gearhead-data).
The current numerical study can estimate requirements; actual winding thermal
limits, reflected inertia, efficiency maps and gear shock capacity remain inputs.

## Next measurements that would change this envelope

Record chassis and hub acceleration at a known sampling rate, ride-height
compression reserve, contact count/load sharing, obstacle/drop geometry and
approach speed. Fit a pulse or replay measured wheel displacement; refine the
simulation timestep and check energy/contact/stop convergence. A practical
first review is nominal 1g support, the requested 3g and 4g cases, a labelled 5g
stress sensitivity and unequal support—not a claim that 5g is a proven limit.
