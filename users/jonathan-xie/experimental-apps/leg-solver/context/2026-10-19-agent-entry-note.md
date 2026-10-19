# App instruction file missing from the shared checkout

Date: 2026-10-19. Requested by Andy during Motion Lab integration.

`users/jonathan-xie/experimental-apps/leg-solver/AGENTS.md` is absent from
the local checkout and fetched `origin/main` at `5d9dfa2`. The repository's
root entry protocol requires this file before dependent app work. Andy asked
to proceed for this integration using the root protocol and existing app/model
documentation, and to leave this reminder.

For Jonathan's next Codex session: please check whether the app's actual
`AGENTS.md` exists locally but is untracked or unpushed. Review and commit/push
that intended file through the normal contribution log and validation workflow.
If no app-specific file exists, agree on its contents with Jonathan before
adding one. This note is not a replacement instruction file or a blanket waiver
of the root protocol for future work.

Motion Lab serves the existing V4 source through its own integration layer;
the solver HTML, numerical conventions and earlier versions remain owned here.
