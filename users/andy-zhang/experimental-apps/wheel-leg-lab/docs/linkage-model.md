# Belt linkage model and conventions

This is a fixed-pivot linkage bench. Its two independent coordinates are suspension fold `q` and coaxial wheel-drive shaft rotation `phi`. The guide belt constrains the second link; it is not a second independently commanded shape hinge. The passive suspension spring acts in parallel with the fold actuator. Wheel drive has its own control channel.

The geometry comes from the user-referenced [curated rough-animation handoff](../context/README.md). The simulator implements an ideal rigid-link, no-slip belt model with editable dimensions and inertias. Defaults are design assumptions pending hardware measurements.

## Coordinates and belts

`A` is the fixed upper pivot. World `x` points right and `y` points up. At `q = 0`, the upper link points vertically down. The guide belt gives the lower-link absolute orientation

`beta = (1 - rs) q + phase`.

For the reference grounded guide ratio `rs = 2` and zero phase, `beta = -q`. Thus

`B = [L1 sin(q), -L1 cos(q)]`

`C = B + [L2 sin(beta), -L2 cos(beta)]`.

With equal links, `xC = 0` and extension is `2 L cos(q)`. Unequal links or a changed guide ratio generally create lateral wheel-centre travel.

The independent wheel-drive belts are described using carrier-relative rotations:

`alphaB = r1 phi + (1 - r1) q`

`thetaWheel = r2 alphaB + (1 - r2) beta`.

Consequently wheel rotation is `a phi + b q`, where `a = r1 r2` and `b = r2 (1-r1) + (1-r2)(1-rs)`. The reference two 1:1 stages give `thetaWheel = phi`, independent of folding. A general product of one does not alone guarantee folding cancellation for arbitrary stage ratios. Belt ratio signs and the guide phase refer to these equations, rather than an ambiguous tooth-count label.

## Forces and moving inertia

Translational kinetic energy uses the upper-link centre of mass, lower-link centre of mass and wheel centre. Rotational energy includes independently entered link inertias about their centres of mass, intermediate rotating drive parts, wheel spin and actuator/shaft inertia. Default rod estimates apply to the default dimensions; changing a link's mass or length does not silently recalculate its entered inertia. For point Jacobians `J_i` and angular velocity coefficient vectors `w_i`, the generalized mass matrix is

`M = sum(m_i J_i^T J_i) + sum(I_i w_i w_i^T)`.

This preserves coupling between fold and drive when the carrier equations generate it. Gravity uses the actual moving mass heights. Prescribed forces at the wheel map by virtual work, `Q = J_C^T F`; prescribed wheel torque maps through the wheel-angle gradient. Power consistency is `Q^T zdot = F^T vC + torqueWheel * thetaWheelDot`, with `z = [q, phi]`.

Spring forces are computed from potential energy. A torsion spring has `U = k(q-qRest)^2/2`; a linear spring uses its physical attachment distance `ell(q)` and `U = k(ell-ellRest)^2/2`. Generalized spring force is `-dU/dq`. Linear-spring load stiffness includes both `k(ell')^2` and `k(ell-ellRest)ell''`; preload and geometry therefore matter.

The nonlinear equation takes the form `M zddot + C(z,zdot) + grad(U) = Q_external + Q_actuator + Q_damping`. Inertial and potential terms remain model calculations; they are not measured hardware loads.

## Hybrid spring and MIT-style control

The fold channel commands shaft torque as `tauCmd = Kp(qDesired-q) + Kd(vDesired-qDot) + tauFeedforward`. `Kp` is N m/rad and `Kd` is N m s/rad at the modeled output shaft. Wheel-drive commands use their own coordinate and gains. The physical spring contributes separately; its stiffness is not included in the entered software gain.

An optional actuator response time creates a torque state with first-order response. Torque limits and configured torque–speed limits determine delivered torque. This is an idealized MIT-style command model; no hardware protocol, current loop, encoder filtering or CAN transport is simulated. The meaning of impedance gains and gravity compensation follows the [MIT manipulation control notes](https://manipulation.mit.edu/force.html).

## Local analysis

Pole and frequency calculations describe small perturbations about a selected pose and command. The force-balance residual must be considered: local modes about a biased nonequilibrium pose do not predict a settled operating point. Load bias, passive-spring geometry and controller stiffness all contribute to tangent stiffness. Actuator lag adds states. Saturation and limits make the local result conditional on the selected branch.

An unregulated wheel angle can produce a zero pole even when the suspension response is locally stable. A free undamped rotor can also have repeated zero poles and angle drift. The UI distinguishes fully decaying modes from the weaker condition of having no growing modes; nondecaying or zero modes do not automatically establish full-state stability. A simple `Kp / J^2` conversion to linear stiffness applies only with constant leverage and no load-dependent geometry term; it is not the general loaded stiffness.

## Scope

The fixed `A` bench resolves linkage motion, moving inertia, spring torque, ideal belt drive kinematics and local controller response. It does not model a freely moving chassis, unilateral tire contact, terrain impact, belt elasticity/backlash, frictional capstan limits, tooth engagement, detailed shaft bearing reactions, structural stress or thermal/electrical limits. The terrain workbench remains a separate reduced single-corner model. Matching a load case or passing this bench is not vehicle validation.
