
"""
QUANTUM CYBER DEFENSE ARENA
V23.4 - MULTI-AGENT DEFENSE ORCHESTRATION SIMULATION

Three deterministic roles:
1. Policy Agent
2. Safety Supervisor
3. Simulation Coordinator

Inputs:
 V23.1 architecture
 V23.2 threat fusion report
 V23.3 optimization report and policy CSV

Outputs:
 multi_agent_defense_orchestration_v23_4_results.json
 multi_agent_defense_orchestration_v23_4_events.csv
 multi_agent_defense_orchestration_v23_4_timeline.json
 MULTI_AGENT_DEFENSE_ORCHESTRATION_V23_4.md

Research-only synthetic simulation.
No real security actions and no trained AI agents.
Python standard library only.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V23 = ROOT / "research_validation" / "v23"

ARCH = V23 / (
    "advanced_cyber_defense_architecture_v23_1_results.json"
)
FUSION = V23 / (
    "intelligent_threat_fusion_v23_2_results.json"
)
POLICY = V23 / (
    "adaptive_defense_policy_optimization_v23_3_results.json"
)
POLICY_CSV = V23 / (
    "adaptive_defense_policy_optimization_v23_3_policies.csv"
)

OUT_JSON = V23 / (
    "multi_agent_defense_orchestration_v23_4_results.json"
)
OUT_CSV = V23 / (
    "multi_agent_defense_orchestration_v23_4_events.csv"
)
OUT_TIMELINE = V23 / (
    "multi_agent_defense_orchestration_v23_4_timeline.json"
)
OUT_MD = V23 / (
    "MULTI_AGENT_DEFENSE_ORCHESTRATION_V23_4.md"
)

ACTIONS = {
    "observe",
    "increase_monitoring",
    "rate_limit",
    "isolate_node",
    "request_review",
}

APPROVAL_REQUIRED = {
    "rate_limit",
    "isolate_node",
    "request_review",
}

AGENT_ROLES = [
    "policy_agent",
    "safety_supervisor",
    "simulation_coordinator",
]

CHECKS = []


def check(name, condition, detail=""):
    passed = bool(condition)
    CHECKS.append({
        "name": name,
        "passed": passed,
        "detail": str(detail),
    })
    print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    if not passed and detail:
        print("       ", detail)
    return passed


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object")
    return data


def load_csv(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))
    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("Empty policy CSV")
    return rows


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            data, indent=2, ensure_ascii=False,
            allow_nan=False
        ),
        encoding="utf-8",
    )


def save_csv(path, rows):
    if not rows:
        raise ValueError("No orchestration events")
    with path.open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=list(rows[0])
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024), b""
        ):
            digest.update(chunk)
    return digest.hexdigest()


def number(value):
    if isinstance(value, bool):
        raise ValueError("Boolean numeric value")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Non-finite measurement")
    return value


def boolean(value):
    if isinstance(value, bool):
        return value
    if str(value).lower() == "true":
        return True
    if str(value).lower() == "false":
        return False
    raise ValueError(f"Invalid boolean: {value}")


def rnd(value):
    return round(float(value), 6)


def verify_inputs(arch, fusion, policy, rows):
    expected = (
        (
            arch, "V23.1",
            "ADVANCED_CYBER_DEFENSE_ARCHITECTURE_PASS"
        ),
        (
            fusion, "V23.2",
            "INTELLIGENT_THREAT_FUSION_PASS"
        ),
        (
            policy, "V23.3",
            "DEFENSE_POLICY_OPTIMIZATION_PASS"
        ),
    )

    for report, version, status in expected:
        check(
            f"{version} validated",
            report.get("version") == version
            and report.get("status") == status
            and report.get("checks_failed") == 0
            and report.get("simulation_mode") is True,
        )

    fingerprints = policy.get("source_sha256", {})

    check(
        "V23.3 architecture hash matches",
        fingerprints.get("architecture") == sha256(ARCH),
    )
    check(
        "V23.3 fusion hash matches",
        fingerprints.get("fusion_report") == sha256(FUSION),
    )
    check(
        "Policy inputs contain 1200 node records",
        len(rows) == 1200
        and policy.get("metrics", {}).get(
            "optimized_observations"
        ) == 1200,
    )
    check(
        "Policy source reports no external actions",
        policy.get("external_actions_enabled") is False,
    )

    profiles = policy.get(
        "configuration", {}
    ).get("profiles", {})

    strategies = policy.get(
        "configuration", {}
    ).get("strategies", {})

    check(
        "All three policy profiles available",
        set(profiles) == {
            "balanced", "service_first", "risk_first"
        },
    )
    check(
        "Five permitted simulated action types",
        set(strategies) == ACTIONS,
    )

    arch_policy = arch.get(
        "architecture", {}
    ).get("safety_policy", {})

    check(
        "V23.1 forbids real operations",
        arch_policy.get("real_network_access") is False
        and arch_policy.get("real_firewall_changes") is False
        and arch_policy.get("real_node_isolation") is False,
    )

    if not all(x["passed"] for x in CHECKS):
        raise ValueError("Source validation failed")

    return profiles, strategies


def normalize_policy_rows(rows, profiles):
    records = []
    identities = set()

    for row in rows:
        tick = int(row["tick"])
        node_id = row["node_id"]
        identity = (tick, node_id)

        if (
            not 0 <= tick < 120
            or identity in identities
        ):
            raise ValueError(
                f"Invalid record identity: {identity}"
            )

        identities.add(identity)
        score = number(row["fusion_score"])

        if not 0 <= score <= 1:
            raise ValueError("Invalid fusion score")

        actions = {}

        for profile in profiles:
            action = row[f"{profile}_action"]

            if action not in ACTIONS:
                raise ValueError(
                    f"Unknown action: {action}"
                )

            required = boolean(
                row[f"{profile}_approval_required"]
            )

            if required != (
                action in APPROVAL_REQUIRED
            ):
                raise ValueError(
                    f"Approval flag inconsistent: {identity}"
                )

            residual = number(
                row[f"{profile}_residual_risk"]
            )
            impact = number(
                row[f"{profile}_service_impact"]
            )

            if not (
                0 <= residual <= 1
                and 0 <= impact <= 1
            ):
                raise ValueError(
                    "Invalid hypothetical strategy values"
                )

            actions[profile] = {
                "action": action,
                "residual": residual,
                "impact": impact,
                "approval_required": required,
            }

        records.append({
            "tick": tick,
            "timestamp": row["timestamp"],
            "node_id": node_id,
            "fusion_score": score,
            "profiles": actions,
        })

    records.sort(
        key=lambda row: (
            row["tick"], row["node_id"]
        )
    )

    check(
        "Every tick has ten source nodes",
        len(records) == 1200
        and all(
            sum(row["tick"] == tick for row in records)
            == 10
            for tick in range(120)
        ),
    )

    check(
        "All input node-tick keys unique",
        len(identities) == 1200,
    )

    return records


def policy_agent(record, profile):
    """
    Produce a proposal from a previously
    optimized, hypothetical policy.
    """
    proposal = record["profiles"][profile]

    return {
        "proposed_action": proposal["action"],
        "approval_required": proposal["approval_required"],
        "predicted_residual_risk": proposal["residual"],
        "predicted_service_impact": proposal["impact"],
    }


def safety_supervisor(proposal):
    """
    Approval is NEVER invented.

    All approval-required actions are
    held as pending human review.

    Non-disruptive monitoring remains
    a simulated, non-executing plan.
    """
    action = proposal["proposed_action"]

    if action not in ACTIONS:
        return {
            "status": "REJECTED",
            "effective_action": "observe",
            "approval_status": "INVALID_ACTION",
        }

    if proposal["approval_required"]:
        return {
            "status": "PENDING_HUMAN_APPROVAL",
            "effective_action": "observe",
            "approval_status": "NOT_GRANTED",
        }

    return {
        "status": "SIMULATION_PLAN_VALIDATED",
        "effective_action": action,
        "approval_status": "NOT_REQUIRED",
    }


def simulation_coordinator(record, profile, proposal, review):
    """
    Convert proposals into simulation records.
    Never invoke a real action.
    """

    return {
        "event_id": (
            f"V23-ORCH-{record['tick']:03d}-"
            f"{record['node_id']}-{profile}"
        ),
        "tick": record["tick"],
        "timestamp": record["timestamp"],
        "node_id": record["node_id"],
        "profile": profile,
        "fusion_score": rnd(record["fusion_score"]),
        "proposed_action": proposal["proposed_action"],
        "orchestration_status": review["status"],
        "approval_status": review["approval_status"],
        "effective_simulated_action": review[
            "effective_action"
        ],
        "human_approval_required": proposal[
            "approval_required"
        ],
        "proposal_residual_risk": rnd(
            proposal["predicted_residual_risk"]
        ),
        "proposal_service_impact": rnd(
            proposal["predicted_service_impact"]
        ),
        "real_action_executed": False,
        "simulation_mode": True,
        "agent_method": "deterministic_role_pipeline",
    }


def orchestrate(records, profiles):
    events = []

    for record in records:
        for profile in profiles:
            proposal = policy_agent(
                record, profile
            )
            review = safety_supervisor(
                proposal
            )
            event = simulation_coordinator(
                record, profile, proposal, review
            )
            events.append(event)

    return events


def build_timeline(events, profiles):
    grouped = defaultdict(list)

    for event in events:
        grouped[event["tick"]].append(event)

    timeline = []

    for tick in range(120):
        tick_events = grouped[tick]

        entry = {
            "tick": tick,
            "timestamp": tick_events[0]["timestamp"],
            "total_proposals": len(tick_events),
            "profiles": {},
            "real_actions_executed": 0,
            "simulation_mode": True,
        }

        for profile in profiles:
            subset = [
                event for event in tick_events
                if event["profile"] == profile
            ]

            proposal_counts = Counter(
                event["proposed_action"]
                for event in subset
            )

            entry["profiles"][profile] = {
                "evaluated_nodes": len(subset),
                "mean_fusion_score": rnd(
                    statistics.mean(
                        e["fusion_score"]
                        for e in subset
                    )
                ),
                "approval_pending": sum(
                    e["orchestration_status"]
                    == "PENDING_HUMAN_APPROVAL"
                    for e in subset
                ),
                "validated_simulation_plans": sum(
                    e["orchestration_status"]
                    == "SIMULATION_PLAN_VALIDATED"
                    for e in subset
                ),
                "proposed_actions": {
                    action: proposal_counts[action]
                    for action in sorted(ACTIONS)
                },
            }

        timeline.append(entry)

    return timeline


def evaluate(events, profiles):
    evaluation = {}

    for profile in profiles:
        subset = [
            e for e in events
            if e["profile"] == profile
        ]

        evaluation[profile] = {
            "total_proposals": len(subset),
            "approval_pending": sum(
                e["orchestration_status"]
                == "PENDING_HUMAN_APPROVAL"
                for e in subset
            ),
            "validated_simulation_plans": sum(
                e["orchestration_status"]
                == "SIMULATION_PLAN_VALIDATED"
                for e in subset
            ),
            "real_actions_executed": 0,
        }

    return evaluation


def validate_results(
    events, timeline, evaluation, records, profiles
):
    check(
        "3600 orchestration events generated",
        len(events) == 1200 * len(profiles) == 3600,
    )

    check(
        "All event identifiers unique",
        len({e["event_id"] for e in events})
        == len(events),
    )

    check(
        "All selected actions recognized",
        all(
            e["proposed_action"] in ACTIONS
            and e["effective_simulated_action"] in ACTIONS
            for e in events
        ),
    )

    check(
        "Every approval-required proposal held",
        all(
            e["orchestration_status"]
            == "PENDING_HUMAN_APPROVAL"
            and e["approval_status"] == "NOT_GRANTED"
            and e["effective_simulated_action"] == "observe"
            for e in events
            if e["human_approval_required"]
        ),
    )

    check(
        "No real actions executed",
        all(
            e["real_action_executed"] is False
            and e["simulation_mode"] is True
            for e in events
        ),
    )

    check(
        "No approval falsely granted",
        all(
            e["approval_status"] != "APPROVED"
            for e in events
        ),
    )

    check(
        "All fused scores bounded",
        all(
            0 <= e["fusion_score"] <= 1
            for e in events
        ),
    )

    check(
        "All modeled outcomes bounded",
        all(
            0 <= e["proposal_residual_risk"] <= 1
            and 0 <= e["proposal_service_impact"] <= 1
            for e in events
        ),
    )

    check(
        "Timeline contains 120 ordered ticks",
        len(timeline) == 120
        and [
            t["tick"] for t in timeline
        ] == list(range(120)),
    )

    check(
        "Thirty proposals per tick",
        all(
            t["total_proposals"] == 30
            for t in timeline
        ),
    )

    check(
        "Ten proposals per profile per tick",
        all(
            t["profiles"][p]["evaluated_nodes"] == 10
            for t in timeline
            for p in profiles
        ),
    )

    check(
        "Profile evaluation totals consistent",
        all(
            result["total_proposals"] == 1200
            and (
                result["approval_pending"]
                + result["validated_simulation_plans"]
                == 1200
            )
            for result in evaluation.values()
        ),
    )

    check(
        "Orchestration is reproducible",
        events == orchestrate(records, profiles),
    )

    prefix = [
        row for row in records
        if row["tick"] < 60
    ]

    check(
        "First 60 ticks independent of future inputs",
        events[:len(prefix) * len(profiles)]
        == orchestrate(prefix, profiles),
    )


def make_document(report):
    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V23.4 - Multi-Agent Defense Orchestration",
        "",
        f"Status: {report['status']}",
        f"Checks passed: {report['checks_passed']}",
        f"Checks failed: {report['checks_failed']}",
        "",
        "### Deterministic analytical roles",
        "",
        "1. Policy Agent",
        "2. Safety Supervisor",
        "3. Simulation Coordinator",
        "",
        "These are software roles, not trained AI agents.",
        "",
        "### Research results",
        "",
        f"- Simulation ticks: {report['metrics']['ticks']}",
        f"- Network nodes: {report['metrics']['nodes']}",
        f"- Policy profiles: {report['metrics']['profiles']}",
        f"- Orchestration events: {report['metrics']['events']}",
        f"- Pending approvals: {report['metrics']['approval_pending']}",
        "- Real network actions: 0",
        "",
        "### Policy comparison",
        "",
        "| Profile | Proposals | Pending approval |",
        "|---|---:|---:|",
    ]

    for name, result in report["evaluation"].items():
        lines.append(
            f"| {name} | {result['total_proposals']} "
            f"| {result['approval_pending']} |"
        )

    lines += [
        "",
        "### Safety model",
        "",
        "Approval-required proposals remain pending.",
        "No approval is invented or granted.",
        "The simulation coordinator only records decisions.",
        "",
        "### Scientific limitations",
        "",
        "- Synthetic input telemetry only.",
        "- Fixed, hypothetical policy-effect assumptions.",
        "- No trained or independent LLM-based agents.",
        "- Approval workflow is a software simulation.",
        "- No real-world effectiveness demonstrated.",
        "- No external network operations.",
        "",
        "### Next stage",
        "",
        "V23.5 - Advanced Cyber Defense Dashboard",
        "",
    ]

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V23.4 - MULTI-AGENT DEFENSE ORCHESTRATION")
    print("=" * 70)

    V23.mkdir(parents=True, exist_ok=True)

    arch = load_json(ARCH)
    fusion = load_json(FUSION)
    policy = load_json(POLICY)
    raw_rows = load_csv(POLICY_CSV)

    profiles, strategies = verify_inputs(
        arch, fusion, policy, raw_rows
    )

    records = normalize_policy_rows(
        raw_rows, profiles
    )

    check(
        "Fusion observation count preserved",
        len(records) == fusion.get(
            "metrics", {}
        ).get("fused_observations"),
    )

    if not all(c["passed"] for c in CHECKS):
        raise ValueError("Input validation failed")

    events = orchestrate(records, profiles)
    timeline = build_timeline(events, profiles)
    evaluation = evaluate(events, profiles)

    validate_results(
        events, timeline, evaluation,
        records, profiles
    )

    passed = sum(c["passed"] for c in CHECKS)
    failed = len(CHECKS) - passed

    status = (
        "DEFENSE_ORCHESTRATION_PASS"
        if failed == 0
        else "DEFENSE_ORCHESTRATION_FAIL"
    )

    metrics = {
        "ticks": 120,
        "nodes": 10,
        "profiles": len(profiles),
        "events": len(events),
        "approval_pending": sum(
            e["orchestration_status"]
            == "PENDING_HUMAN_APPROVAL"
            for e in events
        ),
        "validated_simulation_plans": sum(
            e["orchestration_status"]
            == "SIMULATION_PLAN_VALIDATED"
            for e in events
        ),
        "real_actions_executed": 0,
        "trained_ai_agents_used": False,
    }

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V23.4",
        "module": "Multi-Agent Defense Orchestration",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "is_live": False,
        "external_actions_enabled": False,
        "agent_roles": AGENT_ROLES,
        "metrics": metrics,
        "evaluation": evaluation,
        "source_sha256": {
            "architecture": sha256(ARCH),
            "fusion_report": sha256(FUSION),
            "policy_report": sha256(POLICY),
            "policy_events": sha256(POLICY_CSV),
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "next_stage": (
            "V23.5 Advanced Cyber Defense Dashboard"
        ),
    }

    save_json(OUT_JSON, report)

    if failed == 0:
        save_csv(OUT_CSV, events)

        save_json(
            OUT_TIMELINE,
            {
                "version": "V23.4",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "ticks": len(timeline),
                "timeline": timeline,
            },
        )

        OUT_MD.write_text(
            make_document(report),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V23.4 DEFENSE ORCHESTRATION RESULTS")
    print("=" * 70)
    print("SIMULATION TICKS:", metrics["ticks"])
    print("NETWORK NODES:", metrics["nodes"])
    print("POLICY PROFILES:", metrics["profiles"])
    print("ORCHESTRATION EVENTS:", metrics["events"])
    print("APPROVALS PENDING:", metrics["approval_pending"])
    print("REAL ACTIONS EXECUTED: 0")
    print("CHECKS PASSED:", passed)
    print("CHECKS FAILED:", failed)
    print("JSON REPORT:", OUT_JSON)
    print("V23.4 RESULT:", status)
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(
            "V23.4 FAILED:",
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)
