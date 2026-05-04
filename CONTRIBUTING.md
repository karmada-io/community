# Contributing

Welcome to Karmada!

-   [Before you get started](#before-you-get-started)
    -   [Code of Conduct](#code-of-conduct)
    -   [Community Expectations](#community-expectations)
-   [Getting started](#getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Local Development Setup](#local-development-setup)
-   [Your First Contribution](#your-first-contribution)
    -   [Find something to work on](#find-something-to-work-on)
        -   [Find a good first topic](#find-a-good-first-topic)
        -   [Work on an Issue](#work-on-an-issue)
        -   [File an Issue](#file-an-issue)
-   [Contributor Workflow](#contributor-workflow)
    -   [Creating Pull Requests](#creating-pull-requests)
    -   [PR Checklist](#pr-checklist)
    -   [Commit Message Standards](#commit-message-standards)
    -   [Code Review](#code-review)
    -   [Review Timeline](#review-timeline)
    -   [Testing](#testing)

# Before you get started

## Code of Conduct

Please make sure to read and observe our [Code of Conduct](/CODE_OF_CONDUCT.md).

## Community Expectations

Karmada is a community project driven by its community which strives to promote a healthy, friendly and productive environment.
Karmada aims to provide turnkey automation for multi-cluster application management in multi-cloud and hybrid cloud scenarios,
and intended to realize multi-cloud centralized management, high availability, failure recovery and traffic scheduling.

# Getting started

## Prerequisites

Before contributing, make sure the following tools are installed and configured on your local machine:

| Tool | Version | Purpose |
|------|---------|---------|
| [Go](https://golang.org/dl/) | 1.22 or later (see go.mod) | Primary language for Karmada |
| [Git](https://git-scm.com/) | Any recent version | Version control |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | v1.28 or later | Interact with Kubernetes clusters |
| [Docker](https://docs.docker.com/get-docker/) | Any recent version | Build and run container images |
| [make](https://www.gnu.org/software/make/) | Any recent version | Run build and verification scripts |

Verify your Go installation:

```bash
go version
# Expected: go version go1.22.x ...
```

## Local Development Setup

1. **Fork** the repository on GitHub by clicking the **Fork** button on [karmada-io/karmada](https://github.com/karmada-io/karmada).

2. **Clone** your fork locally:

```bash
git clone https://github.com/<your-github-username>/karmada.git
cd karmada
```

3. **Add the upstream remote** so you can stay in sync with the main repository:

```bash
git remote add upstream https://github.com/karmada-io/karmada.git
git fetch upstream
```

4. **Keep your fork up to date** before starting new work:

```bash
git checkout master
git pull upstream master
```

5. **Create a topic branch** for your change:

```bash
git checkout -b fix/my-descriptive-branch-name
```

6. **Build the project** to confirm your setup is working:

```bash
make all
```

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
- Submit a pull request to [karmada-io/karmada](https://github.com/karmada-io/karmada).

## Creating Pull Requests

Pull requests are often called simply "PR".
Karmada generally follows the standard [github pull request](https://help.github.com/articles/about-pull-requests/) process.
To submit a proposed change, please develop the code/fix and add new test cases.
After that, run these local verifications before submitting pull request to predict the pass or
fail of continuous integration.

* Run and pass `make verify`
* Run and pass `make test`

## PR Checklist

Before submitting your PR, confirm the following:

- [ ] Code compiles without errors (`make all`)
- [ ] All verification checks pass (`make verify`)
- [ ] All tests pass (`make test`)
- [ ] New functionality includes corresponding unit tests
- [ ] Commit messages follow the [Commit Message Standards](#commit-message-standards) below
- [ ] The PR description explains **what** changed and **why**
- [ ] Related issue is linked in the PR description (e.g., `Fixes #123`)
- [ ] The PR is focused — one logical change per PR; split unrelated changes into separate PRs

## Commit Message Standards

Well-structured commit messages make it easier to review changes and maintain a clean project history.
Karmada follows a standard format inspired by [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/).

### Format

```
<type>(<scope>): <short summary>

<optional body>

<optional footer>
```

### Rules

- **Subject line**: 50 characters or fewer, written in the **imperative mood** ("fix bug" not "fixed bug")
- **Type**: one of `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`
- **Scope**: the component or area affected (e.g., `scheduler`, `webhook`, `api`, `docs`)
- **Body**: explain the *why* behind the change, not the *what* (the diff shows what changed)
- **Footer**: reference related issues or PRs (e.g., `Fixes #456`)

### Examples

**Good commit messages:**

```
feat(scheduler): add priority-based binding eviction support

Prior to this change, bindings were evicted in FIFO order regardless
of priority, causing high-priority workloads to be starved.

Fixes #1234
```

```
fix(webhook): validate cluster name length on registration

Cluster names exceeding 253 characters caused silent failures
downstream in the DNS resolution layer.

Fixes #5678
```

```
docs(contributing): expand setup and commit message guidance
```

**Avoid:**

```
fixed stuff         # too vague
WIP                 # not a complete commit
Update file.go      # describes what, not why
```

### Sign-off

All commits must include a `Signed-off-by` line (DCO — Developer Certificate of Origin):

```bash
git commit -s -m "feat(scope): your commit message"
```

This adds the following to your commit automatically:

```
Signed-off-by: Your Name <your@email.com>
```

## Code Review

To make it easier for your PR to receive reviews, consider the reviewers will need you to:

* follow [good coding guidelines](https://github.com/golang/go/wiki/CodeReviewComments).
* write [good commit messages](https://chris.beams.io/posts/git-commit/).
* break large changes into a logical series of smaller patches which individually make easily understandable changes, and in aggregate solve a broader issue.

## Review Timeline

The Karmada maintainers aim to provide an initial review response within **5 business days**.
For urgent bug fixes or security issues, response times may be faster.

If you haven't received any feedback after **7 days**, feel free to:

1. Leave a comment on the PR politely asking for a review status update.
2. Ping the relevant reviewer or maintainer listed in [APPROVERS.md](/APPROVERS.md) or [REVIEWERS.md](/REVIEWERS.md).
3. Raise the topic in the [Karmada Slack channel](https://cloud-native.slack.com/archives/C02MUG27SRS).

Note that maintainers are volunteers — please be patient and respectful.

## Testing

All contributions should maintain or improve test coverage. Follow these guidelines:

### Unit Tests

- Place unit tests in the same package as the code being tested (e.g., `foo_test.go` alongside `foo.go`).
- Test individual functions and edge cases in isolation.
- Run unit tests with:

```bash
make test
```

### Integration Tests

- Integration tests verify interactions between components and live in the `test/` directory.
- Run integration tests with:

```bash
make e2e-test
```

### Verification

Before pushing, always run the full verification suite to catch formatting, linting, and import issues:

```bash
make verify
```

### Coverage

- New features must include unit tests covering the happy path and key error cases.
- Bug fixes should include a test that fails before the fix and passes after.
- Aim to keep coverage equal to or higher than the existing baseline.
