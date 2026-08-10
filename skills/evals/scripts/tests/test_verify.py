import tempfile
import unittest
from pathlib import Path

from verify import EVALUATION_SCENARIOS, validate_scenarios


class VerifyScenariosTest(unittest.TestCase):
    def test_missing_scenario_root_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "scenarios"
            self.assertEqual(
                [f"{root}: missing scenario directory"], validate_scenarios(root)
            )

    def test_missing_expected_scenario_is_reported_without_crashing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in EVALUATION_SCENARIOS[1:]:
                scenario = root / name
                scenario.mkdir()
                (scenario / "README.md").write_text("scenario\n", encoding="utf-8")
                (scenario / "input.json").write_text(
                    '{"expected": {}}\n', encoding="utf-8"
                )

            missing = root / EVALUATION_SCENARIOS[0]
            errors = validate_scenarios(root)
            self.assertIn(f"{missing}: missing scenario directory", errors)


if __name__ == "__main__":
    unittest.main()
