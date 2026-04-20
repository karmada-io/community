# Karmada Roadmap

This document defines a high level roadmap for Karmada development and upcoming releases.
Community and contributor involvement is vital for successfully implementing all desired items for each release.
We hope that the items listed below will inspire further engagement from the community to keep Karmada progressing and shipping exciting and valuable features.

The following outlines Karmada's 2026 feature plan.

## Application Priority and Preemption

Building on priority scheduling delivered in 2025, we plan to add preemption so higher-priority workloads can reclaim resources when needed. See the proposal: https://github.com/karmada-io/karmada/tree/master/docs/proposals/scheduling/binding-priority-preemption

## Multi-cluster Queue Management

For AI training and batch job scenarios, provide queueing to manage multi-tenant workloads fairly and efficiently across clusters.

## Precise Cluster Resource-Aware Scheduling

Before a workload syncs to member clusters, pre-deduct the required resources in those clusters to avoid overload. Track progress in https://github.com/karmada-io/karmada/issues/6783

## Core API Promotion to Beta

Promote core APIs (PropagationPolicy, OverridePolicy) to beta, with compatibility-preserving adjustments and optimizations based on multi-year usage.

## Extended Cluster Affinities

Evolve cluster affinity capabilities based on the original design (https://github.com/karmada-io/karmada/tree/master/docs/proposals/scheduling/multi-scheduling-group) and the new extension proposal (https://github.com/karmada-io/karmada/pull/7078).

## Kubernetes DRA (Dynamic Resource Allocation) Support

Support Kubernetes Dynamic Resource Allocation (DRA) in multi-cluster scenarios, enabling efficient scheduling and management of heterogeneous resources (e.g., GPUs, FPGAs) across clusters. Track progress in https://github.com/karmada-io/karmada/issues/7095

## Federation-Level Application Rolling Update

Provide federation-level rolling update capabilities for applications distributed across multiple clusters, allowing users to perform controlled, progressive rollouts with cross-cluster coordination, canary strategies, and rollback support.

## Others
### Scalability and Performance Enhancement

This is an ongoing effort where a team comprising Karmada adopters will continuously identify and address any 
performance issues within the system. The focus will be on scalability and performance enhancements, ensuring 
that the system evolves to meet growing demands efficiently and effectively. This team will actively work on 
detecting bottlenecks, optimizing resources, and improving the overall performance of Karmada.
See [Karmada SIG-Scalability Meeting Notes](https://docs.google.com/document/d/1BUZBDvtbtfU9MmOz7KVdvGiiCny-zz_34FuLlW4AGmM/edit?usp=sharing)
to follow the progress.

### UI

This is an ongoing effort where the community will continue to iterate on 
its functionality, stability, and user experience based on feedback from users. See [Karmada SIG-UI Meeting Notes](https://docs.google.com/document/d/1dX3skCE-QRBWzABq3O9cG7yhIDUWLYWmg7kGq8UHU6s/edit?usp=sharing)
to follow the progress.

## Pending
- Cluster addon management
- Multi-cluster Application
- Multi-cluster monitoring
- Multi-cluster logging
- Multi-cluster storage
- Multi-cluster RBAC
- Multi-cluster networking
- Data migration across clusters
- Image registry across clouds
- Multi-cluster Service Mesh solutions
- Cluster Problem Detector (CPD)
- Multi-cluster workflow
