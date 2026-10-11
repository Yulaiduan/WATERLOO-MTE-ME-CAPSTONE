# Andy Zhang — shared project context

Updated: 2026-10-10. Status: curated member engineering context, not a private profile export.

Registered focus and contribution workflow: see the [team registry](../../../database/md_research/team.md).
Apps/toolkits: [experimental apps](../../../users/andy-zhang/experimental-apps/README.md).

## Current focus and working preferences

Current published focus: guided wheel-leg geometry, suspension load/impedance tradeoffs, experimental tooling and the control architecture connecting passive mechanics, MIT actuator behavior and an outer chassis controller.

## Controls context packet

Start with the [controls overview](2026-10-10-chatgpt-controls-overview.md): a short orientation, working diagram, current-versus-proposed status and the main floating problems.

| Note | Contents |
| --- | --- |
| [Explored topics](2026-10-10-chatgpt-controls-topics.md) | Plant boundaries, MIT fields, feedforward/integral action, passive/virtual impedance, gain scheduling, linkage mappings, simulation, whole-body control and hardware |
| [Open questions](2026-10-10-chatgpt-controls-open-questions.md) | Fifteen unresolved questions, their origin and proposed evidence to resolve them |
| [Modeling reference](2026-10-10-chatgpt-controls-model-reference.md) | Illustrative variables, local MIT/plant equations, spring/Jacobian mappings and moving-wheel/body models |
| [Conversation/source map](2026-10-10-chatgpt-controls-sources.md) | Twelve core project-thread excerpts, earlier retrieved context, repository sources and coverage limits |

These notes synthesize available Capstone controls discussions through October 10. They preserve open alternatives and distinguish current member-app behavior from a selected or validated whole-robot controller.

## Conversation handoffs

- [2026-10-10 ChatGPT controls context](2026-10-10-chatgpt-controls-overview.md): interconnected controls notes, explored topics, questions and sources.
- [2026-10-09 Wheel Leg Lab](2026-10-09-codex-wheel-leg-lab.md): curated rough-animation and wheel/link-ratio findings, source and validation.
- [2026-10-10 Workspace reorganization](2026-10-10-workspace-reorganization.md): nondeleting local archive, restored GitHub backup and maintained atlas/workbench plus Wheel Leg Lab.

## Open questions and next action

Confirm belt/pulley inputs, component limits, collision clearance and real contact requirements. For controls, define the initial objective, plant boundary, outer-to-MIT command interface and feedback/timing contract using the [question register](2026-10-10-chatgpt-controls-open-questions.md). App-specific setup and model context remain in the toolkit.
