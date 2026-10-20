
"""
QUANTUM CYBER DEFENSE ARENA
V18.5 - STATISTICAL VALIDATION

Statistical analysis of V18.4 results:

1. Artifact and sample consistency
2. Spearman rank correlation
3. Bootstrap confidence interval
4. Permutation test
5. Exact hypergeometric Top-K overlap test
6. Leave-one-out sensitivity
7. JSON and CSV research outputs

Standard Python library only.

IMPORTANT:
- Only 20 transaction samples.
- No verified cyberattack labels.
- No claims of quantum advantage.
- Exploratory statistical analysis only.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
import sys

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V17 = ROOT / "research_validation" / "v17"
V18 = ROOT / "research_validation" / "v18"

DATASET = V17 / "training_features_v17_1.csv"

COMPARISON_REPORT = (
    V18 / "quantum_classical_comparison_v18_4_results.json"
)

COMPARISON_CSV = (
    V18 / "quantum_classical_comparison_v18_4_scores.csv"
)

OUTPUT_JSON = (
    V18 / "statistical_validation_v18_5_results.json"
)

OUTPUT_CSV = (
    V18 / "statistical_validation_v18_5_sensitivity.csv"
)

BOOTSTRAP_ITERATIONS = 2000
PERMUTATION_ITERATIONS = 5000
RANDOM_SEED = 42

ALPHA = 0.05
TOLERANCE = 1e-5

CHECKS = []


def check(name, condition, details=""):
    passed = bool(condition)

    CHECKS.append({
        "name": name,
        "passed": passed,
        "details": str(details),
    })

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")

    if not passed and details:
        print(f"       {details}")

    return passed


def read_json(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        return json.load(handle)


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)

    if not fields or not rows:
        raise ValueError(
            f"Missing CSV data: {path.name}"
        )

    if len(set(fields)) != len(fields):
        raise ValueError(
            f"Duplicate CSV columns: {path.name}"
        )

    return fields, rows


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def numeric(value):
    result = float(value)

    if not math.isfinite(result):
        raise ValueError(
            "Non-finite statistical input."
        )

    return result


def average_ranks(values):
    length = len(values)

    order = sorted(
        range(length),
        key=lambda index: values[index],
    )

    ranks = [0.0] * length
    position = 0

    while position < length:
        end = position + 1

        while (
            end < length
            and values[order[end]] == values[order[position]]
        ):
            end += 1

        rank = (position + 1 + end) / 2.0

        for index in range(position, end):
            ranks[order[index]] = rank

        position = end

    return ranks


def pearson(first, second):
    if len(first) != len(second) or len(first) < 3:
        return None

    mean_a = statistics.mean(first)
    mean_b = statistics.mean(second)

    centered_a = [
        x - mean_a for x in first
    ]

    centered_b = [
        x - mean_b for x in second
    ]

    numerator = sum(
        a * b
        for a, b in zip(centered_a, centered_b)
    )

    variance_a = sum(
        a * a for a in centered_a
    )

    variance_b = sum(
        b * b for b in centered_b
    )

    denominator = math.sqrt(
        variance_a * variance_b
    )

    if denominator < 1e-14:
        return None

    return max(
        -1.0,
        min(1.0, numerator / denominator),
    )


def spearman(first, second):
    return pearson(
        average_ranks(first),
        average_ranks(second),
    )


def percentile(sorted_values, fraction):
    if not sorted_values:
        return None

    position = fraction * (
        len(sorted_values) - 1
    )

    lower = math.floor(position)
    upper = math.ceil(position)

    weight = position - lower

    return (
        sorted_values[lower] * (1.0 - weight)
        + sorted_values[upper] * weight
    )


def bootstrap_test(first, second):
    rng = random.Random(RANDOM_SEED)
    count = len(first)

    estimates = []
    invalid = 0

    for _ in range(BOOTSTRAP_ITERATIONS):
        indexes = [
            rng.randrange(count)
            for _ in range(count)
        ]

        sample_a = [
            first[index] for index in indexes
        ]

        sample_b = [
            second[index] for index in indexes
        ]

        value = spearman(
            sample_a,
            sample_b,
        )

        if value is None:
            invalid += 1
        else:
            estimates.append(value)

    estimates.sort()

    if len(estimates) < BOOTSTRAP_ITERATIONS * 0.9:
        raise ValueError(
            "Too many invalid bootstrap samples."
        )

    return {
        "iterations_requested": BOOTSTRAP_ITERATIONS,
        "iterations_valid": len(estimates),
        "iterations_invalid": invalid,
        "confidence_level": 0.95,
        "ci_lower": percentile(estimates, 0.025),
        "ci_upper": percentile(estimates, 0.975),
        "bootstrap_mean": statistics.mean(estimates),
        "method": "paired_percentile_bootstrap",
    }


def permutation_test(first, second, observed):
    rng = random.Random(RANDOM_SEED + 1)

    shuffled = list(second)
    extreme_count = 0

    for _ in range(PERMUTATION_ITERATIONS):
        rng.shuffle(shuffled)

        value = spearman(
            first,
            shuffled,
        )

        if value is not None and (
            abs(value) >= abs(observed) - 1e-12
        ):
            extreme_count += 1

    # Monte Carlo p-value with plus-one correction.
    p_value = (
        extreme_count + 1
    ) / (
        PERMUTATION_ITERATIONS + 1
    )

    return {
        "iterations": PERMUTATION_ITERATIONS,
        "extreme_permutations": extreme_count,
        "p_value_two_sided": p_value,
        "method": "paired_rank_permutation_test",
        "null_hypothesis": (
            "Scores are exchangeable across "
            "sample associations"
        ),
    }


def top_k_indexes(scores, k):
    order = sorted(
        range(len(scores)),
        key=lambda index: (-scores[index], index),
    )

    return {
        index + 1 for index in order[:k]
    }


def hypergeometric_tail(
    population,
    first_size,
    second_size,
    overlap,
):
    """
    Exact probability of overlap >= observed
    for two independent uniformly random sets.
    """

    denominator = math.comb(
        population,
        second_size,
    )

    probability = 0.0

    maximum = min(
        first_size,
        second_size,
    )

    for shared in range(
        overlap,
        maximum + 1,
    ):
        outside = second_size - shared

        if not 0 <= outside <= population - first_size:
            continue

        ways = (
            math.comb(first_size, shared)
            * math.comb(
                population - first_size,
                outside,
            )
        )

        probability += ways / denominator

    return min(
        1.0,
        probability,
    )


def leave_one_out(first, second, indexes):
    results = []
    correlations = []

    for removed in range(len(first)):
        sample_a = [
            value
            for index, value in enumerate(first)
            if index != removed
        ]

        sample_b = [
            value
            for index, value in enumerate(second)
            if index != removed
        ]

        correlation = spearman(
            sample_a,
            sample_b,
        )

        if correlation is None:
            raise ValueError(
                "Leave-one-out correlation undefined."
            )

        correlations.append(correlation)

        results.append({
            "removed_sample_index": indexes[removed],
            "spearman_correlation": correlation,
        })

    return results, {
        "min": min(correlations),
        "max": max(correlations),
        "mean": statistics.mean(correlations),
        "range": max(correlations) - min(correlations),
    }


def write_sensitivity_csv(results):
    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow([
            "removed_sample_index",
            "spearman_correlation",
        ])

        for row in results:
            writer.writerow([
                row["removed_sample_index"],
                round(
                    row["spearman_correlation"],
                    10,
                ),
            ])


def rounded(value):
    if value is None:
        return None

    return round(
        float(value),
        8,
    )


def main():
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V18.5 - STATISTICAL VALIDATION")
    print("=" * 68)

    V18.mkdir(
        parents=True,
        exist_ok=True,
    )

    required = [
        DATASET,
        COMPARISON_REPORT,
        COMPARISON_CSV,
    ]

    for path in required:
        check(
            f"Required file: {path.name}",
            path.is_file(),
        )

    if not all(path.is_file() for path in required):
        raise FileNotFoundError(
            "Required V18 research files missing."
        )

    comparison = read_json(
        COMPARISON_REPORT
    )

    fields, rows = read_csv(
        COMPARISON_CSV
    )

    required_columns = {
        "sample_index",
        "classical_anomaly_score",
        "quantum_novelty_score",
    }

    if not required_columns.issubset(set(fields)):
        raise ValueError(
            "Comparison CSV has missing columns."
        )

    indexes = []
    classical = []
    quantum = []

    for row in rows:
        indexes.append(
            int(row["sample_index"])
        )

        classical.append(
            numeric(row["classical_anomaly_score"])
        )

        quantum.append(
            numeric(row["quantum_novelty_score"])
        )

    n = len(rows)

    check(
        "V18.4 comparison PASS",
        comparison.get("status") == "COMPARISON_PASS"
        and comparison.get("checks_failed") == 0,
    )

    check(
        "Sample indexes are sequential",
        indexes == list(range(1, n + 1)),
    )

    check(
        "Sample count matches V18.4",
        n == comparison.get("dataset", {}).get("samples"),
    )

    check(
        "Dataset SHA-256 matches",
        sha256_file(DATASET)
        == comparison.get("dataset", {}).get("sha256"),
    )

    check(
        "Sufficient samples for exploratory test",
        n >= 10,
    )

    if not all(item["passed"] for item in CHECKS):
        raise ValueError(
            "Statistical validation input checks failed."
        )

    observed = spearman(
        classical,
        quantum,
    )

    if observed is None:
        raise ValueError(
            "Spearman correlation undefined."
        )

    reported = comparison.get(
        "comparison", {}
    )

    check(
        "Spearman reproduces V18.4",
        math.isclose(
            observed,
            numeric(
                reported["spearman_rank_correlation"]
            ),
            abs_tol=TOLERANCE,
        ),
    )

    top_k = int(
        reported["top_k"]
    )

    if not 1 <= top_k <= n:
        raise ValueError("Invalid Top-K value.")

    classical_top = top_k_indexes(
        classical,
        top_k,
    )

    quantum_top = top_k_indexes(
        quantum,
        top_k,
    )

    overlap = len(
        classical_top & quantum_top
    )

    check(
        "Top-K overlap reproduces V18.4",
        overlap == reported["top_k_overlap"],
    )

    check(
        "Top-K sets reproduce V18.4",
        sorted(classical_top)
        == reported["classical_top_k"]
        and sorted(quantum_top)
        == reported["quantum_top_k"],
    )

    if not all(item["passed"] for item in CHECKS):
        raise ValueError(
            "Statistical consistency checks failed."
        )

    print()
    print("RUNNING BOOTSTRAP...")
    bootstrap = bootstrap_test(
        classical,
        quantum,
    )

    print("RUNNING PERMUTATION TEST...")
    permutation = permutation_test(
        classical,
        quantum,
        observed,
    )

    print("RUNNING TOP-K EXACT TEST...")
    top_p_value = hypergeometric_tail(
        n,
        top_k,
        top_k,
        overlap,
    )

    print("RUNNING LEAVE-ONE-OUT ANALYSIS...")
    loo_results, loo_summary = leave_one_out(
        classical,
        quantum,
        indexes,
    )

    check(
        "Bootstrap confidence interval valid",
        bootstrap["ci_lower"]
        <= bootstrap["ci_upper"]
        and -1.0 <= bootstrap["ci_lower"] <= 1.0
        and -1.0 <= bootstrap["ci_upper"] <= 1.0,
    )

    check(
        "Permutation p-value valid",
        0.0 <= permutation["p_value_two_sided"] <= 1.0,
    )

    check(
        "Hypergeometric p-value valid",
        0.0 <= top_p_value <= 1.0,
    )

    check(
        "Leave-one-out calculations complete",
        len(loo_results) == n,
    )

    write_sensitivity_csv(
        loo_results
    )

    passed = sum(
        item["passed"] for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "STATISTICAL_VALIDATION_PASS"
        if failed == 0
        else "STATISTICAL_VALIDATION_FAIL"
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V18.5",
        "module": "Statistical Validation",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "dataset": {
            "samples": n,
            "sha256": sha256_file(DATASET),
            "source": str(DATASET.relative_to(ROOT)),
        },
        "methods": {
            "classical": "IsolationForest",
            "quantum": "Qiskit Fidelity Kernel Novelty",
        },
        "spearman": {
            "observed_correlation": rounded(observed),
            "bootstrap": {
                key: rounded(value)
                if isinstance(value, float)
                else value
                for key, value in bootstrap.items()
            },
            "permutation": {
                key: rounded(value)
                if isinstance(value, float)
                else value
                for key, value in permutation.items()
            },
        },
        "top_k": {
            "k": top_k,
            "observed_overlap": overlap,
            "expected_overlap_under_random_sets": rounded(
                top_k * top_k / n
            ),
            "hypergeometric_tail_p_value": rounded(
                top_p_value
            ),
            "null_model": (
                "Independent uniformly random Top-K "
                "sets from the same population"
            ),
        },
        "leave_one_out": {
            key: rounded(value)
            for key, value in loo_summary.items()
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "research_limitations": [
            "Only 20 transaction observations.",
            "No verified malicious transaction labels.",
            "Scores were calculated on training data.",
            "Bootstrap resamples score pairs, not "
            "the full model-training procedure.",
            "Transactions may not be independent.",
            "Permutation inference assumes "
            "exchangeability under its null.",
            "Hypergeometric test assumes independent "
            "uniformly random Top-K sets under its null.",
            "P-values measure null-model compatibility, "
            "not detection accuracy or effect importance.",
            "Exploratory p-values are not corrected "
            "for multiple testing.",
            "No quantum computational advantage "
            "or accuracy superiority demonstrated.",
        ],
        "outputs": {
            "report_json": str(
                OUTPUT_JSON.relative_to(ROOT)
            ),
            "sensitivity_csv": str(
                OUTPUT_CSV.relative_to(ROOT)
            ),
        },
        "next_stage": (
            "V18.6 Research Release and Dashboard"
        ),
    }

    with OUTPUT_JSON.open(
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

    print()
    print("=" * 68)
    print("V18.5 STATISTICAL RESULTS")
    print("=" * 68)

    print(f"SAMPLES: {n}")
    print(f"SPEARMAN CORRELATION: {observed:.6f}")

    print(
        "BOOTSTRAP 95% CI: "
        f"[{bootstrap['ci_lower']:.6f}, "
        f"{bootstrap['ci_upper']:.6f}]"
    )

    print(
        "PERMUTATION P-VALUE: "
        f"{permutation['p_value_two_sided']:.6f}"
    )

    print(f"TOP-K OVERLAP: {overlap}/{top_k}")

    print(
        "TOP-K EXACT P-VALUE: "
        f"{top_p_value:.6f}"
    )

    print(
        "LEAVE-ONE-OUT CORRELATION RANGE: "
        f"[{loo_summary['min']:.6f}, "
        f"{loo_summary['max']:.6f}]"
    )

    print()
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON SAVED: {OUTPUT_JSON}")
    print(f"CSV SAVED: {OUTPUT_CSV}")
    print(f"V18.5 RESULT: {status}")
    print("=" * 68)

    if n < 100:
        print(
            "WARNING: Small research sample. "
            "Statistical findings are exploratory."
        )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as exc:
        print()
        print(
            "V18.5 FAILED: "
            f"{type(exc).__name__}: {exc}"
        )
        sys.exit(1)
