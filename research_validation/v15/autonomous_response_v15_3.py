
"""
QUANTUM CYBER DEFENSE ARENA
V15.3 - AUTONOMOUS RESPONSE SIMULATION

Reads the saved V15.2 multi-agent decision results
and produces a deterministic defensive response plan.

Capabilities:
- Priority-aware response planning
- Manual review enforcement
- Simulated response lifecycle
- Response policy validation
- Audit trail
- JSON research report

IMPORTANT:
- Only synthetic research data is supported.
- No firewall, blockchain, or network actions are executed.
- No wallet, host, or external service is modified.
- No real-world response effectiveness is claimed.

Input:
    multi_agent_decision_v15_2_results.json

Output:
    autonomous_response_v15_3_results.json
"""

from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "15.3.0"

HERE = Path(__file__).resolve().parent

INPUT_FILE = (
    HERE / "multi_agent_decision_v15_2_results.json"
)

OUTPUT_FILE = (
    HERE / "autonomous_response_v15_3_results.json"
)

ALLOWED_DECISIONS = {
    "NORMAL",
    "REVIEW",
    "ANOMALY",
}

ALLOWED_PRIORITIES = {
    "P1",
    "P2",
    "P3",
    "P4",
}

ALLOWED_ACTIONS = {
    "ESCALATE_CRITICAL",
    "QUEUE_HIGH_PRIORITY",
    "REQUEST_MANUAL_REVIEW",
    "CONTINUE_MONITORING",
}

RESPONSE_POLICY = {
    "P1": {
        "action": "ESCALATE_CRITICAL",
        "approval_required": True,
        "description": (
            "Prepare a critical incident escalation "
            "for human security analysts."
        ),
    },
    "P2": {
        "action": "QUEUE_HIGH_PRIORITY",
        "approval_required": True,
        "description": (
            "Queue a high-priority simulated "
            "incident investigation."
        ),
    },
    "P3": {
        "action": "REQUEST_MANUAL_REVIEW",
        "approval_required": True,
        "description": (
            "Request human review before any "
            "further response decision."
        ),
    },
    "P4": {
        "action": "CONTINUE_MONITORING",
        "approval_required": False,
        "description": (
            "Record the synthetic event and "
            "continue simulated monitoring."
        ),
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_risk_score(value: Any) -> int:
    if type(value) is not int:
        raise ValueError(
            "Risk score must be an integer."
        )

    if not 0 <= value <= 100:
        raise ValueError(
            "Risk score must be between 0 and 100."
        )

    return value


def load_v15_2_results() -> list[dict]:
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            "V15.2 result file was not found:\n"
            f"{INPUT_FILE}\n"
            "Run multi_agent_decision_v15_2.py first."
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError(
            "Invalid V15.2 JSON structure."
        )

    if payload.get("version") != "15.2.0":
        raise ValueError(
            "Expected V15.2.0 results."
        )

    if payload.get("mode") != "RESEARCH_SIMULATION":
        raise ValueError(
            "Only research simulation mode is supported."
        )

    events = payload.get("events")

    if not isinstance(events, list) or not events:
        raise ValueError(
            "No V15.2 multi-agent results found."
        )

    required_fields = (
        "event_id",
        "network",
        "event_type",
        "risk_score",
        "hybrid_decision",
        "final_priority",
        "final_decision",
        "manual_review_required",
        "consensus",
    )

    seen_ids = set()

    for number, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            raise ValueError(
                f"Event #{number} is not an object."
            )

        missing = [
            name
            for name in required_fields
            if name not in event
        ]

        if missing:
            raise ValueError(
                f"Event #{number} missing fields: "
                f"{missing}"
            )

        event_id = event["event_id"]

        if not isinstance(event_id, str) or not event_id:
            raise ValueError(
                f"Invalid event ID at #{number}."
            )

        if event_id in seen_ids:
            raise ValueError(
                f"Duplicate event ID: {event_id}"
            )

        seen_ids.add(event_id)

        decision = event["final_decision"]
        priority = event["final_priority"]

        if decision not in ALLOWED_DECISIONS:
            raise ValueError(
                f"Invalid decision for {event_id}."
            )

        if priority not in ALLOWED_PRIORITIES:
            raise ValueError(
                f"Invalid priority for {event_id}."
            )

        if type(event["manual_review_required"]) is not bool:
            raise ValueError(
                f"Invalid review flag for {event_id}."
            )

        if event["manual_review_required"] != (
            decision == "REVIEW"
        ):
            raise ValueError(
                f"Inconsistent review flag for {event_id}."
            )

        risk = validate_risk_score(
            event["risk_score"]
        )

        # Validate the V15.2 decision/priority policy.
        expected_priority = {
            "NORMAL": "P4",
            "REVIEW": "P3",
        }.get(decision)

        if decision == "ANOMALY":
            expected_priority = (
                "P1" if risk >= 80 else "P2"
            )

        if priority != expected_priority:
            raise ValueError(
                f"Inconsistent decision and priority "
                f"for {event_id}."
            )

    return events


@dataclass
class ResponseAuditEntry:
    step: int
    event_id: str
    stage: str
    status: str
    detail: str
    timestamp: str


@dataclass
class ResponsePlan:
    event_id: str
    network: str
    event_type: str

    risk_score: int
    decision: str
    priority: str

    planned_action: str
    action_description: str

    approval_required: bool
    manual_review_required: bool

    response_status: str
    simulated_execution: bool
    external_execution: bool

    policy_validated: bool
    reason: str

    audit_trail: list[ResponseAuditEntry] = field(
        default_factory=list
    )

    mode: str = "RESEARCH_SIMULATION"


class AutonomousResponseSimulator:
    """
    Builds and validates simulated response plans.

    All response operations are local decisions
    and JSON audit records.
    """

    def __init__(self) -> None:
        self.plans: list[ResponsePlan] = []

    @staticmethod
    def add_audit(
        audit: list[ResponseAuditEntry],
        event_id: str,
        stage: str,
        status: str,
        detail: str,
    ) -> None:
        audit.append(
            ResponseAuditEntry(
                step=len(audit) + 1,
                event_id=event_id,
                stage=stage,
                status=status,
                detail=detail,
                timestamp=utc_now(),
            )
        )

    @staticmethod
    def validate_policy(
        decision: str,
        priority: str,
        action: str,
        approval_required: bool,
    ) -> bool:
        policy = RESPONSE_POLICY.get(priority)

        if policy is None:
            return False

        if action not in ALLOWED_ACTIONS:
            return False

        if action != policy["action"]:
            return False

        if approval_required != policy["approval_required"]:
            return False

        if decision == "REVIEW":
            return (
                priority == "P3"
                and action == "REQUEST_MANUAL_REVIEW"
                and approval_required
            )

        if decision == "NORMAL":
            return (
                priority == "P4"
                and action == "CONTINUE_MONITORING"
            )

        if decision == "ANOMALY":
            return (
                priority in ("P1", "P2")
                and approval_required
            )

        return False

    def process_event(
        self,
        event: dict,
    ) -> ResponsePlan:

        event_id = event["event_id"]
        decision = event["final_decision"]
        priority = event["final_priority"]
        risk = event["risk_score"]

        audit: list[ResponseAuditEntry] = []

        self.add_audit(
            audit,
            event_id,
            "EVENT_RECEIVED",
            "COMPLETED",
            "V15.2 multi-agent result accepted.",
        )

        self.add_audit(
            audit,
            event_id,
            "RISK_EVALUATION",
            "COMPLETED",
            (
                f"Decision={decision}; "
                f"Priority={priority}; "
                f"Risk={risk}/100."
            ),
        )

        policy = RESPONSE_POLICY[priority]

        action = policy["action"]
        approval_required = policy["approval_required"]

        self.add_audit(
            audit,
            event_id,
            "RESPONSE_PLANNING",
            "COMPLETED",
            f"Selected response action: {action}.",
        )

        policy_validated = self.validate_policy(
            decision=decision,
            priority=priority,
            action=action,
            approval_required=approval_required,
        )

        if not policy_validated:
            response_status = "POLICY_REJECTED"
            simulated_execution = False

            reason = (
                "The proposed response does not "
                "satisfy the defensive response policy."
            )

        elif approval_required:
            response_status = "AWAITING_HUMAN_APPROVAL"
            simulated_execution = False

            reason = (
                "A simulated response was planned. "
                "Human authorization is required "
                "before any actual intervention."
            )

        else:
            response_status = "SIMULATED_MONITORING"
            simulated_execution = True

            reason = (
                "A monitoring-only step was simulated. "
                "No external system was contacted."
            )

        self.add_audit(
            audit,
            event_id,
            "POLICY_VALIDATION",
            (
                "PASSED"
                if policy_validated
                else "FAILED"
            ),
            reason,
        )

        self.add_audit(
            audit,
            event_id,
            "RESPONSE_FINALIZATION",
            response_status,
            (
                "No external security action "
                "was executed."
            ),
        )

        plan = ResponsePlan(
            event_id=event_id,
            network=event["network"],
            event_type=event["event_type"],
            risk_score=risk,
            decision=decision,
            priority=priority,
            planned_action=action,
            action_description=policy["description"],
            approval_required=approval_required,
            manual_review_required=event[
                "manual_review_required"
            ],
            response_status=response_status,
            simulated_execution=simulated_execution,
            external_execution=False,
            policy_validated=policy_validated,
            reason=reason,
            audit_trail=audit,
        )

        self.plans.append(plan)

        return plan


def build_summary(
    plans: list[ResponsePlan],
) -> dict:

    action_counts = Counter(
        plan.planned_action
        for plan in plans
    )

    status_counts = Counter(
        plan.response_status
        for plan in plans
    )

    return {
        "total_events": len(plans),
        "actions": {
            action: action_counts.get(action, 0)
            for action in sorted(ALLOWED_ACTIONS)
        },
        "response_statuses": dict(status_counts),
        "human_approval_required": sum(
            plan.approval_required
            for plan in plans
        ),
        "manual_review_required": sum(
            plan.manual_review_required
            for plan in plans
        ),
        "policy_validated": sum(
            plan.policy_validated
            for plan in plans
        ),
        "simulated_monitoring": sum(
            plan.simulated_execution
            for plan in plans
        ),
        "external_actions_executed": sum(
            plan.external_execution
            for plan in plans
        ),
        "audit_entries": sum(
            len(plan.audit_trail)
            for plan in plans
        ),
    }


def save_report(
    plans: list[ResponsePlan],
    summary: dict,
) -> None:

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "module": "Autonomous Response Simulation",
        "generated_at": utc_now(),
        "mode": "RESEARCH_SIMULATION",
        "source_file": INPUT_FILE.name,
        "response_policy": RESPONSE_POLICY,
        "summary": summary,
        "response_plans": [
            asdict(plan)
            for plan in plans
        ],
        "limitations": [
            "All input events originate from synthetic V15.1 data.",
            "Multi-agent decisions are deterministic rules.",
            "Response actions are simulated recommendations only.",
            "Approval requests are recorded, not sent to real users.",
            "No firewall policies are changed.",
            "No network traffic is blocked.",
            "No blockchain transactions are submitted.",
            "No real incident-remediation effectiveness is claimed.",
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
    print("QUANTUM CYBER DEFENSE ARENA V15.3")
    print("AUTONOMOUS RESPONSE SIMULATION")
    print("=" * 70)

    events = load_v15_2_results()

    simulator = AutonomousResponseSimulator()

    print()
    print("SIMULATED RESPONSE PLANNING")
    print("-" * 70)

    for event in events:

        plan = simulator.process_event(event)

        print(
            f"{plan.event_id} | "
            f"{plan.network:10s} | "
            f"{plan.priority} | "
            f"{plan.planned_action:23s} | "
            f"{plan.response_status}"
        )

    summary = build_summary(simulator.plans)

    save_report(
        simulator.plans,
        summary,
    )

    print()
    print("=" * 70)
    print("V15.3 RESPONSE SUMMARY")
    print("=" * 70)

    print()
    print(
        "TOTAL EVENTS:",
        summary["total_events"],
    )

    print(
        "HUMAN APPROVAL REQUIRED:",
        summary["human_approval_required"],
    )

    print(
        "MANUAL REVIEW REQUIRED:",
        summary["manual_review_required"],
    )

    print(
        "POLICY VALIDATED:",
        summary["policy_validated"],
    )

    print(
        "SIMULATED MONITORING:",
        summary["simulated_monitoring"],
    )

    print(
        "EXTERNAL ACTIONS EXECUTED:",
        summary["external_actions_executed"],
    )

    print(
        "AUDIT ENTRIES:",
        summary["audit_entries"],
    )

    print()
    print("=" * 70)
    print("V15.3 AUTONOMOUS RESPONSE SIMULATION COMPLETED")
    print("=" * 70)

    print()
    print("RESULTS SAVED TO:")
    print(OUTPUT_FILE)

    print()
    print(
        "NOTE: All response actions are simulated. "
        "No external systems were changed."
    )


if __name__ == "__main__":
    main()
