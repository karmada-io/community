# Policy creation and audit knowledge

Use this reference for `PropagationPolicy`, `ClusterPropagationPolicy`, `OverridePolicy`, and
`ClusterOverridePolicy`. It summarizes workflow guardrails; the current checkout remains the source
of truth.

## Choose scope before fields

- `PropagationPolicy` and `OverridePolicy` are namespaced. The namespace field on each provided
  resource selector defaults to the policy namespace and must not select another namespace.
- `ClusterPropagationPolicy` and `ClusterOverridePolicy` are cluster-scoped. Put an explicit
  namespace in a selector when the intent is namespace-specific.
- Do not choose a cluster-scoped policy merely to avoid asking for the workload namespace.

## Create a propagation policy

1. Identify the workload by `apiVersion`, `kind`, namespace, and either name or labels.
2. Choose namespaced or cluster scope from the intended ownership boundary.
3. Translate cluster intent into explicit cluster fields, labels, names, exclusions, tolerations, and
   spread constraints. Do not infer topology from a cluster name.
4. Decide whether replicas are duplicated or divided. Do not invent a division strategy when the
   user did not provide one.
5. Add dependency propagation, failover, priority, preemption, conflict resolution, or scheduler
   selection only when requested or required by a stated scenario.
6. Explain assumptions next to the generated YAML. Never apply it implicitly.

A propagation policy's `resourceSelectors` must contain at least one item. An item that specifies
only API version and kind can intentionally select every resource of that kind in its effective
namespace; audit that breadth rather than treating an empty propagation selector list as match-all.

`clusterAffinity` describes eligible candidates, not proof that every named or matching cluster will
be selected. Actual scheduling also depends on placement rules and runtime cluster state.

## Create an override policy

1. Identify the selected resource and policy scope.
2. Identify target clusters independently from the resource selector.
3. Choose the narrowest overrider type that expresses the requested change.
4. Preserve JSON pointer syntax and operator semantics for plaintext and structured patches.
5. Do not combine propagation and override objects unless the request needs both.

An override policy permits an omitted or empty `resourceSelectors` list, which means matching all
resources in its scope. Generate that only when the user explicitly requests such breadth, and audit
it as a high-impact choice.

Override validation cannot prove that a path exists in every selected workload. Audit both policy
schema and the concrete resource shape when available.

## Validation authorities

- API shape and defaults: `pkg/apis/policy/v1alpha1` and generated CRDs.
- Admission semantics:
  `pkg/webhook/{propagationpolicy,clusterpropagationpolicy,overridepolicy,clusteroverridepolicy}`.
- Shared semantic checks: `pkg/util/validation/validation.go` and its tests.
- Real API acceptance: optional server-side dry-run against the intended Karmada control plane.

A server-side dry-run is stronger than offline prose review but still does not prove that clusters
will be selected or that the workload will run successfully.
