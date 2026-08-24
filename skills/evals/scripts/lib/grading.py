#!/usr/bin/env python3
"""Build and validate blind assertion grading for output evaluations."""

import json
import re

VERDICTS = {"pass", "fail", "uncertain"}
JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)


def critical_assertion_indexes(result: dict) -> set[int]:
    assertions = result.get("assertions") or []
    configured = result.get("critical_assertions")
    if configured is None:
        return set(range(1, len(assertions) + 1))
    return set(configured)


def assertion_severity(result: dict, index: int) -> str:
    critical = result.get("critical_assertions")
    required = result.get("required_assertions")
    if critical is None and required is None:
        return "critical"
    if index in set(critical or []):
        return "critical"
    if index in set(required or []):
        return "required"
    return "advisory"


def build_grading_prompt(result: dict) -> str:
    assertions = result.get("assertions") or []
    assertion_lines = [
        f"{index}. {assertion}" for index, assertion in enumerate(assertions, 1)
    ]
    schema_example = {
        "assertions": [
            {
                "index": 1,
                "verdict": "pass",
                "evidence": "Short quotation or precise description from the answer.",
            }
        ]
    }
    return "\n".join(
        [
            "Grade the answer against each assertion independently.",
            "Do not infer which evaluation condition or skill produced the answer.",
            "Use only the task, expected outcome, assertions, and answer below.",
            "A pass requires direct support in the answer. Use uncertain when the answer is ambiguous.",
            "Return JSON only. Include exactly one item for every assertion in index order.",
            "Allowed verdicts: pass, fail, uncertain.",
            "Schema example:",
            json.dumps(schema_example, ensure_ascii=False),
            "",
            "Task:",
            result.get("prompt", ""),
            "",
            "Expected outcome:",
            result.get("expected_output", ""),
            "",
            "Assertions:",
            *assertion_lines,
            "",
            "Answer:",
            result.get("final_message", ""),
        ]
    )


def _json_object(text: str) -> dict:
    stripped = (text or "").strip()
    try:
        value = json.loads(stripped)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        match = JSON_FENCE_RE.search(stripped)
        if not match:
            return {}
        try:
            value = json.loads(match.group(1))
        except json.JSONDecodeError:
            return {}
        return value if isinstance(value, dict) else {}


def parse_grading_response(
    text: str,
    result: dict,
    grader: str,
    usage: dict = None,
    error: str = None,
) -> dict:
    assertions = result.get("assertions") or []
    critical = critical_assertion_indexes(result)
    if error:
        return {
            "status": "error",
            "grader": grader,
            "error": error,
            "assertions": [],
            "passed": False,
            "usage": usage or {},
        }
    payload = _json_object(text)
    grades = payload.get("assertions") if isinstance(payload, dict) else None
    if not isinstance(grades, list):
        return {
            "status": "error",
            "grader": grader,
            "error": "grader response requires an assertions array",
            "assertions": [],
            "passed": False,
            "usage": usage or {},
        }

    normalized = []
    seen = set()
    errors = []
    for grade in grades:
        if not isinstance(grade, dict):
            errors.append("grade must be an object")
            continue
        index = grade.get("index")
        verdict = grade.get("verdict")
        evidence = grade.get("evidence")
        if type(index) is not int or not 1 <= index <= len(assertions):
            errors.append(f"invalid assertion index: {index!r}")
            continue
        if index in seen:
            errors.append(f"duplicate assertion index: {index}")
            continue
        seen.add(index)
        if verdict not in VERDICTS:
            errors.append(f"invalid verdict for assertion {index}: {verdict!r}")
            continue
        if not isinstance(evidence, str) or not evidence.strip():
            errors.append(f"assertion {index} requires evidence")
            continue
        normalized.append(
            {
                "index": index,
                "assertion": assertions[index - 1],
                "verdict": verdict,
                "evidence": evidence.strip(),
                "critical": index in critical,
                "severity": assertion_severity(result, index),
            }
        )
    expected_indexes = set(range(1, len(assertions) + 1))
    if seen != expected_indexes:
        errors.append(
            f"grader indexes do not match assertions: expected {sorted(expected_indexes)}, "
            f"found {sorted(seen)}"
        )
    if errors:
        return {
            "status": "error",
            "grader": grader,
            "error": "; ".join(errors),
            "assertions": normalized,
            "passed": False,
            "usage": usage or {},
        }

    counts = {
        verdict: sum(item["verdict"] == verdict for item in normalized)
        for verdict in sorted(VERDICTS)
    }
    critical_failures = sum(
        item["critical"] and item["verdict"] != "pass" for item in normalized
    )
    return {
        "status": "completed",
        "grader": grader,
        "error": None,
        "assertions": normalized,
        "counts": counts,
        "critical_failures": critical_failures,
        "passed": critical_failures == 0,
        "usage": usage or {},
    }


def grading_summary(results: list) -> dict:
    gradings = [
        item["grading"]
        for item in results
        if isinstance(item.get("grading"), dict)
        and item["grading"].get("status") == "completed"
    ]
    assertions = [grade for grading in gradings for grade in grading["assertions"]]
    passed = sum(grade["verdict"] == "pass" for grade in assertions)
    severity = {}
    for name in ("critical", "required", "advisory"):
        selected = [grade for grade in assertions if grade.get("severity", "critical") == name]
        selected_passed = sum(grade["verdict"] == "pass" for grade in selected)
        severity[name] = {
            "assertions": len(selected),
            "passed_assertions": selected_passed,
            "pass_rate": round(selected_passed / len(selected), 4) if selected else None,
            "failures": sum(grade["verdict"] == "fail" for grade in selected),
            "uncertain": sum(grade["verdict"] == "uncertain" for grade in selected),
        }
    return {
        "graded_runs": len(gradings),
        "passed_runs": sum(grading.get("passed") is True for grading in gradings),
        "assertions": len(assertions),
        "passed_assertions": passed,
        "assertion_pass_rate": round(passed / len(assertions), 4)
        if assertions
        else None,
        "critical_failures": sum(
            grading.get("critical_failures", 0) for grading in gradings
        ),
        "severity": severity,
    }
