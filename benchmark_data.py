"""Load and evaluate a labeled public network-flow CSV, such as CICIoT2023."""
from io import BytesIO

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.model_selection import train_test_split

MAX_ROWS = 50000
LABEL_NAMES = {"label", "class", "attack", "category", "target", "traffic label"}


def preview_csv(file_bytes, max_rows=MAX_ROWS):
    """Read a bounded CSV sample and identify likely label columns."""
    frame = pd.read_csv(BytesIO(file_bytes), nrows=max_rows, low_memory=False)
    if frame.empty:
        raise ValueError("The CSV contains no rows.")
    labels = [column for column in frame.columns
              if str(column).strip().casefold() in LABEL_NAMES]
    return frame, labels


def evaluate_labeled_csv(frame, label_column, normal_label, seed=42):
    """Train on benign rows and evaluate on a stratified held-out sample."""
    if label_column not in frame.columns:
        raise ValueError("Choose a label column that exists in the CSV.")
    labels = frame[label_column].astype("string").str.strip()
    valid = labels.notna()
    frame = frame.loc[valid].reset_index(drop=True)
    labels = labels.loc[valid].reset_index(drop=True)
    normal_mask = labels.str.casefold() == str(normal_label).strip().casefold()
    truth = (~normal_mask).astype(int).to_numpy()
    if len(np.unique(truth)) != 2 or min(np.bincount(truth)) < 2:
        raise ValueError("The selected sample needs at least two normal and two attack rows.")

    features = frame.drop(columns=[label_column]).select_dtypes(include=[np.number]).copy()
    features = features.replace([np.inf, -np.inf], np.nan)
    features = features.loc[:, features.notna().any()]
    if features.empty:
        raise ValueError("No numeric traffic features were found beside the label column.")
    features = features.fillna(features.median()).fillna(0)
    features = features.loc[:, features.nunique(dropna=False) > 1]
    if features.empty:
        raise ValueError("The selected numeric features are all constant.")

    indices = np.arange(len(frame))
    train_ids, test_ids = train_test_split(
        indices, test_size=0.25, random_state=seed, stratify=truth
    )
    normal_train_ids = train_ids[truth[train_ids] == 0]
    if len(normal_train_ids) < 10:
        raise ValueError("The sample needs at least 10 normal training rows.")

    model = IsolationForest(n_estimators=160, contamination=0.05, random_state=seed)
    model.fit(features.iloc[normal_train_ids])
    test_features = features.iloc[test_ids].reset_index(drop=True)
    predictions = (model.predict(test_features) == -1).astype(int)
    test_truth = truth[test_ids]
    scores = model.decision_function(test_features)

    results = test_features.copy()
    results["source_label"] = labels.iloc[test_ids].astype(str).to_numpy()
    results["is_anomaly"] = test_truth
    results["detected_anomaly"] = predictions
    results["detection"] = np.where(predictions == 1, "Anomaly", "Normal")
    results["anomaly_score"] = scores
    matrix = confusion_matrix(test_truth, predictions, labels=[0, 1])
    metrics = {
        "accuracy": float(accuracy_score(test_truth, predictions)),
        "precision": float(precision_score(test_truth, predictions, zero_division=0)),
        "recall": float(recall_score(test_truth, predictions, zero_division=0)),
        "f1": float(f1_score(test_truth, predictions, zero_division=0)),
        "false_positives": int(matrix[0, 1]),
        "false_negatives": int(matrix[1, 0]),
        "true_negatives": int(matrix[0, 0]),
        "true_positives": int(matrix[1, 1]),
        "rows_loaded": int(len(frame)),
        "rows_evaluated": int(len(test_ids)),
        "feature_count": int(features.shape[1]),
        "features": list(features.columns),
        "label_column": label_column,
        "normal_label": str(normal_label),
    }
    return results, metrics
