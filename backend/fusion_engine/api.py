
"""
QUANTUM CYBER DEFENSE ARENA V7.2
Hybrid Quantum AI Fusion API

Research simulation only.
Scores are experimental risk indicators,
not calibrated attack probabilities.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.ai_detection.detector import AIThreatDetector, FEATURE_NAMES
from backend.fusion_engine.fusion_engine import (
    ClassicalPrediction,
    QuantumAIThreatFusionEngine,
)

router = APIRouter(prefix="/api/fusion", tags=["Hybrid Quantum AI Fusion"])

CLASSICAL_FEATURES = tuple(FEATURE_NAMES)

QUANTUM_FEATURES = (
    "transaction_value",
    "transactions_per_minute",
    "failed_transaction_ratio",
    "gas_spike_ratio",
)

EXPECTED_CLASSICAL_FEATURES = set(QUANTUM_FEATURES) | {
    "unique_counterparties",
}


class FusionEvent(BaseModel):
    event_id: str = Field(min_length=1)
    network: str = Field(min_length=1)
    transaction_value: float = Field(ge=0, le=1)
    transactions_per_minute: float = Field(ge=0, le=1)
    failed_transaction_ratio: float = Field(ge=0, le=1)
    gas_spike_ratio: float = Field(ge=0, le=1)
    unique_counterparties: float = Field(ge=0, le=1)


def normalize_classical_score(
    decision_function: float,
    temperature: float = 0.10,
) -> float:
    if temperature <= 0:
        raise ValueError("Temperature must be positive.")

    decision = float(decision_function)

    if not math.isfinite(decision):
        raise ValueError("Non-finite classical decision.")

    scaled = max(-60.0, min(60.0, decision / temperature))
    return 1.0 / (1.0 + math.exp(scaled))


def create_training_data(rows: int = 800) -> np.ndarray:
    rng = np.random.default_rng(42)
    data = rng.normal(
        loc=0.20,
        scale=0.06,
        size=(rows, len(CLASSICAL_FEATURES)),
    )
    return np.clip(data, 0.0, 1.0)


class FusionService:
    def __init__(self) -> None:
        if (
            len(CLASSICAL_FEATURES) != 5
            or set(CLASSICAL_FEATURES) != EXPECTED_CLASSICAL_FEATURES
        ):
            raise ValueError(
                f"Unexpected classical feature mapping: {CLASSICAL_FEATURES}"
            )

        self.classical = AIThreatDetector(seed=42)
        self.classical.train(create_training_data())
        self.fusion = QuantumAIThreatFusionEngine()

    def analyze(self, event: FusionEvent) -> dict:
        event_data = event.model_dump()

        classical_result = self.classical.predict_event(event_data)

        if classical_result["classification"] == "INSUFFICIENT_DATA":
            raise ValueError("Missing classical model features.")

        classical_prediction = ClassicalPrediction(
            anomaly_score=normalize_classical_score(
                classical_result["decision_function"]
            ),
            is_anomaly=bool(classical_result["is_anomaly"]),
            model="IsolationForest-V2",
        )

        quantum_features = [
            float(event_data[name]) for name in QUANTUM_FEATURES
        ]

        result = self.fusion.analyze(
            event_id=event.event_id,
            network=event.network,
            features=quantum_features,
            classical_prediction=classical_prediction,
        )

        return {
            **result.to_dict(),
            "classical_feature_count": len(CLASSICAL_FEATURES),
            "quantum_feature_count": len(QUANTUM_FEATURES),
            "training_mode": "SYNTHETIC_CLASSICAL_TRAINING",
        }


_service: FusionService | None = None


def get_service() -> FusionService:
    global _service
    if _service is None:
        _service = FusionService()
    return _service


DEMO_EVENTS = [
    FusionEvent(
        event_id="ETH-LIVE-001",
        network="Ethereum",
        transaction_value=0.16,
        transactions_per_minute=0.22,
        failed_transaction_ratio=0.04,
        gas_spike_ratio=0.12,
        unique_counterparties=0.20,
    ),
    FusionEvent(
        event_id="POLY-LIVE-002",
        network="Polygon",
        transaction_value=0.95,
        transactions_per_minute=0.90,
        failed_transaction_ratio=0.85,
        gas_spike_ratio=0.95,
        unique_counterparties=0.95,
    ),
    FusionEvent(
        event_id="BASE-LIVE-003",
        network="Base",
        transaction_value=0.45,
        transactions_per_minute=0.40,
        failed_transaction_ratio=0.38,
        gas_spike_ratio=0.50,
        unique_counterparties=0.45,
    ),
]


@router.get("/status")
def fusion_status():
    return {
        "status": "READY",
        "version": "7.2",
        "classical_features": len(CLASSICAL_FEATURES),
        "quantum_features": len(QUANTUM_FEATURES),
        "mode": "RESEARCH_SIMULATION",
    }


@router.get("/demo")
def fusion_demo():
    try:
        service = get_service()
        return {
            "version": "7.2",
            "mode": "RESEARCH_SIMULATION",
            "results": [
                service.analyze(event) for event in DEMO_EVENTS
            ],
        }
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/analyze")
def fusion_analyze(event: FusionEvent):
    try:
        return get_service().analyze(event)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
