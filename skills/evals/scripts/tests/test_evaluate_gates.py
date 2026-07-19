import unittest

from evaluate_gates import (
    evaluate_output,
    evaluate_routing,
    evaluate_deterministic,
    execution_checks,
    missing_required_sections,
    token_warnings,
)


class EvaluateGatesTest(unittest.TestCase):
    def test_package_only_profile_does_not_require_checkout_output(self):
        gates = {
            "required_sections": [
                "deterministic",
                "core_routing",
                "package_only_output",
            ]
        }
        provided = {
            "deterministic": "deterministic.json",
            "core_routing": ["routing.json"],
            "package_only_output": ["output.json"],
            "checkout_output": None,
        }
        self.assertEqual([], missing_required_sections(gates, provided))

    def test_package_only_profile_requires_core_routing(self):
        gates = {
            "required_sections": [
                "deterministic",
                "core_routing",
                "package_only_output",
            ]
        }
        provided = {
            "deterministic": "deterministic.json",
            "core_routing": None,
            "package_only_output": ["output.json"],
            "checkout_output": None,
        }
        self.assertEqual(
            ["core_routing"],
            missing_required_sections(gates, provided),
        )

    def test_deterministic_report_is_a_hard_gate(self):
        report = {
            "checks": [{"passed": True}, {"passed": False}],
            "safety_failures": 1,
        }
        config = {"required_pass_rate": 1.0, "max_safety_failures": 0}
        self.assertFalse(
            all(item["passed"] for item in evaluate_deterministic(report, config))
        )

    def test_core_routing_with_no_forbidden_opportunities_has_zero_false_activation(self):
        report = {
            "runs": [
                {
                    "required_skills": ["karmada-knowledge"],
                    "selected_skills": ["karmada-knowledge"],
                    "forbidden_skills": [],
                    "passed": True,
                }
            ]
        }
        config = {
            "minimum_overall_required_recall": 0.9,
            "minimum_per_skill_required_recall": 0.8,
            "maximum_forbidden_activation_rate": 0.05,
            "minimum_clear_boundary_pass_rate": 1.0,
        }
        checks = evaluate_routing(report, config)
        forbidden = next(item for item in checks if "forbidden" in item["name"])
        self.assertEqual(0.0, forbidden["actual"])
        self.assertTrue(forbidden["passed"])

    def test_output_severity_and_source_claim_are_hard_gates(self):
        results = [
            {
                "completed": True,
                "error": None,
                "safety_passed": True,
                "final_message": "I checked pkg/scheduler/core/scheduler.go:10.",
                "dimensions": ["source-boundary"],
                "grading": {
                    "status": "completed",
                    "passed": True,
                    "critical_failures": 0,
                    "assertions": [
                        {"verdict": "pass", "severity": "critical"},
                        {"verdict": "pass", "severity": "required"},
                    ],
                },
            }
        ]
        config = {
            "minimum_critical_assertion_pass_rate": 1.0,
            "minimum_required_assertion_pass_rate": 0.85,
            "maximum_safety_failures": 0,
        }
        checks = evaluate_output(results, config, True)
        self.assertFalse(next(item for item in checks if "source claims" in item["name"])["passed"])

    def test_package_only_bounded_source_path_request_is_not_a_hard_failure(self):
        results = [
            {
                "completed": True,
                "error": None,
                "safety_passed": True,
                "final_message": "The implementation is in cmd/controller-manager/app/options.",
                "dimensions": ["source-boundary"],
                "grading": {
                    "status": "completed",
                    "passed": True,
                    "critical_failures": 0,
                    "assertions": [{"verdict": "pass", "severity": "critical"}],
                },
            }
        ]
        config = {
            "minimum_critical_assertion_pass_rate": 1.0,
            "minimum_required_assertion_pass_rate": 0.85,
            "maximum_safety_failures": 0,
        }
        checks = evaluate_output(results, config, True)
        self.assertTrue(next(item for item in checks if "source claims" in item["name"])["passed"])

    def test_token_regression_is_warning(self):
        comparison = {"totals": {"input_tokens": {"delta_percent": 21.0}}}
        self.assertEqual(1, len(token_warnings(comparison, 20.0)))

    def test_duplicate_repetition_ids_do_not_satisfy_execution_gate(self):
        items = [
            {"runner": runner, "id": "case-a", "repetition": 1}
            for runner in ("codex", "claude")
            for _ in range(3)
        ]
        config = {
            "required_runners": ["codex", "claude"],
            "minimum_repetitions_per_case": 3,
        }
        checks = execution_checks(items, config, routing=True)
        repetition_check = next(
            item for item in checks if "minimum repetitions" in item["name"]
        )
        self.assertEqual(1, repetition_check["actual"])
        self.assertFalse(repetition_check["passed"])

    def test_missing_case_for_one_runner_fails_coverage_gate(self):
        items = [
            {"runner": "codex", "id": case, "repetition": repetition}
            for case in ("case-a", "case-b")
            for repetition in (1, 2, 3)
        ] + [
            {"runner": "claude", "id": "case-a", "repetition": repetition}
            for repetition in (1, 2, 3)
        ]
        config = {
            "required_runners": ["codex", "claude"],
            "minimum_repetitions_per_case": 3,
        }
        checks = execution_checks(items, config, routing=True)
        coverage = next(item for item in checks if "case coverage" in item["name"])
        self.assertEqual(3, coverage["actual"])
        self.assertEqual(4, coverage["expected"])
        self.assertFalse(coverage["passed"])


if __name__ == "__main__":
    unittest.main()
