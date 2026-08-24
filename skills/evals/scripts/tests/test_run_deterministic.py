import tempfile
import unittest
from pathlib import Path

from run_deterministic import write_report


class RunDeterministicEvalsTest(unittest.TestCase):
    def test_write_report_preserves_machine_and_human_results(self):
        report = {
            "schema_version": 1,
            "passed": True,
            "safety_failures": 0,
            "checks": [
                {
                    "name": "scenario tests",
                    "passed": True,
                    "test_count": 4,
                    "duration_seconds": 0.1,
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deterministic.json"
            write_report(path, report)
            self.assertIn('"passed": true', path.read_text(encoding="utf-8"))
            self.assertIn("| scenario tests | 4 |", path.with_suffix(".md").read_text())


if __name__ == "__main__":
    unittest.main()
