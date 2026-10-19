
"""
QUANTUM CYBER DEFENSE ARENA
V12.0 - ROBUSTNESS & STRESS TESTING

Research scenarios:
1. Baseline
2. Noisy data
3. Rare anomalies
4. Overlapping anomalies

Existing detectors:
- Classical Isolation Forest
- Quantum State Fidelity Simulator
- Hybrid Fusion

Research simulation only.
"""

from __future__ import annotations

import json
import statistics
import sys

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np


ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.ai_detection.detector import AIThreatDetector
from backend.quantum_detection.quantum_detector import (
    QuantumAnomalyDetector,
)

from research_validation.v11.benchmark_v11 import (
    CLASSICAL_FEATURES,
    QUANTUM_FEATURES,
    classical_scores,
    quantum_scores,
    calculate_metrics,
    validate_configuration,
)


VERSION = "12.0.0"

HERE = Path(__file__).resolve().parent

OUTPUT_FILE = HERE / "robustness_benchmark_v12_results.json"

SEEDS = [101, 202, 303]

TRAIN_SIZE = 800
TEST_SIZE = 200

SCENARIOS = (
    "baseline",
    "noisy",
    "rare_anomalies",
    "overlapping_anomalies",
)

MODELS = (
    "classical",
    "quantum",
    "hybrid",
)


def generate_dataset(
    seed: int,
    scenario: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

    if scenario not in SCENARIOS:
        raise ValueError(
            f"Unknown scenario: {scenario}"
        )

    rng = np.random.default_rng(seed)

    train = rng.normal(
        loc=0.20,
        scale=0.06,
        size=(TRAIN_SIZE, 5),
    )

    anomaly_fraction = (
        0.05
        if scenario == "rare_anomalies"
        else 0.50
    )

    anomaly_count = round(
        TEST_SIZE * anomaly_fraction
    )

    normal_count = TEST_SIZE - anomaly_count

    normal = rng.normal(
        loc=0.23,
        scale=0.12,
        size=(normal_count, 5),
    )

    anomaly_mean = (
        0.36
        if scenario == "overlapping_anomalies"
        else 0.58
    )

    anomalies = rng.normal(
        loc=anomaly_mean,
        scale=0.20,
        size=(anomaly_count, 5),
    )

    X_train = np.clip(
        train,
        0.0,
        1.0,
    )

    X_test = np.clip(
        np.vstack([
            normal,
            anomalies,
        ]),
        0.0,
        1.0,
    )

    y_test = np.asarray(
        [0] * normal_count
        + [1] * anomaly_count,
        dtype=int,
    )

    if scenario == "noisy":
        noise = rng.normal(
            loc=0.0,
            scale=0.12,
            size=X_test.shape,
        )

        X_test = np.clip(
            X_test + noise,
            0.0,
            1.0,
        )

    permutation = rng.permutation(
        len(y_test)
    )

    return (
        X_train,
        X_test[permutation],
        y_test[permutation],
    )


def evaluate_scenario(
    seed: int,
    scenario: str,
) -> dict:

    print()
    print("-" * 65)
    print(
        f"SCENARIO: {scenario.upper()} | SEED: {seed}",
        flush=True,
    )
    print("-" * 65)

    X_train, X_test, y_test = generate_dataset(
        seed,
        scenario,
    )

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

    # Existing V11 hybrid agreement policy.

    agree = classical_pred == quantum_pred

    hybrid_decisions = np.where(
        agree,
        classical_pred,
        -1,
    )

    # REVIEW is treated as negative
    # in the binary F1 calculation.

    hybrid_binary = (
        hybrid_decisions == 1
    ).astype(int)

    fusion_score = (
        0.5 * classical_score
        + 0.5 * quantum_score
    )

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
        hybrid_binary,
    )

    review_rate = float(
        np.mean(~agree)
    )

    result = {
        "seed": seed,
        "scenario": scenario,
        "test_samples": len(y_test),
        "normal_samples": int(
            np.sum(y_test == 0)
        ),
        "anomaly_samples": int(
            np.sum(y_test == 1)
        ),
        "classical": {
            **classical_metrics,
            "runtime_ms": round(
                classical_ms,
                3,
            ),
        },
        "quantum": {
            **quantum_metrics,
            "runtime_ms": round(
                quantum_ms,
                3,
            ),
        },
        "hybrid": {
            **hybrid_metrics,
            "review_rate": round(
                review_rate,
                6,
            ),
            "fusion_score_mean": round(
                float(np.mean(fusion_score)),
                6,
            ),
        },
    }

    for model in MODELS:
        metrics = result[model]

        print(
            f"{model.upper():10s}"
            f" F1={metrics['f1']:.4f}"
            f" PREC={metrics['precision']:.4f}"
            f" RECALL={metrics['recall']:.4f}"
            f" FP={metrics['fp']}"
            f" FN={metrics['fn']}",
            flush=True,
        )

    print(
        f"HYBRID REVIEW RATE: {review_rate:.2%}",
        flush=True,
    )

    return result


def summarize_scenario(
    runs: list[dict],
) -> dict:

    summary = {}

    for model in MODELS:
        model_summary = {}

        for metric in (
            "precision",
            "recall",
            "f1",
            "accuracy",
        ):
            values = [
                float(run[model][metric])
                for run in runs
            ]

            model_summary[metric] = {
                "mean": round(
                    statistics.mean(values),
                    6,
                ),
                "std": round(
                    statistics.stdev(values),
                    6,
                ),
            }

        false_positive_rates = []

        for run in runs:
            fp = run[model]["fp"]
            tn = run[model]["tn"]

            denominator = fp + tn

            false_positive_rates.append(
                fp / denominator
                if denominator
                else 0.0
            )

        model_summary["false_positive_rate"] = {
            "mean": round(
                statistics.mean(
                    false_positive_rates
                ),
                6,
            ),
        }

        if model == "hybrid":
            review_rates = [
                float(
                    run["hybrid"]["review_rate"]
                )
                for run in runs
            ]

            model_summary["review_rate"] = {
                "mean": round(
                    statistics.mean(review_rates),
                    6,
                ),
            }

        else:
            times = [
                float(
                    run[model]["runtime_ms"]
                )
                for run in runs
            ]

            model_summary["runtime_ms"] = {
                "mean": round(
                    statistics.mean(times),
                    3,
                ),
            }

        summary[model] = model_summary

    return summary


def compare_robustness(
    summaries: dict,
) -> dict:

    baseline = summaries["baseline"]

    comparison = {}

    for scenario in SCENARIOS:
        if scenario == "baseline":
            continue

        comparison[scenario] = {}

        for model in MODELS:
            baseline_f1 = (
                baseline[model]["f1"]["mean"]
            )

            scenario_f1 = (
                summaries[scenario][model]["f1"]["mean"]
            )

            difference = scenario_f1 - baseline_f1

            comparison[scenario][model] = {
                "baseline_f1": baseline_f1,
                "scenario_f1": scenario_f1,
                "f1_change": round(
                    difference,
                    6,
                ),
                "change_percentage_points": round(
                    difference * 100,
                    4,
                ),
            }

    return comparison


def print_summary(
    summaries: dict,
    robustness: dict,
) -> None:

    print()
    print("=" * 65)
    print("V12 ROBUSTNESS SUMMARY")
    print("=" * 65)

    for scenario in SCENARIOS:
        print()
        print(
            f"SCENARIO: {scenario.upper()}"
        )

        for model in MODELS:
            metrics = summaries[scenario][model]

            f1 = metrics["f1"]["mean"] * 100

            precision = (
                metrics["precision"]["mean"] * 100
            )

            recall = (
                metrics["recall"]["mean"] * 100
            )

            fpr = (
                metrics["false_positive_rate"]["mean"]
                * 100
            )

            print(
                f"{model.upper():10s} "
                f"F1={f1:.2f}% "
                f"PREC={precision:.2f}% "
                f"RECALL={recall:.2f}% "
                f"FPR={fpr:.2f}%",
            )

    print()
    print("=" * 65)
    print("F1 CHANGE VS BASELINE")
    print("=" * 65)

    for scenario, models in robustness.items():
        print()
        print(scenario.upper())

        for model, values in models.items():
            print(
                f"{model.upper():10s}: "
                f"{values['change_percentage_points']:+.2f}"
                " percentage points"
            )


def main() -> None:
    print()
    print("=" * 65)
    print("QUANTUM CYBER DEFENSE ARENA V12")
    print("ROBUSTNESS & STRESS TESTING")
    print("=" * 65)

    validate_configuration()

    print()
    print("SCENARIOS:", len(SCENARIOS))
    print("SEEDS PER SCENARIO:", len(SEEDS))
    print("TOTAL RUNS:", len(SCENARIOS) * len(SEEDS))
    print("TEST SAMPLES PER RUN:", TEST_SIZE)
    print("MODE: RESEARCH SIMULATION")

    print()
    print(
        "CLASSICAL FEATURES:",
        CLASSICAL_FEATURES,
    )

    print(
        "QUANTUM FEATURES:",
        QUANTUM_FEATURES,
    )

    started = perf_counter()

    all_runs = []
    summaries = {}

    for scenario in SCENARIOS:
        scenario_runs = []

        for seed in SEEDS:
            result = evaluate_scenario(
                seed,
                scenario,
            )

            scenario_runs.append(result)
            all_runs.append(result)

        summaries[scenario] = summarize_scenario(
            scenario_runs
        )

    robustness = compare_robustness(
        summaries
    )

    elapsed = perf_counter() - started

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "mode": "RESEARCH_SIMULATION",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "configuration": {
            "seeds": SEEDS,
            "scenarios": list(SCENARIOS),
            "train_size": TRAIN_SIZE,
            "test_size": TEST_SIZE,
            "total_runs": len(all_runs),
            "total_test_evaluations": (
                len(all_runs) * TEST_SIZE
            ),
            "quantum_threshold": 0.35,
            "hybrid_policy": (
                "agreement-based decision; "
                "disagreement=REVIEW"
            ),
            "review_binary_policy": (
                "REVIEW counted as negative "
                "for binary metrics"
            ),
        },
        "scenario_summary": summaries,
        "robustness_comparison": robustness,
        "runs": all_runs,
        "execution_seconds": round(
            elapsed,
            3,
        ),
        "limitations": [
            "Synthetic datasets only",
            "Classical quantum simulator",
            "Only three seeds per scenario",
            "No demonstrated quantum speedup",
            "No real cybersecurity incidents",
            "Fixed model thresholds",
            "Precision depends on anomaly prevalence",
            "Stress scenarios are simplified",
            "Review decisions are counted as negative",
            "Further real-data validation is required",
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

    print_summary(
        summaries,
        robustness,
    )

    print()
    print("=" * 65)
    print("V12 ROBUSTNESS BENCHMARK COMPLETED")
    print("=" * 65)

    print()
    print(
        "TOTAL EXECUTION TIME:",
        round(elapsed, 2),
        "seconds",
    )

    print()
    print("RESULTS SAVED TO:")
    print(OUTPUT_FILE)

    print()
    print(
        "NOTE: These results are exploratory "
        "and based on synthetic research data."
    )


if __name__ == "__main__":
    main()
