# Controls — illustrative modeling reference

Author: Andy Zhang, with explanatory synthesis by ChatGPT. Updated: 2026-10-10 (America/Toronto).
Status: analytical organizing aid; not a selected robot plant, recovered full transcript or validated controller.
Scope: equations behind the questions in [S02, S05–S06, S10–S12](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts).
Reviewed repository base: `7c5cbc76efd36876e829803efc49578bea24f7fa` (`main`).

[Overview](2026-10-10-chatgpt-controls-overview.md) · [Topics](2026-10-10-chatgpt-controls-topics.md) · [Open questions](2026-10-10-chatgpt-controls-open-questions.md) · [Sources](2026-10-10-chatgpt-controls-sources.md)

The derivations below make the discussion concrete using an ideal MIT torque law, virtual work and local linearization. They are derived explanatory content, not a claim that the missing chat answers used these exact equations. The [current app mathematics](../../../users/andy-zhang/experimental-apps/wheel-leg-lab/math/README.md) remains the source for its implemented nonlinear model and coordinate conventions.

## 1. Define quantities before choosing a controller

The following is a proposed vocabulary for a single-leg study. A quantity's role changes with the selected boundary; for example, MIT gains can be fixed parameters in one model and scheduled control variables in another.

| Category | Illustrative variables | Meaning / units |
| --- | --- | --- |
| References | `z_d`, `q_d`, `v_d` | Desired chassis height (m), joint position (rad), joint velocity (rad/s) |
| Commands | `tau_ff`, or an explicitly selected force/reference command | Additional torque (N·m); task force (N) requires a declared mapping |
| Mechanical states | `q`, `q_dot`, or `z`, `z_dot` in a reduced model | Independent configuration and velocity; do not double-count coordinates tied by a rigid constraint |
| Additional states when modeled | Motor current, integral state, wheel motion, body pitch/roll | Needed only when those dynamics are retained |
| Outputs | Chassis displacement/acceleration, attitude, joint motion, reaction forces | Quantities used to judge or observe response |
| Measurements | Encoder readings, IMU signals, other chosen sensor/estimator outputs | Available data, with frames, filtering and timestamps to define |
| Disturbances | `r(t)`, external force, payload changes | Here `r` is wheel-hub displacement (m); a payload change may instead be a parameter change |
| Parameters | Mass/inertia, geometry, spring law/preload, passive damping, fixed MIT gains | Values assumed constant for the particular model/run |
| Limits | Travel, torque/current, speed, command timing, contact conditions | Constraints on the model and attainable behavior |

For a prescribed-wheel-motion model, chassis height and fold angle may be related algebraically. If both wheel motion and chassis motion are free, additional independent states are needed. The current app holds chassis pitch and prescribes wheel-hub height; that model boundary must be retained when using its equations. [R02–R03](2026-10-10-chatgpt-controls-sources.md#repository-evidence-reviewed)

## 2. MIT law at one declared coordinate

Assume the desired/measured positions and velocities refer to the same independent joint coordinate `q`, and commanded torque is conjugate to that coordinate:

$$
\tau_{cmd}=K_p(q_d-q)+K_d(v_d-\dot q)+\tau_{ff}.
$$

Here `Kp` has units N·m/rad and `Kd` has units N·m·s/rad in this illustrative physical convention. Vendor fields may be scaled differently or refer to motor-side coordinates; that must be verified for the actual drive. `tau_ff` is additive effort, not a gain.

If `q_d(t)` is a desired trajectory, choosing `v_d(t) = d q_d / dt` makes the references kinematically consistent. Other combinations are possible, but they deliberately request both position-error and velocity-error torque and must be analyzed accordingly. Actual torque tracking, clipping and delay are separate dynamics/constraints.

## 3. How MIT changes the plant seen by an outer controller

For a local perturbation about a fixed equilibrium, suppose the reduced joint mechanics are

$$
I_e\ddot{\delta q}+B_{pass}\dot{\delta q}+K_{pass}\delta q
=\delta\tau_{cmd}+\delta d_q.
$$

`Ie` is effective inertia; `Bpass` is passive damping; `Kpass` is the local total passive restoring coefficient, including geometry and gravity effects retained in this model. These are local coefficients, not automatically a spring's catalogue values. Static bias is removed through the equilibrium definition.

With ideal torque tracking and fixed MIT gains, substitution gives

$$
I_e\ddot{\delta q}+(B_{pass}+K_d)\dot{\delta q}
+(K_{pass}+K_p)\delta q
=K_p\delta q_d+K_d\delta v_d+\delta\tau_{ff}+\delta d_q.
$$

Thus, for zero initial conditions,

$$
\delta Q(s)=
\frac{K_p\delta Q_d(s)+K_d\delta V_d(s)+\delta T_{ff}(s)+\delta D_q(s)}
{I_e s^2+(B_{pass}+K_d)s+(K_{pass}+K_p)}.
$$

The torque-to-angle mechanical plant and the feedforward-torque-to-angle plant with MIT feedback closed therefore have different denominators. A position-trajectory input has numerator `Kp + Kd s` only when `Vd = s Qd` under the stated initial-condition convention; independently supplied `v_des` is its own input.

For positive total stiffness in this second-order approximation,

$$
\omega_n=\sqrt{\frac{K_{pass}+K_p}{I_e}},\qquad
\zeta=\frac{B_{pass}+K_d}{2\sqrt{I_e(K_{pass}+K_p)}}.
$$

This shows why Andy's natural-frequency question and the inner-gain question are connected. It does not establish stability of a delayed, saturated, time-varying or contact-switching robot. An outer controller must be analyzed with the inner feedback already included, or with all loops modeled explicitly.

## 4. Linkage position, velocity and force mappings

As an ideal equal-link example, let `q` be fold angle from downward vertical and `ell` the vertical separation between chassis hip and wheel hub:

$$
\ell=f(q)=2L\cos q,\qquad J_\ell(q)=\frac{d\ell}{dq}=-2L\sin q.
$$

Then

$$
\dot\ell=J_\ell\dot q,\qquad
\ddot\ell=J_\ell\ddot q+\dot J_\ell\dot q,\qquad
\tau_q=J_\ell F_\ell.
$$

`Fell` is force conjugate to increasing separation. The last relation follows from equal virtual work, `tau_q dq = Fell d ell`; its sign depends on that force/coordinate definition. IK gives `q = acos(ell / (2L))` only on the chosen feasible branch. It does not appear merely because a torque command is being issued: use the mapping appropriate to the signal being converted.

At a fixed, nonzero Jacobian, an unloaded or sufficiently simple constant-geometry approximation maps joint impedance to vertical impedance as

$$
K_{\ell,virt}\approx\frac{K_p}{J_\ell(q_0)^2},\qquad
C_{\ell,virt}\approx\frac{K_d}{J_\ell(q_0)^2}.
$$

Preload, nonzero nominal effort and changing geometry can add stiffness terms; these formulas are not the full loaded-leg stiffness. Near a zero Jacobian, inverse mappings and this local approximation are unsuitable without additional analysis; an apparent divergent force/stiffness conversion does not establish usable physical capability. The same physical geometry can appear with sine instead of cosine when the angle is measured from horizontal; reconcile coordinates with the app rather than changing formulas by visual resemblance.

## 5. Reflect a physical spring through its actual geometry

Let a bilateral linear spring have extension coordinate `x_s(q)`, free/reference length `x_0`, rate `k_s`, and span derivative `J_s = d x_s / dq`. Its potential and generalized force are

$$
V_s=\tfrac12 k_s(x_s-x_0)^2,\qquad
Q_s=-\frac{dV_s}{dq}=-F_sJ_s,\qquad F_s=k_s(x_s-x_0).
$$

The local spring contribution to restoring stiffness is

$$
K_{s,q}=\frac{d^2V_s}{dq^2}
=k_sJ_s^2+F_s\frac{d^2x_s}{dq^2}.
$$

A simple viscous damper along the same span contributes `B_s,q = c_s J_s^2`. Evaluate these coefficients at the selected operating point; the preload/geometry term can be negative even when the material spring rate is positive. Total passive restoring stiffness also includes the other retained potential-energy terms, such as gravity. One-sided springs, slack ropes, nonlinear laws and changed attachment geometry need their own piecewise/generalized force models.

This is why a physical `N/m` spring rate cannot be added directly to MIT `Kp`, and why a universal pulley multiplier is insufficient without a defined spring and coordinate. A factor of four can arise when a linearized angular displacement doubles, but it is not a general result for every knee spring or cable routing.

## 6. A simple chassis model with a moving wheel input

Let `z` be upward chassis displacement and `r` upward prescribed wheel-hub displacement, both measured from static equilibrium. For an illustrative lumped vertical mass with linear passive spring/damper and active force `Fa`,

$$
m\ddot z+c(\dot z-\dot r)+k(z-r)=F_a+F_d.
$$

Gravity is already balanced at the chosen equilibrium. `z` is inertial chassis-position deviation; `z-r` is the change in chassis-to-wheel separation. These are different control outputs when the wheel moves. Joint-relative MIT damping maps to relative extension velocity under this geometry, not automatically to inertial chassis velocity.

Here `k` and `c` are passive coefficients if `Fa` separately includes MIT-derived feedback; do not include the same virtual stiffness/damping in both places. If the MIT law is substituted and combined into effective coefficients, state the associated reference and geometry assumptions.

This equation distinguishes a wheel-position disturbance from an externally applied force. A physical ground profile equals wheel-center motion only under additional contact/tire assumptions. The current app's nonlinear moving-base model includes configuration-dependent inertia and distributed link mass; this lumped model is not a replacement for it. [R03](2026-10-10-chatgpt-controls-sources.md#repository-evidence-reviewed)

## 7. The whole-body extension

For a small-motion vertical-force illustration, take body axes `x` forward, `y` left and `z` up. At leg positions `(a_i, b_i, 0)` relative to the chosen body origin,

$$
\begin{bmatrix}F_z\\M_x\\M_y\end{bmatrix}
=
\begin{bmatrix}
1&1&1&1\\
b_1&b_2&b_3&b_4\\
-a_1&-a_2&-a_3&-a_4
\end{bmatrix}
\begin{bmatrix}F_1\\F_2\\F_3\\F_4\end{bmatrix}.
$$

The `Fi` here are net transmitted support forces, not just active motor contributions. An actuator can oppose some passive spring force while the net ground contact remains compressive. Use force directions and lever arms expressed in the same frame; significant body tilt requires the appropriate transformations.

This is a force/moment allocation relationship, not a complete controller or full vehicle dynamics. Gravity, inertia, real contact directions, traction, support constraints and actuator limits still matter. It explains why a whole-body heave/pitch/roll problem is multivariable even if the first selected scalar torque-to-joint-angle channel is SISO; independently commanded MIT reference fields instead create a multi-input local model.

## Validation and three-sentence handoff

These equations were reviewed as illustrative analytical relationships; no numerical robot response or hardware validation was performed in this contribution. Their purpose is to make the plant boundaries, units and assumptions explicit enough to continue Andy's questions. Replace them with the selected geometry, actuator interface and measured parameters when defining an executable control model, and keep the owning app/engineering record authoritative.
