# Energy-only drop height to braking torque

Andy Zhang / Codex, 2026-10-23. Experimental chassis-only work screen, not a
trajectory integration, peak rating, hardware test or post-arrest guarantee.

Open **Energy only · drop height → braking torque** in either dynamic tab.
It calculates immediately in the browser from the same saved mechanism, spring
and optional motor profile, including the original massless-wheel V4 baseline.
It works independently of terrain/prescribed mode and requires no dynamics run.

The default **50mm residual underbody-to-ground clearance** is different from
**50mm underside offset below hip A**. The former is the requested remaining
ground gap; the latter defines where the chassis underside is relative to A.
An explicit editable1° compression-stop reserve is an illustrative margin.
Zero reserve allows a clearly labeled mechanical-boundary calculation.

## Geometry and work

The saved landing opening fraction f gives
`q0 = tc + f*(te−tc)` (default f=2/3). With the wheel centre held at radius above
stationary flat ground, hip height is `h(q)=rw−Cz(q)` and underbody clearance is
`h(q)−undersideOffset`. The selected endpoint is the earlier of `tc−reserve`
and the target-clearance crossing on monotonic compression.

Using radians for Δq and metres for height, define:

- Drop energy: `K0=m1*g*H=½*m1*v²`, with `v=sqrt(2*g*H)`.
- Gravity released in compression: `G=m1*g*(h0−hend)`.
- Spring released: `S=Uspring(q0)−Uspring(qend)`; negative means absorbed.
- Cogging released: `C=Ucog(q0)−Ucog(qend)` with the fixed motor phase.
- Constant joint resisting magnitude: `τ=max(0,(K0+G+S+C)/Δq)`.
- Motor-shaft resisting magnitude: `τ/N` for active ideal reduction N.

Compression increases q, so the corresponding braking command is **negative**.
Available torque in this calculator is always **joint-side**, independent of the
dynamic command-basis setting. No controller input is automatically changed.

The inverse endpoint drop capacity is
`Hcap=(τavailable*Δq−G−S−C)/(m1*g)`.
A negative value is reported unavailable rather than silently clipped to zero.
This is a sufficient selected-endpoint work screen, not the true global maximum
over intermediate spring/cogging barriers. It assesses initial arrest only;
rebound and holding after arrest still need a controller/trajectory assessment.

For the V4 baseline with H=100mm and1° reserve, q0=121.666667°, qend=164°,
end clearance315.382413mm and Δq=.738856050rad. The spring absorbs29.644002342J,
compression gravity supplies29.638623504J and the drop supplies8.58375J.
The resulting resisting magnitude is11.6103416383Nm;20Nm gives172.214939136mm
endpoint capacity. With the spring disabled the same screen requires51.7318271992Nm.
Here the mechanical reserve limits travel well before the50mm clearance target.

## Assumptions and storage

This screen retains the full chassis m1*g*H without impact-loss credit. Wheel
impact energy is excluded. Rotor starts/ends at rest, so its endpoint kinetic
change is zero; inertia still changes actual impact trajectories and peaks.
Motor/joint friction is given no energy credit. The path must be vertical and
straight (equal links,2:1 guide), with massless moving links/compound pulley,
positive m1/g, no extra prescribed loads and a valid spring cable route.
Unsupported geometry, slack recovery or unavailable stroke is shown explicitly.

Optional saved `energyConfig` holds drop height, clearance target, stop reserve
and available joint torque. Old profiles remain unchanged until edited; Remove
calculator block restores absence. Shared opening/underside controls explicitly
edit the landing case geometry. Energy-only settings do not stale physical
simulation results or alter their engine hashes. Full project and calculation
JSON exports stay inside the app exports/ folder.

The work relation is the rotational work–energy theorem, with constant resisting
work τΔq; see [OpenStax University Physics10.8](https://openstax.org/books/university-physics-volume-1/pages/10-8-work-and-power-for-rotational-motion).
Source spring geometry/energy remains the unchanged V4 reference, and geared
cogging potential follows [motor-model.md](motor-model.md).
