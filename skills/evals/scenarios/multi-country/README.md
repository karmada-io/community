# Multi-country active-active scenario

This example models clusters in Korea, Japan, and Singapore without deriving geography from names.

## Cluster metadata

Represent country with an organization-approved label. Use the real Karmada
`Cluster.spec.region` and `Cluster.spec.zones` fields for region and zones. The fixture
`input.json` in this directory uses:

| Cluster | Country | Region | Zone |
|---|---|---|---|
| member-seoul-a | kr | seoul | a |
| member-tokyo-a | jp | tokyo | a |
| member-singapore-a | sg | singapore | a |

Run:

```bash
python3 skills/evals/scripts/run_cluster_scenario.py \
  skills/evals/scenarios/multi-country/input.json
```

The helper verifies explicit metadata coverage and the minimum number of represented countries. It
does not prove latency, data residency, connectivity, capacity, availability, or scheduler output.

## Policy reasoning

Use `karmada-create-policy` to generate policy intent from approved metadata keys. Use
`karmada-audit-policy` to review selector scope and spread shape. Use
`karmada-explain-placement` only after binding and Cluster evidence exist. Use
`karmada-debug-propagation` when selected clusters do not receive or report the workload.
