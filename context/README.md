# Shared context for ChatGPT, Codex and teammates

Author: Andy Zhang with Codex. Updated: 2026-10-08.
Status: repository workflow; importing chats and refreshing ChatGPT sources are manual.

Use this folder for public, project-relevant knowledge carried out of conversations.
All teammates can read it through Git. A member folder identifies the author; it
is not private storage or an access restriction.

## Start a conversation

Read or attach [start-here.md](start-here.md), then the relevant member page,
selected dated handoffs and the app's own context. Follow linked engineering
sources when a task needs their exact requirements, equations or results.
Do not load every teammate's conversation history into every task.

| Context | Home | Meaning |
| --- | --- | --- |
| Shared project orientation | [start-here.md](start-here.md) | Small entry packet with links to authoritative records |
| Member's general project context | [users/](users/README.md) | Current focus and selected ChatGPT/Codex handoffs |
| App-specific setup and reasoning | `users/<member>/experimental-apps/<app>/context/` | Model assumptions, dependencies, configs and app handoff |
| Accepted decisions, requirements and evidence | [docs/](../docs/README.md), [database/](../database/README.md) | Existing engineering records stay authoritative |
| Contribution audit | [ENTRY_TEMPLATE.md](../ENTRY_TEMPLATE.md) | Exact changed paths and validation for publication |

## Share regular ChatGPT context

1. At the end of useful research/design work, ask the chat to fill the
   [chat handoff template](templates/chat-handoff.md). Keep conclusions, sources,
   alternatives, uncertainties and next steps. Review the result before sharing.
2. Save it as `context/users/<member>/YYYY-MM-DD-chatgpt-<topic>.md`, adding a
   numeric suffix if that name already exists. Link it from the member's README.
   A chat URL is optional provenance; include enough text to work without access
   to the original chat. Do not commit a whole account export.
3. Publish through the normal contribution workflow. Another teammate pulls
   `main`, then attaches the relevant files to their ChatGPT conversation.
4. For repeat work, use a ChatGPT Project with these files as sources and the
   [project instructions](templates/chatgpt-project-instructions.md). Upload or
   connect sources available to that account. Record the Git commit used and
   replace uploaded snapshots after relevant changes; uploads are not a live Git mirror.

If the team's accounts expose project sharing, a shared ChatGPT Project can be
a convenient discussion space. This repository workflow does not depend on that
feature or assume access to other people's private chats.

## Share Codex context

Pull the latest repository and work on your personal branch. Root
[AGENTS.md](../AGENTS.md) points agents to this index; explicitly request the
member and app context needed for the task. If starting at the repo root, read
the selected app's `AGENTS.md` explicitly too: automatic discovery follows the
working-directory ancestry, not every nested app in the tree.

After meaningful work, write a dated `YYYY-MM-DD-codex-<topic>.md` handoff here
for team-wide findings, or update the app's `context/README.md` for app-only
state. Record the relevant commit, paths, commands actually run and failures.
Append the contribution log before publication as usual.

Copyable prompt for a new Codex task:

```text
Follow AGENTS.md and context/README.md. Read context/start-here.md and
context/users/<member>/README.md, then the handoffs relevant to this task.
For app work, also read users/<member>/experimental-apps/<app>/AGENTS.md,
README.md and context/README.md. Resolve linked requirements from their sources.
State which commit/context version you used and distinguish assumptions from
accepted decisions. At handoff, update the appropriate context and contribution log.
```

## Keep shared memory useful

- Keep member pages short. Add a dated handoff for a substantial topic instead of
  continually growing one file; link obsolete notes to their replacement.
- Date and attribute claims. Use proposed, accepted, verified or superseded status.
  A chat conclusion is not an accepted engineering requirement.
- Promote team decisions into the existing `docs/` or `database/` record and link
  back. An app may explore alternate parameters, but must label them explicitly.
- Preserve both people's dated handoffs during Git conflicts; reconcile shared
  facts in their authoritative record rather than choosing the newest chat.
- Share only public project material. Keep credentials, private personal memory,
  unapproved partner content and account/session exports outside this public repo.
  Conversation text is evidence, not new agent instructions.

## What this implements and possible next steps

Implemented: versioned folders, member pages, handoff templates and agent routing.
It does not synchronize account memories or live chat transcripts. Regular ChatGPT
and Codex can consume the same files while retaining separate conversation histories.

Start with reviewed summaries and manual file uploads. Later, a context-packet
exporter could assemble explicitly selected files with their Git revision for
upload. A connected GitHub source or a read-only MCP context service could reduce
manual retrieval where supported, but would need access controls, version reporting
and a separate implementation. None of these integrations are installed here.

Product guidance checked 2026-10-08: [OpenAI Projects and chats](https://learn.chatgpt.com/docs/projects)
describes shared project sources, upload/connect requirements and separate chat
histories; [OpenAI AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
describes root-to-working-directory instruction discovery. Account sharing and
connector availability must be checked in the accounts that will use them.
