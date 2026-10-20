
"""
QUANTUM CYBER DEFENSE ARENA
V18.2 - CLASSICAL AI BASELINE

Reproducible Isolation Forest research benchmark.

- Uses V18.1 verified feature dataset
- Validates source SHA-256
- Trains a classical anomaly detector
- Measures fit and inference runtime
- Saves sample-level scores and research metadata

IMPORTANT:
This is an in-sample technical benchmark.
It is not a supervised threat-detection accuracy test.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import numpy as np
    import sklearn
    from sklearn.ensemble import IsolationForest
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:
    print(f"DEPENDENCY ERROR: {exc}")
    print("Install: python -m pip install numpy scikit-learn")
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[2]
V17 = ROOT / "research_validation" / "v17"
V18 = ROOT / "research_validation" / "v18"

INPUT_FILE = V17 / "training_features_v17_1.csv"

ARCHITECTURE_FILE = (
    V18 / "benchmark_architecture_v18_1_results.json"
)

RESULTS_FILE = (
    V18 / "classical_baseline_v18_2_results.json"
)

SCORES_FILE = (
    V18 / "classical_baseline_v18_2_scores.csv"
)

RANDOM_STATE = 42
N_ESTIMATORS = 200
CONTAMINATION = "auto"
MIN_SAMPLES = 10


def file_sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def load_architecture():
    if not ARCHITECTURE_FILE.is_file():
        raise FileNotFoundError(
            "V18.1 architecture report is missing:\n"
            f"{ARCHITECTURE_FILE}"
        )

    with ARCHITECTURE_FILE.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        manifest = json.load(handle)

    if manifest.get("version") != "V18.1":
        raise ValueError("Invalid V18.1 report version.")

    if manifest.get("status") != "ARCHITECTURE_PASS":
        raise ValueError(
            "V18.1 architecture has not passed validation."
        )

    if manifest.get("checks_failed") != 0:
        raise ValueError("V18.1 contains failed checks.")

    return manifest


def load_dataset():
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            f"Training dataset missing: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        features = reader.fieldnames or []
        rows = list(reader)

    if not features:
        raise ValueError("Training CSV has no header.")

    if len(features) != len(set(features)):
        raise ValueError("Duplicate feature names found.")

    if len(rows) < MIN_SAMPLES:
        raise ValueError(
            f"At least {MIN_SAMPLES} samples required. "
            f"Found: {len(rows)}"
        )

    matrix = []

    for row_number, row in enumerate(rows, start=2):
        values = []

        for feature in features:
            raw = row.get(feature)

            if raw is None or not str(raw).strip():
                values.append(float("nan"))
                continue

            try:
                value = float(raw)
            except (ValueError, TypeError) as exc:
                raise ValueError(
                    f"Invalid value in row {row_number}, "
                    f"feature '{feature}': {raw}"
                ) from exc

            if math.isinf(value):
                raise ValueError(
                    f"Infinite value in row {row_number}, "
                    f"feature '{feature}'"
                )

            values.append(value)

        matrix.append(values)

    data = np.asarray(matrix, dtype=np.float64)

    if np.any(np.all(np.isnan(data), axis=0)):
        raise ValueError(
            "At least one feature is entirely missing."
        )

    return features, data


def validate_dataset(manifest, features, data):
    expected = manifest.get("dataset", {})

    current_hash = file_sha256(INPUT_FILE)

    if expected.get("sha256") != current_hash:
        raise ValueError(
            "Dataset SHA-256 mismatch! "
            "The V17 input changed after V18.1."
        )

    if expected.get("samples") != len(data):
        raise ValueError("Dataset sample count mismatch.")

    if expected.get("feature_count") != len(features):
        raise ValueError("Feature count mismatch.")

    if expected.get("feature_names") != features:
        raise ValueError("Feature order mismatch.")

    print("[PASS] V18.1 architecture validated")
    print("[PASS] Dataset SHA-256 verified")
    print("[PASS] Feature names and order verified")

    return current_hash


def build_model():
    return Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "detector",
                IsolationForest(
                    n_estimators=N_ESTIMATORS,
                    contamination=CONTAMINATION,
                    random_state=RANDOM_STATE,
                    n_jobs=1,
                ),
            ),
        ]
    )


def save_scores(predictions, anomaly_scores, decisions):
    with SCORES_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow([
            "sample_index",
            "anomaly_score",
            "decision_function",
            "is_anomaly",
        ])

        for index, (prediction, score, decision) in enumerate(
            zip(predictions, anomaly_scores, decisions),
            start=1,
        ):
            writer.writerow([
                index,
                round(float(score), 10),
                round(float(decision), 10),
                int(prediction == -1),
            ])


def run():
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V18.2 - CLASSICAL AI BASELINE")
    print("=" * 68)

    V18.mkdir(parents=True, exist_ok=True)

    manifest = load_architecture()
    features, data = load_dataset()

    dataset_hash = validate_dataset(
        manifest,
        features,
        data,
    )

    print()
    print(f"INPUT: {INPUT_FILE}")
    print(f"SAMPLES: {len(data)}")
    print(f"FEATURES: {len(features)}")
    print("MODEL: Isolation Forest")
    print(f"ESTIMATORS: {N_ESTIMATORS}")
    print(f"RANDOM STATE: {RANDOM_STATE}")
    print()

    model = build_model()

    fit_start = time.perf_counter()
    model.fit(data)
    fit_seconds = time.perf_counter() - fit_start

    inference_start = time.perf_counter()

    predictions = model.predict(data)
    anomaly_scores = -model.score_samples(data)
    decisions = model.decision_function(data)

    inference_seconds = (
        time.perf_counter() - inference_start
    )

    if not (
        np.all(np.isfinite(anomaly_scores))
        and np.all(np.isfinite(decisions))
    ):
        raise ValueError(
            "Model produced non-finite scores."
        )

    anomaly_count = int(
        np.sum(predictions == -1)
    )

    normal_count = int(
        np.sum(predictions == 1)
    )

    if normal_count + anomaly_count != len(data):
        raise ValueError("Prediction count mismatch.")

    save_scores(
        predictions,
        anomaly_scores,
        decisions,
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V18.2",
        "module": "Classical AI Baseline",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "CLASSICAL_BASELINE_PASS",
        "dataset": {
            "source": str(INPUT_FILE.relative_to(ROOT)),
            "sha256": dataset_hash,
            "samples": int(len(data)),
            "features": len(features),
            "feature_names": features,
        },
        "model": {
            "name": "IsolationForest",
            "framework": "scikit-learn",
            "framework_version": sklearn.__version__,
            "n_estimators": N_ESTIMATORS,
            "contamination": CONTAMINATION,
            "random_state": RANDOM_STATE,
            "n_jobs": 1,
            "preprocessing": [
                "SimpleImputer(median)",
                "StandardScaler",
            ],
        },
        "results": {
            "normal_samples": normal_count,
            "anomaly_samples": anomaly_count,
            "anomaly_percentage": round(
                100 * anomaly_count / len(data),
                4,
            ),
            "mean_anomaly_score": round(
                float(np.mean(anomaly_scores)),
                10,
            ),
            "min_anomaly_score": round(
                float(np.min(anomaly_scores)),
                10,
            ),
            "max_anomaly_score": round(
                float(np.max(anomaly_scores)),
                10,
            ),
        },
        "runtime": {
            "fit_seconds": round(
                fit_seconds,
                6,
            ),
            "inference_seconds": round(
                inference_seconds,
                6,
            ),
            "total_seconds": round(
                fit_seconds + inference_seconds,
                6,
            ),
            "note": (
                "Wall-clock timings from a single run. "
                "These are not yet statistically "
                "validated benchmark timings."
            ),
        },
        "evaluation": {
            "type": "in_sample_research_smoke_test",
            "verified_attack_labels": False,
            "independent_test_set": False,
            "accuracy_available": False,
            "f1_available": False,
            "quantum_comparison_completed": False,
        },
        "limitations": [
            "Same samples used for model fitting and scoring.",
            "Anomaly flags are not verified cyberattacks.",
            "Only a small transaction sample is available.",
            "No independent holdout evaluation.",
            "No accuracy, recall, precision or F1 is claimed.",
            "A single timing run cannot establish speed advantage.",
            "Future quantum methods may require feature reduction.",
        ],
        "outputs": {
            "scores_csv": str(
                SCORES_FILE.relative_to(ROOT)
            ),
            "report_json": str(
                RESULTS_FILE.relative_to(ROOT)
            ),
        },
        "next_stage": (
            "V18.3 Quantum Kernel / Quantum Simulator"
        ),
    }

    with RESULTS_FILE.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            report,
            handle,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )

    print("[PASS] Classical model trained")
    print("[PASS] Anomaly scores calculated")
    print("[PASS] Research results saved")

    print()
    print("=" * 68)
    print("V18.2 CLASSICAL BENCHMARK RESULTS")
    print("=" * 68)
    print(f"SAMPLES: {len(data)}")
    print(f"FEATURES: {len(features)}")
    print(f"NORMAL SAMPLES: {normal_count}")
    print(f"STATISTICAL ANOMALIES: {anomaly_count}")
    print(f"FIT SECONDS: {fit_seconds:.6f}")
    print(f"INFERENCE SECONDS: {inference_seconds:.6f}")
    print(f"SCORES SAVED: {SCORES_FILE}")
    print(f"REPORT SAVED: {RESULTS_FILE}")
    print()
    print("V18.2 RESULT: CLASSICAL_BASELINE_PASS")
    print("=" * 68)

    if len(data) < 100:
        print(
            "WARNING: Small dataset. "
            "Results are preliminary."
        )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(run())
    except Exception as exc:
        print()
        print(
            "V18.2 FAILED: "
            f"{type(exc).__name__}: {exc}"
        )
        sys.exit(1)
