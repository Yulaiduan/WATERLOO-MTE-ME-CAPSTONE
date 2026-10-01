# Documentation map

This folder is the home for the CAMEL project's technical and onboarding documentation. The [project README](../README.md) is the short public-facing overview. Keep details here, and distinguish agreed decisions from proposed concepts and unanswered questions.

| Document | Purpose | Current status |
| --- | --- | --- |
| [Architecture](architecture.md) | System concept, subsystem boundaries, and interfaces to define | Preliminary, based on the registration form |
| [Setup](setup.md) | Reproducible workspace and validation environment | Python CPU validator available; canonical model pending |
| [Repository architecture](../README.md#repository-architecture) | Component boundaries, shared interfaces and GPU workflow | Entry protocol implemented; engineering components still scaffolds |
| [Agent entry protocol](../AGENTS.md) | Shared instructions for every agent | Tool-neutral entry point |
| [Knowledge database](../database/README.md) | Compact state, procedures and ownership | Includes rollout blockers and personal branches |
| [Contributing](../CONTRIBUTING.md) | Team Markdown, branches and reviews | Local hooks, required GitHub checks and code-owner review |
| [Terrain specifications for training](design/simulation/terrain-training-spec.md) | Notion terrain envelopes, payload targets, curriculum and evaluation | Source synthesis and proposed plan; no accepted requirements or training results |

## Team documentation layout

Create folders as content arrives: `design/<subsystem>/` for living explanations, `meetings/YYYY-MM-DD-topic.md` for notes, `decisions/NNNN-short-title.md` for decisions with status, and `benchmarks/YYYY-MM-DD-topic/` for reproducible evidence. Keep figures in the topic's `assets/` folder and add links here when adding pages. Organize by subject, not contributor.

Build/run instructions belong with [firmware](../firmware/README.md), [simulation](../simulation/README.md), [training](../training/README.md) and [deployment](../deploy/README.md). Contracts live in [shared](../shared/README.md), reusable robot models in [assets](../assets/README.md). These are currently guides, not executable implementations.

As work develops, add focused documents for requirements and acceptance tests, design decisions, verification results, and subsystem-specific instructions. Link them here. For each important decision, capture its owner, date, rationale, evidence, and any effect on requirements or interfaces. Store partner-provided or sensitive material only according to the team's agreed sharing rules.

The registration form is a dated proposal. Update this map and the README when the use case, advisor, partner permissions, design, or approval state changes; do not silently turn a proposal into a confirmed fact.
