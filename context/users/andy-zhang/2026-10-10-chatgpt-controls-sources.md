# Controls context — conversation and source map

Author: Andy Zhang, curated with ChatGPT. Updated: 2026-10-10 (America/Toronto).
Status: provenance and coverage record for the controls packet.
Scope: Capstone robot discussions; reviewed repository base `7c5cbc76efd36876e829803efc49578bea24f7fa` on `main`.

[Overview](2026-10-10-chatgpt-controls-overview.md) · [Explored topics](2026-10-10-chatgpt-controls-topics.md) · [Open questions](2026-10-10-chatgpt-controls-open-questions.md) · [Model reference](2026-10-10-chatgpt-controls-model-reference.md)

## Coverage and evidence rules

The user requested a scan of Capstone controls chats and publication of useful context, explored topics and unresolved concerns in this member folder. This packet combines the relevant project-conversation excerpts available in the session, targeted retrieval of earlier conversations, and the existing repository records below.

The excerpt set usually contains Andy's own messages and thread titles/dates, while some conversations are truncated and most full assistant responses are absent. Targeted retrieval supplied additional summaries, but did not return complete transcripts or working original-chat URLs for every requested conversation. Original images were not available for full inspection in the controls excerpts. Consequently, this is a broad synthesis of **available controls context**, not a claim that every message in every Capstone chat was retrieved.

The packet uses the following distinctions:

- **Direct user question/preference:** supported by a visible project excerpt, recorded as exploration unless explicit acceptance is available.
- **Retrieved earlier context:** a summary returned by conversation retrieval, with its limitations retained; prior assistant proposals remain proposals.
- **Repository evidence:** the current content of a linked file at the reviewed base. Its historical test claims retain their original scope and were not rerun here.
- **Explanatory synthesis:** organization, proposed follow-up questions and illustrative derivations added for this handoff. These are not attributed to missing original answers.

Only project-relevant engineering summaries were imported. This packet contains no raw account export, full private transcript, unrelated coursework/career/FFB material or partner correspondence. No unavailable chat URL or source identifier has been invented.

## Project conversation excerpts

Dates and titles below follow the project history displayed to this session, in Andy's local project context. Questions are paraphrased for readability. These IDs are local references for this packet, not ChatGPT conversation IDs.

| ID | Date and displayed title | Controls material preserved | Coverage / qualification |
| --- | --- | --- | --- |
| S01 | 2026-09-30 — **Explain Linkage Animation** | How the 2:1 belt arrangement works, why the belt is not simply carried with the leg, how the second link rotates; request for animation | User questions available; original drawing detail and full answer unavailable |
| S02 | 2026-10-03 — **Linkage Simulation Overview** | Modeling levels; mass–spring–damper response and natural frequency; stability/poles; influence of an additional actuator; MIT virtual spring behavior and gain/unit scaling | “Second dynamic actuator” is a question, not a selected actuator count |
| S03 | 2026-10-04 — **Open Source Simulation Tools** | Open-source linkage kinematics/simulation/plotting tools; Simulink as a reference | “Two DOF linear link system” is historical wording; independent DOFs require a defined constraint model |
| S04 | 2026-10-05 — **Compute Hardware Sizing** | Jetson dimensions/adequacy; separate lower-level MCU; H7/F7/Teensy and other alternatives | Initial Orin NX reference was corrected to **Jetson Orin Nano Super**; no final hardware selection established |
| S05 | 2026-10-06 — **MIT Mode Explained** | MIT behavior, `Ki`, and why integral action differs from a virtual spring | User questions available; does not prohibit integral action in every loop |
| S06 | 2026-10-06 — **MIT control loop** | Fixed large pulley, driven upper link and opening spring; outer PID versus MIT; oscillation handling; gain scheduling; IK; SISO/MISO/MIMO; full Mermaid diagrams | Long mechanism thread is partly truncated; tentative understandings are not treated as accepted architecture |
| S07 | 2026-10-08 — **Pulley Spring Simulator Tools** | Planck versus Pymunk; development speed/accuracy; belts, gears, springs and dampers; physics engines versus ODE integration | No final team toolchain choice established by the excerpt |
| S08 | 2026-10-08 — **Motor Controller Alternatives** | moteus/ODrive alternatives; explicit MIT impedance and synchronous-CAN requirement; Motionlayer and SimpleFOC questions | The requirement is direct; product capabilities, synchronization meaning and selection remain unverified |
| S09 | 2026-10-09 — **Constant Force Spring Explained** | Why a linear spring can produce approximately constant mechanism output force; what makes the geometry work | User questions available; original mechanism image/full explanation unavailable in the excerpt |
| S10 | 2026-10-10 — **Control Problem Overview** | Plant boundaries; voltage-to-angle analogy; MIT gains inside the outer plant; governing equations; Jacobian/IK distinctions; detailed and simplified block diagrams | Strong evidence of requested modeling clarity; no final numeric plant/gains recovered |
| S11 | 2026-10-10 — **MIT Control Variables Explained** | `p_des`, `v_des`, torque feedforward; position/velocity/torque behavior; simultaneous references; feedforward as offset versus gain | User questions available; no chosen command mode or device interface established |
| S12 | 2026-10-10 — **Control Systems Terminology** | Classifying inputs, outputs, parameters and other model quantities for this robot | The state/reference/disturbance/measurement table in this packet is an organizing synthesis |

The Oct 7 **October November Timeline** excerpt also places simulation and formal actuator planning alongside the first leg deliverables. It supplies planning context, but this controls packet does not revise the project schedule or claim any milestone has been completed.

## Earlier context recovered by targeted retrieval

These summaries add breadth where full titled conversations were not returned. They are secondary conversation evidence. Unrelated emails, meetings and project alternatives returned by broad retrieval were not used to establish controls decisions.

| ID | Approximate discussion date / topic | Material retained | Limitation |
| --- | --- | --- | --- |
| E01 | 2026-09-29/30 through 2026-10-01 — robot simulation and terrain-parameter planning | User interest in 2D modeling, quantifying controller quality and converting terrain/linkage behavior into motor requirements; compact terrain descriptors and a proposed torque–speed/energy pipeline | Full thread titles/URLs not recovered for these summaries; pipeline details included prior assistant suggestions |
| E02 | 2026-10-01 and 2026-10-06 — suspension hierarchy and MIT modeling | Prior assistant proposals for heave/pitch/roll allocation, fixed local impedance plus outer regulation, position IK versus force mapping, and distinguishing current PI from MIT impedance | No final controller acceptance inferred; some reported equations depend on mechanism assumptions not confirmed by the excerpts |
| E03 | 2026-09-24 and 2026-10-05/06 — terrain preview, proprioception and compute hierarchy | Interest in preview plus body/joint sensing; assistant proposals separating perception/planning, real-time robot control and motor-current loops; higher-level control possibilities | No selected sensor set, compute workload, loop rates or demonstrated policy established |
| E04 | 2026-10-01/02 — engineering-tool interface discussion | Preference for compact, information-dense parameter/results views and useful simulation visualization | Presentation preference, not a controller or solver decision |
| E05 | 2026-09-29/30 and 2026-10-04 — compliant platform concept and active/passive arrangements | Platform-oriented framing, physical assistance alongside actuation, and concern about responsiveness/oscillation with series arrangements | Retrieved summary only; no general rejection of series-elastic systems or finalized topology inferred |

## Repository evidence reviewed

All links resolve within this repository. They are live navigation links; use the base revision above when reproducing this snapshot. This packet links existing engineering records instead of replacing their requirements, equations or test histories.

| ID | Source | Why it matters |
| --- | --- | --- |
| R01 | [Project README](../../../README.md) and [preliminary architecture](../../../docs/architecture.md) | Public project concept, four spring-assisted coupled legs, left/right drive and proposed status |
| R02 | [Wheel Leg Lab README](../../../users/andy-zhang/experimental-apps/wheel-leg-lab/README.md) and [current app context](../../../users/andy-zhang/experimental-apps/wheel-leg-lab/context/README.md) | Current Motion Lab state, prescribed wheel-position correction, floating chassis, fixed-guide constraint, replacement spring, disabled knee controller in that configuration and historical alternatives |
| R03 | [Independent suspension mathematics](../../../users/andy-zhang/experimental-apps/wheel-leg-lab/math/README.md) | Implemented model coordinates, nonlinear moving-base dynamics, spring laws, neutral constant lift, MATLAB scope and contact limitations |
| R04 | [Current app validation](../../../users/andy-zhang/experimental-apps/wheel-leg-lab/docs/validation.md) and [contribution log](../../../ENTRY_TEMPLATE.md) | Owning records for prior numerical, comparison, GUI and launcher evidence; this context contribution does not rerun or broaden those claims |
| R05 | [Oct 9 Wheel Leg Lab handoff](2026-10-09-codex-wheel-leg-lab.md) and [Oct 10 workspace handoff](2026-10-10-workspace-reorganization.md) | Existing imported-chat context and the floating-chassis/prescribed-wheel-height setup; retained intact |
| R06 | [Requirement-parameter research](../../../database/md_research/requirement-parameter-research.md) | Existing preliminary geometry, support, COM and energy screening; numerical examples remain scoped assumptions |
| R07 | [Context workflow](../../README.md), [start packet](../../start-here.md) and [handoff template](../../templates/chat-handoff.md) | Where selected conversation context belongs and how it relates to accepted engineering records |

### Historical products and tools

Names such as moteus, ODrive, Motionlayer, SimpleFOC, Planck, Pymunk and Jetson record what Andy explored. They are not a fresh product comparison. No current vendor specification, firmware feature, price or suitability ranking is asserted. Device-level decisions need authoritative documentation for the exact hardware/firmware version when that work is undertaken.

## What would improve a future refresh

Original exports of missing controls answers or mechanism drawings could add detail, but are not required to use this packet. Any later import should retain the source date, distinguish user acceptance from an assistant suggestion, reconcile current app state with historical alternatives and preserve earlier handoffs. Decisions should be recorded in their owning engineering record; this packet can then link them and mark the corresponding open question resolved.

## Validation and three-sentence handoff

The compilation was reviewed for project scope, proposal-versus-decision wording and source traceability; publication checks are recorded in the contribution log. Some full conversations and images remain unavailable, so the local source IDs identify evidence coverage rather than asserting a complete transcript archive. Continue from the overview and owning repository records, and expand this source map when additional original project material is explicitly imported.
