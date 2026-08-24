#!/usr/bin/env python3
"""Validate explicit multi-country cluster metadata and distribution scenarios."""

import argparse
from collections import Counter

from lib.scenario import emit, load_scenario

def evaluate(data: dict) -> dict:
    findings = []
    countries = Counter()
    country_label = data.get("countryLabel")
    if not country_label:
        findings.append("scenario: missing countryLabel")
    for cluster in data["clusters"]:
        fields = cluster.get("fields", {})
        labels = cluster.get("labels", {})
        country = labels.get(country_label) if country_label else None
        if not country:
            findings.append(f"{cluster['name']}: missing country label")
        if not fields.get("region"):
            findings.append(f"{cluster['name']}: missing Cluster.spec.region")
        zones = fields.get("zones")
        if not isinstance(zones, list) or not zones:
            findings.append(f"{cluster['name']}: missing Cluster.spec.zones")
        if country:
            countries[country] += 1
    minimum = data.get("minimumCountries", 1)
    if len(countries) < minimum:
        findings.append(
            f"spread: requires {minimum} countries, only {len(countries)} represented"
        )
    return {
        "id": data["id"],
        "valid": not findings,
        "countries": dict(sorted(countries.items())),
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario")
    args = parser.parse_args()
    emit(evaluate(load_scenario(args.scenario)))


if __name__ == "__main__":
    main()
