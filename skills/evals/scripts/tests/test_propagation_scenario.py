import unittest

from run_propagation_scenario import evaluate


class PropagationScenariosTest(unittest.TestCase):
    def test_stops_at_first_missing_stage(self):
        result = evaluate(
            {
                "id": "debug",
                "evidence": {
                    "policyClaim": "ok",
                    "binding": "ok",
                    "scheduling": "missing",
                },
            }
        )
        self.assertEqual("scheduling", result["firstProblemStage"])
        self.assertEqual("missing", result["state"])


if __name__ == "__main__":
    unittest.main()
