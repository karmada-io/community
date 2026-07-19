import unittest

from run_policy_scenario import evaluate


class PolicyScenariosTest(unittest.TestCase):
    def test_propagation_policy_empty_selector_is_invalid(self):
        for kind in ("PropagationPolicy", "ClusterPropagationPolicy"):
            with self.subTest(kind=kind):
                result = evaluate(
                    {
                        "id": f"{kind}-empty-selector",
                        "policy": {
                            "kind": kind,
                            "resourceSelectors": [],
                        },
                    }
                )
                self.assertFalse(result["valid"])
                self.assertIn(
                    "spec.resourceSelectors: must not be empty",
                    result["findings"],
                )

    def test_propagation_policy_null_selector_is_invalid(self):
        for kind in ("PropagationPolicy", "ClusterPropagationPolicy"):
            with self.subTest(kind=kind):
                result = evaluate(
                    {
                        "id": f"{kind}-null-selector",
                        "policy": {
                            "kind": kind,
                            "resourceSelectors": None,
                        },
                    }
                )
                self.assertFalse(result["valid"])
                self.assertIn(
                    "spec.resourceSelectors: must not be empty",
                    result["findings"],
                )

    def test_override_policy_empty_or_omitted_selector_is_allowed_but_risky(self):
        for kind in ("OverridePolicy", "ClusterOverridePolicy"):
            for selector_value in ([], None):
                with self.subTest(kind=kind, selector_value=selector_value):
                    policy = {
                        "kind": kind,
                        "namespace": "team-a",
                    }
                    if selector_value is not None:
                        policy["resourceSelectors"] = selector_value
                    result = evaluate(
                        {
                            "id": f"{kind}-empty-selector",
                            "policy": policy,
                        }
                    )
                    self.assertTrue(result["valid"])
                    self.assertIn(
                        "spec.resourceSelectors: empty selector matches all resources in scope",
                        result["warnings"],
                    )

    def test_override_policy_null_selector_is_allowed_but_risky(self):
        for kind in ("OverridePolicy", "ClusterOverridePolicy"):
            with self.subTest(kind=kind):
                result = evaluate(
                    {
                        "id": f"{kind}-null-selector",
                        "policy": {
                            "kind": kind,
                            "namespace": "team-a",
                            "resourceSelectors": None,
                        },
                    }
                )
                self.assertTrue(result["valid"])
                self.assertIn(
                    "spec.resourceSelectors: empty selector matches all resources in scope",
                    result["warnings"],
                )

    def test_reports_namespace_and_preemption_findings(self):
        result = evaluate(
            {
                "id": "bad",
                "policy": {
                    "kind": "PropagationPolicy",
                    "namespace": "team-a",
                    "preemption": "Always",
                    "resourceSelectors": [
                        {"kind": "Deployment", "namespace": "team-b"}
                    ],
                },
            }
        )
        self.assertFalse(result["valid"])
        self.assertEqual(2, len(result["findings"]))


if __name__ == "__main__":
    unittest.main()
