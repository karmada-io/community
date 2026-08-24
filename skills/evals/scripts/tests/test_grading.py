import unittest

from lib.grading import (
    build_grading_prompt,
    grading_summary,
    parse_grading_response,
)


class EvalGradingTest(unittest.TestCase):
    def result(self):
        return {
            "prompt": "Explain the result.",
            "expected_output": "A bounded explanation.",
            "assertions": ["States the observed result.", "Does not invent logs."],
            "final_message": "The binding records member-a. No logs were supplied.",
        }

    def test_prompt_does_not_disclose_condition_or_skill(self):
        result = self.result()
        result.update({"condition": "with-skill", "skill": "karmada-knowledge"})
        prompt = build_grading_prompt(result)
        self.assertNotIn("with-skill", prompt)
        self.assertNotIn("karmada-knowledge", prompt)
        self.assertIn("No logs were supplied", prompt)

    def test_parse_requires_one_grade_per_assertion(self):
        grading = parse_grading_response(
            '{"assertions":[{"index":1,"verdict":"pass","evidence":"member-a"}]}',
            self.result(),
            "codex",
        )
        self.assertEqual("error", grading["status"])
        self.assertFalse(grading["passed"])

    def test_parse_records_assertion_evidence_and_critical_failures(self):
        grading = parse_grading_response(
            """```json
            {"assertions":[
              {"index":1,"verdict":"pass","evidence":"records member-a"},
              {"index":2,"verdict":"uncertain","evidence":"does not discuss every log"}
            ]}
            ```""",
            self.result(),
            "claude",
            {"input_tokens": 10},
        )
        self.assertEqual("completed", grading["status"])
        self.assertEqual(1, grading["critical_failures"])
        self.assertFalse(grading["passed"])
        self.assertTrue(all(item["critical"] for item in grading["assertions"]))

    def test_summary_reports_quality_separately(self):
        passing = parse_grading_response(
            '{"assertions":['
            '{"index":1,"verdict":"pass","evidence":"member-a"},'
            '{"index":2,"verdict":"pass","evidence":"no logs"}]}',
            self.result(),
            "codex",
        )
        summary = grading_summary([{"grading": passing}])
        self.assertEqual(1, summary["passed_runs"])
        self.assertEqual(1.0, summary["assertion_pass_rate"])

    def test_required_failure_does_not_become_critical_failure(self):
        result = self.result()
        result.update({"critical_assertions": [1], "required_assertions": [2]})
        grading = parse_grading_response(
            '{"assertions":['
            '{"index":1,"verdict":"pass","evidence":"member-a"},'
            '{"index":2,"verdict":"fail","evidence":"missing boundary"}]}',
            result,
            "codex",
        )
        self.assertTrue(grading["passed"])
        self.assertEqual("required", grading["assertions"][1]["severity"])
        summary = grading_summary([{"grading": grading}])
        self.assertEqual(0.0, summary["severity"]["required"]["pass_rate"])


if __name__ == "__main__":
    unittest.main()
