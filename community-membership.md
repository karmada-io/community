# Community membership

**Note:** This document is a work in progress

This doc outlines the various responsibilities of contributor roles in Karmada.

| Role       | Responsibilities                                              | Requirements                                                       | Defined by                   |
|------------|---------------------------------------------------------------|--------------------------------------------------------------------|------------------------------|
| Member     | Active contributor in the community                           | Sponsored by 2 reviewers and multiple contributions to the project | Karmada GitHub org member    |
| Reviewer   | Review contributions from other members                       | History of review and authorship in a subproject                   | [OWNERS] file reviewer entry |
| Approver   | Contributions acceptance approval                             | Highly experienced active reviewer and contributor to a subproject | [OWNERS] file approver entry |
| Maintainer | Demonstrated responsibility and excellent technical judgement | Demonstrated responsibility and excellent technical judgement      | [Maintainers] file entry     |

## New contributors

[New contributors] should be welcomed to the community by existing members,
helped with PR workflow, and directed to relevant documentation and
communication channels.

## Member

Members are continuously active contributors in the community. They can have
issues and PRs assigned to them, participate in SIGs through GitHub teams. 
Members are expected to remain active contributors to the community.

**Defined by:** Member of the Karmada GitHub organization

### Requirements

- Enabled [two-factor authentication] on their GitHub account
- Have made multiple contributions to the project or community.  Contribution may include, but is not limited to:
    - Authoring or reviewing PRs on GitHub. At least one PR must be **merged**.
    - Filing or commenting on issues on GitHub
    - Contributing to SIG, subproject, or community discussions (e.g. meetings, Slack, email discussion
      forums, Stack Overflow)
- Subscribed to [Karmada mailling list]
- Have read the [contributor guide]
- Actively contributing to 1 or more subprojects.
- Sponsored by 2 reviewers. **Note the following requirements for sponsors**:
    - Sponsors must have close interactions with the prospective member - e.g. code/design/proposal review, coordinating
      on issues, etc.
    - Sponsors must be reviewers or approvers in at least one OWNERS file within one of the Karmada GitHub organizations.
    - Sponsors must be from multiple member companies to demonstrate integration across community.
- **[Open an issue][membership request] against the karmada-io/community repo**
   - Ensure your sponsors are @mentioned on the issue
   - Complete every item on the issue checklist
   - Make sure that the list of contributions included is representative of your work on the project.
- Have your sponsoring reviewers reply confirmation of sponsorship: `+1`
- Once your sponsors have responded, your request will be handled by the `Karmada GitHub Admin team`.

### Responsibilities and privileges

- Responsive to issues and PRs assigned to them
- Responsive to mentions of SIG teams they are members of
- Active owner of code they have contributed (unless ownership is explicitly transferred)
  - Code is well tested
  - Tests consistently pass
  - Addresses bugs or issues discovered after code is accepted
- Members can do `/lgtm` on open PRs.
- They can be assigned to issues and PRs, and people can ask members for reviews with a `/cc @username`.
- Members can do `/close` to close PRs as well.
- Members are eligible to attend the CNCF Maintainer Summit (exclusive event during KubeCon).

**Note:** members who frequently contribute code are expected to proactively
perform code reviews and work towards becoming a primary *reviewer* for the
subproject that they are active in.

## Reviewer

Reviewers are able to review code for quality and correctness on some part of a
subproject. They are knowledgeable about both the codebase and software
engineering principles.

**Defined by:** *reviewers* entry in an OWNERS file in a repo owned by the
Karmada project.

### Requirements

The following apply to the part of codebase for which one would be a reviewer in
an [OWNERS] file (for repos using the bot).

- member for at least 1 months
- Primary reviewer for at least 5 PRs to the codebase
- Reviewed or merged at least 20 substantial PRs to the codebase
- Knowledgeable about the codebase
- Sponsored by a subproject approver
  - With no objections from other approvers
  - Done through PR to update the OWNERS file
- May either self-nominate, be nominated by an approver in this subproject.

### Responsibilities and privileges

The following apply to the part of codebase for which one would be a reviewer in
an [OWNERS] file (for repos using the bot).

- Code reviewer status may be a precondition to accepting large code contributions
- Responsible for project quality control
  - Focus on code quality and correctness, including testing and factoring
  - May also review for more holistic issues, but not a requirement
- Expected to be responsive to review requests
- Assigned PRs to review related to subproject of expertise
- Assigned test bugs related to subproject of expertise
- May get a badge on PR and issue comments

## Approver

Code approvers are able to both review and approve code contributions.  While
code review is focused on code quality and correctness, approval is focused on
holistic acceptance of a contribution including: backwards / forwards
compatibility, adhering to API and flag conventions, subtle performance and
correctness issues, interactions with other parts of the system, etc.

**Defined by:** *approvers* entry in an OWNERS file in a repo owned by the
Karmada project.

### Requirements

The following apply to the part of codebase for which one would be an approver
in an [OWNERS] file (for repos using the bot).

- Reviewer of the codebase for at least 1 months
- Primary reviewer for at least 10 substantial PRs to the codebase
- Reviewed or merged at least 30 PRs to the codebase
- Nominated by a subproject owner
  - With no objections from other subproject owners
  - Done through PR to update the OWNERS file

### Responsibilities and privileges

The following apply to the part of codebase for which one would be an approver
in an [OWNERS] file (for repos using the bot).

- Approver status may be a precondition to accepting large code contributions
- Demonstrate sound technical judgement
- Responsible for project quality control
  - Focus on holistic acceptance of contribution such as dependencies with other features, backwards / forwards
    compatibility, API and flag definitions, etc
- Expected to be responsive to review requests
- Mentor contributors and reviewers
- May approve code contributions for acceptance

## Maintainer

Maintainers are responsible for the overall health and direction of the project.
They must set technical direction and make or approve design decisions either
directly or through delegation of these responsibilities.

### Requirements

- Deep understanding of the technical goals and direction of the project.
- Deep understanding of the technical domain (specifically the language) of the project.
- Sustained contributions to design and direction by doing all of:
  - Authoring and reviewing proposals
  - Initiating, contributing and resolving discussions (e.g. emails, GitHub issues, meetings)
  - Identifying subtle or complex issues in designs and implementation PRs
- Nominated by a maintainer and pass super-majority(two-thirds/ 66.66%) vote.

### Responsibilities and privileges

- Maintaining the project: responsible for ensuring that the project remains stable, 
  secure, and up-to-date, including fixing bugs, addressing security vulnerabilities 
  and releasing new versions of the project as needed.
- Managing contributions: responsible for managing contributions to the project, 
  including code/non-code contributions, bug reports and feature requests.
- Communicating with the community: responsible for communicating with the project's
  community, including users, developers, and other contributors. This may involve
  responding to questions, addressing concerns, and providing updates on the project's
  status.
- Setting project goals and priorities: responsible for setting the project's goal
  and priorities, and for ensuring that the project remains aligned with these goals
  over time.
- Ensuring project sustainability: responsible for ensuring that the project remains
  sustainable over the long-term, including managing dependencies, ensuring compatibility
  with other projects, and planning for the future of the project.


### The structure of the Maintainers

- No single vendor can exceed 50% of the total number of maintainers.

### Changes in Maintainership

#### Maintainer recruiting

The maintainers have the authority to nominate new maintainers who meet the maintainer requirements listed above.
When nominating new maintainers, a public issue should be opened against the `karmada-io/community` repo with 
detailed contribution metrics for the candidate. Then, the current active maintainers vote on this issue. 
Once a candidate passes a super-majority vote (see requirement listed above), they will officially become a 
maintainer.

In such a case:
- A PR is required to add the new maintainer to the [list of Karmada Maintainers](https://github.com/karmada-io/community/blob/main/MAINTAINERS.md).
- A PR is required to add the new maintainer to the [list of CNCF Maintainers](https://maintainers.cncf.io/).
- The new maintainer will be invited to join the [Karmada Maintainer mailing list](cncf-karmada-maintainers@lists.cncf.io) by current maintainers.

#### Maintainer Retirement
- If a Maintainer feels they cannot fulfill the "Responsibilities and privileges", they are free to step down.
- The community will adjust the list of maintainers based on the following factors
  - The activity level and contribution level of the maintainer in the past six months.
  - Balance of personnel among vendors.

In such a case:

- A PR is required to move the maintainer to the `Emeritus Maintainers` section of the [list of Karmada Maintainers](https://github.com/karmada-io/community/blob/main/MAINTAINERS.md).
- A PR is required to remove the maintainer from the [list of CNCF Maintainers](https://maintainers.cncf.io/).
- Remove the maintainer from the [Karmada Maintainer mailing list](cncf-karmada-maintainers@lists.cncf.io)

## Inactive members

_Members are continuously active contributors in the community._

A core principle in maintaining a healthy community is encouraging active
participation. It is inevitable that people's focuses will change over time and
they are not expected to be actively contributing forever.

However, being a member of one of the Karmada GitHub organizations comes with
an elevated set of permissions. These capabilities should not be used by those
that are not familiar with the current state of the Karmada project.

Therefore members with an extended period away from the project with no activity
will be removed from the Karmada Github Organizations and will be required to
go through the org membership process again after re-familiarizing themselves
with the current state.

### How inactivity is measured

Inactive members are defined as members of one of the Karmada Organizations
with **no** contributions across any organization within 18 months. This is
measured by the CNCF [DevStats project].

**Note:** Devstats does not take into account non-code contributions. If a
non-code contributing member is accidentally removed this way, they may open an
issue to quickly be re-instated.


After an extended period away from the project with no activity
those members would need to re-familiarize themselves with the current state
before being able to contribute effectively.

[contributor guide]: /contributors/guide/README.md
[Karmada mailling list]: https://groups.google.com/forum/#!forum/karmada
[membership request]: https://github.com/karmada-io/community/issues/new?assignees=&labels=area%2Fgithub-membership&template=membership.yml&title=REQUEST%3A+New+membership+for+%3Cyour-GH-handle%3E
[New contributors]: /CONTRIBUTING.md
[OWNERS]: /contributors/guide/owners.md
[two-factor authentication]: https://help.github.com/articles/about-two-factor-authentication
[Devstats project]: https://karmada.devstats.cncf.io/
[Maintainers]: https://github.com/karmada-io/karmada/blob/master/MAINTAINERS.md