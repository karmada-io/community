#!/usr/bin/env python3
"""Evaluate release gates from routing and output result bundles."""

import argparse
import json
import re
from pathlib import Path

from lib.grading import grading_summary

SOURCE_CITATION_RE = re.compile(
    r"(?<![\w.-])(?:pkg|cmd|test|internal|examples|artifacts)/[A-Za-z0-9_./*-]+"
    r":\d+"
)

EVALUATION_SECTIONS = (
    "deterministic",
    "core_routing",
    "package_only_output",
    "checkout_output",
)


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def result_list(path: Path) -> list:
    candidate = path / "results.json" if path.is_dir() else path
    data = load_json(candidate)
    if not isinstance(data, list):
        raise ValueError(f"result bundle must contain a list: {candidate}")
    return data


def missing_required_sections(gates: dict, provided: dict) -> list[str]:
    required = gates.get("required_sections", EVALUATION_SECTIONS)
    unknown = sorted(set(required) - set(EVALUATION_SECTIONS))
    if unknown:
        raise ValueError(f"unknown required evaluation sections: {', '.join(unknown)}")
    return [name for name in required if not provided.get(name)]


def rate(passed: int, total: int) -> float:
    return passed / total if total else 1.0


def check(name: str, actual, operator: str, expected) -> dict:
    if operator == ">=":
        passed = actual >= expected
    elif operator == "<=":
        passed = actual <= expected
    elif operator == "==":
        passed = actual == expected
    else:
        raise ValueError(f"unknown gate operator: {operator}")
    return {
        "name": name,
        "actual": actual,
        "operator": operator,
        "expected": expected,
        "passed": passed,
    }


def evaluate_routing(report: dict, config: dict) -> list[dict]:
    runs = report.get("runs") or []
    if not runs:
        return [check("routing runs present", 0, ">=", 1)]
    required_total = 0
    required_selected = 0
    forbidden_total = 0
    forbidden_selected = 0
    per_skill = {}
    for run in runs:
        required = set(run.get("required_skills") or [])
        selected = set(run.get("selected_skills") or [])
        forbidden = set(run.get("forbidden_skills") or [])
        required_total += len(required)
        required_selected += len(required & selected)
        forbidden_total += len(forbidden)
        forbidden_selected += len(forbidden & selected)
        for skill in required:
            values = per_skill.setdefault(skill, [0, 0])
            values[1] += 1
            values[0] += skill in selected
    forbidden_activation_rate = (
        forbidden_selected / forbidden_total if forbidden_total else 0.0
    )
    overall = rate(required_selected, required_total)
    checks = [
        check(
            "core required skill recall",
            overall,
            ">=",
            config["minimum_overall_required_recall"],
        ),
        check(
            "core minimum per-skill recall",
            min(
                (rate(selected, total) for selected, total in per_skill.values()),
                default=1.0,
            ),
            ">=",
            config["minimum_per_skill_required_recall"],
        ),
        check(
            "core forbidden activation rate",
            forbidden_activation_rate,
            "<=",
            config["maximum_forbidden_activation_rate"],
        ),
        check(
            "core clear boundary pass rate",
            rate(sum(bool(run.get("passed")) for run in runs), len(runs)),
            ">=",
            config["minimum_clear_boundary_pass_rate"],
        ),
    ]
    return checks


def evaluate_output(
    results: list, config: dict, package_only: bool, source_claim_limit: int = 0
) -> list[dict]:
    summary = grading_summary(results)
    severity = summary.get("severity") or {}
    critical = severity.get("critical") or {}
    required = severity.get("required") or {}
    safety_failures = sum(not item.get("safety_passed", True) for item in results)
    source_claims = sum(
        len(SOURCE_CITATION_RE.findall(item.get("final_message") or ""))
        for item in results
    )
    checks = [
        check(
            "all output runs completed",
            sum(bool(item.get("completed")) and not item.get("error") for item in results),
            "==",
            len(results),
        ),
        check(
            "critical assertion pass rate",
            critical.get("pass_rate") if critical.get("pass_rate") is not None else 0.0,
            ">=",
            config["minimum_critical_assertion_pass_rate"],
        ),
        check(
            "required assertion pass rate",
            required.get("pass_rate") if required.get("pass_rate") is not None else 1.0,
            ">=",
            config["minimum_required_assertion_pass_rate"],
        ),
        check(
            "output safety failures",
            safety_failures,
            "<=",
            config["maximum_safety_failures"],
        ),
    ]
    if package_only:
        checks.append(
            check(
                "package-only checkout source claims",
                source_claims,
                "<=",
                source_claim_limit,
            )
        )
    return checks


def execution_checks(items: list, config: dict, routing: bool) -> list[dict]:
    required_runners = set(config["required_runners"])
    observed_runners = {
        item.get("runner") for item in items if isinstance(item.get("runner"), str)
    }
    repetitions = {}
    cases_by_runner = {runner: set() for runner in required_runners}
    for item in items:
        runner = item.get("runner")
        case = (item.get("id"), item.get("skill") if not routing else None)
        key = (runner, *case)
        repetitions.setdefault(key, set()).add(item.get("repetition"))
        if runner in cases_by_runner:
            cases_by_runner[runner].add(case)
    minimum = min((len(values) for values in repetitions.values()), default=0)
    all_cases = set().union(*cases_by_runner.values())
    covered_runner_cases = sum(len(cases) for cases in cases_by_runner.values())
    expected_runner_cases = len(required_runners) * len(all_cases)
    return [
        check(
            "required runners present",
            len(observed_runners & required_runners),
            "==",
            len(required_runners),
        ),
        check(
            "required runner case coverage",
            covered_runner_cases,
            "==",
            expected_runner_cases,
        ),
        check(
            "minimum repetitions per runner and case",
            minimum,
            ">=",
            config["minimum_repetitions_per_case"],
        ),
    ]


def evaluate_comparison(comparison: dict, config: dict) -> list[dict]:
    quality = comparison.get("quality") or {}
    baseline = quality.get("baseline") or {}
    with_skill = quality.get("with_skill") or {}
    baseline_critical = baseline.get("critical_failures")
    with_critical = with_skill.get("critical_failures")
    baseline_required = ((baseline.get("severity") or {}).get("required") or {}).get("pass_rate")
    with_required = ((with_skill.get("severity") or {}).get("required") or {}).get("pass_rate")
    if not all(isinstance(value, (int, float)) for value in (baseline_critical, with_critical)):
        return [check("comparison critical quality is present", 0, "==", 1)]
    checks = [
        check(
            "critical failure delta",
            with_critical - baseline_critical,
            "<=",
            config["baseline_maximum_critical_failure_delta"],
        )
    ]
    if isinstance(baseline_required, (int, float)) and isinstance(with_required, (int, float)):
        checks.append(
            check(
                "required assertion pass-rate delta",
                with_required - baseline_required,
                ">=",
                config["baseline_minimum_required_pass_rate_delta"],
            )
        )
    return checks


def evaluate_deterministic(report: dict, config: dict) -> list[dict]:
    checks = report.get("checks") or []
    passed = sum(bool(item.get("passed")) for item in checks)
    return [
        check(
            "deterministic check pass rate",
            rate(passed, len(checks)) if checks else 0.0,
            ">=",
            config["required_pass_rate"],
        ),
        check(
            "deterministic safety failures",
            report.get("safety_failures", 1),
            "<=",
            config["max_safety_failures"],
        ),
    ]


def token_warnings(comparison: dict, threshold: float) -> list[str]:
    warnings = []
    for field in ("input_tokens", "output_tokens"):
        value = (comparison.get("totals") or {}).get(field) or {}
        delta = value.get("delta_percent")
        if isinstance(delta, (int, float)) and delta > threshold:
            warnings.append(f"{field} increased by {delta}% (warning threshold {threshold}%)")
    return warnings


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = path.with_suffix(".md")
    lines = ["# Evaluation Gates", "", f"Overall: **{'PASS' if report['passed'] else 'FAIL'}**", ""]
    for section, checks in report["sections"].items():
        lines.extend([f"## {section.replace('_', ' ').title()}", "", "| Gate | Actual | Requirement | Result |", "|---|---:|---|---|"])
        for item in checks:
            lines.append(
                f"| {item['name']} | {item['actual']} | {item['operator']} {item['expected']} | "
                f"{'PASS' if item['passed'] else 'FAIL'} |"
            )
        lines.append("")
    if report["warnings"]:
        lines.extend(["## Warnings", "", *[f"- {warning}" for warning in report["warnings"]], ""])
    markdown.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gates", type=Path, required=True)
    parser.add_argument("--deterministic", type=Path)
    parser.add_argument("--core-routing", type=Path, action="append")
    parser.add_argument("--package-only-output", type=Path, action="append")
    parser.add_argument("--checkout-output", type=Path, action="append")
    parser.add_argument("--comparison", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args()

    gates = load_json(args.gates)
    sections = {}
    inputs = (
        ("deterministic", args.deterministic),
        ("core_routing", args.core_routing),
        ("package_only_output", args.package_only_output),
        ("checkout_output", args.checkout_output),
    )
    provided = dict(inputs)
    missing = missing_required_sections(gates, provided)
    if args.deterministic:
        sections["deterministic"] = evaluate_deterministic(
            load_json(args.deterministic), gates["deterministic"]
        )
    if args.core_routing:
        reports = [load_json(path) for path in args.core_routing]
        runs = [dict(run, runner=report.get("runner")) for report in reports for run in report.get("runs", [])]
        sections["core_routing"] = evaluate_routing({"runs": runs}, gates["core_routing"])
        sections["core_routing"].extend(execution_checks(runs, gates["execution"], True))
    if args.package_only_output:
        results = [item for path in args.package_only_output for item in result_list(path)]
        sections["package_only_output"] = evaluate_output(
            results,
            gates["output"],
            True,
            gates["deterministic"]["max_package_only_source_claims"],
        )
        sections["package_only_output"].extend(execution_checks(results, gates["execution"], False))
    if args.checkout_output:
        results = [item for path in args.checkout_output for item in result_list(path)]
        sections["checkout_output"] = evaluate_output(results, gates["output"], False)
        sections["checkout_output"].extend(execution_checks(results, gates["execution"], False))
    warnings = []
    if args.comparison:
        comparison = load_json(args.comparison)
        sections["baseline_comparison"] = evaluate_comparison(comparison, gates["output"])
        warnings.extend(
            token_warnings(comparison, gates["tokens"]["warning_regression_percent"])
        )
    if missing:
        warnings.append(f"not evaluated: {', '.join(missing)}")
    passed = all(item["passed"] for checks in sections.values() for item in checks)
    if missing and not args.allow_missing:
        passed = False
    report = {
        "schema_version": 1,
        "passed": passed,
        "missing_sections": missing,
        "sections": sections,
        "warnings": warnings,
    }
    write_report(args.output, report)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
