---
name: karmada-explain-placement
description: Use this skill when a Karmada user, operator, or platform engineer asks why a concrete ResourceBinding or ClusterResourceBinding selected, rejected, ordered, or assigned replicas to specific member clusters. Use it for observed placement outcomes from full or partial evidence, including prose descriptions when binding YAML or runtime logs are unavailable; in partial cases bound conclusions and request the missing objects. Do not use it for policy creation, static YAML audit, general scheduling concepts, post-scheduling Work/member failures, live mutations, or knowledge maintenance.
---

# Explain Karmada Placement

Explain an observed scheduler decision from supplied runtime evidence and current-checkout sources.
This is a read-only diagnostic workflow for placement outcomes, not a remediation workflow.

## Runtime Mode

- Package-only mode supports bounded interpretation of supplied policy, binding, Cluster, event,
  log, and estimator evidence.
- With a compatible Karmada checkout, verify exact scheduler semantics against its API,
  implementation, and tests when the causal explanation requires them.
- Do not claim exact source behavior or a concrete placement cause when its required evidence is absent.

## Workflow

1. Read `references/placement-debugging.md` and `references/evidence.md`.
2. Identify the exact object under explanation: `ResourceBinding` or `ClusterResourceBinding`,
   namespace/name, UID, generation, referenced workload, applied policy placement annotation or
   policy generation, scheduler name if present, conditions, events, and `status.lastScheduledTime`.
   Selected target names and per-target replica counts belong to `spec.clusters[]`, not `status`.
   When the user supplies only a prose description, call it a supplied binding fact and do not
   invent a `spec` or `status` field path.
3. Separate deterministic policy interpretation from runtime state:
   - Deterministic: placement fields, selectors, explicit cluster names, excluded clusters,
     `clusterAffinities` order, toleration rules, spread declarations, and replica scheduling API
     semantics.
   - Runtime-dependent: the scheduler cache snapshot, deleting clusters, enabled plugin registry,
     plugin ordering, API enablement, taints at schedule time, graceful eviction tasks, score results,
     assigning cache, estimator responses, logs, and events.
4. Establish the Cluster snapshot used for the explanation. Use supplied historical objects, events,
   logs, or saved command output when available. If only current Cluster objects are supplied, label
   conclusions as current-state checks and ask for historical evidence before claiming what the
   scheduler saw earlier.
5. Reconstruct the scheduler pipeline in evidence order:
   - binding reschedule trigger and placement annotation comparison;
   - candidate filtering against deletion state and enabled filter plugins;
   - scoring and spread selection;
   - replica assignment strategy and estimator or capacity inputs;
   - patch/event/status result recorded on the binding.
6. For each cluster, classify it as observed selected, observed rejected, eligible under supplied
   policy facts, ineligible under supplied facts, or unresolved. Do not infer country, region, zone,
   provider, latency, readiness, capacity, or API support from the cluster name.
7. Explain replica assignment only when the evidence includes workload replicas, the binding's
   previous `spec.clusters` when relevant, replica scheduling strategy, candidate clusters,
   allocatable replicas or estimator responses, and observed target replica counts. Otherwise report
   the observed counts and list the missing inputs.
8. Cite API shape, scheduler implementation, and focused tests from the current checkout. Mark any
   reconstruction from logs/events as inference, and never treat policy eligibility alone as proof of
   a historical scheduler choice.
9. Return a concise operator answer with:
   - observed outcome;
   - deterministic policy interpretation;
   - runtime scheduler evidence;
   - selected and rejected cluster table;
   - replica reasoning;
   - missing evidence or next read-only checks;
   - sources consulted.
   When evidence is stale or from a different generation, explicitly request the matching binding
   UID and generation, policy generation, historical Cluster snapshots, scheduler events, scores,
   logs, and scheduling timestamps. Do not collapse this list to generic "matching evidence."
10. When listing sources, use repo-relative plain paths such as
    `pkg/scheduler/core/assignment.go:88`. Never emit absolute temporary checkout paths, `/tmp`,
    `/private/var`, or Markdown links to local source files.

## Source-read gate

- Start with supplied runtime evidence: policy, binding, Cluster snapshot, events, logs, estimator
  output, and workload replicas. Do not read scheduler implementation to compensate for missing
  runtime evidence.
- Use packaged evidence rules for deterministic placement interpretation. Open scheduler source only
  after the supplied evidence identifies the relevant boundary, such as affinity filtering, taint
  filtering, spread selection, estimator-based assignment, or status patching.
- If the binding, historical Cluster snapshot, scheduler events/logs, or estimator data is missing,
  stop with a partial explanation and ask for the exact read-only evidence needed.
- For prose-only evidence, end with an explicit request for the actual binding and policy YAML,
  historical Cluster snapshot, and matching-cycle events, logs, scores, or estimator output needed
  to close the causal gap. Listing those categories as unknowns alone is not sufficient.

## Guardrails

- `ResourceBinding` and `ClusterResourceBinding` target assignments are stored in
  `spec.clusters[]`. Their `status` contains scheduler observation metadata, conditions, and
  aggregated workload status, not the selected target list. Never report target names or target
  replica counts as fields under `status`.
- A current Cluster list may not represent the snapshot used by an earlier scheduling cycle.
- The scheduler does not universally pre-filter all non-Ready clusters. Readiness matters only when
  it appears in supplied evidence or in the specific scheduler/plugin path being cited.
- Do not infer country, region, zone, provider, latency, or capacity from cluster names.
- Do not claim a filter plugin ran merely because its implementation exists.
- When plugin execution evidence is absent, do not say that any named scheduler stage or plugin
  `ran`, `contributed`, `considered`, `rejected`, or `scored` the observed targets. List it only as a
  possible boundary to investigate, not as part of the historical decision.
- Do not convert policy eligibility into proof that a cluster was selected.
- Describe a cluster present in the binding only as `observed selected`. Without matching-cycle
  scores and logs, do not call it a winner or say another cluster lost or was rejected.
- Do not reverse-engineer missing dynamic weights, estimator capacity, or spread results from the
  final binding alone.
- Never trigger a reschedule or mutate policy, binding, or Cluster objects implicitly.
- Do not apply, patch, delete, restart, remove finalizers, edit status, or scale workloads. If the
  user asks for a risky production-impacting change, first provide a read-only explanation and ask
  for explicit confirmation before any separate remediation workflow.
- Do not leak evaluation or local workspace paths. Source evidence must be stable repo-relative
  paths, not absolute filesystem paths.

## Routing boundaries

Use `karmada-create-policy` for desired placement YAML, `karmada-audit-policy` for static policy
review, `karmada-knowledge` for general scheduler concepts, and `karmada-debug-propagation` when the
binding is scheduled but Work or member resources are missing or unhealthy.
