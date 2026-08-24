import json
import unittest
from pathlib import Path

from run_cluster_scenario import evaluate as evaluate_cluster
from run_placement_scenario import evaluate as evaluate_placement
from run_policy_scenario import evaluate as evaluate_policy
from run_propagation_scenario import evaluate as evaluate_propagation


SCENARIOS = Path(__file__).resolve().parents[2] / "scenarios"
EVALUATORS = {
    "multi-country": evaluate_cluster,
    "placement-explanation": evaluate_placement,
    "policy-generation": evaluate_policy,
    "policy-review": evaluate_policy,
    "propagation-debugging": evaluate_propagation,
}


class CheckedInFixtureRegressionTest(unittest.TestCase):
    def test_every_fixture_matches_its_expected_result(self):
        paths = sorted(SCENARIOS.glob("*/input.json"))
        self.assertTrue(paths, "at least one checked-in fixture is required")

        for path in paths:
            with self.subTest(fixture=path.relative_to(SCENARIOS)):
                data = json.loads(path.read_text(encoding="utf-8"))
                category = path.parent.name
                self.assertIn(category, EVALUATORS)
                self.assertIsInstance(data.get("expected"), dict)
                self.assertTrue(data["expected"], "fixture expected result is required")

                actual = EVALUATORS[category](data)
                for key, expected_value in data["expected"].items():
                    self.assertIn(key, actual)
                    self.assertEqual(expected_value, actual[key])


if __name__ == "__main__":
    unittest.main()
