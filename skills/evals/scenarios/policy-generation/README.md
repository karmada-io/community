# Namespaced policy generation scenario

This scenario represents an explicit request to propagate the `shop/checkout` Deployment to two
named member clusters. The machine-readable input is
`input.json` in this directory.

Run the bounded helper:

```bash
python3 skills/evals/scripts/run_policy_scenario.py \
  skills/evals/scenarios/policy-generation/input.json
```

The expected result reports a valid constrained scenario with no findings. It preserves the
supplied policy intent; it does not run Karmada API defaulting, admission validation, scheduling, or
live-cluster checks.

Use `karmada-create-policy` when a user asks for policy YAML from this kind of explicit intent. The
skill must ask for missing workload scope, selector, or placement facts instead of copying this
scenario's values. Use `karmada-audit-policy` for independent review of generated YAML.
