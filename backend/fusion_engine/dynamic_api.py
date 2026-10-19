
"""
QUANTUM CYBER DEFENSE ARENA V7.4
Dynamic Hybrid Fusion Live API

Generates and analyzes synthetic blockchain events.
Classical Isolation Forest + Quantum State Fidelity.

RESEARCH SIMULATION ONLY.
No real blockchain transactions or verified attacks.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import APIRouter, FastAPI, HTTPException

from backend.threat_simulator import generate_threat
from backend.fusion_engine.dynamic_fusion import DynamicFusionEngine


logger = logging.getLogger("cyber_defense.dynamic_fusion")

router = APIRouter(
    prefix="/api/fusion/dynamic",
    tags=["Dynamic Hybrid Fusion V7.4"],
)

MAX_HISTORY = 100
UPDATE_INTERVAL_SECONDS = 3.0

history: deque[dict] = deque(maxlen=MAX_HISTORY)

_engine: DynamicFusionEngine | None = None
_worker: asyncio.Task | None = None
_last_error: str | None = None
_started_at: str | None = None


def get_engine() -> DynamicFusionEngine:
    global _engine

    if _engine is None:
        _engine = DynamicFusionEngine()

    return _engine


def generate_and_analyze() -> dict:
    event = generate_threat()
    return get_engine().analyze(event)


async def process_one_event() -> dict:
    global _last_error

    try:
        result = await asyncio.to_thread(generate_and_analyze)
        history.appendleft(result)
        _last_error = None
        return result
    except Exception as exc:
        _last_error = str(exc)
        logger.exception("Dynamic Fusion event processing failed")
        raise


async def worker_loop() -> None:
    while True:
        try:
            await process_one_event()
        except Exception:
            # Keep the research simulation alive after one
            # failed event. Error is available via /status.
            pass

        await asyncio.sleep(UPDATE_INTERVAL_SECONDS)


async def start_dynamic_fusion() -> None:
    global _worker, _started_at

    if _worker is not None and not _worker.done():
        return

    await asyncio.to_thread(get_engine)

    _started_at = datetime.now(timezone.utc).isoformat()
    _worker = asyncio.create_task(
        worker_loop(),
        name="dynamic_fusion_v74",
    )

    logger.info("Dynamic Fusion V7.4 worker started")


async def stop_dynamic_fusion() -> None:
    global _worker

    if _worker is None:
        return

    _worker.cancel()

    try:
        await _worker
    except asyncio.CancelledError:
        pass

    _worker = None

    logger.info("Dynamic Fusion V7.4 worker stopped")


def dynamic_status() -> dict:
    engine = get_engine()

    return {
        **engine.status(),
        "api_version": "7.4.0",
        "worker_running": (
            _worker is not None and not _worker.done()
        ),
        "update_interval_seconds": UPDATE_INTERVAL_SECONDS,
        "history_size": len(history),
        "started_at": _started_at,
        "last_error": _last_error,
    }


@router.get("/status")
def get_dynamic_status():
    return dynamic_status()


@router.get("/live")
def get_dynamic_live():
    engine = get_engine()

    return {
        "version": "7.4.0",
        "mode": "RESEARCH_SIMULATION",
        "status": "ONLINE"
        if _worker is not None and not _worker.done()
        else "STOPPED",
        "statistics": engine.status(),
        "total_events": engine.processed,
        "events": list(history)[:30],
        "last_error": _last_error,
    }


@router.get("/latest")
def get_latest_event():
    if not history:
        raise HTTPException(
            status_code=404,
            detail="No simulated Fusion events generated yet.",
        )

    return history[0]


@router.post("/generate")
async def generate_manual_event():
    try:
        result = await process_one_event()

        return {
            "status": "GENERATED",
            "mode": "RESEARCH_SIMULATION",
            "event": result,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Dynamic Fusion event generation failed.",
        ) from exc


def register_dynamic_fusion(app: FastAPI) -> None:
    """
    Register routes and hook the worker into the existing
    FastAPI lifespan without replacing its AI simulator.
    """

    app.include_router(router)
