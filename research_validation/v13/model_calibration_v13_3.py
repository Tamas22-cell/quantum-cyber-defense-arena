
"""
QUANTUM CYBER DEFENSE ARENA
V13.3 - MODEL CALIBRATION & FUSION VALIDATION

Real dataset: Elliptic Bitcoin Dataset

Chronological evaluation:
  Time steps 1-24: normal-only model training
  Time steps 25-34: threshold calibration
  Time steps 35-49: exploratory final evaluation

IMPORTANT:
- Test data is never used to select thresholds.
- Historical test results have already been inspected,
  so this is NOT a pristine independent holdout.
- Original 165 Elliptic features remain unchanged.
- Quantum inputs are PCA features, not gas metrics.
- No quantum computational advantage is claimed.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.quantum_detection.quantum_detector import (
    QuantumAnomalyDetector,
)

from research_validation.v11.benchmark_v11 import (
    calculate_metrics,
)


VERSION = "13.3.0"
HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "elliptic_processed"

TRAIN_FILE = DATA_DIR / "train_labeled.parquet"
TEST_FILE = DATA_DIR / "test_labeled.parquet"
OUTPUT_FILE = HERE / "model_calibration_v13_3_results.json"

SEED = 2026

TRAIN_END_STEP = 24
CALIBRATION_END_STEP = 34

MAX_TRAIN = 10000
MAX_CALIBRATION = 400
MAX_TEST = 500

QUANTUM_COMPONENTS = 4

TARGET_FALSE_POSITIVE_RATE = 0.05

FEATURE_COLUMNS = [
    f"feature_{index:03d}"
    for index in range(1, 166)
]


def heading(message: str) -> None:
    print()
    print("=" * 68)
    print(message)
    print("=" * 68, flush=True)


def sample_frame(
    frame: pd.DataFrame,
    maximum: int,
    stratify: bool = False,
) -> pd.DataFrame:
    if len(frame) <= maximum:
        return frame.copy()

    if stratify and frame["label"].nunique() == 2:
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


def load_data():
    heading("STEP 1 - LOADING CHRONOLOGICAL DATA")

    for path in (TRAIN_FILE, TEST_FILE):
        if not path.is_file():
            raise FileNotFoundError(
                f"Missing data file: {path}"
            )

    historical_train = pd.read_parquet(TRAIN_FILE)
    historical_test = pd.read_parquet(TEST_FILE)

    required = set(FEATURE_COLUMNS) | {
        "label",
        "time_step",
    }

    for frame in (historical_train, historical_test):
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(
                f"Missing columns: {sorted(missing)}"
            )

    train = historical_train[
        (historical_train["time_step"] <= TRAIN_END_STEP)
        & (historical_train["label"] == 0)
    ].copy()

    calibration = historical_train[
        (historical_train["time_step"] > TRAIN_END_STEP)
        & (
            historical_train["time_step"]
            <= CALIBRATION_END_STEP
        )
    ].copy()

    test = historical_test[
        historical_test["time_step"] > CALIBRATION_END_STEP
    ].copy()

    train = sample_frame(train, MAX_TRAIN)
    calibration = sample_frame(
        calibration,
        MAX_CALIBRATION,
        stratify=True,
    )
    test = sample_frame(
        test,
        MAX_TEST,
        stratify=True,
    )

    if min(len(train), len(calibration), len(test)) == 0:
        raise ValueError("An evaluation split is empty.")

    if calibration["label"].nunique() != 2:
        raise ValueError(
            "Calibration data needs both known classes."
        )

    if test["label"].nunique() != 2:
        raise ValueError(
            "Test data needs both known classes."
        )

    if not (
        train["time_step"].max()
        < calibration["time_step"].min()
        <= calibration["time_step"].max()
        < test["time_step"].min()
    ):
        raise ValueError(
            "Chronological separation failed."
        )

    frames = {
        "train": train,
        "calibration": calibration,
        "test": test,
    }

    for name, frame in frames.items():
        values = frame[FEATURE_COLUMNS].to_numpy(
            dtype=np.float64
        )

        if not np.isfinite(values).all():
            raise ValueError(
                f"Non-finite features in {name}."
            )

        print(
            f"{name.upper():12s}: "
            f"{len(frame)} rows | "
            f"steps {int(frame['time_step'].min())}-"
            f"{int(frame['time_step'].max())} | "
            f"anomalies {int(frame['label'].sum())}"
        )

    return frames


def build_features(frames):
    heading("STEP 2 - TRAIN-ONLY FEATURE PREPROCESSING")

    train = frames["train"]

    scaler = StandardScaler()

    train_165 = scaler.fit_transform(
        train[FEATURE_COLUMNS].to_numpy(
            dtype=np.float64
        )
    )

    calibration_165 = scaler.transform(
        frames["calibration"][FEATURE_COLUMNS].to_numpy(
            dtype=np.float64
        )
    )

    test_165 = scaler.transform(
        frames["test"][FEATURE_COLUMNS].to_numpy(
            dtype=np.float64
        )
    )

    pca = PCA(
        n_components=QUANTUM_COMPONENTS,
        random_state=SEED,
    )

    train_pca = pca.fit_transform(train_165)
    calibration_pca = pca.transform(calibration_165)
    test_pca = pca.transform(test_165)

    lower = np.percentile(train_pca, 1, axis=0)
    upper = np.percentile(train_pca, 99, axis=0)

    denominator = np.maximum(
        upper - lower,
        1e-12,
    )

    def normalize_pca(values):
        return np.clip(
            (values - lower) / denominator,
            0.0,
            1.0,
        )

    print("StandardScaler: fitted on training data")
    print("PCA: fitted on training data")
    print("Quantum features:", QUANTUM_COMPONENTS)

    return {
        "classical_train": train_165,
        "classical_calibration": calibration_165,
        "classical_test": test_165,
        "quantum_calibration": normalize_pca(
            calibration_pca
        ),
        "quantum_test": normalize_pca(test_pca),
        "pca_explained_variance_ratio": [
            round(float(value), 6)
            for value in pca.explained_variance_ratio_
        ],
    }


def classical_scores(features):
    heading("STEP 3 - CLASSICAL AI")

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=SEED,
        n_jobs=-1,
    )

    model.fit(features["classical_train"])

    # Smaller score_samples = stronger anomaly evidence.
    calibration_raw = model.score_samples(
        features["classical_calibration"]
    )

    test_raw = model.score_samples(
        features["classical_test"]
    )

    # Convert to higher-is-more-anomalous scores.
    calibration_scores = -calibration_raw
    test_scores = -test_raw

    print("Classical Isolation Forest trained.")
    print("Training feature dimensions: 165")

    return calibration_scores, test_scores


def quantum_scores(features):
    heading("STEP 4 - QUANTUM AI SIMULATOR")

    detector = QuantumAnomalyDetector(
        threshold=0.35
    )

    def evaluate(data, description):
        scores = []

        for index, row in enumerate(data, start=1):
            result = detector.detect(
                [float(value) for value in row]
            )

            score = float(result.anomaly_score)

            if not np.isfinite(score):
                raise ValueError(
                    "Non-finite quantum anomaly score."
                )

            scores.append(score)

            if index % 100 == 0:
                print(
                    f"{description}: {index}/{len(data)}",
                    flush=True,
                )

        return np.asarray(scores, dtype=float)

    calibration_scores = evaluate(
        features["quantum_calibration"],
        "Quantum calibration",
    )

    test_scores = evaluate(
        features["quantum_test"],
        "Quantum test",
    )

    return calibration_scores, test_scores


def calibrate_threshold(
    scores: np.ndarray,
    labels: np.ndarray,
    model_name: str,
) -> float:
    """
    Calibrate using NORMAL observations only.

    This avoids choosing a threshold to optimize
    the final test set's F1-score.
    """

    normal_scores = scores[labels == 0]

    if len(normal_scores) < 30:
        raise ValueError(
            "At least 30 normal calibration records "
            "are required."
        )

    threshold = float(
        np.quantile(
            normal_scores,
            1.0 - TARGET_FALSE_POSITIVE_RATE,
        )
    )

    print(
        f"{model_name} threshold: {threshold:.6f}"
    )

    return threshold


def compute_false_positive_rate(metrics: dict) -> float:
    denominator = metrics["fp"] + metrics["tn"]

    if denominator == 0:
        return 0.0

    return metrics["fp"] / denominator


def evaluate_policy(
    classical_prediction: np.ndarray,
    quantum_prediction: np.ndarray,
    labels: np.ndarray,
):
    """
    Three predeclared policies:

    CLASSICAL: calibrated classical score
    QUANTUM: calibrated quantum score

    HYBRID_AND: both detectors must flag an anomaly.
    HYBRID_OR: at least one detector flags an anomaly.

    The agreement-based REVIEW workflow is
    separately evaluated for comparison.
    """

    and_prediction = (
        classical_prediction & quantum_prediction
    ).astype(int)

    or_prediction = (
        classical_prediction | quantum_prediction
    ).astype(int)

    disagreement = (
        classical_prediction != quantum_prediction
    )

    predictions = {
        "classical": classical_prediction,
        "quantum": quantum_prediction,
        "hybrid_and": and_prediction,
        "hybrid_or": or_prediction,
    }

    metrics = {
        name: calculate_metrics(labels, prediction)
        for name, prediction in predictions.items()
    }

    for name, result in metrics.items():
        result["false_positive_rate"] = round(
            compute_false_positive_rate(result),
            6,
        )

    # An AND prediction is equivalent to the old
    # REVIEW-as-negative binary scoring policy.
    review_metrics = calculate_metrics(
        labels,
        and_prediction,
    )

    return {
        "metrics": metrics,
        "review_policy": {
            "review_count": int(np.sum(disagreement)),
            "review_rate": round(
                float(np.mean(disagreement)),
                6,
            ),
            "binary_metrics_if_review_is_negative": (
                review_metrics
            ),
        },
    }


def display_results(results):
    heading("V13.3 CALIBRATED MODEL RESULTS")

    for name, metrics in results["metrics"].items():
        print()
        print(name.upper())
        print("-" * 42)
        print(f"F1:        {metrics['f1'] * 100:.2f}%")
        print(
            f"PRECISION: {metrics['precision'] * 100:.2f}%"
        )
        print(
            f"RECALL:    {metrics['recall'] * 100:.2f}%"
        )
        print(
            f"FPR:       "
            f"{metrics['false_positive_rate'] * 100:.2f}%"
        )
        print(
            f"TP={metrics['tp']} "
            f"TN={metrics['tn']} "
            f"FP={metrics['fp']} "
            f"FN={metrics['fn']}"
        )

    print()
    print(
        "HYBRID REVIEW RATE:",
        f"{results['review_policy']['review_rate'] * 100:.2f}%",
    )


def main():
    heading(
        "QUANTUM CYBER DEFENSE ARENA "
        "V13.3 MODEL CALIBRATION"
    )

    started = perf_counter()

    frames = load_data()
    features = build_features(frames)

    classical_cal, classical_test = classical_scores(
        features
    )

    quantum_cal, quantum_test = quantum_scores(
        features
    )

    calibration_labels = (
        frames["calibration"]["label"].to_numpy(
            dtype=int
        )
    )

    test_labels = (
        frames["test"]["label"].to_numpy(
            dtype=int
        )
    )

    heading("STEP 5 - CALIBRATING THRESHOLDS")

    classical_threshold = calibrate_threshold(
        classical_cal,
        calibration_labels,
        "Classical",
    )

    quantum_threshold = calibrate_threshold(
        quantum_cal,
        calibration_labels,
        "Quantum",
    )

    classical_prediction = (
        classical_test > classical_threshold
    ).astype(int)

    quantum_prediction = (
        quantum_test > quantum_threshold
    ).astype(int)

    heading("STEP 6 - EVALUATING FIXED POLICIES")

    results = evaluate_policy(
        classical_prediction,
        quantum_prediction,
        test_labels,
    )

    display_results(results)

    elapsed = perf_counter() - started

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "mode": "EXPLORATORY_REAL_DATA_CALIBRATION",
        "dataset": "Elliptic Bitcoin Dataset",
        "configuration": {
            "train_end_step": TRAIN_END_STEP,
            "calibration_end_step": CALIBRATION_END_STEP,
            "test_start_step": CALIBRATION_END_STEP + 1,
            "training_normal_samples": len(
                frames["train"]
            ),
            "calibration_samples": len(
                frames["calibration"]
            ),
            "test_samples": len(
                frames["test"]
            ),
            "test_anomalies": int(
                np.sum(test_labels)
            ),
            "original_feature_count": 165,
            "pca_components": QUANTUM_COMPONENTS,
            "target_calibration_fpr": (
                TARGET_FALSE_POSITIVE_RATE
            ),
            "seed": SEED,
        },
        "calibrated_thresholds": {
            "classical": classical_threshold,
            "quantum": quantum_threshold,
        },
        "pca_explained_variance_ratio": features[
            "pca_explained_variance_ratio"
        ],
        "results": results,
        "execution_seconds": round(elapsed, 3),
        "limitations": [
            "Previously inspected chronological test period",
            "Results are exploratory, not unbiased validation",
            "Only one dataset and one time split",
            "Calibration thresholds use normal records only",
            "Finite calibration sample limits FPR precision",
            "Classical model has 165 features",
            "Quantum simulator uses four PCA features",
            "Hybrid AND and OR are simple predefined rules",
            "No independent quantum hardware experiment",
            "No demonstrated quantum computational advantage",
            "No operational cybersecurity certification",
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

    heading("V13.3 MODEL CALIBRATION COMPLETED")

    print()
    print("RESULTS SAVED TO:")
    print(OUTPUT_FILE)

    print()
    print(
        "Important: do not interpret these results "
        "as independent confirmation, because the "
        "historical test period was previously inspected."
    )


if __name__ == "__main__":
    main()
