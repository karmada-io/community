#!/usr/bin/env python3
"""Run deterministic Agent Skills validation and preserve machine-readable evidence."""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

TEST_COUNT_RE = re.compile(r"Ran (\d+) tests?")


def run_check(
    name: str, command: list[str], cwd: Path, env: Optional[dict] = None
) -> dict:
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    output = completed.stdout + completed.stderr
    match = TEST_COUNT_RE.search(output)
    return {
        "name": name,
        "command": command,
        "passed": completed.returncode == 0,
        "exit_code": completed.returncode,
        "duration_seconds": round(time.monotonic() - started, 3),
        "test_count": int(match.group(1)) if match else None,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Deterministic Evaluation",
        "",
        f"Overall: **{'PASS' if report['passed'] else 'FAIL'}**",
        "",
        "| Check | Tests | Seconds | Result |",
        "|---|---:|---:|---|",
    ]
    for item in report["checks"]:
        lines.append(
            f"| {item['name']} | {item['test_count'] or '-'} | "
            f"{item['duration_seconds']} | {'PASS' if item['passed'] else 'FAIL'} |"
        )
    lines.extend(["", f"Safety failures: `{report['safety_failures']}`", ""])
    path.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    scripts = root / "skills/evals/scripts"
    base_env = os.environ.copy()
    checks = [
        run_check(
            "script unit and scenario tests",
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                str(scripts / "tests"),
                "-p",
                "test_*.py",
            ],
            root,
            dict(base_env, PYTHONPATH=str(scripts)),
        ),
        run_check(
            "collection validator",
            [sys.executable, str(scripts / "verify.py")],
            root,
            base_env,
        ),
    ]
    report = {
        "schema_version": 1,
        "passed": all(item["passed"] for item in checks),
        "safety_failures": 0 if all(item["passed"] for item in checks) else 1,
        "checks": checks,
    }
    write_report(args.output, report)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
