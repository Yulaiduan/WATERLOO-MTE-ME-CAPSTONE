# Screenshot equation cross-check

Source: the user-provided Desmos screenshots, retained in `references/equations-1.png`, `references/equations-2.png` and the clearer `references/equations-complete.png`. They are reference mathematics, not executable instructions. The clearer image resolves the wheel-radius term and the distinct T0 force; numerical parameter definitions are still incomplete.

## Coordinate and variable mapping

The visible lower-link moment expression is consistent with reference **y = horizontal**, **z = vertical**, and **θ measured from horizontal**. In the engine, world **x = horizontal right**, **y = vertical up**. Thus reference `F_y → engine F_x` and `F_z → engine F_y`. The engine has separate instantaneous upper/lower angles; use each link's own angle for checking its moment, instead of silently assuming zero constraint drift.

For an actual lower-link free body, the wheel force on that link is minus the J3 force on the wheel. It differs from the prescribed force at the wheel body's centre when wheel gravity and inertia contribute. The force on the upper link from the lower link is minus the reported J2 force on the lower link.

Names are not interchangeable: screenshot `q` is the **sign of a moment**, not the previous simulator's folding coordinate; screenshot `f1` is an **absolute moment in N·m**, not the hip joint force J1; screenshot `T` and `T0` are distinct belt-force quantities, not the suspension spring tension; screenshot `beta` is a proposed belt-span angle, not the lower-link absolute orientation.

## Visible equations retained

```text
F_z = g_z * (35 * 1.3 / 4) * 9.81
F_y = g_y * (45 / 4) * 9.81
M_in(theta) = L2 * (-F_z cos(theta) + F_y sin(theta)) + F_y r_w
f1 = abs(M_in)
q = sign(M_in)
T = M_in / (q r_B)
beta = theta - q asin(r_B / L1)
B_y = F_y - T0 cos(theta) - T cos(beta)
B_z = F_z + T0 sin(theta) + T sin(beta)
M_act_visible = L1 * (B_z cos(theta) + B_y sin(theta))
B_r = sqrt(B_y^2 + B_z^2)
g2 = 50 + F_z - B_z + T sin(beta)
g1 = 67 + F_y - B_y - T cos(beta)
r_s = 0.04
```

The displayed load values are `F_z = 111.58875 N` and `F_y = 27.590625 N`. The latter corresponds arithmetically to `g_y = 0.25`; the former to `g_z = 1`. With the confirmed 0.2 m wheel radius and the now-complete moment expression, the screenshot's two reported torque values imply **L1 = L2 = 0.4 m**. At 0°, `(M_act + F_y r_w)/F_z = L1 + L2 = 0.8 m`; the 42° value gives `L1 - L2` equal to zero within its printed precision. The reference then reproduces **83.752875 N·m** at 0° and **60.82315671519248 N·m** at 42°.

This is a **conditional reconstruction**, not independent confirmation of the sheet's dimensions or physical belt routing. The 400 mm lengths are inferred, while the bench's unchanged default is 273 mm each. The two torque values are reproduced without r_B or T0 because those terms cancel from this moment expression; numerical belt/bearing loads still require their values and interpretation.

## Algebraic reduction of the belt reference

For nonzero M_in, `T = abs(M_in)/r_B` and `qT r_B = M_in`. Substituting the visible B components into the visible M_act expression gives

```text
M_act_visible = L1 (F_z cos(theta) + F_y sin(theta))
              + L1 T sin(beta - theta)
              = L1 (F_z cos(theta) + F_y sin(theta)) - M_in.
```

The T0 terms cancel because their force lies along the upper link. This identity holds for distinct T0 and T; it does not require T0 = T. Substituting the newly visible wheel-radius term gives

```text
M_act_visible = (L1 + L2) F_z cos(theta)
              + (L1 - L2) F_y sin(theta) - F_y r_w.
```

For equal links, the link-lever horizontal terms cancel, but the **wheel-radius horizontal moment remains**: `M_act = 2 L F_z cos(theta) - F_y r_w`. T0 changes B_y/B_z and B_r even though it cancels from this actuator-moment expression. The two offset expressions reduce to `g2 = 50 - T0 sin(theta)` and `g1 = 67 + T0 cos(theta)`. These are algebraic identities within the reference assumptions, not independent validation of the belt routing or pretension model.

`equation_checks.screenshot_reference(...)` evaluates the complete visible chain with explicit L1/L2/r_B, **r_w and T0**. It also accepts optional additional moments and offset values for extended cases; those are not part of the now-complete visible M_in expression. Lengths are metres, angles are supplied in degrees and converted to radians, forces are N, and moments are N·m. It rejects invalid asin domains. At M_in = 0, the original `0/0` expression is replaced by its continuous force limit T = 0; the tight-span direction is reported as undefined. The independent T0 force remains in B.

The user subsequently confirmed **T0 is belt tension**. Its numerical value and whether it represents a slack span, tight span, or separate belt have not been provided. It remains independent of T(theta) and of the suspension spring tension.

The 50/67 force offsets and `r_s` are retained without assigning a physical source. In particular, `r_s = 0.04` is not silently treated as the present 50 mm lower-link extension.

## Checks inside the Pymunk trace

Each solver row now includes:

- Reference-coordinate F and B components.
- `ref_Min_wheel_moment`: the visible lower-link wheel-force moment.
- `ref_Min_contact_moment`: the bottom-contact lever expression including F_y r_w; it is checked against the direct moment of a hypothetical force at that bottom point.
- Actual external wheel moment and wheel-drive reaction torque, including wheel angular inertia when the drive is locked.
- `ref_Mact_knee_moment`: the visible upper-link knee-reaction force moment.
- `ref_Br`: the reference resultant-force magnitude.
- Direct cross-product residuals for both force-moment expressions.
- Full lower and upper link moment-balance residuals, including actual spring torque, gravity, motor, guide, stops and inertia.
- Resultant-force residual against Pymunk's J2 constraint impulse divided by dt.

For a moving reference point K, the inertia term is `I_COM alpha + (COM-K) × (m a_COM)`. It is not replaced with `I_K alpha` without accounting for K's motion. The static reference contributions are not labeled as the complete actuator torque during a transient.

The browser section **Equation cross-check · reference screenshots** exposes the expressions and current residuals. Full trace CSV and saved run metadata retain the checks. Horizontal load bias is independently editable; the disturbance waveform remains vertical or knee torque as before.

## Wheel-radius torque in the actual solver

The previous hub-force mode applies horizontal force through the wheel centre, giving no radius moment. The new **Tire bottom** input applies the force at `(hub_x, hub_y - radius)`, so Pymunk generates the actual moment `F_x * radius`.

A **free wheel** responds by spinning; its ideal pin does not transmit a couple to the lower link. Selecting **Lock wheel drive to lower link** adds an actual ratio-1 GearJoint between lower link and wheel, modeling zero relative wheel-drive speed. It transmits the reaction into the lower link and includes the wheel's rotational inertia. In static equilibrium, the lower-link reaction equals F_x r_w. During motion it is `F_x r_w - I_w alpha_w`. The reaction is reconstructed from wheel angular momentum and checked against the engine's drive-joint impulse.

This is not a ground-contact constraint or a rolling/traction model. The load is prescribed at the tire bottom. The locked drive is available only with the hip fixed; locking the wheel to the lower link while the wheel fixture is fixed would remove the intended folding degree of freedom. Spring auto-balance includes the transmitted constant wheel-contact torque when that mode is active. Original free-wheel/hub defaults are retained.

## Important physical boundary of the comparison

The screenshot's B_y/B_z expressions include explicit belt-span forces. The current model has an ideal angular GearJoint, which resolves equivalent motion and constraint couples but does not represent individual belt spans, pretension or pulley-bearing force distribution. Accordingly, the screenshot's full B must not be compared directly to the ideal model's pivot reaction as though both represented identical bearing loads. The force-resultant identity and generic r×F moments are checked against the engine; the explicit span model is retained separately.

Completing that bearing-load comparison needs belt routing, tight/slack tension interpretation, pulley radii and the T0 value. If T0 is physically the slack-span tension and T is the tight-span tension of the same pulley, its moment normally depends on their **difference**; the sheet's T = abs(M_in)/r_B would then need an interpretation or adjustment. T0 is therefore kept independent without assigning an unconfirmed physical role. No actual pulley bearing loads are fabricated from the reference algebra.

## Validation

`python -m unittest -v test_physics test_equation_checks`: the reference suite checks distinct T0 values, wheel-radius moments, both moment signs and different pulley radii. Zero moment and invalid-radius domains are covered. The free-wheel/contact case spins without adding lower-link torque; the locked-drive/contact case transmits the expected static torque, with an engine-impulse check. Live mapped moment/resultant and full link balance residuals pass for both fixtures with nonzero horizontal loading; observed errors are around numerical roundoff, below 1e-7 N or N·m in the checked cases. Independent RK4 trajectory/refinement checks remain unchanged for the original mode and are extended to locked-wheel inertia.
