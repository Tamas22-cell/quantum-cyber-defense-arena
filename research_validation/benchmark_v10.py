
"""
QUANTUM CYBER DEFENSE ARENA V10
Research Validation and Benchmarking Engine

Compares three existing research models:
1. Classical Isolation Forest V2
2. Quantum State Fidelity Detector
3. Hybrid Quantum AI Fusion Engine

Features:
- Reproducible synthetic experiments
- Separate training and testing datasets
- Precision, recall, F1 and accuracy
- Confusion matrices
- Model agreement analysis
- Inference time comparison
- Bootstrap confidence intervals
- JSON results export

IMPORTANT:
This is a synthetic research benchmark.
It does not establish real-world security effectiveness
or quantum computational advantage.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.ai_detection.detector import (
    AIThreatDetector,
    FEATURE_NAMES,
)

from backend.fusion_engine.fusion_engine import (
    ClassicalPrediction,
    QuantumAIThreatFusionEngine,
)


VERSION = "10.0.0"

EXPERIMENT_SEEDS = [42, 123, 2026]

TRAINING_SAMPLES = 800

NORMAL_TEST_SAMPLES = 60
ANOMALY_TEST_SAMPLES = 60

BOOTSTRAP_SAMPLES = 1000

CLASSICAL_FEATURES = tuple(FEATURE_NAMES)

QUANTUM_FEATURES = (
    "transaction_value",
    "transactions_per_minute",
    "failed_transaction_ratio",
    "gas_spike_ratio",
)

EXPECTED_CLASSICAL_FEATURES = set(
    QUANTUM_FEATURES
) | {"unique_counterparties"}

OUTPUT_FILE = (
    PROJECT_ROOT
    / "research_validation"
    / "benchmark_v10_results.json"
)


@dataclass
class ExperimentRecord:
    seed: int
    event_id: str
    true_label: int
    classical_prediction: int
    quantum_prediction: int
    hybrid_prediction: int
    hybrid_review: bool
    classical_score: float
    quantum_score: float
    hybrid_score: float
    classical_runtime_ms: float
    quantum_hybrid_runtime_ms: float


def validate_mapping() -> None:
    if len(CLASSICAL_FEATURES) != 5:
        raise ValueError(
            "Classical detector must use five features. "
            f"Actual: {CLASSICAL_FEATURES}"
        )

    if set(CLASSICAL_FEATURES) != EXPECTED_CLASSICAL_FEATURES:
        raise ValueError(
            "Unexpected classical feature mapping: "
            f"{CLASSICAL_FEATURES}"
        )

    if not set(QUANTUM_FEATURES).issubset(
        set(CLASSICAL_FEATURES)
    ):
        raise ValueError(
            "Quantum features cannot be mapped "
            "from classical event fields."
        )


def clamp_data(data: np.ndarray) -> np.ndarray:
    return np.clip(data, 0.0, 1.0)


def create_training_data(
    seed: int,
    count: int = TRAINING_SAMPLES,
) -> np.ndarray:
    """
    Synthetic normal training samples.

    The classical detector receives five features.
    Test events are generated separately.
    """
    rng = np.random.default_rng(seed)

    data = rng.normal(
        loc=0.20,
        scale=0.06,
        size=(count, len(CLASSICAL_FEATURES)),
    )

    return clamp_data(data)


def create_test_events(
    seed: int,
) -> list[dict]:
    """
    Build a balanced, labeled synthetic test dataset.

    Labels are assigned from the generation process,
    independently of detector predictions.
    """
    rng = np.random.default_rng(seed + 10000)

    normal = rng.normal(
        loc=0.20,
        scale=0.07,
        size=(
            NORMAL_TEST_SAMPLES,
            len(CLASSICAL_FEATURES),
        ),
    )

    anomaly = rng.normal(
        loc=0.78,
        scale=0.14,
        size=(
            ANOMALY_TEST_SAMPLES,
            len(CLASSICAL_FEATURES),
        ),
    )

    normal = clamp_data(normal)
    anomaly = clamp_data(anomaly)

    samples = np.concatenate(
        [normal, anomaly],
        axis=0,
    )

    labels = np.array(
        [0] * NORMAL_TEST_SAMPLES
        + [1] * ANOMALY_TEST_SAMPLES,
        dtype=int,
    )

    order = rng.permutation(len(labels))

    networks = [
        "Ethereum",
        "Polygon",
        "Arbitrum",
        "Base",
    ]

    events = []

    for index, sample_index in enumerate(order):
        row = samples[sample_index]
        label = int(labels[sample_index])

        event = {
            "id": f"V10-{seed}-{index:04d}",
            "network": networks[index % len(networks)],
            "true_label": label,
        }

        for feature_name, value in zip(
            CLASSICAL_FEATURES,
            row,
        ):
            event[feature_name] = float(value)

        events.append(event)

    return events


def normalize_classical_score(
    decision_function: float,
    temperature: float = 0.10,
) -> float:
    if temperature <= 0:
        raise ValueError(
            "Temperature must be positive."
        )

    decision = float(decision_function)

    if not math.isfinite(decision):
        raise ValueError(
            "Non-finite classical decision."
        )

    scaled = max(
        -60.0,
        min(60.0, decision / temperature),
    )

    return 1.0 / (1.0 + math.exp(scaled))


def calculate_metrics(
    true_labels: list[int],
    predictions: list[int],
) -> dict:
    if len(true_labels) != len(predictions):
        raise ValueError(
            "Labels and predictions have "
            "different lengths."
        )

    if not true_labels:
        raise ValueError(
            "Cannot calculate metrics for empty data."
        )

    tp = sum(
        t == 1 and p == 1
        for t, p in zip(true_labels, predictions)
    )

    tn = sum(
        t == 0 and p == 0
        for t, p in zip(true_labels, predictions)
    )

    fp = sum(
        t == 0 and p == 1
        for t, p in zip(true_labels, predictions)
    )

    fn = sum(
        t == 1 and p == 0
        for t, p in zip(true_labels, predictions)
    )

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0.0
    )

    f1 = (
        2.0 * precision * recall
        / (precision + recall)
        if precision + recall
        else 0.0
    )

    accuracy = (tp + tn) / len(true_labels)

    return {
        "accuracy": round(accuracy, 6),
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "confusion_matrix": {
            "TP": tp,
            "TN": tn,
            "FP": fp,
            "FN": fn,
        },
        "sample_count": len(true_labels),
    }


def evaluate_experiment(
    seed: int,
) -> list[ExperimentRecord]:
    print()
    print("=" * 65)
    print(f"EXPERIMENT SEED: {seed}")
    print("=" * 65)

    classical_detector = AIThreatDetector(
        seed=seed
    )

    training_data = create_training_data(seed)

    classical_detector.train(training_data)

    fusion_engine = QuantumAIThreatFusionEngine()

    events = create_test_events(seed)

    records = []

    for event in events:
        # Classical inference

        classical_start = perf_counter()

        classical_result = (
            classical_detector.predict_event(event)
        )

        classical_runtime_ms = (
            perf_counter() - classical_start
        ) * 1000.0

        if (
            classical_result["classification"]
            == "INSUFFICIENT_DATA"
        ):
            raise RuntimeError(
                "Classical detector rejected "
                f"benchmark event {event['id']}"
            )

        classical_score = normalize_classical_score(
            classical_result["decision_function"]
        )

        classical_anomaly = bool(
            classical_result["is_anomaly"]
        )

        classical_prediction = ClassicalPrediction(
            anomaly_score=classical_score,
            is_anomaly=classical_anomaly,
            model="IsolationForest-V2",
        )

        quantum_features = [
            float(event[name])
            for name in QUANTUM_FEATURES
        ]

        # Quantum inference and hybrid fusion.
        # The existing Fusion Engine computes
        # the quantum detector result internally.

        quantum_start = perf_counter()

        fusion_result = fusion_engine.analyze(
            event_id=event["id"],
            network=event["network"],
            features=quantum_features,
            classical_prediction=classical_prediction,
        )

        quantum_hybrid_runtime_ms = (
            perf_counter() - quantum_start
        ) * 1000.0

        quantum_anomaly = bool(
            fusion_result.quantum_anomaly
        )

        hybrid_classification = (
            fusion_result.classification
        )

        # Research policy:
        # REVIEW is not treated as a confirmed anomaly.
        # It is recorded separately as an abstention.
        hybrid_anomaly = (
            hybrid_classification == "ANOMALY"
        )

        hybrid_review = (
            hybrid_classification == "REVIEW"
        )

        record = ExperimentRecord(
            seed=seed,
            event_id=event["id"],
            true_label=int(event["true_label"]),
            classical_prediction=int(
                classical_anomaly
            ),
            quantum_prediction=int(
                quantum_anomaly
            ),
            hybrid_prediction=int(
                hybrid_anomaly
            ),
            hybrid_review=hybrid_review,
            classical_score=classical_score,
            quantum_score=float(
                fusion_result.quantum_score
            ),
            hybrid_score=float(
                fusion_result.fusion_score
            ),
            classical_runtime_ms=(
                classical_runtime_ms
            ),
            quantum_hybrid_runtime_ms=(
                quantum_hybrid_runtime_ms
            ),
        )

        records.append(record)

    print(
        "Training samples:",
        len(training_data),
    )

    print(
        "Independent test samples:",
        len(records),
    )

    print(
        "Hybrid review decisions:",
        sum(r.hybrid_review for r in records),
    )

    return records


def bootstrap_f1_difference(
    records: list[ExperimentRecord],
    first_model: str,
    second_model: str,
    seed: int = 20261019,
) -> dict:
    """
    Paired, stratified bootstrap by experiment seed
    and true class.

    Both models are evaluated on identical
    resampled events.

    Confidence intervals describe this synthetic
    experimental dataset only.
    """
    rng = np.random.default_rng(seed)

    grouped_indices: dict[tuple[int, int], list[int]] = {}

    for index, record in enumerate(records):
        key = (record.seed, record.true_label)
        grouped_indices.setdefault(key, []).append(index)

    groups = [
        np.asarray(indices, dtype=int)
        for indices in grouped_indices.values()
    ]

    def model_f1(
        sample: list[ExperimentRecord],
        model: str,
    ) -> float:
        labels = [r.true_label for r in sample]
        predictions = [
            int(getattr(r, model))
            for r in sample
        ]

        return calculate_metrics(
            labels,
            predictions,
        )["f1"]

    observed = (
        model_f1(records, first_model)
        - model_f1(records, second_model)
    )

    differences = []

    for _ in range(BOOTSTRAP_SAMPLES):
        sampled_indices = np.concatenate(
            [
                rng.choice(
                    group,
                    size=len(group),
                    replace=True,
                )
                for group in groups
            ]
        )

        sample = [
            records[int(index)]
            for index in sampled_indices
        ]

        difference = (
            model_f1(sample, first_model)
            - model_f1(sample, second_model)
        )

        differences.append(difference)

    lower, upper = np.percentile(
        differences,
        [2.5, 97.5],
    )

    return {
        "model_a": first_model,
        "model_b": second_model,
        "observed_f1_difference_pp": round(
            observed * 100,
            4,
        ),
        "ci_95_lower_pp": round(
            float(lower) * 100,
            4,
        ),
        "ci_95_upper_pp": round(
            float(upper) * 100,
            4,
        ),
        "bootstrap_samples": BOOTSTRAP_SAMPLES,
        "method": (
            "paired stratified bootstrap "
            "within experiment seed and true class"
        ),
    }


def summarize_records(
    records: list[ExperimentRecord],
) -> dict:
    labels = [
        r.true_label
        for r in records
    ]

    classical = [
        r.classical_prediction
        for r in records
    ]

    quantum = [
        r.quantum_prediction
        for r in records
    ]

    hybrid = [
        r.hybrid_prediction
        for r in records
    ]

    review_count = sum(
        r.hybrid_review
        for r in records
    )

    agreement_count = sum(
        r.classical_prediction
        == r.quantum_prediction
        for r in records
    )

    decisive_records = [
        r for r in records
        if not r.hybrid_review
    ]

    review_corrected_metrics = None

    if decisive_records:
        review_corrected_metrics = (
            calculate_metrics(
                [
                    r.true_label
                    for r in decisive_records
                ],
                [
                    r.hybrid_prediction
                    for r in decisive_records
                ],
            )
        )

    runtime_classical = np.array(
        [
            r.classical_runtime_ms
            for r in records
        ],
        dtype=float,
    )

    runtime_quantum_hybrid = np.array(
        [
            r.quantum_hybrid_runtime_ms
            for r in records
        ],
        dtype=float,
    )

    result = {
        "sample_count": len(records),
        "classical": calculate_metrics(
            labels,
            classical,
        ),
        "quantum": calculate_metrics(
            labels,
            quantum,
        ),
        "hybrid_conservative": (
            calculate_metrics(
                labels,
                hybrid,
            )
        ),
        "hybrid_abstention": {
            "review_count": review_count,
            "review_rate": round(
                review_count / len(records),
                6,
            ),
            "decisive_coverage": round(
                len(decisive_records) / len(records),
                6,
            ),
            "decisive_only_metrics": (
                review_corrected_metrics
            ),
            "policy": (
                "REVIEW counts as not confirmed "
                "for conservative binary metrics."
            ),
        },
        "classical_quantum_agreement": {
            "agree_count": agreement_count,
            "disagree_count": (
                len(records) - agreement_count
            ),
            "agreement_rate": round(
                agreement_count / len(records),
                6,
            ),
        },
        "runtime_ms": {
            "classical_mean": round(
                float(runtime_classical.mean()),
                5,
            ),
            "classical_median": round(
                float(np.median(runtime_classical)),
                5,
            ),
            "quantum_plus_fusion_mean": round(
                float(runtime_quantum_hybrid.mean()),
                5,
            ),
            "quantum_plus_fusion_median": round(
                float(np.median(
                    runtime_quantum_hybrid
                )),
                5,
            ),
            "note": (
                "Measured as separate Python inference "
                "calls; quantum-plus-fusion includes "
                "statevector simulation and fusion logic."
            ),
        },
    }

    result["confidence_intervals"] = [
        bootstrap_f1_difference(
            records,
            "quantum_prediction",
            "classical_prediction",
        ),
        bootstrap_f1_difference(
            records,
            "hybrid_prediction",
            "classical_prediction",
            seed=20261020,
        ),
    ]

    return result


def main() -> None:
    print()
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA V10")
    print("RESEARCH VALIDATION & BENCHMARKING")
    print("=" * 70)

    validate_mapping()

    print()
    print("Classical features:", len(CLASSICAL_FEATURES))
    print("Quantum features:", len(QUANTUM_FEATURES))
    print("Experiment seeds:", EXPERIMENT_SEEDS)

    all_records = []

    experiment_results = []

    for seed in EXPERIMENT_SEEDS:
        records = evaluate_experiment(seed)

        all_records.extend(records)

        experiment_results.append({
            "seed": seed,
            "results": {
                "classical": calculate_metrics(
                    [r.true_label for r in records],
                    [
                        r.classical_prediction
                        for r in records
                    ],
                ),
                "quantum": calculate_metrics(
                    [r.true_label for r in records],
                    [
                        r.quantum_prediction
                        for r in records
                    ],
                ),
                "hybrid": calculate_metrics(
                    [r.true_label for r in records],
                    [
                        r.hybrid_prediction
                        for r in records
                    ],
                ),
                "review_count": sum(
                    r.hybrid_review
                    for r in records
                ),
            },
        })

    summary = summarize_records(all_records)

    output = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "mode": "RESEARCH_SIMULATION",
        "configuration": {
            "training_samples_per_seed": (
                TRAINING_SAMPLES
            ),
            "normal_test_samples_per_seed": (
                NORMAL_TEST_SAMPLES
            ),
            "anomaly_test_samples_per_seed": (
                ANOMALY_TEST_SAMPLES
            ),
            "experiment_seeds": EXPERIMENT_SEEDS,
            "bootstrap_samples": BOOTSTRAP_SAMPLES,
            "classical_features": CLASSICAL_FEATURES,
            "quantum_features": QUANTUM_FEATURES,
        },
        "experiments": experiment_results,
        "summary": summary,
        "limitations": [
            "Synthetic events only.",
            "Anomaly distribution is deliberately "
            "different from the normal distribution.",
            "Test datasets are generated independently "
            "from training datasets.",
            "Only three experiment seeds are used.",
            "Hybrid REVIEW is an abstention, not a "
            "confirmed positive detection.",
            "No real-world blockchain attack labels.",
            "No calibration of anomaly scores.",
            "No quantum hardware execution.",
            "No demonstrated quantum advantage.",
        ],
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 70)
    print("OVERALL BENCHMARK RESULTS")
    print("=" * 70)

    for name in [
        "classical",
        "quantum",
        "hybrid_conservative",
    ]:
        metrics = summary[name]

        print()
        print(name.upper())

        print(
            "Accuracy:",
            round(metrics["accuracy"] * 100, 2),
            "%",
        )

        print(
            "Precision:",
            round(metrics["precision"] * 100, 2),
            "%",
        )

        print(
            "Recall:",
            round(metrics["recall"] * 100, 2),
            "%",
        )

        print(
            "F1 Score:",
            round(metrics["f1"] * 100, 2),
            "%",
        )

    print()
    print(
        "Hybrid reviews:",
        summary["hybrid_abstention"]["review_count"],
    )

    print(
        "Model agreement:",
        round(
            summary[
                "classical_quantum_agreement"
            ]["agreement_rate"] * 100,
            2,
        ),
        "%",
    )

    print()
    print("CONFIDENCE INTERVALS")

    for comparison in summary[
        "confidence_intervals"
    ]:
        print(
            comparison["model_a"],
            "vs",
            comparison["model_b"],
            ":",
            comparison["observed_f1_difference_pp"],
            "pp",
        )

        print(
            "95% CI:",
            comparison["ci_95_lower_pp"],
            "to",
            comparison["ci_95_upper_pp"],
            "pp",
        )

    print()
    print(
        "Classical runtime:",
        summary["runtime_ms"]["classical_mean"],
        "ms/event",
    )

    print(
        "Quantum + Fusion runtime:",
        summary["runtime_ms"][
            "quantum_plus_fusion_mean"
        ],
        "ms/event",
    )

    print()
    print("Saved results:", OUTPUT_FILE)

    print()
    print("=" * 70)
    print("V10 RESEARCH BENCHMARK COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
