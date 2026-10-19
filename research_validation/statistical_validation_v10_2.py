
"""
QUANTUM CYBER DEFENSE ARENA V10.2
Statistical Research Validation

Analyzes V10.1 overlapping-data benchmark results.

IMPORTANT:
- Uses synthetic research data.
- Confidence intervals come from the V10.1 bootstrap.
- The confidence interval is not an independent replication.
- No demonstrated quantum computational advantage.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    ROOT
    / "research_validation"
    / "benchmark_v10_1_results.json"
)

OUTPUT = (
    ROOT
    / "research_validation"
    / "statistical_validation_v10_2_results.json"
)

VERSION = "10.2.0"


def load_results() -> dict:
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"V10.1 results not found: {SOURCE}"
        )

    with SOURCE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if data.get("version") != "10.1.0":
        raise ValueError(
            "Expected V10.1 benchmark results."
        )

    if "summary" not in data:
        raise ValueError(
            "Benchmark summary is missing."
        )

    return data


def get_f1(summary: dict, model: str) -> float:
    value = float(summary[model]["f1"])

    if not math.isfinite(value):
        raise ValueError(
            f"Non-finite F1 score for {model}."
        )

    if not 0.0 <= value <= 1.0:
        raise ValueError(
            f"Invalid F1 score for {model}."
        )

    return value


def analyze_model_comparison(summary: dict) -> dict:
    classical = get_f1(summary, "classical")
    quantum = get_f1(summary, "quantum")
    hybrid = get_f1(summary, "hybrid_conservative")

    differences = {
        "quantum_vs_classical_pp": round(
            (quantum - classical) * 100,
            4,
        ),
        "hybrid_vs_classical_pp": round(
            (hybrid - classical) * 100,
            4,
        ),
        "hybrid_vs_quantum_pp": round(
            (hybrid - quantum) * 100,
            4,
        ),
    }

    return {
        "classical_f1": round(classical, 6),
        "quantum_f1": round(quantum, 6),
        "hybrid_f1": round(hybrid, 6),
        "differences": differences,
    }


def analyze_confidence_intervals(summary: dict) -> list[dict]:
    comparisons = summary.get(
        "confidence_intervals",
        [],
    )

    results = []

    for item in comparisons:
        lower = float(item["ci_95_lower_pp"])
        upper = float(item["ci_95_upper_pp"])
        difference = float(
            item["observed_f1_difference_pp"]
        )

        if not all(
            math.isfinite(value)
            for value in (lower, upper, difference)
        ):
            raise ValueError(
                "Confidence interval contains invalid values."
            )

        excludes_zero = lower > 0 or upper < 0

        if lower > 0:
            interpretation = (
                "Positive F1 difference in this "
                "synthetic benchmark bootstrap."
            )
        elif upper < 0:
            interpretation = (
                "Negative F1 difference in this "
                "synthetic benchmark bootstrap."
            )
        else:
            interpretation = (
                "The confidence interval includes zero."
            )

        results.append(
            {
                "model_a": item["model_a"],
                "model_b": item["model_b"],
                "f1_difference_pp": difference,
                "ci_95_lower_pp": lower,
                "ci_95_upper_pp": upper,
                "excludes_zero": excludes_zero,
                "interpretation": interpretation,
                "method": item.get(
                    "method",
                    "bootstrap",
                ),
                "bootstrap_samples": item.get(
                    "bootstrap_samples",
                    None,
                ),
            }
        )

    return results


def analyze_hybrid_reviews(summary: dict) -> dict:
    data = summary["hybrid_abstention"]

    return {
        "review_count": int(
            data["review_count"]
        ),
        "review_rate_percent": round(
            float(data["review_rate"]) * 100,
            2,
        ),
        "decisive_coverage_percent": round(
            float(data["decisive_coverage"]) * 100,
            2,
        ),
        "policy": data.get("policy", ""),
    }


def analyze_runtime(summary: dict) -> dict:
    runtime = summary["runtime_ms"]

    classical_ms = float(
        runtime["classical_mean"]
    )

    quantum_fusion_ms = float(
        runtime["quantum_plus_fusion_mean"]
    )

    return {
        "classical_ms_per_event": classical_ms,
        "quantum_plus_fusion_ms_per_event": (
            quantum_fusion_ms
        ),
        "note": (
            "The measurements cover different operations. "
            "They cannot establish quantum speedup."
        ),
    }


def main() -> None:
    print()
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA V10.2")
    print("STATISTICAL RESEARCH VALIDATION")
    print("=" * 70)

    benchmark = load_results()
    summary = benchmark["summary"]

    comparison = analyze_model_comparison(summary)

    confidence_intervals = (
        analyze_confidence_intervals(summary)
    )

    reviews = analyze_hybrid_reviews(summary)
    runtime = analyze_runtime(summary)

    output = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_benchmark": str(SOURCE),
        "source_version": benchmark["version"],
        "mode": "RESEARCH_SIMULATION",
        "model_comparison": comparison,
        "confidence_intervals": confidence_intervals,
        "hybrid_reviews": reviews,
        "runtime": runtime,
        "limitations": [
            "All evaluation data are synthetic.",
            "The confidence intervals were already "
            "computed by V10.1.",
            "This module does not generate new experiments.",
            "The number of independent seeds is small.",
            "The bootstrap is based on simulated events.",
            "Model performance may not generalize.",
            "No quantum hardware execution.",
            "No evidence of quantum computational advantage.",
        ],
    }

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("MODEL F1 SCORES")
    print(
        "Classical:",
        f"{comparison['classical_f1'] * 100:.2f}%",
    )
    print(
        "Quantum:",
        f"{comparison['quantum_f1'] * 100:.2f}%",
    )
    print(
        "Hybrid:",
        f"{comparison['hybrid_f1'] * 100:.2f}%",
    )

    print()
    print("F1 DIFFERENCES")

    for name, value in comparison[
        "differences"
    ].items():
        print(name, ":", value, "pp")

    print()
    print("95% BOOTSTRAP CONFIDENCE INTERVALS")

    for item in confidence_intervals:
        print()
        print(
            item["model_a"],
            "vs",
            item["model_b"],
        )
        print(
            "Difference:",
            item["f1_difference_pp"],
            "pp",
        )
        print(
            "95% CI:",
            item["ci_95_lower_pp"],
            "to",
            item["ci_95_upper_pp"],
            "pp",
        )
        print(
            "Excludes zero:",
            item["excludes_zero"],
        )

    print()
    print("HYBRID REVIEW ANALYSIS")
    print("Review count:", reviews["review_count"])
    print(
        "Review rate:",
        reviews["review_rate_percent"],
        "%",
    )
    print(
        "Decisive coverage:",
        reviews["decisive_coverage_percent"],
        "%",
    )

    print()
    print("RUNTIME")
    print(
        "Classical:",
        runtime["classical_ms_per_event"],
        "ms/event",
    )
    print(
        "Quantum + Fusion:",
        runtime["quantum_plus_fusion_ms_per_event"],
        "ms/event",
    )

    print()
    print("Results saved:", OUTPUT)

    print()
    print("=" * 70)
    print("V10.2 STATISTICAL VALIDATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
