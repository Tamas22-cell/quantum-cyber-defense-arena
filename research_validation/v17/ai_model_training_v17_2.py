
"""
QUANTUM CYBER DEFENSE ARENA
V17.2 - AI MODEL TRAINING ENGINE

Isolation Forest anomaly detection on V17.1
Ethereum transaction features.

Research prototype:
- Unsupervised machine learning
- No verified threat labels
- No blockchain write operations
"""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import joblib
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:
    print("V17.2 DEPENDENCY ERROR:", exc)
    print("Install: python -m pip install numpy scikit-learn joblib")
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[2]
V17_DIR = ROOT / "research_validation" / "v17"

INPUT_FILE = V17_DIR / "training_features_v17_1.csv"
MODEL_FILE = V17_DIR / "isolation_forest_model_v17_2.joblib"
SCORES_FILE = V17_DIR / "anomaly_scores_v17_2.csv"
REPORT_FILE = V17_DIR / "ai_model_training_v17_2_results.json"

RANDOM_STATE = 42
MIN_SAMPLES = 10
N_ESTIMATORS = 200
CONTAMINATION = "auto"


def load_training_data():
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            f"V17.1 input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        features = reader.fieldnames or []
        rows = list(reader)

    if not features:
        raise ValueError("Input CSV has no feature columns.")

    if len(features) != len(set(features)):
        raise ValueError("Duplicate feature names detected.")

    if len(rows) < MIN_SAMPLES:
        raise ValueError(
            f"At least {MIN_SAMPLES} rows required; "
            f"found {len(rows)}."
        )

    values = []

    for row_number, row in enumerate(rows, start=2):
        numeric_row = []

        for feature in features:
            raw = row.get(feature)

            if raw is None or not str(raw).strip():
                numeric_row.append(float("nan"))
                continue

            try:
                value = float(raw)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid number at CSV row {row_number}, "
                    f"column '{feature}': {raw}"
                ) from exc

            if math.isinf(value):
                raise ValueError(
                    f"Infinite value at row {row_number}, "
                    f"column '{feature}'."
                )

            numeric_row.append(value)

        values.append(numeric_row)

    data = np.asarray(values, dtype=np.float64)

    if data.ndim != 2:
        raise ValueError("Training data must be two-dimensional.")

    if data.shape[1] == 0:
        raise ValueError("No features available.")

    if np.any(np.all(np.isnan(data), axis=0)):
        raise ValueError(
            "At least one feature contains only missing values."
        )

    return features, data


def create_model():
    return Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "detector",
                IsolationForest(
                    n_estimators=N_ESTIMATORS,
                    contamination=CONTAMINATION,
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def save_scores(predictions, scores, decisions):
    with SCORES_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow(
            [
                "sample_index",
                "anomaly_score",
                "decision_function",
                "is_anomaly",
            ]
        )

        for index, (prediction, score, decision) in enumerate(
            zip(predictions, scores, decisions),
            start=1,
        ):
            writer.writerow(
                [
                    index,
                    round(float(score), 8),
                    round(float(decision), 8),
                    int(prediction == -1),
                ]
            )


def train():
    print("=" * 66)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V17.2 - AI MODEL TRAINING ENGINE")
    print("=" * 66)

    features, data = load_training_data()

    print(f"INPUT: {INPUT_FILE}")
    print(f"SAMPLES: {data.shape[0]}")
    print(f"FEATURES: {data.shape[1]}")
    print("MODEL: Isolation Forest")
    print()

    model = create_model()
    model.fit(data)

    predictions = model.predict(data)

    # Higher anomaly_score means more unusual.
    raw_scores = model.score_samples(data)
    anomaly_scores = -raw_scores
    decisions = model.decision_function(data)

    anomaly_count = int(np.sum(predictions == -1))
    normal_count = int(np.sum(predictions == 1))

    if not (
        np.all(np.isfinite(anomaly_scores))
        and np.all(np.isfinite(decisions))
    ):
        raise ValueError("Model returned non-finite scores.")

    # Save the preprocessing and detector together.
    joblib.dump(
        {
            "pipeline": model,
            "feature_names": features,
            "version": "V17.2",
            "random_state": RANDOM_STATE,
        },
        MODEL_FILE,
    )

    save_scores(
        predictions,
        anomaly_scores,
        decisions,
    )

    # Training-set-only descriptive statistics.
    # Not an out-of-sample accuracy evaluation.
    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V17.2",
        "module": "AI Model Training Engine",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "MODEL_TRAINING_PASS",
        "model": "IsolationForest",
        "model_type": "unsupervised_anomaly_detection",
        "dataset": str(INPUT_FILE.relative_to(ROOT)),
        "samples": int(data.shape[0]),
        "feature_count": len(features),
        "feature_names": features,
        "parameters": {
            "n_estimators": N_ESTIMATORS,
            "contamination": CONTAMINATION,
            "random_state": RANDOM_STATE,
        },
        "training_set_results": {
            "anomalies": anomaly_count,
            "normal": normal_count,
            "anomaly_percentage": round(
                100 * anomaly_count / len(data),
                2,
            ),
            "mean_anomaly_score": round(
                float(np.mean(anomaly_scores)),
                8,
            ),
            "max_anomaly_score": round(
                float(np.max(anomaly_scores)),
                8,
            ),
            "min_anomaly_score": round(
                float(np.min(anomaly_scores)),
                8,
            ),
        },
        "outputs": {
            "model": str(MODEL_FILE.relative_to(ROOT)),
            "scores": str(SCORES_FILE.relative_to(ROOT)),
            "report": str(REPORT_FILE.relative_to(ROOT)),
        },
        "verified_threat_labels": False,
        "classification_accuracy_available": False,
        "out_of_sample_evaluation": False,
        "limitations": [
            "Anomalies are not confirmed cyberattacks.",
            "Scores are calculated on the training dataset.",
            "No independent test set is evaluated.",
            "Small samples can produce unstable findings.",
            "Temporal and cross-block validation are needed.",
        ],
    }

    with REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            report,
            handle,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

    print(f"NORMAL TRANSACTIONS: {normal_count}")
    print(f"STATISTICAL ANOMALIES: {anomaly_count}")
    print(
        "ANOMALY PERCENTAGE: "
        f"{report['training_set_results']['anomaly_percentage']}%"
    )

    if len(data) < 100:
        print(
            "WARNING: Small research dataset; "
            "results require further validation."
        )

    print()
    print(f"MODEL SAVED: {MODEL_FILE}")
    print(f"SCORES SAVED: {SCORES_FILE}")
    print(f"REPORT SAVED: {REPORT_FILE}")
    print()
    print("V17.2 RESULT: MODEL_TRAINING_PASS")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(train())
    except Exception as exc:
        print()
        print(
            f"V17.2 FAILED: "
            f"{type(exc).__name__}: {exc}"
        )
        sys.exit(1)
