
"""
QUANTUM CYBER DEFENSE ARENA
V18.4 - QUANTUM-CLASSICAL COMPARISON

Compares:
V18.2 - Classical Isolation Forest anomaly scores
V18.3 - Qiskit quantum kernel novelty scores

Checks source integrity, sample alignment,
rank correlation and top-K overlap.

Standard library only.
No verified attack labels or quantum advantage claims.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V17 = ROOT / "research_validation" / "v17"
V18 = ROOT / "research_validation" / "v18"

DATASET = V17 / "training_features_v17_1.csv"

ARCH_FILE = V18 / "benchmark_architecture_v18_1_results.json"
CLASSICAL_REPORT = V18 / "classical_baseline_v18_2_results.json"
QUANTUM_REPORT = V18 / "quantum_kernel_v18_3_results.json"

CLASSICAL_CSV = V18 / "classical_baseline_v18_2_scores.csv"
QUANTUM_CSV = V18 / "quantum_kernel_v18_3_scores.csv"
KERNEL_CSV = V18 / "quantum_kernel_v18_3_matrix.csv"

OUTPUT_JSON = V18 / "quantum_classical_comparison_v18_4_results.json"
OUTPUT_CSV = V18 / "quantum_classical_comparison_v18_4_scores.csv"

TOP_K = 5
CHECKS = []


def check(name, condition, details=""):
    passed = bool(condition)

    CHECKS.append({
        "name": name,
        "passed": passed,
        "details": str(details),
    })

    print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if not passed and details:
        print(f"       {details}")

    return passed


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames or []
        rows = list(reader)

    if not fields:
        raise ValueError(f"No CSV header: {path.name}")

    if len(fields) != len(set(fields)):
        raise ValueError(f"Duplicate CSV columns: {path.name}")

    if not rows:
        raise ValueError(f"Empty CSV: {path.name}")

    return fields, rows


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def finite_float(value, name):
    result = float(value)

    if not math.isfinite(result):
        raise ValueError(f"Invalid numeric value: {name}")

    return result


def load_scores(path, score_column):
    fields, rows = read_csv(path)

    if "sample_index" not in fields:
        raise ValueError(f"Missing sample_index: {path.name}")

    if score_column not in fields:
        raise ValueError(
            f"Missing {score_column}: {path.name}"
        )

    indexes = []
    scores = []
    flags = []

    for row in rows:
        index = int(row["sample_index"])
        score = finite_float(
            row[score_column],
            score_column,
        )

        indexes.append(index)
        scores.append(score)

        if "is_anomaly" in fields:
            flag = int(row["is_anomaly"])

            if flag not in (0, 1):
                raise ValueError("Invalid anomaly flag.")

            flags.append(flag)

    if len(set(indexes)) != len(indexes):
        raise ValueError(
            f"Duplicate sample indexes: {path.name}"
        )

    expected = list(range(1, len(indexes) + 1))

    if indexes != expected:
        raise ValueError(
            f"Sample indexes must be sequential: {path.name}"
        )

    return scores, flags


def average_ranks(values):
    """
    Average ranks for ties.
    Rank 1 = lowest score.
    """

    count = len(values)
    order = sorted(
        range(count),
        key=lambda index: values[index],
    )

    ranks = [0.0] * count
    position = 0

    while position < count:
        end = position + 1

        while (
            end < count
            and values[order[end]] == values[order[position]]
        ):
            end += 1

        average = (position + 1 + end) / 2.0

        for current in range(position, end):
            ranks[order[current]] = average

        position = end

    return ranks


def pearson(x, y):
    if len(x) != len(y) or len(x) < 2:
        return None

    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)

    centered_x = [value - mean_x for value in x]
    centered_y = [value - mean_y for value in y]

    numerator = sum(
        a * b
        for a, b in zip(centered_x, centered_y)
    )

    denominator = math.sqrt(
        sum(a * a for a in centered_x)
        * sum(b * b for b in centered_y)
    )

    if denominator <= 1e-15:
        return None

    return max(
        -1.0,
        min(1.0, numerator / denominator),
    )


def spearman(x, y):
    return pearson(
        average_ranks(x),
        average_ranks(y),
    )


def top_k_indexes(scores, k):
    """
    Larger score means more unusual.
    Ties are resolved by original sample index.
    """

    order = sorted(
        range(len(scores)),
        key=lambda i: (-scores[i], i),
    )

    return {index + 1 for index in order[:k]}


def jaccard(first, second):
    union = first | second

    if not union:
        return 1.0

    return len(first & second) / len(union)


def anomaly_flag_agreement(classical_flags, quantum_top):
    quantum_flags = [
        int(index in quantum_top)
        for index in range(1, len(classical_flags) + 1)
    ]

    return statistics.mean(
        int(a == b)
        for a, b in zip(classical_flags, quantum_flags)
    )


def load_kernel_diagonal():
    fields, rows = read_csv(KERNEL_CSV)

    n = len(rows)

    if len(fields) != n + 1:
        raise ValueError("Kernel CSV dimensions mismatch.")

    matrix = []

    for row_index, row in enumerate(rows):
        if int(row["sample_index"]) != row_index + 1:
            raise ValueError("Kernel row index mismatch.")

        matrix.append([
            finite_float(
                row[f"sample_{j + 1}"],
                "kernel",
            )
            for j in range(n)
        ])

    for i in range(n):
        if not math.isclose(
            matrix[i][i],
            1.0,
            abs_tol=1e-6,
        ):
            raise ValueError("Kernel diagonal is invalid.")

        for j in range(n):
            if not -1e-6 <= matrix[i][j] <= 1.0 + 1e-6:
                raise ValueError("Kernel fidelity out of bounds.")

            if not math.isclose(
                matrix[i][j],
                matrix[j][i],
                abs_tol=1e-6,
            ):
                raise ValueError("Kernel symmetry mismatch.")

    return matrix


def write_sample_comparison(classical, quantum, flags):
    classical_ranks = average_ranks(classical)
    quantum_ranks = average_ranks(quantum)

    classical_top = top_k_indexes(classical, TOP_K)
    quantum_top = top_k_indexes(quantum, TOP_K)

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "sample_index",
            "classical_anomaly_score",
            "quantum_novelty_score",
            "classical_rank_low_to_high",
            "quantum_rank_low_to_high",
            "classical_is_anomaly",
            "classical_top_k",
            "quantum_top_k",
        ])

        for index in range(len(classical)):
            sample = index + 1

            writer.writerow([
                sample,
                round(classical[index], 10),
                round(quantum[index], 10),
                classical_ranks[index],
                quantum_ranks[index],
                flags[index],
                int(sample in classical_top),
                int(sample in quantum_top),
            ])

    return classical_top, quantum_top


def main():
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V18.4 - QUANTUM-CLASSICAL COMPARISON")
    print("=" * 68)

    V18.mkdir(parents=True, exist_ok=True)

    required = [
        DATASET,
        ARCH_FILE,
        CLASSICAL_REPORT,
        QUANTUM_REPORT,
        CLASSICAL_CSV,
        QUANTUM_CSV,
        KERNEL_CSV,
    ]

    for path in required:
        check(
            f"Required file: {path.name}",
            path.is_file(),
            path,
        )

    if not all(path.is_file() for path in required):
        raise FileNotFoundError(
            "Required V18 files are missing."
        )

    arch = read_json(ARCH_FILE)
    classical_report = read_json(CLASSICAL_REPORT)
    quantum_report = read_json(QUANTUM_REPORT)

    check(
        "V18.1 architecture PASS",
        arch.get("status") == "ARCHITECTURE_PASS",
    )

    check(
        "V18.2 classical PASS",
        classical_report.get("status")
        == "CLASSICAL_BASELINE_PASS",
    )

    check(
        "V18.3 quantum PASS",
        quantum_report.get("status")
        == "QUANTUM_KERNEL_PASS",
    )

    digest = sha256(DATASET)

    hashes = [
        arch.get("dataset", {}).get("sha256"),
        classical_report.get("dataset", {}).get("sha256"),
        quantum_report.get("dataset", {}).get("sha256"),
    ]

    check(
        "Identical dataset SHA-256",
        all(value == digest for value in hashes),
    )

    dataset_fields, dataset_rows = read_csv(DATASET)
    n = len(dataset_rows)

    check(
        "Dataset sample counts agree",
        n == arch.get("dataset", {}).get("samples")
        == classical_report.get("dataset", {}).get("samples")
        == quantum_report.get("dataset", {}).get("samples"),
    )

    check(
        "Dataset feature order agrees",
        dataset_fields
        == arch.get("dataset", {}).get("feature_names")
        == classical_report.get("dataset", {}).get("feature_names")
        == quantum_report.get("dataset", {}).get("feature_names"),
    )

    classical_scores, classical_flags = load_scores(
        CLASSICAL_CSV,
        "anomaly_score",
    )

    quantum_scores, _ = load_scores(
        QUANTUM_CSV,
        "quantum_novelty_score",
    )

    check(
        "Sample-level score alignment",
        len(classical_scores) == len(quantum_scores) == n
        and len(classical_flags) == n,
    )

    kernel = load_kernel_diagonal()

    check(
        "Kernel matrix sample count",
        len(kernel) == n,
    )

    # Recalculate quantum novelty from the saved kernel.
    expected_novelty = [
        1.0 - sum(
            kernel[i][j]
            for j in range(n)
            if j != i
        ) / (n - 1)
        for i in range(n)
    ]

    check(
        "Quantum novelty matches saved kernel",
        all(
            math.isclose(
                actual,
                expected,
                abs_tol=1e-7,
            )
            for actual, expected in zip(
                quantum_scores,
                expected_novelty,
            )
        ),
    )

    # Verify the classical report count against saved flags.
    reported_anomalies = classical_report.get(
        "results", {}
    ).get("anomaly_samples")

    check(
        "Classical anomaly count matches report",
        sum(classical_flags) == reported_anomalies,
    )

    if not all(item["passed"] for item in CHECKS):
        raise ValueError(
            "Input integrity checks failed. "
            "Comparison has not been released."
        )

    k = min(TOP_K, n)

    classical_top, quantum_top = write_sample_comparison(
        classical_scores,
        quantum_scores,
        classical_flags,
    )

    correlation = spearman(
        classical_scores,
        quantum_scores,
    )

    overlap = len(classical_top & quantum_top)
    union = len(classical_top | quantum_top)

    top_jaccard = jaccard(
        classical_top,
        quantum_top,
    )

    classical_fit = finite_float(
        classical_report["runtime"]["fit_seconds"],
        "classical fit",
    )

    classical_inference = finite_float(
        classical_report["runtime"]["inference_seconds"],
        "classical inference",
    )

    quantum_total = finite_float(
        quantum_report["runtime"]["total_seconds"],
        "quantum total runtime",
    )

    check(
        "Comparison scores are finite",
        all(map(math.isfinite, classical_scores))
        and all(map(math.isfinite, quantum_scores)),
    )

    check(
        "Top-K sets have correct size",
        len(classical_top) == k
        and len(quantum_top) == k,
    )

    check(
        "Spearman correlation calculable",
        correlation is not None,
    )

    passed = sum(item["passed"] for item in CHECKS)
    failed = len(CHECKS) - passed

    status = (
        "COMPARISON_PASS"
        if failed == 0
        else "COMPARISON_FAIL"
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V18.4",
        "module": "Quantum-Classical Comparison",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "dataset": {
            "sha256": digest,
            "samples": n,
            "original_features": len(dataset_fields),
        },
        "methods": {
            "classical": "IsolationForest",
            "quantum": (
                "Qiskit simulated fidelity kernel "
                "with mean-fidelity novelty scoring"
            ),
        },
        "comparison": {
            "spearman_rank_correlation": (
                round(correlation, 8)
                if correlation is not None
                else None
            ),
            "top_k": k,
            "classical_top_k": sorted(classical_top),
            "quantum_top_k": sorted(quantum_top),
            "top_k_overlap": overlap,
            "top_k_union": union,
            "top_k_jaccard": round(top_jaccard, 8),
            "top_k_overlap_fraction": round(
                overlap / k,
                8,
            ),
            "classical_anomaly_flags": sum(classical_flags),
            "classical_vs_quantum_top_k_flag_agreement": round(
                anomaly_flag_agreement(
                    classical_flags,
                    quantum_top,
                ),
                8,
            ),
        },
        "runtime_observations": {
            "classical_fit_seconds": classical_fit,
            "classical_inference_seconds": classical_inference,
            "classical_total_seconds": round(
                classical_fit + classical_inference,
                6,
            ),
            "quantum_preprocessing_simulation_kernel_seconds": (
                quantum_total
            ),
            "timing_comparison_is_fair": False,
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "verified_attack_labels": False,
        "quantum_advantage_demonstrated": False,
        "limitations": [
            "Only 20 blockchain transaction samples.",
            "No independently verified cyberattack labels.",
            "No independent test set.",
            "Isolation Forest and quantum novelty scores "
            "have different statistical meanings.",
            "Top-K overlap measures agreement, not accuracy.",
            "Runtime figures describe different algorithms "
            "and were not collected under repeated "
            "controlled benchmark conditions.",
            "Quantum computations used local simulation, "
            "not physical quantum hardware.",
            "No quantum speedup or detection superiority "
            "is established.",
        ],
        "outputs": {
            "comparison_csv": str(
                OUTPUT_CSV.relative_to(ROOT)
            ),
            "report_json": str(
                OUTPUT_JSON.relative_to(ROOT)
            ),
        },
        "next_stage": (
            "V18.5 Statistical Validation"
        ),
    }

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

    print()
    print("=" * 68)
    print("V18.4 COMPARISON RESULTS")
    print("=" * 68)
    print(f"SAMPLES: {n}")
    print(f"CLASSICAL ANOMALIES: {sum(classical_flags)}")
    print(f"TOP-K: {k}")
    print(f"TOP-K OVERLAP: {overlap}/{k}")
    print(f"TOP-K JACCARD: {top_jaccard:.6f}")

    if correlation is not None:
        print(
            "SPEARMAN RANK CORRELATION: "
            f"{correlation:.6f}"
        )

    print()
    print(
        "CLASSICAL TOTAL SECONDS: "
        f"{classical_fit + classical_inference:.6f}"
    )
    print(
        "QUANTUM SIMULATION TOTAL SECONDS: "
        f"{quantum_total:.6f}"
    )
    print("FAIR SPEED COMPARISON: NO")

    print()
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"CSV SAVED: {OUTPUT_CSV}")
    print(f"JSON SAVED: {OUTPUT_JSON}")
    print(f"V18.4 RESULT: {status}")
    print("=" * 68)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as error:
        print()
        print(
            "V18.4 FAILED: "
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)
