
"""
Quantum Cyber Defense Arena
FastAPI Backend V10.3

Classical AI + Quantum Research + Hybrid Fusion
+ Dynamic Hybrid Fusion + Autonomous Investigation
+ Multi-Agent Threat Intelligence
+ Research Validation Lab

RESEARCH SIMULATION ONLY.
No verified real-world attacks.
"""

from __future__ import annotations

import asyncio
import logging

from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.threat_simulator import generate_threat

from backend.ai_detection.detector import (
    AIThreatDetector,
    generate_training_data,
)

from backend.ai_detection.api import (
    router as ai_router,
)

from backend.quantum_detection.api import (
    router as quantum_router,
)

from backend.fusion_engine.api import (
    router as fusion_router,
)

from backend.fusion_engine.dynamic_api import (
    register_dynamic_fusion,
    start_dynamic_fusion,
    stop_dynamic_fusion,
)

from backend.investigation_api import (
    router as investigation_router,
)

from backend.multi_agent_api import (
    register_multi_agent_routes,
)

from research_validation.api import (
    router as research_validation_router,
)


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("cyber_defense")

MAX_EVENTS = 100

events = deque(maxlen=MAX_EVENTS)

total_generated = 0

detector = AIThreatDetector(seed=42)


def initialize_ai() -> None:
    """Train the existing classical AI detector."""

    if not detector.trained:
        logger.info("Training Isolation Forest...")

        detector.train(generate_training_data())

        logger.info("AI Threat Detection V2 READY")


def analyze_event(event: dict) -> dict:
    """Attach classical AI results to a simulated event."""

    result = dict(event)

    try:
        prediction = detector.predict_event(result)

        result["ai_detection"] = prediction
        result["ai_is_anomaly"] = prediction["is_anomaly"]
        result["ai_anomaly_score"] = prediction["anomaly_score"]
        result["ai_classification"] = prediction["classification"]

    except Exception:
        logger.exception("AI inference failed")

        result["ai_detection"] = {
            "classification": "ERROR",
            "is_anomaly": None,
            "anomaly_score": None,
        }

        result["ai_is_anomaly"] = None
        result["ai_anomaly_score"] = None
        result["ai_classification"] = "ERROR"

    return result


async def simulation_loop() -> None:
    """Generate simulated security events every two seconds."""

    global total_generated

    while True:
        try:
            started = perf_counter()

            raw_event = generate_threat()

            analyzed_event = await asyncio.to_thread(
                analyze_event,
                raw_event,
            )

            events.appendleft(analyzed_event)

            total_generated += 1

            elapsed = (
                perf_counter() - started
            ) * 1000

            logger.debug(
                "Event processed in %.2f ms",
                elapsed,
            )

        except Exception:
            logger.exception("Simulation loop error")

        await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Start the existing classical AI simulator and
    the V7.4 Dynamic Hybrid Fusion worker.

    V8 and V9 consume existing events.
    V10.3 serves saved research results.
    """

    logger.info(
        "Quantum Cyber Defense Arena V10.3 starting"
    )

    await asyncio.to_thread(initialize_ai)

    simulation_task = asyncio.create_task(
        simulation_loop(),
        name="classical_ai_simulation",
    )

    try:
        await start_dynamic_fusion()

        logger.info(
            "Dynamic Hybrid Fusion V7.4 READY"
        )

        logger.info(
            "Autonomous Investigation API V8.2 READY"
        )

        logger.info(
            "Multi-Agent Threat Intelligence API V9.2 READY"
        )

        logger.info(
            "Research Validation API V10.3 READY"
        )

        yield

    finally:
        await stop_dynamic_fusion()

        simulation_task.cancel()

        try:
            await simulation_task
        except asyncio.CancelledError:
            pass

        logger.info(
            "Quantum Cyber Defense Arena stopped"
        )


app = FastAPI(
    title="Quantum Cyber Defense Arena",
    version="10.3.0",
    description=(
        "AI, Blockchain, Quantum Cybersecurity, "
        "Autonomous Threat Investigation, "
        "Multi-Agent Intelligence and "
        "Research Validation Platform"
    ),
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "OPTIONS",
    ],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "project": "Quantum Cyber Defense Arena",
        "status": "ONLINE",
        "version": "10.3.0",
        "mode": "SIMULATION",
        "ai_engine": "Isolation Forest V2",
        "quantum_engine": "Quantum State Fidelity",
        "fusion_engine": "Dynamic Hybrid Quantum AI Fusion",
        "investigation_engine": (
            "Autonomous Threat Investigator V8.2"
        ),
        "multi_agent_engine": (
            "Multi-Agent Threat Intelligence V9.2"
        ),
        "research_engine": "Research Validation V10.3",
        "agent_count": 3,
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "backend": "FastAPI",
        "ai_trained": detector.trained,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }


@app.get("/api/threats")
def get_threats():
    recent = list(events)

    active = sum(
        event["risk_score"] >= 60
        for event in recent
    )

    critical = sum(
        event["risk_score"] >= 80
        for event in recent
    )

    average = (
        round(
            sum(
                event["risk_score"]
                for event in recent
            ) / len(recent),
            1,
        )
        if recent
        else 0
    )

    ai_anomalies = sum(
        event.get("ai_is_anomaly") is True
        for event in recent
    )

    return {
        "mode": "simulation",
        "total_events": total_generated,
        "active_threats": active,
        "critical_events": critical,
        "average_risk": average,
        "ai_anomalies": ai_anomalies,
        "ai_engine": "IsolationForest",
        "events": recent[:30],
    }


@app.get("/api/ai/live")
def ai_live():
    recent = list(events)

    analyzed = [
        event
        for event in recent
        if event.get("ai_is_anomaly") is not None
    ]

    anomalies = [
        event
        for event in analyzed
        if event["ai_is_anomaly"] is True
    ]

    return {
        "status": "ONLINE",
        "mode": "SIMULATION",
        "model": "IsolationForest",
        "total_analyzed": len(analyzed),
        "anomalies_detected": len(anomalies),
        "model_statistics": detector.get_status(),
        "recent_anomalies": anomalies[:10],
    }


# V2 / V3 - Classical AI Threat Detection
app.include_router(ai_router)

# V6.4 - Quantum Research Dashboard
app.include_router(quantum_router)

# V7.2 - Hybrid Quantum AI Fusion
app.include_router(fusion_router)

# V7.4 - Dynamic Hybrid Fusion
register_dynamic_fusion(app)

# V8.2 - Autonomous Threat Investigation
app.include_router(investigation_router)

# V9.2 / V9.3 - Multi-Agent Threat Intelligence
register_multi_agent_routes(app)

# V10.3 - Research Validation Lab
app.include_router(research_validation_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )
