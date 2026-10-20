
"""
QUANTUM CYBER DEFENSE ARENA
V16.3 - BLOCKCHAIN ANOMALY DETECTION

Research-only Isolation Forest analysis of
real Ethereum transaction features from V16.2.

Input:
    transaction_features_v16_2_results.json

Outputs:
    blockchain_anomaly_v16_3_results.json
    blockchain_anomaly_v16_3.csv

IMPORTANT:
- Data contains a small, biased, single-block sample.
- Anomalies are statistical observations, not attacks.
- No fraud labels are available.
- No accuracy or F1 score is claimed.
- No blockchain or wallet actions are performed.

Requires:
    numpy
    scikit-learn
"""

from __future__ import annotations

import csv
import json
import math
import sys

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:
    raise SystemExit(
        "Missing dependency. Install with:\n"
        "python -m pip install numpy scikit-learn"
    ) from exc


VERSION = "16.3.0"

HERE = Path(__file__).resolve().parent

INPUT_FILE = (
    HERE / "transaction_features_v16_2_results.json"
)

JSON_OUTPUT = (
    HERE / "blockchain_anomaly_v16_3_results.json"
)

CSV_OUTPUT = (
    HERE / "blockchain_anomaly_v16_3.csv"
)

RANDOM_STATE = 163

# Small, single-block training data.
# This is experimental and not a calibrated threshold.
CONTAMINATION = 0.10

MIN_SAMPLES = 8

FEATURE_NAMES = [
    "log_value_eth",
    "log_gas_limit",
    "gas_price_gwei",
    "max_fee_per_gas_gwei",
    "max_priority_fee_gwei",
    "nonce",
    "is_contract_creation",
    "is_zero_value",
    "sender_tx_count_in_sample",
]

CSV_COLUMNS = [
    "transaction_hash",
    "network",
    "block_number",
    "value_eth",
    "gas_limit",
    "anomaly_score",
    "isolation_forest_prediction",
    "classification",
    "risk_indicator",
    "mode",
]


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise ValueError(message)


def validate_numeric(
    value: Any,
    field_name: str,
    allow_missing: bool = False,
) -> float | None:

    if value is None:
        if allow_missing:
            return None

        raise ValueError(
            f"Missing required value: {field_name}"
        )

    require(
        not isinstance(value, bool),
        f"Boolean is invalid for {field_name}",
    )

    try:
        number = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"Invalid numeric value: {field_name}"
        ) from exc

    require(
        math.isfinite(number) and number >= 0,
        f"Invalid numeric range: {field_name}",
    )

    return number


def load_features() -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
]:
    require(
        INPUT_FILE.is_file(),
        (
            "V16.2 results not found:\n"
            f"{INPUT_FILE}\n"
            "Run transaction_features_v16_2.py first."
        ),
    )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as handle:
        payload = json.load(handle)

    require(
        isinstance(payload, dict),
        "Invalid JSON root",
    )

    require(
        payload.get("version") == "16.2.0",
        "Expected V16.2.0 results",
    )

    require(
        payload.get("network") == "ethereum-mainnet",
        "Expected Ethereum mainnet input",
    )

    require(
        payload.get("mode")
        == "REAL_BLOCKCHAIN_FEATURE_EXTRACTION",
        "Unexpected input mode",
    )

    transactions = payload.get("transactions")

    require(
        isinstance(transactions, list),
        "Missing transaction list",
    )

    require(
        len(transactions) >= MIN_SAMPLES,
        (
            f"At least {MIN_SAMPLES} records are required. "
            f"Found {len(transactions)}."
        ),
    )

    seen_hashes = set()

    for index, row in enumerate(transactions):
        require(
            isinstance(row, dict),
            f"Invalid transaction row #{index}",
        )

        tx_hash = row.get("transaction_hash")

        require(
            isinstance(tx_hash, str)
            and tx_hash.startswith("0x")
            and len(tx_hash) == 66,
            f"Invalid transaction hash #{index}",
        )

        require(
            tx_hash not in seen_hashes,
            f"Duplicate transaction: {tx_hash}",
        )

        seen_hashes.add(tx_hash)

        for feature in FEATURE_NAMES:
            validate_numeric(
                row.get(feature),
                feature,
                allow_missing=feature in {
                    "gas_price_gwei",
                    "max_fee_per_gas_gwei",
                    "max_priority_fee_gwei",
                },
            )

    summary = payload.get("summary")

    require(
        isinstance(summary, dict),
        "Missing V16.2 summary",
    )

    require(
        summary.get("sample_size")
        == len(transactions),
        "Transaction count mismatch",
    )

    return payload, transactions


def build_feature_matrix(
    rows: list[dict[str, Any]],
) -> tuple[np.ndarray, list[str], dict[str, Any]]:
    """
    Avoid using identifiers as ML features.
    Missing fee values are imputed using
    observed feature medians.

    Entirely missing feature columns are excluded.
    """

    selected_features = []

    for name in FEATURE_NAMES:
        if any(
            row.get(name) is not None
            for row in rows
        ):
            selected_features.append(name)

    require(
        len(selected_features) >= 2,
        "Not enough usable numeric features",
    )

    matrix = np.array(
        [
            [
                (
                    float(row[name])
                    if row.get(name) is not None
                    else np.nan
                )
                for name in selected_features
            ]
            for row in rows
        ],
        dtype=float,
    )

    require(
        np.isfinite(
            matrix[~np.isnan(matrix)]
        ).all(),
        "Matrix contains invalid numeric values",
    )

    missing_count = int(
        np.isnan(matrix).sum()
    )

    imputer = SimpleImputer(
        strategy="median"
    )

    imputed = imputer.fit_transform(matrix)

    require(
        imputed.shape[1] == len(selected_features),
        "Feature shape changed during imputation",
    )

    variances = np.var(imputed, axis=0)

    varying = [
        index
        for index, variance in enumerate(variances)
        if variance > 1e-12
    ]

    require(
        len(varying) >= 1,
        "All selected features are constant",
    )

    selected_features = [
        selected_features[index]
        for index in varying
    ]

    imputed = imputed[:, varying]

    scaler = StandardScaler()

    scaled = scaler.fit_transform(imputed)

    metadata = {
        "missing_numeric_values_imputed": missing_count,
        "imputation": "median",
        "scaling": "StandardScaler",
        "constant_columns_excluded": True,
        "identifiers_used_as_features": False,
    }

    return scaled, selected_features, metadata


def train_and_score(
    matrix: np.ndarray,
) -> tuple[
    IsolationForest,
    np.ndarray,
    np.ndarray,
]:
    model = IsolationForest(
        n_estimators=200,
        contamination=CONTAMINATION,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )

    predictions = model.fit_predict(matrix)

    # Higher anomaly_score means more unusual
    # relative to this fitted sample.
    scores = -model.score_samples(matrix)

    require(
        np.isfinite(scores).all(),
        "Non-finite anomaly scores",
    )

    return model, predictions, scores


def describe_risk(
    prediction: int,
) -> str:
    if prediction == -1:
        return "EXPLORATORY_OUTLIER"

    return "WITHIN_SAMPLE_PATTERN"


def assemble_results(
    payload: dict[str, Any],
    rows: list[dict[str, Any]],
    predictions: np.ndarray,
    scores: np.ndarray,
) -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
]:
    output_rows = []

    for row, prediction, score in zip(
        rows,
        predictions,
        scores,
    ):
        is_outlier = int(prediction) == -1

        output_rows.append(
            {
                "transaction_hash": row[
                    "transaction_hash"
                ],
                "network": row["network"],
                "block_number": row["block_number"],
                "value_eth": row["value_eth"],
                "gas_limit": row["gas_limit"],
                "anomaly_score": round(
                    float(score), 8
                ),
                "isolation_forest_prediction": int(
                    prediction
                ),
                "classification": (
                    "STATISTICAL_OUTLIER"
                    if is_outlier
                    else "NOT_FLAGGED"
                ),
                "risk_indicator": describe_risk(
                    int(prediction)
                ),
                "mode": "EXPLORATORY_UNSUPERVISED",
            }
        )

    count = Counter(
        row["classification"]
        for row in output_rows
    )

    flagged_count = count["STATISTICAL_OUTLIER"]

    summary = {
        "source_block_number": payload[
            "source_block"
        ]["number"],
        "source_block_hash": payload[
            "source_block"
        ]["hash"],
        "transactions_analyzed": len(
            output_rows
        ),
        "statistical_outliers": flagged_count,
        "not_flagged": count["NOT_FLAGGED"],
        "outlier_fraction": round(
            flagged_count / len(output_rows),
            4,
        ),
        "average_anomaly_score": round(
            float(np.mean(scores)),
            8,
        ),
        "minimum_anomaly_score": round(
            float(np.min(scores)),
            8,
        ),
        "maximum_anomaly_score": round(
            float(np.max(scores)),
            8,
        ),
        "confirmed_threats": None,
        "labeled_ground_truth_available": False,
        "classification_accuracy": None,
        "f1_score": None,
    }

    return output_rows, summary


def save_outputs(
    output_rows: list[dict[str, Any]],
    summary: dict[str, Any],
    selected_features: list[str],
    preprocessing: dict[str, Any],
) -> None:
    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "module": "Blockchain Anomaly Detection",
        "mode": "EXPLORATORY_UNSUPERVISED",
        "generated_at": utc_now(),
        "network": "ethereum-mainnet",
        "source_file": INPUT_FILE.name,
        "algorithm": {
            "name": "IsolationForest",
            "n_estimators": 200,
            "contamination": CONTAMINATION,
            "random_state": RANDOM_STATE,
            "training_scope": (
                "Same single-block sample used for "
                "training and scoring"
            ),
            "anomaly_score_definition": (
                "negative score_samples; higher means "
                "more unusual within this sample"
            ),
        },
        "selected_features": selected_features,
        "preprocessing": preprocessing,
        "summary": summary,
        "transactions": output_rows,
        "limitations": [
            "Real Ethereum inputs, but a small biased sample.",
            "The first transactions of one block were selected.",
            "Training and scoring use the same sample.",
            "Isolation Forest decisions are not attack labels.",
            "Contamination is an experimental parameter.",
            "No independent test set is evaluated.",
            "No verified illicit-transaction labels exist.",
            "Accuracy, recall and F1 cannot be calculated.",
            "No trained quantum model is used.",
            "No blockchain or wallet action is executed.",
        ],
    }

    JSON_OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        ),
        encoding="utf-8",
    )

    with CSV_OUTPUT.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=CSV_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(output_rows)


def main() -> int:
    print()
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA V16.3")
    print("BLOCKCHAIN ANOMALY DETECTION")
    print("=" * 70)

    try:
        payload, transactions = load_features()

        matrix, selected_features, preprocessing = (
            build_feature_matrix(transactions)
        )

        _, predictions, scores = train_and_score(
            matrix
        )

        results, summary = assemble_results(
            payload,
            transactions,
            predictions,
            scores,
        )

        save_outputs(
            results,
            summary,
            selected_features,
            preprocessing,
        )

    except (
        ValueError,
        TypeError,
        KeyError,
        OSError,
        json.JSONDecodeError,
    ) as exc:
        print()
        print("V16.3 ANOMALY DETECTION FAILED")
        print(str(exc))
        return 1

    print()
    print("REAL BLOCKCHAIN ANALYSIS")
    print("-" * 70)

    print(
        "Transactions analyzed:",
        summary["transactions_analyzed"],
    )
    print(
        "Statistical outliers:",
        summary["statistical_outliers"],
    )
    print(
        "Not flagged:",
        summary["not_flagged"],
    )
    print(
        "Average anomaly score:",
        summary["average_anomaly_score"],
    )

    print()
    print("FEATURES USED:")
    for name in selected_features:
        print(" -", name)

    print()
    print("SAMPLE RESULTS")
    print("-" * 70)

    for row in results[:5]:
        print(
            row["transaction_hash"][:20],
            "| Score:",
            row["anomaly_score"],
            "|",
            row["classification"],
        )

    print()
    print("=" * 70)
    print("V16.3 BLOCKCHAIN ANOMALY DETECTION COMPLETED")
    print("=" * 70)

    print()
    print("RESULTS SAVED TO:")
    print(JSON_OUTPUT)
    print(CSV_OUTPUT)

    print()
    print(
        "NOTE: Statistical outliers are not "
        "confirmed blockchain threats."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
