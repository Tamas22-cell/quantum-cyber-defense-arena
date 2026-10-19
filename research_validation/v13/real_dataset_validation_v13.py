
"""
QUANTUM CYBER DEFENSE ARENA
V13.0 - REAL DATASET VALIDATION

Evaluates existing Classical AI, Quantum AI
and Hybrid Fusion models on an external CSV.

IMPORTANT:
- No synthetic dataset is generated.
- No example scores are invented.
- Five required features must be present.
- Input features must already be normalized to [0, 1].
- Labels: 0 = normal, 1 = anomaly.
- Use only genuinely measured external data.

Research validation, not operational certification.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sklearn.model_selection import train_test_split

from backend.ai_detection.detector import AIThreatDetector
from backend.quantum_detection.quantum_detector import (
    QuantumAnomalyDetector,
)

from research_validation.v11.benchmark_v11 import (
    CLASSICAL_FEATURES,
    QUANTUM_FEATURES,
    calculate_metrics,
    classical_scores,
    quantum_scores,
    validate_configuration,
)


VERSION = "13.0.0"

HERE = Path(__file__).resolve().parent

DATASET_FILE = HERE / "real_security_dataset.csv"

OUTPUT_FILE = HERE / "real_dataset_validation_v13_results.json"

LABEL_COLUMN = "label"

TEST_FRACTION = 0.30

SEED = 2026

MAX_TEST_SAMPLES = 500

MODEL_NAMES = (
    "classical",
    "quantum",
    "hybrid",
)


def print_header() -> None:
    print()
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA V13")
    print("REAL DATASET VALIDATION")
    print("=" * 68)
    print()
    print("VERSION:", VERSION)
    print("DATASET:", DATASET_FILE)
    print("MODE: EXTERNAL DATA VALIDATION")
    print()


def load_external_dataset():
    """
    Load an independently supplied dataset.

    The CSV must contain:
    - All five V11 classical feature columns.
    - A binary label column.

    This function deliberately refuses to generate
    fallback synthetic data.
    """

    if not DATASET_FILE.is_file():
        raise FileNotFoundError(
            "\nEXTERNAL DATASET NOT FOUND.\n\n"
            "Expected file:\n"
            f"{DATASET_FILE}\n\n"
            "Required CSV columns:\n"
            + ", ".join(CLASSICAL_FEATURES)
            + ", label\n\n"
            "All five features must be numeric "
            "and normalized to [0, 1].\n"
            "The label must be 0 (normal) "
            "or 1 (anomaly).\n"
            "Do not use synthetic benchmark "
            "results as real-world input."
        )

    features = []
    labels = []

    with DATASET_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as stream:
        reader = csv.DictReader(stream)

        if not reader.fieldnames:
            raise ValueError("The CSV header is missing.")

        columns = set(reader.fieldnames)

        required = set(CLASSICAL_FEATURES)
        required.add(LABEL_COLUMN)

        missing = sorted(required - columns)

        if missing:
            raise ValueError(
                "Missing CSV columns: "
                + ", ".join(missing)
            )

        for line_number, row in enumerate(
            reader,
            start=2,
        ):
            try:
                values = [
                    float(row[name])
                    for name in CLASSICAL_FEATURES
                ]

                label = int(row[LABEL_COLUMN])

            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(
                    f"Invalid data at CSV line {line_number}: "
                    f"{exc}"
                ) from exc

            if any(
                not math.isfinite(value)
                or not 0 <= value <= 1
                for value in values
            ):
                raise ValueError(
                    f"Feature outside [0, 1] "
                    f"at CSV line {line_number}."
                )

            if label not in (0, 1):
                raise ValueError(
                    f"Invalid label at CSV line {line_number}. "
                    "Use 0 or 1."
                )

            features.append(values)
            labels.append(label)

    if len(features) < 100:
        raise ValueError(
            "At least 100 labeled observations "
            "are required for this V13 benchmark."
        )

    X = np.asarray(features, dtype=float)
    y = np.asarray(labels, dtype=int)

    classes, counts = np.unique(
        y,
        return_counts=True,
    )

    if len(classes) != 2:
        raise ValueError(
            "Both normal and anomaly samples are required."
        )

    if min(counts) < 10:
        raise ValueError(
            "At least 10 samples of each class "
            "are required."
        )

    return X, y


def prepare_data(
    X: np.ndarray,
    y: np.ndarray,
):
    """
    Reproducible stratified holdout.

    Test observations are not used
    for fitting the classical detector.
    """

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_FRACTION,
            random_state=SEED,
            stratify=y,
        )
    )

    # Train the anomaly detector on normal data only.
    X_train_normal = X_train[y_train == 0]

    if len(X_train_normal) < 20:
        raise ValueError(
            "Not enough normal training observations."
        )

    if len(X_test) > MAX_TEST_SAMPLES:
        X_test, _, y_test, _ = train_test_split(
            X_test,
            y_test,
            train_size=MAX_TEST_SAMPLES,
            random_state=SEED,
            stratify=y_test,
        )

    return (
        X_train_normal,
        X_test,
        y_test,
    )


def evaluate_models(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> dict:
    """
    Run the existing V11 detection implementations.

    Hybrid:
      both anomaly -> anomaly
      both normal -> normal
      disagreement -> REVIEW

    REVIEW is counted as negative in binary
    metrics and reported separately.
    """

    print("TRAINING CLASSICAL AI...")

    classical = AIThreatDetector(seed=SEED)
    classical.train(X_train)

    print("INITIALIZING QUANTUM SIMULATOR...")

    quantum = QuantumAnomalyDetector(
        threshold=0.35
    )

    print("RUNNING CLASSICAL DETECTION...")

    started = perf_counter()

    classical_score, classical_pred = (
        classical_scores(
            classical,
            X_test,
        )
    )

    classical_time = (
        perf_counter() - started
    )

    print("RUNNING QUANTUM DETECTION...")

    started = perf_counter()

    quantum_score, quantum_pred = (
        quantum_scores(
            quantum,
            X_test,
        )
    )

    quantum_time = (
        perf_counter() - started
    )

    agree = classical_pred == quantum_pred

    hybrid_pred = np.where(
        agree,
        classical_pred,
        -1,
    )

    hybrid_binary = (
        hybrid_pred == 1
    ).astype(int)

    fusion_score = (
        0.5 * classical_score
        + 0.5 * quantum_score
    )

    classical_metrics = calculate_metrics(
        y_test,
        classical_pred,
    )

    quantum_metrics = calculate_metrics(
        y_test,
        quantum_pred,
    )

    hybrid_metrics = calculate_metrics(
        y_test,
        hybrid_binary,
    )

    return {
        "classical": {
            **classical_metrics,
            "inference_seconds": round(
                classical_time,
                4,
            ),
        },
        "quantum": {
            **quantum_metrics,
            "inference_seconds": round(
                quantum_time,
                4,
            ),
        },
        "hybrid": {
            **hybrid_metrics,
            "review_rate": round(
                float(np.mean(~agree)),
                6,
            ),
            "fusion_score_mean": round(
                float(np.mean(fusion_score)),
                6,
            ),
        },
    }


def print_results(results: dict) -> None:
    print()
    print("=" * 68)
    print("V13 REAL DATASET RESULTS")
    print("=" * 68)

    for model in MODEL_NAMES:
        metrics = results[model]

        print()
        print(model.upper())
        print("-" * 35)

        print(
            f"PRECISION: {metrics['precision'] * 100:.2f}%"
        )

        print(
            f"RECALL:    {metrics['recall'] * 100:.2f}%"
        )

        print(
            f"F1 SCORE:  {metrics['f1'] * 100:.2f}%"
        )

        print(
            f"ACCURACY:  {metrics['accuracy'] * 100:.2f}%"
        )

        print(
            "CONFUSION MATRIX:",
            f"TP={metrics['tp']}",
            f"TN={metrics['tn']}",
            f"FP={metrics['fp']}",
            f"FN={metrics['fn']}",
        )

        if model == "hybrid":
            print(
                f"REVIEW RATE: "
                f"{metrics['review_rate'] * 100:.2f}%"
            )


def main() -> None:
    print_header()

    validate_configuration()

    print(
        "REQUIRED FEATURES:",
        CLASSICAL_FEATURES,
    )

    print(
        "QUANTUM FEATURES:",
        QUANTUM_FEATURES,
    )

    X, y = load_external_dataset()

    print()
    print("EXTERNAL DATASET LOADED")
    print("TOTAL OBSERVATIONS:", len(y))
    print("NORMAL OBSERVATIONS:", int(np.sum(y == 0)))
    print("ANOMALIES:", int(np.sum(y == 1)))

    X_train, X_test, y_test = prepare_data(
        X,
        y,
    )

    print()
    print("NORMAL TRAINING SAMPLES:", len(X_train))
    print("TEST SAMPLES:", len(X_test))
    print()

    start = perf_counter()

    results = evaluate_models(
        X_train,
        X_test,
        y_test,
    )

    elapsed = perf_counter() - start

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "mode": "EXTERNAL_DATA_VALIDATION",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "dataset": {
            "filename": DATASET_FILE.name,
            "source_provenance": (
                "Not independently verified by program"
            ),
            "total_observations": len(y),
            "normal_observations": int(
                np.sum(y == 0)
            ),
            "anomaly_observations": int(
                np.sum(y == 1)
            ),
            "training_normal_samples": len(X_train),
            "test_samples": len(X_test),
            "feature_names": list(
                CLASSICAL_FEATURES
            ),
            "label_column": LABEL_COLUMN,
            "features_pre_normalized": True,
        },
        "methodology": {
            "split": "stratified random holdout",
            "test_fraction": TEST_FRACTION,
            "seed": SEED,
            "maximum_test_samples": MAX_TEST_SAMPLES,
            "classical_model": "Isolation Forest",
            "quantum_model": (
                "Quantum state fidelity simulator"
            ),
            "hybrid_decision": (
                "Agreement-based fusion; "
                "disagreement=REVIEW"
            ),
            "review_binary_policy": (
                "REVIEW treated as negative"
            ),
        },
        "results": results,
        "execution_seconds": round(
            elapsed,
            3,
        ),
        "limitations": [
            "CSV provenance is not independently verified",
            "Feature semantics must match existing detectors",
            "Input is required to be pre-normalized",
            "Random split may leak related records",
            "Time-based or entity-based evaluation "
            "is preferable when applicable",
            "One random split cannot prove stability",
            "Model thresholds were not recalibrated",
            "REVIEW is counted as negative for F1",
            "Classical quantum simulation only",
            "No demonstrated quantum speedup",
            "Real-world effectiveness remains unproven",
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

    print_results(results)

    print()
    print("=" * 68)
    print("V13 REAL DATASET VALIDATION COMPLETED")
    print("=" * 68)

    print()
    print(
        "EXECUTION TIME:",
        round(elapsed, 2),
        "seconds",
    )

    print()
    print("RESULTS SAVED TO:")
    print(OUTPUT_FILE)

    print()
    print(
        "NOTE: Results require verified data provenance "
        "and appropriate feature mapping before "
        "making external validity claims."
    )


if __name__ == "__main__":
    try:
        main()
    except (
        FileNotFoundError,
        ValueError,
    ) as error:
        print()
        print("=" * 68)
        print("V13 VALIDATION NOT STARTED")
        print("=" * 68)
        print(error)
        sys.exit(1)
