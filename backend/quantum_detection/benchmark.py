
"""
QUANTUM CYBER DEFENSE ARENA V6.1

Quantum vs Classical Anomaly Detection Benchmark

Models:
    1. Quantum State Fidelity Detector (Qiskit)
    2. Classical Isolation Forest (scikit-learn)

Data:
    Reproducible synthetic blockchain transaction features.

Metrics:
    Accuracy
    Precision
    Recall
    F1-score
    False positives
    False negatives
    Prediction time

IMPORTANT:
    Research simulation only.
    Not a validated production security detector.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from quantum_detector import QuantumAnomalyDetector


RANDOM_SEED = 42

TRAIN_SAMPLES = 500
NORMAL_TEST_SAMPLES = 100
ANOMALY_TEST_SAMPLES = 100

QUANTUM_THRESHOLD = 0.35

FEATURE_NAMES = [
    "transaction_value",
    "transactions_per_minute",
    "failed_transaction_ratio",
    "gas_spike_ratio",
]

NORMAL_REFERENCE = np.array(
    [0.15, 0.20, 0.05, 0.10],
    dtype=float,
)

NORMAL_STANDARD_DEVIATION = np.array(
    [0.06, 0.07, 0.03, 0.05],
    dtype=float,
)

ANOMALY_CENTER = np.array(
    [0.88, 0.85, 0.80, 0.90],
    dtype=float,
)

ANOMALY_STANDARD_DEVIATION = np.array(
    [0.10, 0.10, 0.12, 0.08],
    dtype=float,
)


def generate_normal_samples(
    rng: np.random.Generator,
    count: int,
) -> np.ndarray:
    """Generate synthetic normal blockchain activity."""

    samples = rng.normal(
        loc=NORMAL_REFERENCE,
        scale=NORMAL_STANDARD_DEVIATION,
        size=(count, 4),
    )

    return np.clip(samples, 0.0, 1.0)


def generate_anomaly_samples(
    rng: np.random.Generator,
    count: int,
) -> np.ndarray:
    """Generate clearly separated synthetic anomalies."""

    samples = rng.normal(
        loc=ANOMALY_CENTER,
        scale=ANOMALY_STANDARD_DEVIATION,
        size=(count, 4),
    )

    return np.clip(samples, 0.0, 1.0)


def prepare_dataset() -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    """
    Build reproducible train and test sets.

    Training:
        Normal samples only.

    Testing:
        Separate normal and anomalous samples.

    Labels:
        0 = NORMAL
        1 = ANOMALY
    """

    rng = np.random.default_rng(RANDOM_SEED)

    x_train = generate_normal_samples(
        rng,
        TRAIN_SAMPLES,
    )

    normal_test = generate_normal_samples(
        rng,
        NORMAL_TEST_SAMPLES,
    )

    anomaly_test = generate_anomaly_samples(
        rng,
        ANOMALY_TEST_SAMPLES,
    )

    x_test = np.vstack(
        [normal_test, anomaly_test]
    )

    y_test = np.concatenate(
        [
            np.zeros(
                NORMAL_TEST_SAMPLES,
                dtype=int,
            ),
            np.ones(
                ANOMALY_TEST_SAMPLES,
                dtype=int,
            ),
        ]
    )

    indices = rng.permutation(len(y_test))

    return (
        x_train,
        x_test[indices],
        y_test[indices],
    )


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    prediction_seconds: float,
) -> dict:
    """Calculate comparable detection metrics."""

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    ).ravel()

    return {
        "accuracy": round(
            float(accuracy_score(y_true, y_pred)),
            4,
        ),
        "precision": round(
            float(
                precision_score(
                    y_true,
                    y_pred,
                    zero_division=0,
                )
            ),
            4,
        ),
        "recall": round(
            float(
                recall_score(
                    y_true,
                    y_pred,
                    zero_division=0,
                )
            ),
            4,
        ),
        "f1_score": round(
            float(
                f1_score(
                    y_true,
                    y_pred,
                    zero_division=0,
                )
            ),
            4,
        ),
        "true_positives": int(tp),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "prediction_time_ms": round(
            prediction_seconds * 1000,
            3,
        ),
        "average_prediction_ms": round(
            prediction_seconds
            * 1000
            / max(len(y_pred), 1),
            4,
        ),
    }


def benchmark_quantum(
    x_test: np.ndarray,
    y_test: np.ndarray,
) -> dict:
    """Evaluate the existing Qiskit detector."""

    detector = QuantumAnomalyDetector(
        threshold=QUANTUM_THRESHOLD,
        reference=NORMAL_REFERENCE.tolist(),
    )

    predictions = []
    scores = []

    start = time.perf_counter()

    for features in x_test:
        result = detector.detect(
            features.tolist()
        )

        predictions.append(
            1 if result.classification == "ANOMALY"
            else 0
        )

        scores.append(result.anomaly_score)

    elapsed = time.perf_counter() - start

    metrics = calculate_metrics(
        y_test,
        np.asarray(predictions, dtype=int),
        elapsed,
    )

    metrics["model"] = (
        "Quantum State Fidelity Detector"
    )
    metrics["qubits"] = 2
    metrics["threshold"] = QUANTUM_THRESHOLD
    metrics["mean_anomaly_score"] = round(
        float(np.mean(scores)),
        6,
    )
    metrics["execution"] = (
        "Qiskit Statevector Simulation"
    )

    return metrics


def benchmark_classical(
    x_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
) -> dict:
    """Train and evaluate a classical Isolation Forest."""

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=RANDOM_SEED,
        n_jobs=1,
    )

    training_start = time.perf_counter()

    model.fit(x_train)

    training_time = (
        time.perf_counter() - training_start
    )

    prediction_start = time.perf_counter()

    raw_predictions = model.predict(x_test)

    prediction_time = (
        time.perf_counter() - prediction_start
    )

    predictions = np.where(
        raw_predictions == -1,
        1,
        0,
    )

    metrics = calculate_metrics(
        y_test,
        predictions,
        prediction_time,
    )

    metrics["model"] = "Isolation Forest"
    metrics["training_time_ms"] = round(
        training_time * 1000,
        3,
    )
    metrics["estimators"] = 100
    metrics["execution"] = "Classical CPU"

    return metrics


def print_result(
    title: str,
    metrics: dict,
) -> None:
    """Display a readable benchmark result."""

    print()
    print("-" * 60)
    print(title)
    print("-" * 60)

    print(
        f"Accuracy:         {metrics['accuracy']:.2%}"
    )
    print(
        f"Precision:        {metrics['precision']:.2%}"
    )
    print(
        f"Recall:           {metrics['recall']:.2%}"
    )
    print(
        f"F1-score:         {metrics['f1_score']:.2%}"
    )

    print(
        f"True positives:   {metrics['true_positives']}"
    )
    print(
        f"True negatives:   {metrics['true_negatives']}"
    )
    print(
        f"False positives:  {metrics['false_positives']}"
    )
    print(
        f"False negatives:  {metrics['false_negatives']}"
    )

    print(
        "Prediction time:  "
        f"{metrics['prediction_time_ms']:.3f} ms"
    )

    print(
        "Average per sample: "
        f"{metrics['average_prediction_ms']:.4f} ms"
    )


def main() -> None:
    print()
    print("=" * 60)
    print("QUANTUM CYBER DEFENSE ARENA V6.1")
    print("QUANTUM VS CLASSICAL BENCHMARK")
    print("=" * 60)

    print()
    print("Generating synthetic blockchain dataset...")

    x_train, x_test, y_test = prepare_dataset()

    print("Training samples:", len(x_train))
    print("Test samples:", len(x_test))
    print("Features:", len(FEATURE_NAMES))

    print()
    print("Running Quantum State Fidelity Detector...")

    quantum_result = benchmark_quantum(
        x_test,
        y_test,
    )

    print("Running Isolation Forest...")

    classical_result = benchmark_classical(
        x_train,
        x_test,
        y_test,
    )

    print_result(
        "QUANTUM DETECTOR RESULTS",
        quantum_result,
    )

    print_result(
        "CLASSICAL ISOLATION FOREST RESULTS",
        classical_result,
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "6.1",
        "experiment": (
            "Quantum vs Classical Anomaly Detection"
        ),
        "data_source": "SYNTHETIC_SIMULATION",
        "random_seed": RANDOM_SEED,
        "features": FEATURE_NAMES,
        "training_samples": len(x_train),
        "test_samples": len(x_test),
        "quantum": quantum_result,
        "classical": classical_result,
        "limitations": [
            "Synthetic, clearly separated anomaly classes",
            "Quantum model uses an untrained fixed reference",
            "The quantum threshold is not calibrated",
            "This is not evidence of quantum advantage",
            "This is not a production security benchmark",
        ],
    }

    output_path = (
        Path(__file__).resolve().parent
        / "benchmark_results.json"
    )

    output_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print("BENCHMARK COMPLETED")
    print("=" * 60)
    print("Results saved to:")
    print(output_path)


if __name__ == "__main__":
    main()
