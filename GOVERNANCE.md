# Karmada Project Governance

The Karmada project is dedicated to creating open, multi-cloud, multi-cluster
Kubernetes orchestration.  
This governance explains how the project is run.

- [Values](#values)
- [Membership](#membership)
- [Meetings](#meetings)
- [CNCF Resources](#cncf-resources)
- [Code of Conduct Enforcement](#code-of-conduct)
- [Security Response Team](#security-response-team)
- [Voting](#voting)
- [Modifications](#modifying-this-charter)

## Values

The Karmada and its leadership embrace the following values:

* Openness: Communication and decision-making happens in the open and is discoverable for future
  reference. As much as possible, all discussions and work take place in public
  forums and open repositories.

* Fairness: All stakeholders have the opportunity to provide feedback and submit
  contributions, which will be considered on their merits.

* Community over Product or Company: Sustaining and growing our community takes
  priority over shipping code or sponsors' organizational goals. Each
  contributor participates in the project as an individual.

* Inclusivity: We innovate through different perspectives and skill sets, which
  can only be accomplished in a welcoming and respectful environment.

* Participation: Responsibilities within the project are earned through
  participation, and there is a clear path up the contributor ladder into leadership
  positions.

## Membership

The [Community Membership](https://github.com/karmada-io/community/blob/main/community-membership.md)
outlines responsibilities and requirements for different roles in Karmada.

Currently, the maintainers are the governing body for the project. This may 
change as the community grows, such as by adopting an elected steering committee.

## Meetings

Regular meetings are described at [Community Meeting](https://github.com/karmada-io/community/#community-meeting).

Maintainers will also have closed meetings in order to discuss security reports
or Code of Conduct violations. Such meetings should be scheduled by any
Maintainer on receipt of a security issue or CoC report. All current Maintainers
must be invited to such closed meetings, except for any Maintainer who is
accused of a CoC violation.

## CNCF Resources

Any Maintainer may suggest a request for CNCF resources, by filing a request
on [Service Desk](https://cncfservicedesk.atlassian.net/servicedesk/customer/portals),
the request should be shared with all maintainers. The Maintainers may also 
choose to delegate working with the CNCF to non-Maintainer community members, 
who will then be added to the [CNCF's Maintainer List](https://github.com/cncf/foundation/blob/main/project-maintainers.csv)
for that purpose.

## Code of Conduct

[Code of Conduct](./CODE_OF_CONDUCT.md)
violations by community members will be referred to the CNCF Code of Conduct
Committee. Should the CNCF CoC Committee need to work with the project on resolution, the
Maintainers will appoint a non-involved contributor to work with them.

## Subprojects

The subprojects of Karmada are closely related to the main project, serving as essential supplements that need to be
released synchronously with the main version when necessary. Among other listed projects, some are for exploratory 
purposes while others are related to peripheral ecosystem products.

Current Sub-Projects:
- [Dashboard](https://github.com/karmada-io/dashboard): Karmada Dashboard is a general-purpose, web-based control 
panel for Karmada.

The Karmada organization is open to receive new subprojects under its umbrella. To accept a project
into the __Karmada__ organization, it has to meet the following criteria:

- Must be licensed under the terms of the Apache License v2.0.
- Must be closely related to one or more areas of the Karmada ecosystem, and Karmada relies heavily on these projects.
- Must be supported by a Maintainer not associated or affiliated with the author(s) of the subprojects.
- Sub-Projects can have their own repositories but follow the same governance mechanism as the main project.
- Joining a subproject requires submitting an issue in the main project to obtain a 2/3 vote of approval from the Maintainers. Similarly, significant actions such as project archiving also require the consent of the Maintainers.

The submission process starts as an Issue on the
[karmada-io/community](https://github.com/karmada-io/community) repository with the required information
mentioned above. Once a project is accepted, it's considered a __subproject under the umbrella of Karmada__.

## Security Response Team

The Maintainers will appoint a Security Response Team to handle security reports.
This committee may simply consist of the Maintainer Council themselves.  If this
responsibility is delegated, the Maintainers will appoint a team of at least two 
contributors to handle it. The Maintainers will review who is assigned to this
at least once a year.

The Security Response Team is responsible for handling all reports of security
holes and breaches according to the [security policy](https://github.com/karmada-io/community/blob/main/security-team/SECURITY.md).

## Roadmap
### Rules
- Define goals: Clearly articulate the long-term and short-term objectives of the project. These goals should align with the project's vision and values while meeting the needs of users or the community.
- Prioritize: Rank the goals based on their importance and urgency. Considering resource and time constraints, ensure that the focus is placed on the most critical objectives.
- Time-based planning: Break down the goals into milestones or phased tasks. Define specific objectives and measurable metrics for each phase to evaluate progress later on.
- Transparency and communication: Share the roadmap openly with project stakeholders, including users, contributors, and other interested parties. This helps establish transparency and keeps everyone informed about the project's direction and plans.
- Continuous adjustment: The project roadmap should be a dynamic document that may require adjustments and updates over time as new insights are gained. Regularly review and reassess the roadmap, making modifications as needed.
- Approach: When creating the roadmap, take into account the opinions and suggestions of the community to ensure that the project's development aligns with broad expectations and needs.
- Engage in discussions with project users and contributors to gather feedback and understand their requirements. This can be done through channels such as mailing lists, forums, and social media.

### Changes in project Roadmap
- Proposals will be collected from mailing lists, forums, GitHub issues, community meetings, social media, etc.
- Changes to the project roadmap should be initiated as a pull request on GitHub.
- Maintainers will make decisions based on a majority vote.

## Voting

While most business in Karmada is conducted by "[lazy consensus](https://community.apache.org/committers/lazyConsensus.html)", 
periodically the Maintainers may need to vote on specific actions or changes.
A vote can be taken on [the developer mailing list](https://groups.google.com/forum/#!forum/karmada) or
[community repo issue](https://github.com/karmada-io/community/issues/new/choose) 
for security or conduct matters. Votes may also be taken at [the developer meeting](https://github.com/karmada-io/community/#community-meeting).
Any Maintainer may demand a vote be taken.

Most votes require a simple majority of all Maintainers to succeed, except where
otherwise noted. Two-thirds majority votes mean at least two-thirds of all 
existing maintainers.

## Modifying this Charter

Changes to this Governance and its supporting documents may be approved by 
a 2/3 vote of the Maintainers.
