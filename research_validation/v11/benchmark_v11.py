
"""
QUANTUM CYBER DEFENSE ARENA V11
Advanced Research Validation Benchmark

Compares:
    1. Classical Isolation Forest
    2. Quantum State Fidelity
    3. Hybrid Quantum AI Fusion

Uses synthetic datasets and reproducible seeds.

IMPORTANT:
This is a research simulation.
No real cybersecurity incidents are analyzed.
No quantum computational advantage is claimed.
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ai_detection.detector import (
    AIThreatDetector,
    FEATURE_NAMES,
)
from backend.quantum_detection.quantum_detector import (
    QuantumAnomalyDetector,
)


OUTPUT_FILE = (
    Path(__file__).resolve().parent
    / "benchmark_v11_results.json"
)

SEEDS = [11, 22, 33, 44, 55]
TEST_SIZE = 200
TRAIN_SIZE = 800

QUANTUM_FEATURES = (
    "transaction_value",
    "transactions_per_minute",
    "failed_transaction_ratio",
    "gas_spike_ratio",
)

CLASSICAL_FEATURES = tuple(FEATURE_NAMES)


def validate_configuration() -> None:
    expected = set(QUANTUM_FEATURES) | {
        "unique_counterparties"
    }

    if len(CLASSICAL_FEATURES) != 5:
        raise ValueError(
            f"Expected 5 classical features: {CLASSICAL_FEATURES}"
        )

    if set(CLASSICAL_FEATURES) != expected:
        raise ValueError(
            f"Unexpected feature names: {CLASSICAL_FEATURES}"
        )


def create_dataset(
    seed: int,
    train_size: int = TRAIN_SIZE,
    test_size: int = TEST_SIZE,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate separate training and test sets.

    Training:
        normal traffic only.

    Test:
        50% normal, 50% anomalous traffic.

    Data is normalized to [0, 1].
    """

    rng = np.random.default_rng(seed)

    train = rng.normal(
        loc=0.20,
        scale=0.06,
        size=(train_size, 5),
    )

    normal = rng.normal(
        loc=0.23,
        scale=0.12,
        size=(test_size // 2, 5),
    )

    anomalous = rng.normal(
        loc=0.58,
        scale=0.20,
        size=(test_size - test_size // 2, 5),
    )

    X_train = np.clip(train, 0, 1)
    X_test = np.clip(
        np.vstack([normal, anomalous]),
        0,
        1,
    )

    y_test = np.array(
        [0] * len(normal) + [1] * len(anomalous),
        dtype=int,
    )

    permutation = rng.permutation(len(y_test))

    return (
        X_train,
        X_test[permutation],
        y_test[permutation],
    )


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict:
    """
    Binary classification metrics.
    Positive class = anomaly.
    """

    true = np.asarray(y_true, dtype=int)
    pred = np.asarray(y_pred, dtype=int)

    tp = int(np.sum((true == 1) & (pred == 1)))
    tn = int(np.sum((true == 0) & (pred == 0)))
    fp = int(np.sum((true == 0) & (pred == 1)))
    fn = int(np.sum((true == 1) & (pred == 0)))

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    accuracy = (
        (tp + tn) / len(true)
        if len(true)
        else 0.0
    )

    return {
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "accuracy": round(accuracy, 6),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def classical_scores(
    detector: AIThreatDetector,
    X_test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Produce classical anomaly scores and classifications.

    Negative Isolation Forest decision values
    indicate stronger anomaly evidence.

    The logistic score is a heuristic,
    not a calibrated probability.
    """

    scores = []
    predictions = []

    for row in X_test:
        event = {
            name: float(value)
            for name, value in zip(
                CLASSICAL_FEATURES,
                row,
            )
        }

        result = detector.predict_event(event)

        decision = float(
            result["decision_function"]
        )

        scaled = np.clip(
            decision / 0.10,
            -60,
            60,
        )

        score = 1.0 / (
            1.0 + math.exp(float(scaled))
        )

        scores.append(score)
        predictions.append(
            int(bool(result["is_anomaly"]))
        )

    return (
        np.asarray(scores),
        np.asarray(predictions),
    )


def quantum_scores(
    detector: QuantumAnomalyDetector,
    X_test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Run the existing Qiskit detector.

    Select its four features by name,
    rather than assuming column order.
    """

    indices = [
        CLASSICAL_FEATURES.index(name)
        for name in QUANTUM_FEATURES
    ]

    scores = []
    predictions = []

    for row in X_test:
        features = [
            float(row[index])
            for index in indices
        ]

        result = detector.detect(features)

        scores.append(
            float(result.anomaly_score)
        )

        predictions.append(
            int(result.classification == "ANOMALY")
        )

    return (
        np.asarray(scores),
        np.asarray(predictions),
    )


def run_single_benchmark(seed: int) -> dict:
    print()
    print("-" * 60)
    print(f"BENCHMARK SEED: {seed}")
    print("-" * 60)

    X_train, X_test, y_test = create_dataset(seed)

    classical = AIThreatDetector(seed=seed)
    classical.train(X_train)

    quantum = QuantumAnomalyDetector(
        threshold=0.35
    )

    start = perf_counter()

    classical_score, classical_pred = classical_scores(
        classical,
        X_test,
    )

    classical_ms = (
        perf_counter() - start
    ) * 1000

    start = perf_counter()

    quantum_score, quantum_pred = quantum_scores(
        quantum,
        X_test,
    )

    quantum_ms = (
        perf_counter() - start
    ) * 1000

    # Match the existing V7 Fusion Engine 50/50
    # weighted scoring rule.
    fusion_score = (
        0.5 * classical_score
        + 0.5 * quantum_score
    )

    # Match the fusion decision logic:
    # agreement -> classification;
    # disagreement -> REVIEW.
    agree = classical_pred == quantum_pred

    hybrid_pred = np.where(
        agree,
        classical_pred,
        -1,
    )

    # For binary F1 comparison, REVIEW is counted
    # as not confirmed as an anomaly.
    # The review rate is reported separately.
    hybrid_binary_pred = (
        hybrid_pred == 1
    ).astype(int)

    classical_metrics = calculate_metrics(
        y_test,
        classical_pred,
    )

    quantum_metrics = calculate_metrics(
        y_test,
        quantum_pred,
    )

    hybrid_metrics = calculate_metrics(
        y_test,
        hybrid_binary_pred,
    )

    review_rate = float(
        np.mean(~agree)
    )

    output = {
        "seed": seed,
        "test_samples": len(y_test),
        "classical": {
            **classical_metrics,
            "runtime_ms": round(classical_ms, 3),
        },
        "quantum": {
            **quantum_metrics,
            "runtime_ms": round(quantum_ms, 3),
        },
        "hybrid": {
            **hybrid_metrics,
            "review_rate": round(review_rate, 6),
            "fusion_score_mean": round(
                float(np.mean(fusion_score)),
                6,
            ),
            "fusion_rule": (
                "both_anomaly=1; "
                "both_normal=0; "
                "disagreement=REVIEW"
            ),
        },
    }

    for model in ("classical", "quantum", "hybrid"):
        print(
            f"{model.upper():10s} "
            f"F1={output[model]['f1']:.4f} "
            f"PREC={output[model]['precision']:.4f} "
            f"RECALL={output[model]['recall']:.4f}"
        )

    print(
        f"HYBRID REVIEW RATE: {review_rate:.2%}"
    )

    return output


def summarize(results: list[dict]) -> dict:
    summary = {}

    for model in ("classical", "quantum", "hybrid"):
        summary[model] = {}

        for metric in (
            "precision",
            "recall",
            "f1",
            "accuracy",
        ):
            values = [
                result[model][metric]
                for result in results
            ]

            summary[model][metric] = {
                "mean": round(
                    float(np.mean(values)),
                    6,
                ),
                "std": round(
                    float(np.std(values, ddof=1)),
                    6,
                ),
            }

    for model in ("classical", "quantum"):
        times = [
            result[model]["runtime_ms"]
            for result in results
        ]

        summary[model]["runtime_ms"] = {
            "mean": round(
                float(np.mean(times)),
                3,
            ),
            "std": round(
                float(np.std(times, ddof=1)),
                3,
            ),
        }

    review_rates = [
        result["hybrid"]["review_rate"]
        for result in results
    ]

    summary["hybrid"]["review_rate"] = {
        "mean": round(
            float(np.mean(review_rates)),
            6,
        ),
        "std": round(
            float(np.std(review_rates, ddof=1)),
            6,
        ),
    }

    return summary


def main() -> None:
    print()
    print("=" * 60)
    print("QUANTUM CYBER DEFENSE ARENA V11")
    print("ADVANCED RESEARCH VALIDATION BENCHMARK")
    print("=" * 60)

    validate_configuration()

    results = [
        run_single_benchmark(seed)
        for seed in SEEDS
    ]

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "11.0.0",
        "mode": "RESEARCH_SIMULATION",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "dataset": {
            "type": "synthetic",
            "train_samples": TRAIN_SIZE,
            "test_samples_per_seed": TEST_SIZE,
            "seeds": SEEDS,
            "normal_class_fraction": 0.5,
            "anomaly_class_fraction": 0.5,
        },
        "methodology": {
            "classical": "IsolationForest",
            "quantum": "Quantum State Fidelity Simulator",
            "hybrid": "50/50 score fusion and agreement decision",
            "review_policy": (
                "REVIEW counted as negative for binary "
                "classification, reported separately."
            ),
            "limitations": [
                "Synthetic data only",
                "Quantum detector uses a classical simulator",
                "No quantum speedup claim",
                "F1 metrics depend on synthetic distributions",
                "Fusion scores are not calibrated probabilities",
            ],
        },
        "runs": results,
        "summary": summarize(results),
    }

    OUTPUT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print("V11 BENCHMARK COMPLETED")
    print("=" * 60)

    print()
    print("RESULTS FILE:")
    print(OUTPUT_FILE)

    print()
    print("MEAN F1 SCORES:")

    for model in ("classical", "quantum", "hybrid"):
        mean_f1 = report["summary"][model]["f1"]["mean"]

        print(
            f"{model.upper():10s}: {mean_f1:.4f}"
        )


if __name__ == "__main__":
    main()
