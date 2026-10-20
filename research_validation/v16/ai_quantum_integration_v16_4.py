
"""
QUANTUM CYBER DEFENSE ARENA
V16.4 - AI–QUANTUM THREAT INTEGRATION

Real Ethereum transaction research pipeline.

Inputs:
    transaction_features_v16_2_results.json
    blockchain_anomaly_v16_3_results.json

Optional future input:
    quantum_scores_v16_4.json

Outputs:
    ai_quantum_integration_v16_4_results.json
    ai_quantum_integration_v16_4.csv

Functions:
- Validate V16.2 and V16.3 inputs
- Match transactions by real transaction hash
- Preserve actual Isolation Forest model outputs
- Create a verified interface for quantum model results
- Calculate hybrid agreement ONLY if genuine quantum
  outputs for the same transactions are provided
- Preserve source and data provenance
- Produce integration and research audit summaries

No quantum scores are invented.
No live threat detection is claimed.
No blockchain or wallet operations are performed.
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


VERSION = "16.4.0"

HERE = Path(__file__).resolve().parent

FEATURE_FILE = (
    HERE / "transaction_features_v16_2_results.json"
)

CLASSICAL_FILE = (
    HERE / "blockchain_anomaly_v16_3_results.json"
)

QUANTUM_FILE = (
    HERE / "quantum_scores_v16_4.json"
)

JSON_OUTPUT = (
    HERE / "ai_quantum_integration_v16_4_results.json"
)

CSV_OUTPUT = (
    HERE / "ai_quantum_integration_v16_4.csv"
)

CSV_COLUMNS = [
    "transaction_hash",
    "network",
    "block_number",
    "value_eth",
    "gas_limit",
    "classical_anomaly_score",
    "classical_prediction",
    "classical_classification",
    "quantum_anomaly_score",
    "quantum_prediction",
    "hybrid_decision",
    "model_agreement",
    "integration_status",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise ValueError(message)


def valid_hash(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 66
        and value.startswith("0x")
        and all(
            character in "0123456789abcdefABCDEF"
            for character in value[2:]
        )
    )


def checked_float(
    value: Any,
    field: str,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    require(
        type(value) in (int, float, str),
        f"Invalid numeric type: {field}",
    )

    result = float(value)

    require(
        math.isfinite(result),
        f"Non-finite numeric value: {field}",
    )

    if minimum is not None:
        require(
            result >= minimum,
            f"{field} below minimum",
        )

    if maximum is not None:
        require(
            result <= maximum,
            f"{field} above maximum",
        )

    return result


def read_json(path: Path) -> dict[str, Any]:
    require(
        path.is_file(),
        f"Missing input file: {path}",
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        payload = json.load(handle)

    require(
        isinstance(payload, dict),
        f"Invalid JSON document: {path.name}",
    )

    return payload


def indexed_rows(
    rows: Any,
    name: str,
) -> dict[str, dict[str, Any]]:
    require(
        isinstance(rows, list) and len(rows) > 0,
        f"{name}: missing or empty transactions",
    )

    result = {}

    for row in rows:
        require(
            isinstance(row, dict),
            f"{name}: invalid row structure",
        )

        tx_hash = row.get("transaction_hash")

        require(
            valid_hash(tx_hash),
            f"{name}: invalid transaction hash",
        )

        normalized_hash = tx_hash.lower()

        require(
            normalized_hash not in result,
            f"{name}: duplicate transaction hash",
        )

        result[normalized_hash] = row

    return result


def validate_real_inputs() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    features = read_json(FEATURE_FILE)
    classical = read_json(CLASSICAL_FILE)

    require(
        features.get("version") == "16.2.0",
        "Expected V16.2 feature data",
    )

    require(
        classical.get("version") == "16.3.0",
        "Expected V16.3 classical model data",
    )

    require(
        features.get("network") == "ethereum-mainnet",
        "Unexpected V16.2 network",
    )

    require(
        classical.get("network") == "ethereum-mainnet",
        "Unexpected V16.3 network",
    )

    require(
        features.get("mode")
        == "REAL_BLOCKCHAIN_FEATURE_EXTRACTION",
        "Unexpected V16.2 mode",
    )

    require(
        classical.get("mode")
        == "EXPLORATORY_UNSUPERVISED",
        "Unexpected V16.3 mode",
    )

    feature_rows = indexed_rows(
        features.get("transactions"),
        "V16.2",
    )

    classical_rows = indexed_rows(
        classical.get("transactions"),
        "V16.3",
    )

    require(
        set(feature_rows) == set(classical_rows),
        "V16.2 and V16.3 transaction hashes differ",
    )

    features_block = features.get("source_block")
    classical_summary = classical.get("summary")

    require(
        isinstance(features_block, dict)
        and isinstance(classical_summary, dict),
        "Missing source block metadata",
    )

    require(
        features_block.get("hash")
        == classical_summary.get("source_block_hash"),
        "Source block hashes do not match",
    )

    require(
        features_block.get("number")
        == classical_summary.get("source_block_number"),
        "Source block numbers do not match",
    )

    require(
        features.get("summary", {}).get("sample_size")
        == len(feature_rows),
        "V16.2 sample count mismatch",
    )

    require(
        classical_summary.get("transactions_analyzed")
        == len(classical_rows),
        "V16.3 sample count mismatch",
    )

    for tx_hash, row in classical_rows.items():

        prediction = row.get(
            "isolation_forest_prediction"
        )

        require(
            type(prediction) is int
            and prediction in (-1, 1),
            f"Invalid classical prediction: {tx_hash}",
        )

        expected_classification = (
            "STATISTICAL_OUTLIER"
            if prediction == -1
            else "NOT_FLAGGED"
        )

        require(
            row.get("classification")
            == expected_classification,
            f"Classical classification mismatch: {tx_hash}",
        )

        checked_float(
            row.get("anomaly_score"),
            "classical_anomaly_score",
        )

        feature_row = feature_rows[tx_hash]

        require(
            feature_row.get("network")
            == row.get("network"),
            f"Network mismatch: {tx_hash}",
        )

        require(
            feature_row.get("block_number")
            == row.get("block_number"),
            f"Block mismatch: {tx_hash}",
        )

    return (
        features,
        classical,
        feature_rows,
        classical_rows,
    )


def load_optional_quantum(
    expected_hashes: set[str],
    expected_block_hash: str,
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, Any],
]:
    """
    Optional input contract for future
    independently executed quantum model.

    Contract:
    {
      "network": "ethereum-mainnet",
      "block_hash": "0x...",
      "model_name": "...",
      "execution_mode": "CLASSICAL_QUANTUM_SIMULATOR",
      "score_definition": "...",
      "decision_threshold": 0.5,
      "transactions": [
        {
          "transaction_hash": "0x...",
          "anomaly_score": 0.7,
          "prediction": "ANOMALY"
        }
      ]
    }

    Scores must be the genuine output of a
    separately executed documented experiment.

    The file does not exist in this release.
    """

    if not QUANTUM_FILE.exists():
        return {}, {
            "available": False,
            "status": "QUANTUM_MODEL_NOT_EXECUTED",
            "source_file": None,
            "model_name": None,
        }

    payload = read_json(QUANTUM_FILE)

    require(
        payload.get("network") == "ethereum-mainnet",
        "Quantum input uses a different network",
    )

    require(
        payload.get("block_hash") == expected_block_hash,
        "Quantum input uses a different block",
    )

    require(
        isinstance(payload.get("model_name"), str)
        and bool(payload["model_name"].strip()),
        "Quantum model name is required",
    )

    require(
        payload.get("execution_mode") in {
            "CLASSICAL_QUANTUM_SIMULATOR",
            "QUANTUM_HARDWARE",
        },
        "Unsupported quantum execution mode",
    )

    require(
        isinstance(payload.get("score_definition"), str)
        and bool(payload["score_definition"].strip()),
        "Quantum score definition is required",
    )

    threshold = checked_float(
        payload.get("decision_threshold"),
        "quantum_decision_threshold",
        minimum=0.0,
        maximum=1.0,
    )

    rows = indexed_rows(
        payload.get("transactions"),
        "Quantum model",
    )

    require(
        set(rows) == expected_hashes,
        "Quantum output does not cover identical transactions",
    )

    for tx_hash, row in rows.items():

        score = checked_float(
            row.get("anomaly_score"),
            "quantum_anomaly_score",
            minimum=0.0,
            maximum=1.0,
        )

        prediction = row.get("prediction")

        require(
            prediction in {"NORMAL", "ANOMALY"},
            f"Invalid quantum prediction: {tx_hash}",
        )

        expected = (
            "ANOMALY" if score >= threshold
            else "NORMAL"
        )

        require(
            prediction == expected,
            f"Quantum threshold mismatch: {tx_hash}",
        )

    return rows, {
        "available": True,
        "status": "EXTERNAL_QUANTUM_RESULTS_LOADED",
        "source_file": QUANTUM_FILE.name,
        "model_name": payload["model_name"],
        "execution_mode": payload["execution_mode"],
        "score_definition": payload["score_definition"],
        "decision_threshold": threshold,
        "warning": (
            "File metadata and consistency are checked, "
            "but independent quantum execution and "
            "scientific provenance are not verified "
            "by this integration module."
        ),
    }


def integrate(
    feature_rows: dict[str, dict[str, Any]],
    classical_rows: dict[str, dict[str, Any]],
    quantum_rows: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:

    results = []

    for tx_hash, feature in feature_rows.items():

        classical = classical_rows[tx_hash]

        classical_prediction = (
            "ANOMALY"
            if classical["isolation_forest_prediction"] == -1
            else "NORMAL"
        )

        quantum = quantum_rows.get(tx_hash)

        if quantum is None:

            quantum_score = None
            quantum_prediction = None
            hybrid_decision = "NOT_EVALUATED"
            model_agreement = None
            integration_status = "CLASSICAL_ONLY"

        else:

            quantum_score = float(
                quantum["anomaly_score"]
            )

            quantum_prediction = quantum["prediction"]

            model_agreement = (
                classical_prediction == quantum_prediction
            )

            hybrid_decision = (
                classical_prediction
                if model_agreement
                else "REVIEW"
            )

            integration_status = (
                "BOTH_MODEL_OUTPUTS_AVAILABLE"
            )

        results.append({
            "transaction_hash": tx_hash,
            "network": feature["network"],
            "block_number": feature["block_number"],
            "value_eth": feature["value_eth"],
            "gas_limit": feature["gas_limit"],
            "classical_anomaly_score": (
                classical["anomaly_score"]
            ),
            "classical_prediction": (
                classical_prediction
            ),
            "classical_classification": (
                classical["classification"]
            ),
            "quantum_anomaly_score": quantum_score,
            "quantum_prediction": quantum_prediction,
            "hybrid_decision": hybrid_decision,
            "model_agreement": model_agreement,
            "integration_status": integration_status,
        })

    return results


def summarize(
    results: list[dict[str, Any]],
    quantum_metadata: dict[str, Any],
) -> dict[str, Any]:

    classical_counts = Counter(
        row["classical_prediction"]
        for row in results
    )

    hybrid_counts = Counter(
        row["hybrid_decision"]
        for row in results
    )

    available_quantum = sum(
        row["quantum_prediction"] is not None
        for row in results
    )

    agreements = sum(
        row["model_agreement"] is True
        for row in results
    )

    disagreements = sum(
        row["model_agreement"] is False
        for row in results
    )

    return {
        "transactions_integrated": len(results),
        "classical_predictions": dict(
            classical_counts
        ),
        "quantum_results_available": available_quantum,
        "quantum_model_available": (
            quantum_metadata["available"]
        ),
        "hybrid_decisions": dict(hybrid_counts),
        "model_agreements": (
            agreements
            if quantum_metadata["available"]
            else None
        ),
        "model_disagreements": (
            disagreements
            if quantum_metadata["available"]
            else None
        ),
        "confirmed_attacks": None,
        "validated_model_accuracy": None,
        "validated_quantum_advantage": False,
    }


def save_results(
    results: list[dict[str, Any]],
    summary: dict[str, Any],
    feature_payload: dict[str, Any],
    classical_payload: dict[str, Any],
    quantum_metadata: dict[str, Any],
) -> None:

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "module": "AI–Quantum Threat Integration",
        "mode": "REAL_BLOCKCHAIN_RESEARCH_INTEGRATION",
        "generated_at": utc_now(),
        "network": "ethereum-mainnet",
        "source_block": (
            feature_payload["source_block"]
        ),
        "data_sources": {
            "transaction_features": FEATURE_FILE.name,
            "classical_model": CLASSICAL_FILE.name,
            "quantum_model": quantum_metadata,
        },
        "classical_model": (
            classical_payload.get("algorithm", {})
        ),
        "fusion_policy": (
            "If independently supplied predictions "
            "agree: use that classification. "
            "Otherwise: REVIEW. "
            "No hybrid decision when quantum "
            "model output is unavailable."
        ),
        "summary": summary,
        "transactions": results,
        "limitations": [
            "Real blockchain data from a small single-block sample.",
            "Classical model trained and scored on the same sample.",
            "Anomaly scores are not calibrated attack probabilities.",
            "Classical outliers are not confirmed attacks.",
            "No quantum computation is performed by this module.",
            "Optional quantum outputs require independent verification.",
            "A missing quantum model produces no fabricated scores.",
            "No model accuracy or real-world effectiveness is claimed.",
            "No blockchain or network action is performed.",
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
        writer.writerows(results)


def main() -> int:

    print()
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA V16.4")
    print("AI-QUANTUM THREAT INTEGRATION")
    print("=" * 70)

    try:

        (
            feature_payload,
            classical_payload,
            feature_rows,
            classical_rows,
        ) = validate_real_inputs()

        quantum_rows, quantum_metadata = (
            load_optional_quantum(
                expected_hashes=set(feature_rows),
                expected_block_hash=(
                    feature_payload["source_block"]["hash"]
                ),
            )
        )

        results = integrate(
            feature_rows,
            classical_rows,
            quantum_rows,
        )

        summary = summarize(
            results,
            quantum_metadata,
        )

        save_results(
            results,
            summary,
            feature_payload,
            classical_payload,
            quantum_metadata,
        )

    except (
        ValueError,
        TypeError,
        KeyError,
        OSError,
        json.JSONDecodeError,
    ) as error:

        print()
        print("V16.4 INTEGRATION FAILED")
        print(str(error))

        return 1

    print()
    print("REAL BLOCKCHAIN INTEGRATION SUMMARY")
    print("-" * 70)

    print(
        "Transactions integrated:",
        summary["transactions_integrated"],
    )

    print(
        "Classical anomaly predictions:",
        summary["classical_predictions"].get(
            "ANOMALY", 0
        ),
    )

    print(
        "Quantum results available:",
        summary["quantum_results_available"],
    )

    print(
        "Quantum model status:",
        quantum_metadata["status"],
    )

    print()
    print("HYBRID DECISION STATUS")
    print("-" * 70)

    if quantum_metadata["available"]:

        print(
            "Model agreements:",
            summary["model_agreements"],
        )

        print(
            "Model disagreements:",
            summary["model_disagreements"],
        )

    else:

        print(
            "PENDING: A quantum detector has not yet "
            "been executed on these Ethereum transactions."
        )

        print(
            "Classical results are preserved. "
            "No hybrid predictions were invented."
        )

    print()
    print("=" * 70)
    print("V16.4 AI-QUANTUM INTEGRATION COMPLETED")
    print("=" * 70)

    print()
    print("RESULTS SAVED TO:")
    print(JSON_OUTPUT)
    print(CSV_OUTPUT)

    print()
    print(
        "NOTE: Real blockchain data and actual "
        "classical model outputs were integrated. "
        "No quantum advantage or confirmed "
        "security incident is claimed."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
