import unittest

from run_placement_scenario import evaluate


class PlacementScenariosTest(unittest.TestCase):
    def test_readiness_does_not_imply_scheduler_rejection(self):
        result = evaluate(
            {
                "id": "placement",
                "requiredLabels": {"region": "us"},
                "clusters": [
                    {"name": "a", "ready": True, "labels": {"region": "us"}},
                    {"name": "b", "ready": False, "labels": {"region": "us"}},
                ],
                "bindingClusters": ["a"],
            }
        )
        self.assertEqual(["a", "b"], result["policyEligible"])
        self.assertEqual(["b"], result["unresolved"])
        self.assertEqual({"a": True, "b": False}, result["clusterReadiness"])
        self.assertFalse(result["historicalEvidenceComplete"])

    def test_keeps_explicit_runtime_rejection_separate(self):
        result = evaluate(
            {
                "id": "runtime-rejection",
                "requiredLabels": {"region": "us"},
                "clusters": [
                    {"name": "a", "labels": {"region": "us"}},
                    {"name": "b", "labels": {"region": "us"}},
                    {"name": "c", "labels": {"region": "eu"}},
                ],
                "bindingClusters": ["a"],
                "runtimeRejections": {
                    "b": ["scheduler event: untolerated taint"]
                },
                "historicalEvidenceComplete": True,
            }
        )
        self.assertEqual(
            {"c": ["label-mismatch:region"]}, result["policyIneligible"]
        )
        self.assertEqual(
            {"b": ["scheduler event: untolerated taint"]},
            result["observedRejected"],
        )
        self.assertEqual([], result["unresolved"])
        self.assertTrue(result["historicalEvidenceComplete"])


if __name__ == "__main__":
    unittest.main()
