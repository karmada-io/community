# Security Policy

## Report a vulnerability

We sincerely request you to keep the vulnerability information confidential and responsibly disclose the vulnerabilities.

To report a vulnerability, please contact the Security Team: [cncf-karmada-security@lists.cncf.io](mailto:cncf-karmada-security@lists.cncf.io). You can email the Security Team with the security details and the details expected for [Karmada bug reports](https://github.com/karmada-io/karmada/blob/master/.github/ISSUE_TEMPLATE/bug-report.md). 

The information of the Security Team members can be found [here](security-groups.md#the-security-team).

### E-mail Response

The team will help diagnose the severity of the issue and determine how to address the issue. The reporter(s) can expect a response within 2 business day acknowledging the issue was received. If a response is not received within 2 business day, please reach out to any Security Team member directly to confirm receipt of the issue. We’ll try to keep you informed about our progress throughout the process.

### When Should I Report a Vulnerability?

- You think you discovered a potential security vulnerability in Karmada
- You are unsure how a vulnerability affects Karmada

### When Should I NOT Report a Vulnerability?

- You need help tuning Karmada components for security
- You need help applying security related updates
- Your issue is not security related

If you think you discovered a vulnerability in another project that Karmada depends on, and that project has their own vulnerability reporting and disclosure process, please report it directly there.

## Security release process

The Karmada community will strictly handle the reporting vulnerability according to this [procedure](security-release-process.md). The following flowchart shows the vulnerability handling process.

<img src="./images/Vulnerability-handling-process.PNG">

## Relative Mailing lists

- [cncf-karmada-security@lists.cncf.io](mailto:cncf-karmada-security@lists.cncf.io), is for reporting security concerns to the Karmada Security Team, who uses the list to privately discuss security issues and fixes prior to disclosure.

- [cncf-karmada-distributors-announce@lists.cncf.io](mailto:cncf-karmada-distributors-announce@lists.cncf.io), is for advance private information and vulnerability disclosure. 

More details of group membership is managed [here](security-groups.md).

See the [private-distributors-list](private-distributors-list.md) for information on how Karmada distributors or vendors can apply to join this list.

## Supported versions

Karmada versions are expressed as x.y.z, where x is the major version, y is the minor version, and z is the patch version, following [Semantic Versioning](https://semver.org/) terminology.

The Karmada project maintains release branches for the most recent three minor releases. Applicable fixes, including security fixes, may be backported to those three release branches, depending on severity and feasibility.

Our typical patch release cadence is every 3 months. Critical bug fixes may cause a more immediate release outside of the normal cadence. We also aim to not make releases during major holiday periods.

See the [Karmada releases page](https://github.com/karmada-io/karmada/releases) for information on supported versions of Karmada.

## Dependencies policy

Dependencies are evaluated before being introduced to ensure they:

1) are actively maintained
2) are maintained by trustworthy maintainers 
3) are licensed in a way not to impact the Karmada license based on [the CNCF license allowlist](https://github.com/cncf/foundation/blob/main/allowed-third-party-license-policy.md).


These evaluations vary from dependency to dependencies.

Dependencies are also scheduled for removal if the project has been deprecated or if the project is no longer maintained. Additionally based on license changes we replace dependencies as necessary.

CVEs in dependencies will be patched for all supported versions if the CVE is applicable and is assessed by [trivy](https://github.com/aquasecurity/trivy). Automation generates a new [trivy scan](https://github.com/karmada-io/karmada/blob/master/.github/workflows/ci-image-scanning.yaml) after each pull request gets merged and alerts are addressed.