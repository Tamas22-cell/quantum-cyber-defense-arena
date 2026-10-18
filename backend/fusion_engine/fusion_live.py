
"""
QUANTUM CYBER DEFENSE ARENA V7.1
Classical Isolation Forest + Qiskit Quantum Fusion

Runs both existing detectors on the same synthetic events.

Classical detector: 5 features.
Quantum detector:   4 features.

This is an integration research test, not a production
security system or a calibrated attack probability.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.ai_detection.detector import (
    AIThreatDetector,
    FEATURE_NAMES,
)

from backend.fusion_engine.fusion_engine import (
    ClassicalPrediction,
    QuantumAIThreatFusionEngine,
)


CLASSICAL_FEATURES = tuple(FEATURE_NAMES)

QUANTUM_FEATURES = (
    "transaction_value",
    "transactions_per_minute",
    "failed_transaction_ratio",
    "gas_spike_ratio",
)


def normalize_classical_score(
    decision_function: float,
    temperature: float = 0.10,
) -> float:
    """
    Map Isolation Forest decision_function into [0, 1].

    Negative decisions mean greater anomaly evidence.

    Logistic mapping is a research heuristic,
    not a calibrated probability.
    """

    if temperature <= 0:
        raise ValueError("Temperature must be positive.")

    decision = float(decision_function)

    if not math.isfinite(decision):
        raise ValueError(
            "Isolation Forest returned a non-finite decision."
        )

    scaled = max(
        -60.0,
        min(60.0, decision / temperature),
    )

    return 1.0 / (1.0 + math.exp(scaled))


def validate_feature_mapping() -> None:
    """
    Check that both existing model feature sets
    can be constructed from the same event.
    """

    expected_classical = {
        "transaction_value",
        "transactions_per_minute",
        "failed_transaction_ratio",
        "gas_spike_ratio",
        "unique_counterparties",
    }

    if len(CLASSICAL_FEATURES) != 5:
        raise ValueError(
            "Expected five classical features, received: "
            f"{CLASSICAL_FEATURES}"
        )

    if set(CLASSICAL_FEATURES) != expected_classical:
        raise ValueError(
            "Unexpected Isolation Forest feature mapping: "
            f"{CLASSICAL_FEATURES}"
        )

    missing = [
        feature
        for feature in QUANTUM_FEATURES
        if feature not in CLASSICAL_FEATURES
    ]

    if missing:
        raise ValueError(
            "Quantum feature mapping missing: "
            f"{missing}"
        )


def create_training_data(
    rows: int = 800,
) -> np.ndarray:
    """
    Train the existing Isolation Forest with synthetic
    normal traffic for this integration test.
    """

    rng = np.random.default_rng(42)

    data = rng.normal(
        loc=0.20,
        scale=0.06,
        size=(rows, len(CLASSICAL_FEATURES)),
    )

    return np.clip(data, 0.0, 1.0)


def create_events() -> list[dict]:
    """
    Create events with all five classical features.

    Quantum analysis selects its four named features
    from each event.
    """

    return [
        {
            "id": "ETH-LIVE-001",
            "network": "Ethereum",
            "transaction_value": 0.16,
            "transactions_per_minute": 0.22,
            "failed_transaction_ratio": 0.04,
            "gas_spike_ratio": 0.12,
            "unique_counterparties": 0.20,
        },
        {
            "id": "POLY-LIVE-002",
            "network": "Polygon",
            "transaction_value": 0.95,
            "transactions_per_minute": 0.90,
            "failed_transaction_ratio": 0.85,
            "gas_spike_ratio": 0.95,
            "unique_counterparties": 0.95,
        },
        {
            "id": "BASE-LIVE-003",
            "network": "Base",
            "transaction_value": 0.45,
            "transactions_per_minute": 0.40,
            "failed_transaction_ratio": 0.38,
            "gas_spike_ratio": 0.50,
            "unique_counterparties": 0.45,
        },
    ]


def main() -> None:

    print()
    print("=" * 66)
    print("QUANTUM CYBER DEFENSE ARENA V7.1")
    print("CLASSICAL AI + QUANTUM MODEL INTEGRATION")
    print("=" * 66)

    validate_feature_mapping()

    print()
    print("CLASSICAL FEATURES:", len(CLASSICAL_FEATURES))
    print("QUANTUM FEATURES:", len(QUANTUM_FEATURES))

    print()
    print("Initializing Isolation Forest V2...")

    classical_detector = AIThreatDetector(seed=42)

    training_data = create_training_data()

    classical_detector.train(training_data)

    print("Isolation Forest trained on synthetic traffic.")

    print()
    print("Initializing Quantum Fusion Engine...")

    fusion_engine = QuantumAIThreatFusionEngine()

    events = create_events()

    results = []

    for event in events:

        event_id = event["id"]

        print()
        print("-" * 66)
        print("EVENT:", event_id)
        print("NETWORK:", event["network"])

        # ----------------------------------------------
        # 1. Actual classical Isolation Forest inference
        # ----------------------------------------------

        classical_result = (
            classical_detector.predict_event(event)
        )

        if (
            classical_result["classification"]
            == "INSUFFICIENT_DATA"
        ):
            print(
                "SKIPPED:",
                classical_result.get("missing_features"),
            )
            continue

        classical_score = normalize_classical_score(
            classical_result["decision_function"]
        )

        classical_prediction = ClassicalPrediction(
            anomaly_score=classical_score,
            is_anomaly=bool(
                classical_result["is_anomaly"]
            ),
            model="IsolationForest-V2",
        )

        # ----------------------------------------------
        # 2. Actual Qiskit quantum detector inference
        # ----------------------------------------------

        quantum_features = [
            float(event[name])
            for name in QUANTUM_FEATURES
        ]

        # ----------------------------------------------
        # 3. Hybrid model fusion
        # ----------------------------------------------

        fusion_result = fusion_engine.analyze(
            event_id=event_id,
            network=event["network"],
            features=quantum_features,
            classical_prediction=classical_prediction,
        )

        record = fusion_result.to_dict()

        record["classical_decision_function"] = (
            classical_result["decision_function"]
        )

        record["classical_raw_anomaly_score"] = (
            classical_result["anomaly_score"]
        )

        record["classical_feature_count"] = len(
            CLASSICAL_FEATURES
        )

        record["quantum_feature_count"] = len(
            QUANTUM_FEATURES
        )

        record["training_mode"] = (
            "SYNTHETIC_CLASSICAL_TRAINING"
        )

        results.append(record)

        print(
            "CLASSICAL DECISION:",
            classical_result["classification"],
        )

        print(
            "CLASSICAL SCORE:",
            round(classical_score, 6),
        )

        print(
            "QUANTUM SCORE:",
            record["quantum_score"],
        )

        print(
            "FUSION SCORE:",
            record["fusion_score_100"],
            "/100",
        )

        print(
            "FUSION CLASSIFICATION:",
            record["classification"],
        )

        print(
            "SEVERITY:",
            record["severity"],
        )

        print(
            "MODEL AGREEMENT:",
            record["models_agree"],
        )

        print(
            "DECISION STATUS:",
            record["decision_status"],
        )

    print()
    print("=" * 66)
    print("V7.1 LIVE MODEL INTEGRATION TEST COMPLETED")
    print("=" * 66)

    print()
    print("JSON RESULTS:")
    print(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
