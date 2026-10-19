
"""
QUANTUM CYBER DEFENSE ARENA
V13.2 - REAL BLOCKCHAIN AI VALIDATION

Dataset: Elliptic Bitcoin Dataset

Models:
1. Classical Isolation Forest, 165 original features
2. Quantum State Fidelity Simulator, 4 PCA components
3. Hybrid agreement-based fusion

The original feature semantics are preserved.
The 4 quantum inputs are learned PCA components,
NOT fabricated Ethereum-specific features.

Preprocessing is fitted on training data only.
Chronological train/test separation is preserved.

This is exploratory research.
No quantum computational advantage is claimed.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.quantum_detection.quantum_detector import (
    QuantumAnomalyDetector,
)

from research_validation.v11.benchmark_v11 import (
    calculate_metrics,
    quantum_scores,
)


VERSION = "13.2.0"

HERE = Path(__file__).resolve().parent

DATA_DIR = HERE / "elliptic_processed"

TRAIN_FILE = DATA_DIR / "train_normal.parquet"
TEST_FILE = DATA_DIR / "test_labeled.parquet"

OUTPUT_FILE = (
    HERE / "elliptic_validation_v13_2_results.json"
)

SEED = 2026

MAX_TRAIN = 10000
MAX_TEST = 500

QUANTUM_COMPONENTS = 4

QUANTUM_THRESHOLD = 0.35

FEATURE_COLUMNS = [
    f"feature_{i:03d}"
    for i in range(1, 166)
]


def banner(text: str) -> None:
    print()
    print("=" * 68)
    print(text)
    print("=" * 68)


def check_files() -> None:
    for file in (TRAIN_FILE, TEST_FILE):
        if not file.is_file():
            raise FileNotFoundError(
                f"Missing prepared dataset:\n{file}\n"
                "Run elliptic_prepare_v13.py first."
            )


def load_data():
    banner("STEP 1 - LOADING REAL ELLIPTIC DATA")

    check_files()

    train = pd.read_parquet(TRAIN_FILE)
    test = pd.read_parquet(TEST_FILE)

    required = set(FEATURE_COLUMNS) | {
        "time_step",
        "label",
    }

    for name, frame in (
        ("train", train),
        ("test", test),
    ):
        missing = required - set(frame.columns)

        if missing:
            raise ValueError(
                f"Missing {name} columns: {sorted(missing)}"
            )

        if frame[FEATURE_COLUMNS].isna().any().any():
            raise ValueError(
                f"Missing numeric data in {name}"
            )

    if (train["label"] != 0).any():
        raise ValueError(
            "Training dataset must contain normal records only."
        )

    if int(train["time_step"].max()) >= int(
        test["time_step"].min()
    ):
        raise ValueError(
            "Chronological training/test overlap detected."
        )

    train = train.sample(
        n=min(len(train), MAX_TRAIN),
        random_state=SEED,
    )

    # Stratified sampling, retaining the real class proportions
    # as closely as the capped sample allows.
    if len(test) > MAX_TEST:
        from sklearn.model_selection import train_test_split

        sample, _ = train_test_split(
            test,
            train_size=MAX_TEST,
            random_state=SEED,
            stratify=test["label"],
        )

        test = sample

    y_test = test["label"].to_numpy(dtype=int)

    if set(np.unique(y_test)) != {0, 1}:
        raise ValueError(
            "Both normal and anomaly labels must occur in test."
        )

    X_train = train[FEATURE_COLUMNS].to_numpy(
        dtype=np.float64
    )

    X_test = test[FEATURE_COLUMNS].to_numpy(
        dtype=np.float64
    )

    if not (
        np.isfinite(X_train).all()
        and np.isfinite(X_test).all()
    ):
        raise ValueError("Non-finite feature values found.")

    print("Training normal records:", len(X_train))
    print("Test records:", len(X_test))
    print("Test normal:", int(np.sum(y_test == 0)))
    print("Test anomaly:", int(np.sum(y_test == 1)))
    print("Feature count:", len(FEATURE_COLUMNS))
    print(
        "Chronological train steps:",
        int(train["time_step"].min()),
        "-",
        int(train["time_step"].max()),
    )
    print(
        "Chronological test steps:",
        int(test["time_step"].min()),
        "-",
        int(test["time_step"].max()),
    )

    return X_train, X_test, y_test


def scale_features(
    X_train: np.ndarray,
    X_test: np.ndarray,
):
    banner("STEP 2 - TRAIN-ONLY PREPROCESSING")

    scaler = StandardScaler()

    train_scaled = scaler.fit_transform(X_train)
    test_scaled = scaler.transform(X_test)

    print("StandardScaler fitted on normal training data.")

    return train_scaled, test_scaled


def classical_detection(
    train_scaled: np.ndarray,
    test_scaled: np.ndarray,
):
    banner("STEP 3 - CLASSICAL ISOLATION FOREST")

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=SEED,
        n_jobs=-1,
    )

    started = perf_counter()

    model.fit(train_scaled)

    prediction = model.predict(test_scaled)

    seconds = perf_counter() - started

    binary = (prediction == -1).astype(int)

    print(
        "Classical model completed:",
        round(seconds, 2),
        "seconds",
    )

    return binary, seconds


def quantum_detection(
    train_scaled: np.ndarray,
    test_scaled: np.ndarray,
):
    banner("STEP 4 - QUANTUM PCA ADAPTATION")

    pca = PCA(
        n_components=QUANTUM_COMPONENTS,
        random_state=SEED,
    )

    # PCA is trained on the normal training set only.
    train_pca = pca.fit_transform(train_scaled)
    test_pca = pca.transform(test_scaled)

    # Map each PCA component to the simulator's [0,1]
    # input range using training-set percentiles only.
    lower = np.percentile(train_pca, 1, axis=0)
    upper = np.percentile(train_pca, 99, axis=0)

    denominator = np.maximum(
        upper - lower,
        1e-12,
    )

    quantum_inputs = np.clip(
        (test_pca - lower) / denominator,
        0.0,
        1.0,
    )

    detector = QuantumAnomalyDetector(
        threshold=QUANTUM_THRESHOLD
    )

    # V11 quantum_scores assumes the legacy V11 feature
    # ordering. Here the four PCA coordinates are passed
    # directly to the detector instead.
    predictions = []
    scores = []

    started = perf_counter()

    for index, row in enumerate(quantum_inputs, start=1):
        result = detector.detect(
            [float(value) for value in row]
        )

        predictions.append(
            int(result.classification == "ANOMALY")
        )

        scores.append(float(result.anomaly_score))

        if index % 100 == 0:
            print(
                f"Quantum evaluations: {index}/{len(quantum_inputs)}",
                flush=True,
            )

    seconds = perf_counter() - started

    print(
        "Quantum simulation completed:",
        round(seconds, 2),
        "seconds",
    )

    return (
        np.asarray(predictions, dtype=int),
        np.asarray(scores, dtype=float),
        seconds,
        {
            "method": "PCA",
            "components": QUANTUM_COMPONENTS,
            "explained_variance_ratio": [
                round(float(value), 6)
                for value in pca.explained_variance_ratio_
            ],
            "normalization": (
                "Training-only 1st/99th percentile mapping "
                "to [0,1], with clipping"
            ),
            "feature_semantics": (
                "PCA coordinates, not transaction-value "
                "or gas-related quantities"
            ),
        },
    )


def hybrid_detection(
    classical_pred: np.ndarray,
    quantum_pred: np.ndarray,
):
    banner("STEP 5 - HYBRID FUSION")

    agree = classical_pred == quantum_pred

    hybrid = np.where(
        agree,
        classical_pred,
        -1,
    )

    # REVIEW is not counted as a confirmed anomaly.
    binary = (hybrid == 1).astype(int)

    review_count = int(np.sum(~agree))

    review_rate = float(np.mean(~agree))

    print("Review decisions:", review_count)
    print("Review rate:", f"{review_rate * 100:.2f}%")

    return binary, review_count, review_rate


def false_positive_rate(metrics: dict) -> float:
    fp = metrics["fp"]
    tn = metrics["tn"]

    if fp + tn == 0:
        return 0.0

    return fp / (fp + tn)


def print_model_results(name: str, metrics: dict):
    print()
    print(name.upper())
    print("-" * 42)

    print(
        f"Precision: {metrics['precision'] * 100:.2f}%"
    )
    print(
        f"Recall:    {metrics['recall'] * 100:.2f}%"
    )
    print(
        f"F1 Score:  {metrics['f1'] * 100:.2f}%"
    )
    print(
        f"Accuracy:  {metrics['accuracy'] * 100:.2f}%"
    )
    print(
        "False Positive Rate:",
        f"{false_positive_rate(metrics) * 100:.2f}%",
    )

    print(
        "TP:", metrics["tp"],
        "TN:", metrics["tn"],
        "FP:", metrics["fp"],
        "FN:", metrics["fn"],
    )


def main():
    banner("QUANTUM CYBER DEFENSE ARENA V13.2")

    X_train, X_test, y_test = load_data()

    train_scaled, test_scaled = scale_features(
        X_train,
        X_test,
    )

    classical_pred, classical_seconds = (
        classical_detection(
            train_scaled,
            test_scaled,
        )
    )

    (
        quantum_pred,
        quantum_scores_array,
        quantum_seconds,
        pca_report,
    ) = quantum_detection(
        train_scaled,
        test_scaled,
    )

    (
        hybrid_pred,
        review_count,
        review_rate,
    ) = hybrid_detection(
        classical_pred,
        quantum_pred,
    )

    results = {
        "classical": calculate_metrics(
            y_test,
            classical_pred,
        ),
        "quantum": calculate_metrics(
            y_test,
            quantum_pred,
        ),
        "hybrid": calculate_metrics(
            y_test,
            hybrid_pred,
        ),
    }

    banner("V13.2 REAL ELLIPTIC RESULTS")

    for name, metrics in results.items():
        print_model_results(name, metrics)

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "mode": "REAL_DATA_EXPLORATORY_VALIDATION",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "dataset": {
            "name": "Elliptic Bitcoin Dataset",
            "source": (
                "edisonlin2002/elliptic-bitcoin-dataset"
            ),
            "normal_training_records": len(X_train),
            "test_records": len(X_test),
            "normal_test_records": int(
                np.sum(y_test == 0)
            ),
            "anomaly_test_records": int(
                np.sum(y_test == 1)
            ),
            "original_feature_count": 165,
            "train_test_split": (
                "chronological Elliptic time steps"
            ),
        },
        "model_configuration": {
            "classical": {
                "method": "IsolationForest",
                "estimators": 200,
                "contamination": 0.05,
                "input_features": 165,
                "training_seconds": round(
                    classical_seconds,
                    4,
                ),
            },
            "quantum": {
                "method": (
                    "Quantum State Fidelity Simulator"
                ),
                "threshold": QUANTUM_THRESHOLD,
                "input_features": 4,
                "pca": pca_report,
                "inference_seconds": round(
                    quantum_seconds,
                    4,
                ),
                "mean_anomaly_score": round(
                    float(np.mean(quantum_scores_array)),
                    6,
                ),
            },
            "hybrid": {
                "method": (
                    "Agreement-based hybrid fusion"
                ),
                "review_count": review_count,
                "review_rate": round(review_rate, 6),
                "review_policy": (
                    "REVIEW counted as negative "
                    "for binary F1 evaluation"
                ),
            },
        },
        "results": results,
        "false_positive_rates": {
            name: round(
                false_positive_rate(metrics),
                6,
            )
            for name, metrics in results.items()
        },
        "limitations": [
            "Exploratory real-data evaluation only",
            "A capped, stratified chronological test subset",
            "The quantum detector receives PCA-derived features",
            "Quantum input semantics differ from V11",
            "Quantum detector thresholds are not calibrated",
            "Classical model uses 165 input dimensions",
            "Quantum model uses only four PCA dimensions",
            "Model input dimensions therefore differ",
            "Hybrid agreement is not a trained meta-model",
            "REVIEW decisions count as negative",
            "One chronological holdout is not sufficient "
            "for broad external generalization",
            "Bitcoin illicit labels are a proxy for "
            "anomaly detection, not live cyber incidents",
            "The quantum detector is classically simulated",
            "No quantum computational advantage is proven",
        ],
    }

    OUTPUT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    banner("V13.2 REAL DATA VALIDATION COMPLETED")

    print()
    print("RESULTS SAVED TO:")
    print(OUTPUT_FILE)

    print()
    print("RESEARCH LIMITATION:")
    print(
        "This exploratory evaluation does not "
        "demonstrate quantum advantage or "
        "real-world deployment readiness."
    )


if __name__ == "__main__":
    try:
        main()
    except (
        FileNotFoundError,
        ValueError,
        ImportError,
    ) as error:
        print()
        print("V13.2 ERROR:")
        print(error)
        sys.exit(1)

