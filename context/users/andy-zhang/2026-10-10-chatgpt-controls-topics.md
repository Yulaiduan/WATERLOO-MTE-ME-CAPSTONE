# Controls topics explored

Author: Andy Zhang, synthesized with ChatGPT. Updated: 2026-10-10 (America/Toronto).
Status: discussion history and explanatory synthesis; proposals remain proposals.
Scope: Capstone robot controls. Reviewed base: `7c5cbc76efd36876e829803efc49578bea24f7fa` (`main`).

[Overview](2026-10-10-chatgpt-controls-overview.md) · [Open questions](2026-10-10-chatgpt-controls-open-questions.md) · [Model reference](2026-10-10-chatgpt-controls-model-reference.md) · [Sources](2026-10-10-chatgpt-controls-sources.md)

Statements under **Andy explored** summarize the available user questions. **Context to retain** is an organizing explanation or a specifically attributed earlier suggestion, not evidence that the team accepted a design.

## 1. The plant and the controller boundary

**Andy explored:** The familiar example is a motor with a voltage-to-angle plant and a PID wrapped around it. What becomes the plant when the motor already has MIT position and velocity gains? What does a block called “leg/chassis dynamics” physically contain? Can every block be expanded into actual equations and subblocks? [S10](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**Context to retain:** The boundary determines the answer. A voltage-to-angle motor model includes electrical and mechanical dynamics. A torque-command-to-joint-motion model assumes or includes the inner torque/current loop. An outer controller operating through fixed MIT gains sees the mechanical system together with that local feedback. These are different models of the same nested system, not competing names for one universal transfer function.

Andy requested both a full mathematical block diagram and a simplified gains/mass/spring/damper diagram. Omitting coordinate-conversion blocks in the latter is a request for a clearer view of the feedback structure, not a conclusion that implementation can omit those relationships.

**Still open:** Select the outer-loop input and measured output, define which inner loops are included, and state whether the first model assumes ideal torque tracking or includes actuator delay and saturation. The [reference equations](2026-10-10-chatgpt-controls-model-reference.md#3-how-mit-changes-the-plant-seen-by-an-outer-controller) illustrate the distinction.

## 2. MIT command fields and control modes

**Andy explored:** What do `p_des` and `v_des` do? Can both be commanded together? How can the same MIT interface act as position, velocity or torque control? Does `t_ff` interfere with position/velocity control, and is it an offset or an extra gain? [S05, S11](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**Context to retain:** The usual illustrative law is

$$
\tau_{cmd}=K_p(q_d-q)+K_d(v_d-\dot q)+\tau_{ff}.
$$

The position and velocity error terms contribute torque simultaneously. Feedforward is an additive commanded torque; a constant bias is one use, and a model-derived, time-varying compensation term is another. It is not itself an error gain. A position and velocity reference can coexist, but their relationship should be intentional—for example, a trajectory's desired velocity can be its position derivative.

| Explored behavior | Illustrative setting | Qualification |
| --- | --- | --- |
| Direct torque command | `Kp = Kd = 0`, command `tau_ff` | Actual torque follows only within the drive's bandwidth and limits. |
| Velocity feedback | `Kp = 0`, `Kd > 0`, command `v_des` | This is proportional velocity feedback in the illustrative law; it does not establish a device's separate velocity mode or integral behavior. |
| Position tracking with damping | `Kp > 0`, `Kd > 0`, command `p_des` and an appropriate `v_des` | Finite stiffness allows load-dependent position error unless compensation or another loop addresses it. |
| Combined impedance and feedforward | Both gains active, plus `tau_ff` | Requires a clear division between local impedance, static support compensation and outer feedback. |

These settings explain the interface discussed; they are not selected robot settings or verified firmware capabilities. Numeric units and scaling depend on the chosen drive and coordinate convention.

## 3. Integral action and the spring analogy

**Andy explored:** Why do motor controllers use `Ki`, and why is an integrator different from a spring-like actuator? [S05](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**Context to retain:** A virtual spring produces torque based on current displacement error. An integrator accumulates error over time, so the torque can continue changing while the displacement remains fixed. Earlier discussion distinguished a current-regulation PI loop from the local MIT impedance law and a possible outer height controller. That distinction is more useful than treating integral action as forbidden everywhere. [E02](2026-10-10-chatgpt-controls-sources.md#earlier-context-recovered-by-targeted-retrieval)

**Still open:** Whether steady support error is handled through physical spring preload, model-based torque compensation, an outer integral term or a combination. Saturation and accumulated integral error are implementation follow-ups if integral action is selected; no integral gains were established here.

## 4. Passive support, virtual stiffness and oscillation control

**Andy explored:** If a spring opens the knee, how does that spring interact with motor control? Does MIT supply local spring/damper behavior while an outer PID regulates height or force? Should oscillations be handled by MIT `Kd`, the outer controller, or changing MIT gains? Do physical and virtual spring/damper coefficients have the same units? [S02, S06, S10](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**Context to retain:** A physical spring supplies effort through its mounting geometry. MIT supplies active effort at a selected actuator coordinate. Their stiffness and damping can be combined only after expressing them at the same coordinate and operating point. Joint stiffness in N·m/rad is not directly added to a linear spring rate in N/m.

Static support, restoring stiffness and damping are separate quantities. The current app's ideal constant-lift spring balances weight but is elastically neutral: support alone does not choose a unique height. Its latest wheel configuration includes passive damping and has the knee controller disabled. This app state should not be described as an implemented outer-PID/MIT controller. [R02–R03](2026-10-10-chatgpt-controls-sources.md#repository-evidence-reviewed)

Earlier context also raised series compliance versus a spring acting alongside the actuator, including concerns about responsiveness and oscillation. That concern does not establish that every series-elastic arrangement is unsuitable. Actual topology remains model-specific. [E05](2026-10-10-chatgpt-controls-sources.md#earlier-context-recovered-by-targeted-retrieval)

## 5. Fixed gains, dynamic gains and gain scheduling

**Andy explored:** Can actuator `Kp`/`Kd` be changed dynamically to reduce bounce? Is that worse than leaving them fixed and using the outer controller? Could gain scheduling account for ride height or other operating conditions? [S06](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**Context to retain:** Fixed local gains plus an outer controller were proposed as a starting architecture in earlier assistant answers. Scheduling gains by configuration, payload, contact or terrain was also discussed. Those are candidate design approaches, not a final control policy. [E02](2026-10-10-chatgpt-controls-sources.md#earlier-context-recovered-by-targeted-retrieval)

The tentative takeaway that dynamic gain changes are “bad” must not become a blanket rule. A time-varying controller needs its own stability and energy analysis; fixed-gain stability at individual operating points does not by itself establish stability during switching. Ride-height commands and gains also have different roles: a height/reference command expresses the target, while gains describe response around it.

**Still open:** Which variables are scheduled, how smoothly they change, which loop handles fast disturbances, and what limits or evidence make transitions acceptable. No schedule, update rate or gain values were selected in the available record.

## 6. Linkage constraints, IK and Jacobians

**Andy explored:** How does the fixed 2:1 belt/pulley arrangement make the second link rotate? Why does the belt not simply move with the leg? Are linkage position, velocity, force calculations and the Jacobian the same thing? Why is IK needed? Why is a Jacobian sometimes a scalar when it is usually a matrix? [S01, S03, S06, S10](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**Context to retain:** Forward kinematics gives geometry from a coordinate. IK selects a coordinate from a desired geometry. The Jacobian is the local derivative mapping coordinate velocity to task velocity; its transpose maps task force to generalized effort through virtual work. A one-input/one-output mapping has a 1×1 Jacobian. A constrained two-link mechanism need not have two independent configuration coordinates.

An ideal equal-link example used in the discussions is extension `ell = 2 L cos(q)` with a fold angle measured from downward vertical. The current app also uses an angle measured from horizontal, and multiple studies have different coordinate conventions. Identical-looking symbols do not guarantee identical definitions. [R03](2026-10-10-chatgpt-controls-sources.md#repository-evidence-reviewed)

**Still open:** Confirm actual pulley routing, joint signs, independent DOFs, motor-versus-joint coordinates, allowable branch of IK and behavior near poor leverage. The current app prohibits hip-pulley reindexing in its fixed-guide proposal; its earlier reindexing demonstrations are historical alternatives. [R02](2026-10-10-chatgpt-controls-sources.md#repository-evidence-reviewed)

## 7. Natural frequency, poles and the first useful simulation

**Andy explored:** Start with a mass–spring–damper response and natural frequency, then what else is needed for stability and poles? How does an additional dynamic actuator enter? Is an analytical/numerically integrated ODE different from a 2D physics engine? Compare Planck and Pymunk for development speed, accuracy and belts/linkages/gears/springs/dampers. What open-source alternatives resemble Simulink? [S02–S03, S07](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**Context to retain:** The choice depends on the question being tested. A local linear model exposes pole and gain relationships; nonlinear equations retain chosen geometry and forces; a multibody/contact model addresses additional constraints and interactions. Visual motion, numerical agreement and hardware fidelity are different forms of evidence.

The repository now contains both an independent SciPy mathematical suspension model and a Pymunk physical bench, plus scoped MATLAB support and a saved-run comparison workspace. That is an existing member experiment, while the chats' broader Planck/Pymunk/Simulink comparison did not establish a final team toolchain. MATLAB coverage is limited to the original supported spring arrangement; it is not equivalent to every current spring preset. [R02–R04](2026-10-10-chatgpt-controls-sources.md#repository-evidence-reviewed)

**Still open:** Choose a common model/configuration for comparisons, define the outputs of interest and check timestep effects before interpreting force peaks. Select when to add linkage inertia, motor bandwidth, contact, pitch/roll and drivetrain coupling. The “second dynamic actuator” phrase in S02 is a question, not evidence of a finalized actuator count.

## 8. Disturbances, floating chassis and contact

**Andy explored:** How terrain parameters can drive the linkage simulation and produce useful motor requirements and controller-quality measures. Earlier context favored compact terrain descriptors such as slope, cross-slope, roughness, characteristic spacing and obstacle dimensions. [E01](2026-10-10-chatgpt-controls-sources.md#earlier-context-recovered-by-targeted-retrieval)

**Current repository correction:** The Oct 10 app record explicitly identifies **wheel position** as the excitation. The chassis is allowed to move, and its motion and required wheel-driver reaction are outputs. Fixed-hip or fixed-wheel fixtures answer different questions. The bench prescribes wheel-hub motion rather than automatically solving tire/soil contact. [R02–R03, R05](2026-10-10-chatgpt-controls-sources.md#repository-evidence-reviewed)

**Still open:** How a terrain profile becomes wheel-hub motion at a given speed, when the wheel can lose contact, and what extra tire/unsprung dynamics the intended test needs. A prescribed position fixture can supply a reaction that real ground cannot; its reaction history is therefore useful evidence, not automatic proof of terrain-following capability.

## 9. One leg versus the whole body

**Andy explored:** Is the control problem SISO, MISO or MIMO? What are its inputs, outputs, states and parameters? Earlier discussion considered heave, pitch and roll control followed by allocation to individual leg forces. [S06, S12; E02](2026-10-10-chatgpt-controls-sources.md)

**Context to retain:** Classification follows the selected model boundary. A torque-to-joint-angle channel may be SISO. The MIT law uses several command and measurement signals. A chassis model relating several leg efforts to heave/pitch/roll is multivariable. Counting sensor channels alone does not settle the plant's input/output classification.

The six-actuator project proposal also includes left/right wheel propulsion. Suspension and drive efforts may interact through contact and load distribution, even if the first study isolates one leg. [R01](2026-10-10-chatgpt-controls-sources.md#repository-evidence-reviewed)

**Still open:** Body state/measurement definitions, force allocation, actuator/contact constraints and the point at which the single-leg model must become a coupled body model.

## 10. Compute, CAN, sensing and higher-level control

**Andy explored:** Whether Jetson-class compute is sufficient, whether a separate lower-level MCU is needed, and alternatives including H7, STM32 F7 and Teensy. The thread ended by correcting the Jetson reference to **Orin Nano Super**. For motor drives he asked about moteus, ODrive, alternatives, Motionlayer and SimpleFOC, with an explicit MIT-plus-synchronous-CAN requirement. [S04, S08](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**Context to retain:** Earlier assistant proposals separated perception/planning from real-time robot control and motor-current regulation. Earlier context also explored terrain preview with proprioception, and higher-level MPC/state-feedback/RL ideas. These are future architecture options; no selected sensor set, compute workload, loop rate, controller library or learned policy is established by this packet. [E02–E03](2026-10-10-chatgpt-controls-sources.md#earlier-context-recovered-by-targeted-retrieval)

Synchronization needs a precise definition: packing parameters for one actuator, receiving feedback at known times, updating several actuators together and actually applying their commands at a common time are different requirements. This is a derived clarification of Andy's requirement, not a recovered final protocol.

Candidate products here record what was explored. Their present-day firmware, packet formats, gain scaling and synchronization support were not independently verified for this contribution, so this list makes no suitability ranking.

## Current work and three-sentence handoff

This is a discussion-only synthesis; no new engineering tests or hardware trials were performed. The explored topics connect model definition, passive mechanics, local actuator impedance, outer feedback and the eventual real-time implementation. Continue with the [open questions](2026-10-10-chatgpt-controls-open-questions.md), keeping current app behavior distinct from the proposed whole-robot controller.
