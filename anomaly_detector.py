"""Train and apply an Isolation Forest to generated baseline traffic."""
import numpy as np
from sklearn.ensemble import IsolationForest
from data_generator import FEATURES, generate_traffic


def classification_metrics(truth, predictions):
    """Summarize binary labels (0=normal, 1=anomaly) against detector predictions."""
    truth = np.asarray(truth, dtype=int)
    predictions = np.asarray(predictions, dtype=int)
    if len(truth) != len(predictions):
        raise ValueError("truth and predictions must have the same number of records")

    true_positive = int(((truth == 1) & (predictions == 1)).sum())
    false_negative = int(((truth == 1) & (predictions == 0)).sum())
    true_negative = int(((truth == 0) & (predictions == 0)).sum())
    false_positive = int(((truth == 0) & (predictions == 1)).sum())
    positive_count = true_positive + false_negative
    normal_count = true_negative + false_positive
    return {
        "normal_records": normal_count,
        "anomalous_records": positive_count,
        "true_negatives": true_negative,
        "false_positives": false_positive,
        "false_negatives": false_negative,
        "true_positives": true_positive,
        "detection_rate": true_positive / positive_count if positive_count else None,
        "false_positive_rate": false_positive / normal_count if normal_count else None,
    }


def train_detector(seed: int = 42):
    baseline = generate_traffic(rows=1500, seed=seed)
    baseline = baseline[baseline["scenario"] == "Normal"]
    model = IsolationForest(n_estimators=160, contamination=0.08, random_state=seed)
    model.fit(baseline[FEATURES])
    return model


def score_traffic(model, traffic):
    result = traffic.copy()
    result["anomaly_score"] = model.decision_function(result[FEATURES])
    result["detected_anomaly"] = (model.predict(result[FEATURES]) == -1).astype(int)
    result["detection"] = result["detected_anomaly"].map({0: "Normal", 1: "Anomaly"})
    return result
