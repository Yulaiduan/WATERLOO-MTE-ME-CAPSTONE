# Controls — floating problems and open questions

Author: Andy Zhang, synthesized with ChatGPT. Updated: 2026-10-10 (America/Toronto).
Status: open discussion register, not a committed implementation backlog.
Scope: Capstone suspension and robot controls. Reviewed base: `7c5cbc76efd36876e829803efc49578bea24f7fa` (`main`).

[Overview](2026-10-10-chatgpt-controls-overview.md) · [Explored topics](2026-10-10-chatgpt-controls-topics.md) · [Model reference](2026-10-10-chatgpt-controls-model-reference.md) · [Sources](2026-10-10-chatgpt-controls-sources.md)

These questions preserve what Andy was trying to understand and the ambiguities exposed by the discussions. **Direct** means an explicit question appears in the available project excerpts. **Synthesis** means the question is a follow-up inferred from those excerpts or current repository evidence. Suggested resolution evidence is proposed here; owners, deadlines, gains and acceptance thresholds have not been assigned.

## Q01 — What are we trying to optimize?

**Open; direct motivation with synthesized decision framing.** Active leveling and reducing oscillation recur, but “keep the body flat,” “hold height,” “reduce acceleration” and “maintain support/contact” do not specify the same output. Payload disturbance, suspension travel and actuator effort also affect whether a response is useful. [S02, S06, S10; E01–E03; R01](2026-10-10-chatgpt-controls-sources.md)

**What would resolve it:** A short objective statement for the first demonstration: commanded variables, measured performance outputs, disturbance conditions and limits. Candidate comparison measures are body displacement/attitude error, peak/RMS acceleration, settling behavior, contact reaction, travel and actuator effort. Values and priorities still need agreement.

## Q02 — What exactly is the plant at each loop boundary?

**Open; direct.** Andy's reference is a voltage-to-angle motor plant. He asked how motor `Kp`/`Kd` and the spring–mass–damper mechanism change what an outer controller sees, and what belongs inside “leg/chassis dynamics.” [S10](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**What would resolve it:** One diagram and input/output definition for each relevant boundary: physical motor, torque-controlled joint/leg, and MIT-controlled leg as seen by the body controller. State whether motor-current dynamics, sensor filtering, transmission, contact and delay are included. The [model reference](2026-10-10-chatgpt-controls-model-reference.md) is a starting illustration, not the chosen robot model.

## Q03 — What should the outer controller send to MIT?

**Open; direct.** Position/height targets, velocity targets, force/torque compensation and changing local gains have all been raised. Andy also asked whether simultaneous `p_des`/`v_des` commands conflict and whether `t_ff` disturbs position or velocity regulation. [S06, S11](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**What would resolve it:** A command contract showing how each outer output becomes the five MIT fields, in one declared coordinate system. Separate nominal support compensation from dynamic feedback and specify consistent reference trajectories. Compare a small number of explicit alternatives under the same disturbance before selecting one.

## Q04 — Who handles the oscillations?

**Open; direct.** Should local MIT damping, the outer controller or gain changes suppress bounce? If both layers respond to the same motion, how do their combined gains and timing affect the result? [S02, S06, S10](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**What would resolve it:** The combined local/outer model, intended bandwidths and sensor/command timing, followed by response and stability checks over representative poses and loads. Positive local gains alone do not settle the coupled system's behavior. The earlier fixed-gain proposal is a candidate baseline, not a rule that variable gains are always unsuitable.

## Q05 — What changes with ride height, payload or terrain mode?

**Open; direct.** Andy explicitly raised gain scheduling for ride height and operating conditions after discussing dynamic gain changes. Geometry-dependent leverage also means the same joint gains need not produce the same vertical compliance everywhere. [S06, S10; E02](2026-10-10-chatgpt-controls-sources.md)

**What would resolve it:** A distinction between target changes and gain changes, candidate scheduling variables, transition behavior and checks over the intended operating range. No particular schedule or fast/slow rate is established in the recovered record.

## Q06 — How do passive support, restoring stiffness and active effort combine?

**Open; direct, with current app evidence.** Andy asked how the physical spring and MIT spring/damper behavior combine and whether their units match. He also asked how a linear spring mechanism can produce approximately constant external force. The current app studies a replacement constant-lift spring whose ideal elastic balance is neutral, with passive damping and the knee controller disabled. [S02, S06, S09; R02–R03](2026-10-10-chatgpt-controls-sources.md)

**What would resolve it:** Curves for support effort, local stiffness and damping versus configuration, using the actual spring law, preload and attachment geometry. Then establish how a ride height is selected and how remaining static/dynamic effort is supplied. A physically loaded spring must not be replaced by a constant gain without documenting the approximation.

## Q07 — Where should integral action and feedforward compensation live?

**Open; direct.** Why does a motor controller use `Ki` while MIT is described as spring/damper behavior? Is a torque offset appropriate while trying to control position or velocity? [S05, S11](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**What would resolve it:** Identify each control loop and its purpose, then assign steady support/error compensation deliberately. A current PI loop, local impedance and outer height integrator are different mechanisms. If an integrator is used, its limits and recovery from actuator saturation become part of that design.

## Q08 — What are the actual coordinates, constraints and units?

**Open; direct.** Andy asked about the 2:1 belt relationship, second-link rotation, IK and Jacobians, while some chat wording calls the mechanism “two DOF.” Current studies use more than one angle convention. [S01, S03, S06, S10; R02–R03](2026-10-10-chatgpt-controls-sources.md)

**What would resolve it:** One drawing tied to CAD with independent coordinates, constrained joints, spring extension, actuator shaft/encoder location, gear ratio, force/torque signs and units. Derive the actual velocity and virtual-work mappings. Identify dead-center limits and the valid IK branch. Do not infer independent DOF count from the number of links or actuator count from a discussion phrase.

## Q09 — What does the terrain disturbance mean in the first model?

**Open extension of a documented correction.** The current app already resolves one issue: its excitation is prescribed wheel-hub position and the chassis responds. What remains is how that test relates to real terrain and tire contact. [E01; R02–R03, R05](2026-10-10-chatgpt-controls-sources.md)

**What would resolve it:** State whether the input is ground elevation, wheel-center height, contact force or actuator torque; define the conversion from a spatial profile and speed to a time history. Specify which motion is imposed and which is solved. Add contact loss, tire compliance or unsprung dynamics only when required for the chosen question, and report the scope of each result.

## Q10 — What is the minimum model that answers the current question?

**Open; direct.** Andy wants mass–spring–damper response, natural frequency and poles, while also exploring nonlinear equations and 2D rigid-body simulation. The main tool comparison is Planck/Pymunk versus explicit numerical modeling, with Simulink as a familiar reference. [S02–S03, S07](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**What would resolve it:** Choose a first model, state omitted effects and define what result would justify adding detail. Existing SciPy/Pymunk comparisons can inform this, but compare identical geometry, forcing, spring laws, initial conditions and sampling. A mismatch may involve modeling assumptions or numerical integration; it is not automatically proof that one engine is physically correct.

## Q11 — How does a one-leg controller become a whole-body controller?

**Open; direct with earlier proposed architecture.** Andy asked SISO/MISO/MIMO. Earlier assistant suggestions described heave/pitch/roll regulation followed by allocation to leg forces; the project proposal also includes coupled left/right propulsion. [S06, S12; E02; R01](2026-10-10-chatgpt-controls-sources.md)

**What would resolve it:** Define body coordinates and leg locations, then the mapping between leg efforts and body force/moments. State contact assumptions and available actuator authority. Decide when load distribution, roll/pitch and wheel-drive interaction must be included rather than inferred from four isolated single-leg studies.

## Q12 — What can we actually measure or estimate?

**Open; synthesis grounded in model-variable and earlier sensor discussions.** Desired body height, leg extension, world vertical velocity, joint speed and wheel contact are different quantities. The input/output terminology discussion and earlier IMU/joint/terrain-preview proposals leave a concrete sensing contract to define. [S12; E02–E03](2026-10-10-chatgpt-controls-sources.md)

**What would resolve it:** A table mapping every feedback quantity to a sensor or estimator, coordinate frame, update timing, expected filtering and missing-state assumptions. Distinguish relative leg height from world body height, and a direct measurement from an inferred quantity. Sensor selection is not established by listing a desired state vector.

## Q13 — Which actuator/compute stack provides the required behavior?

**Open; direct.** MIT impedance with synchronous CAN packets is explicitly required. moteus, ODrive, Motionlayer, SimpleFOC and other candidates were explored. Jetson/MCU roles and packaging were questioned; Orin Nano Super was the latest Jetson reference. [S04, S08](2026-10-10-chatgpt-controls-sources.md#project-conversation-excerpts)

**What would resolve it:** Define “synchronous” in terms of actual command application, feedback timing and allowed skew. Verify the exact hardware/firmware versions against that contract, including command units, gains, telemetry, limits and missed-command behavior. Workload and timing estimates should drive compute selection. No current vendor capability is certified by these historical notes.

## Q14 — How much preview or advanced control is useful for the first robot?

**Open; retrieved earlier exploration.** Terrain preview with proprioception, body-level state feedback/MPC and RL/perception ideas appeared in earlier context. They are relevant longer-term possibilities, but the accessible record does not choose an algorithm or establish a trained policy. [E02–E03](2026-10-10-chatgpt-controls-sources.md#earlier-context-recovered-by-targeted-retrieval)

**What would resolve it:** Identify a specific failure or limitation of the initial feedback baseline that preview or a more complex controller is intended to address. Define the required terrain information, timing and comparison test. This keeps algorithm selection tied to a demonstrated control need.

## Q15 — How will simulation turn into actuator requirements and credible evidence?

**Open; direct motivation with synthesized validation details.** Earlier controls planning asked how terrain and linkage simulations can produce motor requirements and quantify control quality. Static support calculations and the current passive app are relevant inputs but do not establish active terrain performance. [S02, S07; E01; R02–R04, R06](2026-10-10-chatgpt-controls-sources.md)

**What would resolve it:** Retain torque–speed histories, travel, reaction/contact limits, current/thermal/energy assumptions and the exact controller/model revision for a representative disturbance set. Compare agreed passive and active configurations with the same initial conditions and constraints. Map each claimed improvement to a metric and an explicitly scoped simulation or hardware result.

## Suggested order for the next focused discussion

This is a proposed sequence, not a replacement for the project timeline:

1. Set the first performance objective and model input/output boundary: Q01–Q03, Q09.
2. Fix the coordinate, spring and actuator assumptions: Q06–Q08.
3. Study the combined response and what changes with pose/load: Q04–Q05, Q10.
4. Connect the result to body allocation, measurements and real hardware timing: Q11–Q13.
5. Use measured limitations and requirements to justify preview/advanced control and validation scope: Q14–Q15.

## Current work and three-sentence handoff

No engineering tests were run to close these questions in this documentation contribution. The register records the distinctions needed to turn Andy's controls exploration into an explicit model and interface. Continue by resolving a small, coherent set of model assumptions and record any selected answer in the owning engineering document with supporting evidence.
