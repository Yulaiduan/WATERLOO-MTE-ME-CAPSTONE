# Team workspaces and contribution workflow

Updated: 2026-10-08. Names and engineering focus come from the registration form
already summarized in the project README. Normal team work uses `main` with
validated direct pushes and no PR requirement. Member folders organize personal
experiments; the published personal branches below remain optional.

| Member | Optional personal branch | Registered focus | GitHub identity |
| --- | --- | --- | --- |
| Ali Muizz | `members/ali-muizz/work` | Gearbox/transmission | Pending confirmation |
| Andy Zhang | `members/andy-zhang/work` | Motor/chassis | Pending confirmation |
| Jonathan Xie | `members/jonathan-xie/work` | Electronics/kinematics | Pending confirmation |
| Yulai Duan | `members/yulai-duan/work` | Controls/thermal/simulation | `Yulaiduan` (repository owner) |
| Jiaan Li | `members/jiaan-li/work` | Structure/integration | Pending confirmation |

Use `users/<member>/experimental-apps/` for personal tools and
`context/users/<member>/` for general shared handoffs. All teammates can read them;
folder names do not restrict access. Keep accepted engineering records and team
code in their existing components.

Use `members/<member>/<topic>` when a separate branch helps concurrent tasks. One agent writes a checkout at
a time; use a separate Git worktree for each simultaneous agent. Never reuse a
teammate's branch. Branch names are organization, not access controls; GitHub
write access alone does not restrict a user to their assigned branch.

Do not create the bare `members/<member>` ref: Git cannot store that branch and
its topic children at the same time. The five `/work` branches were published with
the protocol and are optional. External forks use `contributors/<github-login>/<topic>` and the
same checks when proposing changes to this repository.

Verified collaborators are `Yulaiduan`, `Code-Andy` and `Jiaan124`. Routine paths
do not automatically request peer review and may be pushed to `main` after local
checks pass without teammate approval. Member experiments/context stay together
on main without CI; shared engineering/enforcement changes run CI after publication.
CODEOWNERS keeps the shared pool for canonical assets and
shared interfaces, and routes checks/enforcement/agent rules to `Yulaiduan`.
Specialist ownership remains unsettled. Add the other accounts with write access
before assigning them as code owners; change this file and CODEOWNERS together.

Enforcement files, shared agent instructions and physics gate implementation
require `Yulaiduan` authorization/review. An explicit owner request can authorize
the policy change without a separate author or PR. Critical-path human review is
a team procedure; the live GitHub ruleset blocks force pushes and deletion of
`main`, without requiring PRs or passing statuses before publication. CODEOWNERS
requests review when an optional PR is used.
