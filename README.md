# CAMEL

**Controlled Active-Suspension Mobility for Extreme Landscapes** is the ME 481/482 capstone project of Group 40 (Fall 2026 registration). The team is developing an all-terrain mobile platform intended to combine efficient wheeled travel with active adaptation to uneven ground. A specific use case and measurable performance targets are still to be selected with the external partner.

The team's [GitHub repository](https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE) is the shared home for documentation and engineering code. It is currently **public**; include only material approved for public sharing.

## Repository architecture

Use **one repository with separate components**. One commit can capture compatible code, interfaces, robot assets, and documentation, while each component keeps its own dependencies and run instructions. Documentation contributors do not need a firmware compiler or GPU environment.

**Implementation status:** this change establishes folders and contribution conventions, not working firmware, training pipelines or GPU launch scripts. Existing local MuJoCo work will be imported separately after review. The hardware toolchain, GPU provider, training backend and on-robot policy runtime remain open.

```text
WATERLOO-MTE-ME-CAPSTONE/
├── README.md                 Project overview and repository architecture
├── CONTRIBUTING.md           Branches, reviews and Markdown conventions
├── docs/                     Team Markdown: design, meetings, decisions, evidence
├── firmware/                 Embedded control, sensors, drivers, hardware tests
├── simulation/               Local MuJoCo environments, viewers and experiments
├── training/                 Learning algorithms, rewards, configs and evaluation
├── deploy/                   GPU images, job submission and artifact transfer
├── shared/                   Versioned contracts and portable shared utilities
├── assets/                   Canonical robot models, meshes and parameters
└── .github/                  PR template; future automated checks
```

| Area | Owns | Shared connections |
| --- | --- | --- |
| [docs](docs/README.md) | Markdown explanations, requirements, meetings, decisions and selected results | Links to every component and its evidence |
| [firmware](firmware/README.md) | Board code, drivers, real-time control, command limits and watchdogs | Implements shared command/telemetry contracts; builds without Python or cloud dependencies |
| [simulation](simulation/README.md) | MuJoCo runtime, local viewer, environment API and experiments | Uses canonical assets and contracts; exposes its environment to training |
| [training](training/README.md) | Algorithms, rewards, configs, evaluation and policy export | Uses the simulation API, assets and shared policy/observation/action contracts |
| [deploy](deploy/README.md) | GPU environment images, job scripts, storage and launch config | Launches the same training entry point at a pinned repository commit |
| [shared](shared/README.md) | Language-neutral schemas, units, conventions and portable utilities | Used by multiple components; never imports board, simulator or cloud-specific code |
| [assets](assets/README.md) | Reusable robot models, meshes and physical parameters | One canonical source for simulation and training, with explicit exports where hardware needs them |

### How the components connect

Arrows show dependency or artifact flow, not direct network connections:

```mermaid
flowchart LR
    S[Shared contracts] --> F[Firmware]
    S --> M[MuJoCo simulation]
    S --> T[Training and evaluation]
    A[Robot assets] --> M
    M --> T
    D[GPU deployment] -->|launches pinned commit| T
    T -->|versioned policy artifact| E[Local simulation evaluation]
    E -->|validated candidate| H[Hardware integration and safety review]
    H --> R[Selected on-robot runtime]
    R -->|command and telemetry interface| F
```

- **Local simulation:** debug and visualize on a laptop without cloud tooling. Training consumes the environment API rather than keeping another simulator copy.
- **GPU training:** deployment selects a commit, config, seed, assets and dependency/image versions, then launches training. GPU availability alone does not make ordinary MuJoCo physics GPU-accelerated; select and validate any accelerated backend separately.
- **Firmware integration:** inference may run on a companion computer or another selected runtime; microcontroller inference is not assumed. Firmware independently enforces command limits, watchdogs, and safe handling of missing or invalid commands.
- **Shared interfaces:** specify observation/action ordering and shapes, SI units, coordinate frames, joint names, timestamps, limits, control frequency, command/telemetry schemas and a compatibility version. Python and embedded code can implement the same contract without sharing a runtime.
- **Policy handoff:** export weights with the code commit, assets revision, interface version, normalization, action scaling, frequency, seed and training config. Validate compatibility and evaluate in simulation before a separately reviewed hardware test.

Each component owns its dependency manifest, lockfile where supported, tests and verified instructions. Package reusable Python code when implemented; avoid absolute developer-specific paths and copied source. A shared interface change must update affected consumers and tests in the same pull request, or include an explicit backwards-compatible migration.

### Multiple contributors: Markdown and code

Use short-lived branches from `main` and small pull requests. Organize by **topic or subsystem**, not a permanent folder or branch per person. Suggested branch names: `docs/<topic>`, `firmware/<topic>`, `sim/<topic>`, `train/<topic>` and `infra/<topic>`.

| Contribution | Destination |
| --- | --- |
| Living design explanation or calculation | `docs/design/<subsystem>/<topic>.md` or `<topic>/README.md` |
| Meeting notes | `docs/meetings/YYYY-MM-DD-topic.md` |
| Decision with status and rationale | `docs/decisions/NNNN-short-title.md` |
| Reproducible engineering result | `docs/benchmarks/YYYY-MM-DD-topic/README.md` plus small selected evidence |
| A topic's figures | Its adjacent `assets/` folder |
| Component build/run instructions | That component's `README.md` |

Create deeper folders as content arrives. Add authors, date, status, assumptions and sources to substantive notes. Update existing topics instead of creating competing copies, and link new pages from `docs/README.md`. Coordinate edits to the same section and preserve both contributors' meaning when resolving conflicts. See [contribution instructions](CONTRIBUTING.md).

### Artifacts and GitHub checks

Commit Markdown, source, small configs, schemas and manageable text robot models. Keep raw runs, checkpoints, datasets, videos and large generated meshes in team-approved artifact storage; commit compact summaries and reproducibility manifests. Use Git LFS for selected large source assets only after configuring it. Credentials and local environments stay out of Git.

Planned checks are scoped by changed paths: Markdown links for docs, embedded build/tests for firmware, headless smoke tests for simulation, CPU smoke tests for training, and image/config checks for deployment. Changes to `shared/` or `assets/` also exercise affected consumers. Full GPU jobs require explicit launch and runtime/cost limits, rather than running on every pull request.

**Not configured yet:** automated workflows, required reviews/checks, branch protection, CODEOWNERS, GPU runners and artifact storage. Add checks as working components arrive, then protect `main` using actual check names and a team-agreed review policy. Assign reviewers by affected subsystem; the registered roles below do not establish software ownership.

### Bring existing work into this layout

1. Import reviewed local docs under `docs/` and MuJoCo code under `simulation/`, preserving links and verified launch paths.
2. Extract genuinely reused robot assets into `assets/` and contracts into `shared/`; update consumers together and rerun simulation checks.
3. Add the chosen firmware toolchain and a minimal repeatable training/evaluation entry point with separate dependencies.
4. Add the GPU launch environment after the training entry point runs locally; record backend, versions, output storage and cleanup procedures.

Do not blindly copy local environments, generated results or private partner material during import. Component READMEs must distinguish planned work from verified commands.

## Proposed design

The registration concept is a four-wheel-drive, low-degree-of-freedom quadruped with four independently actuated, spring-assisted wheeled legs. Each leg's upper and lower sections are mechanically coupled so the leg operates with one degree of freedom. Motors mounted on the chassis reduce unsprung mass; two additional motors drive the left and right wheel pairs for steering. The intended capabilities are active chassis levelling, obstacle clearance, and terrain adaptability. This is a **preliminary concept**, not a frozen design.

## Team

| Member | Registered focus |
| --- | --- |
| Ali Muizz | Gearbox and transmission design |
| Andy Zhang | Motor and chassis design |
| Jonathan Xie | Electronics and kinematic analysis |
| Yulai Duan | Controls, thermal modelling, and simulations |
| Jiaan Li | Structure design and integration |

The team is working with an external partner providing funding and guidance. The registration form does not name the partner. A faculty advisor was not confirmed in the form.

## Verification approach

The team plans to agree on measurable size, mass, speed, payload, and terrain-performance requirements with the partner. Hand calculations, analysis, and simulation will inform the design; a scaled proof of concept will precede a full-scale functional prototype. Final tests should compare the prototype with the agreed requirements. Test methods and pass/fail thresholds have not yet been documented.

## Current documentation

Start with the [documentation map](docs/README.md). It separates the [preliminary physical system architecture](docs/architecture.md) from the repository architecture above and the [setup checklist](docs/setup.md). Local MuJoCo work exists separately; hardware and GPU training/deployment choices remain open.

## Items to confirm

- Specific use case, users, operating environment, and constraints.
- Faculty advisor, partner identity and sharing/confidentiality rules.
- Requirements, target values, test conditions, and acceptance criteria.
- Final subsystem interfaces, components, tools, budget, and schedule.
- Instructor feedback and approval. The approval boxes in the supplied registration form are blank.

**Source:** *ME 481 - Fall 2026 Design Project Registration Form*, pages 2-3, supplied as `Project Registration Form.docx.pdf`. Statements above describe the team's submitted proposal, not instructor approval or independently verified market claims.
