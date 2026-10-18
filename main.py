
"""
Quantum Cyber Defense Arena
FastAPI Backend V3

Real-time simulated events with Isolation Forest inference.
Research only — no verified attacks.
"""

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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cyber_defense")

MAX_EVENTS = 100

events = deque(maxlen=MAX_EVENTS)
total_generated = 0

detector = AIThreatDetector(seed=42)


def initialize_ai() -> None:
    if not detector.trained:
        logger.info("Training Isolation Forest...")
        detector.train(generate_training_data())
        logger.info("AI Threat Detection V2 READY")


def analyze_event(event: dict) -> dict:
    """Return a new event with AI results attached."""
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

            elapsed = (perf_counter() - started) * 1000

            logger.debug(
                "Event processed in %.2f ms",
                elapsed,
            )

        except Exception:
            logger.exception("Simulation loop error")

        await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Quantum Cyber Defense Arena starting")

    await asyncio.to_thread(initialize_ai)

    task = asyncio.create_task(simulation_loop())

    try:
        yield
    finally:
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        logger.info("Quantum Cyber Defense Arena stopped")


app = FastAPI(
    title="Quantum Cyber Defense Arena",
    version="3.0.0",
    description=(
        "AI, Blockchain and Quantum Cybersecurity "
        "Research Platform"
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
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "project": "Quantum Cyber Defense Arena",
        "status": "ONLINE",
        "version": "3.0.0",
        "mode": "SIMULATION",
        "ai_engine": "Isolation Forest V2",
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
            sum(event["risk_score"] for event in recent)
            / len(recent),
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


# Register existing demonstration API before server startup.
from backend.ai_detection.api import router as ai_router

app.include_router(ai_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )
