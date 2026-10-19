
"""
QUANTUM CYBER DEFENSE ARENA V10.3
Research Validation Results API

Serves existing V10.1 and V10.2 research results.
Read-only API. Does not rerun benchmarks.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

ROOT = Path(__file__).resolve().parents[1]
RESEARCH_DIR = ROOT / "research_validation"

router = APIRouter(
    prefix="/api/research",
    tags=["Research Validation V10.3"],
)

RESULT_FILES = {
    "v10-1": "benchmark_v10_1_results.json",
    "v10-2": "statistical_validation_v10_2_results.json",
}


def load_result(key: str) -> dict[str, Any]:
    filename = RESULT_FILES.get(key)

    if filename is None:
        raise HTTPException(
            status_code=404,
            detail="Unknown research result.",
        )

    path = RESEARCH_DIR / filename

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Research results not found: {filename}",
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            result = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to read research results.",
        ) from exc

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid research results format.",
        )

    return result


@router.get("/status")
def research_status():
    return {
        "status": "READY",
        "version": "10.3.0",
        "mode": "RESEARCH_SIMULATION",
        "results_available": {
            key: (RESEARCH_DIR / filename).is_file()
            for key, filename in RESULT_FILES.items()
        },
    }


@router.get("/v10-1")
def research_benchmark_v10_1():
    return load_result("v10-1")


@router.get("/v10-2")
def research_statistics_v10_2():
    return load_result("v10-2")
