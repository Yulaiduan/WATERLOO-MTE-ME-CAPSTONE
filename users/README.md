# Member experimental apps and toolkits

Author: Andy Zhang with Codex. Updated: 2026-10-08.
Status: experimental workspace scaffold; no apps imported by this change.

Use `users/<member>/experimental-apps/<app>/` for developing simulation sandboxes,
calculators, visualizations and other vibe-coded tools. A named owner makes it
easy to find the work; all teammates may use it. Coordinate changes with its owner.

| Member | Apps/toolkits |
| --- | --- |
| Ali Muizz | [experimental-apps](ali-muizz/experimental-apps/README.md) |
| Andy Zhang | [experimental-apps](andy-zhang/experimental-apps/README.md) |
| Jonathan Xie | [experimental-apps](jonathan-xie/experimental-apps/README.md) |
| Yulai Duan | [experimental-apps](yulai-duan/experimental-apps/README.md) |
| Jiaan Li | [experimental-apps](jiaan-li/experimental-apps/README.md) |

## Start an app

Copy the structure in [_template/experimental-app/](_template/experimental-app/README.md)
into your member folder and fill in its README, AGENTS.md and context/README.md.
The template is documentation, not a runnable app. Add the actual source,
dependency manifest/lockfile, small nonsecret configuration and meaningful
model/application checks when building it. Each app owns its dependencies.

```text
users/<member>/experimental-apps/<app>/
  README.md              Owner, experimental status, verified usage and limitations
  AGENTS.md              Focused app instructions, inheriting root protocol
  context/README.md      Model, assumptions, setup and current handoff
  src/                   App implementation, when added
  tests/                 Relevant checks, when added
  <dependency files>     Versions and lockfile for the chosen runtime
  <project launcher>     .cmd/.bat when a localhost app is created
```

General ChatGPT/Codex context belongs in [context/users/](../context/users/README.md).
Keep tool-specific equations, choices and setup with the tool; link shared facts
and requirements instead of duplicating them. Browser-local state is not shared
context: document a nonsecret import/export config when reproducibility needs it.

## Validation and promotion

The experimental label is a maturity label, not a gate exemption. Markdown-only
context/scaffolding uses the preliminary scope. Executable app code, configs,
dependency files and launchers retain the existing physics/mixed gate, plus the
app's own relevant checks. With no canonical robot, those contributions remain
blocked under current policy. A future app-only gate would require a separate
owner-reviewed change; this layout does not silently create one.

Root artifact, size, script-documentation and credential checks still apply.
Canonical robot models/meshes stay in `assets/`; production components must not
import member experiments. Keep caches and raw output out of Git, and add explicit
app ignore rules when importing/building an app.

Once useful to the team and validated, move a tool into its owning subsystem
(`simulation/`, `tools/` or another existing component), update imports/docs and
retire the duplicate in the same contribution. Preserve provenance and leave a
pointer from the member's app index. Keep existing research prototypes where they
are until a deliberate promotion; this change moves no code.

For localhost apps, create a durable launcher inside that app's root using an
installed runtime. Preserve its host, port and route, keep startup errors readable,
verify actual start/restart, and include its project folder, launcher and URL in
the delivery. No boot/login automation is implied.
