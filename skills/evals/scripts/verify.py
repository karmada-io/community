#!/usr/bin/env python3
"""Validate the package-only Karmada Agent Skills collection."""

import json
import re
import sys
from pathlib import Path

COLLECTION = Path(__file__).resolve().parents[2]
USER_SKILLS = (
    "karmada-knowledge",
    "karmada-create-policy",
    "karmada-audit-policy",
    "karmada-explain-placement",
    "karmada-debug-propagation",
    "karmada-search",
    "karmada-controller-manager",
)
EVALUATION_SCENARIOS = (
    "multi-country",
    "placement-explanation",
    "policy-generation",
    "policy-review",
    "propagation-debugging",
)
PACKAGE_ONLY_DIMENSIONS = {
    "standalone-utility",
    "source-boundary",
    "runtime-evidence",
    "mutation-safety",
    "missing-input",
    "conflicting-evidence",
    "environment-boundary",
    "version-boundary",
}
LOCAL_REFERENCE_RE = re.compile(r"`(references/[^`]+)`")
ABSOLUTE_LOCAL_PATH_RE = re.compile(r"/(?:Users|tmp|private/var|var/folders)/")
CLIENT_SPECIFIC_RE = re.compile(r"\b(?:Codex|Claude(?: Code)?|OpenAI|Anthropic)\b", re.I)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except (OSError, json.JSONDecodeError) as error:
        return {}, [f"{path}: {error}"]


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening YAML frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("missing closing YAML frontmatter delimiter") from error
    values = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def validate_packaged_skill(package: Path, root: Path = None) -> list[str]:
    errors = []
    if package.is_symlink() or not package.is_dir():
        return [f"{package}: package must be a regular directory"]
    for path in package.rglob("*"):
        if path.is_symlink():
            errors.append(f"{package}: package contains symlink {path.relative_to(package)}")
    skill_file = package / "SKILL.md"
    if skill_file.is_symlink():
        return errors
    if not skill_file.is_file():
        return errors + [f"{package}: missing SKILL.md"]
    for path in [skill_file, *sorted((package / "references").rglob("*"))]:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if ABSOLUTE_LOCAL_PATH_RE.search(text):
            errors.append(f"{path}: contains a local absolute path")
        if CLIENT_SPECIFIC_RE.search(text):
            errors.append(f"{path}: runtime content must remain client-neutral")
    text = skill_file.read_text(encoding="utf-8")
    for reference in LOCAL_REFERENCE_RE.findall(text):
        target = (package / reference).resolve()
        try:
            target.relative_to(package.resolve())
        except ValueError:
            errors.append(f"{skill_file}: reference escapes package: {reference}")
            continue
        if not target.is_file():
            errors.append(f"{skill_file}: missing reference {reference}")
    return errors


def validate_package_only_output(path: Path) -> list[str]:
    data, errors = load_json(path)
    if errors:
        return errors
    if data.get("schema_version") != 2 or not isinstance(data.get("cases"), list):
        return [f"{path}: expected schema_version 2 and cases"]
    counts = {skill: 0 for skill in USER_SKILLS}
    dimensions = set()
    ids = set()
    for case in data["cases"]:
        case_id = case.get("id")
        skill = case.get("skill")
        location = f"{path}: {case_id or '<missing id>'}"
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            errors.append(f"{location}: invalid or duplicate id")
        ids.add(case_id)
        if skill not in counts:
            errors.append(f"{location}: unknown skill {skill}")
        else:
            counts[skill] += 1
        assertions = case.get("assertions")
        critical = case.get("critical_assertions")
        required = case.get("required_assertions")
        if not isinstance(assertions, list) or not assertions:
            errors.append(f"{location}: assertions are required")
            continue
        indexes = set(range(1, len(assertions) + 1))
        if not isinstance(critical, list) or not isinstance(required, list):
            errors.append(f"{location}: assertion severities are required")
        elif set(critical) & set(required) or not set(critical + required).issubset(indexes):
            errors.append(f"{location}: invalid assertion severity indexes")
        case_dimensions = case.get("dimensions")
        if not isinstance(case_dimensions, list) or not case_dimensions:
            errors.append(f"{location}: dimensions are required")
        else:
            dimensions.update(case_dimensions)
        safety = case.get("safety")
        required_safety = ("artifact_allowed", "live_mutation_command_allowed")
        if not isinstance(safety, dict) or any(type(safety.get(key)) is not bool for key in required_safety):
            errors.append(f"{location}: complete boolean safety metadata is required")
    for skill, count in counts.items():
        if count < 3:
            errors.append(f"{path}: {skill} requires at least three cases")
    missing = PACKAGE_ONLY_DIMENSIONS - dimensions
    if missing:
        errors.append(f"{path}: missing dimensions {', '.join(sorted(missing))}")
    return errors


def validate_gate(path: Path) -> list[str]:
    data, errors = load_json(path)
    if errors:
        return errors
    expected = ["deterministic", "core_routing", "package_only_output"]
    if data.get("profile") != "package-only" or data.get("required_sections") != expected:
        errors.append(f"{path}: package-only required_sections mismatch")
    execution = data.get("execution") or {}
    if execution.get("required_runners") != ["codex", "claude"]:
        errors.append(f"{path}: both Codex and Claude are required")
    if execution.get("minimum_repetitions_per_case") != 3:
        errors.append(f"{path}: three repetitions are required")
    return errors


def main() -> int:
    errors = []
    for legacy in ("examples", "fixtures", "scripts"):
        path = COLLECTION / legacy
        if path.exists():
            errors.append(f"{path}: evaluation support files must live under evals")
    actual = {path.name for path in COLLECTION.glob("karmada-*") if path.is_dir()}
    expected = set(USER_SKILLS)
    if actual != expected:
        errors.append(f"{COLLECTION}: skill set mismatch: expected {sorted(expected)}, found {sorted(actual)}")
    for skill in USER_SKILLS:
        package = COLLECTION / skill
        errors.extend(validate_packaged_skill(package))
        try:
            metadata = parse_frontmatter(package / "SKILL.md")
        except (OSError, ValueError) as error:
            errors.append(f"{package / 'SKILL.md'}: {error}")
            continue
        if set(metadata) != {"name", "description"}:
            errors.append(f"{package / 'SKILL.md'}: frontmatter must contain only name and description")
        if metadata.get("name") != skill:
            errors.append(f"{package / 'SKILL.md'}: name must match {skill}")
    evals = COLLECTION / "evals"
    cases = evals / "cases"
    expected_case_files = {"output.json", "routing.json"}
    actual_case_files = {path.name for path in cases.glob("*.json")}
    if actual_case_files != expected_case_files:
        errors.append(
            f"{cases}: case file mismatch: expected {sorted(expected_case_files)}, "
            f"found {sorted(actual_case_files)}"
        )
    trigger_files = {path.stem for path in (cases / "trigger").glob("*.json")}
    if trigger_files != set(USER_SKILLS):
        errors.append(
            f"{cases / 'trigger'}: trigger corpus mismatch: expected "
            f"{sorted(USER_SKILLS)}, found {sorted(trigger_files)}"
        )
    for path in sorted(cases.rglob("*.json")):
        _, json_errors = load_json(path)
        errors.extend(json_errors)

    scenario_root = evals / "scenarios"
    actual_scenarios = {path.name for path in scenario_root.iterdir() if path.is_dir()}
    if actual_scenarios != set(EVALUATION_SCENARIOS):
        errors.append(
            f"{scenario_root}: scenario set mismatch: expected "
            f"{sorted(EVALUATION_SCENARIOS)}, found {sorted(actual_scenarios)}"
        )
    for name in EVALUATION_SCENARIOS:
        scenario = scenario_root / name
        files = {path.name for path in scenario.iterdir() if path.is_file()}
        if files != {"README.md", "input.json"}:
            errors.append(
                f"{scenario}: expected README.md and input.json, found {sorted(files)}"
            )
        data, json_errors = load_json(scenario / "input.json")
        errors.extend(json_errors)
        if not json_errors and not isinstance(data.get("expected"), dict):
            errors.append(f"{scenario / 'input.json'}: expected result is required")

    errors.extend(validate_package_only_output(cases / "output.json"))
    errors.extend(validate_gate(evals / "gate.json"))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"Validated {len(USER_SKILLS)} self-contained Karmada skills and package-only gates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
