
"""
QUANTUM CYBER DEFENSE ARENA V11.2
Extended Research Benchmark - 30 Runs

Models:
1. Classical Isolation Forest
2. Quantum State Fidelity Detector
3. Hybrid Quantum AI Fusion

Uses the existing V11 benchmark functions.

Research simulation only.
No real attacks or quantum speedup claims.
"""

from __future__ import annotations

import json
import random
import statistics
import sys

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from research_validation.v11.benchmark_v11 import (
    run_single_benchmark,
    summarize,
    validate_configuration,
)


VERSION = "11.2.0"

SEEDS = list(range(101, 131))

BOOTSTRAP_ITERATIONS = 10000
PERMUTATION_ITERATIONS = 20000

RANDOM_SEED = 2026

OUTPUT_FILE = (
    Path(__file__).resolve().parent
    / "benchmark_v11_2_results.json"
)

MODELS = (
    "classical",
    "quantum",
    "hybrid",
)


def bootstrap_confidence_interval(
    differences: list[float],
    iterations: int = BOOTSTRAP_ITERATIONS,
) -> list[float]:
    """
    Paired bootstrap confidence interval
    for the mean F1 difference.
    """

    rng = np.random.default_rng(RANDOM_SEED)

    values = np.asarray(differences, dtype=float)

    if len(values) < 2:
        raise ValueError(
            "At least two paired runs are required."
        )

    bootstrap_means = np.empty(
        iterations,
        dtype=float,
    )

    for index in range(iterations):
        sample = rng.choice(
            values,
            size=len(values),
            replace=True,
        )

        bootstrap_means[index] = float(
            np.mean(sample)
        )

    lower, upper = np.quantile(
        bootstrap_means,
        [0.025, 0.975],
    )

    return [
        round(float(lower), 6),
        round(float(upper), 6),
    ]


def paired_permutation_test(
    differences: list[float],
    iterations: int = PERMUTATION_ITERATIONS,
) -> float:
    """
    Approximate two-sided paired sign-flip test.

    Suitable for 30 paired observations,
    where exhaustive enumeration would
    require 2**30 permutations.

    Assumes exchangeability of difference signs
    under the null hypothesis.
    """

    rng = random.Random(RANDOM_SEED)

    observed = abs(
        statistics.mean(differences)
    )

    extreme = 0

    for _ in range(iterations):
        simulated = statistics.mean(
            difference * rng.choice((-1, 1))
            for difference in differences
        )

        if abs(simulated) >= observed - 1e-12:
            extreme += 1

    return round(
        (extreme + 1) / (iterations + 1),
        6,
    )


def compare_models(
    results: list[dict],
    model_a: str,
    model_b: str,
) -> dict:
    """
    Compare F1 scores from matching
    benchmark seeds.
    """

    differences = [
        float(result[model_a]["f1"])
        - float(result[model_b]["f1"])
        for result in results
    ]

    mean_difference = statistics.mean(
        differences
    )

    confidence_interval = (
        bootstrap_confidence_interval(
            differences
        )
    )

    p_value = paired_permutation_test(
        differences
    )

    wins = sum(
        difference > 1e-12
        for difference in differences
    )

    losses = sum(
        difference < -1e-12
        for difference in differences
    )

    ties = (
        len(differences)
        - wins
        - losses
    )

    return {
        "model_a": model_a,
        "model_b": model_b,
        "paired_runs": len(differences),
        "mean_f1_difference": round(
            mean_difference,
            6,
        ),
        "difference_percentage_points": round(
            mean_difference * 100,
            4,
        ),
        "bootstrap_ci_95": confidence_interval,
        "permutation_p_value": p_value,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "paired_differences": [
            round(value, 6)
            for value in differences
        ],
    }


def print_model_summary(
    summary: dict,
) -> None:
    print()
    print("=" * 65)
    print("V11.2 MODEL PERFORMANCE")
    print("=" * 65)

    for model in MODELS:
        metrics = summary[model]

        print()
        print(model.upper())

        print(
            "PRECISION:",
            round(
                metrics["precision"]["mean"] * 100,
                2,
            ),
            "%",
        )

        print(
            "RECALL:",
            round(
                metrics["recall"]["mean"] * 100,
                2,
            ),
            "%",
        )

        print(
            "F1 SCORE:",
            round(
                metrics["f1"]["mean"] * 100,
                2,
            ),
            "%",
        )

        print(
            "ACCURACY:",
            round(
                metrics["accuracy"]["mean"] * 100,
                2,
            ),
            "%",
        )

        if model == "hybrid":
            print(
                "REVIEW RATE:",
                round(
                    metrics["review_rate"]["mean"] * 100,
                    2,
                ),
                "%",
            )
        else:
            print(
                "INFERENCE RUNTIME:",
                metrics["runtime_ms"]["mean"],
                "ms per test batch",
            )


def print_comparisons(
    comparisons: list[dict],
) -> None:
    print()
    print("=" * 65)
    print("V11.2 PAIRED STATISTICAL COMPARISONS")
    print("=" * 65)

    for comparison in comparisons:
        print()

        print(
            comparison["model_a"].upper(),
            "VS",
            comparison["model_b"].upper(),
        )

        print(
            "F1 DIFFERENCE:",
            comparison[
                "difference_percentage_points"
            ],
            "percentage points",
        )

        print(
            "95% BOOTSTRAP CI:",
            comparison["bootstrap_ci_95"],
        )

        print(
            "PERMUTATION P-VALUE:",
            comparison["permutation_p_value"],
        )

        print(
            "WINS / LOSSES / TIES:",
            comparison["wins"],
            "/",
            comparison["losses"],
            "/",
            comparison["ties"],
        )


def main() -> None:
    print()
    print("=" * 65)
    print("QUANTUM CYBER DEFENSE ARENA V11.2")
    print("EXTENDED QUANTUM AI RESEARCH BENCHMARK")
    print("=" * 65)

    print()
    print("BENCHMARK RUNS:", len(SEEDS))
    print("TEST SAMPLES PER RUN: 200")
    print("TRAINING SAMPLES PER RUN: 800")
    print("MODE: SYNTHETIC RESEARCH")
    print()

    validate_configuration()

    started = perf_counter()

    results = []

    for index, seed in enumerate(SEEDS, start=1):
        print()
        print(
            f"RUN {index}/{len(SEEDS)}"
        )

        result = run_single_benchmark(seed)

        results.append(result)

    elapsed_seconds = (
        perf_counter() - started
    )

    summary = summarize(results)

    comparisons = [
        compare_models(
            results,
            "hybrid",
            "quantum",
        ),
        compare_models(
            results,
            "hybrid",
            "classical",
        ),
        compare_models(
            results,
            "quantum",
            "classical",
        ),
    ]

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "mode": "RESEARCH_SIMULATION",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "benchmark": {
            "runs": len(SEEDS),
            "seeds": SEEDS,
            "train_samples_per_run": 800,
            "test_samples_per_run": 200,
            "total_test_evaluations": (
                len(SEEDS) * 200
            ),
            "elapsed_seconds": round(
                elapsed_seconds,
                3,
            ),
        },
        "models": {
            "classical": "Isolation Forest",
            "quantum": (
                "Quantum State Fidelity Simulator"
            ),
            "hybrid": (
                "50/50 score fusion; "
                "agreement-based decision"
            ),
        },
        "summary": summary,
        "comparisons": comparisons,
        "runs": results,
        "statistical_methodology": {
            "pairing": "identical benchmark seeds",
            "bootstrap_iterations": (
                BOOTSTRAP_ITERATIONS
            ),
            "permutation_iterations": (
                PERMUTATION_ITERATIONS
            ),
            "random_seed": RANDOM_SEED,
            "confidence_level": 0.95,
            "hypothesis_test": (
                "two-sided Monte Carlo "
                "paired sign-flip test"
            ),
            "review_policy": (
                "REVIEW counted as negative "
                "for binary F1; review rate "
                "reported separately"
            ),
        },
        "limitations": [
            "Synthetic datasets only",
            "Quantum algorithm uses a classical simulator",
            "No demonstrated quantum computational advantage",
            "Repeated synthetic seeds are not real-world validation",
            "F1 depends on the generated class distributions",
            "Hybrid REVIEW policy affects reported metrics",
            "Bootstrap and permutation results are exploratory",
            "Model thresholds were not independently calibrated",
            "Statistical significance does not prove deployment utility",
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

    print_model_summary(summary)

    print_comparisons(comparisons)

    print()
    print("=" * 65)
    print("V11.2 EXTENDED BENCHMARK COMPLETED")
    print("=" * 65)

    print()
    print(
        "TOTAL EXECUTION TIME:",
        round(elapsed_seconds, 2),
        "seconds",
    )

    print()
    print("RESULTS SAVED TO:")
    print(OUTPUT_FILE)

    print()
    print("RESEARCH LIMITATION:")
    print(
        "Results are based on synthetic datasets "
        "and classical quantum simulation."
    )


if __name__ == "__main__":
    main()
