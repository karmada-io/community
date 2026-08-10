#!/usr/bin/env python3
"""Evaluate exact routing across all installed Karmada runtime skills."""

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

from lib.runtime import USER_SKILLS, package_digest, run_condition, skill_package_dirs

RUNNERS = ("codex", "claude")
FALLBACK_TARGET = "karmada-knowledge"


def load_cases(path: Path) -> list:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("cases"), list):
        raise ValueError("routing corpus must use schema_version 1 and cases")
    cases = []
    ids = set()
    for item in data["cases"]:
        case_id = item.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            raise ValueError(f"invalid or duplicate routing id: {case_id}")
        if not isinstance(item.get("prompt"), str) or not item["prompt"].strip():
            raise ValueError(f"missing prompt for {case_id}")
        expected = item.get("expected_skill")
        if expected is not None and (
            not isinstance(expected, str) or expected not in USER_SKILLS
        ):
            raise ValueError(f"invalid expected_skill for {case_id}")
        routing = {
            "required_skills": [expected] if expected else [],
            "allowed_supporting_skills": [],
            "forbidden_skills": [],
        }
        ids.add(case_id)
        cases.append(
            {
                "id": case_id,
                "skill": expected or FALLBACK_TARGET,
                "prompt": item["prompt"],
                "expected_trigger": bool(expected),
                "expected_skill": expected,
                "routing_expectation": routing,
                "boundary": item.get("boundary", ""),
            }
        )
    return cases


def classify(result: dict) -> dict:
    routing = result.get("routing_expectation") or {
        "required_skills": [result["expected_skill"]] if result.get("expected_skill") else [],
        "allowed_supporting_skills": [],
        "forbidden_skills": [],
    }
    required = set(routing["required_skills"])
    allowed = set(routing["allowed_supporting_skills"])
    forbidden = set(routing["forbidden_skills"])
    response = (result.get("final_message") or "").strip().strip("`")
    actual = set(result.get("selected_skills") or [])
    if result.get("selected_skill"):
        actual.add(result["selected_skill"])
    actual.update(result.get("loaded_skills") or [])
    missing = required - actual
    disallowed = (actual & forbidden) | (actual - required - allowed)
    passed = bool(
        result.get("completed")
        and not result.get("error")
        and not missing
        and not disallowed
    )
    return {
        "id": result["id"],
        "repetition": result["repetition"],
        "boundary": result.get("boundary", ""),
        "expected_skill": result.get("expected_skill"),
        "required_skills": sorted(required),
        "allowed_supporting_skills": sorted(allowed),
        "forbidden_skills": sorted(forbidden),
        "selected_skills": sorted(actual),
        "missing_required_skills": sorted(missing),
        "disallowed_skills": sorted(disallowed),
        "response": response,
        "passed": passed,
        "completed": bool(result.get("completed")),
        "activation_method": (result.get("activation_evidence") or {}).get("method"),
        "usage": result.get("usage", {}),
        "error": result.get("error"),
        "trace": result.get("trace"),
    }


def build_report(runner: str, digest: str, results: list) -> dict:
    runs = [classify(result) for result in results]
    expected = Counter(
        skill for run in runs for skill in (run["required_skills"] or ["none"])
    )
    selected = Counter(
        skill for run in runs for skill in (run["selected_skills"] or ["none"])
    )
    passed = sum(run["passed"] for run in runs)
    required_total = sum(len(run["required_skills"]) for run in runs)
    required_selected = sum(
        len(set(run["required_skills"]) & set(run["selected_skills"])) for run in runs
    )
    forbidden_total = sum(len(run["forbidden_skills"]) for run in runs)
    forbidden_selected = sum(
        len(set(run["forbidden_skills"]) & set(run["selected_skills"])) for run in runs
    )
    return {
        "schema_version": 1,
        "runner": runner,
        "package_digest": digest,
        "passed": passed == len(runs),
        "summary": {
            "runs": len(runs),
            "passed": passed,
            "failed": len(runs) - passed,
            "accuracy": passed / len(runs) if runs else 0,
            "expected_counts": dict(sorted(expected.items())),
            "selected_counts": dict(sorted(selected.items())),
            "required_skill_recall": required_selected / required_total if required_total else 1.0,
            "forbidden_activation_rate": forbidden_selected / forbidden_total if forbidden_total else 0.0,
        },
        "runs": runs,
    }


def write_report(path: Path, report: dict) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "routing-results.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = report["summary"]
    lines = [
        f"# {report['runner'].title()} Cross-Skill Routing",
        "",
        f"Accuracy: **{summary['passed']}/{summary['runs']} ({summary['accuracy']:.1%})**",
        "",
        "| Case | Run | Expected | Selected | Result | Input | Output |",
        "|---|---:|---|---|---|---:|---:|",
    ]
    for run in report["runs"]:
        usage = run["usage"]
        lines.append(
            f"| `{run['id']}` | {run['repetition']} | `{', '.join(run['required_skills']) or 'none'}` | "
            f"`{', '.join(run['selected_skills']) or 'none'}` | {'PASS' if run['passed'] else 'FAIL'} | "
            f"{usage.get('input_tokens', 0)} | {usage.get('output_tokens', 0)} |"
        )
    (path / "routing-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--collection-root", type=Path)
    parser.add_argument("--corpus", type=Path)
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runner", choices=RUNNERS + ("all",), default="all")
    parser.add_argument(
        "--profile",
        choices=("checkout", "package-only"),
        default="package-only",
        help="Workspace profile used for routing. Release routing uses package-only.",
    )
    parser.add_argument(
        "--case",
        action="append",
        dest="case_ids",
        help="Limit evaluation to a case id. Can be repeated.",
    )
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--case-timeout", type=int, default=180)
    args = parser.parse_args()
    if args.repetitions < 1 or args.case_timeout < 1:
        parser.error("--repetitions and --case-timeout must be positive")

    root = args.root.resolve()
    collection = (
        args.collection_root.resolve()
        if args.collection_root
        else Path(__file__).resolve().parents[2]
    )
    corpus = args.corpus or collection / "evals/cases/routing.json"
    package_dir = args.package_dir.resolve()
    output = args.output.expanduser().resolve()
    cases = load_cases(corpus)
    if args.case_ids:
        requested = set(args.case_ids)
        available = {case["id"] for case in cases}
        unknown = requested - available
        if unknown:
            parser.error(f"unknown --case values: {', '.join(sorted(unknown))}")
        cases = [case for case in cases if case["id"] in requested]
    runners = RUNNERS if args.runner == "all" else (args.runner,)
    all_passed = True
    digest = package_digest(package_dir)
    available_skills = [path.name for path in skill_package_dirs(package_dir)]
    for case in cases:
        case["available_skills"] = available_skills
    for runner in runners:
        if shutil.which(runner) is None:
            print(f"{runner}: executable not found")
            all_passed = False
            continue
        runner_output = output / runner
        results = run_condition(
            root,
            runner_output,
            cases,
            args.repetitions,
            "trigger",
            "with-skill",
            package_dir,
            runner,
            args.case_timeout,
            args.profile,
        )
        report = build_report(runner, digest, results)
        write_report(runner_output, report)
        summary = report["summary"]
        print(f"{runner}: {summary['passed']}/{summary['runs']} ({runner_output})")
        all_passed = all_passed and report["passed"]
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
