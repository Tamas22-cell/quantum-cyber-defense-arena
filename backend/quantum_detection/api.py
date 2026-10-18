
"""
Quantum Cyber Defense Arena V6.4
Quantum Research REST API

Endpoints:
    GET /api/quantum/status
    GET /api/quantum/benchmark
    GET /api/quantum/statistics

Reads existing V6.2 and V6.3 research results.
Does not generate or invent benchmark data.

Research simulation only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/api/quantum",
    tags=["Quantum Research V6.4"],
)

BASE_DIR = Path(__file__).resolve().parent

BENCHMARK_FILE = BASE_DIR / "benchmark_v2_results.json"
STATISTICS_FILE = BASE_DIR / "statistical_analysis_results.json"


def load_json_file(path: Path) -> dict[str, Any]:
    """
    Load an existing research result file.

    Missing or invalid files return an API error instead
    of fabricated benchmark values.
    """

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Research results not found",
                "file": path.name,
                "message": (
                    "Run the corresponding V6 research "
                    "experiment first."
                ),
            },
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to read research results",
                "file": path.name,
                "reason": str(exc),
            },
        ) from exc

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Invalid research result format",
                "file": path.name,
            },
        )

    return data


@router.get("/status")
def quantum_status() -> dict[str, Any]:
    """
    Report the availability of saved research results.

    READY means both result files exist.
    This does not mean quantum hardware is running.
    """

    benchmark_available = BENCHMARK_FILE.is_file()
    statistics_available = STATISTICS_FILE.is_file()

    ready = benchmark_available and statistics_available

    return {
        "status": "READY" if ready else "INCOMPLETE",
        "engine": "Quantum Research V6.4",
        "mode": "RESEARCH_SIMULATION",
        "quantum_backend": "Qiskit Statevector",
        "quantum_hardware": False,
        "benchmark_available": benchmark_available,
        "statistics_available": statistics_available,
        "endpoints": [
            "/api/quantum/status",
            "/api/quantum/benchmark",
            "/api/quantum/statistics",
        ],
    }


@router.get("/benchmark")
def get_quantum_benchmark() -> dict[str, Any]:
    """
    Return actual saved V6.2 benchmark results.

    Includes model summaries and individual experiments.
    """

    data = load_json_file(BENCHMARK_FILE)

    if data.get("version") != "6.2":
        raise HTTPException(
            status_code=500,
            detail="Expected V6.2 benchmark results.",
        )

    if not isinstance(data.get("quantum"), dict):
        raise HTTPException(
            status_code=500,
            detail="Quantum benchmark data missing.",
        )

    if not isinstance(data.get("classical"), dict):
        raise HTTPException(
            status_code=500,
            detail="Classical benchmark data missing.",
        )

    return data


@router.get("/statistics")
def get_quantum_statistics() -> dict[str, Any]:
    """
    Return actual saved V6.3 statistical analysis.

    Includes paired tests, confidence intervals
    and runtime comparisons.
    """

    data = load_json_file(STATISTICS_FILE)

    if data.get("version") != "6.3":
        raise HTTPException(
            status_code=500,
            detail="Expected V6.3 statistical results.",
        )

    if not isinstance(data.get("f1_score"), dict):
        raise HTTPException(
            status_code=500,
            detail="F1 statistical analysis missing.",
        )

    if not isinstance(data.get("runtime"), dict):
        raise HTTPException(
            status_code=500,
            detail="Runtime statistics missing.",
        )

    return data
