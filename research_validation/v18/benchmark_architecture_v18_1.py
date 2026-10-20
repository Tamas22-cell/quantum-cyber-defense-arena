
"""
QUANTUM CYBER DEFENSE ARENA
V18.1 - QUANTUM-CLASSICAL BENCHMARK ARCHITECTURE

Creates a reproducible benchmark manifest from
the V17 blockchain training feature dataset.

This stage does not train or compare models.
Python standard library only.
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

INPUT = V17 / "training_features_v17_1.csv"
V17_RELEASE = V17 / "ai_training_research_release_v17_5_results.json"

OUTPUT = V18 / "benchmark_architecture_v18_1_results.json"

RANDOM_STATE = 42

CHECKS = []


def check(name, condition, detail=""):
    passed = bool(condition)

    CHECKS.append({
        "name": name,
        "passed": passed,
        "detail": str(detail),
    })

    print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if not passed and detail:
        print(f"       {detail}")

    return passed


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def load_dataset():
    with INPUT.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        features = reader.fieldnames or []
        rows = list(reader)

    if not features:
        raise ValueError("Dataset has no feature columns.")

    if len(features) != len(set(features)):
        raise ValueError("Duplicate feature names.")

    if not rows:
        raise ValueError("Dataset has no samples.")

    matrix = []

    for row_number, row in enumerate(rows, start=2):
        sample = []

        for feature in features:
            value = row.get(feature)

            try:
                number = float(value)
            except (ValueError, TypeError) as exc:
                raise ValueError(
                    f"Invalid numeric value at row "
                    f"{row_number}, feature {feature}"
                ) from exc

            if not math.isfinite(number):
                raise ValueError(
                    f"Non-finite value at row {row_number}, "
                    f"feature {feature}"
                )

            sample.append(number)

        matrix.append(sample)

    return features, matrix


def feature_statistics(features, matrix):
    result = {}

    for index, feature in enumerate(features):
        values = [row[index] for row in matrix]

        result[feature] = {
            "min": min(values),
            "max": max(values),
            "mean": round(statistics.mean(values), 8),
            "population_std": round(
                statistics.pstdev(values),
                8,
            ),
            "unique_values": len(set(values)),
        }

    return result


def main():
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V18.1 - QUANTUM-CLASSICAL BENCHMARK ARCHITECTURE")
    print("=" * 68)

    V18.mkdir(parents=True, exist_ok=True)

    check(
        "V17 feature dataset exists",
        INPUT.is_file(),
        str(INPUT),
    )

    check(
        "V17 research release report exists",
        V17_RELEASE.is_file(),
        str(V17_RELEASE),
    )

    features = []
    matrix = []
    dataset_error = None

    if INPUT.is_file():
        try:
            features, matrix = load_dataset()

            check(
                "Feature dataset readable",
                True,
            )

        except (OSError, ValueError) as exc:
            dataset_error = str(exc)
            check(
                "Feature dataset readable",
                False,
                dataset_error,
            )

    check(
        "Sufficient samples for architecture smoke test",
        len(matrix) >= 10,
        f"Samples: {len(matrix)}",
    )

    check(
        "At least two numerical features",
        len(features) >= 2,
        f"Features: {len(features)}",
    )

    release = None

    if V17_RELEASE.is_file():
        try:
            with V17_RELEASE.open(
                "r",
                encoding="utf-8-sig",
            ) as file:
                release = json.load(file)

            check(
                "V17 research release validated",
                release.get("status")
                == "RESEARCH_RELEASE_PASS"
                and release.get("checks_failed") == 0,
            )

        except (OSError, ValueError) as exc:
            check(
                "V17 research release readable",
                False,
                str(exc),
            )

    if matrix:
        stats = feature_statistics(features, matrix)
    else:
        stats = {}

    passed = sum(item["passed"] for item in CHECKS)
    failed = len(CHECKS) - passed

    status = (
        "ARCHITECTURE_PASS"
        if failed == 0
        else "ARCHITECTURE_FAIL"
    )

    manifest = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V18.1",
        "module": "Quantum-Classical Benchmark Architecture",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "dataset": {
            "source": str(INPUT.relative_to(ROOT)),
            "sha256": sha256(INPUT) if INPUT.is_file() else None,
            "samples": len(matrix),
            "feature_count": len(features),
            "feature_names": features,
            "feature_statistics": stats,
        },
        "benchmark_design": {
            "random_state": RANDOM_STATE,
            "classical_baseline": "IsolationForest",
            "quantum_candidate": (
                "Quantum kernel or simulator method "
                "to be defined and implemented in V18.3"
            ),
            "same_input_dataset_required": True,
            "same_test_partitions_required": True,
            "preprocessing_fit_on_training_only": True,
            "report_runtime_and_resources": True,
            "report_model_parameters": True,
            "avoid_ground_truth_accuracy_claims": True,
        },
        "dataset_limitations": {
            "verified_attack_labels": False,
            "independent_test_set": False,
            "sample_size_sufficient_for_publication": False,
            "scientific_claim": (
                "Architecture and data integrity only"
            ),
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "next_stage": "V18.2 Classical AI Baseline",
    }

    with OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            manifest,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

    print()
    print("=" * 68)
    print("V18.1 BENCHMARK ARCHITECTURE RESULTS")
    print("=" * 68)
    print(f"SAMPLES: {len(matrix)}")
    print(f"FEATURES: {len(features)}")
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"V18.1 RESULT: {status}")
    print(f"REPORT SAVED: {OUTPUT}")
    print("=" * 68)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(
            f"V18.1 FATAL ERROR: "
            f"{type(exc).__name__}: {exc}"
        )
        sys.exit(1)
