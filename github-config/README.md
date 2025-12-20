# GitHub Organization Management

This directory contains the configuration for managing the Karmada GitHub organization, including team memberships, repository settings, and access controls.

## Purpose

The configurations in this directory serve to:

- Transparency: All team memberships and repository permissions are publicly visible and tracked in version control
- Automation: Changes are automatically applied through pull requests and reviews
- Accountability: Every permission change has a clear history and approval process

## Structure

- `config.yaml` - Complete configuration for teams, members, and repository permissions

## Making Changes

To modify team memberships or repository permissions:

1. Create a pull request with your proposed changes
2. Get approval from appropriate maintainers/approvers
3. Changes will be automatically applied after merge

## Automation

This directory uses [CNCF CLOWarden](https://github.com/cncf/clowarden) to automate the management of teams, members, and repository permissions.

### How It Works

- **Pull Request Validation**: When a PR is submitted, CLOWarden validates the configuration file for correctness and compliance
- **Automatic Application**: After the PR is merged, CLOWarden automatically applies the changes to the GitHub organization
- **Periodic Reconciliation**: CLOWarden periodically reconciles the actual state with the desired state to ensure consistency

### What Gets Managed

- **Teams**: Fully managed by CLOWarden
  - Teams not defined in the configuration will be removed during reconciliation
  - Team maintainers and members not defined in the configuration will be removed from teams

- **Team Members**: Managed at the team level
  - Team membership (both maintainers and members) is defined per team
  - Team members not defined in the configuration will be removed from their teams during reconciliation

- **Organization Members**: Not managed by CLOWarden
  - Organization-level members (those not assigned to any team) are completely outside CLOWarden's scope
  - These members will not be affected by any reconciliation process
  - Organization membership must be managed separately through GitHub settings

- **Repositories**: Completely protected from deletion
  - CLOWarden **does NOT support repository deletion operations**
  - Repositories can only be added via configuration, never removed
  - This is a deliberate safety design to prevent accidental data loss
  - Even if a repository is removed from the configuration, the actual GitHub repository will remain untouched

For more information about CLOWarden, visit the [official repository](https://github.com/cncf/clowarden).
