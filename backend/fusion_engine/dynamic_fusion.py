
"""
QUANTUM CYBER DEFENSE ARENA V7.3
Dynamic Hybrid Quantum AI Fusion Engine

Generates changing synthetic blockchain events and analyzes
each event with the existing V7.2 Classical + Quantum API service.

Research simulation only.
Feature scaling is experimental, not production-calibrated.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.threat_simulator import generate_threat
from backend.fusion_engine.api import (
    FusionEvent,
    get_service,
)


ENGINE_VERSION = "7.3.0"

# Approximate scaling references for synthetic event telemetry.
# These values are research heuristics, not learned calibration.
SCALE_REFERENCES = {
    "transaction_value": 250_000.0,
    "transactions_per_minute": 850.0,
    "gas_spike_ratio": 12.0,
    "unique_counterparties": 350.0,
}


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def normalize_event(event: dict) -> FusionEvent:
    """
    Convert raw simulator telemetry into five normalized
    features required by the existing V7.2 FusionService.

    The quantum detector receives four of these five
    features through the existing FusionService.
    """

    return FusionEvent(
        event_id=str(event["id"]),
        network=str(event["network"]),
        transaction_value=clamp01(
            float(event["transaction_value"])
            / SCALE_REFERENCES["transaction_value"]
        ),
        transactions_per_minute=clamp01(
            float(event["transactions_per_minute"])
            / SCALE_REFERENCES["transactions_per_minute"]
        ),
        failed_transaction_ratio=clamp01(
            float(event["failed_transaction_ratio"])
        ),
        gas_spike_ratio=clamp01(
            float(event["gas_spike_ratio"])
            / SCALE_REFERENCES["gas_spike_ratio"]
        ),
        unique_counterparties=clamp01(
            float(event["unique_counterparties"])
            / SCALE_REFERENCES["unique_counterparties"]
        ),
    )


class DynamicFusionEngine:
    """
    Reuses one trained Classical AI model and one quantum
    Fusion Engine across multiple simulated events.
    """

    def __init__(self) -> None:
        self.service = get_service()
        self.processed = 0
        self.anomalies = 0
        self.reviews = 0
        self.model_disagreements = 0

    def analyze(self, event: dict) -> dict:
        normalized = normalize_event(event)

        fusion = self.service.analyze(normalized)

        self.processed += 1

        if fusion["classification"] == "ANOMALY":
            self.anomalies += 1

        if fusion["classification"] == "REVIEW":
            self.reviews += 1

        if not fusion["models_agree"]:
            self.model_disagreements += 1

        return {
            "version": ENGINE_VERSION,
            "mode": "RESEARCH_SIMULATION",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "event_id": event["id"],
            "network": event["network"],
            "event_type": event["type"],
            "simulation_label": event["simulation_label"],
            "original_risk_score": event["risk_score"],
            "raw_telemetry": {
                "transaction_value": event["transaction_value"],
                "transactions_per_minute": (
                    event["transactions_per_minute"]
                ),
                "failed_transaction_ratio": (
                    event["failed_transaction_ratio"]
                ),
                "gas_spike_ratio": event["gas_spike_ratio"],
                "unique_counterparties": (
                    event["unique_counterparties"]
                ),
            },
            "normalized_features": normalized.model_dump(),
            "fusion": fusion,
        }

    def status(self) -> dict:
        return {
            "version": ENGINE_VERSION,
            "status": "READY",
            "mode": "RESEARCH_SIMULATION",
            "processed_events": self.processed,
            "fusion_anomalies": self.anomalies,
            "review_events": self.reviews,
            "model_disagreements": self.model_disagreements,
        }


def run_simulation(count: int = 5, delay: float = 1.0) -> None:
    """
    Run a finite simulation test.

    Each generated event is passed to the existing V7.2
    classical and quantum models.
    """

    if count < 1:
        raise ValueError("Count must be at least 1.")

    if delay < 0:
        raise ValueError("Delay must not be negative.")

    print()
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA V7.3")
    print("DYNAMIC HYBRID QUANTUM AI FUSION")
    print("=" * 70)
    print("MODE: RESEARCH SIMULATION")
    print("Initializing Classical AI + Quantum Fusion...")

    engine = DynamicFusionEngine()

    print("Fusion Engine initialized.")
    print("Generating synthetic blockchain events...")

    results = []

    for index in range(count):
        event = generate_threat()
        result = engine.analyze(event)

        fusion = result["fusion"]

        results.append(result)

        print()
        print("-" * 70)
        print(f"EVENT {index + 1}/{count}")
        print("-" * 70)

        print("NETWORK:", result["network"])
        print("EVENT TYPE:", result["event_type"])
        print("SIMULATION LABEL:", result["simulation_label"])

        print(
            "CLASSICAL AI SCORE:",
            round(fusion["classical_score"] * 100, 2),
        )

        print(
            "QUANTUM AI SCORE:",
            round(fusion["quantum_score"] * 100, 2),
        )

        print(
            "HYBRID FUSION SCORE:",
            fusion["fusion_score_100"],
            "/100",
        )

        print(
            "CLASSIFICATION:",
            fusion["classification"],
        )

        print(
            "SEVERITY:",
            fusion["severity"],
        )

        print(
            "MODEL AGREEMENT:",
            fusion["models_agree"],
        )

        print(
            "DECISION STATUS:",
            fusion["decision_status"],
        )

        if index < count - 1 and delay > 0:
            time.sleep(delay)

    print()
    print("=" * 70)
    print("V7.3 DYNAMIC FUSION TEST COMPLETED")
    print("=" * 70)

    print()
    print("FINAL ENGINE STATUS:")
    print(
        json.dumps(
            engine.status(),
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("FULL JSON RESULTS:")
    print(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="V7.3 Dynamic Hybrid Fusion Research Test"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of simulated events (default: 5)",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds between events (default: 1)",
    )

    args = parser.parse_args()

    run_simulation(
        count=args.count,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
