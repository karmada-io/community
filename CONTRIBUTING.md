# Contributing

Welcome to Karmada!

-   [Before you get started](#before-you-get-started)
    -   [Code of Conduct](#code-of-conduct)
    -   [Community Expectations](#community-expectations)
-   [Getting started](#getting-started)
-   [Your First Contribution](#your-first-contribution)
    -   [Find something to work on](#find-something-to-work-on)
        -   [Find a good first topic](#find-a-good-first-topic)
        -   [Work on an Issue](#work-on-an-issue)
        -   [File an Issue](#file-an-issue)
-   [Contributor Workflow](#contributor-workflow)
    -   [Creating Pull Requests](#creating-pull-requests)
        -   [PR Checklist](#pr-checklist)
    -   [Commit Message Standards](#commit-message-standards)
    -   [Review Timeline](#review-timeline)
    -   [Testing](#testing)
    -   [Code Review](#code-review)
    -   [Repository Setup](#repository-setup)

# Before you get started

## Code of Conduct

Please make sure to read and observe our [Code of Conduct](/CODE_OF_CONDUCT.md).

## Community Expectations

Karmada is a community project driven by its community which strives to promote a healthy, friendly and productive environment.
Karmada aims to provide turnkey automation for multi-cluster application management in multi-cloud and hybrid cloud scenarios,
and intended to realize multi-cloud centralized management, high availability, failure recovery and traffic scheduling.

# Getting started

- Fork the repository on GitHub.
- Make your changes on your fork repository.
- Submit a PR.


# Your First Contribution

We will help you to contribute in different areas like filing issues, developing features, fixing critical bugs and
getting your work reviewed and merged.

If you have questions about the development process,
feel free to [file an issue](https://github.com/karmada-io/karmada/issues/new/choose).

## Find something to work on

We are always in need of help, be it fixing documentation, reporting bugs or writing some code.
Look at places where you feel best coding practices aren't followed, code refactoring is needed or tests are missing.
Here is how you get started.

### Find a good first topic

There are [multiple repositories](https://github.com/karmada-io/) within the Karmada organization.
Each repository has beginner-friendly issues that provide a good first issue.
For example, [karmada-io/karmada](https://github.com/karmada-io/karmada) has
[help wanted](https://github.com/karmada-io/karmada/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22) and
[good first issue](https://github.com/karmada-io/karmada/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22)
labels for issues that should not need deep knowledge of the system.
We can help new contributors who wish to work on such issues.

Another good way to contribute is to find a documentation improvement, such as a missing/broken link.
Please see [Contributing](#contributing) below for the workflow.

#### Work on an issue

When you are willing to take on an issue, just reply on the issue. The maintainer will assign it to you.

### File an Issue

While we encourage everyone to contribute code, it is also appreciated when someone reports an issue.
Issues should be filed under the appropriate Karmada sub-repository.

*Example:* a Karmada issue should be opened to [karmada-io/karmada](https://github.com/karmada-io/karmada/issues).

Please follow the prompted submission guidelines while opening an issue.

# Contributor Workflow

Please do not ever hesitate to ask a question or send a pull request.

This is a rough outline of what a contributor's workflow looks like:

- Create a topic branch from where to base the contribution. This is usually master.
- Make commits of logical units.
- Push changes in a topic branch to a personal fork of the repository.
- Submit a pull request to the repository you forked.

## Creating Pull Requests

Pull requests are often called simply "PR".
Karmada generally follows the standard [github pull request](https://help.github.com/articles/about-pull-requests/) process.
To submit a proposed change, please develop the code/fix and add new test cases.
After that, run whatever verification steps the target repository's contributing guide specifies before submitting a pull request to predict the pass or
fail of continuous integration.

### PR Checklist

Before submitting your PR, confirm the following:

- [ ] Commits follow the [Commit Message Standards](#commit-message-standards) below with DCO sign-off (`git commit -s`)
- [ ] PR description explains what changed and why
- [ ] Related issue is linked (`Fixes #123` or `Refs #123`)
- [ ] PR is scoped to one logical change; unrelated changes are split into separate PRs
- [ ] Verification steps documented in the target repository have been run

## Commit Message Standards

Karmada follows a conventional commit format across all repositories.

### Format

```
<type>(<scope>): <short summary>

<optional body>

<optional footer>
```

### Rules

- **Subject line**: 50 characters or fewer, imperative mood ("fix bug" not "fixed bug")
- **Type**: one of `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`
- **Scope**: the component affected (e.g., `scheduler`, `docs`, `api`)
- **Body**: explain the *why*, not the *what*
- **Footer**: reference issues (`Fixes #123`)

### Examples

```
fix(scheduler): correct replica count overflow
```

```
docs(contributing): add commit standards and PR guidelines
```

### DCO Sign-off

All commits must include a Developer Certificate of Origin sign-off:

```bash
git commit -s -m "type(scope): your message"
```

This appends `Signed-off-by: Your Name <your@email.com>` to the commit.

For more guidance, see [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/).

## Review Timeline

Maintainers aim to provide an initial review response within **5 business days**.

If you haven't received feedback after **7 days**, feel free to:

1. Leave a polite comment on the PR asking for a status update.
2. Ping the relevant reviewer from [REVIEWERS.md](REVIEWERS.md) or [APPROVERS.md](APPROVERS.md).
3. Ask in the [#karmada Slack channel](https://cloud-native.slack.com/archives/C02MUF8QXUN).

Note that maintainers are volunteers — please be patient and respectful.

## Testing

Testing requirements vary by repository. In general:

- New features should include tests that cover the happy path and key error cases.
- Bug fixes should include a regression test that fails before the fix and passes after.
- For code repositories, run the unit and integration tests documented in that repo before opening a PR.
- Refer to the target repository's contributing guide for specific test commands and coverage expectations.

## Code Review

To make it easier for your PR to receive reviews, consider the reviewers will need you to:

* follow [good coding guidelines](https://github.com/golang/go/wiki/CodeReviewComments).
* write [good commit messages](https://chris.beams.io/posts/git-commit/).
* break large changes into a logical series of smaller patches which individually make easily understandable changes, and in aggregate solve a broader issue.

## Repository Setup

Since the Karmada organization has multiple repositories, environment setup differs per repo. Before contributing, check the contributing guide of the specific repo you are working in:

| Repository | Setup docs |
|---|---|
| [karmada-io/karmada](https://github.com/karmada-io/karmada) | [CONTRIBUTING.md](https://github.com/karmada-io/karmada/blob/master/CONTRIBUTING.md) |
| [karmada-io/website](https://github.com/karmada-io/website) | [README.md](https://github.com/karmada-io/website/blob/main/README.md) |
| [karmada-io/community](https://github.com/karmada-io/community) | This file — docs/governance only, no build step required |
| Other repos | See [github.com/karmada-io](https://github.com/karmada-io) |
