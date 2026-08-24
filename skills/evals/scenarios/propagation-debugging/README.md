# Missing Work propagation scenario

This scenario supplies ordered evidence that policy claim, binding creation, and scheduling
succeeded, while the expected Work is missing. The machine-readable input is
`input.json` in this directory.

Run the bounded helper:

```bash
python3 skills/evals/scripts/run_propagation_scenario.py \
  skills/evals/scenarios/propagation-debugging/input.json
```

The expected result identifies `work` as the first unsupported stage and stops there. The helper
does not infer a controller defect or prescribe mutation because no controller status, events,
logs, or live objects are present.

Use `karmada-debug-propagation` for a concrete propagation incident. Start with read-only evidence,
verify each stage in order, and distinguish observed facts from hypotheses and remediation steps.
