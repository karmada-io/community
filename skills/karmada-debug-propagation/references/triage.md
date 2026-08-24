# Propagation Incident Triage

This runbook is for concrete Karmada propagation incidents. It is self-contained for runtime use:
do not require shared knowledge directories, generated source maps, website pages, or external docs
to answer.

The goal is to find the first stage where evidence is missing, stale, or failed. Keep production
diagnostics read-only until the operator confirms a specific mutation plan.

Implementation paths in this runbook are citation hints. Do not open them during normal incident
triage unless supplied evidence conflicts with the runbook, the user asks for source-level detail, or
the first failing stage depends on exact current-checkout behavior.

## Required Incident Inputs

Ask for missing inputs before diagnosing when they affect the next step:

- Workload identity: `apiVersion`, `kind`, `name`, and `namespace` for namespaced resources.
- Karmada control-plane kube context.
- Target member cluster name.
- Member cluster kube context when member-side evidence is needed.
- Cluster registration mode if known: push or pull.
- Related PropagationPolicy, ClusterPropagationPolicy, ResourceBinding, ClusterResourceBinding, or
  Work name if the operator already has it.
- Incident time window and last known good state.

If some inputs are unknown, give read-only commands that discover them. Do not guess.

## Mutation Guardrails

Start with read-only evidence:

- Allowed first: `kubectl get`, `kubectl describe`, `kubectl logs`, `kubectl get events`, JSONPath,
  field selectors, label selectors, and `--since` or `--tail` bounded log reads.
- Before explicit operator confirmation, remediation must be prose only. Do not output write-command
  syntax, code blocks, or one-liners that mutate source workloads, member objects, policies,
  bindings, Works, controller state, or cluster state.
- This includes any `kubectl` command whose verb is `apply`, `patch`, `delete`, `create`, `replace`,
  `edit`, `scale`, `set`, `label`, `annotate`, or `rollout`, even when the user asks for a fast
  command or evidence points to a clear fix. Use prose such as "confirm whether you want a member
  object image patch plan" instead of the command.
- If evidence points to a production mutation, separate it into a remediation plan, explain blast
  radius, and ask for explicit confirmation before giving write commands.
- Do not diagnose network, RBAC, webhook, interpreter, scheduler, agent, or member API failure unless
  evidence from that boundary supports it.
- Treat cleanup of orphan Works or finalizers as a remediation step, not a diagnostic shortcut.

## Stage Order

For each stage, record `supported`, `missing`, `stale`, `failed`, or `unknown`.

| Order | Stage | First evidence | Owner or source path |
|---|---|---|---|
| 1 | Source object and policy claim/detector | Source labels and annotations naming PropagationPolicy or ClusterPropagationPolicy; matching policy selectors; detector logs or events | `pkg/detector/claim.go`, `pkg/detector/compare.go`, `pkg/util/selector.go` |
| 2 | Binding object | ResourceBinding or ClusterResourceBinding exists; `spec.resource` matches the source; generation and observed conditions are current | Binding and scheduler controllers |
| 3 | Scheduling result | Binding `spec.clusters`, replicas, graceful eviction or suspension fields, scheduler events and logs | Scheduler writes binding scheduling result |
| 4 | Work generation | Work exists in `karmada-es-<cluster>` with expected manifest, annotations, labels, generation, finalizer, and suspend state | `pkg/controllers/binding/binding_controller.go`, `pkg/controllers/binding/cluster_resource_binding_controller.go`, `pkg/controllers/binding/common.go` |
| 5 | Execution namespace and cluster mode | Execution namespace exists; target Cluster object shows push or pull mode and Ready condition | `pkg/util/names/names.go`, cluster controller and cluster status controller |
| 6 | Push or pull execution owner | Push: `karmada-controller-manager` execution-controller handles Work. Pull: `karmada-agent` handles Work for its cluster. | `cmd/controller-manager/app/controllermanager.go`, `cmd/agent/app/agent.go`, `pkg/controllers/execution/execution_controller.go` |
| 7 | Member apply | Work conditions and events, execution logs, member object existence, member events | `pkg/controllers/execution/execution_controller.go` |
| 8 | Work status reflection | Work `status.manifestStatuses`, visible `Applied` condition, interpreter health/status events, member object annotations back to Work | `pkg/controllers/status/work_status_controller.go` |
| 9 | Binding and source status aggregation | ResourceBinding or ClusterResourceBinding aggregated status updated from Work; source object status updated from binding | `pkg/controllers/status/rb_status_controller.go`, `pkg/controllers/status/crb_status_controller.go` |

Do not skip a stage. For example, if a ResourceBinding is scheduled but the target Work is absent,
the first failing stage is Work generation. Do not blame the execution-controller, karmada-agent,
member networking, or member API until a Work exists and execution evidence is available.

## Stage 1: Source Object And Policy Claim

Purpose: prove that Karmada has claimed the source object with the intended policy, or identify
that detection/policy matching is the first failing stage.

Read-only evidence:

```bash
kubectl --context <karmada-context> -n <workload-namespace> get <kind> <name> -o yaml
kubectl --context <karmada-context> -n <policy-namespace> get propagationpolicy <policy-name> -o yaml
kubectl --context <karmada-context> get clusterpropagationpolicy <policy-name> -o yaml
kubectl --context <karmada-context> -n <workload-namespace> get events --field-selector involvedObject.name=<name> --sort-by=.lastTimestamp
kubectl --context <karmada-context> -n <karmada-system-namespace> logs deploy/karmada-controller-manager --since=<duration> --tail=<lines> | grep -E 'Matched policy|No propagationpolicy|No clusterpropagationpolicy|<name>'
```

What to check:

- Namespaced policy claim metadata should identify the PropagationPolicy namespace and name.
- Cluster policy claim metadata should identify the ClusterPropagationPolicy name.
- The policy `spec.resourceSelectors` should match the workload `apiVersion`, `kind`, namespace,
  name, or labels. Matching behavior comes from `pkg/util/selector.go`: name match takes precedence
  over label selector when both are set; empty name and empty label selector matches all resources of
  the selected apiVersion/kind/namespace.
- If multiple policies match, detector comparison uses explicit priority first, then implicit
  selector priority, then name ordering. See `pkg/detector/compare.go`.

First-failure examples:

- No claim metadata and no matching selector evidence: first failing stage is detector or policy
  match.
- Source object has claim metadata for an unexpected policy: first failing stage is policy selection,
  not Work execution.

## Stage 2: Binding Object

Purpose: prove that Karmada created the binding that references the source object.

Use ResourceBinding for namespaced resources and ClusterResourceBinding for cluster-scoped
resources.

Read-only evidence:

```bash
kubectl --context <karmada-context> -n <workload-namespace> get resourcebinding -o wide
kubectl --context <karmada-context> -n <workload-namespace> describe resourcebinding <binding-name>
kubectl --context <karmada-context> -n <workload-namespace> get resourcebinding <binding-name> -o yaml
kubectl --context <karmada-context> get clusterresourcebinding -o wide
kubectl --context <karmada-context> describe clusterresourcebinding <binding-name>
kubectl --context <karmada-context> get clusterresourcebinding <binding-name> -o yaml
```

What to check:

- `spec.resource` matches the workload group, version, kind, namespace, and name.
- Binding generation, labels, annotations, finalizers, and conditions are current.
- Binding exists before you inspect Work generation. If no binding exists, keep diagnosis at
  binding creation/scheduling input rather than execution.

## Stage 3: Scheduling Result

Purpose: distinguish "binding exists but unscheduled" from "scheduled but later stage failed".

Read-only evidence:

```bash
kubectl --context <karmada-context> -n <workload-namespace> get resourcebinding <binding-name> -o jsonpath='{.spec.clusters}{"\n"}{.status.conditions}{"\n"}'
kubectl --context <karmada-context> get clusterresourcebinding <binding-name> -o jsonpath='{.spec.clusters}{"\n"}{.status.conditions}{"\n"}'
kubectl --context <karmada-context> -n <workload-namespace> describe resourcebinding <binding-name>
kubectl --context <karmada-context> describe clusterresourcebinding <binding-name>
kubectl --context <karmada-context> -n <karmada-system-namespace> logs deploy/karmada-scheduler --since=<duration> --tail=<lines> | grep -E '<binding-name>|<workload-name>|<cluster-name>'
```

What to check:

- `spec.clusters` includes the expected cluster and replica assignment.
- Scheduling conditions and events explain unscheduled, suspended, or requeued work.
- If `spec.clusters` does not include the expected cluster but the user asks why, route or answer as
  placement explanation rather than propagation execution.

First-failure examples:

- Binding exists but `spec.clusters` is empty: first failing stage is scheduling.
- Binding is scheduled to member-a but Work is absent in `karmada-es-member-a`: first failing stage
  is Work generation.

## Stage 4: Work Generation

Purpose: prove that the binding controller transformed the binding and source workload into a Work
in the target execution namespace.

Karmada execution namespaces are named `karmada-es-<cluster>`.

Read-only evidence:

```bash
kubectl --context <karmada-context> get ns karmada-es-<cluster>
kubectl --context <karmada-context> -n karmada-es-<cluster> get work -o wide
kubectl --context <karmada-context> -n karmada-es-<cluster> get work <work-name> -o yaml
kubectl --context <karmada-context> -n karmada-es-<cluster> describe work <work-name>
kubectl --context <karmada-context> -n <workload-namespace> describe resourcebinding <binding-name>
kubectl --context <karmada-context> describe clusterresourcebinding <binding-name>
kubectl --context <karmada-context> -n <karmada-system-namespace> logs deploy/karmada-controller-manager --since=<duration> --tail=<lines> | grep -E 'ResourceBinding|ClusterResourceBinding|Sync work|SyncWork|<binding-name>|<workload-name>'
```

What to check:

- Work namespace equals `karmada-es-<target-cluster>`.
- Work manifest contains the intended workload after override and replica revision.
- Work annotations point back to the ResourceBinding or ClusterResourceBinding.
- Work labels include the binding permanent ID label.
- Work finalizers and suspend-dispatching state are expected.

Source behavior:

- `pkg/controllers/binding/binding_controller.go` and
  `pkg/controllers/binding/cluster_resource_binding_controller.go` reconcile bindings.
- `pkg/controllers/binding/common.go` `ensureWork` loops over target clusters, computes
  `karmada-es-<cluster>`, applies replica/override logic, and creates or updates Work objects.

First-failure examples:

- Scheduled binding plus no Work: binding-to-Work generation is the first failing stage.
- Work manifest exists but contains unexpected overrides or replicas: Work generation or override
  application is the first failing stage.

## Stage 5: Execution Namespace And Cluster Mode

Purpose: identify who owns Work execution before inspecting logs.

Read-only evidence:

```bash
kubectl --context <karmada-context> get cluster <cluster-name> -o yaml
kubectl --context <karmada-context> get cluster <cluster-name> -o jsonpath='{.spec.syncMode}{"\n"}{.status.conditions}{"\n"}'
kubectl --context <karmada-context> get ns karmada-es-<cluster> -o yaml
```

What to check:

- `spec.syncMode: Push` means `karmada-controller-manager` owns execution for that cluster.
- `spec.syncMode: Pull` means `karmada-agent` in the member cluster owns execution for that cluster.
- Cluster Ready condition can block execution and status reflection, but cite the condition as
  evidence before diagnosing cluster readiness.

## Stage 6: Push Or Pull Execution Owner

Purpose: inspect the correct component for Work dispatch.

Push mode read-only evidence:

```bash
kubectl --context <karmada-context> -n <karmada-system-namespace> logs deploy/karmada-controller-manager --since=<duration> --tail=<lines> | grep -E 'execution-controller|Sync work|Failed to sync work|<work-name>|<cluster-name>'
kubectl --context <karmada-context> -n karmada-es-<cluster> describe work <work-name>
```

Pull mode read-only evidence:

```bash
kubectl --context <member-context> get deploy -A -l app=karmada-agent
kubectl --context <member-context> -n <karmada-agent-namespace> logs deploy/karmada-agent --since=<duration> --tail=<lines> | grep -E 'execution-controller|Sync work|Failed to sync work|<work-name>|<cluster-name>'
kubectl --context <karmada-context> -n karmada-es-<cluster> describe work <work-name>
```

What to check:

- Work `Dispatching` and `Applied` conditions.
- Events with visible reasons `SyncFailed`, `SyncSucceed`, or `WorkDispatching`. `SuspendDispatching`
  is the `Dispatching` condition reason, not the event reason.
- Component logs for the owner selected by sync mode.

Source behavior:

- `cmd/controller-manager/app/controllermanager.go` starts execution and Work status controllers for
  push-mode clusters.
- `cmd/agent/app/agent.go` starts execution and Work status controllers for pull-mode clusters and
  watches only the cluster execution namespace.
- `pkg/controllers/execution/execution_controller.go` gets the cluster name from the Work namespace,
  verifies cluster readiness, observes suspend dispatching, and creates or updates member objects.

## Stage 7: Member Apply

Purpose: prove whether the desired object was applied to the member cluster.

Read-only evidence:

```bash
kubectl --context <member-context> -n <workload-namespace> get <kind> <name> -o yaml
kubectl --context <member-context> -n <workload-namespace> describe <kind> <name>
kubectl --context <member-context> -n <workload-namespace> get events --field-selector involvedObject.name=<name> --sort-by=.lastTimestamp
kubectl --context <karmada-context> -n karmada-es-<cluster> get work <work-name> -o jsonpath='{.status.conditions}{"\n"}'
```

What to check:

- Member object exists, has expected spec, and contains Karmada management annotations.
- Work `Applied` condition records true or false with a reason and message.
- Member-side Kubernetes events explain admission, quota, webhook, image, scheduling, or controller
  issues. Do not infer these causes without events or logs.

First-failure examples:

- Work exists and `Applied=False` while member object is absent: execution/member apply is the first
  failing stage.
- Member object exists but workload pods are unhealthy: this may be application health, not Karmada
  propagation, unless Work health/status reflection is also stale or failed.

## Stage 8: Work Status Reflection

Purpose: prove that status and health moved from the member object back into Work status.

Read-only evidence:

```bash
kubectl --context <karmada-context> -n karmada-es-<cluster> get work <work-name> -o yaml
kubectl --context <karmada-context> -n karmada-es-<cluster> get work <work-name> -o jsonpath='{.status.manifestStatuses}{"\n"}{.status.conditions}{"\n"}'
kubectl --context <karmada-context> -n karmada-es-<cluster> describe work <work-name>
kubectl --context <karmada-context> -n <karmada-system-namespace> logs deploy/karmada-controller-manager --since=<duration> --tail=<lines> | grep -E 'work-status-controller|Reflect status|Interpret health|<work-name>|<workload-name>'
kubectl --context <member-context> get deploy -A -l app=karmada-agent
kubectl --context <member-context> -n <karmada-agent-namespace> logs deploy/karmada-agent --since=<duration> --tail=<lines> | grep -E 'work-status-controller|Reflect status|Interpret health|<work-name>|<workload-name>'
```

Use controller-manager logs for push mode and agent logs for pull mode.

What to check:

- Work is applied before expecting status reflection.
- Member object annotations include Work namespace and Work name.
- `status.manifestStatuses` contains the expected resource identifier, status payload, and health.
- Events or logs mention reflect status or interpret health success/failure.

Source behavior:

- `pkg/controllers/status/work_status_controller.go` registers member informers after Work is
  applied, reflects member object status through the resource interpreter, interprets health when a
  health hook exists, and writes `status.manifestStatuses`.

## Stage 9: Binding And Source Status Aggregation

Purpose: distinguish Work status reflection from binding/source aggregation.

Read-only evidence:

```bash
kubectl --context <karmada-context> -n <workload-namespace> get resourcebinding <binding-name> -o yaml
kubectl --context <karmada-context> get clusterresourcebinding <binding-name> -o yaml
kubectl --context <karmada-context> -n <workload-namespace> get <kind> <name> -o yaml
kubectl --context <karmada-context> -n <karmada-system-namespace> logs deploy/karmada-controller-manager --since=<duration> --tail=<lines> | grep -E 'resource-binding-status-controller|cluster-resource-binding-status-controller|aggregate|workStatues|<binding-name>|<workload-name>'
```

What to check:

- Work `status.manifestStatuses` is newer than binding status or contains data missing from binding.
- Binding status reflects per-cluster status, health, and aggregation from the related Work.
- Source object status was updated from binding status when the resource interpreter supports it.

Source behavior:

- `pkg/controllers/status/rb_status_controller.go` watches ResourceBindings and related Works, then
  aggregates Work status to ResourceBinding and source status.
- `pkg/controllers/status/crb_status_controller.go` does the same for ClusterResourceBinding.

First-failure examples:

- Member object status changed and Work status is current, but ResourceBinding status is stale:
  first failing stage is binding status aggregation.
- Binding status is current but source object status is stale: first failing stage is source status
  update or interpreter support.

## Response Template

When answering an incident, use this shape:

1. **Missing inputs:** List only the inputs needed for the next diagnostic step.
2. **Confirmed facts:** Summarize supplied evidence without inventing missing facts.
3. **Stage table:** One row per stage with status and evidence.
4. **First failing stage:** Name the earliest unsupported, missing, stale, or failed stage.
5. **Likely causes:** Rank by evidence. Mark unproven possibilities as unproven.
6. **Next read-only checks:** Provide scoped commands with placeholders filled when known.
7. **Remediation gate:** If a mutation may be needed, describe the plan and ask for confirmation.

Never end with a destructive command as the default next step.
