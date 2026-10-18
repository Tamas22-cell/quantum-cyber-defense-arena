
"""
QUANTUM CYBER DEFENSE ARENA V7
Quantum AI Threat Fusion Engine

Combines:
    - Classical AI anomaly detection
    - Quantum State Fidelity Detector
    - Hybrid fusion risk assessment

Capabilities:
    - Quantum anomaly scoring
    - Classical AI score integration
    - Weighted fusion score
    - Model agreement/disagreement detection
    - Threat severity classification
    - Explainable decision summary
    - JSON-compatible results

RESEARCH SIMULATION ONLY.

The quantum algorithm runs on a classical statevector
simulator. Scores are experimental and are not calibrated
probabilities of a real attack.
"""

from __future__ import annotations

import json
import math
import sys

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


# Allow direct execution from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.quantum_detection.quantum_detector import (
    QuantumAnomalyDetector,
)


# ============================================================
# CONFIGURATION
# ============================================================

ENGINE_VERSION = "7.0.0"

CLASSICAL_WEIGHT = 0.50
QUANTUM_WEIGHT = 0.50

CLASSICAL_THRESHOLD = 0.50
QUANTUM_THRESHOLD = 0.35
FUSION_THRESHOLD = 0.50

FEATURE_NAMES = (
    "transaction_value",
    "transactions_per_minute",
    "failed_transaction_ratio",
    "gas_spike_ratio",
)


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class ClassicalPrediction:
    """
    Classical model output supplied by a caller.

    anomaly_score must already be normalized to [0, 1].

    It is NOT the raw Isolation Forest decision_function.
    """

    anomaly_score: float
    is_anomaly: bool
    model: str = "IsolationForest"


@dataclass
class FusionResult:
    engine: str
    version: str
    mode: str

    event_id: str
    network: str

    classical_model: str
    classical_score: float
    classical_anomaly: bool

    quantum_model: str
    quantum_score: float
    quantum_similarity: float
    quantum_anomaly: bool

    fusion_score: float
    fusion_score_100: float

    classification: str
    severity: str

    models_agree: bool
    decision_status: str
    explanation: str

    classical_weight: float
    quantum_weight: float

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# VALIDATION
# ============================================================

def validate_score(value: float, name: str) -> float:
    """Validate a normalized score."""

    value = float(value)

    if not math.isfinite(value):
        raise ValueError(
            f"{name} must be finite."
        )

    if not 0.0 <= value <= 1.0:
        raise ValueError(
            f"{name} must be between 0 and 1."
        )

    return value


def severity_from_score(score: float) -> str:
    """Convert an experimental fusion score to severity."""

    if score >= 0.85:
        return "CRITICAL"

    if score >= 0.65:
        return "HIGH"

    if score >= 0.40:
        return "MEDIUM"

    return "LOW"


# ============================================================
# FUSION ENGINE
# ============================================================

class QuantumAIThreatFusionEngine:
    """
    Research prototype combining classical and quantum
    anomaly detection.

    Classical output is supplied by the caller so that
    this module does not retrain or duplicate the existing
    AI Threat Detection V2 model.
    """

    def __init__(
        self,
        classical_weight: float = CLASSICAL_WEIGHT,
        quantum_weight: float = QUANTUM_WEIGHT,
    ) -> None:

        classical_weight = validate_score(
            classical_weight,
            "classical_weight",
        )

        quantum_weight = validate_score(
            quantum_weight,
            "quantum_weight",
        )

        total_weight = classical_weight + quantum_weight

        if total_weight <= 0.0:
            raise ValueError(
                "At least one model weight must be positive."
            )

        self.classical_weight = (
            classical_weight / total_weight
        )

        self.quantum_weight = (
            quantum_weight / total_weight
        )

        self.quantum_detector = QuantumAnomalyDetector(
            threshold=QUANTUM_THRESHOLD,
        )

    def analyze(
        self,
        event_id: str,
        network: str,
        features: Sequence[float],
        classical_prediction: ClassicalPrediction,
    ) -> FusionResult:
        """
        Analyze one simulated blockchain event.

        features:
            Four normalized transaction features [0, 1].

        classical_prediction:
            Existing classical AI result, whose score
            has been mapped to [0, 1] by the caller.
        """

        classical_score = validate_score(
            classical_prediction.anomaly_score,
            "classical_anomaly_score",
        )

        # ----------------------------------------------
        # Quantum analysis
        # ----------------------------------------------

        quantum_result = self.quantum_detector.detect(
            features
        )

        quantum_score = validate_score(
            quantum_result.anomaly_score,
            "quantum_anomaly_score",
        )

        quantum_anomaly = (
            quantum_result.classification == "ANOMALY"
        )

        # ----------------------------------------------
        # Classical analysis
        # ----------------------------------------------

        classical_anomaly = bool(
            classical_prediction.is_anomaly
        )

        # ----------------------------------------------
        # Weighted score fusion
        # ----------------------------------------------

        fusion_score = (
            classical_score * self.classical_weight
            + quantum_score * self.quantum_weight
        )

        fusion_score = max(
            0.0,
            min(1.0, fusion_score),
        )

        fusion_score_100 = fusion_score * 100.0

        # ----------------------------------------------
        # Agreement analysis
        # ----------------------------------------------

        models_agree = (
            classical_anomaly == quantum_anomaly
        )

        if classical_anomaly and quantum_anomaly:
            decision_status = "BOTH_DETECTED"

        elif not classical_anomaly and not quantum_anomaly:
            decision_status = "BOTH_NORMAL"

        elif classical_anomaly:
            decision_status = "CLASSICAL_ONLY"

        else:
            decision_status = "QUANTUM_ONLY"

        # ----------------------------------------------
        # Final decision
        # ----------------------------------------------

        if models_agree:
            if classical_anomaly:
                classification = "ANOMALY"
                explanation = (
                    "Both classical AI and quantum detector "
                    "flagged this simulated event."
                )

            else:
                classification = "NORMAL"
                explanation = (
                    "Both detectors classified this "
                    "simulated event as normal."
                )

        else:
            # Avoid presenting disagreement as certainty.
            classification = "REVIEW"

            explanation = (
                "Classical and quantum model decisions "
                "disagree. Manual or additional automated "
                "analysis is recommended."
            )

        # Combined score is used to rank events for review.
        # It does not override a disagreement.
        severity = severity_from_score(
            fusion_score
        )

        return FusionResult(
            engine="Quantum AI Threat Fusion Engine",
            version=ENGINE_VERSION,
            mode="RESEARCH_SIMULATION",

            event_id=str(event_id),
            network=str(network),

            classical_model=classical_prediction.model,
            classical_score=round(classical_score, 6),
            classical_anomaly=classical_anomaly,

            quantum_model="Quantum State Fidelity",
            quantum_score=round(quantum_score, 6),
            quantum_similarity=round(
                quantum_result.similarity,
                6,
            ),
            quantum_anomaly=quantum_anomaly,

            fusion_score=round(fusion_score, 6),
            fusion_score_100=round(
                fusion_score_100,
                2,
            ),

            classification=classification,
            severity=severity,

            models_agree=models_agree,
            decision_status=decision_status,
            explanation=explanation,

            classical_weight=self.classical_weight,
            quantum_weight=self.quantum_weight,
        )

    def analyze_batch(
        self,
        events: list[dict],
    ) -> list[dict]:
        """Analyze a list of events with supplied AI outputs."""

        results = []

        for event in events:

            prediction = ClassicalPrediction(
                anomaly_score=event["classical_score"],
                is_anomaly=event["classical_anomaly"],
                model=event.get(
                    "classical_model",
                    "IsolationForest",
                ),
            )

            result = self.analyze(
                event_id=event["event_id"],
                network=event["network"],
                features=event["features"],
                classical_prediction=prediction,
            )

            results.append(result.to_dict())

        return results


# ============================================================
# DEMONSTRATION
# ============================================================

def main() -> None:

    print()
    print("=" * 66)
    print("QUANTUM CYBER DEFENSE ARENA V7")
    print("QUANTUM AI THREAT FUSION ENGINE")
    print("=" * 66)

    engine = QuantumAIThreatFusionEngine()

    # These classical scores are illustrative mock outputs.
    # They are not generated by the live Isolation Forest.
    demo_events = [
        {
            "event_id": "ETH-NORMAL-001",
            "network": "Ethereum",
            "features": [0.16, 0.22, 0.04, 0.12],
            "classical_score": 0.08,
            "classical_anomaly": False,
            "classical_model": "SIMULATED_CLASSICAL_OUTPUT",
        },
        {
            "event_id": "POLY-CRITICAL-002",
            "network": "Polygon",
            "features": [0.95, 0.90, 0.85, 0.95],
            "classical_score": 0.94,
            "classical_anomaly": True,
            "classical_model": "SIMULATED_CLASSICAL_OUTPUT",
        },
        {
            "event_id": "BASE-REVIEW-003",
            "network": "Base",
            "features": [0.95, 0.90, 0.85, 0.95],
            "classical_score": 0.12,
            "classical_anomaly": False,
            "classical_model": "SIMULATED_CLASSICAL_OUTPUT",
        },
    ]

    results = engine.analyze_batch(demo_events)

    for result in results:

        print()
        print("-" * 66)

        print("EVENT:", result["event_id"])
        print("NETWORK:", result["network"])

        print(
            "CLASSICAL SCORE:",
            result["classical_score"],
        )

        print(
            "QUANTUM SCORE:",
            result["quantum_score"],
        )

        print(
            "FUSION SCORE:",
            result["fusion_score_100"],
            "/100",
        )

        print(
            "CLASSIFICATION:",
            result["classification"],
        )

        print("SEVERITY:", result["severity"])

        print(
            "AGREEMENT:",
            result["models_agree"],
        )

        print(
            "DECISION:",
            result["decision_status"],
        )

        print(
            "EXPLANATION:",
            result["explanation"],
        )

    print()
    print("=" * 66)
    print("QUANTUM AI FUSION TEST COMPLETED")
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
