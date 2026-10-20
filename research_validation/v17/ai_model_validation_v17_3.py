
"""
QUANTUM CYBER DEFENSE ARENA
V17.3 - AI MODEL EVALUATION & VALIDATION

Validation:
1. Input and output files
2. Model structure
3. Feature consistency
4. Saved anomaly scores
5. Model predictions
6. Deterministic retraining
7. Research limitations

Requires:
numpy, scikit-learn, joblib

IMPORTANT:
Only load trusted local joblib model files.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import joblib
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:
    print("DEPENDENCY ERROR:", exc)
    print("Install: python -m pip install numpy scikit-learn joblib")
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[2]
V17 = ROOT / "research_validation" / "v17"

FEATURES_FILE = V17 / "training_features_v17_1.csv"
MODEL_FILE = V17 / "isolation_forest_model_v17_2.joblib"
SCORES_FILE = V17 / "anomaly_scores_v17_2.csv"
TRAIN_REPORT = V17 / "ai_model_training_v17_2_results.json"

OUTPUT_FILE = V17 / "ai_model_validation_v17_3_results.json"

CHECKS = []
TOLERANCE = 1e-6


def check(name, condition, details=""):
    passed = bool(condition)

    CHECKS.append({
        "name": name,
        "passed": passed,
        "details": str(details),
    })

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")

    if details and not passed:
        print(f"       {details}")

    return passed


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
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
        raise ValueError(f"Missing CSV header: {path.name}")

    if len(fields) != len(set(fields)):
        raise ValueError(f"Duplicate CSV columns: {path.name}")

    return fields, rows


def load_features():
    columns, rows = read_csv(FEATURES_FILE)

    if not rows:
        raise ValueError("Training features CSV is empty.")

    values = []

    for row_number, row in enumerate(rows, start=2):
        result = []

        for column in columns:
            raw = row.get(column)

            if raw is None or not str(raw).strip():
                result.append(float("nan"))
                continue

            try:
                value = float(raw)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid number at row {row_number}, "
                    f"column {column}"
                ) from exc

            if math.isinf(value):
                raise ValueError(
                    f"Infinite value in column {column}"
                )

            result.append(value)

        values.append(result)

    data = np.asarray(values, dtype=np.float64)

    if np.any(np.all(np.isnan(data), axis=0)):
        raise ValueError("A feature contains only missing values.")

    return columns, data


def load_scores():
    columns, rows = read_csv(SCORES_FILE)

    required = {
        "sample_index",
        "anomaly_score",
        "decision_function",
        "is_anomaly",
    }

    if not required.issubset(set(columns)):
        raise ValueError("Saved scores CSV has missing columns.")

    indexes = []
    scores = []
    decisions = []
    flags = []

    for row in rows:
        indexes.append(int(row["sample_index"]))
        scores.append(float(row["anomaly_score"]))
        decisions.append(float(row["decision_function"]))

        flag = int(row["is_anomaly"])

        if flag not in (0, 1):
            raise ValueError("Anomaly flag must be 0 or 1.")

        flags.append(flag)

    score_array = np.asarray(scores, dtype=float)
    decision_array = np.asarray(decisions, dtype=float)

    if not np.all(np.isfinite(score_array)):
        raise ValueError("Saved anomaly scores are not finite.")

    if not np.all(np.isfinite(decision_array)):
        raise ValueError("Saved decision values are not finite.")

    return indexes, score_array, decision_array, np.asarray(flags)


def build_reference_model(parameters):
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "detector",
                IsolationForest(
                    n_estimators=int(parameters["n_estimators"]),
                    contamination=parameters["contamination"],
                    random_state=int(parameters["random_state"]),
                    n_jobs=-1,
                ),
            ),
        ]
    )


def close_enough(actual, expected):
    return bool(
        np.allclose(
            actual,
            expected,
            rtol=TOLERANCE,
            atol=TOLERANCE,
        )
    )


def main():
    print("=" * 66)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V17.3 - AI MODEL EVALUATION & VALIDATION")
    print("=" * 66)

    V17.mkdir(parents=True, exist_ok=True)

    required_files = [
        FEATURES_FILE,
        MODEL_FILE,
        SCORES_FILE,
        TRAIN_REPORT,
    ]

    files_available = all(
        path.is_file() for path in required_files
    )

    for path in required_files:
        check(
            f"File available: {path.name}",
            path.is_file(),
        )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V17.3",
        "module": "AI Model Evaluation & Validation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_type": "Isolation Forest",
        "validation_scope": (
            "Saved-artifact consistency and deterministic "
            "retraining on the same data"
        ),
        "verified_threat_labels": False,
        "out_of_sample_test": False,
    }

    if files_available:
        try:
            columns, data = load_features()
            indexes, saved_scores, saved_decisions, saved_flags = (
                load_scores()
            )
            train_report = load_json(TRAIN_REPORT)

            # joblib can execute code during loading.
            # Load only the model generated by this trusted project.
            model_package = joblib.load(MODEL_FILE)

            model = model_package["pipeline"]
            model_features = model_package["feature_names"]

            check(
                "Model is a scikit-learn Pipeline",
                isinstance(model, Pipeline),
            )

            check(
                "Correct model steps",
                list(model.named_steps.keys())
                == ["imputer", "scaler", "detector"],
            )

            check(
                "Detector is Isolation Forest",
                isinstance(
                    model.named_steps["detector"],
                    IsolationForest,
                ),
            )

            check(
                "Training data has at least 10 samples",
                len(data) >= 10,
                f"Samples: {len(data)}",
            )

            check(
                "Training features match saved model",
                list(columns) == list(model_features),
            )

            check(
                "Training features match V17.2 report",
                list(columns)
                == train_report.get("feature_names"),
            )

            check(
                "Training sample count matches report",
                len(data) == train_report.get("samples"),
            )

            check(
                "Saved scores count matches samples",
                len(saved_scores) == len(data),
            )

            check(
                "Saved sample indexes are sequential",
                indexes == list(range(1, len(indexes) + 1)),
            )

            predictions = model.predict(data)
            actual_scores = -model.score_samples(data)
            actual_decisions = model.decision_function(data)
            actual_flags = (predictions == -1).astype(int)

            check(
                "Saved anomaly scores are consistent",
                close_enough(actual_scores, saved_scores),
            )

            check(
                "Saved decision values are consistent",
                close_enough(actual_decisions, saved_decisions),
            )

            check(
                "Saved anomaly flags are consistent",
                np.array_equal(actual_flags, saved_flags),
            )

            anomaly_count = int(np.sum(actual_flags))
            normal_count = len(data) - anomaly_count

            reported = train_report.get(
                "training_set_results", {}
            )

            check(
                "Anomaly count matches report",
                anomaly_count == reported.get("anomalies"),
            )

            check(
                "Normal count matches report",
                normal_count == reported.get("normal"),
            )

            check(
                "Anomaly percentage matches report",
                math.isclose(
                    round(100 * anomaly_count / len(data), 2),
                    float(reported.get("anomaly_percentage", -1)),
                    abs_tol=0.01,
                ),
            )

            parameters = train_report.get("parameters", {})

            reference = build_reference_model(parameters)
            reference.fit(data)

            reference_scores = -reference.score_samples(data)
            reference_flags = (
                reference.predict(data) == -1
            ).astype(int)

            check(
                "Deterministic retraining: anomaly scores",
                close_enough(
                    reference_scores,
                    actual_scores,
                ),
            )

            check(
                "Deterministic retraining: predictions",
                np.array_equal(
                    reference_flags,
                    actual_flags,
                ),
            )

            report["data_summary"] = {
                "samples": int(len(data)),
                "features": int(len(columns)),
                "feature_names": list(columns),
                "normal_count": normal_count,
                "statistical_anomalies": anomaly_count,
                "anomaly_percentage": round(
                    100 * anomaly_count / len(data),
                    2,
                ),
            }

        except Exception as exc:
            check(
                "Model evaluation completed",
                False,
                f"{type(exc).__name__}: {exc}",
            )

            report["error"] = (
                f"{type(exc).__name__}: {exc}"
            )

    passed = sum(item["passed"] for item in CHECKS)
    failed = len(CHECKS) - passed

    report["checks"] = CHECKS
    report["checks_passed"] = passed
    report["checks_failed"] = failed

    report["limitations"] = [
        "No verified malicious transaction labels.",
        "No precision, recall, F1 or accuracy evaluation.",
        "No independent test dataset was used.",
        "Validation uses the same training samples.",
        "Small samples cannot establish operational reliability.",
        "Anomaly flags are not confirmed cyberattacks.",
    ]

    report["status"] = (
        "VALIDATION_PASS"
        if failed == 0
        else "VALIDATION_FAIL"
    )

    with OUTPUT_FILE.open(
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
    print("=" * 66)
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"V17.3 RESULT: {report['status']}")
    print(f"REPORT SAVED: {OUTPUT_FILE}")
    print("=" * 66)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(
            f"V17.3 FATAL ERROR: "
            f"{type(exc).__name__}: {exc}"
        )
        sys.exit(1)
