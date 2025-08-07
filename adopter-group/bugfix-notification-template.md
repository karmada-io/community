<!--
This template is used by the Karmada community to notify adopters when a critical issue or bug has been identified that 
may impact the stability, security, or functionality of Karmada deployments. It provides a standardized format for 
communicating the nature of the issue, affected versions, remediation steps, and relevant tracking information to ensure
users can take prompt and informed action.
-->

Subject: [Action Required] [bugfix #0000]: [issue description]

---

Dear Karmada Adopters,

We are reaching out to inform you of a recently identified critical issue affecting Karmada. Karmada has released an 
urgent bugfix to address this problem and strongly recommends that all users take immediate action to ensure the 
stability and security of your Karmada deployments.

**Summary of the Issue:**

_Briefly describe the bug, its impact, and how it may affect users. Example: "An issue was discovered in the resource 
scheduling component that could lead to unexpected workload placement."_

**Am I Affected:**

_Describe how users can determine if they are affected by this issue. For example: "You are affected if you are running
any of the affected versions listed below, or if your deployment matches the following conditions..." Provide clear 
steps or criteria for users to check their environment. For example: You are affected by this issue if any of the 
following conditions are true: describe the condition in detail._

**Affected Versions:**

_List the affected components and versions, for example:_
```
- karmada-controller-manager: < v1.14.2
- karmada-controller-manager: < v1.13.5
- karmada-controller-manager: < v1.12.8
```

**Fixed Version:**
_For example:_
```
- v1.14.2
- v1.13.5
- v1.12.8
```

**Bugfix Details:**

- Track Issue: _issue link for track this bugfix if any_
- Fixed Pull Requests: _Pull Request list for this bugfix_
_For example:_
```
- master: https://github.com/karmada-io/karmada/pull/6434
- release-1.14: https://github.com/karmada-io/karmada/pull/6583
- release-1.13: https://github.com/karmada-io/karmada/pull/6584
- release-1.12: https://github.com/karmada-io/karmada/pull/6585
```
- Follow-up tracking issue: _issue link for track followup tasks if any_

**Recommended Actions:**

1. Review the information above and evaluate how this issue may impact your environment.
2. Upgrade your Karmada installation to the latest fixed version as soon as possible.

**Workaround:**

_If a workaround is available before upgrading, describe it here. For example: "As a temporary mitigation, you can 
update the relevant configuration settings in your deployment to reduce the impact of the issue. Please refer to the 
specific configuration guidance provided for this bug." If no workaround exists, state: "There is currently no 
workaround; upgrading to a fixed version is required."_

If you have any questions or need assistance with the upgrade process, please do not hesitate to reach out to the 
Karmada community or support channels.

Thank you for your prompt attention to this matter and for being a valued member of the Karmada Adopter Group.

Thanks,  
[Your Name] on behalf of the Karmada Maintainers
