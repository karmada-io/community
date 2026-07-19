# Karmada Components

This reference is a navigation aid. Confirm details in the current checkout before making
version-sensitive claims.

## Control plane

- **karmada-apiserver:** Kubernetes-compatible API front end that stores Kubernetes and Karmada API
  objects for the control plane.
- **karmada-aggregated-apiserver:** aggregated APIs including cluster-related subresources and access
  paths to member-cluster resources.
- **kube-controller-manager:** selected upstream Kubernetes controllers. Workload templates stored in
  the Karmada API are not reconciled into Pods in the control plane merely because they are standard
  Kubernetes resources.
- **karmada-controller-manager:** Karmada-specific controllers that reconcile Karmada objects and
  coordinate resource propagation and status processing.
- **karmada-scheduler:** selects eligible member clusters, ranks them, and records scheduling results
  for propagated resources.
- **karmada-webhook:** mutation and validation for Karmada and Kubernetes API objects.
- **etcd:** backing store for control-plane API objects.
- **karmada-agent:** pull-mode agent that registers a member cluster, consumes manifests from its
  execution namespace, and reports cluster and resource status.

## Add-ons and interfaces

- **karmada-scheduler-estimator:** estimates schedulable replicas using member-cluster scheduling
  information; do not reduce its role to aggregate free resources alone.
- **karmada-descheduler:** initiates rescheduling for supported dynamic replica scheduling scenarios.
- **karmada-search:** aggregated server for cross-cluster resource search and proxy capabilities.
- **karmadactl / kubectl karmada:** command-line interfaces for Karmada control-plane operations.

## Diagnostic boundary

Do not attribute every propagation failure to `karmada-controller-manager`. First locate the failed
stage: source resource and policy matching, binding creation, scheduling, override resolution, Work
creation, member-cluster apply, or status aggregation. Push and pull registration modes also change
which component performs member-cluster access.

## Packaged documentation topics

- core-concepts/components
- userguide/clustermanager/cluster-registration
