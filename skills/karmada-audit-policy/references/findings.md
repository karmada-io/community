# Finding format

## Finding classes

- Blocking: invalid YAML, wrong API group/version/kind, missing required selectors for propagation, invalid placement shape, admission webhook rejection.
- High: broad selectors in production scope, failover enabled without operational intent, conflict overwrite without ownership evidence, unsafe cluster-scoped propagation.
- Medium: runtime-dependent cluster labels, readiness, taints, capacity, or feature gates that cannot be proven from YAML alone.
- Informational: accepted broad override selector, omitted optional behavior, dry-run command.

## Deterministic routes

Use these known routes before opening source files:

- Namespaced `PropagationPolicy` or `OverridePolicy` selecting another namespace: blocking
  namespace-boundary issue. Safe fix is to align the policy namespace with the selected resource
  namespace, unless the operator explicitly wants cluster-wide ownership.
- `PropagationPolicy` or `ClusterPropagationPolicy` with empty or omitted `resourceSelectors`:
  blocking selector issue. Propagation policies require at least one resource selector.
- `OverridePolicy` or `ClusterOverridePolicy` with omitted or empty `resourceSelectors`: accepted
  broad selector. Report effective all-resources-in-scope behavior and blast radius; do not mark it
  invalid.
- Cluster-scoped policy used for a namespaced resource without selector namespace: ambiguous broad
  namespace scope. Ask whether cluster-wide ownership is intended or recommend an explicit selector
  namespace.
- Placement using cluster names, labels, fields, taints, spread, or replica weights: deterministic
  YAML interpretation only. Actual selected clusters require Cluster and binding evidence.
- Override patch path or operator review without the concrete workload manifest: validate policy
  shape, then mark path existence and semantic effect as runtime/resource-shape dependent.

For namespace mismatch findings on namespaced policies, the safe fix is usually to align the policy
namespace with the selected resource namespace. Do not present a cluster-scoped policy conversion as
the default fix; only mention it when the user has already stated cluster-wide ownership intent, and
pair it with a blast-radius warning.

For live-policy fixes, keep the first response non-mutating. Provide corrected YAML and a
`--dry-run=server` validation command, then ask for explicit operator confirmation before emitting
non-dry-run `kubectl apply`, `kubectl patch`, `kubectl delete`, or cleanup commands.

## Format

Use this compact structure for each finding:

```text
[severity] code-or-title
path: $.spec...
evidence: repository path or runtime input
impact: what can be rejected or behave unexpectedly
fix: exact correction or verification step
```

Write repository evidence as repo-relative text only, for example
`pkg/util/validation/validation.go:123`. Do not format source evidence as Markdown links and do not
include absolute checkout paths, `/tmp`, `/private/var`, or evaluation workspace directories.

Prefer stable descriptive titles until a maintained finding-code catalog exists. Do not invent a
code that implies a deterministic helper produced the result.
