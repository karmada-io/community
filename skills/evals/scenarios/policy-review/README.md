# Broad preemption policy review scenario

This scenario supplies a namespaced PropagationPolicy intent with `preemption: Always` and a broad
Deployment selector. The machine-readable input is
`input.json` in this directory.

Run the bounded helper:

```bash
python3 skills/evals/scripts/run_policy_scenario.py \
  skills/evals/scenarios/policy-review/input.json
```

The expected finding requires an explicit resource name for this constrained preemption scenario.
This result is a suite invariant, not proof that a manifest passed the current Karmada admission
chain. Exact API and admission claims require a compatible Karmada checkout or server-side dry run.

Use `karmada-audit-policy` when a user supplies policy YAML for review. Report schema or admission
errors separately from operational risks and clearly identify the evidence used for each finding.
