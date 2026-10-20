
"""
QUANTUM CYBER DEFENSE ARENA
V19.4 - BENCHMARK AGENT

Validates and summarizes V18 classical and quantum
research results.

Inputs:
- V19.1 architecture
- V19.3 validation
- V18.2 classical baseline
- V18.3 quantum kernel
- V18.4 comparison
- V18.5 statistical validation

Outputs:
- Benchmark Agent JSON report
- Markdown research report

Standard library only.
Read-only research workflow.
No LLM or external actions.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V17 = ROOT / "research_validation" / "v17"
V18 = ROOT / "research_validation" / "v18"
V19 = ROOT / "research_validation" / "v19"

FILES = {
    "architecture": V19 / "multi_agent_architecture_v19_1_results.json",
    "validation": V19 / "validation_agent_v19_3_results.json",
    "classical": V18 / "classical_baseline_v18_2_results.json",
    "quantum": V18 / "quantum_kernel_v18_3_results.json",
    "comparison": V18 / "quantum_classical_comparison_v18_4_results.json",
    "statistics": V18 / "statistical_validation_v18_5_results.json",
}

DATASET = V17 / "training_features_v17_1.csv"

CLASSICAL_CSV = V18 / "classical_baseline_v18_2_scores.csv"
QUANTUM_CSV = V18 / "quantum_kernel_v18_3_scores.csv"

OUTPUT_JSON = V19 / "benchmark_agent_v19_4_results.json"
OUTPUT_MD = V19 / "BENCHMARK_AGENT_V19_4.md"

EXPECTED = {
    "architecture": ("V19.1", "ARCHITECTURE_PASS"),
    "validation": ("V19.3", "VALIDATION_AGENT_PASS"),
    "classical": ("V18.2", "CLASSICAL_BASELINE_PASS"),
    "quantum": ("V18.3", "QUANTUM_KERNEL_PASS"),
    "comparison": ("V18.4", "COMPARISON_PASS"),
    "statistics": ("V18.5", "STATISTICAL_VALIDATION_PASS"),
}

CHECKS = []


def check(name, condition, detail=""):
    passed = bool(condition)

    CHECKS.append({
        "name": name,
        "passed": passed,
        "detail": str(detail),
    })

    print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if detail and not passed:
        print(f"       {detail}")

    return passed


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid JSON object: {path.name}")

    return data


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        rows = list(reader)

    if not columns or not rows:
        raise ValueError(f"Empty or invalid CSV: {path.name}")

    if len(columns) != len(set(columns)):
        raise ValueError(f"Duplicate CSV columns: {path.name}")

    return columns, rows


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def number(value):
    if isinstance(value, bool):
        raise ValueError("Boolean is not a numeric metric")

    result = float(value)

    if not math.isfinite(result):
        raise ValueError("Non-finite metric encountered")

    return result


def close(a, b, tolerance=1e-5):
    return math.isclose(
        number(a),
        number(b),
        rel_tol=tolerance,
        abs_tol=tolerance,
    )


def rank(values):
    order = sorted(
        range(len(values)),
        key=lambda i: values[i],
    )

    result = [0.0] * len(values)
    position = 0

    while position < len(values):
        end = position + 1

        while (
            end < len(values)
            and values[order[end]] == values[order[position]]
        ):
            end += 1

        average = (position + 1 + end) / 2.0

        for i in range(position, end):
            result[order[i]] = average

        position = end

    return result


def spearman(a, b):
    x = rank(a)
    y = rank(b)

    mx = sum(x) / len(x)
    my = sum(y) / len(y)

    numerator = sum(
        (p - mx) * (q - my)
        for p, q in zip(x, y)
    )

    denominator = math.sqrt(
        sum((p - mx) ** 2 for p in x)
        * sum((q - my) ** 2 for q in y)
    )

    if denominator == 0:
        raise ValueError("Undefined rank correlation")

    return numerator / denominator


def load_score_column(path, field, expected_count):
    columns, rows = read_csv(path)

    if "sample_index" not in columns or field not in columns:
        raise ValueError(f"Required columns missing: {path.name}")

    indexes = [int(row["sample_index"]) for row in rows]

    if indexes != list(range(1, expected_count + 1)):
        raise ValueError(f"Sample alignment invalid: {path.name}")

    return [number(row[field]) for row in rows]


def top_k(values, k):
    order = sorted(
        range(len(values)),
        key=lambda i: (-values[i], i),
    )

    return {i + 1 for i in order[:k]}


def validate_reports(reports):
    for key, (version, status) in EXPECTED.items():
        report = reports[key]

        check(
            f"{key}: correct version",
            report.get("version") == version,
        )

        check(
            f"{key}: validated status",
            report.get("status") == status
            and (
                report.get("checks_failed") == 0
                if key not in ("classical", "quantum")
                else "checks_failed" not in report
                or report.get("checks_failed") == 0
            ),
        )

    agents = reports["architecture"].get("agents", [])

    check(
        "Benchmark Agent registered",
        any(
            isinstance(agent, dict)
            and agent.get("id") == "benchmark_agent"
            and agent.get("permissions", {}).get(
                "external_actions"
            ) is False
            for agent in agents
        ),
    )

    check(
        "Seven research findings validated",
        reports["validation"].get("findings_validated") == 7
        and reports["validation"].get("findings_total") == 7,
    )


def validate_dataset(reports):
    _, rows = read_csv(DATASET)
    digest = sha256(DATASET)
    count = len(rows)

    for key in ("classical", "quantum", "comparison", "statistics"):
        dataset = reports[key].get("dataset", {})

        check(
            f"{key}: source SHA-256",
            dataset.get("sha256") == digest,
        )

        check(
            f"{key}: sample count",
            dataset.get("samples") == count,
        )

    return count, digest


def create_benchmark(reports, count, digest):
    classical = reports["classical"]
    quantum = reports["quantum"]
    comparison = reports["comparison"]
    statistics = reports["statistics"]

    classical_scores = load_score_column(
        CLASSICAL_CSV,
        "anomaly_score",
        count,
    )

    quantum_scores = load_score_column(
        QUANTUM_CSV,
        "quantum_novelty_score",
        count,
    )

    measured_rho = spearman(
        classical_scores,
        quantum_scores,
    )

    comp = comparison["comparison"]
    stat = statistics["spearman"]

    check(
        "Rank correlation reproduces V18.4",
        close(
            measured_rho,
            comp["spearman_rank_correlation"],
        ),
    )

    check(
        "Rank correlation reproduces V18.5",
        close(
            measured_rho,
            stat["observed_correlation"],
        ),
    )

    k = int(comp["top_k"])

    if not 1 <= k <= count:
        raise ValueError("Invalid Top-K")

    classical_top = top_k(
        classical_scores,
        k,
    )

    quantum_top = top_k(
        quantum_scores,
        k,
    )

    overlap = len(
        classical_top & quantum_top
    )

    check(
        "Top-K overlap reproduced",
        overlap == comp["top_k_overlap"],
    )

    check(
        "Classical Top-K reproduced",
        sorted(classical_top)
        == comp["classical_top_k"],
    )

    check(
        "Quantum Top-K reproduced",
        sorted(quantum_top)
        == comp["quantum_top_k"],
    )

    expected_jaccard = overlap / len(
        classical_top | quantum_top
    )

    check(
        "Top-K Jaccard reproduced",
        close(
            expected_jaccard,
            comp["top_k_jaccard"],
        ),
    )

    bootstrap = stat["bootstrap"]
    permutation = stat["permutation"]
    top_stats = statistics["top_k"]

    ci_low = number(bootstrap["ci_lower"])
    ci_high = number(bootstrap["ci_upper"])

    p_permutation = number(
        permutation["p_value_two_sided"]
    )

    p_top = number(
        top_stats["hypergeometric_tail_p_value"]
    )

    check(
        "Bootstrap interval valid",
        -1 <= ci_low <= ci_high <= 1,
    )

    check(
        "Permutation p-value valid",
        0 <= p_permutation <= 1,
    )

    check(
        "Top-K exact p-value valid",
        0 <= p_top <= 1,
    )

    check(
        "Statistical Top-K consistency",
        top_stats["k"] == k
        and top_stats["observed_overlap"] == overlap,
    )

    check(
        "Quantum simulator, not physical hardware",
        quantum["quantum_method"].get(
            "physical_quantum_hardware"
        ) is False,
    )

    check(
        "No quantum advantage claim",
        comparison.get(
            "quantum_advantage_demonstrated"
        ) is False,
    )

    classical_time = number(
        classical["runtime"]["total_seconds"]
    )

    quantum_time = number(
        quantum["runtime"]["total_seconds"]
    )

    check(
        "Runtime observations valid",
        classical_time >= 0
        and quantum_time >= 0,
    )

    check(
        "Timing comparison explicitly not fair",
        comparison.get(
            "runtime_observations", {}
        ).get("timing_comparison_is_fair") is False,
    )

    return {
        "dataset_sha256": digest,
        "samples": count,
        "methods": {
            "classical": "IsolationForest",
            "quantum": "Qiskit simulated fidelity kernel",
        },
        "spearman": round(measured_rho, 8),
        "top_k": k,
        "top_k_overlap": overlap,
        "top_k_jaccard": round(
            expected_jaccard,
            8,
        ),
        "bootstrap_95_percent_ci": [
            ci_low,
            ci_high,
        ],
        "permutation_p_value": p_permutation,
        "top_k_exact_p_value": p_top,
        "classical_runtime_seconds": classical_time,
        "quantum_simulation_runtime_seconds": quantum_time,
        "runtime_comparison_is_fair": False,
        "verified_attack_labels": False,
        "quantum_advantage_demonstrated": False,
    }


def write_markdown(benchmark, passed, failed):
    ci = benchmark["bootstrap_95_percent_ci"]

    content = f"""# Quantum Cyber Defense Arena

## V19.4 - Benchmark Agent

**Status:** BENCHMARK_AGENT_PASS

**Validation checks:** {passed} passed, {failed} failed

### Research dataset

- Blockchain-derived samples: {benchmark['samples']}
- Shared dataset SHA-256: `{benchmark['dataset_sha256']}`

### Compared methods

- Classical: Isolation Forest
- Quantum: Qiskit simulated fidelity kernel

### Benchmark results

| Metric | Value |
|---|---|
| Spearman correlation | {benchmark['spearman']} |
| Top-K size | {benchmark['top_k']} |
| Shared Top-K samples | {benchmark['top_k_overlap']} |
| Top-K Jaccard | {benchmark['top_k_jaccard']} |
| Bootstrap 95% CI | [{ci[0]}, {ci[1]}] |
| Permutation p-value | {benchmark['permutation_p_value']} |
| Top-K exact p-value | {benchmark['top_k_exact_p_value']} |
| Classical runtime (s) | {benchmark['classical_runtime_seconds']} |
| Quantum simulation runtime (s) | {benchmark['quantum_simulation_runtime_seconds']} |

### Scientific interpretation

The two methods show an exploratory positive
rank association on the shared transaction sample.

The runtime figures measure different computational
procedures and do not establish a speed advantage.

Top-K overlap measures agreement between methods,
not the accuracy of attack detection.

### Limitations

- Only a small transaction sample is used
- No independently verified attack labels
- No out-of-sample performance measurements
- No physical quantum hardware
- No demonstrated quantum advantage
- Statistical tests have assumptions and uncertainty

### Next stage

V19.5 - Autonomous Supervisor
"""

    OUTPUT_MD.write_text(
        content,
        encoding="utf-8",
    )


def main():
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V19.4 - BENCHMARK AGENT")
    print("=" * 68)

    V19.mkdir(parents=True, exist_ok=True)

    required = list(FILES.values()) + [
        DATASET,
        CLASSICAL_CSV,
        QUANTUM_CSV,
    ]

    available = True

    for path in required:
        exists = path.is_file()
        available = available and exists

        check(
            f"File available: {path.name}",
            exists,
        )

    benchmark = None
    error_message = None

    if available:
        try:
            reports = {
                name: read_json(path)
                for name, path in FILES.items()
            }

            validate_reports(reports)

            count, digest = validate_dataset(reports)

            benchmark = create_benchmark(
                reports,
                count,
                digest,
            )

        except (OSError, ValueError, KeyError, TypeError) as exc:
            error_message = (
                f"{type(exc).__name__}: {exc}"
            )
            check(
                "Benchmark evaluation completed",
                False,
                error_message,
            )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    if benchmark is None and failed == 0:
        check(
            "Benchmark output generated",
            False,
        )
        failed = 1

    status = (
        "BENCHMARK_AGENT_PASS"
        if failed == 0
        else "BENCHMARK_AGENT_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V19.4",
        "module": "Benchmark Agent",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "agent_id": "benchmark_agent",
        "agent_type": "deterministic_benchmark_analysis",
        "llm_enabled": False,
        "external_actions_enabled": False,
        "benchmark": benchmark,
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error_message,
        "limitations": [
            "No independently verified attack labels.",
            "No out-of-sample predictive evaluation.",
            "Small blockchain transaction dataset.",
            "Ranking agreement is not detection accuracy.",
            "Runtime timings are not directly comparable.",
            "No quantum computational advantage demonstrated.",
            "The agent does not run external actions.",
        ],
        "next_stage": "V19.5 Autonomous Supervisor",
    }

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            result,
            handle,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

    if failed == 0:
        write_markdown(
            benchmark,
            passed,
            failed,
        )

    print()
    print("=" * 68)
    print("V19.4 BENCHMARK AGENT RESULTS")
    print("=" * 68)

    if benchmark is not None:
        print(f"SAMPLES: {benchmark['samples']}")
        print(f"SPEARMAN: {benchmark['spearman']}")
        print(
            "TOP-K OVERLAP: "
            f"{benchmark['top_k_overlap']}/"
            f"{benchmark['top_k']}"
        )

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {OUTPUT_JSON}")

    if failed == 0:
        print(f"RESEARCH DOCUMENT: {OUTPUT_MD}")

    print(f"V19.4 RESULT: {status}")
    print("=" * 68)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print()
        print(
            f"V19.4 FAILED: "
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)
