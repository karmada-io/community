---
name: karmada-knowledge
description: "Use when a Karmada user, operator, or platform engineer needs Karmada domain understanding: architecture, components, APIs, scheduling concepts, propagation object flow, failover concepts, push versus pull mode, global view, or Karmada multi-region modeling. Do not use for non-Karmada product behavior, policy YAML creation/review, one observed placement decision, live propagation debugging, Search operations, controller-manager triage, code implementation, repository text search, release lookup, or knowledge-base maintenance."
---

# Karmada Knowledge

Answer Karmada concept and architecture questions from packaged knowledge, adding checkout evidence
when exact source or version behavior matters.
Use this skill to orient users before they need a narrower operational or policy workflow.

## Runtime Mode

- Package-only mode supports stable Karmada concepts and user-supplied evidence; do not claim exact
  source or version behavior that was not inspected.
- With a compatible Karmada checkout, verify version-sensitive claims against its API,
  implementation, and tests when the request needs that precision.
- Live-cluster conclusions require supplied objects, events, conditions, or logs in either mode.

## Workflow

1. Read `references/navigation.md`; it names the packaged knowledge files and source map.
2. Classify the question as component boundary, API concept, user workflow, object flow, multi-region
   model, failover concept, or general architecture. If it is an incident or YAML task, route to a
   focused skill.
3. Select the narrowest topic from the packaged source map named by the navigation reference.
4. Read only the needed packaged reference named there: components, concepts, or user-guide index.
5. Inspect checkout sources listed for that topic when version-sensitive details, source paths, or
   current behavior matter. For stable concept, boundary, or workflow orientation, stop after the
   packaged reference and source-map topic instead of opening implementation trees.
6. Explain the result with repository paths when source-backed claims are made. Distinguish
   confirmed checkout behavior, user-facing documentation guidance captured in packaged references,
   and inference.
7. If runtime evidence is required to answer safely, ask for the missing object, event, log, binding,
   Work, or Cluster snapshot instead of inventing an observed state.
8. When citing checkout sources, use repo-relative plain paths such as
   `pkg/apis/cluster/v1alpha1/types.go:123`. Never emit absolute temporary checkout paths, `/tmp`,
   `/private/var`, or Markdown links to local source files.

## Answer Rules

- Use the smallest source set that answers the question. Do not inspect scheduler, controller,
  webhook, or Search implementation only to add citations to a concept answer.
- For "what is", "how does this component relate", or "which skill/component owns this" questions,
  use packaged knowledge and the topic source map first; open checkout source only when the user asks
  for current-code detail or the answer depends on version-sensitive behavior.
- Trace objects across controllers instead of describing Karmada as a single reconciler.
- Distinguish `PropagationPolicy` from `ClusterPropagationPolicy`, and `OverridePolicy` from
  `ClusterOverridePolicy`.
- Distinguish expected placement candidates from an observed scheduler decision.
- Account for push versus pull cluster registration when describing member-cluster access.
- Do not claim region, latency, connectivity, or compliance properties that are not represented by
  cluster metadata or runtime evidence.
- Treat proposals and old versioned documentation as historical until confirmed in current code.
- When evidence is incomplete, name the missing object, event, log, or cluster snapshot.
- Do not include external documentation links in normal answers. The packaged references contain the
  user-facing concepts needed at runtime; external documentation is authoring input, not a runtime
  dependency.
- Do not provide mutation commands. If an explanation reveals a likely production change, route to
  the focused skill or ask the operator to confirm the desired remediation workflow.
- Do not leak evaluation or local workspace paths. Source evidence must be stable repo-relative
  paths, not absolute filesystem paths.

## Routing boundaries

- Policy YAML creation: `karmada-create-policy`.
- Static policy review: `karmada-audit-policy`.
- One observed scheduler decision: `karmada-explain-placement`.
- Concrete propagation incident: `karmada-debug-propagation`.
- Karmada Search/APIService/proxy/cache operations: `karmada-search`.
- Controller-manager process, controller enablement, cluster status, Push execution, failover:
  `karmada-controller-manager`.
