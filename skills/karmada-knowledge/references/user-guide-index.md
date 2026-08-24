# Karmada User Guide Knowledge Index

Use this index to choose packaged user-facing workflow topics, then verify claims against the current
checkout. The topic names were derived from official Karmada documentation during authoring, but the
runtime skill should not depend on website access.

## Cluster lifecycle

- Cluster registration and push/pull modes:
  userguide/clustermanager/cluster-registration
- ANP integration:
  userguide/clustermanager/working-with-anp

## Scheduling and policy

- Propagation policy:
  userguide/scheduling/propagation-policy
- Override policy:
  userguide/scheduling/override-policy
- Dependency propagation:
  userguide/scheduling/propagate-dependencies
- Priority scheduling:
  userguide/scheduling/priority-scheduling
- Cluster resource modeling and scheduler estimator:
  userguide/scheduling/cluster-resources
  and userguide/scheduling/scheduler-estimator
- Descheduling, overcommit protection, and workload rebalancing:
  userguide/scheduling/descheduler,
  userguide/scheduling/scheduling-overcommit-protection,
  and userguide/scheduling/workload-rebalancer
- Multi-component scheduling:
  userguide/scheduling/multi-component-scheduling

## Failure handling

- Cluster and application failover:
  userguide/failover/cluster-failover
  and userguide/failover/application-failover
- Cluster status and taints:
  userguide/failover/cluster-status-maintenance
  and userguide/failover/cluster-taint-management
- Failover processing details:
  userguide/failover/failover-analysis

## Global view and resource access

- Aggregated API endpoint:
  userguide/globalview/aggregated-api-endpoint
- Global search and proxy:
  userguide/globalview/global-search-for-resources
  and userguide/globalview/proxy-global-resource
- Resource interpreter customization:
  userguide/globalview/customizing-resource-interpreter

## Multi-cluster services and networking

- Multi-cluster service discovery and native service access:
  userguide/service/multi-cluster-service
  and userguide/service/multi-cluster-service-with-native-svc-access
- Multi-cluster ingress:
  userguide/service/multi-cluster-ingress
- Network integrations:
  userguide/network/working-with-submariner

## Additional domains

The User Guide also covers autoscaling, CI/CD integrations, security governance, namespace and quota
management, and service-mesh integrations. Add these topics to `source-map.json` when a skill begins
depending on them; avoid loading all User Guide material for unrelated requests.
