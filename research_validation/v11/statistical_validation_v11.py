
"""
QUANTUM CYBER DEFENSE ARENA V11.1
Statistical Research Validation

Paired comparison of:
- Classical Isolation Forest
- Quantum State Fidelity
- Hybrid Quantum AI Fusion

Reads existing V11 benchmark results.

Research simulation only.
No quantum computational advantage is claimed.
"""

from __future__ import annotations

import itertools
import json
import math
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent

INPUT_FILE = HERE / "benchmark_v11_results.json"

OUTPUT_FILE = (
    HERE / "statistical_validation_v11_results.json"
)

BOOTSTRAP_SAMPLES = 10000
BOOTSTRAP_SEED = 2026
CONFIDENCE_LEVEL = 0.95

MODELS = (
    "classical",
    "quantum",
    "hybrid",
)


def load_results() -> list[dict]:
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            "V11 benchmark results not found:\n"
            f"{INPUT_FILE}\n"
            "Run benchmark_v11.py first."
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    runs = data.get("runs")

    if not isinstance(runs, list) or len(runs) < 2:
        raise ValueError(
            "At least two benchmark runs are required."
        )

    for run in runs:
        for model in MODELS:
            if model not in run:
                raise ValueError(
                    f"Missing model: {model}"
                )

            value = float(run[model]["f1"])

            if not math.isfinite(value):
                raise ValueError(
                    f"Invalid F1 score for {model}"
                )

            if not 0 <= value <= 1:
                raise ValueError(
                    f"F1 score outside [0, 1]: {model}"
                )

    return runs


def extract_f1(
    runs: list[dict],
    model: str,
) -> list[float]:
    return [
        float(run[model]["f1"])
        for run in runs
    ]


def percentile(
    values: list[float],
    probability: float,
) -> float:
    ordered = sorted(values)

    if not ordered:
        raise ValueError("Empty sample.")

    position = probability * (len(ordered) - 1)

    low = math.floor(position)
    high = math.ceil(position)

    if low == high:
        return ordered[low]

    fraction = position - low

    return (
        ordered[low] * (1 - fraction)
        + ordered[high] * fraction
    )


def bootstrap_mean_ci(
    differences: list[float],
) -> tuple[float, float]:
    """
    Paired bootstrap confidence interval.

    Resamples whole benchmark-run differences,
    preserving the pairing between models.
    """

    rng = random.Random(BOOTSTRAP_SEED)

    n = len(differences)

    means = []

    for _ in range(BOOTSTRAP_SAMPLES):
        sample = [
            differences[rng.randrange(n)]
            for _ in range(n)
        ]

        means.append(statistics.mean(sample))

    alpha = 1.0 - CONFIDENCE_LEVEL

    return (
        percentile(means, alpha / 2),
        percentile(means, 1 - alpha / 2),
    )


def exact_sign_flip_test(
    differences: list[float],
) -> float:
    """
    Two-sided paired sign-flip randomization test.

    Enumerates all 2^n sign assignments.

    Assumes sign-exchangeability of paired
    differences under the null hypothesis.
    """

    observed = abs(statistics.mean(differences))

    count_extreme = 0
    count_total = 0

    for signs in itertools.product(
        (-1, 1),
        repeat=len(differences),
    ):
        simulated = statistics.mean(
            difference * sign
            for difference, sign in zip(
                differences,
                signs,
            )
        )

        if abs(simulated) >= observed - 1e-12:
            count_extreme += 1

        count_total += 1

    return count_extreme / count_total


def compare_models(
    runs: list[dict],
    model_a: str,
    model_b: str,
) -> dict:
    scores_a = extract_f1(runs, model_a)
    scores_b = extract_f1(runs, model_b)

    differences = [
        a - b
        for a, b in zip(scores_a, scores_b)
    ]

    mean_difference = statistics.mean(differences)

    ci_low, ci_high = bootstrap_mean_ci(differences)

    p_value = exact_sign_flip_test(differences)

    wins = sum(
        difference > 1e-12
        for difference in differences
    )

    losses = sum(
        difference < -1e-12
        for difference in differences
    )

    ties = len(differences) - wins - losses

    return {
        "model_a": model_a,
        "model_b": model_b,
        "sample_count": len(differences),
        "mean_f1_a": round(
            statistics.mean(scores_a),
            6,
        ),
        "mean_f1_b": round(
            statistics.mean(scores_b),
            6,
        ),
        "mean_f1_difference": round(
            mean_difference,
            6,
        ),
        "difference_percentage_points": round(
            mean_difference * 100,
            4,
        ),
        "bootstrap_ci_95": [
            round(ci_low, 6),
            round(ci_high, 6),
        ],
        "exact_sign_flip_p_value": round(
            p_value,
            6,
        ),
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "paired_differences": [
            round(value, 6)
            for value in differences
        ],
        "exploratory": True,
    }


def model_summary(
    runs: list[dict],
    model: str,
) -> dict:
    values = extract_f1(runs, model)

    return {
        "mean_f1": round(
            statistics.mean(values),
            6,
        ),
        "std_f1": round(
            statistics.stdev(values),
            6,
        ),
        "minimum_f1": round(
            min(values),
            6,
        ),
        "maximum_f1": round(
            max(values),
            6,
        ),
    }


def main() -> None:
    print()
    print("=" * 65)
    print("QUANTUM CYBER DEFENSE ARENA V11.1")
    print("STATISTICAL RESEARCH VALIDATION")
    print("=" * 65)

    runs = load_results()

    print()
    print("BENCHMARK RUNS:", len(runs))

    summaries = {
        model: model_summary(runs, model)
        for model in MODELS
    }

    comparisons = [
        compare_models(
            runs,
            "hybrid",
            "quantum",
        ),
        compare_models(
            runs,
            "hybrid",
            "classical",
        ),
        compare_models(
            runs,
            "quantum",
            "classical",
        ),
    ]

    print()
    print("AVERAGE F1 SCORES:")
    print("-" * 65)

    for model in MODELS:
        mean_f1 = summaries[model]["mean_f1"]

        print(
            f"{model.upper():12s}: "
            f"{mean_f1 * 100:.2f}%"
        )

    print()
    print("PAIRED STATISTICAL COMPARISONS:")
    print("-" * 65)

    for result in comparisons:
        print()
        print(
            result["model_a"].upper(),
            "VS",
            result["model_b"].upper(),
        )

        print(
            "F1 DIFFERENCE:",
            result["difference_percentage_points"],
            "percentage points",
        )

        print(
            "95% BOOTSTRAP CI:",
            result["bootstrap_ci_95"],
        )

        print(
            "EXACT SIGN-FLIP P-VALUE:",
            result["exact_sign_flip_p_value"],
        )

        print(
            "WINS / LOSSES / TIES:",
            result["wins"],
            "/",
            result["losses"],
            "/",
            result["ties"],
        )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "11.1.0",
        "mode": "RESEARCH_SIMULATION",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "input_file": INPUT_FILE.name,
        "benchmark_runs": len(runs),
        "model_summaries": summaries,
        "comparisons": comparisons,
        "methodology": {
            "paired_by": "benchmark run",
            "bootstrap_samples": BOOTSTRAP_SAMPLES,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "confidence_level": CONFIDENCE_LEVEL,
            "hypothesis_test": (
                "two-sided exact paired sign-flip"
            ),
            "limitations": [
                "Only five benchmark runs",
                "Synthetic data distributions",
                "Classical quantum simulation",
                "Bootstrap intervals may be unstable",
                "Repeated seeds do not establish "
                "external generalization",
                "Sign-flip test assumes exchangeable signs",
                "Results are exploratory",
                "No proven quantum computational advantage",
            ],
        },
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
    print("=" * 65)
    print("V11.1 STATISTICAL VALIDATION COMPLETED")
    print("=" * 65)

    print()
    print("RESULTS SAVED TO:")
    print(OUTPUT_FILE)

    print()
    print(
        "NOTE: With five paired runs, a two-sided exact "
        "sign-flip test cannot reach p < 0.05. "
        "More independent benchmark runs are needed."
    )


if __name__ == "__main__":
    main()
