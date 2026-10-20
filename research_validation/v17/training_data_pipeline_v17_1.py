
"""
QUANTUM CYBER DEFENSE ARENA
V17.1 - AI TRAINING DATA PIPELINE

Prepare real blockchain transaction features
for subsequent machine-learning research.

Read-only source processing.
No wallet access or blockchain transactions.
"""

import csv
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V16 = ROOT / "research_validation" / "v16"
V17 = ROOT / "research_validation" / "v17"

OUTPUT_CSV = V17 / "training_features_v17_1.csv"
OUTPUT_JSON = V17 / "training_data_pipeline_v17_1_results.json"

EXCLUDED = {
    "hash",
    "tx_hash",
    "transaction_hash",
    "block_hash",
    "from",
    "to",
    "from_address",
    "to_address",
    "sender",
    "receiver",
    "address",
    "block_number",
    "block_timestamp",
    "timestamp",
    "transaction_index",
    "index",
    "label",
    "target",
    "class",
    "is_fraud",
    "is_anomaly",
    "anomaly",
    "anomaly_score",
    "risk_score",
    "threat_score",
    "prediction",
    "predicted_label",
    "isolation_forest_score",
    "isolation_forest_label",
}


def normalized_name(name):
    return str(name).strip().lower().replace(
        "-", "_"
    ).replace(" ", "_")


def excluded_column(name):
    name = normalized_name(name)

    if name in EXCLUDED:
        return True

    return name.endswith((
        "_hash",
        "_address",
        "_label",
        "_score",
        "_prediction",
        "_timestamp",
    ))


def number(value):
    if value is None or isinstance(value, bool):
        return None

    try:
        if isinstance(value, str):
            value = value.strip()

            if not value:
                return None

            if value.startswith("0x"):
                return None

        result = float(value)

        if math.isfinite(result):
            return result

    except (TypeError, ValueError, OverflowError):
        pass

    return None


def find_source():
    if not V16.exists():
        raise FileNotFoundError(
            f"V16 directory not found: {V16}"
        )

    preferred = [
        V16 / "transaction_features_v16_2.csv",
        V16 / "transaction_features_v16_2_results.csv",
    ]

    for path in preferred:
        if path.is_file():
            return path

    candidates = [
        path
        for path in V16.rglob("*.csv")
        if (
            "feature" in path.name.lower()
            and "v17" not in path.name.lower()
        )
    ]

    if not candidates:
        raise FileNotFoundError(
            "No V16 transaction feature CSV found. "
            "Run V16.2 or export its transaction "
            "features to a CSV file."
        )

    return sorted(candidates)[0]


def load_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)
        fields = reader.fieldnames or []

        rows = list(reader)

    if not fields:
        raise ValueError(
            "Source CSV has no column headers."
        )

    if not rows:
        raise ValueError(
            "Source CSV contains no transactions."
        )

    return fields, rows


def select_numeric_features(fields, rows):
    features = []
    rejected = {}

    for field in fields:
        if excluded_column(field):
            rejected[field] = "excluded_metadata_or_label"
            continue

        values = [
            number(row.get(field))
            for row in rows
        ]

        valid = [
            value
            for value in values
            if value is not None
        ]

        if len(valid) < 2:
            rejected[field] = "insufficient_numeric_values"
            continue

        if len(set(valid)) < 2:
            rejected[field] = "constant_feature"
            continue

        if len(valid) / len(rows) < 0.5:
            rejected[field] = "too_many_missing_values"
            continue

        features.append(field)

    if not features:
        raise ValueError(
            "No suitable varying numeric features "
            "found in the V16 CSV."
        )

    return features, rejected


def prepare_rows(rows, features):
    medians = {}

    for feature in features:
        valid = [
            number(row.get(feature))
            for row in rows
        ]

        medians[feature] = statistics.median(
            value for value in valid
            if value is not None
        )

    prepared = []
    missing_values_filled = 0

    for row in rows:
        output = {}

        for feature in features:
            value = number(row.get(feature))

            if value is None:
                value = medians[feature]
                missing_values_filled += 1

            output[feature] = value

        prepared.append(output)

    return prepared, missing_values_filled


def save_csv(rows, features):
    V17.mkdir(parents=True, exist_ok=True)

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=features,
        )

        writer.writeheader()
        writer.writerows(rows)


def save_report(report):
    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )


def main():
    print("=" * 60)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V17.1 - AI TRAINING DATA PIPELINE")
    print("=" * 60)

    source = find_source()

    print(f"SOURCE: {source}")

    fields, rows = load_csv(source)

    features, rejected = select_numeric_features(
        fields,
        rows,
    )

    prepared, filled = prepare_rows(
        rows,
        features,
    )

    save_csv(prepared, features)

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V17.1",
        "module": "AI Training Data Pipeline",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "source": str(source.relative_to(ROOT)),
        "source_rows": len(rows),
        "source_columns": len(fields),
        "prepared_rows": len(prepared),
        "selected_features": features,
        "feature_count": len(features),
        "rejected_columns": rejected,
        "missing_values_imputed": filled,
        "imputation_method": "median",
        "supervised_training_ready": False,
        "verified_threat_labels": False,
        "status": "FEATURE_PREPARATION_PASS",
        "limitations": [
            "No verified malicious transaction labels.",
            "No model training performed.",
            "No demonstrated threat detection accuracy.",
            "Median imputation must be fitted on "
            "training data only during future model "
            "evaluation to avoid data leakage.",
        ],
    }

    save_report(report)

    print()
    print(f"SOURCE ROWS: {len(rows)}")
    print(f"PREPARED ROWS: {len(prepared)}")
    print(f"FEATURE COUNT: {len(features)}")
    print(f"MISSING VALUES FILLED: {filled}")

    print()
    print("SELECTED FEATURES:")

    for feature in features:
        print(f"  - {feature}")

    print()
    print("SUPERVISED TRAINING READY: NO")
    print("V17.1 RESULT: FEATURE_PREPARATION_PASS")
    print(f"SAVED CSV: {OUTPUT_CSV}")
    print(f"SAVED REPORT: {OUTPUT_JSON}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as error:
        print()
        print(
            "V17.1 FAILED: "
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)
