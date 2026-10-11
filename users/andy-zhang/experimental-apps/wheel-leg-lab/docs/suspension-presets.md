# Suspension spring presets

Owner: Andy Zhang. Updated: 2026-10-10. Status: editable experimental interpretations of the user's sketches, not selected or measured hardware.

Source sketches: [six suspension layouts](../references/suspension-layouts.png)
and [internal pulley / pull-through capture](../references/pull-through-capture.png).

## Nine mechanisms

The Mathematical and 2D Physical tabs share this catalog. The original spring remains available alongside six sketch mechanisms, the internal knee capture arrangement and the later constant-lift gravity compensator. Selecting a preset loads demo geometry and a default coil/routing law; mounts, lengths, radius, direction, free length, stiffness and damping remain editable. The leg's physical 2:1 guide remains separate from the suspension drum.

| Preset ID | Mechanism and physical force sites | Default coil / transmission |
| --- | --- | --- |
| `legacy_tip` | Original hip-to-lower-link extension tip, 50 mm beyond knee | Captured / direct |
| `hip_pulley` | Ideal drum at hip; tangent force pair on upper link and chassis | Extension / direct |
| `knee_pulley` | Ideal knee drum using relative link rotation; tangent force pair on lower and upper links | Extension / direct |
| `direct_scissor` | Coil between editable points along the two links | Compression / direct |
| `hip_bellcrank` | Rigid crank on upper link at hip, connected to an editable chassis mount | Extension / direct |
| `knee_bellcrank` | Rigid crank on lower link at knee, connected to an editable upper-link point | Extension / direct |
| `chassis_direct` | Editable lower-link point to an editable chassis mount | Compression / direct |
| `knee_capture` | Internal knee drum payout pulls a rigid rod through a compression coil; the external load is tension | Compression / pullrod |
| `gravity_balance` | Downward vertical chassis mount to an upper-link point; zero-effective-length tension converts into constant generalized chassis lift | Extension / direct, `zero_effective` law |

The catalog is defined in [spring_mechanisms.py](../spring_mechanisms.py) and returned by `GET /api/spring-presets`. Current curated rates/damping and leverage are listed in the [mechanism audit](mechanism-audit.md). Common illustrative geometry includes 200 mm input/coil reference spans, midpoint attachments and a chassis mount at (120, 50) mm; hip/knee crank offsets are 135°/180°. Hip drum and hip crank now use 80 mm leverage; other mechanism geometry is explicit in the catalog. These are editable illustrations; the confirmed fixture inputs remain the 200 mm wheel radius and original 50 mm link extension. They do not establish spring packaging, travel clearance or component ratings.

## Coil loading and transmission are separate choices

**Compression** coils carry load only while shorter than their free length. **Extension** coils carry load only while longer than their free length. **Captured** is a bilateral ideal coil law that permits both signs; this law is distinct from the `knee_capture` mechanism name. A disengaged coil has zero elastic and damper load and is shown relaxed at its free length. The nominal geometric coil span is reported separately.

Let `ell` be the mechanism input span, `ell_ref` its initial reference and `c` the coil length. Direct routing uses `c=ell`, so `eta=dc/dell=+1`. Rigid pullrod and the ideal compression pull-through rope use `c=c_ref-(ell-ell_ref)`, so `eta=-1`: **increasing input span compresses the coil**. This does not determine which leg motion compresses it. Mount geometry or pulley wrap/direction determines `dell/dtheta`; both payout directions are selectable.

Positive `T_input` contracts the input span. With active coil deformation `delta=c-free_length`, the signed elastic input tension is `eta*k*delta`, and the generalized spring force is

```text
Q_theta = -T_input * d(ell)/d(theta).
```

For hip payout, `ell=ell_ref-direction*r*(theta-theta_ref)`. Knee and internal capture payout use twice the shape angle: `ell=ell_ref-direction*2r*(theta-theta_ref)`. Direct/crank spans and their Jacobians follow the actual attachment separation. Coil damping is a separate dissipative term; ideal transmission efficiency does not remove damping loss.

A rigid rod can transmit either force sign when its selected coil law permits it. An **ideal rope is tension-only, massless, zero-stretch and 100% efficient**; it cannot push and has no damper load while slack. In this compression pull-through mapping, an extension-only coil on the ideal rope remains slack. Extension operation needs direct routing or a separately specified routing, rather than a silent sign reversal.

## Preload and physical loads

Automatic balance solves the initial static support requirement using the selected mechanism's leverage and coil law. Dead centres, incompatible one-sided preload directions, coincident anchors and nonpositive payout/coil/free lengths fail explicitly. A rejected combination is not repaired by inventing a holding torque; change its routing/mounts or disable automatic balance to study the resulting motion.

All nine current Pymunk presets use `spring_integration=point_force`:
[suspension_runtime.py](../suspension_runtime.py) applies spring force pairs at
direct anchors or drum tangent sites before `Space.step(dt)`. Their moment arms
retain spring-transmission pin/bearing loads. Explicit integration requires
timestep refinement. `native_legacy` retains DampedSpring only for explicitly
selected `legacy_tip/captured/direct/hooke` diagnostics and warns about
constraint/spring splitting bias. The separate 2:1 guide belt's optional tension
arrows are viewer assumptions, not additional solver bearing forces.

The drum, bellcrank and pullrod are ideal massless transmission geometry, not additional inertial bodies with their own bearings or contacts. The model excludes rope stretch/sag, transmission friction, coil solid height/bind, attachment contact and hardware stress. Wheel-height support is prescribed and bilateral; tire contact and terrain compliance are not solved.

## Independent mathematics and exports

The [Python/SciPy energy model](../math/README.md) supports all nine mechanisms and reconstructs instantaneous loads from the same specified force sites while integrating independently of Pymunk. Pymunk reports step-averaged constraint loads from impulses; SciPy uses adaptive integration and its `dt` controls exported sample spacing. Compare smooth motions and refine output/timestep rather than equating instantaneous mathematical loads with unresolved stop impulses.

The MATLAB/Octave companion currently supports **only `legacy_tip` + captured + direct**. Other configurations are explicitly rejected. Saved JSON profiles retain topology, coil mode, transmission, dimensions, direction and preload settings; run data also includes coil travel/load, input tension, engagement/slack and spring energy.

Current actual evidence is centralized in [validation](validation.md).
The [mechanism audit](mechanism-audit.md) owns curated rates, passive-stability
classification and the finite six-second demo envelope. Edited profiles are not
certified by a preset's previous results. Initial balance alone does not prove
restoring behavior; passive stability excludes any enabled controller.

Historical superseded example (2026-10-10): the 40 mm hip drum with an 8 kN/m
coil was unstable near 45°, with acceleration slope about +15.63 s⁻². The current
hip demo uses 80 mm leverage and increased damping. This repair is explicit;
no artificial holding motor hides passive instability. Historical release
counts and short-step results remain in validation with their original scope.

## Constant-lift addition

The ninth preset is `gravity_balance`.
Its [full derivation and standalone lever study](constant-lift.md) distinguish
constant equivalent support from variable spring tension/moment. For the
vertical-mount wheel geometry, ideal lift is `kHR/(2L)`, including distributed
link weight in automatic rate calibration. `spring_force_law=zero_effective`
with `spring_effective_free_length=0` describes an input law, while the physical
coil retains positive free length. Direct extension length is `free+span`;
compression pull-through is `free-span` and must stay positive.

Automatic zero-effective balance calibrates and records spring stiffness;
ordinary Hooke automatic balance instead adjusts free length/preload. A finite
effective free length or horizontal chassis-mount offset makes exact lift vary
with angle, even when the initial pose is calibrated. Exact undamped gravity
compensation is neutrally balanced without ride-height restoring stiffness, so
it does not supply restoring ride-height stiffness. The current one-unit
[replacement architecture](suspension-architecture.md) keeps that limit explicit
and adds damping to the same unit, with auxiliary off. Validation is recorded in
[validation.md](validation.md).

Primary API references: [Pymunk body forces and Space](https://www.pymunk.org/en/latest/pymunk.html), [constraints and DampedSpring](https://www.pymunk.org/en/latest/pymunk.constraints.html), and the [official Pygame debug renderer](https://www.pymunk.org/en/latest/pymunk.pygame_util.html).
