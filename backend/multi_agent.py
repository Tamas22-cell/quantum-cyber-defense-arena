
"""
QUANTUM CYBER DEFENSE ARENA V9.4
MULTI-AGENT THREAT INTELLIGENCE ENGINE

Three deterministic research agents:
1. Threat Analysis Agent
2. Investigation Agent
3. Reporting Agent

Fix:
- Read fusion scores from flat or nested results.
- Preserve valid zero scores.
- Never silently replace missing scores with zero.
- Accept real V7 Fusion result fields.

RESEARCH SIMULATION ONLY.
Not a production security system.
"""

from __future__ import annotations

import json
import math

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


ENGINE_VERSION = "9.4.0"
ENGINE_MODE = "RESEARCH_SIMULATION"

VALID_CLASSIFICATIONS = {
    "NORMAL",
    "REVIEW",
    "ANOMALY",
}

VALID_SEVERITIES = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def valid_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    return result if math.isfinite(result) else None


def normalized_score(value: Any) -> float:
    number = valid_number(value)

    if number is None:
        return 0.0

    return max(0.0, min(1.0, number))


def score_100(value: Any) -> float:
    number = valid_number(value)

    if number is None:
        raise ValueError("Invalid numerical score.")

    if not 0.0 <= number <= 100.0:
        raise ValueError("Score must be between 0 and 100.")

    return round(number, 2)


def find_fusion_source(
    event: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Locate the V7 Fusion result.

    Supports flat events and common nested
    API / investigation result structures.
    """

    queue: list[Mapping[str, Any]] = [event]
    visited: set[int] = set()

    container_keys = (
        "fusion_result",
        "fusion",
        "fusion_analysis",
        "hybrid_fusion",
        "analysis",
        "result",
        "event",
        "source_event",
        "original_event",
        "data",
    )

    while queue:
        current = queue.pop(0)

        if id(current) in visited:
            continue

        visited.add(id(current))

        for key in ("fusion_score_100", "fusion_score"):
            if current.get(key) is not None:
                return current

        for key in container_keys:
            child = current.get(key)

            if isinstance(child, Mapping):
                queue.append(child)

    return event


def get_fusion_score(
    event: Mapping[str, Any],
) -> float:
    """
    Return the Fusion Score on a 0-100 scale.

    Missing data is an error, never an
    automatically invented 0.00 score.
    """

    source = find_fusion_source(event)

    value_100 = source.get("fusion_score_100")

    if value_100 is not None:
        return score_100(value_100)

    normalized = source.get("fusion_score")

    if normalized is not None:
        number = valid_number(normalized)

        if number is None or not 0.0 <= number <= 1.0:
            raise ValueError(
                "Invalid normalized fusion_score."
            )

        return score_100(number * 100.0)

    raise ValueError(
        "Missing Fusion Score for event "
        f"{event.get('event_id', event.get('id', 'UNKNOWN'))}. "
        "Check the V7.4 to V9 API mapping."
    )


def prepare_event(
    event: Mapping[str, Any],
) -> dict:
    """
    Normalize one incoming V7/V9 event.

    Keep all existing fields and copy missing
    Fusion fields from nested source data.
    """

    if not isinstance(event, Mapping):
        raise TypeError("Event must be a mapping.")

    result = dict(event)
    source = find_fusion_source(event)

    result["fusion_score_100"] = get_fusion_score(event)

    fields = (
        "event_id",
        "network",
        "classification",
        "severity",
        "classical_score",
        "quantum_score",
        "classical_anomaly",
        "quantum_anomaly",
        "models_agree",
        "decision_status",
        "explanation",
    )

    for key in fields:
        if result.get(key) is None:
            if source.get(key) is not None:
                result[key] = source[key]

    if not result.get("event_id"):
        result["event_id"] = str(
            result.get("id", "UNKNOWN")
        )

    if not result.get("network"):
        result["network"] = "Unknown"

    classification = str(
        result.get("classification", "REVIEW")
    ).upper()

    if classification not in VALID_CLASSIFICATIONS:
        classification = "REVIEW"

    result["classification"] = classification

    severity = str(
        result.get("severity", "MEDIUM")
    ).upper()

    if severity not in VALID_SEVERITIES:
        severity = "MEDIUM"

    result["severity"] = severity

    return result


@dataclass
class AgentFinding:
    agent: str
    status: str
    summary: str

    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    confidence_note: str = (
        "Experimental rule-based assessment."
    )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MultiAgentReport:
    report_id: str
    event_id: str
    network: str
    timestamp: str

    engine_version: str
    mode: str

    classification: str
    severity: str
    fusion_score_100: float
    priority: str

    agent_count: int
    agent_results: list[dict]

    consensus: str
    requires_review: bool
    executive_summary: str

    consolidated_findings: list[str]
    recommended_actions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


class ThreatAnalysisAgent:
    NAME = "Threat Analysis Agent"

    def analyze(
        self,
        event: Mapping[str, Any],
    ) -> AgentFinding:

        classification = event["classification"]
        severity = event["severity"]

        fusion_score = get_fusion_score(event)

        findings = [
            f"Fusion risk score: {fusion_score:.2f}/100.",
            f"Classification: {classification}.",
            f"Severity: {severity}.",
        ]

        recommendations = []

        classical_raw = valid_number(
            event.get("classical_score")
        )

        quantum_raw = valid_number(
            event.get("quantum_score")
        )

        if classical_raw is not None:
            classical = normalized_score(classical_raw)

            findings.append(
                "Classical anomaly evidence: "
                f"{classical * 100:.2f}/100."
            )

        if quantum_raw is not None:
            quantum = normalized_score(quantum_raw)

            findings.append(
                "Quantum anomaly evidence: "
                f"{quantum * 100:.2f}/100."
            )

        if (
            classical_raw is not None
            and quantum_raw is not None
        ):
            gap = abs(
                normalized_score(classical_raw)
                - normalized_score(quantum_raw)
            ) * 100.0

            if gap >= 30.0:
                findings.append(
                    f"Model score difference: {gap:.2f} pp."
                )

                recommendations.append(
                    "Review detector thresholds "
                    "and feature preprocessing."
                )

        if severity == "CRITICAL":
            recommendations.append(
                "Prioritize simulated event for review."
            )

        elif severity == "HIGH":
            recommendations.append(
                "Review before lower-priority cases."
            )

        elif classification == "REVIEW":
            recommendations.append(
                "Collect additional simulation evidence."
            )

        else:
            recommendations.append(
                "Continue research monitoring."
            )

        status = (
            "ALERT"
            if classification == "ANOMALY"
            else "REVIEW"
            if classification == "REVIEW"
            else "CLEAR"
        )

        return AgentFinding(
            agent=self.NAME,
            status=status,
            summary=(
                f"Threat classification: {classification}. "
                f"Severity: {severity}."
            ),
            findings=findings,
            recommendations=recommendations,
        )


class InvestigationAgent:
    NAME = "Investigation Agent"

    def analyze(
        self,
        event: Mapping[str, Any],
    ) -> AgentFinding:

        agreement = event.get("models_agree")

        classical = event.get("classical_anomaly")
        quantum = event.get("quantum_anomaly")

        decision = str(
            event.get("decision_status", "UNKNOWN")
        )

        findings = []
        recommendations = []

        if agreement is False:
            status = "DISAGREEMENT"

            findings.append(
                "Classical and quantum models disagree."
            )

            recommendations.append(
                "Preserve both original model outputs."
            )

            recommendations.append(
                "Request additional model validation."
            )

        elif agreement is True:
            status = "AGREEMENT"

            findings.append(
                "Both models agree on the anomaly decision."
            )

        else:
            status = "INSUFFICIENT_EVIDENCE"

            findings.append(
                "Model agreement information is missing."
            )

            recommendations.append(
                "Verify the upstream Fusion API mapping."
            )

        if classical is True and quantum is True:
            findings.append(
                "Both detectors flagged anomaly evidence."
            )

        elif classical is False and quantum is False:
            findings.append(
                "Both detectors classified the event as normal."
            )

        findings.append(
            f"Fusion decision status: {decision}."
        )

        return AgentFinding(
            agent=self.NAME,
            status=status,
            summary="Cross-model evidence review completed.",
            findings=findings,
            recommendations=recommendations,
        )


class ReportingAgent:
    NAME = "Reporting Agent"

    def analyze(
        self,
        event: Mapping[str, Any],
    ) -> AgentFinding:

        event_id = str(event["event_id"])
        network = str(event["network"])
        classification = event["classification"]
        severity = event["severity"]

        findings = [
            f"Event ID: {event_id}.",
            f"Blockchain network: {network}.",
            f"Reported severity: {severity}.",
            f"Fusion classification: {classification}.",
            (
                "Fusion risk score: "
                f"{get_fusion_score(event):.2f}/100."
            ),
        ]

        recommendations = [
            "Preserve the research report "
            "with the source simulation event."
        ]

        if classification == "REVIEW":
            recommendations.append(
                "Perform additional model comparison."
            )

        elif classification == "ANOMALY":
            recommendations.append(
                "Document anomaly evidence and model outputs."
            )

        return AgentFinding(
            agent=self.NAME,
            status="REPORT_READY",
            summary="Structured research report prepared.",
            findings=findings,
            recommendations=recommendations,
        )


class MultiAgentCyberDefenseEngine:

    def __init__(self) -> None:
        self.threat_agent = ThreatAnalysisAgent()
        self.investigation_agent = InvestigationAgent()
        self.reporting_agent = ReportingAgent()

        self.processed_events = 0
        self.review_events = 0
        self.anomaly_events = 0

    def analyze(
        self,
        event: Mapping[str, Any],
    ) -> MultiAgentReport:

        prepared = prepare_event(event)

        event_id = str(prepared["event_id"])
        network = str(prepared["network"])

        classification = prepared["classification"]
        severity = prepared["severity"]

        fusion_score = get_fusion_score(prepared)

        agent_results = [
            self.threat_agent.analyze(prepared),
            self.investigation_agent.analyze(prepared),
            self.reporting_agent.analyze(prepared),
        ]

        requires_review = (
            classification == "REVIEW"
            or prepared.get("models_agree") is False
        )

        if requires_review:
            consensus = "REVIEW_REQUIRED"

        elif classification == "ANOMALY":
            consensus = (
                "ANOMALY_CONFIRMED_BY_FUSION_RULES"
            )

        else:
            consensus = "NORMAL_BY_FUSION_RULES"

        if (
            classification == "ANOMALY"
            and severity == "CRITICAL"
        ):
            priority = "P1"

        elif classification == "ANOMALY":
            priority = "P2"

        elif requires_review:
            priority = "P2"

        else:
            priority = "P4"

        findings = []
        actions = []

        for result in agent_results:
            findings.extend(result.findings)
            actions.extend(result.recommendations)

        findings = list(dict.fromkeys(findings))
        actions = list(dict.fromkeys(actions))

        summary = (
            f"Event {event_id} on {network}: "
            f"fusion classification {classification}, "
            f"risk score {fusion_score:.2f}/100, "
            f"priority {priority}. "
            f"Multi-agent consensus: {consensus}."
        )

        self.processed_events += 1

        if requires_review:
            self.review_events += 1

        if classification == "ANOMALY":
            self.anomaly_events += 1

        return MultiAgentReport(
            report_id=f"V9-{event_id}",
            event_id=event_id,
            network=network,
            timestamp=utc_now(),
            engine_version=ENGINE_VERSION,
            mode=ENGINE_MODE,
            classification=classification,
            severity=severity,
            fusion_score_100=fusion_score,
            priority=priority,
            agent_count=len(agent_results),
            agent_results=[
                result.to_dict()
                for result in agent_results
            ],
            consensus=consensus,
            requires_review=requires_review,
            executive_summary=summary,
            consolidated_findings=findings,
            recommended_actions=actions,
        )

    def analyze_batch(
        self,
        events: Sequence[Mapping[str, Any]],
    ) -> list[dict]:
        return [
            self.analyze(event).to_dict()
            for event in events
        ]

    def status(self) -> dict:
        return {
            "version": ENGINE_VERSION,
            "status": "READY",
            "mode": ENGINE_MODE,
            "agents": [
                self.threat_agent.NAME,
                self.investigation_agent.NAME,
                self.reporting_agent.NAME,
            ],
            "agent_count": 3,
            "processed_events": self.processed_events,
            "review_events": self.review_events,
            "anomaly_events": self.anomaly_events,
        }


def create_demo_events() -> list[dict]:
    return [
        {
            "event_id": "ETH-V9-001",
            "network": "Ethereum",
            "classification": "NORMAL",
            "severity": "LOW",
            "fusion_score_100": 21.20,
            "classical_score": 0.419962,
            "quantum_score": 0.004014,
            "classical_anomaly": False,
            "quantum_anomaly": False,
            "models_agree": True,
            "decision_status": "BOTH_NORMAL",
        },
        {
            "event_id": "POLY-V9-002",
            "network": "Polygon",
            "classification": "ANOMALY",
            "severity": "CRITICAL",
            "fusion_score_100": 90.34,
            "classical_score": 0.882699,
            "quantum_score": 0.924183,
            "classical_anomaly": True,
            "quantum_anomaly": True,
            "models_agree": True,
            "decision_status": "BOTH_DETECTED",
        },
        {
            "event_id": "BASE-V9-003",
            "network": "Base",
            "classification": "REVIEW",
            "severity": "HIGH",
            "fusion_result": {
                "fusion_score_100": 67.50,
                "classical_score": 0.82,
                "quantum_score": 0.53,
                "classical_anomaly": True,
                "quantum_anomaly": False,
                "models_agree": False,
                "decision_status": "CLASSICAL_ONLY",
            },
        },
    ]


def main() -> None:
    print()
    print("=" * 64)
    print("QUANTUM CYBER DEFENSE ARENA V9.4")
    print("MULTI-AGENT FUSION SCORE VALIDATION")
    print("=" * 64)

    engine = MultiAgentCyberDefenseEngine()

    reports = engine.analyze_batch(
        create_demo_events()
    )

    for report in reports:
        print()
        print("EVENT:", report["event_id"])
        print("NETWORK:", report["network"])
        print(
            "FUSION SCORE:",
            report["fusion_score_100"],
        )
        print(
            "CLASSIFICATION:",
            report["classification"],
        )
        print("PRIORITY:", report["priority"])

    print()
    print("TEST COMPLETED")
    print(json.dumps(
        engine.status(),
        indent=2,
    ))


if __name__ == "__main__":
    main()
