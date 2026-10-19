
"""
QUANTUM CYBER DEFENSE ARENA V8.1
Live Autonomous Threat Investigation API

Investigates existing V7.4 synthetic Fusion events.
Rule-based research prototype, not real incident detection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.autonomous_investigation import (
    AutonomousThreatInvestigator,
)
from backend.fusion_engine import dynamic_api


router = APIRouter(
    prefix="/api/investigation",
    tags=["Autonomous Threat Investigation V8.1"],
)

investigator = AutonomousThreatInvestigator()


def get_event_id(event: dict[str, Any]) -> str:
    return str(
        event.get("event_id")
        or event.get("id")
        or "UNKNOWN"
    )


def investigate_recent_events(
    limit: int = 30,
    include_normal: bool = False,
) -> dict[str, Any]:
    """
    Read the existing V7.4 Fusion event history and
    generate deterministic investigation reports.

    No duplicate background worker is started here.
    """
    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100.")

    available_events = list(dynamic_api.history)

    if not available_events:
        return {
            "version": "8.1.0",
            "mode": "RESEARCH_SIMULATION",
            "status": "WAITING_FOR_EVENTS",
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "total_available": 0,
            "investigated": 0,
            "investigations": [],
        }

    selected_events = []

    for event in available_events:
        classification = str(
            event.get("classification", "")
        ).upper()

        if include_normal or classification in {
            "ANOMALY",
            "REVIEW",
        }:
            selected_events.append(event)

        if len(selected_events) >= limit:
            break

    reports = [
        investigator.investigate(event)
        for event in selected_events
    ]

    return {
        "version": "8.1.0",
        "mode": "RESEARCH_SIMULATION",
        "status": "ONLINE",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_available": len(available_events),
        "investigated": len(reports),
        "investigations": reports,
    }


@router.get("/status")
def investigation_status() -> dict:
    return {
        "version": "8.1.0",
        "status": "READY",
        "mode": "RESEARCH_SIMULATION",
        "source": "V7.4 DYNAMIC FUSION",
        "source_worker_running": (
            dynamic_api._worker is not None
            and not dynamic_api._worker.done()
        ),
        "available_events": len(dynamic_api.history),
    }


@router.get("/live")
def investigation_live(
    limit: int = 30,
    include_normal: bool = False,
) -> dict:
    try:
        return investigate_recent_events(
            limit=limit,
            include_normal=include_normal,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/latest")
def investigation_latest() -> dict:
    for event in dynamic_api.history:
        classification = str(
            event.get("classification", "")
        ).upper()

        if classification in {"ANOMALY", "REVIEW"}:
            return investigator.investigate(event)

    raise HTTPException(
        status_code=404,
        detail="No suspicious simulated events available.",
    )


@router.get("/event/{event_id}")
def investigation_by_event(event_id: str) -> dict:
    for event in dynamic_api.history:
        if get_event_id(event) == event_id:
            return investigator.investigate(event)

    raise HTTPException(
        status_code=404,
        detail="Simulated event not found in recent history.",
    )
