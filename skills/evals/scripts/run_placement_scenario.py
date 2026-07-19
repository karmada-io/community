#!/usr/bin/env python3
"""Separate policy eligibility from observed placement and runtime evidence."""

import argparse

from lib.scenario import emit, load_scenario


def evaluate(data: dict) -> dict:
    required = data.get("requiredLabels", {})
    policy_eligible = []
    policy_ineligible = {}
    readiness = {}
    for cluster in data["clusters"]:
        reasons = []
        if "ready" in cluster:
            readiness[cluster["name"]] = cluster["ready"]
        for key, value in required.items():
            if cluster.get("labels", {}).get(key) != value:
                reasons.append(f"label-mismatch:{key}")
        if reasons:
            policy_ineligible[cluster["name"]] = reasons
        else:
            policy_eligible.append(cluster["name"])

    observed = sorted(data.get("bindingClusters") or [])
    runtime_rejections = {
        name: list(reasons)
        for name, reasons in sorted(data.get("runtimeRejections", {}).items())
    }
    eligible_names = set(policy_eligible)
    observed_names = set(observed)
    rejected_names = set(runtime_rejections)
    return {
        "id": data["id"],
        "policyEligible": sorted(policy_eligible),
        "policyIneligible": policy_ineligible,
        "observedSelected": observed,
        "observedRejected": runtime_rejections,
        "unresolved": sorted(eligible_names - observed_names - rejected_names),
        "contradictoryObserved": sorted(observed_names - eligible_names),
        "clusterReadiness": dict(sorted(readiness.items())),
        "historicalEvidenceComplete": data.get(
            "historicalEvidenceComplete", False
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario")
    args = parser.parse_args()
    emit(evaluate(load_scenario(args.scenario)))


if __name__ == "__main__":
    main()
