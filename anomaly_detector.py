"""Train and apply an Isolation Forest to generated baseline traffic."""
from sklearn.ensemble import IsolationForest
from data_generator import FEATURES, generate_traffic


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
