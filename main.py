
import asyncio
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.threat_simulator import generate_threat


MAX_EVENTS = 100
events = deque(maxlen=MAX_EVENTS)
total_generated = 0
simulation_running = True


async def simulation_loop():
    global total_generated

    while True:
        if simulation_running:
            event = generate_threat()
            events.appendleft(event)
            total_generated += 1

        await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(simulation_loop())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Quantum Cyber Defense Arena",
    version="1.0.0",
    description="AI, Blockchain and Quantum Security Research",
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
        "mode": "SIMULATION",
        "version": "1.0.0",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "backend": "FastAPI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
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

    return {
        "mode": "simulation",
        "total_events": total_generated,
        "active_threats": active,
        "critical_events": critical,
        "average_risk": average,
        "events": recent[:30],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )
