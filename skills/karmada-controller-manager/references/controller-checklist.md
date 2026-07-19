# Controller-Manager Operational Checklist

Use this runbook for `karmada-controller-manager` operational diagnosis. It is self-contained for
runtime use: do not require shared knowledge directories, generated source maps, website pages, or
external docs.

Implementation paths below are citation hints. Start from component args, ownership boundaries,
events, health, metrics, and bounded logs. Open source files only when those facts conflict, the user
asks for source-level proof, or a controller enablement rule is not covered here.

## Required Inputs

Ask for missing inputs before diagnosing when they affect the next check:

- Karmada control-plane kube context and namespace where control-plane components run.
- Install method when known: Helm, `karmadactl init`, operator, or custom manifests.
- Affected Cluster name, `spec.syncMode`, and whether the issue is Push or Pull mode.
- Affected controller name or symptom: cluster status, binding, execution, workStatus, failover,
  taint, MCS, HPA, quota, namespace, unifiedAuth, or another controller.
- Affected object identity and namespace when the symptom is object-specific.
- Incident time window, current component args, last known good state, and recent upgrade/change.

If the operator only says "propagation is broken", collect propagation evidence first or route to
`karmada-debug-propagation`. Use this skill once evidence points at a controller-manager process,
controller enablement, Push execution/status, binding generation, cluster status, or failover
boundary.

## Read-Only First

Allowed first:

```bash
kubectl --context <karmada-context> -n <karmada-namespace> get deploy,po,lease -l app=karmada-controller-manager -o wide
kubectl --context <karmada-context> -n <karmada-namespace> describe deploy karmada-controller-manager
kubectl --context <karmada-context> -n <karmada-namespace> get po -l app=karmada-controller-manager -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].args}{"\n"}{end}'
kubectl --context <karmada-context> -n <karmada-namespace> logs deploy/karmada-controller-manager --since=<duration> --tail=<lines>
kubectl --context <karmada-context> -n <karmada-namespace> get events --sort-by=.lastTimestamp
kubectl --context <karmada-context> get cluster <cluster-name> -o yaml
```

Do not initially recommend:

- `rollout restart`, `scale`, pod deletion, or deployment edits.
- Changing `--controllers`, leader election, feature gates, QPS, concurrency, or failover flags.
- Broadening RBAC or member-cluster credentials.
- Patching Cluster status, ResourceBinding status, Work status, finalizers, taints, or Works.

If mutation is justified, separate it into a remediation plan, name blast radius, and ask for explicit
operator confirmation before giving write commands. The response that first identifies the supported
fix must still omit executable write commands. Do not treat "give the next answer", "what should I do
next", or "show the fix" as confirmation; wait for explicit approval of the named mutation, for
example changing `--controllers` on the `karmada-controller-manager` Deployment. If the operator asks
for immediate fix commands before evidence is collected or before approving the specific mutation,
provide the read-only diagnostic bundle and list the possible remediation choices as confirmation
prompts.

## Controller Ownership Map

Controller names are registered in `cmd/controller-manager/app/controllermanager.go`.

| Symptom boundary | Controller-manager owner | Primary evidence |
|---|---|---|
| Component not healthy | process, manager, probes, leader election | Deployment args, Pod readiness, Lease, `/healthz`, logs |
| Controller disabled or not started | `--controllers`, `StartControllers`, disabled-by-default set | args, startup logs: disabled/Starting/Started |
| Cluster object lifecycle and execution namespace | `cluster` | Cluster events; `karmada-es-<cluster>` namespace |
| Push-mode cluster health/API discovery | `clusterStatus` | Cluster Ready and CompleteAPIEnablements conditions; cluster status logs |
| Policy-to-binding and binding-to-Work generation | detector plus `binding` | source claim, ResourceBinding/ClusterResourceBinding, Work in execution namespace |
| Binding/source status aggregation | `bindingStatus` | ResourceBinding/ClusterResourceBinding status, source status, aggregation logs |
| Push-mode Work apply | `execution` | Work conditions/events, member object, execution logs |
| Push-mode Work status reflection | `workStatus` | Work `status.manifestStatuses`, ReflectStatus events, status logs |
| Cluster taints and eviction | `clustertaintpolicy`, `gracefulEviction`, `applicationFailover`, `remedy` | Cluster taints, graceful eviction tasks, failover events/logs |
| Pull-mode Work apply/status | Not controller-manager; `karmada-agent` | Cluster `spec.syncMode: Pull`, agent logs |
| Search API/indexing | Not controller-manager; Search subsystem | Search APIService, karmada-search logs |
| Scheduler selection/ranking | Not controller-manager; scheduler | scheduler logs, binding placement evidence |
| Admission/defaulting rejection | Not controller-manager; webhook/admission | admission error, webhook logs, ValidatingWebhookConfiguration |

## Process And Runtime Checks

Use this order before blaming a controller implementation:

1. Component Pod is Ready and not restarting.
2. Args match expectation: `--controllers`, feature gates, QPS/burst, concurrency, cluster monitor
   periods, health/metrics bind addresses.
3. Leader election has a current holder and the holder matches a running Pod when HA is enabled.
4. Health probe and metrics endpoint are reachable from an appropriate network location.
5. Logs show the process version, manager startup, controller startup, cache sync, and no fatal setup
   errors.
6. Events or metrics show the relevant controller is reconciling or failing.

Useful read-only commands:

```bash
kubectl --context <karmada-context> -n <karmada-namespace> get lease karmada-controller-manager -o yaml
kubectl --context <karmada-context> -n <karmada-namespace> describe po -l app=karmada-controller-manager
kubectl --context <karmada-context> -n <karmada-namespace> logs deploy/karmada-controller-manager --since=<duration> --tail=<lines> | grep -E 'Starting|Started|disabled|Skipping|Error starting|leader|cache|<controller-name>|<object-name>'
kubectl --context <karmada-context> -n <karmada-namespace> port-forward deploy/karmada-controller-manager 10357:10357
curl -fsS http://127.0.0.1:10357/healthz
```

Do not treat a standby replica with no reconciles as failure until leader election evidence shows it
should be active.

## Controller Enablement

The `--controllers` flag controls which controllers run:

- `*` enables all on-by-default controllers.
- `name` explicitly enables a controller.
- `-name` disables a controller.
- If `*` is omitted, only explicitly named controllers run.
- In `karmada-controller-manager`, `hpaScaleTargetMarker` and `deploymentReplicasSyncer` are
  disabled by default unless explicitly enabled.

Code paths:

- `cmd/controller-manager/app/options/options.go`: flag definition and defaults.
- `pkg/controllers/context/context.go`: enablement logic and startup log messages.
- `cmd/controller-manager/app/controllermanager.go`: registered controller names and disabled set.

First-failure examples:

- Args contain `--controllers=cluster,clusterStatus` and binding is not running: controller-manager
  process is healthy, but `binding` is disabled by configuration.
- Logs say `"binding" is disabled`: do not diagnose member API, scheduler, or Work execution first.
- Logs say `Error starting "workStatus"`: collect setup error, RBAC, informer, RESTMapper, and
  client evidence for that controller.

## Permissions And Admission Boundaries

Forbidden errors in controller-manager logs are evidence, not permission to broaden RBAC immediately.
Use read-only checks first:

```bash
kubectl --context <karmada-context> -n <karmada-namespace> logs deploy/karmada-controller-manager --since=<duration> --tail=<lines> | grep -E 'forbidden|RBAC|cannot|get|list|watch|update|patch|<resource>'
kubectl --context <karmada-context> auth can-i <verb> <resource> --as=system:serviceaccount:<karmada-namespace>:<serviceaccount>
kubectl --context <karmada-context> get clusterrole,clusterrolebinding,role,rolebinding | grep karmada-controller-manager
```

If an object is rejected before reconciliation, treat it as admission/webhook territory rather than
controller-manager. Collect the admission error and webhook logs before investigating controller
queues.

## Push Versus Pull Boundary

Do not assume `karmada-controller-manager` owns every Work.

- Push cluster: `karmada-controller-manager` handles `execution` and `workStatus`.
- Pull cluster: `karmada-agent` handles `execution` and `workStatus`; controller-manager should not
  be treated as the owner for Work apply/status.

Read-only commands:

```bash
kubectl --context <karmada-context> get cluster <cluster-name> -o jsonpath='{.spec.syncMode}{"\n"}{.status.conditions}{"\n"}'
kubectl --context <karmada-context> -n karmada-es-<cluster-name> get work -o wide
kubectl --context <karmada-context> -n karmada-es-<cluster-name> describe work <work-name>
```

Checkout-only implementation paths (do not cite or paraphrase as current behavior in package-only mode):

- `cmd/controller-manager/app/controllermanager.go`: `execution` and `workStatus` use
  `WorkWithinPushClusterPredicate`.
- `pkg/util/helper/predicate.go`: filters Work events to Push clusters for controller-manager.
- `cmd/agent/app/agent.go`: agent owns pull-mode execution/status.

## Cluster Status And Failover Boundary

Cluster Ready, API enablement, failover, and taint symptoms may involve controller-manager but are
not automatically controller-manager bugs. Separate these causes:

- Cluster credential or SecretRef failure.
- Member API unavailable, slow, or partially discoverable.
- Pull cluster heartbeat/lease behavior.
- Controller flags: monitor period, grace period, success/failure thresholds, cache sync timeout.
- Taint/failover configuration and controller enablement.
- Scheduler or policy behavior after the cluster condition changes.

Read-only commands:

```bash
kubectl --context <karmada-context> get cluster <cluster-name> -o yaml
kubectl --context <karmada-context> get events --field-selector involvedObject.kind=Cluster,involvedObject.name=<cluster-name> --sort-by=.lastTimestamp
kubectl --context <karmada-context> -n <karmada-namespace> logs deploy/karmada-controller-manager --since=<duration> --tail=<lines> | grep -E 'clusterStatus|cluster-controller|taint|failover|graceful|<cluster-name>'
kubectl --context <karmada-context> -n karmada-es-<cluster-name> get work -o wide
```

Cluster status source paths:

- `cmd/controller-manager/app/controllermanager.go`: starts `cluster` and `clusterStatus`.
- `pkg/controllers/status/cluster_status_controller.go`: updates Cluster Ready, API enablement, and
  initializes informer managers for healthy clusters.
- `cmd/controller-manager/app/options/options.go`: cluster monitor and threshold flags.

Failover and taint source paths:

- `pkg/controllers/taint`
- `pkg/controllers/gracefuleviction`
- `pkg/controllers/applicationfailover`
- `pkg/controllers/remediation`

## Binding, Work Generation, And Status Aggregation

Use `karmada-debug-propagation` for the full propagation pipeline. Stay in this skill when the
operator has already isolated a controller-manager boundary such as a disabled controller, setup
error, stale controller logs, or Push-mode ownership.

Read-only checks:

```bash
kubectl --context <karmada-context> -n <workload-namespace> get resourcebinding <binding-name> -o yaml
kubectl --context <karmada-context> get clusterresourcebinding <binding-name> -o yaml
kubectl --context <karmada-context> -n karmada-es-<cluster-name> get work -o yaml
kubectl --context <karmada-context> -n <karmada-namespace> logs deploy/karmada-controller-manager --since=<duration> --tail=<lines> | grep -E 'binding|bindingStatus|execution|workStatus|<binding-name>|<work-name>'
```

Interpretation:

- Scheduled binding with no Work: first controller-manager boundary is `binding`/Work generation.
- Work exists and cluster is Push: execution and Work status are controller-manager boundaries.
- Work exists and cluster is Pull: execution and Work status are `karmada-agent` boundaries.
- Work `status.manifestStatuses` is current but ResourceBinding/source status is stale:
  `bindingStatus` aggregation is the controller-manager boundary.

Relevant source paths:

- `pkg/controllers/binding/binding_controller.go`
- `pkg/controllers/binding/cluster_resource_binding_controller.go`
- `pkg/controllers/binding/common.go`
- `pkg/controllers/execution/execution_controller.go`
- `pkg/controllers/status/work_status_controller.go`
- `pkg/controllers/status/rb_status_controller.go`
- `pkg/controllers/status/crb_status_controller.go`

## Response Shape

Return concise sections:

- Confirmed facts
- Missing inputs
- Controller ownership map
- First failing or unknown boundary
- Read-only commands to run next
- Likely causes ranked by evidence
- Remediation plan requiring explicit confirmation before mutation
