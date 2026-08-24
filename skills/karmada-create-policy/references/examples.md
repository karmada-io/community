# Policy Examples

Use these as scoped templates. Replace every uppercase placeholder with user-provided values.

`ClusterPropagationPolicy` and `ClusterOverridePolicy` are cluster-scoped policy objects. They can
select either cluster-scoped resources or namespaced resources. Omit `resourceSelectors[].namespace`
for a cluster-scoped resource; set it explicitly for a namespaced resource.

These examples are the first source for ordinary YAML generation. Use API or webhook source only
when a requested field is not covered here, admission behavior is uncertain, or the user asks for
current-checkout proof.

## Namespaced Propagation

```yaml
apiVersion: policy.karmada.io/v1alpha1
kind: PropagationPolicy
metadata:
  name: RESOURCE_NAME-propagation
  namespace: RESOURCE_NAMESPACE
spec:
  resourceSelectors:
    - apiVersion: RESOURCE_API_VERSION
      kind: RESOURCE_KIND
      namespace: RESOURCE_NAMESPACE
      name: RESOURCE_NAME
  placement:
    clusterAffinity:
      clusterNames:
        - TARGET_CLUSTER
```

Repository evidence: `artifacts/example/propagationpolicy_simple.yaml`.

## Cluster Policy for a Cluster-Scoped Resource

Use `ClusterPropagationPolicy`; omit the selector namespace.

```yaml
apiVersion: policy.karmada.io/v1alpha1
kind: ClusterPropagationPolicy
metadata:
  name: RESOURCE_NAME-propagation
spec:
  resourceSelectors:
    - apiVersion: RESOURCE_API_VERSION
      kind: CLUSTER_SCOPED_RESOURCE_KIND
      name: RESOURCE_NAME
  placement:
    clusterAffinity:
      clusterNames:
        - TARGET_CLUSTER
```

API evidence: `pkg/apis/policy/v1alpha1/propagation_types.go`.

## Cluster Policy for Cross-Namespace Namespaced Resources

Use `ClusterPropagationPolicy` when cluster-wide or cross-namespace policy ownership is intended.
Set every selected namespaced resource's namespace explicitly.

```yaml
apiVersion: policy.karmada.io/v1alpha1
kind: ClusterPropagationPolicy
metadata:
  name: CROSS_NAMESPACE_POLICY_NAME
spec:
  resourceSelectors:
    - apiVersion: RESOURCE_API_VERSION
      kind: RESOURCE_KIND
      namespace: RESOURCE_NAMESPACE_A
      name: RESOURCE_NAME_A
    - apiVersion: RESOURCE_API_VERSION
      kind: RESOURCE_KIND
      namespace: RESOURCE_NAMESPACE_B
      name: RESOURCE_NAME_B
  placement:
    clusterAffinity:
      clusterNames:
        - TARGET_CLUSTER
```

Repository evidence: `artifacts/example/clusterpropagationpolicy_simple.yaml`.

## Namespaced Override

```yaml
apiVersion: policy.karmada.io/v1alpha1
kind: OverridePolicy
metadata:
  name: RESOURCE_NAME-override
  namespace: RESOURCE_NAMESPACE
spec:
  resourceSelectors:
    - apiVersion: RESOURCE_API_VERSION
      kind: RESOURCE_KIND
      namespace: RESOURCE_NAMESPACE
      name: RESOURCE_NAME
  overrideRules:
    - targetCluster:
        clusterNames:
          - TARGET_CLUSTER
      overriders:
        annotationsOverrider:
          - operator: add
            value:
              ANNOTATION_KEY: ANNOTATION_VALUE
```

Repository evidence: `artifacts/example/overridepolicy_simple.yaml`.

## Cluster Override for a Cluster-Scoped Resource

Use `ClusterOverridePolicy`; omit the selector namespace.

```yaml
apiVersion: policy.karmada.io/v1alpha1
kind: ClusterOverridePolicy
metadata:
  name: RESOURCE_NAME-override
spec:
  resourceSelectors:
    - apiVersion: RESOURCE_API_VERSION
      kind: CLUSTER_SCOPED_RESOURCE_KIND
      name: RESOURCE_NAME
  overrideRules:
    - targetCluster:
        labelSelector:
          matchLabels:
            CLUSTER_LABEL_KEY: CLUSTER_LABEL_VALUE
      overriders:
        annotationsOverrider:
          - operator: add
            value:
              ANNOTATION_KEY: ANNOTATION_VALUE
```

API evidence: `pkg/apis/policy/v1alpha1/override_types.go`.

## Cluster Override for Cross-Namespace Namespaced Resources

Use `ClusterOverridePolicy` when cluster-wide or cross-namespace override ownership is intended. Set
every selected namespaced resource's namespace explicitly.

```yaml
apiVersion: policy.karmada.io/v1alpha1
kind: ClusterOverridePolicy
metadata:
  name: CROSS_NAMESPACE_OVERRIDE_NAME
spec:
  resourceSelectors:
    - apiVersion: RESOURCE_API_VERSION
      kind: RESOURCE_KIND
      namespace: RESOURCE_NAMESPACE_A
      name: RESOURCE_NAME_A
    - apiVersion: RESOURCE_API_VERSION
      kind: RESOURCE_KIND
      namespace: RESOURCE_NAMESPACE_B
      name: RESOURCE_NAME_B
  overrideRules:
    - targetCluster:
        labelSelector:
          matchLabels:
            CLUSTER_LABEL_KEY: CLUSTER_LABEL_VALUE
      overriders:
        annotationsOverrider:
          - operator: add
            value:
              ANNOTATION_KEY: ANNOTATION_VALUE
```

Repository evidence: `artifacts/example/clusteroverridepolicy.yaml`.

## Optional Live Validation

This command contacts the intended Karmada API server. Do not include it by default in a
package-only answer or when the user only asks for an artifact. Offer it only when the user
explicitly asks for live validation and all placeholders are resolved:

```bash
kubectl --context <karmada-apiserver> apply --server-side --dry-run=server -f policy.yaml
```

The observed response can check API and admission acceptance for that server. Before it is run, do
not claim successful admission. Even a successful response does not prove cluster existence,
matching labels, readiness, capacity, feature-gate state, or final scheduling.
