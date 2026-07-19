# Observed placement explanation scenario

This scenario contains three clusters, a required `region=us-east` label, and an observed binding
that selected only `member-a`. The machine-readable input is
`input.json` in this directory.

Run the bounded helper:

```bash
python3 skills/evals/scripts/run_placement_scenario.py \
  skills/evals/scenarios/placement-explanation/input.json
```

The helper classifies `member-a` and `member-b` as policy-eligible, `member-c` as ineligible, and
`member-b` as unresolved. Although the supplied snapshot marks `member-b` not ready, the helper does
not rewrite current readiness into a historical scheduler rejection. The fixture explicitly marks
historical evidence as incomplete.

Use `karmada-explain-placement` for an observed ResourceBinding or ClusterResourceBinding. A
definitive explanation requires the relevant policy, binding, cluster snapshot, and scheduler
events or status from the decision window.
