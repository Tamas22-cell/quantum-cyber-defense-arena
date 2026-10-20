
"""
QUANTUM CYBER DEFENSE ARENA
V15.1 - INTELLIGENT THREAT ORCHESTRATOR

Research prototype:
- Classical AI decision input
- Quantum AI decision input
- Hybrid Fusion
- Confidence and disagreement analysis
- Threat prioritization
- Explainable security recommendations
- JSON research report

The standalone demonstration uses synthetic scores.
It does not execute trained AI models or Qiskit.

No real security actions are performed.
"""

from __future__ import annotations

import json
import random
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


VERSION = "15.1.0"

HERE = Path(__file__).resolve().parent

OUTPUT_FILE = HERE / "threat_orchestrator_v15_1_results.json"

SEED = 151
EVENT_COUNT = 30

NETWORKS = (
    "Ethereum",
    "Polygon",
    "Arbitrum",
    "Base",
)

EVENT_TYPES = (
    "LARGE_TOKEN_TRANSFER",
    "UNUSUAL_TRANSACTION_FREQUENCY",
    "SMART_CONTRACT_ANOMALY",
    "WALLET_BEHAVIOR_ANOMALY",
    "FAILED_TRANSACTION_SPIKE",
)

Decision = Literal["NORMAL", "REVIEW", "ANOMALY"]
Priority = Literal["P1", "P2", "P3", "P4"]


@dataclass
class ThreatEvent:
    event_id: str
    network: str
    event_type: str
    classical_score: float
    quantum_score: float
    timestamp: str


@dataclass
class OrchestratorResult:
    event_id: str
    network: str
    event_type: str

    classical_score: float
    quantum_score: float
    fusion_score: float

    classical_decision: str
    quantum_decision: str
    hybrid_decision: str

    model_agreement: bool
    confidence: float
    risk_score: int

    priority: str
    severity: str

    recommended_action: str
    explanation: str

    mode: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def classify(score: float, threshold: float) -> str:
    return "ANOMALY" if score >= threshold else "NORMAL"


class IntelligentThreatOrchestrator:
    """
    Coordinates outputs of two detection systems.

    Standalone V15.1 accepts normalized model scores.

    Both scores must be between 0 and 1:
        0 = low anomaly indication
        1 = high anomaly indication

    The thresholds and fusion policy are experimental.
    """

    def __init__(
        self,
        classical_threshold: float = 0.55,
        quantum_threshold: float = 0.55,
        classical_weight: float = 0.50,
    ):
        if not 0 < classical_threshold < 1:
            raise ValueError("Invalid classical threshold.")

        if not 0 < quantum_threshold < 1:
            raise ValueError("Invalid quantum threshold.")

        if not 0 <= classical_weight <= 1:
            raise ValueError("Invalid fusion weight.")

        self.classical_threshold = classical_threshold
        self.quantum_threshold = quantum_threshold

        self.classical_weight = classical_weight
        self.quantum_weight = 1.0 - classical_weight

    def calculate_confidence(
        self,
        classical_score: float,
        quantum_score: float,
        agreement: bool,
    ) -> float:
        """
        Heuristic agreement-confidence indicator.

        This is NOT a calibrated probability
        that the detection is correct.
        """

        distance = abs(
            classical_score - quantum_score
        )

        if agreement:
            confidence = 1.0 - distance * 0.5
        else:
            confidence = 0.5 * (1.0 - distance)

        return round(clamp(confidence), 4)

    @staticmethod
    def calculate_priority(
        decision: str,
        risk_score: int,
    ) -> tuple[str, str]:
        if decision == "ANOMALY":
            if risk_score >= 80:
                return "P1", "CRITICAL"

            return "P2", "HIGH"

        if decision == "REVIEW":
            return "P3", "MEDIUM"

        return "P4", "LOW"

    @staticmethod
    def recommend_action(
        decision: str,
        priority: str,
    ) -> str:
        if priority == "P1":
            return (
                "Escalate simulated incident for "
                "immediate analyst investigation."
            )

        if priority == "P2":
            return (
                "Queue simulated high-risk incident "
                "for analyst review."
            )

        if decision == "REVIEW":
            return (
                "Request manual review because "
                "the detection models disagree."
            )

        return (
            "Continue simulated monitoring; "
            "no intervention recommended."
        )

    @staticmethod
    def explain(
        classical_decision: str,
        quantum_decision: str,
        hybrid_decision: str,
    ) -> str:
        if hybrid_decision == "REVIEW":
            return (
                "Classical and quantum detection "
                "outputs disagree. The fusion policy "
                "requires human review."
            )

        if hybrid_decision == "ANOMALY":
            return (
                "Both detection outputs indicate "
                "an anomaly under their configured "
                "thresholds."
            )

        return (
            "Both detection outputs classify "
            "the event as normal."
        )

    def analyze(
        self,
        event: ThreatEvent,
    ) -> OrchestratorResult:

        classical = clamp(event.classical_score)
        quantum = clamp(event.quantum_score)

        classical_decision = classify(
            classical,
            self.classical_threshold,
        )

        quantum_decision = classify(
            quantum,
            self.quantum_threshold,
        )

        agreement = (
            classical_decision == quantum_decision
        )

        if agreement:
            hybrid_decision = classical_decision
        else:
            hybrid_decision = "REVIEW"

        fusion_score = (
            self.classical_weight * classical
            + self.quantum_weight * quantum
        )

        risk_score = round(fusion_score * 100)

        confidence = self.calculate_confidence(
            classical,
            quantum,
            agreement,
        )

        priority, severity = self.calculate_priority(
            hybrid_decision,
            risk_score,
        )

        action = self.recommend_action(
            hybrid_decision,
            priority,
        )

        explanation = self.explain(
            classical_decision,
            quantum_decision,
            hybrid_decision,
        )

        return OrchestratorResult(
            event_id=event.event_id,
            network=event.network,
            event_type=event.event_type,
            classical_score=round(classical, 4),
            quantum_score=round(quantum, 4),
            fusion_score=round(fusion_score, 4),
            classical_decision=classical_decision,
            quantum_decision=quantum_decision,
            hybrid_decision=hybrid_decision,
            model_agreement=agreement,
            confidence=confidence,
            risk_score=risk_score,
            priority=priority,
            severity=severity,
            recommended_action=action,
            explanation=explanation,
            mode="RESEARCH_SIMULATION",
        )


def generate_synthetic_events(
    count: int = EVENT_COUNT,
) -> list[ThreatEvent]:

    rng = random.Random(SEED)

    events = []

    for index in range(count):

        baseline = rng.random()

        classical = clamp(
            baseline + rng.uniform(-0.23, 0.23)
        )

        quantum = clamp(
            baseline + rng.uniform(-0.23, 0.23)
        )

        events.append(
            ThreatEvent(
                event_id=f"V15-EVENT-{index + 1:04d}",
                network=rng.choice(NETWORKS),
                event_type=rng.choice(EVENT_TYPES),
                classical_score=round(classical, 4),
                quantum_score=round(quantum, 4),
                timestamp=utc_now(),
            )
        )

    return events


def build_summary(
    results: list[OrchestratorResult],
) -> dict:

    decisions = (
        "NORMAL",
        "REVIEW",
        "ANOMALY",
    )

    priorities = (
        "P1",
        "P2",
        "P3",
        "P4",
    )

    return {
        "total_events": len(results),
        "decisions": {
            decision: sum(
                result.hybrid_decision == decision
                for result in results
            )
            for decision in decisions
        },
        "priorities": {
            priority: sum(
                result.priority == priority
                for result in results
            )
            for priority in priorities
        },
        "model_agreements": sum(
            result.model_agreement
            for result in results
        ),
        "model_disagreements": sum(
            not result.model_agreement
            for result in results
        ),
        "average_risk_score": round(
            statistics.mean(
                result.risk_score
                for result in results
            ),
            2,
        ),
        "average_heuristic_confidence": round(
            statistics.mean(
                result.confidence
                for result in results
            ),
            4,
        ),
    }


def save_report(
    results: list[OrchestratorResult],
    summary: dict,
) -> None:

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "module": "Intelligent Threat Orchestrator",
        "mode": "RESEARCH_SIMULATION",
        "generated_at": utc_now(),
        "configuration": {
            "seed": SEED,
            "event_count": EVENT_COUNT,
            "classical_threshold": 0.55,
            "quantum_threshold": 0.55,
            "classical_weight": 0.50,
            "quantum_weight": 0.50,
            "fusion_policy": (
                "Agreement-based classification; "
                "disagreement requires REVIEW"
            ),
        },
        "summary": summary,
        "events": [
            asdict(result)
            for result in results
        ],
        "limitations": [
            "Scores are synthetic demo inputs.",
            "No trained AI model is executed.",
            "No Qiskit circuit is executed.",
            "Confidence is an uncalibrated heuristic.",
            "Thresholds are experimental.",
            "No real attack data is processed.",
            "No automated security action is executed.",
            "No production detection performance is claimed.",
        ],
    }

    OUTPUT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main() -> None:

    print()
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA V15.1")
    print("INTELLIGENT THREAT ORCHESTRATOR")
    print("=" * 70)

    orchestrator = IntelligentThreatOrchestrator()

    events = generate_synthetic_events()

    results = []

    print()
    print("SIMULATED THREAT ORCHESTRATION")
    print("-" * 70)

    for event in events:

        result = orchestrator.analyze(event)

        results.append(result)

        print(
            f"{result.event_id} | "
            f"{result.network:10s} | "
            f"RISK {result.risk_score:3d}/100 | "
            f"{result.hybrid_decision:7s} | "
            f"{result.priority}"
        )

    summary = build_summary(results)

    save_report(results, summary)

    print()
    print("=" * 70)
    print("V15.1 RESEARCH SUMMARY")
    print("=" * 70)

    print()
    print("TOTAL EVENTS:", summary["total_events"])

    print(
        "NORMAL:",
        summary["decisions"]["NORMAL"],
    )

    print(
        "REVIEW:",
        summary["decisions"]["REVIEW"],
    )

    print(
        "ANOMALY:",
        summary["decisions"]["ANOMALY"],
    )

    print(
        "MODEL AGREEMENTS:",
        summary["model_agreements"],
    )

    print(
        "MODEL DISAGREEMENTS:",
        summary["model_disagreements"],
    )

    print(
        "AVERAGE RISK:",
        summary["average_risk_score"],
    )

    print()
    print("=" * 70)
    print("V15.1 INTELLIGENT THREAT ORCHESTRATOR COMPLETED")
    print("=" * 70)

    print()
    print("RESULTS SAVED TO:")
    print(OUTPUT_FILE)

    print()
    print(
        "NOTE: Synthetic standalone orchestration "
        "demonstration. No real-world detection "
        "or automated response is performed."
    )


if __name__ == "__main__":
    main()
