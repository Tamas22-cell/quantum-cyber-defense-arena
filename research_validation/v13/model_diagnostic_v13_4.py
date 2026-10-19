

"""
QUANTUM CYBER DEFENSE ARENA
V13.4 - MODEL DIAGNOSTIC & BASELINE VALIDATION

Dataset:
    Real Elliptic Bitcoin Dataset

Purpose:
    Determine whether the original 165 features
    support discrimination of licit and illicit
    Bitcoin transactions.

Models:
    1. Dummy majority-class baseline
    2. Logistic Regression
    3. Random Forest

Chronological separation:
    Time steps 1-24: model training
    Time steps 25-34: model selection and calibration
    Time steps 35-49: exploratory evaluation

IMPORTANT:
    - No synthetic observations are generated.
    - All original 165 features are preserved.
    - Unknown labels are excluded.
    - No test labels are used during model fitting.
    - Final test period has already been inspected
      in earlier V13 experiments.
    - Results are exploratory, not independently
      confirmed out-of-sample performance.
    - No quantum advantage is claimed.
"""

from __future__ import annotations

import json
import math
import sys
import warnings

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


VERSION = "13.4.0"

HERE = Path(__file__).resolve().parent

DATA_DIRECTORY = HERE / "elliptic_processed"

TRAIN_FILE = DATA_DIRECTORY / "train_labeled.parquet"
TEST_FILE = DATA_DIRECTORY / "test_labeled.parquet"

OUTPUT_FILE = HERE / "model_diagnostic_v13_4_results.json"

SEED = 2026

TRAIN_END_STEP = 24
CALIBRATION_END_STEP = 34

MAX_TRAIN = 20000
MAX_CALIBRATION = 2000
MAX_TEST = 2000

FEATURE_COLUMNS = [
    f"feature_{index:03d}"
    for index in range(1, 166)
]

THRESHOLDS = np.linspace(
    0.05,
    0.95,
    91,
)

MODEL_NAMES = (
    "dummy",
    "logistic_regression",
    "random_forest",
)


def heading(message: str) -> None:
    print()
    print("=" * 72)
    print(message)
    print("=" * 72, flush=True)


def validate_frame(
    frame: pd.DataFrame,
    name: str,
) -> None:
    required = set(FEATURE_COLUMNS) | {
        "label",
        "time_step",
        "txId",
    }

    missing = required - set(frame.columns)

    if missing:
        raise ValueError(
            f"{name}: missing columns {sorted(missing)}"
        )

    if not frame["label"].isin([0, 1]).all():
        raise ValueError(
            f"{name}: invalid labels found."
        )

    if frame["txId"].isna().any():
        raise ValueError(
            f"{name}: missing transaction IDs."
        )

    if frame["txId"].duplicated().any():
        raise ValueError(
            f"{name}: duplicate transaction IDs."
        )

    values = frame[FEATURE_COLUMNS].to_numpy(
        dtype=np.float64
    )

    if not np.isfinite(values).all():
        raise ValueError(
            f"{name}: non-finite feature values."
        )


def sample_frame(
    frame: pd.DataFrame,
    maximum: int,
) -> pd.DataFrame:
    """
    Deterministic stratified subsampling.

    Sampling is performed separately inside
    each chronological partition.
    """

    if len(frame) <= maximum:
        return frame.copy()

    from sklearn.model_selection import train_test_split

    if frame["label"].nunique() == 2:
        selected, _ = train_test_split(
            frame,
            train_size=maximum,
            random_state=SEED,
            stratify=frame["label"],
        )

        return selected.copy()

    return frame.sample(
        n=maximum,
        random_state=SEED,
    ).copy()


def load_data() -> dict:
    heading("STEP 1 - LOADING ELLIPTIC DATA")

    for filename in (TRAIN_FILE, TEST_FILE):
        if not filename.is_file():
            raise FileNotFoundError(
                f"Missing prepared dataset: {filename}"
            )

    historical_train = pd.read_parquet(
        TRAIN_FILE
    )

    historical_test = pd.read_parquet(
        TEST_FILE
    )

    validate_frame(
        historical_train,
        "Historical training dataset",
    )

    validate_frame(
        historical_test,
        "Historical test dataset",
    )

    train = historical_train[
        historical_train["time_step"]
        <= TRAIN_END_STEP
    ].copy()

    calibration = historical_train[
        (
            historical_train["time_step"]
            > TRAIN_END_STEP
        )
        & (
            historical_train["time_step"]
            <= CALIBRATION_END_STEP
        )
    ].copy()

    test = historical_test[
        historical_test["time_step"]
        > CALIBRATION_END_STEP
    ].copy()

    train = sample_frame(
        train,
        MAX_TRAIN,
    )

    calibration = sample_frame(
        calibration,
        MAX_CALIBRATION,
    )

    test = sample_frame(
        test,
        MAX_TEST,
    )

    for name, frame in (
        ("TRAIN", train),
        ("CALIBRATION", calibration),
        ("TEST", test),
    ):
        if frame.empty:
            raise ValueError(
                f"{name} partition is empty."
            )

        if frame["label"].nunique() != 2:
            raise ValueError(
                f"{name} requires both labeled classes."
            )

        print(
            f"{name:12s}: "
            f"{len(frame):5d} records | "
            f"normal={int((frame['label'] == 0).sum())} | "
            f"illicit={int((frame['label'] == 1).sum())} | "
            f"steps={int(frame['time_step'].min())}-"
            f"{int(frame['time_step'].max())}"
        )

    if not (
        train["time_step"].max()
        < calibration["time_step"].min()
        <= calibration["time_step"].max()
        < test["time_step"].min()
    ):
        raise ValueError(
            "Chronological train/calibration/test "
            "separation failed."
        )

    all_ids = [
        set(frame["txId"].astype(str))
        for frame in (train, calibration, test)
    ]

    if (
        all_ids[0] & all_ids[1]
        or all_ids[0] & all_ids[2]
        or all_ids[1] & all_ids[2]
    ):
        raise ValueError(
            "Transaction ID leakage across partitions."
        )

    return {
        "train": train,
        "calibration": calibration,
        "test": test,
    }


def extract_features(
    frame: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    X = frame[FEATURE_COLUMNS].to_numpy(
        dtype=np.float64
    )

    y = frame["label"].to_numpy(
        dtype=np.int64
    )

    return X, y


def build_models() -> dict:
    """
    Supervised reference baselines.

    These models are NOT the original V11
    unsupervised anomaly detectors.
    """

    return {
        "dummy": DummyClassifier(
            strategy="prior"
        ),
        "logistic_regression": Pipeline([
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=SEED,
                    solver="lbfgs",
                ),
            ),
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=16,
            min_samples_leaf=3,
            class_weight="balanced_subsample",
            random_state=SEED,
            n_jobs=-1,
        ),
    }


def evaluate_predictions(
    y_true: np.ndarray,
    predictions: np.ndarray,
    probabilities: np.ndarray,
) -> dict:
    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    f1 = f1_score(
        y_true,
        predictions,
        zero_division=0,
    )

    precision = precision_score(
        y_true,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        predictions,
        zero_division=0,
    )

    balanced_accuracy = balanced_accuracy_score(
        y_true,
        predictions,
    )

    average_precision = average_precision_score(
        y_true,
        probabilities,
    )

    roc_auc = roc_auc_score(
        y_true,
        probabilities,
    )

    fpr = (
        fp / (fp + tn)
        if fp + tn
        else 0.0
    )

    return {
        "precision": round(
            float(precision),
            6,
        ),
        "recall": round(
            float(recall),
            6,
        ),
        "f1": round(
            float(f1),
            6,
        ),
        "balanced_accuracy": round(
            float(balanced_accuracy),
            6,
        ),
        "average_precision": round(
            float(average_precision),
            6,
        ),
        "roc_auc": round(
            float(roc_auc),
            6,
        ),
        "false_positive_rate": round(
            float(fpr),
            6,
        ),
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
    }


def choose_threshold(
    probabilities: np.ndarray,
    labels: np.ndarray,
) -> tuple[float, float]:
    """
    Choose threshold on the CALIBRATION set only.

    Search criterion: maximum F1-score.

    The resulting test-set score is exploratory
    because the same historical test period
    was previously inspected in V13.
    """

    best_threshold = 0.5
    best_f1 = -1.0

    for threshold in THRESHOLDS:
        predictions = (
            probabilities >= threshold
        ).astype(int)

        score = f1_score(
            labels,
            predictions,
            zero_division=0,
        )

        if score > best_f1 + 1e-12:
            best_f1 = float(score)
            best_threshold = float(threshold)

    return (
        best_threshold,
        best_f1,
    )


def print_metrics(
    name: str,
    metrics: dict,
) -> None:
    print()
    print(name.upper())
    print("-" * 50)

    print(
        f"F1 SCORE:          "
        f"{metrics['f1'] * 100:.2f}%"
    )

    print(
        f"PRECISION:         "
        f"{metrics['precision'] * 100:.2f}%"
    )

    print(
        f"RECALL:            "
        f"{metrics['recall'] * 100:.2f}%"
    )

    print(
        f"BALANCED ACCURACY: "
        f"{metrics['balanced_accuracy'] * 100:.2f}%"
    )

    print(
        f"AVERAGE PRECISION: "
        f"{metrics['average_precision'] * 100:.2f}%"
    )

    print(
        f"ROC AUC:           "
        f"{metrics['roc_auc']:.4f}"
    )

    print(
        f"FALSE POSITIVE RATE: "
        f"{metrics['false_positive_rate'] * 100:.2f}%"
    )

    print(
        f"TP={metrics['tp']} "
        f"TN={metrics['tn']} "
        f"FP={metrics['fp']} "
        f"FN={metrics['fn']}"
    )


def main() -> None:
    heading(
        "QUANTUM CYBER DEFENSE ARENA "
        "V13.4 - MODEL DIAGNOSTIC"
    )

    started = perf_counter()

    frames = load_data()

    X_train, y_train = extract_features(
        frames["train"]
    )

    X_calibration, y_calibration = (
        extract_features(
            frames["calibration"]
        )
    )

    X_test, y_test = extract_features(
        frames["test"]
    )

    models = build_models()

    report_results = {}

    heading("STEP 2 - TRAINING BASELINE MODELS")

    for name, model in models.items():
        print()
        print(
            f"TRAINING: {name.upper()}",
            flush=True,
        )

        train_started = perf_counter()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            model.fit(
                X_train,
                y_train,
            )

        training_seconds = (
            perf_counter() - train_started
        )

        calibration_probabilities = (
            model.predict_proba(
                X_calibration
            )[:, 1]
        )

        threshold, calibration_f1 = (
            choose_threshold(
                calibration_probabilities,
                y_calibration,
            )
        )

        test_probabilities = (
            model.predict_proba(
                X_test
            )[:, 1]
        )

        test_predictions = (
            test_probabilities >= threshold
        ).astype(int)

        metrics = evaluate_predictions(
            y_test,
            test_predictions,
            test_probabilities,
        )

        print(
            "Calibration threshold:",
            round(threshold, 4),
        )

        print(
            "Calibration F1:",
            f"{calibration_f1 * 100:.2f}%",
        )

        print_metrics(
            name,
            metrics,
        )

        report_results[name] = {
            "training_seconds": round(
                training_seconds,
                3,
            ),
            "selected_threshold": round(
                threshold,
                6,
            ),
            "calibration_f1": round(
                calibration_f1,
                6,
            ),
            "test_metrics": metrics,
        }

    heading("STEP 3 - RESEARCH SUMMARY")

    ranking = sorted(
        report_results.items(),
        key=lambda item: (
            item[1]["test_metrics"]["f1"]
        ),
        reverse=True,
    )

    for position, (name, result) in enumerate(
        ranking,
        start=1,
    ):
        metrics = result["test_metrics"]

        print(
            f"{position}. {name.upper():22s}"
            f" F1={metrics['f1'] * 100:.2f}%"
            f" AP={metrics['average_precision'] * 100:.2f}%"
        )

    elapsed = perf_counter() - started

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "mode": "EXPLORATORY_REAL_DATA_DIAGNOSTIC",
        "dataset": {
            "name": "Elliptic Bitcoin Dataset",
            "source": (
                "edisonlin2002/elliptic-bitcoin-dataset"
            ),
            "original_feature_count": 165,
            "training_records": len(y_train),
            "calibration_records": len(
                y_calibration
            ),
            "test_records": len(y_test),
            "training_anomalies": int(
                np.sum(y_train)
            ),
            "calibration_anomalies": int(
                np.sum(y_calibration)
            ),
            "test_anomalies": int(
                np.sum(y_test)
            ),
            "training_steps": "1-24",
            "calibration_steps": "25-34",
            "test_steps": "35-49",
        },
        "models": report_results,
        "ranking": [
            {
                "name": name,
                "f1": result["test_metrics"]["f1"],
                "average_precision": (
                    result["test_metrics"][
                        "average_precision"
                    ]
                ),
            }
            for name, result in ranking
        ],
        "threshold_selection": {
            "method": (
                "Maximum calibration-set F1"
            ),
            "grid": {
                "minimum": 0.05,
                "maximum": 0.95,
                "steps": len(THRESHOLDS),
            },
            "test_labels_used_for_selection": False,
        },
        "execution_seconds": round(
            elapsed,
            3,
        ),
        "limitations": [
            "Previously inspected test period",
            "Exploratory evaluation only",
            "No untouched independent external test",
            "Original Bitcoin features are anonymized",
            "Supervised baselines differ from "
            "unsupervised anomaly detectors",
            "Class-imbalance impacts F1",
            "Calibration F1 threshold may overfit",
            "Single chronological split",
            "Unknown transaction labels excluded",
            "Graph dependencies are not fully controlled",
            "No quantum hardware advantage demonstrated",
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

    heading(
        "V13.4 MODEL DIAGNOSTIC COMPLETED"
    )

    print()
    print("TOTAL EXECUTION TIME:")
    print(round(elapsed, 2), "seconds")

    print()
    print("RESULTS SAVED TO:")
    print(OUTPUT_FILE)

    print()
    print(
        "IMPORTANT: The V13.4 results are "
        "exploratory and do not replace "
        "the original V13.2 or V13.3 results."
    )


if __name__ == "__main__":
    try:
        main()
    except (
        FileNotFoundError,
        ValueError,
        KeyError,
    ) as error:
        print()
        print("V13.4 VALIDATION ERROR:")
        print(error)
        sys.exit(1)
