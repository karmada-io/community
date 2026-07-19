#!/usr/bin/env python3
"""Deterministically generate or review constrained Karmada policy scenarios."""

import argparse

from lib.scenario import emit, load_scenario


def evaluate(data: dict) -> dict:
    policy = data["policy"]
    findings = []
    warnings = []
    selectors = policy.get("resourceSelectors") or []
    if not selectors and policy["kind"] in {
        "PropagationPolicy",
        "ClusterPropagationPolicy",
    }:
        findings.append("spec.resourceSelectors: must not be empty")
    if not selectors and policy["kind"] in {
        "OverridePolicy",
        "ClusterOverridePolicy",
    }:
        warnings.append(
            "spec.resourceSelectors: empty selector matches all resources in scope"
        )
    if policy["kind"] in {"PropagationPolicy", "OverridePolicy"}:
        policy_namespace = policy.get("namespace")
        for index, selector in enumerate(selectors):
            namespace = selector.get("namespace", policy_namespace)
            if namespace != policy_namespace:
                findings.append(
                    f"spec.resourceSelectors[{index}].namespace: crosses policy namespace"
                )
    if policy.get("preemption") == "Always":
        for index, selector in enumerate(selectors):
            if not selector.get("name"):
                findings.append(
                    f"spec.resourceSelectors[{index}].name: required with preemption Always"
                )
    return {
        "id": data["id"],
        "valid": not findings,
        "findings": findings,
        "warnings": warnings,
        "policy": policy,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario")
    args = parser.parse_args()
    emit(evaluate(load_scenario(args.scenario)))


if __name__ == "__main__":
    main()
