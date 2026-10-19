
"""
QUANTUM CYBER DEFENSE ARENA V10.1
Advanced Overlapping-Data Research Benchmark

Classical Isolation Forest vs Quantum State Fidelity
vs Hybrid Quantum AI Fusion.

Research simulation only.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ai_detection.detector import AIThreatDetector
from backend.fusion_engine.fusion_engine import (
    ClassicalPrediction,
    QuantumAIThreatFusionEngine,
)
from research_validation.benchmark_v10 import (
    CLASSICAL_FEATURES,
    QUANTUM_FEATURES,
    ExperimentRecord,
    calculate_metrics,
    create_training_data,
    normalize_classical_score,
    summarize_records,
    validate_mapping,
)

VERSION = "10.1.0"

SEEDS = [42, 123, 2026]
NORMAL_SAMPLES = 60
ANOMALY_SAMPLES = 60

OUTPUT_FILE = (
    ROOT
    / "research_validation"
    / "benchmark_v10_1_results.json"
)


def create_hard_events(seed: int) -> list[dict]:
    """Generate overlapping synthetic normal/anomaly classes."""

    rng = np.random.default_rng(seed + 20000)
    feature_count = len(CLASSICAL_FEATURES)

    normal = rng.normal(
        loc=0.40,
        scale=0.16,
        size=(NORMAL_SAMPLES, feature_count),
    )

    anomaly = rng.normal(
        loc=0.55,
        scale=0.16,
        size=(ANOMALY_SAMPLES, feature_count),
    )

    data = np.clip(
        np.concatenate([normal, anomaly]),
        0.0,
        1.0,
    )

    labels = np.array(
        [0] * NORMAL_SAMPLES
        + [1] * ANOMALY_SAMPLES,
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
        row = data[sample_index]

        event = {
            "id": f"V101-{seed}-{index:04d}",
            "network": networks[index % len(networks)],
            "true_label": int(labels[sample_index]),
        }

        for name, value in zip(CLASSICAL_FEATURES, row):
            event[name] = float(value)

        events.append(event)

    return events


def run_experiment(seed: int) -> list[ExperimentRecord]:
    print()
    print("=" * 65)
    print(f"V10.1 EXPERIMENT SEED: {seed}")
    print("=" * 65)

    classical = AIThreatDetector(seed=seed)
    training_data = create_training_data(seed)
    classical.train(training_data)

    fusion = QuantumAIThreatFusionEngine()
    test_events = create_hard_events(seed)

    records = []

    for event in test_events:
        classical_start = perf_counter()
        result = classical.predict_event(event)
        classical_time = (
            perf_counter() - classical_start
        ) * 1000.0

        if result["classification"] == "INSUFFICIENT_DATA":
            raise RuntimeError(
                f"Missing features: {event['id']}"
            )

        classical_score = normalize_classical_score(
            result["decision_function"]
        )

        classical_anomaly = bool(result["is_anomaly"])

        classical_prediction = ClassicalPrediction(
            anomaly_score=classical_score,
            is_anomaly=classical_anomaly,
            model="IsolationForest-V2",
        )

        quantum_features = [
            float(event[name])
            for name in QUANTUM_FEATURES
        ]

        quantum_start = perf_counter()

        fused = fusion.analyze(
            event_id=event["id"],
            network=event["network"],
            features=quantum_features,
            classical_prediction=classical_prediction,
        )

        quantum_fusion_time = (
            perf_counter() - quantum_start
        ) * 1000.0

        records.append(
            ExperimentRecord(
                seed=seed,
                event_id=event["id"],
                true_label=int(event["true_label"]),
                classical_prediction=int(classical_anomaly),
                quantum_prediction=int(fused.quantum_anomaly),
                hybrid_prediction=int(
                    fused.classification == "ANOMALY"
                ),
                hybrid_review=(
                    fused.classification == "REVIEW"
                ),
                classical_score=classical_score,
                quantum_score=float(fused.quantum_score),
                hybrid_score=float(fused.fusion_score),
                classical_runtime_ms=classical_time,
                quantum_hybrid_runtime_ms=quantum_fusion_time,
            )
        )

    print("Training samples:", len(training_data))
    print("Hard test samples:", len(records))
    print(
        "Hybrid REVIEW cases:",
        sum(record.hybrid_review for record in records),
    )

    return records


def print_metrics(name: str, metrics: dict) -> None:
    print()
    print(name)
    print("-" * 45)

    for key in ("accuracy", "precision", "recall", "f1"):
        print(
            f"{key.upper():12s}: "
            f"{metrics[key] * 100:.2f}%"
        )

    matrix = metrics["confusion_matrix"]

    print("TP:", matrix["TP"])
    print("TN:", matrix["TN"])
    print("FP:", matrix["FP"])
    print("FN:", matrix["FN"])


def main() -> None:
    print()
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA V10.1")
    print("ADVANCED OVERLAPPING-DATA VALIDATION")
    print("=" * 70)

    validate_mapping()

    all_records = []

    for seed in SEEDS:
        all_records.extend(run_experiment(seed))

    summary = summarize_records(all_records)

    output = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "mode": "RESEARCH_SIMULATION",
        "dataset": "OVERLAPPING_SYNTHETIC_CLASSES",
        "configuration": {
            "seeds": SEEDS,
            "training_samples_per_seed": 800,
            "normal_test_samples_per_seed": NORMAL_SAMPLES,
            "anomaly_test_samples_per_seed": ANOMALY_SAMPLES,
            "normal_mean": 0.40,
            "anomaly_mean": 0.55,
            "standard_deviation": 0.16,
        },
        "summary": summary,
        "limitations": [
            "Synthetic labeled events only.",
            "Training and testing distributions differ.",
            "Class distributions deliberately overlap.",
            "Only three experiment seeds.",
            "No real-world attack labels.",
            "Quantum calculations use a simulator.",
            "Hybrid REVIEW is an abstention.",
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
    print("V10.1 OVERALL RESULTS")
    print("=" * 70)

    print_metrics(
        "CLASSICAL ISOLATION FOREST",
        summary["classical"],
    )

    print_metrics(
        "QUANTUM STATE FIDELITY",
        summary["quantum"],
    )

    print_metrics(
        "HYBRID QUANTUM AI",
        summary["hybrid_conservative"],
    )

    abstention = summary["hybrid_abstention"]

    print()
    print("HYBRID REVIEW STATISTICS")
    print("Reviews:", abstention["review_count"])
    print(
        "Review rate:",
        f"{abstention['review_rate'] * 100:.2f}%",
    )
    print(
        "Decisive coverage:",
        f"{abstention['decisive_coverage'] * 100:.2f}%",
    )

    print()
    print("95% BOOTSTRAP CONFIDENCE INTERVALS")

    for item in summary["confidence_intervals"]:
        print()
        print(item["model_a"], "vs", item["model_b"])
        print(
            "F1 difference:",
            item["observed_f1_difference_pp"],
            "pp",
        )
        print(
            "95% CI:",
            item["ci_95_lower_pp"],
            "to",
            item["ci_95_upper_pp"],
            "pp",
        )

    runtime = summary["runtime_ms"]

    print()
    print("RUNTIME")
    print(
        "Classical:",
        runtime["classical_mean"],
        "ms/event",
    )
    print(
        "Quantum + Fusion:",
        runtime["quantum_plus_fusion_mean"],
        "ms/event",
    )

    print()
    print("Results saved:", OUTPUT_FILE)
    print()
    print("=" * 70)
    print("V10.1 ADVANCED VALIDATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
