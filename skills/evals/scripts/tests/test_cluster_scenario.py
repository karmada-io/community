import unittest

from run_cluster_scenario import evaluate


class ClusterScenariosTest(unittest.TestCase):
    def test_requires_country_label_and_cluster_region_and_zones(self):
        result = evaluate(
            {
                "id": "countries",
                "minimumCountries": 2,
                "countryLabel": "topology.example.io/country",
                "clusters": [
                    {
                        "name": "seoul-a",
                        "labels": {"topology.example.io/country": "kr"},
                        "fields": {"region": "seoul", "zones": ["a"]},
                    },
                    {"name": "tokyo-a", "fields": {"region": "tokyo", "zones": ["a"]}},
                ],
            }
        )
        self.assertFalse(result["valid"])
        self.assertIn("tokyo-a: missing country label", result["findings"])


if __name__ == "__main__":
    unittest.main()
