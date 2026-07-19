import json
import tempfile
import unittest
from pathlib import Path

from run_routing_evals import build_report, classify, load_cases


class CrossSkillRoutingTest(unittest.TestCase):
    def result(self, expected, selected, response=None):
        return {
            "id": "route",
            "repetition": 1,
            "expected_skill": expected,
            "selected_skill": selected,
            "final_message": response if response is not None else (selected or "none"),
            "completed": True,
            "error": None,
            "activation_evidence": {"method": "model_output"},
            "usage": {"input_tokens": 1, "output_tokens": 1},
        }

    def test_exact_skill_passes(self):
        self.assertTrue(classify(self.result("karmada-search", "karmada-search"))["passed"])

    def test_adjacent_skill_fails(self):
        self.assertFalse(classify(self.result("karmada-search", "karmada-knowledge"))["passed"])

    def test_none_requires_exact_none(self):
        self.assertTrue(classify(self.result(None, None))["passed"])
        self.assertTrue(classify(self.result(None, None, "No skill applies"))["passed"])

    def test_report_computes_accuracy(self):
        report = build_report(
            "codex",
            "digest",
            [self.result("karmada-search", "karmada-search"), self.result(None, "karmada-knowledge")],
        )
        self.assertEqual(0.5, report["summary"]["accuracy"])
        self.assertFalse(report["passed"])

    def test_load_cases_validates_expected_skill(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "routing.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "cases": [
                            {"id": "none", "prompt": "plain", "expected_skill": None}
                        ],
                    }
                )
            )
            cases = load_cases(path)
            self.assertFalse(cases[0]["expected_trigger"])


if __name__ == "__main__":
    unittest.main()
