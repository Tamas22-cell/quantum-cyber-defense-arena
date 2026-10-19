
"""
QUANTUM CYBER DEFENSE ARENA V9.2
MULTI-AGENT LIVE API

Connects the V9.1 multi-agent research engine
to existing V7.4 Dynamic Hybrid Fusion events.

Agents:
    1. Threat Analysis Agent
    2. Investigation Agent
    3. Reporting Agent

Endpoints:
    GET /api/agents/status
    GET /api/agents/live
    GET /api/agents/latest
    GET /api/agents/event/{event_id}

RESEARCH SIMULATION ONLY.

This is a deterministic rule-based multi-agent system.
No external LLM or automatic defensive actions.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.multi_agent import MultiAgentCyberDefenseEngine
from backend.fusion_engine import dynamic_api


logger = logging.getLogger("cyber_defense.multi_agent")

router = APIRouter(
    prefix="/api/agents",
    tags=["Multi-Agent Cyber Defense V9.2"],
)

ENGINE_VERSION = "9.2.0"
MODE = "RESEARCH_SIMULATION"

_engine: MultiAgentCyberDefenseEngine | None = None

# Cache reports by source event ID so repeated polling
# does not count the same event multiple times.
_report_cache: dict[str, dict[str, Any]] = {}

MAX_CACHE = 500


def get_engine() -> MultiAgentCyberDefenseEngine:
    global _engine

    if _engine is None:
        _engine = MultiAgentCyberDefenseEngine()

    return _engine


def get_source_events() -> list[dict[str, Any]]:
    """
    Return the events buffered by the existing V7.4 worker.

    Does not create another generator or replace the
    currently running backend simulation.
    """
    return list(dynamic_api.history)


def identify_event(event: dict[str, Any]) -> str:
    value = event.get("event_id") or event.get("id")

    if value is None:
        raise ValueError(
            "Dynamic Fusion event has no identifier."
        )

    return str(value)


def analyze_events(
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Process unseen events once.

    Previously generated reports are retrieved from cache.
    """
    engine = get_engine()
    reports: list[dict[str, Any]] = []

    for event in events:
        event_id = identify_event(event)

        if event_id not in _report_cache:
            report = engine.analyze(event).to_dict()
            _report_cache[event_id] = report

        reports.append(_report_cache[event_id])

    # Keep a bounded report cache.
    if len(_report_cache) > MAX_CACHE:
        excess = len(_report_cache) - MAX_CACHE

        for old_id in list(_report_cache)[:excess]:
            del _report_cache[old_id]

    return reports


def build_status() -> dict[str, Any]:
    engine = get_engine()

    worker_running = (
        dynamic_api._worker is not None
        and not dynamic_api._worker.done()
    )

    return {
        "version": ENGINE_VERSION,
        "status": (
            "ONLINE" if worker_running else "WAITING"
        ),
        "mode": MODE,
        "agent_count": 3,
        "agents": [
            "Threat Analysis Agent",
            "Investigation Agent",
            "Reporting Agent",
        ],
        "source": "Dynamic Hybrid Fusion V7.4",
        "source_worker_running": worker_running,
        "source_buffer_size": len(dynamic_api.history),
        "cached_reports": len(_report_cache),
        "engine_statistics": engine.status(),
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }


@router.get("/status")
def multi_agent_status():
    return build_status()


@router.get("/live")
async def multi_agent_live(
    limit: int = Query(default=20, ge=1, le=100),
    include_normal: bool = Query(default=False),
):
    """
    Return multi-agent reports for recent dynamic events.

    The source produces simulated blockchain events
    periodically. This endpoint does not claim to
    analyze real transactions.
    """

    try:
        source_events = get_source_events()

        # Run CPU-bound report generation away from
        # the FastAPI event loop.
        reports = await asyncio.to_thread(
            analyze_events,
            source_events,
        )

        if not include_normal:
            reports = [
                report
                for report in reports
                if report["classification"] != "NORMAL"
            ]

        selected = reports[:limit]

        return {
            "version": ENGINE_VERSION,
            "mode": MODE,
            "status": "ONLINE",
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "total_available": len(source_events),
            "report_count": len(selected),
            "agent_count": 3,
            "reports": selected,
            "statistics": get_engine().status(),
        }

    except (ValueError, RuntimeError) as exc:
        logger.exception(
            "Multi-agent live analysis failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get("/latest")
async def multi_agent_latest():
    """
    Return the newest source event's multi-agent report.
    """

    source_events = get_source_events()

    if not source_events:
        raise HTTPException(
            status_code=404,
            detail="No dynamic events available yet.",
        )

    try:
        reports = await asyncio.to_thread(
            analyze_events,
            source_events[:1],
        )

        return reports[0]

    except (ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get("/event/{event_id}")
async def multi_agent_event(event_id: str):
    """
    Find and analyze a specific buffered event.
    """

    if event_id in _report_cache:
        return _report_cache[event_id]

    source_events = get_source_events()

    matching = [
        event
        for event in source_events
        if (
            event.get("event_id") == event_id
            or event.get("id") == event_id
        )
    ]

    if not matching:
        raise HTTPException(
            status_code=404,
            detail=(
                "Event not found in the current "
                "simulation buffer."
            ),
        )

    try:
        reports = await asyncio.to_thread(
            analyze_events,
            matching[:1],
        )

        return reports[0]

    except (ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


def register_multi_agent_routes(app) -> None:
    """
    Register V9.2 endpoints without replacing
    the existing FastAPI lifespan or routers.
    """
    app.include_router(router)


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("QUANTUM CYBER DEFENSE ARENA V9.2")
    print("MULTI-AGENT LIVE API")
    print("=" * 60)
    print()
    print("Engine:", get_engine().status())
    print()
    print("API routes:")
    for route in router.routes:
        print(
            getattr(route, "path", "UNKNOWN")
        )
    print()
    print("V9.2 API MODULE READY")
