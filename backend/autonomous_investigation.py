
"""
QUANTUM CYBER DEFENSE ARENA V8
Autonomous AI Threat Investigation

Rule-based autonomous investigation prototype.
Uses outputs from the existing hybrid fusion models.

RESEARCH SIMULATION ONLY.
No real attacks, verified incidents, or live transactions.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


class AutonomousThreatInvestigator:
    VERSION = "8.0.0"

    def investigate(self, event: dict[str, Any]) -> dict[str, Any]:
        """Generate an explainable investigation from a Fusion event."""

        event_id = str(
            event.get("event_id") or event.get("id") or "UNKNOWN"
        )
        network = str(event.get("network") or "UNKNOWN")

        classification = str(
            event.get("classification") or "UNKNOWN"
        ).upper()

        severity = str(
            event.get("severity") or "UNKNOWN"
        ).upper()

        decision_status = str(
            event.get("decision_status") or "UNKNOWN"
        ).upper()

        classical_score = self._get_score(
            event.get("classical_score")
        )
        quantum_score = self._get_score(
            event.get("quantum_score")
        )

        fusion_score = self._get_fusion_score(event)

        models_agree = event.get("models_agree")

        findings: list[str] = []
        recommendations: list[str] = []

        if classification == "ANOMALY":
            findings.append(
                "The fusion system classified this simulated "
                "event as anomalous."
            )
            recommendations.append(
                "Prioritize this event for additional analysis."
            )

        elif classification == "REVIEW":
            findings.append(
                "The hybrid system requires additional review."
            )
            recommendations.append(
                "Compare the classical and quantum model outputs."
            )

        elif classification == "NORMAL":
            findings.append(
                "The fusion system classified this simulated "
                "event as normal."
            )

        else:
            findings.append(
                "The event has an unknown fusion classification."
            )
            recommendations.append(
                "Verify the input data and model outputs."
            )

        if models_agree is False:
            findings.append(
                "Classical and quantum model decisions disagree."
            )
            recommendations.append(
                "Investigate the disagreement before escalation."
            )

        elif models_agree is True:
            findings.append(
                "Classical and quantum model decisions agree."
            )

        if severity in {"HIGH", "CRITICAL"}:
            recommendations.append(
                "Review the associated simulated transaction "
                "features and anomaly scores."
            )

        if (
            classical_score is not None
            and quantum_score is not None
        ):
            difference = abs(classical_score - quantum_score)

            if difference >= 0.30:
                findings.append(
                    "A large difference exists between model "
                    "anomaly scores."
                )
                recommendations.append(
                    "Check model sensitivity and feature mapping."
                )

        if not recommendations:
            recommendations.append(
                "Continue monitoring simulated events."
            )

        priority = self._priority(
            classification,
            severity,
            models_agree,
        )

        return {
            "investigator": "Autonomous Threat Investigator",
            "version": self.VERSION,
            "mode": "RESEARCH_SIMULATION",
            "investigation_id": f"INV-{event_id}",
            "event_id": event_id,
            "network": network,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "classification": classification,
            "severity": severity,
            "priority": priority,
            "decision_status": decision_status,
            "models_agree": models_agree,
            "classical_score": classical_score,
            "quantum_score": quantum_score,
            "fusion_score_100": fusion_score,
            "findings": findings,
            "recommendations": list(dict.fromkeys(recommendations)),
            "status": "INVESTIGATION_COMPLETED",
            "disclaimer": (
                "Automated rule-based research assessment "
                "of synthetic events. Not a verified incident."
            ),
        }

    @staticmethod
    def _get_score(value: Any) -> float | None:
        if isinstance(value, bool):
            return None

        try:
            score = float(value)
        except (TypeError, ValueError):
            return None

        if not 0 <= score <= 1:
            return None

        return round(score, 6)

    @staticmethod
    def _get_fusion_score(event: dict[str, Any]) -> float | None:
        value = event.get("fusion_score_100")

        if value is None:
            normalized = AutonomousThreatInvestigator._get_score(
                event.get("fusion_score")
            )
            if normalized is None:
                return None
            return round(normalized * 100, 2)

        if isinstance(value, bool):
            return None

        try:
            score = float(value)
        except (TypeError, ValueError):
            return None

        if not 0 <= score <= 100:
            return None

        return round(score, 2)

    @staticmethod
    def _priority(
        classification: str,
        severity: str,
        models_agree: Any,
    ) -> str:
        if severity == "CRITICAL":
            return "P1"

        if severity == "HIGH" or classification == "ANOMALY":
            return "P2"

        if classification == "REVIEW" or models_agree is False:
            return "P3"

        return "P4"


def main() -> None:
    investigator = AutonomousThreatInvestigator()

    demo_event = {
        "event_id": "POLY-V8-001",
        "network": "Polygon",
        "classical_score": 0.88,
        "quantum_score": 0.92,
        "fusion_score_100": 90.0,
        "classification": "ANOMALY",
        "severity": "CRITICAL",
        "models_agree": True,
        "decision_status": "BOTH_DETECTED",
    }

    result = investigator.investigate(demo_event)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
