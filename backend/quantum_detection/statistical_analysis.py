
"""
QUANTUM CYBER DEFENSE ARENA V6.3
Statistical Research Analysis

Analyzes paired Quantum vs Classical benchmark results.

Input:
    benchmark_v2_results.json

Output:
    statistical_analysis_results.json

Statistics:
    - Paired experiment comparison
    - Mean F1 difference
    - 95% confidence interval
    - Paired t-test
    - Wilcoxon signed-rank test
    - Win / loss / tie counts
    - Effect size (Cohen's dz)
    - Runtime comparison

Research simulation only.
No claim of quantum computational advantage.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "benchmark_v2_results.json"
OUTPUT_FILE = BASE_DIR / "statistical_analysis_results.json"

ALPHA = 0.05


def load_benchmark() -> dict:
    """Load and validate V6.2 benchmark data."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Benchmark file not found: {INPUT_FILE}\n"
            "Run benchmark_v2.py first."
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if data.get("version") != "6.2":
        raise ValueError(
            "Expected a V6.2 benchmark report."
        )

    if "quantum" not in data or "classical" not in data:
        raise ValueError(
            "Missing quantum or classical results."
        )

    quantum_runs = data["quantum"]["experiments"]
    classical_runs = data["classical"]["experiments"]

    if len(quantum_runs) != len(classical_runs):
        raise ValueError(
            "Quantum and classical run counts differ."
        )

    if len(quantum_runs) < 2:
        raise ValueError(
            "At least two paired experiments are required."
        )

    return data


def extract_metric(
    experiments: list[dict],
    metric: str,
) -> np.ndarray:
    """Extract numerical metric values."""

    values = np.asarray(
        [run[metric] for run in experiments],
        dtype=float,
    )

    if not np.all(np.isfinite(values)):
        raise ValueError(
            f"Invalid values for metric: {metric}"
        )

    return values


def paired_statistics(
    quantum_values: np.ndarray,
    classical_values: np.ndarray,
) -> dict:
    """
    Compute paired differences.

    Positive difference means the quantum model
    scored higher for the selected metric.
    """

    differences = quantum_values - classical_values

    n = len(differences)
    mean_difference = float(np.mean(differences))
    std_difference = float(
        np.std(differences, ddof=1)
    )

    standard_error = std_difference / np.sqrt(n)

    degrees_of_freedom = n - 1

    if standard_error > 0:
        t_critical = stats.t.ppf(
            1.0 - ALPHA / 2.0,
            df=degrees_of_freedom,
        )

        ci_lower = (
            mean_difference - t_critical * standard_error
        )

        ci_upper = (
            mean_difference + t_critical * standard_error
        )

        t_result = stats.ttest_rel(
            quantum_values,
            classical_values,
        )

        t_statistic = float(t_result.statistic)
        t_p_value = float(t_result.pvalue)

        cohen_dz = mean_difference / std_difference

    else:
        ci_lower = mean_difference
        ci_upper = mean_difference

        if np.isclose(mean_difference, 0.0):
            t_statistic = 0.0
            t_p_value = 1.0
            cohen_dz = 0.0
        else:
            # All paired differences are identical,
            # so the t statistic is not finite.
            t_statistic = None
            t_p_value = None
            cohen_dz = None

    wins = int(
        np.sum(differences > 1e-12)
    )

    losses = int(
        np.sum(differences < -1e-12)
    )

    ties = n - wins - losses

    try:
        if np.all(np.abs(differences) < 1e-12):
            wilcoxon_statistic = 0.0
            wilcoxon_p_value = 1.0
        else:
            wilcoxon_result = stats.wilcoxon(
                differences,
                alternative="two-sided",
                zero_method="wilcox",
            )

            wilcoxon_statistic = float(
                wilcoxon_result.statistic
            )
            wilcoxon_p_value = float(
                wilcoxon_result.pvalue
            )

    except ValueError:
        wilcoxon_statistic = None
        wilcoxon_p_value = None

    return {
        "sample_size": n,
        "quantum_mean": float(
            np.mean(quantum_values)
        ),
        "classical_mean": float(
            np.mean(classical_values)
        ),
        "mean_difference": mean_difference,
        "std_difference": std_difference,
        "confidence_interval_95": {
            "lower": float(ci_lower),
            "upper": float(ci_upper),
        },
        "paired_t_test": {
            "statistic": t_statistic,
            "p_value": t_p_value,
        },
        "wilcoxon_signed_rank": {
            "statistic": wilcoxon_statistic,
            "p_value": wilcoxon_p_value,
        },
        "cohens_dz": cohen_dz,
        "quantum_wins": wins,
        "classical_wins": losses,
        "ties": ties,
    }


def print_f1_analysis(result: dict) -> None:
    """Print F1 statistical analysis."""

    print()
    print("=" * 65)
    print("F1-SCORE PAIRED STATISTICAL ANALYSIS")
    print("=" * 65)

    print(
        f"Experiments:             {result['sample_size']}"
    )

    print(
        "Quantum mean F1:         "
        f"{result['quantum_mean']:.2%}"
    )

    print(
        "Classical mean F1:       "
        f"{result['classical_mean']:.2%}"
    )

    print(
        "Mean difference:         "
        f"{result['mean_difference'] * 100:+.2f} percentage points"
    )

    ci = result["confidence_interval_95"]

    print(
        "95% confidence interval: "
        f"[{ci['lower'] * 100:+.2f}, "
        f"{ci['upper'] * 100:+.2f}] percentage points"
    )

    print()
    print(
        "Quantum wins:            "
        f"{result['quantum_wins']}"
    )

    print(
        "Classical wins:          "
        f"{result['classical_wins']}"
    )

    print(
        "Ties:                    "
        f"{result['ties']}"
    )

    t_p = result["paired_t_test"]["p_value"]
    w_p = result["wilcoxon_signed_rank"]["p_value"]

    print()
    print(
        "Paired t-test p-value:   "
        f"{t_p:.6f}" if t_p is not None
        else "Paired t-test:          undefined"
    )

    print(
        "Wilcoxon p-value:        "
        f"{w_p:.6f}" if w_p is not None
        else "Wilcoxon test:          undefined"
    )

    effect = result["cohens_dz"]

    if effect is not None:
        print(f"Cohen's dz:              {effect:.4f}")

    if t_p is None:
        conclusion = (
            "The paired t-test is undefined because "
            "the differences have zero variance."
        )
    elif t_p < ALPHA:
        conclusion = (
            "A statistically detectable paired F1 difference "
            "was observed at alpha=0.05."
        )
    else:
        conclusion = (
            "No statistically significant paired F1 difference "
            "was detected at alpha=0.05."
        )

    print()
    print("CONCLUSION:")
    print(conclusion)


def main() -> None:
    print()
    print("=" * 65)
    print("QUANTUM CYBER DEFENSE ARENA V6.3")
    print("STATISTICAL RESEARCH ANALYSIS")
    print("=" * 65)

    benchmark = load_benchmark()

    quantum_runs = benchmark["quantum"]["experiments"]
    classical_runs = benchmark["classical"]["experiments"]

    quantum_f1 = extract_metric(
        quantum_runs,
        "f1_score",
    )

    classical_f1 = extract_metric(
        classical_runs,
        "f1_score",
    )

    f1_analysis = paired_statistics(
        quantum_f1,
        classical_f1,
    )

    print_f1_analysis(f1_analysis)

    quantum_accuracy = extract_metric(
        quantum_runs,
        "accuracy",
    )

    classical_accuracy = extract_metric(
        classical_runs,
        "accuracy",
    )

    accuracy_analysis = paired_statistics(
        quantum_accuracy,
        classical_accuracy,
    )

    quantum_recall = extract_metric(
        quantum_runs,
        "recall",
    )

    classical_recall = extract_metric(
        classical_runs,
        "recall",
    )

    recall_analysis = paired_statistics(
        quantum_recall,
        classical_recall,
    )

    quantum_time = extract_metric(
        quantum_runs,
        "prediction_time_ms",
    )

    classical_time = extract_metric(
        classical_runs,
        "prediction_time_ms",
    )

    mean_quantum_time = float(
        np.mean(quantum_time)
    )

    mean_classical_time = float(
        np.mean(classical_time)
    )

    speed_ratio = (
        mean_quantum_time / mean_classical_time
        if mean_classical_time > 0.0
        else None
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "6.3",
        "input_file": INPUT_FILE.name,
        "data_source": "SYNTHETIC_SIMULATION",
        "significance_level": ALPHA,
        "f1_score": f1_analysis,
        "accuracy": accuracy_analysis,
        "recall": recall_analysis,
        "runtime": {
            "quantum_mean_ms": mean_quantum_time,
            "classical_mean_ms": mean_classical_time,
            "quantum_to_classical_ratio": speed_ratio,
        },
        "limitations": [
            "Ten paired experiments provide limited statistical power",
            "Both models were evaluated on synthetic data",
            "Normal and anomaly distributions are manually specified",
            "Quantum and classical hyperparameters were not jointly tuned",
            "Paired t-test assumes approximately normal differences",
            "Multiple metrics were examined without multiplicity adjustment",
            "No verified quantum advantage",
            "No real-world attack detection validation",
        ],
    }

    OUTPUT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 65)
    print("STATISTICAL ANALYSIS COMPLETED")
    print("=" * 65)
    print("Results saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
