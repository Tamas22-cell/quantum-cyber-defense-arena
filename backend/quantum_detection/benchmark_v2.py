
"""
QUANTUM CYBER DEFENSE ARENA V6.2
Advanced Quantum vs Classical Benchmark

Models:
    - Quantum State Fidelity Detector (Qiskit Statevector)
    - Classical Isolation Forest (scikit-learn)

Features:
    - Overlapping synthetic normal/anomaly distributions
    - Multiple independent experiments
    - Accuracy, precision, recall, F1
    - False-positive and false-negative analysis
    - Detection latency
    - Mean and standard deviation across experiments
    - JSON research report

Research simulation only.
No claims of quantum advantage or production attack detection.
"""

from __future__ import annotations

import json
import sys
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

# Support running this file directly or as a module.
try:
    from .quantum_detector import QuantumAnomalyDetector
except ImportError:
    from quantum_detector import QuantumAnomalyDetector


# ============================================================
# CONFIGURATION
# ============================================================

EXPERIMENTS = 10
TRAIN_SAMPLES = 500
NORMAL_TEST_SAMPLES = 150
ANOMALY_TEST_SAMPLES = 150

BASE_SEED = 2026
QUANTUM_THRESHOLD = 0.35

FEATURE_NAMES = [
    "transaction_value",
    "transactions_per_minute",
    "failed_transaction_ratio",
    "gas_spike_ratio",
]

NORMAL_CENTER = np.array(
    [0.30, 0.35, 0.20, 0.25],
    dtype=float,
)

NORMAL_STD = np.array(
    [0.15, 0.16, 0.13, 0.14],
    dtype=float,
)

ANOMALY_CENTER = np.array(
    [0.55, 0.57, 0.43, 0.50],
    dtype=float,
)

ANOMALY_STD = np.array(
    [0.19, 0.18, 0.18, 0.19],
    dtype=float,
)


# ============================================================
# DATA GENERATION
# ============================================================

def generate_samples(
    rng: np.random.Generator,
    count: int,
    center: np.ndarray,
    std: np.ndarray,
) -> np.ndarray:
    """
    Generate normalized synthetic transaction features.

    Clipping is applied to [0, 1] because the existing
    quantum detector requires normalized input.
    """
    samples = rng.normal(
        loc=center,
        scale=std,
        size=(count, 4),
    )

    return np.clip(samples, 0.0, 1.0)


def create_dataset(
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create independent training and testing samples.

    Train:
        Only normal traffic.

    Test:
        Both normal and anomalous traffic.
    """
    rng = np.random.default_rng(seed)

    x_train = generate_samples(
        rng,
        TRAIN_SAMPLES,
        NORMAL_CENTER,
        NORMAL_STD,
    )

    x_normal = generate_samples(
        rng,
        NORMAL_TEST_SAMPLES,
        NORMAL_CENTER,
        NORMAL_STD,
    )

    x_anomaly = generate_samples(
        rng,
        ANOMALY_TEST_SAMPLES,
        ANOMALY_CENTER,
        ANOMALY_STD,
    )

    x_test = np.vstack(
        [x_normal, x_anomaly]
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


# ============================================================
# METRICS
# ============================================================

def evaluate_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    prediction_time_ms: float,
) -> dict:
    """Calculate metrics using anomaly as positive class."""

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    ).ravel()

    return {
        "accuracy": float(
            accuracy_score(y_true, y_pred)
        ),
        "precision": float(
            precision_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "f1_score": float(
            f1_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "true_positives": int(tp),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "prediction_time_ms": float(
            prediction_time_ms
        ),
        "average_prediction_ms": float(
            prediction_time_ms / len(y_pred)
        ),
    }


# ============================================================
# QUANTUM EVALUATION
# ============================================================

def run_quantum(
    x_test: np.ndarray,
    y_test: np.ndarray,
) -> dict:
    """
    Evaluate the existing Qiskit Statevector detector.

    Note: This includes Python-level quantum-state
    simulation, not real QPU execution.
    """

    detector = QuantumAnomalyDetector(
        threshold=QUANTUM_THRESHOLD,
        reference=NORMAL_CENTER.tolist(),
    )

    predictions: list[int] = []

    start = time.perf_counter()

    for row in x_test:
        result = detector.detect(row.tolist())

        predictions.append(
            1
            if result.classification == "ANOMALY"
            else 0
        )

    elapsed_ms = (
        time.perf_counter() - start
    ) * 1000.0

    metrics = evaluate_predictions(
        y_test,
        np.array(predictions, dtype=int),
        elapsed_ms,
    )

    metrics["model"] = (
        "Quantum State Fidelity Detector"
    )

    return metrics


# ============================================================
# CLASSICAL EVALUATION
# ============================================================

def run_classical(
    x_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    seed: int,
) -> dict:
    """Evaluate Isolation Forest on the same test data."""

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=seed,
        n_jobs=1,
    )

    training_start = time.perf_counter()

    model.fit(x_train)

    training_ms = (
        time.perf_counter() - training_start
    ) * 1000.0

    prediction_start = time.perf_counter()

    raw_predictions = model.predict(x_test)

    prediction_ms = (
        time.perf_counter() - prediction_start
    ) * 1000.0

    predictions = np.where(
        raw_predictions == -1,
        1,
        0,
    )

    metrics = evaluate_predictions(
        y_test,
        predictions,
        prediction_ms,
    )

    metrics["model"] = "Isolation Forest"
    metrics["training_time_ms"] = float(
        training_ms
    )

    return metrics


# ============================================================
# STATISTICS
# ============================================================

METRIC_NAMES = [
    "accuracy",
    "precision",
    "recall",
    "f1_score",
    "false_positives",
    "false_negatives",
    "prediction_time_ms",
    "average_prediction_ms",
]


def summarize(
    results: list[dict],
) -> dict:
    """Calculate mean and standard deviation by metric."""

    summary = {}

    for metric in METRIC_NAMES:
        values = np.array(
            [result[metric] for result in results],
            dtype=float,
        )

        summary[metric] = {
            "mean": round(
                float(np.mean(values)),
                6,
            ),
            "std": round(
                float(np.std(values, ddof=1))
                if len(values) > 1
                else 0.0,
                6,
            ),
            "min": round(
                float(np.min(values)),
                6,
            ),
            "max": round(
                float(np.max(values)),
                6,
            ),
        }

    return summary


def print_summary(
    name: str,
    summary: dict,
) -> None:
    """Print formatted benchmark results."""

    print()
    print("-" * 66)
    print(name)
    print("-" * 66)

    for metric in [
        "accuracy",
        "precision",
        "recall",
        "f1_score",
    ]:
        result = summary[metric]

        print(
            f"{metric.upper():<22}"
            f"{result['mean'] * 100:7.2f}% "
            f"+/- {result['std'] * 100:.2f}%"
        )

    for metric in [
        "false_positives",
        "false_negatives",
        "prediction_time_ms",
        "average_prediction_ms",
    ]:
        result = summary[metric]

        print(
            f"{metric:<22}"
            f"{result['mean']:9.4f} "
            f"+/- {result['std']:.4f}"
        )


# ============================================================
# MAIN EXPERIMENT
# ============================================================

def main() -> None:
    print()
    print("=" * 66)
    print("QUANTUM CYBER DEFENSE ARENA V6.2")
    print("ADVANCED QUANTUM VS CLASSICAL BENCHMARK")
    print("=" * 66)

    print()
    print("Dataset: overlapping synthetic transaction distributions")
    print("Independent experiments:", EXPERIMENTS)
    print("Training samples per experiment:", TRAIN_SAMPLES)
    print(
        "Testing samples per experiment:",
        NORMAL_TEST_SAMPLES + ANOMALY_TEST_SAMPLES,
    )
    print("Features:", len(FEATURE_NAMES))
    print()

    quantum_results: list[dict] = []
    classical_results: list[dict] = []

    for experiment in range(EXPERIMENTS):
        seed = BASE_SEED + experiment

        x_train, x_test, y_test = create_dataset(seed)

        quantum = run_quantum(
            x_test,
            y_test,
        )

        classical = run_classical(
            x_train,
            x_test,
            y_test,
            seed,
        )

        quantum_results.append(quantum)
        classical_results.append(classical)

        print(
            f"Experiment {experiment + 1:02d}/{EXPERIMENTS} | "
            f"Quantum F1: {quantum['f1_score']:.3f} | "
            f"Classical F1: {classical['f1_score']:.3f}"
        )

    quantum_summary = summarize(quantum_results)
    classical_summary = summarize(classical_results)

    print_summary(
        "QUANTUM DETECTOR - AGGREGATED RESULTS",
        quantum_summary,
    )

    print_summary(
        "ISOLATION FOREST - AGGREGATED RESULTS",
        classical_summary,
    )

    quantum_f1 = quantum_summary["f1_score"]["mean"]
    classical_f1 = classical_summary["f1_score"]["mean"]

    if quantum_f1 > classical_f1:
        best_f1 = "Quantum State Fidelity Detector"
    elif classical_f1 > quantum_f1:
        best_f1 = "Isolation Forest"
    else:
        best_f1 = "TIE"

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "6.2",
        "experiment": "Overlapping Quantum vs Classical Benchmark",
        "data_source": "SYNTHETIC_SIMULATION",
        "configuration": {
            "experiments": EXPERIMENTS,
            "base_seed": BASE_SEED,
            "train_samples": TRAIN_SAMPLES,
            "normal_test_samples": NORMAL_TEST_SAMPLES,
            "anomaly_test_samples": ANOMALY_TEST_SAMPLES,
            "quantum_threshold": QUANTUM_THRESHOLD,
            "features": FEATURE_NAMES,
            "normal_center": NORMAL_CENTER.tolist(),
            "normal_std": NORMAL_STD.tolist(),
            "anomaly_center": ANOMALY_CENTER.tolist(),
            "anomaly_std": ANOMALY_STD.tolist(),
        },
        "quantum": {
            "model": "Quantum State Fidelity Detector",
            "summary": quantum_summary,
            "experiments": quantum_results,
        },
        "classical": {
            "model": "Isolation Forest",
            "summary": classical_summary,
            "experiments": classical_results,
        },
        "best_mean_f1": best_f1,
        "limitations": [
            "All data are synthetic",
            "Quantum model uses a fixed normal reference",
            "Quantum threshold is not tuned on validation data",
            "Classical model uses an assumed contamination value",
            "Classical training time and quantum reference construction are not directly compared",
            "Runtime depends on hardware and software environment",
            "No evidence of quantum advantage",
            "Not validated for real blockchain security monitoring",
        ],
    }

    output_path = (
        Path(__file__).resolve().parent
        / "benchmark_v2_results.json"
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
    print("=" * 66)
    print("BENCHMARK V6.2 COMPLETED")
    print("=" * 66)
    print("Best mean F1-score:", best_f1)
    print("Results saved to:", output_path)
    print("=" * 66)


if __name__ == "__main__":
    main()
