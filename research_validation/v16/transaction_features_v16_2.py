
"""
QUANTUM CYBER DEFENSE ARENA
V16.2 - TRANSACTION FEATURE ENGINEERING

Input:
    blockchain_ingestion_v16_1_results.json

Outputs:
    transaction_features_v16_2_results.json
    transaction_features_v16_2.csv

Features:
- Real Ethereum transaction value
- Logarithmic transaction value
- Gas limit
- Gas price
- Maximum fee and priority fee
- Contract creation indicator
- Zero-value transaction indicator
- Same-block sender frequency
- Exploratory statistical outlier flags
- Data-quality checks

IMPORTANT:
The input contains a small sample from one real block.
Outlier flags are NOT evidence of fraud or cyberattacks.
No trained AI or quantum model is executed.
No blockchain transaction is submitted.

Python 3.11+ - standard library only.
"""

from __future__ import annotations

import csv
import json
import math
import statistics

from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


VERSION = "16.2.0"

HERE = Path(__file__).resolve().parent

INPUT_FILE = (
    HERE / "blockchain_ingestion_v16_1_results.json"
)

JSON_OUTPUT = (
    HERE / "transaction_features_v16_2_results.json"
)

CSV_OUTPUT = (
    HERE / "transaction_features_v16_2.csv"
)

FEATURE_COLUMNS = [
    "transaction_hash",
    "network",
    "block_number",
    "value_eth",
    "log_value_eth",
    "gas_limit",
    "log_gas_limit",
    "gas_price_gwei",
    "max_fee_per_gas_gwei",
    "max_priority_fee_gwei",
    "nonce",
    "transaction_type",
    "is_contract_creation",
    "is_zero_value",
    "sender_tx_count_in_sample",
    "value_outlier_flag",
    "gas_outlier_flag",
    "exploratory_flag_count",
    "classification",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise ValueError(message)


def decimal_value(
    value: Any,
    field_name: str,
    allow_none: bool = False,
) -> float | None:

    if value is None:
        if allow_none:
            return None

        raise ValueError(
            f"Missing required numeric field: {field_name}"
        )

    if isinstance(value, bool):
        raise ValueError(
            f"Invalid boolean in {field_name}"
        )

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(
            f"Invalid numeric value in {field_name}"
        ) from error

    require(
        number.is_finite() and number >= 0,
        f"{field_name} must be finite and non-negative",
    )

    result = float(number)

    require(
        math.isfinite(result),
        f"{field_name} exceeds supported numeric range",
    )

    return result


def integer_value(
    value: Any,
    field_name: str,
    allow_none: bool = False,
) -> int | None:

    if value is None and allow_none:
        return None

    require(
        type(value) is int and value >= 0,
        f"{field_name} must be a non-negative integer",
    )

    return value


def valid_eth_hash(value: Any) -> bool:
    if not isinstance(value, str):
        return False

    if len(value) != 66 or not value.startswith("0x"):
        return False

    return all(
        character in "0123456789abcdefABCDEF"
        for character in value[2:]
    )


def valid_address(
    value: Any,
    nullable: bool = False,
) -> bool:
    if nullable and value is None:
        return True

    if not isinstance(value, str):
        return False

    if len(value) != 42 or not value.startswith("0x"):
        return False

    return all(
        character in "0123456789abcdefABCDEF"
        for character in value[2:]
    )


def load_input() -> dict[str, Any]:

    require(
        INPUT_FILE.is_file(),
        (
            "V16.1 result file not found. "
            "Run blockchain_ingestion_v16_1.py first."
        ),
    )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as handle:
        payload = json.load(handle)

    require(
        isinstance(payload, dict),
        "Invalid JSON root structure",
    )

    require(
        payload.get("version") == "16.1.0",
        "Expected V16.1.0 result file",
    )

    require(
        payload.get("network") == "ethereum-mainnet",
        "Expected Ethereum mainnet input",
    )

    require(
        payload.get("mode")
        == "READ_ONLY_PUBLIC_BLOCKCHAIN",
        "Unexpected data collection mode",
    )

    block = payload.get("block")

    require(
        isinstance(block, dict),
        "Missing block metadata",
    )

    require(
        valid_eth_hash(block.get("hash")),
        "Invalid block hash",
    )

    integer_value(
        block.get("number"),
        "block.number",
    )

    transactions = payload.get("transactions")

    require(
        isinstance(transactions, list)
        and len(transactions) > 0,
        "No transaction records found",
    )

    collection = payload.get("collection")

    require(
        isinstance(collection, dict),
        "Missing collection metadata",
    )

    require(
        collection.get("processed") == len(transactions),
        "V16.1 processed count does not match records",
    )

    seen_hashes: set[str] = set()

    for index, tx in enumerate(transactions):

        require(
            isinstance(tx, dict),
            f"Transaction #{index} is not a JSON object",
        )

        tx_hash = tx.get("transaction_hash")

        require(
            valid_eth_hash(tx_hash),
            f"Invalid transaction hash at index {index}",
        )

        require(
            tx_hash not in seen_hashes,
            f"Duplicate transaction hash: {tx_hash}",
        )

        seen_hashes.add(tx_hash)

        require(
            valid_address(tx.get("from_address")),
            f"Invalid sender at index {index}",
        )

        require(
            valid_address(
                tx.get("to_address"),
                nullable=True,
            ),
            f"Invalid recipient at index {index}",
        )

    return payload


def robust_upper_outlier_flags(
    values: list[float],
) -> list[bool]:
    """
    Exploratory upper-tail outlier indicators.

    Requires at least 8 observations.
    Uses median and median absolute deviation.

    These are descriptive data-quality signals,
    NOT trained anomaly classifications.
    """

    if len(values) < 8:
        return [False] * len(values)

    median = statistics.median(values)

    deviations = [
        abs(value - median)
        for value in values
    ]

    mad = statistics.median(deviations)

    if mad == 0:
        return [False] * len(values)

    return [
        (
            0.6745 * (value - median) / mad
        ) > 3.5
        for value in values
    ]


def extract_features(
    payload: dict[str, Any],
) -> list[dict[str, Any]]:

    transactions = payload["transactions"]

    block_number = payload["block"]["number"]

    sender_counts = Counter(
        tx["from_address"].lower()
        for tx in transactions
    )

    features = []

    for tx in transactions:

        value_eth = decimal_value(
            tx["value_eth"],
            "value_eth",
        )

        gas_limit = integer_value(
            tx["gas_limit"],
            "gas_limit",
        )

        nonce = integer_value(
            tx["nonce"],
            "nonce",
        )

        tx_type = integer_value(
            tx.get("transaction_type"),
            "transaction_type",
            allow_none=True,
        )

        gas_price = decimal_value(
            tx.get("gas_price_gwei"),
            "gas_price_gwei",
            allow_none=True,
        )

        max_fee = decimal_value(
            tx.get("max_fee_per_gas_gwei"),
            "max_fee_per_gas_gwei",
            allow_none=True,
        )

        priority_fee = decimal_value(
            tx.get("max_priority_fee_gwei"),
            "max_priority_fee_gwei",
            allow_none=True,
        )

        sender = tx["from_address"].lower()

        recipient = tx["to_address"]

        row = {
            "transaction_hash": tx["transaction_hash"],
            "network": "ethereum-mainnet",
            "block_number": block_number,
            "value_eth": value_eth,
            "log_value_eth": round(
                math.log1p(value_eth),
                8,
            ),
            "gas_limit": gas_limit,
            "log_gas_limit": round(
                math.log1p(gas_limit),
                8,
            ),
            "gas_price_gwei": gas_price,
            "max_fee_per_gas_gwei": max_fee,
            "max_priority_fee_gwei": priority_fee,
            "nonce": nonce,
            "transaction_type": tx_type,
            "is_contract_creation": int(
                recipient is None
            ),
            "is_zero_value": int(
                value_eth == 0
            ),
            "sender_tx_count_in_sample": (
                sender_counts[sender]
            ),
            "value_outlier_flag": 0,
            "gas_outlier_flag": 0,
            "exploratory_flag_count": 0,
            "classification": "NOT_EVALUATED",
        }

        features.append(row)

    value_flags = robust_upper_outlier_flags(
        [
            row["log_value_eth"]
            for row in features
        ]
    )

    gas_flags = robust_upper_outlier_flags(
        [
            row["log_gas_limit"]
            for row in features
        ]
    )

    for index, row in enumerate(features):

        row["value_outlier_flag"] = int(
            value_flags[index]
        )

        row["gas_outlier_flag"] = int(
            gas_flags[index]
        )

        row["exploratory_flag_count"] = (
            row["value_outlier_flag"]
            + row["gas_outlier_flag"]
        )

    return features


def build_summary(
    features: list[dict[str, Any]],
    payload: dict[str, Any],
) -> dict[str, Any]:

    values = [
        row["value_eth"]
        for row in features
    ]

    gas_limits = [
        row["gas_limit"]
        for row in features
    ]

    return {
        "block_number": payload["block"]["number"],
        "block_hash": payload["block"]["hash"],
        "sample_size": len(features),
        "selection": payload["collection"].get(
            "selection"
        ),
        "unique_senders": len({
            tx["from_address"].lower()
            for tx in payload["transactions"]
        }),
        "average_value_eth": round(
            statistics.mean(values), 9
        ),
        "median_value_eth": round(
            statistics.median(values), 9
        ),
        "maximum_value_eth": round(
            max(values), 9
        ),
        "average_gas_limit": round(
            statistics.mean(gas_limits), 2
        ),
        "contract_creations": sum(
            row["is_contract_creation"]
            for row in features
        ),
        "zero_value_transactions": sum(
            row["is_zero_value"]
            for row in features
        ),
        "value_outliers": sum(
            row["value_outlier_flag"]
            for row in features
        ),
        "gas_limit_outliers": sum(
            row["gas_outlier_flag"]
            for row in features
        ),
        "exploratory_flagged_transactions": sum(
            row["exploratory_flag_count"] > 0
            for row in features
        ),
        "threats_confirmed": None,
        "classification_mode": "NOT_EVALUATED",
    }


def save_results(
    payload: dict[str, Any],
    features: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:

    output = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "module": "Transaction Feature Engineering",
        "mode": "REAL_BLOCKCHAIN_FEATURE_EXTRACTION",
        "generated_at": utc_now(),
        "network": "ethereum-mainnet",
        "source_file": INPUT_FILE.name,
        "source_block": payload["block"],
        "summary": summary,
        "feature_columns": FEATURE_COLUMNS,
        "transactions": features,
        "limitations": [
            "Data comes from a small single-block sample.",
            "Selection of the first transactions is not random.",
            "Value and gas-limit outliers are descriptive only.",
            "No confirmed security incident labels are available.",
            "Gas limit is not actual gas used.",
            "Public on-chain activity can have legitimate causes.",
            "No AI or quantum model is executed.",
            "No statistical generalization is claimed.",
            "No wallet or blockchain transaction is performed.",
        ],
    }

    JSON_OUTPUT.write_text(
        json.dumps(
            output,
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
            fieldnames=FEATURE_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(features)


def main() -> None:

    print()
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA V16.2")
    print("TRANSACTION FEATURE ENGINEERING")
    print("=" * 70)

    payload = load_input()

    features = extract_features(payload)

    summary = build_summary(
        features,
        payload,
    )

    save_results(
        payload,
        features,
        summary,
    )

    print()
    print("REAL BLOCKCHAIN FEATURE SUMMARY")
    print("-" * 70)

    print(
        "Block number:",
        summary["block_number"],
    )

    print(
        "Transactions processed:",
        summary["sample_size"],
    )

    print(
        "Unique senders:",
        summary["unique_senders"],
    )

    print(
        "Average transaction value:",
        summary["average_value_eth"],
        "ETH",
    )

    print(
        "Median transaction value:",
        summary["median_value_eth"],
        "ETH",
    )

    print(
        "Contract creations:",
        summary["contract_creations"],
    )

    print(
        "Zero-value transactions:",
        summary["zero_value_transactions"],
    )

    print(
        "Exploratory flagged transactions:",
        summary["exploratory_flagged_transactions"],
    )

    print()
    print("SAMPLE FEATURE ROWS")
    print("-" * 70)

    for row in features[:5]:
        print(
            row["transaction_hash"][:18],
            "| ETH:",
            row["value_eth"],
            "| GAS:",
            row["gas_limit"],
            "| FLAGS:",
            row["exploratory_flag_count"],
        )

    print()
    print("=" * 70)
    print("V16.2 TRANSACTION FEATURE ENGINEERING COMPLETED")
    print("=" * 70)

    print()
    print("RESULTS SAVED TO:")
    print(JSON_OUTPUT)
    print(CSV_OUTPUT)

    print()
    print(
        "NOTE: Real Ethereum features were extracted. "
        "Outlier flags are exploratory, not confirmed threats."
    )


if __name__ == "__main__":
    main()
