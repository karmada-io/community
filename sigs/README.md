# Special Interest Groups

Special Interest Groups (SIGs) are lightweight, topic-oriented groups formed to
coordinate design reviews, technical discussions, and community collaboration in
specific areas of Karmada. SIGs are open to all community members and operate in
public.

SIGs in Karmada are intentionally lightweight and are coordinated by one or more
leads. They do not require a separate charter document. Each SIG should keep its
scope, discussions, agenda, and notes accessible to the community.

The current list of SIGs is maintained as:

- [SIG-UI](sig-ui/README.md)
- [SIG-Scalability](sig-scalability/README.md)

## Scope

A SIG focuses on a specific technical area or user experience topic in the
Karmada ecosystem. Within its defined scope, a SIG may:

- Host design reviews and technical discussions.
- Collect feedback from users and contributors.
- Document ongoing work, open questions, and meeting notes in public.
- Make decisions that are binding within the SIG's scope.

If a SIG cannot reach consensus on a topic, the matter should be escalated to
the [Community Meeting](../README.md#community-meeting) for resolution.

For topics that span multiple SIGs, the leads of the relevant SIGs should collaborate
to resolve the issue. If they cannot reach agreement, the matter should be escalated
to the Community Meeting.

## Leads

Each SIG should have one or more leads. Having multiple leads is recommended to
share the workload and ensure continuity.

### Responsibilities

- Organize and facilitate SIG meetings.
- Maintain the meeting agenda and ensure meeting notes are recorded.
- Drive discussions and follow up on action items.
- Coordinate with other SIGs or escalate topics to the [Community Meeting](../README.md#community-meeting)
  when needed.

### Requirements

Leads must be [members](../community-membership.md) of the Karmada community.

### Selection and Changes

- Initial leads are proposed as part of the SIG creation process.
- New leads may be added through agreement among the existing leads.
- Leads may step down voluntarily at any time by informing the other leads (or
  Maintainers if no other leads exist).
- If a lead becomes inactive for more than six months, the remaining leads (or
  Maintainers if no other leads exist) may propose a replacement through the
  SIG's regular discussion channels.

## Participation

Participation in any SIG is fully open. Anyone may join SIG meetings, contribute
to discussions, add items to the meeting agenda, and participate in design
reviews. No approval or membership prerequisite is required.

## Meetings

SIGs typically hold biweekly meetings. Meetings may be canceled or rescheduled
when there are no agenda items or during major events such as KubeCon. Meeting
notes, agendas, and participant information are maintained in each SIG's public
meeting document.

## Creating a SIG

Creating a new SIG requires a two-thirds majority vote of all Maintainers, as
described in the [Governance Voting](../GOVERNANCE.md#voting) section.

A proposal to create a SIG should be submitted as an issue in the
[karmada-io/community](https://github.com/karmada-io/community) repository. The
proposal should include:

- The proposed SIG name.
- A clear description of the scope and purpose.
- The initial leads.
- The initial communication channels (e.g., Slack channel, mailing list).
- A public meeting notes document.

## Retiring a SIG

A SIG may be retired when its goals have been completed, its scope is no longer
relevant, or it has become inactive. Retiring a SIG requires a two-thirds
majority vote of all Maintainers, as described in the [Governance Voting](../GOVERNANCE.md#voting)
section.

A proposal to retire a SIG should be submitted as an issue in the
[karmada-io/community](https://github.com/karmada-io/community) repository. The
proposal should notify the SIG's leads and all maintainers, and be announced on
public community channels (e.g., Slack, mailing list).

Once approved, a pull request should update the target SIG document.
