---
name: karmada-debug-propagation
description: Use when a Karmada user, operator, or platform engineer has a concrete propagation incident where a known workload, ResourceBinding or ClusterResourceBinding, Work, member object, or status update failed, is missing, or is stale across member clusters. Do not use for policy creation, static YAML review, explaining cluster or replica placement choices, Search incidents, controller-manager restart/flag/role/ownership questions before controller-manager is ruled in or out, general architecture, website lookup, or knowledge maintenance.
---

# Debug Karmada Propagation

Find the first unsupported or failing stage in a real propagation incident before proposing any
production mutation.

## Runtime Mode

- Package-only mode supports stage diagnosis from bundled object-flow knowledge and supplied
  objects, events, conditions, and logs; do not invent repository paths.
- With a compatible Karmada checkout, verify exact object flow and ownership against its API,
  controllers, commands, and tests when needed.
- Do not identify a live failing stage without the runtime evidence required for that stage.

## Workflow

1. Read `references/triage.md`. It is the runtime runbook; do not require shared knowledge
   directories, generated source maps, website pages, or external documentation.
2. Confirm this is a concrete incident. If the request is missing material inputs, ask for the
   minimum needed before diagnosing: workload apiVersion/kind/name/namespace, Karmada control-plane
   context, target member cluster, member context when member evidence is needed, push or pull
   registration mode if known, relevant policy or binding name if known, incident time, and last
   known good state.
3. Start read-only. Use `get`, `describe`, `events`, JSONPath, and bounded logs. Before explicit
   operator confirmation, remediation must be prose only: do not output any write-command syntax,
   code block, or one-liner that would mutate source workloads, member objects, policies, bindings,
   Works, controller state, or cluster state. This includes any `kubectl` command whose verb is
   `apply`, `patch`, `delete`, `create`, `replace`, `edit`, `scale`, `set`, `label`, `annotate`, or
   `rollout`, even when the user asks for a fast command or the evidence points to a clear fix.
4. Walk the pipeline in order:
   - source object and policy claim/detector selection
   - ResourceBinding or ClusterResourceBinding
   - scheduling result in `spec.clusters`
   - Work generation in the target execution namespace
   - push versus pull execution owner
   - member-cluster apply result
   - Work status reflection
   - binding and source status aggregation
5. Stop at the first stage whose required evidence is missing, stale, or failed. Do not diagnose
   later stages as root cause until earlier stages are supported.
6. For each stage, state `supported`, `missing`, `stale`, `failed`, or `unknown`, with the exact
   object, condition, event, or log line needed to move forward.
7. Return: confirmed facts, missing inputs, first failing stage, likely causes ranked by evidence,
   next read-only commands, and a separate remediation section. If mutation is appropriate, present
   a narrow mutation plan and ask for confirmation before giving write commands.

## Guardrails

- Do not skip directly from policy presence to member-cluster diagnosis.
- Missing Work and unhealthy Work are different failures.
- A scheduled binding without a Work is a binding-controller or Work-generation problem until proven
  otherwise, not an execution-controller, agent, member API, or network problem.
- Account for push versus pull registration before naming the responsible execution process. Push
  execution is owned by `karmada-controller-manager`; pull execution is owned by `karmada-agent`.
- Do not recommend deleting bindings, Works, orphan Works, or finalizers as an initial diagnostic
  step. Cleanup actions require read-only ownership evidence and explicit operator approval.
- Do not claim network, RBAC, webhook, interpreter, scheduler, or member API failure without evidence
  from that boundary.
- Prefer commands that scope by namespace, name, cluster, and time window. Avoid broad log scraping
  when a narrower selector is available.

## Routing boundaries

Use another skill when the primary request is not a concrete propagation incident:

- `karmada-create-policy`: create a new PropagationPolicy or ClusterPropagationPolicy.
- `karmada-audit-policy`: review supplied policy YAML without a live incident.
- `karmada-explain-placement`: explain why a scheduler chose clusters or replica weights.
- `karmada-search`: troubleshoot Karmada Search API indexing or query results.
- `karmada-controller-manager`: answer whether controller-manager owns a symptom, should be
  restarted, or is ruled out by push/pull mode, flags, leader, or controller enablement evidence.
- `karmada-knowledge`: general object-flow or architecture explanation.
