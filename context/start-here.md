# CAMEL context packet

Maintainer: CAMEL team. Updated: 2026-10-08.
Status: orientation snapshot; follow the linked records for current detail.
When uploading this file to ChatGPT, record the Git commit of the copy alongside it.

CAMEL means Controlled Active-Suspension Mobility for Extreme Landscapes, the
ME 481/482 Group 40 all-terrain platform proposal. The four spring-assisted
wheeled legs and active adaptation are a preliminary concept. Use case,
accepted performance requirements, hardware selection and approval still need
confirmation; chat suggestions do not settle them.

## Read the source that owns the question

| Question | Source |
| --- | --- |
| Project purpose, proposed architecture, registered roles | [Project README](../README.md) |
| Member workspaces, accounts and direct-push workflow | [Team registry](../database/md_research/team.md) |
| Entry/validation status and blockers | [Protocol record](../database/md_research/entry-protocol.md) and latest [contribution entry](../ENTRY_TEMPLATE.md) |
| Terrain envelopes and proposed training plan | [Terrain specification](../docs/design/simulation/terrain-training-spec.md) |
| Geometry, springs, COM and energy screening | [Research summary](../database/md_research/requirement-parameter-research.md) and linked evidence |
| Canonical robot and executable validation | [Assets](../assets/README.md) and [simulation](../simulation/README.md) |
| All engineering documents | [Documentation map](../docs/README.md) |

At this snapshot, no canonical robot/mass/joint baseline is registered. Analytical
studies are preliminary evidence; they do not certify driven-terrain or hardware
performance. Check the asset manifest and latest contribution before repeating
that status in a later conversation.

Member experiments live in `users/<member>/experimental-apps/`; general member
chat context lives in `context/users/<member>/`. Experimental app folders keep
their own models, setup and handoffs. Shared engineering components remain in
their existing subsystem folders.

Attach the actual linked source files needed for a ChatGPT task: relative links
inside an uploaded Markdown file do not provide the linked files by themselves.
End a useful conversation with the [handoff template](templates/chat-handoff.md).
