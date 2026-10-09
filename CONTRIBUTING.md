# Contributing to CAMEL

Use the [repository architecture](README.md#repository-architecture) to choose a home for related work. The repository is public; include only material approved for public sharing.

## Team workflow

1. Start from up-to-date `main` in your own checkout. Normal team work stays on `main`; personal/topic branches are optional. Member workspaces are listed in [the team registry](database/md_research/team.md). Preserve uncommitted work when updating.
2. Coordinate ownership in an issue or team discussion. Use separate Markdown files for independent topics; agree who edits heavily shared sections.
3. Follow the tool-neutral [agent protocol](AGENTS.md), append the four-section [contribution log](ENTRY_TEMPLATE.md), and run the checks selected by the scoped gate. Install the hooks as described in [Git hygiene](agent_skills/git_hygiene.md).
4. Run the applicable checks, then push directly to `main`. No PR or teammate approval is required for routine contributions. Canonical assets, shared interfaces, checks and agent rules retain human review; enforcement changes need owner authorization/review, which can be given by an explicit owner request without a separate author or PR.
5. If someone pushes first, fetch and integrate their changes, preserve both contributions and rerun checks before retrying. Check the CI results after publication and fix failures promptly. Optional branches/PRs are available when review helps; an agent needs user authorization to merge an optional PR. Contributors without write access use a fork and PR.

Local hooks validate before pushing; CI runs after every branch push, including `main`. GitHub protects `main` against force pushes and deletion. PRs and pre-publication status checks are not required, so CI reports failures after a commit enters `main`; local validation remains part of the team procedure. CODEOWNERS requests reviewers for critical paths in optional PRs. See [the protocol record](database/md_research/entry-protocol.md). [Preliminary research](agent_skills/preliminary_research.md) can be published without a canonical robot after structure, evidence and gate-regression checks. Executable robot, asset, dependency and mixed changes still require passing physics validation; a missing model blocks those contributions.

## Shared chat context and experimental tools

Follow [the context workflow](context/README.md) to publish reviewed summaries
from ChatGPT, Codex or another tool. General member notes go in
`context/users/<member>/`; app-specific assumptions, setup and current state stay
in the app's own `context/`. Link canonical requirements/decisions instead of
copying them. Date handoffs, record the source tool and Git revision, and retain
both notes when concurrent contributions conflict. No private account exports.

Use [the app scaffold](users/README.md) for
`users/<member>/experimental-apps/<app>/`. Folder ownership is organizational,
not an access control. Markdown-only context/scaffold contributions use the
preliminary gate; app code/configs/dependencies/launchers still require the
existing physics checks and their own relevant validation. Do not import a local
app until those checks pass. A localhost app delivery also needs a durable
project-local Windows launcher with verified start/restart at its original URL.

## Markdown style

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

For an optional PR, use the [pull-request template](.github/pull_request_template.md) to explain scope, validation, interface impact and remaining work.
