# Agent knowledge database

Read all tracked contents of this directory every workspace loop, as required
by `AGENTS.md`. Keep summaries compact and link to long source material in
`docs/`; never duplicate existing design documents. Update this index with new
topics. Read archived log entries only as needed; the contribution log is at the
repository root so this database can stay small.

| Location | Contents |
| --- | --- |
| [Protocol](md_research/entry-protocol.md) | Enforcement, migration and open blockers |
| [Team](md_research/team.md) | Personal branches and review assignments |
| [Requirement parameter research](md_research/requirement-parameter-research.md) | Geometry, mass/COM, spring and energy findings with linked calculations |
| [LaTeX](brainstorming_tex/README.md) | Mechanical derivations and assumptions |
| [Prototypes](code_prototypes/README.md) | Small experimental snippets |
| [Contribution log](../ENTRY_TEMPLATE.md) | Exact changes and latest handoff |
| [Existing documentation](../docs/README.md) | Design and terrain sources |
| [Five-bump simulation results](../docs/benchmarks/2026-10-06-five-bumps/README.md) | Preliminary local 6B/8A/8B forward/reverse evidence at 5 m/s; contact/roll unresolved, executable implementation unpublished |

Promote a prototype to its owning component only with documented interfaces,
dependencies and validation. Link its replacement and retire duplicate code in
the same change. Raw datasets, notebooks with bulky output and copied third-party
repositories do not belong in the database.
