---
name: karmada-create-policy
description: Use when a Karmada user or platform engineer asks to create PropagationPolicy, ClusterPropagationPolicy, OverridePolicy, or ClusterOverridePolicy YAML, or requests explicit field or value changes to those policy objects. Do not use when the primary task is reviewing or auditing supplied policy YAML for problems.
---

# Create Karmada Policy

Create narrowly scoped Karmada policy YAML. Ask only when missing facts change scope, placement, or
production impact.

## Runtime Mode

- Package-only mode supports policy drafting from bundled workflows and supplied manifests. Label
  exact-version assumptions that cannot be verified; do not invent repository paths. Return the
  artifact and offline review guidance only. Do not provide `kubectl apply`, including
  `--dry-run=server`, unless the user separately asks to validate against a live API server.
- With a compatible Karmada checkout, verify version-sensitive or advanced fields against its API,
  validation, and tests when needed.
- Generated YAML is an artifact, not evidence that admission, placement, or propagation succeeded.

## Input Contract

| Intent | Object |
|---|---|
| Propagate a namespaced workload | `PropagationPolicy` |
| Propagate a cluster-scoped resource or use cluster-wide/cross-namespace policy ownership | `ClusterPropagationPolicy` |
| Customize selected resources in one namespace | `OverridePolicy` |
| Customize a cluster-scoped resource or use cluster-wide/cross-namespace override ownership | `ClusterOverridePolicy` |

Before generating ready-to-validate YAML, ask when any of these are missing and affect the result:

- namespace or namespaced versus cluster scope
- workload `apiVersion`, `kind`, and name or labels
- target cluster names, labels, or fields

When one of these required values is missing, keep the first response to prose questions and a
plain-text summary of facts already known. Do not emit YAML, JSON, fenced manifest fragments, or a
partial workload selector while waiting for the answer, even if some fields are already known.

Failover and dependency propagation have a safe omission default. Do not ask about them solely to
decide whether to enable them; omit them unless the request explicitly requires them.

Use explicit placeholders only for a clearly labeled draft. Do not present placeholder YAML as ready
to apply.

## Workflow

1. Read `references/policy-workflows.md`.
2. Read `references/examples.md` only for the requested object family.
3. Summarize workload identity, policy scope, placement, replica behavior, overrides, optional
   behavior, and unknown runtime checks.
4. Ask the minimum questions required by the input contract.
5. Generate only the requested objects. Keep propagation and override policies separate unless both
   are requested.
   For namespaced `PropagationPolicy` or `OverridePolicy` selecting a namespaced resource, include
   `resourceSelectors[].namespace` explicitly even when it equals `metadata.namespace`.
6. Validate fields against packaged policy guidance and, when checkout-specific proof is required,
   current API types and propagation or override admission. Do not present suite regression fixtures
   as validation of generated YAML.
7. Return YAML, effective scope, assumptions, omitted optional behavior, and validation appropriate
   to the runtime mode. In package-only mode, state that admission is unverified and do not include
   a live API command by default.

## Source-read gate

- Common propagation and override templates should be produced from `policy-workflows.md` and the
  relevant example family. Do not open API, webhook, scheduler, or controller source for ordinary
  cluster-name, label-selector, namespace, or annotation override requests.
- Open current checkout source only when the request uses an advanced or ambiguous field, asks for
  current-code proof, conflicts with packaged guidance, or needs exact admission behavior not already
  captured in the packaged references.
- If runtime state is the unknown, stop and list it as a runtime check. Do not inspect implementation
  code to infer cluster existence, labels, readiness, capacity, feature gates, or final scheduling.

## Safety

- Generate YAML and mode-appropriate validation guidance only. Never apply resources or imply
  permission to mutate infrastructure. A server-side dry run still contacts a live API server and
  must not be offered in package-only mode unless the user explicitly requests live validation.
- If clarification is required before a safe policy can be generated, do not output any manifest
  fragment. A partial selector or placeholder object is still an artifact and can be mistaken for
  ready-to-use configuration.
- Never say that admission succeeds, a field is defaulted, or a runtime result will occur when no
  compatible checkout or live admission response establishes it.
- Never broaden selectors to avoid a question or invent topology, labels, capacity, readiness,
  feature gates, or cluster names.
- Prefer explicit namespace in generated resource selectors for namespaced policies. Relying on
  namespace defaulting is API-compatible, but generated production YAML should make selector scope
  visible to reviewers.
- Do not infer region, country, provider, latency, or compliance from cluster names.
- Do not enable failover, dependency propagation, preemption, conflict overwrite, a custom
  scheduler, or feature-gated behavior without explicit intent.
- Propagation policies require at least one resource selector.
- Override policies permit omitted or empty resource selectors, but that matches all resources in
  scope. Warn about the blast radius and generate it only when explicitly requested.
- Treat cluster existence, labels, readiness, capacity, and feature-gate state as runtime checks.
- For divided replica scheduling, explicitly separate API compatibility, admission, observed
  capacity inputs, and the scheduler's final replica assignment. Source compatibility does not
  predict the final per-cluster replica counts.

## Output Contract

1. YAML, or clarification questions when required inputs are missing
2. Effective namespace and selector scope
3. Assumptions and missing runtime checks
4. Omitted optional behavior
5. Offline review limits in package-only mode; server-side dry-run commands only when live
   validation was explicitly requested

## Routing

Use `karmada-audit-policy` for supplied-policy review, `karmada-explain-placement` for an observed
`ResourceBinding` or scheduling result, and `karmada-debug-propagation` for runtime propagation
incidents.
