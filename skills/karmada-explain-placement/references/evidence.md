# Placement evidence and explanation checklist

This reference is intentionally self-contained for packaged skill runtime. Use the current checkout
as the source of truth when paths exist, and treat website material only as authoring context.

## Evidence to collect

Collect evidence in this order, stopping to ask for missing inputs when a conclusion would otherwise
depend on guessing:

1. Workload GVK, namespace, name, UID, replicas, and resource requests.
2. PropagationPolicy or ClusterPropagationPolicy name, scope, generation, priority, and placement.
3. ResourceBinding or ClusterResourceBinding UID, generation, resource reference, placement
   annotation, `spec.placement`, previous and current `spec.clusters`, `spec.rescheduleTriggeredAt`,
   `status.schedulerObservedGeneration`, `status.schedulerObservedAffinityName`,
   `status.lastScheduledTime`, conditions, and events.
4. Cluster objects from the relevant scheduling interval, including deletion timestamp, labels,
   `spec.provider`, `spec.region`, `spec.zones`, taints, API enablement, resource models, and status
   conditions.
5. Scheduler runtime evidence: enabled in-tree or custom plugins, feature gates, scheduler logs,
   events tied to the binding UID/generation, and any saved scheduler cache snapshot.
6. Estimator inputs and outputs when dynamic available capacity, aggregated division, or
   multi-template scheduling affects replicas: workload resource requests, replica requirements,
   assumed workloads, estimator name, and per-cluster available replicas or component sets.
7. Focused tests or deterministic fixtures that match the observed behavior. Fixtures are regression
   evidence, not a substitute for live objects, events, or logs.

Classify every conclusion as observed, derived from supplied objects, supported by checkout
implementation, or unresolved because historical runtime evidence is absent.

When only final `spec.clusters` is supplied, do not narrate the generic scheduler pipeline as what
happened. In particular, do not say named filters, scoring, spread, affinity, API enablement, or
taint handling ran or contributed. They are only candidate investigation boundaries until events,
logs, configuration, source evidence, or a reproducible trace connects them to this decision.

## Stop conditions

Stop and ask for missing evidence instead of opening broader source files when:

- no `ResourceBinding` or `ClusterResourceBinding` is supplied for an observed decision;
- the answer depends on historical Cluster labels, fields, taints, deletion state, API enablement, or
  readiness that were not captured for the scheduling interval;
- the answer depends on scheduler plugin configuration, score output, event messages, or logs that
  are not supplied;
- replica reasoning depends on estimator or allocatable replica data that is absent;
- the question has moved from placement to Work generation, execution, member apply, or status
  reflection.

## Deterministic policy interpretation

These facts can be derived from supplied policy/binding YAML without a live scheduler snapshot:

- `placement.clusterAffinity` and each `clusterAffinities[*]` term define cluster candidate rules.
  `clusterAffinity` and `clusterAffinities` are alternatives; when neither is set, policy affinity
  alone does not narrow candidates.
- Cluster affinity is conjunctive across label selector, field selector, explicit cluster names, and
  exclusions. Field selectors use Cluster fields such as provider, region, and zones; label
  selectors use Cluster metadata labels.
- `clusterAffinities` are evaluated in order. The observed
  `status.schedulerObservedAffinityName` identifies the group the scheduler was observing; overflow
  affinities apply only to workload resources that need compute capacity.
- `clusterTolerations` describe which NoSchedule or NoExecute Cluster taints a new target can
  tolerate. A current taint list is not proof that the same taints existed at schedule time.
- `spreadConstraints` declare grouping requirements. Defaulting and validation are API/admission
  facts, but the selected groups depend on the candidates and runtime scheduler data.
- `replicaScheduling` API semantics are deterministic: `Duplicated` applies the original replica
  count to each selected target; `Divided` splits replicas according to `Aggregated` or `Weighted`.
  Dynamic weighted placement needs runtime available-replica evidence.

## Runtime scheduler state

Explain these as runtime-dependent unless the user supplies the exact evidence:

- The scheduler snapshots clusters from its cache, skips deleting clusters, runs filter plugins,
  scores feasible clusters, selects clusters under spread constraints, then assigns replicas.
- The in-tree registry includes API enablement, taint/toleration, cluster affinity, spread
  constraint, cluster locality, and cluster eviction plugins; workload affinity plugins depend on
  the corresponding feature gate. Custom builds or configuration may differ.
- `ClusterAffinity` filtering uses the binding placement plus the observed affinity term and its
  applicable overflow terms.
- `TaintToleration` checks NoSchedule and NoExecute taints for new targets, but allows clusters
  already in the binding target list so taint-driven eviction can handle graceful removal.
- `APIEnablement` checks whether a new target supports the workload GVK, but allows existing targets
  so the scheduler does not delete scheduled resources only because API discovery changed.
- `SpreadConstraint` filtering rejects missing provider, region, or zones fields for the matching
  spread field before later spread selection chooses groups.
- `ClusterEviction` rejects clusters listed in graceful eviction tasks.
- Scores and final cluster order require scheduler logs or reproduced source-level evidence. Do not
  claim tie-breaking or score reasons from the final binding alone.

## Replica assignment boundaries

Use this decision table:

| Evidence present | Safe explanation |
| --- | --- |
| Observed `spec.clusters` only | Report the recorded target clusters and replica counts. Do not explain the arithmetic. |
| Workload replicas plus `Duplicated` | State that each selected cluster receives the original replica count, then compare to observed counts. |
| Workload replicas plus static weighted `Divided` | Explain weights only for clusters matched by supplied static weight rules; ask for previous assignment if scale-up/down steadiness matters. |
| Dynamic `AvailableReplicas` or `Aggregated` | Require estimator or allocatable replica evidence, resource requests, and previous assignment. Without them, state what is missing. |
| Manual reschedule trigger | Note that fresh assignment may ignore previous distribution; require `spec.rescheduleTriggeredAt` and `status.lastScheduledTime`. |

## Answer shape

Prefer this compact structure:

```text
Observed outcome
- Binding <namespace/name or name> records <clusters and replicas>.

Deterministic policy interpretation
- What the placement rules mean from the supplied YAML.

Runtime scheduler evidence
- Which supplied events/status/logs/Cluster objects support or fail to support the outcome.

Cluster-by-cluster
| Cluster | Classification | Evidence | Unknowns |

Replica reasoning
- Explain only what the available inputs prove.

Missing evidence / next read-only checks
- Ask for exact objects, events, logs, or estimator responses needed to close gaps.

Sources
- Cite current-checkout paths such as pkg/apis/policy/v1alpha1/propagation_types.go,
  pkg/scheduler/scheduler.go, pkg/scheduler/core/generic_scheduler.go,
  pkg/scheduler/core/assignment.go, pkg/scheduler/core/division_algorithm.go,
  pkg/scheduler/framework/plugins/*, pkg/apis/cluster/v1alpha1/types.go, and focused tests.
- Use repo-relative plain paths only. Do not write Markdown links or absolute temporary checkout
  paths such as `/tmp` or `/private/var`.
```

## Safe read-only commands

When the user wants next checks, suggest read-only collection only. Examples should be adapted to
the actual namespace and object names:

```bash
kubectl get resourcebinding -n <namespace> <name> -o yaml
kubectl get clusterresourcebinding <name> -o yaml
kubectl get propagationpolicy -n <namespace> <name> -o yaml
kubectl get clusterpropagationpolicy <name> -o yaml
kubectl get clusters -o yaml
kubectl get events -A --field-selector involvedObject.name=<binding-name>
kubectl logs -n karmada-system deploy/karmada-scheduler --since=<duration>
```

Do not suggest `apply`, `patch`, `delete`, restarts, finalizer removal, or status edits as part of
placement explanation.
