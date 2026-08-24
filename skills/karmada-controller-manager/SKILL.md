---
name: karmada-controller-manager
description: Use when a Karmada operator needs to inspect or rule out karmada-controller-manager process health, controller enablement, leader election, runtime flags, logs, events, or ownership, or when a contributor needs to add or change a controller, option, flag, registration, test, or RBAC wiring in karmada-controller-manager. Use karmada-debug-propagation for a generic end-to-end workload incident unless the request explicitly targets controller-manager ownership or implementation. Do not use for kube-controller-manager, Search internals, scheduler-only placement, or policy YAML.
---

# Operate and Develop Karmada Controller Manager

Determine whether an incident is owned by `karmada-controller-manager` or by an adjacent Karmada
component before proposing remediation, or trace the complete checkout-local implementation path for
an explicitly requested controller-manager change.

## Runtime Mode

- Package-only mode supports ownership triage from bundled boundaries and supplied flags, logs,
  events, and status; do not claim exact implementation paths.
- Package-only ownership decisions may identify the component named by supplied conditions or logs,
  but must not name exact predicates, registrations, initializer paths, or controller internals as
  current behavior. Keep those implementation details unverified until a compatible checkout is
  inspected.
- Packaged controller names and defaults are navigation baselines, not proof of the user's current
  build. In package-only mode, do not assert exact registration, default enablement, or feature-gate
  state without matching build or runtime evidence.
- In particular, never mention `WorkWithinPushClusterPredicate` or claim how `execution` and
  `workStatus` are registered in a package-only answer. Supplied Pull-mode agent evidence can
  support routing the next check to the agent without proving those internals.
- With a compatible Karmada checkout, verify exact controller ownership and development paths
  against registration, options, controllers, RBAC, and tests when needed.
- Live process and controller conclusions require supplied runtime evidence.

## Workflow

1. Establish package-only versus checkout-enhanced mode, then read
   `references/controller-checklist.md` as a runtime runbook. In package-only mode, source paths and
   named predicates in that reference are navigation hints only and must not appear as inspected
   evidence or exact current behavior. Do not require shared knowledge directories, generated
   source maps, website pages, or external documentation.
2. Confirm the incident boundary and ask for missing inputs that affect the next read-only step:
   Karmada control-plane context, Karmada namespace, component install method when known, target
   Cluster name, sync mode, affected resource or controller name, incident time window, current
   component args, and last known good state.
3. Start read-only. Use `get`, `describe`, events, JSONPath, health endpoints, metrics, and bounded
   logs. Do not restart, scale, patch args, disable leader election, edit `--controllers`, broaden
   RBAC, remove finalizers, taint clusters, or delete Works until evidence identifies a specific fix
   and the operator explicitly confirms mutation. If the user asks for "commands to fix it now" but
   has not confirmed a specific mutation after seeing evidence, provide only read-only commands and a
   separate remediation plan without write commands.
   Before any controller enable/disable proposal, collect current deployment args, build or checkout
   identity, startup logs covering controller registration and leader election, Lease, Cluster
   conditions, and events. Name each of those inputs explicitly rather than treating recent runtime
   logs or an image string alone as startup or build evidence. Explain that a controller flag
   change affects every object reconciled by that controller in the control plane, not only the
   reported Cluster, and require explicit confirmation of that scope.
4. Classify the suspected boundary:
   - process/config: pod health, args, `--controllers`, leader election, probes, metrics
   - controller enablement: controller name, disabled-by-default status, startup log evidence
   - cluster status/failover: `cluster`, `clusterStatus`, `clustertaintpolicy`, `gracefulEviction`
   - binding/Work generation: `binding` and `bindingStatus`
   - push-mode execution/status: `execution` and `workStatus` for Push clusters only
   - status aggregation: `bindingStatus`, `workStatus`, resource interpreter evidence
5. For each stage, state whether controller-manager ownership is `supported`, `not supported`,
   `failed`, `stale`, or `unknown`, with the exact object, flag, condition, event, or log evidence.
6. If the issue is a full workload propagation pipeline, first decide whether controller-manager is
   supported or ruled out from supplied evidence. Route to `karmada-debug-propagation` when the
   failure is outside controller-manager or needs end-to-end propagation triage.
7. Return confirmed facts, missing inputs, controller ownership map, first failing boundary, next
   read-only commands, likely causes ranked by evidence, and a separate remediation section that asks
   for confirmation before production mutation. The response that first identifies a likely fix must
   not include executable write commands; wait for the operator to confirm that exact fix in a later
   turn.

## Contributor workflow

When the primary request is to implement a controller-manager change rather than diagnose a live
incident:

1. Read the implementation section of `references/controller-checklist.md` and inspect the current
   checkout before proposing edits.
2. Trace controller package ownership, initializer registration in
   `cmd/controller-manager/app/controllermanager.go`, controller context dependencies, and focused
   reconciliation tests.
3. For options or flags, trace defaults, validation, flag binding, config propagation, generated
   command documentation, deployment manifests, and compatibility behavior.
4. Review controller enablement, disabled-by-default registration, leader requirements, RBAC,
   deployment manifests, metrics, events, and feature gates affected by the change.
5. Implement and run the narrowest unit tests first, then broader controller-manager tests required
   by shared registration or option changes.
6. Keep contributor implementation separate from live-cluster remediation. Code changes do not
   authorize deployment mutation.

## Guardrails

- A controller package or controller name alone does not prove the controller is enabled, leader, or
  reconciling.
- `--controllers=*` generally enables on-by-default controllers; explicitly named controllers are
  enabled and `-name` disables a controller. Treat packaged examples such as
  `hpaScaleTargetMarker` and `deploymentReplicasSyncer` as unverified for the user's build until a
  compatible checkout, startup log, or current arguments establish their registration and default.
- Push and Pull clusters have different owners. `karmada-controller-manager` handles execution and
  Work status for Push clusters. Pull-mode execution and Work status belong to `karmada-agent`.
- Do not confuse Karmada controller-manager with Kubernetes kube-controller-manager.
- Do not assume every controller runs in karmada-agent or scheduler.
- Never include `rollout restart`, `scale`, `set resources`, `patch`, `apply`, `delete`, RBAC edits,
  leader-election changes, controller-arg changes, finalizer removal, taints, or Work edits in the
  first response unless the operator has explicitly confirmed that exact mutation after evidence.
- Phrases like "give the next answer", "what should I do next", or "show the fix" are not
  confirmation. Accept confirmation only when the operator explicitly approves the named mutation,
  such as changing `--controllers` on the `karmada-controller-manager` Deployment.

## Routing boundaries

Use another skill when the primary request is not a controller-manager operational boundary:

- `karmada-debug-propagation`: concrete workload propagation incident before controller-manager
  ownership is isolated, or after this skill rules controller-manager out.
- `karmada-explain-placement`: scheduler cluster or replica placement explanation.
- `karmada-search`: Search API, indexing, APIService, or stale Search results.
- Karmada webhook/admission guidance: validation, mutation, or admission rejection before
  reconciliation reaches controller-manager.
- `karmada-create-policy` or `karmada-audit-policy`: policy generation or static YAML review.
- `karmada-knowledge`: general architecture, component overview, or object-flow explanation.
