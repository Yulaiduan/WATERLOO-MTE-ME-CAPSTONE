# Contributing to CAMEL

Use the [repository architecture](README.md#repository-architecture) to choose a home for related work. The repository is public; include only material approved for public sharing.

## Team workflow

1. Start from up-to-date `main` in your own checkout. Use your personal `members/<name>/work` branch or a topic branch with a different final segment, as listed in [the team registry](database/md_research/team.md). Preserve uncommitted work when updating.
2. Coordinate ownership in an issue or team discussion. Use separate Markdown files for independent topics; agree who edits heavily shared sections.
3. Follow the tool-neutral [agent protocol](AGENTS.md), append the four-section [contribution log](ENTRY_TEMPLATE.md), and run the checks selected by the scoped gate. Install the hooks as described in [Git hygiene](agent_skills/git_hygiene.md).
4. Push the branch and open a pull request describing the result and validation. Request a teammate familiar with the area; interface changes need review from affected consumers.
5. Incorporate feedback and merge after review and available checks. Resolve conflicts without dropping someone else's content. Avoid direct pushes to `main`.

Local hooks and CI implement the contribution gate. GitHub checks and code-owner review apply to PRs from both member branches and forks; see [the protocol record](database/md_research/entry-protocol.md). Each member has an isolated branch; regularly integrate reviewed `main` so canonical assets and interfaces do not diverge. [Preliminary research](agent_skills/preliminary_research.md) can be published without a canonical robot after structure, evidence and gate-regression checks. Executable robot, asset, dependency and mixed changes still require passing physics validation; a missing model blocks those contributions.

## Markdown

- Use lowercase filenames with hyphens; date meeting notes and benchmarks.
- Include authors, updated date, status, assumptions and sources in substantive notes. Distinguish draft/proposed/accepted decisions and verified measurements.
- Put explanations in `docs/design/`, decisions in `docs/decisions/`, meetings in `docs/meetings/`, and reproducible evidence in `docs/benchmarks/`. Create folders when adding content.
- Keep figures adjacent to their topic in `assets/`, use relative links, and update `docs/README.md`.
- Update existing topics rather than making parallel copies. Retain disagreements and open questions explicitly.

## Code and reproducibility

- Keep dependencies and verified build/run instructions with each component. Do not publish placeholder commands as operational.
- Put cross-component contracts in `shared/` and reusable robot models/parameters in `assets/`. Document units, frames, ordering, limits, timing and compatibility; update consumers and tests together.
- Retained runs need the commit, resolved config, seed, dependencies/backend, assets revision and interface version. Keep large raw artifacts outside Git and link selected results from dated benchmarks.
- Documentation needs a link/path check. Code needs affected-component tests; shared changes need consumer checks. Report unavailable GPU/hardware checks honestly.

Use the [pull-request template](.github/pull_request_template.md) to explain scope, validation, interface impact and remaining work.
