# Team branches and reviewers

Updated: 2026-10-06. Names and engineering focus come from the registration form
already summarized in the project README. The branches below assign an isolated
workspace to every member; they share reviewed `main` as the integration branch.

| Member | Personal branch | Registered focus | GitHub identity |
| --- | --- | --- | --- |
| Ali Muizz | `members/ali-muizz/work` | Gearbox/transmission | Pending confirmation |
| Andy Zhang | `members/andy-zhang/work` | Motor/chassis | Pending confirmation |
| Jonathan Xie | `members/jonathan-xie/work` | Electronics/kinematics | Pending confirmation |
| Yulai Duan | `members/yulai-duan/work` | Controls/thermal/simulation | `Yulaiduan` (repository owner) |
| Jiaan Li | `members/jiaan-li/work` | Structure/integration | Pending confirmation |

Use `members/<member>/<topic>` for concurrent tasks. One agent writes a checkout at
a time; use a separate Git worktree for each simultaneous agent. Never reuse a
teammate's branch. Branch names are organization, not access controls; GitHub
write access alone does not restrict a user to their assigned branch.

Do not create the bare `members/<member>` ref: Git cannot store that branch and
its topic children at the same time. The five `/work` branches are published with
the protocol. External forks use `contributors/<github-login>/<topic>` and the
same checks when proposing changes to this repository.

Verified collaborators are `Yulaiduan`, `Code-Andy` and `Jiaan124`. Routine paths
do not automatically request peer review and may merge after CI passes without
teammate approval. CODEOWNERS keeps the shared pool for canonical assets and
shared interfaces, and routes checks/enforcement/agent rules to `Yulaiduan`.
Specialist ownership remains unsettled. Add the other accounts with write access
before assigning them as code owners; change this file and CODEOWNERS together.

Enforcement files, shared agent instructions and physics gate implementation
require `Yulaiduan` review. Critical-path human review is a team procedure;
the live GitHub ruleset requires zero approvals and does not enforce it by path.
The owner cannot self-approve: another contributor must author an enforcement
change when owner approval is required.
