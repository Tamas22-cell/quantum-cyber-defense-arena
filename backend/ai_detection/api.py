
from functools import lru_cache

import numpy as np
from fastapi import APIRouter

from backend.ai_detection.detector import (
    AIThreatDetector,
    generate_training_data,
)

router = APIRouter(prefix="/api/ai", tags=["AI Detection"])


@lru_cache(maxsize=1)
def get_detector() -> AIThreatDetector:
    detector = AIThreatDetector(seed=42)
    detector.train(generate_training_data(count=2000, seed=42))
    return detector


@router.get("/status")
def ai_status():
    detector = get_detector()

    return {
        "status": "ONLINE" if detector.trained else "OFFLINE",
        "model": "IsolationForest",
        "trained": detector.trained,
        "mode": "SIMULATION",
    }


@router.get("/demo")
def ai_demo():
    detector = get_detector()

    normal = np.array([55.0, 12.0, 0.04, 1.05, 8.0])
    suspicious = np.array(
        [250000.0, 850.0, 0.91, 12.0, 350.0]
    )

    return {
        "mode": "SIMULATION",
        "normal": detector.predict(normal),
        "suspicious": detector.predict(suspicious),
    }
