
"""
QUANTUM CYBER DEFENSE ARENA
V18.6 - QUANTUM-CLASSICAL RESEARCH RELEASE

Final V18 research release:
- Validate V18.1 through V18.5 artifacts
- Verify common blockchain-derived dataset
- Check model and statistical results
- Generate scientific research report
- Export dashboard-ready JSON

Does not alter existing React components.
Does not claim quantum advantage.
Standard Python library only.
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

PUBLIC_DIR = ROOT / "frontend" / "public" / "v18"

DATASET = V17 / "training_features_v17_1.csv"

REPORT_NAMES = {
    "v18_1": "benchmark_architecture_v18_1_results.json",
    "v18_2": "classical_baseline_v18_2_results.json",
    "v18_3": "quantum_kernel_v18_3_results.json",
    "v18_4": "quantum_classical_comparison_v18_4_results.json",
    "v18_5": "statistical_validation_v18_5_results.json",
}

EXPECTED_STATUS = {
    "v18_1": "ARCHITECTURE_PASS",
    "v18_2": "CLASSICAL_BASELINE_PASS",
    "v18_3": "QUANTUM_KERNEL_PASS",
    "v18_4": "COMPARISON_PASS",
    "v18_5": "STATISTICAL_VALIDATION_PASS",
}

OTHER_ARTIFACTS = [
    "classical_baseline_v18_2_scores.csv",
    "quantum_kernel_v18_3_matrix.csv",
    "quantum_kernel_v18_3_scores.csv",
    "quantum_classical_comparison_v18_4_scores.csv",
    "statistical_validation_v18_5_sensitivity.csv",
]

RESULT_JSON = V18 / "research_release_v18_6_results.json"

RESULT_MD = V18 / "V18_RESEARCH_RELEASE.md"

DASHBOARD_JSON = (
    PUBLIC_DIR / "quantum_classical_v18_dashboard.json"
)

CHECKS = []


def check(name, condition, detail=""):
    passed = bool(condition)

    CHECKS.append({
        "name": name,
        "passed": passed,
        "detail": str(detail),
    })

    label = "PASS" if passed else "FAIL"

    print(f"[{label}] {name}")

    if not passed and detail:
        print(f"       {detail}")

    return passed


def read_json(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        value = json.load(handle)

    if not isinstance(value, dict):
        raise ValueError(
            f"Expected JSON object: {path.name}"
        )

    return value


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        columns = reader.fieldnames or []
        rows = list(reader)

    if not columns:
        raise ValueError(
            f"CSV header missing: {path.name}"
        )

    if len(columns) != len(set(columns)):
        raise ValueError(
            f"Duplicate CSV columns: {path.name}"
        )

    if not rows:
        raise ValueError(
            f"CSV has no data rows: {path.name}"
        )

    return columns, rows


def finite_number(value):
    if isinstance(value, bool):
        return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(result):
        return None

    return result


def close_values(a, b, tolerance=1e-5):
    x = finite_number(a)
    y = finite_number(b)

    return (
        x is not None
        and y is not None
        and math.isclose(
            x, y,
            rel_tol=tolerance,
            abs_tol=tolerance,
        )
    )


def save_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            data,
            handle,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )


def validate_source_files():
    required = (
        [DATASET]
        + [V18 / name for name in REPORT_NAMES.values()]
        + [V18 / name for name in OTHER_ARTIFACTS]
    )

    for path in required:
        check(
            f"File exists: {path.name}",
            path.is_file()
            and path.stat().st_size > 0
            if path.is_file()
            else False,
        )

    if not all(item["passed"] for item in CHECKS):
        raise ValueError(
            "Required research artifacts are missing."
        )


def validate_reports(reports):
    for key, report in reports.items():
        expected_version = (
            "V18." + key.split("_")[1]
        )

        check(
            f"{expected_version} version",
            report.get("version") == expected_version,
        )

        check(
            f"{expected_version} result PASS",
            report.get("status")
            == EXPECTED_STATUS[key],
        )

    for key in ("v18_1", "v18_4", "v18_5"):
        report = reports[key]

        check(
            f"{key} checks failed = 0",
            report.get("checks_failed") == 0,
        )


def validate_data(reports):
    columns, rows = read_csv(DATASET)

    digest = sha256_file(DATASET)

    n = len(rows)

    hashes = [
        reports["v18_1"].get(
            "dataset", {}
        ).get("sha256"),
        reports["v18_2"].get(
            "dataset", {}
        ).get("sha256"),
        reports["v18_3"].get(
            "dataset", {}
        ).get("sha256"),
        reports["v18_4"].get(
            "dataset", {}
        ).get("sha256"),
        reports["v18_5"].get(
            "dataset", {}
        ).get("sha256"),
    ]

    check(
        "All stages use the same SHA-256 dataset",
        all(value == digest for value in hashes),
    )

    counts = [
        reports["v18_1"]["dataset"].get("samples"),
        reports["v18_2"]["dataset"].get("samples"),
        reports["v18_3"]["dataset"].get("samples"),
        reports["v18_4"]["dataset"].get("samples"),
        reports["v18_5"]["dataset"].get("samples"),
    ]

    check(
        "All stages use the same sample count",
        all(value == n for value in counts),
    )

    check(
        "Source feature count verified",
        len(columns)
        == reports["v18_1"]["dataset"].get(
            "feature_count"
        ),
    )

    check(
        "Source feature order verified",
        columns
        == reports["v18_1"]["dataset"].get(
            "feature_names"
        ),
    )

    check(
        "Sample size documented",
        n >= 10,
    )

    csv_counts = {}

    for filename in OTHER_ARTIFACTS:
        path = V18 / filename
        _, artifact_rows = read_csv(path)

        csv_counts[filename] = len(artifact_rows)

    check(
        "Classical score rows verified",
        csv_counts[
            "classical_baseline_v18_2_scores.csv"
        ] == n,
    )

    check(
        "Quantum kernel rows verified",
        csv_counts[
            "quantum_kernel_v18_3_matrix.csv"
        ] == n,
    )

    check(
        "Quantum score rows verified",
        csv_counts[
            "quantum_kernel_v18_3_scores.csv"
        ] == n,
    )

    check(
        "Comparison score rows verified",
        csv_counts[
            "quantum_classical_comparison_v18_4_scores.csv"
        ] == n,
    )

    check(
        "Sensitivity analysis rows verified",
        csv_counts[
            "statistical_validation_v18_5_sensitivity.csv"
        ] == n,
    )

    return n, columns, digest


def validate_scientific_results(reports, n):
    classical = reports["v18_2"]

    quantum = reports["v18_3"]

    comparison = reports["v18_4"]

    statistical = reports["v18_5"]

    c_results = classical.get("results", {})

    q_method = quantum.get("quantum_method", {})

    q_kernel = quantum.get("kernel_validation", {})

    comp = comparison.get("comparison", {})

    stats_spearman = statistical.get(
        "spearman", {}
    )

    stats_top = statistical.get("top_k", {})

    check(
        "Classical anomaly counts consistent",
        c_results.get("normal_samples", -1)
        + c_results.get("anomaly_samples", -1)
        == n,
    )

    check(
        "Quantum calculation is simulated",
        q_method.get("physical_quantum_hardware")
        is False,
    )

    check(
        "Quantum kernel dimensions consistent",
        q_kernel.get("matrix_shape") == [n, n],
    )

    check(
        "Quantum kernel PSD confirmed",
        q_kernel.get("positive_semidefinite")
        is True,
    )

    check(
        "Quantum qubit count valid",
        isinstance(
            q_method.get("number_of_qubits"),
            int,
        )
        and q_method["number_of_qubits"] >= 1,
    )

    check(
        "Spearman correlation agrees",
        close_values(
            comp.get("spearman_rank_correlation"),
            stats_spearman.get(
                "observed_correlation"
            ),
        ),
    )

    check(
        "Top-K overlap agrees",
        comp.get("top_k_overlap")
        == stats_top.get("observed_overlap"),
    )

    check(
        "Top-K size agrees",
        comp.get("top_k")
        == stats_top.get("k"),
    )

    bootstrap = stats_spearman.get(
        "bootstrap", {}
    )

    lower = finite_number(
        bootstrap.get("ci_lower")
    )

    upper = finite_number(
        bootstrap.get("ci_upper")
    )

    check(
        "Bootstrap confidence interval valid",
        lower is not None
        and upper is not None
        and -1 <= lower <= upper <= 1,
    )

    permutation = stats_spearman.get(
        "permutation", {}
    )

    p_value = finite_number(
        permutation.get("p_value_two_sided")
    )

    check(
        "Permutation p-value valid",
        p_value is not None
        and 0 <= p_value <= 1,
    )

    top_p_value = finite_number(
        stats_top.get(
            "hypergeometric_tail_p_value"
        )
    )

    check(
        "Top-K exact p-value valid",
        top_p_value is not None
        and 0 <= top_p_value <= 1,
    )

    check(
        "No quantum advantage claimed",
        comparison.get(
            "quantum_advantage_demonstrated"
        ) is False,
    )


def artifact_manifest():
    paths = (
        [DATASET]
        + [V18 / name for name in REPORT_NAMES.values()]
        + [V18 / name for name in OTHER_ARTIFACTS]
    )

    return [
        {
            "path": str(path.relative_to(ROOT)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in paths
    ]


def build_dashboard(reports, n, status):
    classical = reports["v18_2"]
    quantum = reports["v18_3"]
    comparison = reports["v18_4"]
    statistical = reports["v18_5"]

    comp = comparison["comparison"]
    stats = statistical["spearman"]
    top = statistical["top_k"]

    return {
        "project": "Quantum Cyber Defense Arena",
        "version": "V18.6",
        "status": status,
        "data_mode": "SAVED_RESEARCH_RESULTS",
        "is_live": False,
        "research_samples": n,
        "classical": {
            "model": "Isolation Forest",
            "anomaly_count": classical[
                "results"
            ]["anomaly_samples"],
            "runtime_seconds": classical[
                "runtime"
            ]["total_seconds"],
        },
        "quantum": {
            "model": "Qiskit Fidelity Kernel",
            "qubits": quantum[
                "quantum_method"
            ]["number_of_qubits"],
            "layers": quantum[
                "quantum_method"
            ]["circuit_layers"],
            "kernel_shape": quantum[
                "kernel_validation"
            ]["matrix_shape"],
            "runtime_seconds": quantum[
                "runtime"
            ]["total_seconds"],
            "simulated": True,
        },
        "comparison": {
            "spearman": comp[
                "spearman_rank_correlation"
            ],
            "top_k": comp["top_k"],
            "overlap": comp["top_k_overlap"],
            "jaccard": comp["top_k_jaccard"],
            "bootstrap_ci_lower": stats[
                "bootstrap"
            ]["ci_lower"],
            "bootstrap_ci_upper": stats[
                "bootstrap"
            ]["ci_upper"],
            "permutation_p_value": stats[
                "permutation"
            ]["p_value_two_sided"],
            "top_k_exact_p_value": top[
                "hypergeometric_tail_p_value"
            ],
        },
        "disclaimers": [
            "Results are not real-time.",
            "Only a small transaction sample was used.",
            "No verified cyberattack labels.",
            "No quantum computational advantage established.",
            "Runtime values are not a fair speed comparison.",
            "The quantum method ran on a simulator.",
        ],
    }


def build_markdown(reports, checks_passed):
    classical = reports["v18_2"]
    quantum = reports["v18_3"]
    comparison = reports["v18_4"]
    statistical = reports["v18_5"]

    comp = comparison["comparison"]
    stats = statistical["spearman"]
    top = statistical["top_k"]

    return f"""# Quantum Cyber Defense Arena

## V18 - Quantum-Classical Benchmark Lab

**Research release:** V18.6

**Release validation:** PASS

**Release checks passed:** {checks_passed}

### Completed stages

| Version | Research module |
|---|---|
| V18.1 | Benchmark Architecture |
| V18.2 | Classical Isolation Forest Baseline |
| V18.3 | Qiskit Quantum Kernel Simulator |
| V18.4 | Quantum-Classical Comparison |
| V18.5 | Statistical Validation |
| V18.6 | Research Release and Data Export |

### Research dataset

- Blockchain-derived transaction samples: {comparison['dataset']['samples']}
- Original numerical features: {comparison['dataset']['original_features']}
- Independently verified malicious labels: No
- Independent test-set evaluation: No

### Classical baseline

- Method: Isolation Forest
- Statistical anomalies: {classical['results']['anomaly_samples']}
- Recorded total runtime: {classical['runtime']['total_seconds']} seconds

### Quantum simulator

- Framework: Qiskit
- Qubits: {quantum['quantum_method']['number_of_qubits']}
- Circuit layers: {quantum['quantum_method']['circuit_layers']}
- Kernel: fidelity-based quantum kernel
- Kernel dimensions: {quantum['kernel_validation']['matrix_shape']}
- Recorded total runtime: {quantum['runtime']['total_seconds']} seconds

### Cross-method results

| Statistic | Result |
|---|---|
| Spearman correlation | {comp['spearman_rank_correlation']} |
| Top-K size | {comp['top_k']} |
| Shared Top-K samples | {comp['top_k_overlap']} |
| Top-K Jaccard | {comp['top_k_jaccard']} |
| Bootstrap 95% lower bound | {stats['bootstrap']['ci_lower']} |
| Bootstrap 95% upper bound | {stats['bootstrap']['ci_upper']} |
| Permutation p-value | {stats['permutation']['p_value_two_sided']} |
| Exact Top-K p-value | {top['hypergeometric_tail_p_value']} |

### Scientific interpretation

The methods exhibit a positive anomaly-ranking
association on this small research dataset.

The experiment does not demonstrate:
- Confirmed cyberattack detection accuracy
- Better quantum predictive performance
- Quantum computational advantage
- Production readiness

The two methods use different anomaly scoring
definitions and different computational pipelines.

### Limitations

1. Small sample size.
2. No verified malicious-transaction labels.
3. In-sample exploratory comparison.
4. Possible dependence between transactions.
5. No physical quantum hardware.
6. No repeated controlled runtime benchmark.
7. Exploratory statistics require larger independent datasets.

### Reproducibility

The release JSON contains SHA-256 fingerprints
for the underlying research artifacts.

### Dashboard export

`frontend/public/v18/quantum_classical_v18_dashboard.json`

This is a static data export. It does not connect
the results to the React interface automatically.

### Next development stage

V19 - Autonomous Multi-Agent Research.
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V18.6 - QUANTUM-CLASSICAL RESEARCH RELEASE")
    print("=" * 70)

    validate_source_files()

    reports = {
        key: read_json(V18 / filename)
        for key, filename in REPORT_NAMES.items()
    }

    validate_reports(reports)

    samples, features, digest = validate_data(reports)

    validate_scientific_results(
        reports,
        samples,
    )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "RESEARCH_RELEASE_PASS"
        if failed == 0
        else "RESEARCH_RELEASE_FAIL"
    )

    release = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V18.6",
        "module": (
            "Quantum-Classical Research Release"
        ),
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "checks_passed": passed,
        "checks_failed": failed,
        "checks": CHECKS,
        "dataset": {
            "samples": samples,
            "feature_count": len(features),
            "feature_names": features,
            "sha256": digest,
        },
        "research": build_dashboard(
            reports,
            samples,
            status,
        ),
        "artifact_fingerprints": artifact_manifest(),
        "scientific_limitations": [
            "Small research sample.",
            "No verified malicious labels.",
            "In-sample evaluation only.",
            "No validated quantum advantage.",
            "Different algorithms and score definitions.",
            "No controlled runtime superiority established.",
        ],
        "next_stage": (
            "V19 - Autonomous Multi-Agent Research"
        ),
    }

    # Always preserve the complete validation result.
    save_json(
        RESULT_JSON,
        release,
    )

    if failed > 0:
        print()
        print(f"CHECKS FAILED: {failed}")
        print("V18.6 RESULT: RESEARCH_RELEASE_FAIL")
        print(f"REPORT SAVED: {RESULT_JSON}")
        return 1

    dashboard = build_dashboard(
        reports,
        samples,
        status,
    )

    markdown = build_markdown(
        reports,
        passed,
    )

    save_json(
        DASHBOARD_JSON,
        dashboard,
    )

    RESULT_MD.write_text(
        markdown,
        encoding="utf-8",
    )

    print()
    print("=" * 70)
    print("V18 FINAL RESEARCH RELEASE")
    print("=" * 70)

    print(f"DATASET SAMPLES: {samples}")
    print(f"FEATURES: {len(features)}")
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")

    print()
    print(f"RELEASE REPORT: {RESULT_JSON}")
    print(f"RESEARCH DOCUMENT: {RESULT_MD}")
    print(f"DASHBOARD DATA: {DASHBOARD_JSON}")

    print()
    print("V18.6 RESULT: RESEARCH_RELEASE_PASS")
    print("=" * 70)

    print(
        "NOTE: Dashboard JSON is exported, "
        "but React integration is not yet performed."
    )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as error:
        print()
        print(
            "V18.6 FAILED: "
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)
