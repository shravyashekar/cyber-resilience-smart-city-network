import unittest

from anomaly_detector import classification_metrics, score_traffic, train_detector
from data_generator import SERVICES, generate_traffic
from incident_triage import triage_alerts
from simulation import run_simulation


class DetectionDrivenResponseTests(unittest.TestCase):
    def test_incident_records_belong_to_target_service(self):
        traffic = generate_traffic(rows=300, seed=5, scenario="DoS", target_service="Water Supply")
        attacks = traffic[traffic["is_anomaly"] == 1]
        self.assertGreater(len(attacks), 0)
        self.assertEqual(set(attacks["service"]), {"Water Supply"})
        self.assertGreater(traffic.loc[traffic["is_anomaly"] == 0, "service"].nunique(), 1)

    def test_detector_is_good_but_not_perfect(self):
        missed = 0
        for seed in range(5):
            model = train_detector(seed)
            for scenario in ("DoS", "Malware-like"):
                scored = score_traffic(model, generate_traffic(240, seed, scenario, target_service="Hospital"))
                metrics = classification_metrics(scored["is_anomaly"], scored["detected_anomaly"])
                self.assertGreater(metrics["detection_rate"], 0.6)
                missed += metrics["false_negatives"]
        self.assertGreater(missed, 0, "synthetic attacks should not all be trivially separable")

    def test_triage_infers_the_simulated_threat(self):
        for seed in range(4):
            model = train_detector(seed)
            for scenario in ("DoS", "Port Scan", "Malware-like"):
                for service in SERVICES:
                    with self.subTest(seed=seed, scenario=scenario, service=service):
                        scored = score_traffic(model, generate_traffic(240, seed, scenario, target_service=service))
                        triage = triage_alerts(scored, service)
                        self.assertTrue(triage["incident_detected"])
                        self.assertEqual(triage["inferred_threat"], scenario)

    def test_normal_day_false_alarms_do_not_trigger_response(self):
        for seed in range(6):
            for service in SERVICES:
                with self.subTest(seed=seed, service=service):
                    traffic, _before, _after, actions = run_simulation("Normal", service, seed=seed)
                    self.assertFalse(actions["triage"]["incident_detected"])
                    self.assertEqual(actions["response_mode"], "No action")

    def test_response_follows_detected_threat(self):
        _traffic, _before, _after, actions = run_simulation("DoS", "Hospital", seed=17)
        self.assertEqual(actions["detected_threat"], "DoS")
        self.assertEqual(actions["response_mode"], "Failover")
        self.assertTrue(actions["critical_services_reachable"])


if __name__ == "__main__":
    unittest.main()
