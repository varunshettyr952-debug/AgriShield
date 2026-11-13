"""Unit tests for truth_table.py. Run: python -m unittest -v"""

import unittest
from truth_table import evaluate_rules


class TestTruthTable(unittest.TestCase):

    def setUp(self):
        self.data = {
            "N": 10, "P": 10, "K": 10,
            "Soil_pH": 5.0, "Temp": 36,
            "Humidity": 90, "Moisture": 10,
            "water_depletion": 0.80,
            "N_REQUIREMENT_CONFIRMED": True,
            "P_REQUIREMENT_CONFIRMED": True,
            "K_REQUIREMENT_CONFIRMED": True,
            "IRRIGATION_REQUIRED": True,
            "WATERLOGGING_RISK": True,
            "ACIDITY_CONFIRMED": True,
            "ALKALINITY_CONFIRMED": True,
            "DISEASE_CONFIRMED": True,
            "REGISTERED_TREATMENT_AVAILABLE": True,
        }
        self.thresholds = {
            "N_CRITICAL": 20, "P_CRITICAL": 20, "K_CRITICAL": 20,
            "RAW_THRESHOLD": 0.50, "M_WATERLOGGING": 70,
            "PH_MIN_CROP": 5.5, "PH_MAX_CROP": 7.0,
            "T_MAX_CROP": 34, "M_STRESS_CROP": 20,
            "H_DISEASE_THRESHOLD": 80,
            "T_MIN_PATHOGEN": 20, "T_MAX_PATHOGEN": 30,
        }

    def test_all_ten_rules_return_a_result(self):
        results = evaluate_rules(self.data, self.thresholds)
        self.assertEqual(len(results), 10)
        self.assertEqual(
            [item["rule"] for item in results],
            [f"R{i}" for i in range(1, 11)]
        )

    def test_rules_that_match_return_true(self):
        results = evaluate_rules(self.data, self.thresholds)
        statuses = {item["rule"]: item["status"] for item in results}
        expected_true = {"R1", "R2", "R3", "R4", "R6", "R8", "R10"}
        for rule in expected_true:
            self.assertEqual(statuses[rule], "TRUE", rule)

    def test_r7_false_when_ph_is_not_above_maximum(self):
        results = evaluate_rules(self.data, self.thresholds)
        status = next(item["status"] for item in results if item["rule"] == "R7")
        self.assertEqual(status, "FALSE")

    def test_r9_false_when_temperature_is_outside_pathogen_range(self):
        results = evaluate_rules(self.data, self.thresholds)
        status = next(item["status"] for item in results if item["rule"] == "R9")
        self.assertEqual(status, "FALSE")

    def test_missing_required_input_returns_unknown(self):
        incomplete_data = dict(self.data)
        del incomplete_data["N"]
        results = evaluate_rules(incomplete_data, self.thresholds)
        status = next(item["status"] for item in results if item["rule"] == "R1")
        self.assertEqual(status, "UNKNOWN")

    def test_missing_threshold_returns_unknown(self):
        incomplete_thresholds = dict(self.thresholds)
        del incomplete_thresholds["RAW_THRESHOLD"]
        results = evaluate_rules(self.data, incomplete_thresholds)
        status = next(item["status"] for item in results if item["rule"] == "R4")
        self.assertEqual(status, "UNKNOWN")

    def test_false_confirmation_flag_prevents_rule_activation(self):
        data = dict(self.data)
        data["N_REQUIREMENT_CONFIRMED"] = False
        results = evaluate_rules(data, self.thresholds)
        status = next(item["status"] for item in results if item["rule"] == "R1")
        self.assertEqual(status, "FALSE")

    def test_missing_boolean_flag_returns_unknown(self):
        data = dict(self.data)
        del data["DISEASE_CONFIRMED"]
        results = evaluate_rules(data, self.thresholds)
        status = next(item["status"] for item in results if item["rule"] == "R10")
        self.assertEqual(status, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
