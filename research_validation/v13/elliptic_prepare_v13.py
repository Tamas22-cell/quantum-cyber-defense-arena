
"""
QUANTUM CYBER DEFENSE ARENA
V13.1 - ELLIPTIC REAL DATA PREPARATION

Prepares the real Elliptic Bitcoin transaction dataset.

Input files:
    elliptic_raw/elliptic_txs_classes.csv
    elliptic_raw/elliptic_txs_features.csv

Output files:
    elliptic_processed/train_normal.parquet
    elliptic_processed/train_labeled.parquet
    elliptic_processed/test_labeled.parquet
    elliptic_processed/dataset_report.json

Principles:
- Preserve original 165 numeric features.
- Do not invent Ethereum-specific features.
- Exclude transactions with unknown labels.
- Prevent transaction ID from becoming a model feature.
- Use chronological split by Elliptic time step.
- Preserve class imbalance.
- Do not fit preprocessing on the test set.

Labels:
    Original 1 = illicit -> anomaly 1
    Original 2 = licit   -> normal 0

Research data preparation only.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


VERSION = "13.1.0"

HERE = Path(__file__).resolve().parent

RAW_DIRECTORY = HERE / "elliptic_raw"
OUTPUT_DIRECTORY = HERE / "elliptic_processed"

CLASSES_FILE = RAW_DIRECTORY / "elliptic_txs_classes.csv"
FEATURES_FILE = RAW_DIRECTORY / "elliptic_txs_features.csv"

TRAIN_END_TIME_STEP = 34

EXPECTED_COLUMNS = 167
EXPECTED_FEATURES = 165

FEATURE_COLUMNS = [
    f"feature_{index:03d}"
    for index in range(1, EXPECTED_FEATURES + 1)
]

ALL_COLUMNS = [
    "txId",
    "time_step",
    *FEATURE_COLUMNS,
]


def print_header() -> None:
    print()
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA V13.1")
    print("ELLIPTIC REAL BLOCKCHAIN DATA PREPARATION")
    print("=" * 70)
    print()


def validate_files() -> None:
    for file in (CLASSES_FILE, FEATURES_FILE):
        if not file.is_file():
            raise FileNotFoundError(
                f"Missing input file: {file}"
            )

    print("Both original Elliptic CSV files found.")


def load_classes() -> pd.DataFrame:
    print()
    print("STEP 1: LOADING TRANSACTION LABELS")

    classes = pd.read_csv(
        CLASSES_FILE,
        dtype={
            "txId": "string",
            "class": "string",
        },
    )

    required = {"txId", "class"}

    if not required.issubset(classes.columns):
        raise ValueError(
            "Invalid class CSV columns."
        )

    classes = classes[["txId", "class"]].copy()

    if classes["txId"].isna().any():
        raise ValueError(
            "Missing transaction IDs in label file."
        )

    if classes["txId"].duplicated().any():
        raise ValueError(
            "Duplicate transaction IDs in label file."
        )

    print("Total label rows:", len(classes))
    print()
    print("Original label distribution:")
    print(classes["class"].value_counts(dropna=False))

    return classes


def load_features() -> pd.DataFrame:
    print()
    print("STEP 2: LOADING ORIGINAL TRANSACTION FEATURES")

    features = pd.read_csv(
        FEATURES_FILE,
        header=None,
        dtype={0: "string"},
        low_memory=False,
    )

    if features.shape[1] != EXPECTED_COLUMNS:
        raise ValueError(
            f"Expected {EXPECTED_COLUMNS} columns, "
            f"found {features.shape[1]}."
        )

    features.columns = ALL_COLUMNS

    if features["txId"].isna().any():
        raise ValueError(
            "Missing transaction ID in features."
        )

    if features["txId"].duplicated().any():
        raise ValueError(
            "Duplicate transaction IDs in features."
        )

    features["time_step"] = pd.to_numeric(
        features["time_step"],
        errors="raise",
    )

    if features["time_step"].isna().any():
        raise ValueError(
            "Missing time steps."
        )

    print("Transactions:", len(features))
    print("Numeric feature columns:", len(FEATURE_COLUMNS))
    print(
        "Time-step range:",
        features["time_step"].min(),
        "to",
        features["time_step"].max(),
    )

    return features


def join_and_label(
    features: pd.DataFrame,
    classes: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    print()
    print("STEP 3: JOINING TRANSACTIONS WITH LABELS")

    merged = features.merge(
        classes,
        on="txId",
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    if (merged["_merge"] != "both").any():
        raise ValueError(
            "Some feature transactions have no matching "
            "label-file entry."
        )

    original_count = len(merged)

    unknown_count = int(
        (merged["class"] == "unknown").sum()
    )

    invalid = ~merged["class"].isin(
        ["1", "2", "unknown"]
    )

    if invalid.any():
        raise ValueError(
            "Unexpected original class labels: "
            + str(
                merged.loc[
                    invalid,
                    "class",
                ].unique().tolist()
            )
        )

    labeled = merged[
        merged["class"].isin(["1", "2"])
    ].copy()

    labeled["label"] = (
        labeled["class"]
        .map({
            "1": 1,
            "2": 0,
        })
        .astype("int8")
    )

    labeled.drop(
        columns=["class", "_merge"],
        inplace=True,
    )

    report = {
        "original_transactions": original_count,
        "unknown_removed": unknown_count,
        "labeled_transactions": len(labeled),
        "normal_transactions": int(
            (labeled["label"] == 0).sum()
        ),
        "anomaly_transactions": int(
            (labeled["label"] == 1).sum()
        ),
    }

    print("Original transactions:", original_count)
    print("Unknown labels removed:", unknown_count)
    print("Labeled transactions:", len(labeled))
    print("Normal transactions:", report["normal_transactions"])
    print("Anomaly transactions:", report["anomaly_transactions"])

    return labeled, report


def validate_numeric_data(
    data: pd.DataFrame,
) -> None:
    print()
    print("STEP 4: VALIDATING NUMERIC FEATURES")

    data.loc[:, FEATURE_COLUMNS] = data[
        FEATURE_COLUMNS
    ].apply(
        pd.to_numeric,
        errors="raise",
    )

    values = data[FEATURE_COLUMNS].to_numpy(
        dtype=np.float64
    )

    if not np.isfinite(values).all():
        raise ValueError(
            "Non-finite feature values detected."
        )

    if not data["time_step"].between(1, 49).all():
        raise ValueError(
            "Unexpected Elliptic time-step values."
        )

    print("Numeric validation: PASS")
    print("Feature count:", len(FEATURE_COLUMNS))
    print("Missing/non-finite feature values: 0")


def split_by_time(
    data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    print()
    print("STEP 5: CHRONOLOGICAL TRAIN / TEST SPLIT")

    train = data[
        data["time_step"] <= TRAIN_END_TIME_STEP
    ].copy()

    test = data[
        data["time_step"] > TRAIN_END_TIME_STEP
    ].copy()

    if train.empty or test.empty:
        raise ValueError(
            "Chronological split produced an empty dataset."
        )

    train_normal = train[
        train["label"] == 0
    ]

    if train_normal.empty:
        raise ValueError(
            "No normal samples available for model training."
        )

    if test["label"].nunique() != 2:
        raise ValueError(
            "Both known classes must exist in test data."
        )

    if train["time_step"].max() >= test["time_step"].min():
        raise ValueError(
            "Chronological overlap detected."
        )

    print(
        "Train time steps:",
        int(train["time_step"].min()),
        "-",
        int(train["time_step"].max()),
    )

    print(
        "Test time steps:",
        int(test["time_step"].min()),
        "-",
        int(test["time_step"].max()),
    )

    print("Train rows:", len(train))
    print("Test rows:", len(test))
    print("Normal training rows:", len(train_normal))

    return train, test


def summarize_split(data: pd.DataFrame) -> dict:
    normal = int(
        (data["label"] == 0).sum()
    )

    anomalies = int(
        (data["label"] == 1).sum()
    )

    return {
        "rows": len(data),
        "normal": normal,
        "anomalies": anomalies,
        "anomaly_fraction": round(
            anomalies / len(data),
            6,
        ),
        "first_time_step": int(
            data["time_step"].min()
        ),
        "last_time_step": int(
            data["time_step"].max()
        ),
    }


def save_outputs(
    train: pd.DataFrame,
    test: pd.DataFrame,
    statistics: dict,
) -> None:
    print()
    print("STEP 6: SAVING PREPARED RESEARCH DATA")

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_normal = train[
        train["label"] == 0
    ].copy()

    train_normal_path = (
        OUTPUT_DIRECTORY / "train_normal.parquet"
    )

    train_labeled_path = (
        OUTPUT_DIRECTORY / "train_labeled.parquet"
    )

    test_path = (
        OUTPUT_DIRECTORY / "test_labeled.parquet"
    )

    # These files retain the original numerical features.
    # Normalization must be fitted only on training data
    # by the later model-specific validation module.

    train_normal.to_parquet(
        train_normal_path,
        index=False,
        engine="pyarrow",
    )

    train.to_parquet(
        train_labeled_path,
        index=False,
        engine="pyarrow",
    )

    test.to_parquet(
        test_path,
        index=False,
        engine="pyarrow",
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "dataset": "Elliptic Bitcoin Dataset",
        "mode": "REAL_DATA_PREPARATION",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_files": [
            CLASSES_FILE.name,
            FEATURES_FILE.name,
        ],
        "label_mapping": {
            "1": "illicit / anomaly",
            "2": "licit / normal",
            "unknown": "excluded",
        },
        "features": {
            "number": EXPECTED_FEATURES,
            "column_names": FEATURE_COLUMNS,
            "original_features_preserved": True,
            "ethereum_specific_features_invented": False,
            "feature_values_normalized": False,
        },
        "split": {
            "strategy": "chronological Elliptic time step",
            "train_time_steps": "1-34",
            "test_time_steps": "35-49",
            "random_split": False,
        },
        "statistics": statistics,
        "train": summarize_split(train),
        "test": summarize_split(test),
        "outputs": [
            train_normal_path.name,
            train_labeled_path.name,
            test_path.name,
        ],
        "research_limitations": [
            "Time-step separation does not eliminate "
            "all possible graph or entity dependencies.",
            "Original anonymized features require "
            "careful interpretation.",
            "No network gas metric was invented.",
            "Data preparation is not model validation.",
            "Model-specific preprocessing must be "
            "fitted on training observations only.",
            "Further independent datasets are needed "
            "for external generalization.",
        ],
    }

    report_path = (
        OUTPUT_DIRECTORY / "dataset_report.json"
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("SAVED:")
    print(train_normal_path)
    print(train_labeled_path)
    print(test_path)
    print(report_path)


def main() -> None:
    print_header()

    validate_files()

    classes = load_classes()

    features = load_features()

    labeled, statistics = join_and_label(
        features,
        classes,
    )

    validate_numeric_data(labeled)

    train, test = split_by_time(labeled)

    save_outputs(
        train,
        test,
        statistics,
    )

    print()
    print("=" * 70)
    print("V13.1 ELLIPTIC DATA PREPARATION COMPLETED")
    print("=" * 70)

    print()
    print("Original 165 numeric features preserved.")
    print("No synthetic transactions generated.")
    print("Chronological train/test split complete.")
    print()
    print(
        "NEXT: Model adaptation and real-data evaluation."
    )


if __name__ == "__main__":
    main()

