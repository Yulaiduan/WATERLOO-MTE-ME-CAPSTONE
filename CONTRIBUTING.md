# Contributing to CAMEL

Use the [repository architecture](README.md#repository-architecture) to choose a home for related work. The repository is public; include only material approved for public sharing.

## Team workflow

1. Start from up-to-date `main` in your own checkout and create a short-lived topic branch. Preserve uncommitted work when updating.
2. Coordinate ownership in an issue or team discussion. Use separate Markdown files for independent topics; agree who edits heavily shared sections.
3. Make a focused change, update relative links and instructions, and run relevant checks.
4. Push the branch and open a pull request describing the result and validation. Request a teammate familiar with the area; interface changes need review from affected consumers.
5. Incorporate feedback and merge after review and available checks. Resolve conflicts without dropping someone else's content. Avoid direct pushes to `main`.

This is a contribution convention: branch protection and required reviews are not configured by this change. Use folders in one shared history, not permanent subsystem branches with divergent robot models.

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
