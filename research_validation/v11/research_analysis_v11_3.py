
"""
QUANTUM CYBER DEFENSE ARENA
V11.3 - ADVANCED RESEARCH ANALYSIS

Analyzes completed V11.2 benchmark results.

Features:
- 30-run benchmark validation
- Model performance ranking
- F1 stability analysis
- Paired statistical comparisons
- Holm multiple-testing correction
- Hybrid win/loss analysis
- Research quality checks
- JSON research report
- Markdown research report

Research simulation only.
No demonstrated quantum computational advantage.
"""

from __future__ import annotations

import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path


VERSION = "11.3.0"

HERE = Path(__file__).resolve().parent

INPUT_FILE = HERE / "benchmark_v11_2_results.json"

JSON_OUTPUT = HERE / "research_analysis_v11_3_results.json"

MARKDOWN_OUTPUT = HERE / "research_analysis_v11_3_report.md"

MODELS = ("classical", "quantum", "hybrid")

MODEL_LABELS = {
    "classical": "Classical AI",
    "quantum": "Quantum AI",
    "hybrid": "Hybrid Fusion",
}

ALPHA = 0.05


def load_benchmark() -> dict:
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            "V11.2 benchmark result file not found:\n"
            f"{INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Invalid benchmark JSON structure.")

    if data.get("version") != "11.2.0":
        raise ValueError(
            "Expected V11.2 benchmark results. "
            f"Found: {data.get('version')}"
        )

    runs = data.get("runs")

    if not isinstance(runs, list) or len(runs) < 2:
        raise ValueError("Benchmark runs are missing.")

    for index, run in enumerate(runs, start=1):
        if not isinstance(run, dict):
            raise ValueError(f"Invalid run #{index}")

        for model in MODELS:
            metrics = run.get(model)

            if not isinstance(metrics, dict):
                raise ValueError(
                    f"Missing {model} metrics in run #{index}"
                )

            f1 = float(metrics["f1"])

            if not math.isfinite(f1) or not 0 <= f1 <= 1:
                raise ValueError(
                    f"Invalid F1 score in run #{index}"
                )

    comparisons = data.get("comparisons")

    if not isinstance(comparisons, list):
        raise ValueError("Statistical comparisons are missing.")

    return data


def model_analysis(runs: list[dict], model: str) -> dict:
    scores = [
        float(run[model]["f1"])
        for run in runs
    ]

    mean = statistics.mean(scores)
    std = statistics.stdev(scores)

    return {
        "model": model,
        "label": MODEL_LABELS[model],
        "runs": len(scores),
        "mean_f1": round(mean, 6),
        "mean_f1_percent": round(mean * 100, 4),
        "median_f1": round(statistics.median(scores), 6),
        "std_f1": round(std, 6),
        "min_f1": round(min(scores), 6),
        "max_f1": round(max(scores), 6),
        "f1_range": round(max(scores) - min(scores), 6),
        "scores": [round(score, 6) for score in scores],
    }


def holm_correction(comparisons: list[dict]) -> list[dict]:
    """
    Holm-Bonferroni correction for multiple comparisons.

    Uses the permutation-test p-values
    already calculated by V11.2.
    """

    items = []

    for comparison in comparisons:
        p_value = float(comparison["permutation_p_value"])

        if not math.isfinite(p_value) or not 0 <= p_value <= 1:
            raise ValueError("Invalid permutation p-value.")

        items.append({
            "model_a": comparison["model_a"],
            "model_b": comparison["model_b"],
            "raw_p_value": p_value,
            "comparison": comparison,
        })

    ordered = sorted(
        items,
        key=lambda item: item["raw_p_value"],
    )

    number_of_tests = len(ordered)
    running_adjusted_p = 0.0

    for index, item in enumerate(ordered):
        multiplier = number_of_tests - index

        adjusted_p = min(
            1.0,
            item["raw_p_value"] * multiplier,
        )

        running_adjusted_p = max(
            running_adjusted_p,
            adjusted_p,
        )

        item["holm_adjusted_p_value"] = round(
            running_adjusted_p, 6
        )

        item["significant_at_0_05"] = (
            running_adjusted_p <= ALPHA
        )

    return sorted(
        ordered,
        key=lambda item: (
            item["model_a"],
            item["model_b"],
        ),
    )


def validate_benchmark(data: dict) -> dict:
    runs = data["runs"]
    metadata = data.get("benchmark", {})

    expected_runs = metadata.get("runs")

    issues = []

    if expected_runs != len(runs):
        issues.append(
            "Declared run count differs from actual run count."
        )

    if len(runs) != 30:
        issues.append(
            "Expected 30 research runs; "
            f"found {len(runs)}."
        )

    seed_values = metadata.get("seeds", [])

    if len(seed_values) != len(runs):
        issues.append(
            "Seed count does not match benchmark runs."
        )

    if len(set(seed_values)) != len(seed_values):
        issues.append("Duplicate benchmark seeds.")

    if data.get("mode") != "RESEARCH_SIMULATION":
        issues.append("Unexpected benchmark mode.")

    return {
        "status": "PASS" if not issues else "WARNING",
        "actual_runs": len(runs),
        "declared_runs": expected_runs,
        "issues": issues,
    }


def hybrid_analysis(runs: list[dict]) -> dict:
    hybrid = [
        float(run["hybrid"]["f1"])
        for run in runs
    ]

    quantum = [
        float(run["quantum"]["f1"])
        for run in runs
    ]

    classical = [
        float(run["classical"]["f1"])
        for run in runs
    ]

    def compare(reference: list[float]) -> dict:
        differences = [
            h - r
            for h, r in zip(hybrid, reference)
        ]

        return {
            "wins": sum(d > 1e-12 for d in differences),
            "losses": sum(d < -1e-12 for d in differences),
            "ties": sum(abs(d) <= 1e-12 for d in differences),
            "mean_difference_percentage_points": round(
                statistics.mean(differences) * 100,
                4,
            ),
            "positive_mean_advantage": (
                statistics.mean(differences) > 0
            ),
        }

    return {
        "vs_quantum": compare(quantum),
        "vs_classical": compare(classical),
    }


def prepare_comparisons(
    comparisons: list[dict],
) -> list[dict]:
    corrected = holm_correction(comparisons)

    results = []

    for item in corrected:
        original = item["comparison"]

        ci = original["bootstrap_ci_95"]

        results.append({
            "model_a": item["model_a"],
            "model_b": item["model_b"],
            "mean_difference_percentage_points": original[
                "difference_percentage_points"
            ],
            "bootstrap_ci_95": ci,
            "raw_p_value": item["raw_p_value"],
            "holm_adjusted_p_value": item[
                "holm_adjusted_p_value"
            ],
            "significant_at_0_05": item[
                "significant_at_0_05"
            ],
            "wins": original["wins"],
            "losses": original["losses"],
            "ties": original["ties"],
        })

    return results


def build_markdown(report: dict) -> str:
    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V11.3 Advanced Research Analysis",
        "",
        f"Generated: {report['created_at']}",
        "",
        "**Research type:** Synthetic simulation",
        "",
        "## Benchmark configuration",
        "",
        f"- Benchmark runs: {report['benchmark_runs']}",
        "- Source: V11.2 Extended Research Benchmark",
        "- Quantum component: Classical quantum simulation",
        "",
        "## Model performance",
        "",
        "| Model | Mean F1 | Std F1 | Minimum | Maximum |",
        "|---|---:|---:|---:|---:|",
    ]

    for item in report["ranking"]:
        lines.append(
            f"| {item['label']} "
            f"| {item['mean_f1_percent']:.2f}% "
            f"| {item['std_f1']:.4f} "
            f"| {item['min_f1']:.4f} "
            f"| {item['max_f1']:.4f} |"
        )

    lines.extend([
        "",
        "## Statistical comparisons",
        "",
        "| Comparison | F1 difference (pp) | Raw p | Holm p | Significant |",
        "|---|---:|---:|---:|---|",
    ])

    for item in report["comparisons"]:
        significant = (
            "Yes" if item["significant_at_0_05"] else "No"
        )

        lines.append(
            f"| {item['model_a']} vs {item['model_b']} "
            f"| {item['mean_difference_percentage_points']:+.4f} "
            f"| {item['raw_p_value']:.6f} "
            f"| {item['holm_adjusted_p_value']:.6f} "
            f"| {significant} |"
        )

    lines.extend([
        "",
        "## Hybrid Fusion consistency",
        "",
    ])

    for name, comparison in report["hybrid_analysis"].items():
        lines.extend([
            f"### {name.replace('_', ' ').title()}",
            "",
            f"- Wins: {comparison['wins']}",
            f"- Losses: {comparison['losses']}",
            f"- Ties: {comparison['ties']}",
            "- Mean F1 difference: "
            f"{comparison['mean_difference_percentage_points']:+.4f} "
            "percentage points",
            "",
        ])

    lines.extend([
        "## Research validation",
        "",
        f"Configuration check: **{report['quality_check']['status']}**",
        "",
    ])

    for issue in report["quality_check"]["issues"]:
        lines.append(f"- Warning: {issue}")

    lines.extend([
        "",
        "## Research limitations",
        "",
        "- All benchmark inputs are synthetic.",
        "- The quantum component runs on a classical simulator.",
        "- The tested hybrid is a specified fusion rule, not evidence "
        "that quantum hardware is superior.",
        "- The measured F1 values depend on test-data distributions "
        "and anomaly decision thresholds.",
        "- Correlated synthetic test runs can overstate generalization.",
        "- Statistical significance does not prove operational usefulness.",
        "- The sign-flip test relies on exchangeable paired differences.",
        "- Bootstrap confidence intervals remain approximate.",
        "- REVIEW decisions require separate operational assessment.",
        "- Real-world security datasets and deployment testing "
        "are still required.",
        "",
        "## Next research stage",
        "",
        "V11.4: Research Dashboard.",
        "",
        "V12: Robustness and Stress Testing.",
        "",
        "V13: Real Dataset Validation.",
        "",
        "V14: Professional Research Release.",
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    print()
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA V11.3")
    print("ADVANCED RESEARCH ANALYSIS")
    print("=" * 68)

    data = load_benchmark()

    runs = data["runs"]

    print()
    print("LOADED BENCHMARK RUNS:", len(runs))

    quality_check = validate_benchmark(data)

    models = {
        name: model_analysis(runs, name)
        for name in MODELS
    }

    ranking = sorted(
        models.values(),
        key=lambda item: item["mean_f1"],
        reverse=True,
    )

    comparisons = prepare_comparisons(
        data["comparisons"]
    )

    hybrid = hybrid_analysis(runs)

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "mode": "RESEARCH_SIMULATION",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_file": INPUT_FILE.name,
        "benchmark_runs": len(runs),
        "quality_check": quality_check,
        "ranking": ranking,
        "models": models,
        "comparisons": comparisons,
        "hybrid_analysis": hybrid,
        "multiple_testing_method": "Holm-Bonferroni",
        "significance_alpha": ALPHA,
        "research_status": "EXPLORATORY",
        "quantum_advantage_proven": False,
    }

    JSON_OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    MARKDOWN_OUTPUT.write_text(
        build_markdown(report),
        encoding="utf-8",
    )

    print()
    print("MODEL RANKING")
    print("-" * 68)

    for position, item in enumerate(ranking, start=1):
        print(
            f"{position}. {item['label']:20s} "
            f"F1: {item['mean_f1_percent']:.2f}% "
            f"STD: {item['std_f1']:.4f}"
        )

    print()
    print("STATISTICAL VALIDATION")
    print("-" * 68)

    for item in comparisons:
        print()
        print(
            item["model_a"].upper(),
            "VS",
            item["model_b"].upper(),
        )

        print(
            "F1 DIFFERENCE:",
            item["mean_difference_percentage_points"],
            "percentage points",
        )

        print(
            "RAW P-VALUE:",
            item["raw_p_value"],
        )

        print(
            "HOLM ADJUSTED P-VALUE:",
            item["holm_adjusted_p_value"],
        )

        print(
            "SIGNIFICANT AT 0.05:",
            item["significant_at_0_05"],
        )

    print()
    print("RESEARCH QUALITY CHECK:", quality_check["status"])

    print()
    print("=" * 68)
    print("V11.3 ADVANCED RESEARCH ANALYSIS COMPLETED")
    print("=" * 68)

    print()
    print("JSON REPORT:")
    print(JSON_OUTPUT)

    print()
    print("MARKDOWN REPORT:")
    print(MARKDOWN_OUTPUT)

    print()
    print(
        "NOTE: Results are exploratory and do not "
        "demonstrate quantum computational advantage."
    )


if __name__ == "__main__":
    main()
