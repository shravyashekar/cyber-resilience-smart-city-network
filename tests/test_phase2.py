import unittest

import numpy as np
import pandas as pd

from anomaly_detector import (
    classification_metrics,
    score_traffic,
    train_detector,
)
from benchmark_data import evaluate_labeled_csv
from data_generator import FEATURES, generate_traffic
from network_topology import create_smart_city_network
from risk_assessment import assess_risk
from self_healing import respond
from simulation import run_simulation


class PhaseTwoTests(unittest.TestCase):
    def test_selected_attack_is_mixed_with_normal_records(self):
        traffic = generate_traffic(rows=400, seed=17, scenario="Malware-like")

        self.assertIn(0, traffic["is_anomaly"].values)
        self.assertIn(1, traffic["is_anomaly"].values)
        self.assertEqual(set(traffic["scenario"].unique()), {"Normal", "Malware-like"})
        self.assertAlmostEqual(traffic["is_anomaly"].mean(), 0.25, delta=0.06)

    def test_normal_scenario_contains_no_ground_truth_attacks(self):
        traffic = generate_traffic(rows=100, seed=17, scenario="Normal")

        self.assertEqual(int(traffic["is_anomaly"].sum()), 0)

    def test_scored_flags_match_isolation_forest_predictions(self):
        traffic = generate_traffic(rows=160, seed=17, scenario="DoS")
        model = train_detector(seed=17)

        scored = score_traffic(model, traffic)
        expected = (model.predict(traffic[FEATURES]) == -1).astype(int)

        np.testing.assert_array_equal(scored["detected_anomaly"].to_numpy(), expected)

    def test_scenario_runs_use_detector_predictions_for_metrics(self):
        for scenario, service in (
            ("Normal", "Hospital"),
            ("DoS", "Hospital"),
            ("Port Scan", "Water Supply"),
            ("Malware-like", "Public Display"),
        ):
            with self.subTest(scenario=scenario):
                traffic, _before, _after, actions = run_simulation(
                    scenario, service, rows=160, seed=17
                )
                metrics = classification_metrics(
                    traffic["is_anomaly"], traffic["detected_anomaly"]
                )

                self.assertEqual(
                    int(traffic["detected_anomaly"].sum()),
                    int((traffic["detection"] == "Anomaly").sum()),
                )
                self.assertEqual(
                    metrics["anomalous_records"], int(traffic["is_anomaly"].sum())
                )
                self.assertEqual(
                    metrics["true_positives"] + metrics["false_positives"],
                    int(traffic["detected_anomaly"].sum()),
                )
                self.assertIn(actions["response_mode"], (
                    "No action", "Failover", "Safe fallback", "Isolation", "Monitor"
                ))
                if scenario != "Normal":
                    self.assertGreater(metrics["anomalous_records"], 0)
                    self.assertGreater(metrics["normal_records"], 0)
                    predicted_rate = traffic["detected_anomaly"].mean()
                    self.assertGreater(predicted_rate, 0)
                    self.assertLess(predicted_rate, 1)

    def test_recovery_policy_uses_risk_and_service_tier(self):
        graph = create_smart_city_network()
        tier_one_risk = assess_risk("Critical", 1, 100)
        tier_two_risk = assess_risk("Critical", 2, 85)
        tier_three_risk = assess_risk("Critical", 3, 25)
        moderate_tier_one_risk = assess_risk("Low", 1, 100)
        low_risk = assess_risk("Low", 3, 25)

        _recovered, tier_one = respond(graph, "Hospital", "Critical", tier_one_risk)
        _recovered, tier_two = respond(graph, "Water Supply", "Critical", tier_two_risk)
        _recovered, tier_three = respond(graph, "Public Display", "Critical", tier_three_risk)
        _recovered, tier_one_fallback = respond(
            graph, "Hospital", "Low", moderate_tier_one_risk
        )
        _recovered, low_risk_action = respond(graph, "Public Display", "Low", low_risk)

        self.assertEqual(tier_one["response_mode"], "Failover")
        self.assertEqual(tier_two["response_mode"], "Safe fallback")
        self.assertEqual(tier_three["response_mode"], "Isolation")
        self.assertEqual(tier_one_fallback["response_mode"], "Safe fallback")
        self.assertTrue(tier_one_fallback["critical_services_reachable"])
        self.assertEqual(low_risk_action["response_mode"], "Monitor")

    def test_metric_rates_are_computed_from_ground_truth(self):
        metrics = classification_metrics([0, 0, 1, 1], [1, 0, 1, 0])

        self.assertEqual(metrics["detection_rate"], 0.5)
        self.assertEqual(metrics["false_positive_rate"], 0.5)

    def test_labeled_csv_evaluation_exposes_ground_truth_rates(self):
        rng = np.random.default_rng(23)
        frame = pd.DataFrame({
            "packet_rate": np.concatenate((rng.normal(100, 8, 100), rng.normal(500, 20, 100))),
            "cpu_load": np.concatenate((rng.normal(30, 5, 100), rng.normal(85, 5, 100))),
            "label": ["Normal"] * 100 + ["Attack"] * 100,
        })

        evaluated, _benchmark_metrics = evaluate_labeled_csv(
            frame, "label", "Normal", seed=23
        )
        metrics = classification_metrics(
            evaluated["is_anomaly"], evaluated["detected_anomaly"]
        )

        self.assertEqual(
            metrics["normal_records"] + metrics["anomalous_records"],
            len(evaluated),
        )
        self.assertIsNotNone(metrics["detection_rate"])
        self.assertIsNotNone(metrics["false_positive_rate"])


if __name__ == "__main__":
    unittest.main()
