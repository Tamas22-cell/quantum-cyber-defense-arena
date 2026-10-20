
"""
QUANTUM CYBER DEFENSE ARENA
V15.2 - MULTI-AGENT DECISION ENGINE

Three explainable rule-based agents:
1. Threat Analysis Agent
2. Investigation Agent
3. Decision Agent

Reads actual saved V15.1 research simulation results.
Does not execute independent language-model agents.
Does not execute real-world security responses.

Input:
    threat_orchestrator_v15_1_results.json

Output:
    multi_agent_decision_v15_2_results.json
"""

from __future__ import annotations

import json
import math
import statistics
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "15.2.0"

HERE = Path(__file__).resolve().parent

INPUT_FILE = HERE / "threat_orchestrator_v15_1_results.json"
OUTPUT_FILE = HERE / "multi_agent_decision_v15_2_results.json"

AGENT_NAMES = (
    "Threat Analysis Agent",
    "Investigation Agent",
    "Decision Agent",
)

PRIORITY_ORDER = {
    "P1": 4,
    "P2": 3,
    "P3": 2,
    "P4": 1,
}

ALLOWED_DECISIONS = {
    "NORMAL",
    "REVIEW",
    "ANOMALY",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def validate_probability(
    value: Any,
    field: str,
) -> float:
    number = float(value)

    if not math.isfinite(number) or not 0 <= number <= 1:
        raise ValueError(
            f"Invalid {field}: expected a finite value from 0 to 1."
        )

    return number


@dataclass
class AgentAssessment:
    agent: str
    event_id: str
    decision: str
    priority: str
    score: float
    explanation: str
    recommended_action: str


@dataclass
class MultiAgentResult:
    event_id: str
    network: str
    event_type: str
    risk_score: int
    hybrid_decision: str
    threat_assessment: dict
    investigation_assessment: dict
    decision_assessment: dict
    consensus: str
    final_priority: str
    final_decision: str
    manual_review_required: bool
    explanation: str
    recommended_action: str
    mode: str


def load_v15_1_results() -> list[dict]:
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            "V15.1 results not found:\n"
            f"{INPUT_FILE}\n"
            "Run threat_orchestrator_v15_1.py first."
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if data.get("version") != "15.1.0":
        raise ValueError(
            "Expected V15.1.0 research results."
        )

    if data.get("mode") != "RESEARCH_SIMULATION":
        raise ValueError(
            "Only research simulation data is supported."
        )

    events = data.get("events")

    if not isinstance(events, list) or not events:
        raise ValueError(
            "No research events found in V15.1 results."
        )

    required_fields = (
        "event_id",
        "network",
        "event_type",
        "classical_score",
        "quantum_score",
        "fusion_score",
        "classical_decision",
        "quantum_decision",
        "hybrid_decision",
        "model_agreement",
        "risk_score",
    )

    seen_ids = set()

    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            raise ValueError(f"Invalid event #{index}.")

        missing = [
            field
            for field in required_fields
            if field not in event
        ]

        if missing:
            raise ValueError(
                f"Event #{index} missing fields: {missing}"
            )

        event_id = str(event["event_id"])

        if event_id in seen_ids:
            raise ValueError(
                f"Duplicate event ID: {event_id}"
            )

        seen_ids.add(event_id)

        for name in (
            "classical_score",
            "quantum_score",
            "fusion_score",
        ):
            validate_probability(event[name], name)

        if event["hybrid_decision"] not in ALLOWED_DECISIONS:
            raise ValueError(
                f"Invalid hybrid decision: {event_id}"
            )

        if event["classical_decision"] not in {
            "NORMAL",
            "ANOMALY",
        }:
            raise ValueError(
                f"Invalid classical decision: {event_id}"
            )

        if event["quantum_decision"] not in {
            "NORMAL",
            "ANOMALY",
        }:
            raise ValueError(
                f"Invalid quantum decision: {event_id}"
            )

        risk = event["risk_score"]

        if type(risk) is not int or not 0 <= risk <= 100:
            raise ValueError(
                f"Invalid risk score: {event_id}"
            )

        expected_agreement = (
            event["classical_decision"]
            == event["quantum_decision"]
        )

        if event["model_agreement"] is not expected_agreement:
            raise ValueError(
                f"Inconsistent agreement: {event_id}"
            )

        expected_hybrid = (
            event["classical_decision"]
            if expected_agreement
            else "REVIEW"
        )

        if event["hybrid_decision"] != expected_hybrid:
            raise ValueError(
                f"Inconsistent fusion decision: {event_id}"
            )

    return events


class ThreatAnalysisAgent:
    """
    Evaluates the supplied V15.1 risk score,
    hybrid decision, and detector scores.
    """

    name = "Threat Analysis Agent"

    def analyze(self, event: dict) -> AgentAssessment:
        risk = int(event["risk_score"])
        decision = event["hybrid_decision"]

        if decision == "ANOMALY":
            priority = "P1" if risk >= 80 else "P2"

            explanation = (
                "Both detection systems indicate an anomaly. "
                "The risk level determines incident urgency."
            )

            action = (
                "Escalate for simulated analyst investigation."
            )

        elif decision == "REVIEW":
            priority = "P3"

            explanation = (
                "The models disagree about this event. "
                "A combined risk score alone cannot resolve "
                "the conflicting classifications."
            )

            action = (
                "Request human review of both model outputs."
            )

        else:
            priority = "P4"

            explanation = (
                "Both models classify the event as normal "
                "under the V15.1 thresholds."
            )

            action = "Continue simulated monitoring."

        return AgentAssessment(
            agent=self.name,
            event_id=event["event_id"],
            decision=decision,
            priority=priority,
            score=round(risk / 100, 4),
            explanation=explanation,
            recommended_action=action,
        )


class InvestigationAgent:
    """
    Checks whether a simulated incident needs
    further investigation.

    A REVIEW decision always requires review.
    """

    name = "Investigation Agent"

    def analyze(self, event: dict) -> AgentAssessment:
        risk = int(event["risk_score"])
        disagreement = not event["model_agreement"]
        decision = event["hybrid_decision"]

        distance = abs(
            float(event["classical_score"])
            - float(event["quantum_score"])
        )

        if disagreement:
            recommendation = "REVIEW"
            priority = "P3"

            explanation = (
                "Detector disagreement identified. "
                f"Absolute normalized score gap: {distance:.4f}."
            )

            action = (
                "Inspect both scores and request manual review."
            )

        elif decision == "ANOMALY":
            recommendation = "ANOMALY"
            priority = "P1" if risk >= 80 else "P2"

            explanation = (
                "Both models agree on an anomaly. "
                "Investigation is recommended according "
                "to the simulated incident priority."
            )

            action = (
                "Prepare an analyst investigation case."
            )

        else:
            recommendation = "NORMAL"
            priority = "P4"

            explanation = (
                "No detector disagreement or anomaly "
                "is present under the configured rules."
            )

            action = "Record and continue monitoring."

        return AgentAssessment(
            agent=self.name,
            event_id=event["event_id"],
            decision=recommendation,
            priority=priority,
            score=round(clamp(distance), 4),
            explanation=explanation,
            recommended_action=action,
        )


class DecisionAgent:
    """
    Coordinates the two earlier assessments.

    The agent does not claim independent
    model inference or LLM-based consensus.
    """

    name = "Decision Agent"

    def analyze(
        self,
        event: dict,
        threat: AgentAssessment,
        investigation: AgentAssessment,
    ) -> AgentAssessment:

        decisions = (
            threat.decision,
            investigation.decision,
        )

        if "REVIEW" in decisions:
            final_decision = "REVIEW"
            priority = "P3"

            explanation = (
                "At least one assessment requires manual "
                "review. Automatic clearance is withheld."
            )

            action = (
                "Create a simulated review request."
            )

        elif all(
            decision == "ANOMALY"
            for decision in decisions
        ):
            final_decision = "ANOMALY"

            priority = (
                "P1"
                if event["risk_score"] >= 80
                else "P2"
            )

            explanation = (
                "Both earlier assessments agree on "
                "an anomaly. The event is escalated "
                "for investigation."
            )

            action = (
                "Recommend analyst investigation; "
                "do not execute automatic blocking."
            )

        else:
            final_decision = "NORMAL"
            priority = "P4"

            explanation = (
                "Both assessments support continued "
                "monitoring under the research rules."
            )

            action = (
                "Record the result and continue monitoring."
            )

        return AgentAssessment(
            agent=self.name,
            event_id=event["event_id"],
            decision=final_decision,
            priority=priority,
            score=round(
                float(event["fusion_score"]),
                4,
            ),
            explanation=explanation,
            recommended_action=action,
        )


class MultiAgentDecisionEngine:
    """
    Runs three sequential deterministic
    assessment stages.
    """

    def __init__(self) -> None:
        self.threat_agent = ThreatAnalysisAgent()
        self.investigation_agent = InvestigationAgent()
        self.decision_agent = DecisionAgent()

    def evaluate(self, event: dict) -> MultiAgentResult:

        threat = self.threat_agent.analyze(event)

        investigation = self.investigation_agent.analyze(
            event
        )

        decision = self.decision_agent.analyze(
            event,
            threat,
            investigation,
        )

        votes = [
            threat.decision,
            investigation.decision,
            decision.decision,
        ]

        consensus = (
            "UNANIMOUS_" + votes[0]
            if len(set(votes)) == 1
            else "DISAGREEMENT_REVIEW_REQUIRED"
        )

        manual_review = (
            decision.decision == "REVIEW"
        )

        return MultiAgentResult(
            event_id=event["event_id"],
            network=event["network"],
            event_type=event["event_type"],
            risk_score=event["risk_score"],
            hybrid_decision=event["hybrid_decision"],
            threat_assessment=asdict(threat),
            investigation_assessment=asdict(
                investigation
            ),
            decision_assessment=asdict(decision),
            consensus=consensus,
            final_priority=decision.priority,
            final_decision=decision.decision,
            manual_review_required=manual_review,
            explanation=decision.explanation,
            recommended_action=decision.recommended_action,
            mode="RESEARCH_SIMULATION",
        )


def build_summary(
    results: list[MultiAgentResult],
) -> dict:

    decisions = Counter(
        result.final_decision
        for result in results
    )

    priorities = Counter(
        result.final_priority
        for result in results
    )

    consensus_counts = Counter(
        result.consensus
        for result in results
    )

    return {
        "total_events": len(results),
        "decisions": {
            key: decisions.get(key, 0)
            for key in (
                "NORMAL",
                "REVIEW",
                "ANOMALY",
            )
        },
        "priorities": {
            key: priorities.get(key, 0)
            for key in (
                "P1",
                "P2",
                "P3",
                "P4",
            )
        },
        "manual_review_required": sum(
            result.manual_review_required
            for result in results
        ),
        "unanimous_consensus": sum(
            result.consensus.startswith("UNANIMOUS_")
            for result in results
        ),
        "consensus_breakdown": dict(
            consensus_counts
        ),
        "average_risk_score": round(
            statistics.mean(
                result.risk_score
                for result in results
            ),
            2,
        ),
    }


def save_report(
    results: list[MultiAgentResult],
    summary: dict,
) -> None:

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "module": "Multi-Agent Decision Engine",
        "mode": "RESEARCH_SIMULATION",
        "generated_at": utc_now(),
        "source_file": INPUT_FILE.name,
        "agents": list(AGENT_NAMES),
        "execution_model": (
            "Sequential deterministic rule-based agents"
        ),
        "summary": summary,
        "events": [
            asdict(result)
            for result in results
        ],
        "limitations": [
            "Input model scores originate from V15.1 synthetic data.",
            "Agents use deterministic rules, not independent LLMs.",
            "All assessments inherit the same V15.1 input.",
            "Unanimous consensus is not independent confirmation.",
            "No live threat intelligence feeds are used.",
            "No external model inference is performed.",
            "No automatic blocking or security remediation.",
            "No real-world detection performance is established.",
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
    print("QUANTUM CYBER DEFENSE ARENA V15.2")
    print("MULTI-AGENT DECISION ENGINE")
    print("=" * 70)

    events = load_v15_1_results()

    engine = MultiAgentDecisionEngine()

    results = []

    print()
    print("AGENT PIPELINE")
    print("-" * 70)

    for event in events:

        result = engine.evaluate(event)

        results.append(result)

        print(
            f"{result.event_id} | "
            f"{result.network:10s} | "
            f"RISK {result.risk_score:3d}/100 | "
            f"{result.final_decision:7s} | "
            f"{result.final_priority} | "
            f"{result.consensus}"
        )

    summary = build_summary(results)

    save_report(results, summary)

    print()
    print("=" * 70)
    print("V15.2 MULTI-AGENT SUMMARY")
    print("=" * 70)

    print()
    print("TOTAL EVENTS:", summary["total_events"])

    for decision, count in summary["decisions"].items():
        print(f"{decision}: {count}")

    print()
    print(
        "MANUAL REVIEW REQUIRED:",
        summary["manual_review_required"],
    )

    print(
        "UNANIMOUS CONSENSUS:",
        summary["unanimous_consensus"],
    )

    print(
        "AVERAGE RISK:",
        summary["average_risk_score"],
    )

    print()
    print("=" * 70)
    print("V15.2 MULTI-AGENT DECISION ENGINE COMPLETED")
    print("=" * 70)

    print()
    print("RESULTS SAVED TO:")
    print(OUTPUT_FILE)

    print()
    print(
        "NOTE: Three deterministic assessment stages "
        "analyze synthetic V15.1 outputs. "
        "No independent LLM agents or "
        "live remediation are used."
    )


if __name__ == "__main__":
    main()
