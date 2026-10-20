
"""
QUANTUM CYBER DEFENSE ARENA
V22.3 - MULTI-AGENT DEFENSE DECISION ENGINE

Deterministic simulation-only decision support.

Analytical roles:
  1. Threat Assessment Agent
  2. Defense Strategy Agent
  3. Decision Validation Supervisor

Inputs:
  V22.1 architecture
  V22.2 adaptive detection report and scores
  V21.5 intelligence data

Outputs:
  multi_agent_defense_decision_v22_3_results.json
  multi_agent_defense_decision_v22_3_decisions.csv
  multi_agent_defense_decision_v22_3_timeline.json
  MULTI_AGENT_DEFENSE_DECISION_V22_3.md

No LLM or trained model is used.
No real traffic, devices or firewalls are modified.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V22 = ROOT / "research_validation" / "v22"

ARCH_FILE = V22 / (
    "autonomous_defense_architecture_v22_1_results.json"
)

DETECTOR_FILE = V22 / (
    "adaptive_threat_detection_v22_2_results.json"
)

SCORES_FILE = V22 / (
    "adaptive_threat_detection_v22_2_scores.csv"
)

INTELLIGENCE_FILE = ROOT / (
    "frontend/public/v21/intelligence_data.json"
)

OUTPUT_JSON = V22 / (
    "multi_agent_defense_decision_v22_3_results.json"
)

OUTPUT_CSV = V22 / (
    "multi_agent_defense_decision_v22_3_decisions.csv"
)

OUTPUT_TIMELINE = V22 / (
    "multi_agent_defense_decision_v22_3_timeline.json"
)

OUTPUT_MD = V22 / (
    "MULTI_AGENT_DEFENSE_DECISION_V22_3.md"
)

CHECKS = []

ACTIONS = {
    "observe",
    "increase_monitoring",
    "rate_limit",
    "isolate_node",
    "request_review",
}

DISRUPTIVE_ACTIONS = {
    "rate_limit",
    "isolate_node",
}

AGENTS = (
    "threat_assessment_agent",
    "defense_strategy_agent",
    "decision_validation_supervisor",
)


def check(name, condition, detail=""):
    passed = bool(condition)

    CHECKS.append({
        "name": name,
        "passed": passed,
        "detail": str(detail),
    })

    print(
        f"[{'PASS' if passed else 'FAIL'}] {name}"
    )

    if not passed and detail:
        print("       " + str(detail))

    return passed


def read_json(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected JSON object: {path.name}"
        )

    return data


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("Empty adaptive score CSV")

    return rows


def write_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


def write_csv(path, rows):
    if not rows:
        raise ValueError("No decisions to export")

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0]),
        )

        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def as_number(value):
    if isinstance(value, bool):
        raise ValueError(
            "Boolean is not a measurement"
        )

    result = float(value)

    if not math.isfinite(result):
        raise ValueError(
            "Non-finite numeric measurement"
        )

    return result


def as_bool(value):
    if isinstance(value, bool):
        return value

    if str(value).lower() == "true":
        return True

    if str(value).lower() == "false":
        return False

    raise ValueError(
        f"Invalid boolean: {value}"
    )


def rounded(value):
    return round(float(value), 6)


def validate_sources(arch, detector, intelligence):
    check(
        "V22.1 architecture passed",
        arch.get("version") == "V22.1"
        and arch.get("status")
        == "AUTONOMOUS_DEFENSE_ARCHITECTURE_PASS"
        and arch.get("checks_failed") == 0,
    )

    check(
        "V22.2 adaptive detector passed",
        detector.get("version") == "V22.2"
        and detector.get("status")
        == "ADAPTIVE_THREAT_DETECTION_PASS"
        and detector.get("checks_failed") == 0,
    )

    check(
        "V21.5 intelligence export passed",
        intelligence.get("version") == "V21.5"
        and intelligence.get("status")
        == "DASHBOARD_INTEGRATION_PASS"
        and intelligence.get("simulation_mode") is True
        and intelligence.get("is_live") is False,
    )

    fingerprints = detector.get(
        "source_sha256", {}
    )

    check(
        "V22.2 architecture fingerprint valid",
        fingerprints.get("architecture")
        == sha256(ARCH_FILE),
    )

    check(
        "V22.2 intelligence fingerprint valid",
        fingerprints.get("data")
        == sha256(INTELLIGENCE_FILE),
    )

    policy = arch.get(
        "architecture", {}
    ).get("policy", {})

    check(
        "Architecture simulation mode enforced",
        policy.get("simulation_mode") is True,
    )

    check(
        "Real network modifications disabled",
        policy.get(
            "real_network_changes_allowed"
        ) is False,
    )

    check(
        "Real traffic blocking disabled",
        policy.get(
            "real_traffic_blocking"
        ) is False,
    )

    check(
        "Real node isolation disabled",
        policy.get(
            "automatic_node_isolation"
        ) is False,
    )

    check(
        "Human approval policy enabled",
        policy.get(
            "human_approval_for_disruptive_actions"
        ) is True,
    )

    actions = arch.get(
        "architecture", {}
    ).get("defense_actions", [])

    check(
        "Five documented defense actions",
        {item["id"] for item in actions}
        == ACTIONS,
    )

    check(
        "All documented actions are simulations",
        all(
            item.get("implementation")
            == "simulated"
            for item in actions
        ),
    )

    frames = intelligence.get("frames", [])

    check(
        "120 intelligence frames available",
        len(frames) == 120
        and [
            frame.get("tick")
            for frame in frames
        ] == list(range(120)),
    )

    check(
        "Ten nodes per frame",
        all(
            len(frame.get("nodes", [])) == 10
            for frame in frames
        ),
    )

    if not all(
        item["passed"]
        for item in CHECKS
    ):
        raise ValueError(
            "Source validation failed"
        )

    return frames


def normalize_scores(rows, frames):
    normalized = []

    node_sets = {
        frame["tick"]: {
            node["id"]
            for node in frame["nodes"]
        }
        for frame in frames
    }

    seen = set()

    for row in rows:
        tick = int(row["tick"])
        node_id = row["node_id"]

        key = (tick, node_id)

        if (
            tick not in node_sets
            or node_id not in node_sets[tick]
            or key in seen
        ):
            raise ValueError(
                f"Invalid score identity: {key}"
            )

        seen.add(key)

        score = as_number(
            row["anomaly_score"]
        )
        threshold = as_number(
            row["adaptive_threshold"]
        )
        risk = as_number(
            row["risk_score"]
        )

        if (
            score < 0
            or threshold < 0
            or not 0 <= risk <= 1
        ):
            raise ValueError(
                f"Invalid score at {key}"
            )

        ready = as_bool(
            row["baseline_ready"]
        )
        detected = as_bool(
            row["detected_anomaly"]
        )

        if detected != (
            ready and score >= threshold
        ):
            raise ValueError(
                f"Inconsistent detection at {key}"
            )

        normalized.append({
            "tick": tick,
            "timestamp": row["timestamp"],
            "node_id": node_id,
            "anomaly_score": score,
            "adaptive_threshold": threshold,
            "risk": risk,
            "baseline_ready": ready,
            "detected": detected,
            "injected_marker": as_bool(
                row["injected_anomaly"]
            ),
        })

    check(
        "1200 node observations available",
        len(normalized) == 1200,
    )

    check(
        "All node observations unique",
        len(seen) == len(normalized),
    )

    check(
        "Every frame/node has an adaptive score",
        all(
            (frame["tick"], node["id"]) in seen
            for frame in frames
            for node in frame["nodes"]
        ),
    )

    normalized.sort(
        key=lambda row: (
            row["tick"],
            row["node_id"],
        )
    )

    return normalized


def threat_assessment_agent(row, frame):
    """
    Evaluate current synthetic evidence.

    Synthetic injected markers are intentionally
    NOT used to select an action.
    """

    anomaly_strength = 0.0

    if row["baseline_ready"]:
        anomaly_strength = min(
            1.0,
            row["anomaly_score"]
            / max(row["adaptive_threshold"], 0.01)
        )

    correlation = as_number(
        frame["correlation_score"]
    )

    if not 0 <= correlation <= 1:
        raise ValueError(
            "Correlation outside zero-one range"
        )

    # Frame-wide correlation is context, not
    # necessarily evidence against this node.
    evidence_score = (
        0.65 * row["risk"]
        + 0.25 * anomaly_strength
        + 0.10 * correlation
    )

    evidence_score = min(
        1.0,
        max(0.0, evidence_score),
    )

    if evidence_score >= 0.90:
        severity = "critical"
    elif evidence_score >= 0.75:
        severity = "high"
    elif evidence_score >= 0.50:
        severity = "medium"
    elif evidence_score >= 0.25:
        severity = "low"
    else:
        severity = "normal"

    return {
        "evidence_score": rounded(
            evidence_score
        ),
        "severity": severity,
        "adaptive_detection": row["detected"],
        "node_risk": rounded(row["risk"]),
        "frame_correlation": rounded(
            correlation
        ),
    }


def defense_strategy_agent(assessment):
    """
    Propose a simulated policy response.

    No decision is executed against a
    real network.
    """

    severity = assessment["severity"]
    detected = assessment[
        "adaptive_detection"
    ]

    if severity == "critical" and detected:
        action = "isolate_node"

    elif severity == "high" and detected:
        action = "rate_limit"

    elif severity in {"high", "critical"}:
        action = "request_review"

    elif detected or severity == "medium":
        action = "increase_monitoring"

    else:
        action = "observe"

    reasons = [
        "synthetic_risk="
        + str(assessment["node_risk"]),
        "adaptive_detection="
        + str(detected),
        "severity="
        + severity,
    ]

    return {
        "proposed_action": action,
        "reason": "; ".join(reasons),
        "requires_human_approval": (
            action in {
                "rate_limit",
                "isolate_node",
                "request_review",
            }
        ),
    }


def decision_validation_supervisor(
    assessment,
    proposal,
    allowed_actions,
):
    """
    Validate the simulated proposal.

    High-impact action proposals remain
    recommendations only.
    """

    action = proposal["proposed_action"]

    known = action in allowed_actions

    requires_approval = proposal[
        "requires_human_approval"
    ]

    approval_valid = (
        action not in DISRUPTIVE_ACTIONS
        or requires_approval
    )

    if not known or not approval_valid:
        final_action = "request_review"
        supervisor_status = "ESCALATED"

    else:
        final_action = action
        supervisor_status = "VALIDATED"

    return {
        "final_action": final_action,
        "supervisor_status": supervisor_status,
        "human_approval_required": (
            final_action in {
                "rate_limit",
                "isolate_node",
                "request_review",
            }
        ),
        "real_action_executed": False,
        "simulation_only": True,
    }


def build_decisions(rows, frames, allowed_actions):
    frame_by_tick = {
        frame["tick"]: frame
        for frame in frames
    }

    decisions = []

    for row in rows:
        frame = frame_by_tick[
            row["tick"]
        ]

        assessment = threat_assessment_agent(
            row,
            frame,
        )

        proposal = defense_strategy_agent(
            assessment
        )

        validation = decision_validation_supervisor(
            assessment,
            proposal,
            allowed_actions,
        )

        decisions.append({
            "decision_id": (
                f"V22-DEC-{row['tick']:03d}-"
                f"{row['node_id']}"
            ),
            "tick": row["tick"],
            "timestamp": row["timestamp"],
            "node_id": row["node_id"],
            "severity": assessment["severity"],
            "evidence_score": assessment[
                "evidence_score"
            ],
            "node_risk": assessment["node_risk"],
            "adaptive_detection": row["detected"],
            "anomaly_score": rounded(
                row["anomaly_score"]
            ),
            "frame_correlation": assessment[
                "frame_correlation"
            ],
            "proposed_action": proposal[
                "proposed_action"
            ],
            "final_action": validation[
                "final_action"
            ],
            "reason": proposal["reason"],
            "supervisor_status": validation[
                "supervisor_status"
            ],
            "human_approval_required": validation[
                "human_approval_required"
            ],
            "real_action_executed": False,
            "simulation_only": True,
            "synthetic_injection_marker": row[
                "injected_marker"
            ],
            "decision_method": (
                "deterministic_multi_role_policy"
            ),
        })

    return decisions


def build_timeline(decisions, frames):
    by_tick = defaultdict(list)

    for decision in decisions:
        by_tick[decision["tick"]].append(
            decision
        )

    timeline = []

    for frame in frames:
        tick = frame["tick"]
        items = by_tick[tick]

        action_counts = Counter(
            item["final_action"]
            for item in items
        )

        timeline.append({
            "tick": tick,
            "timestamp": frame["timestamp"],
            "evaluated_nodes": len(items),
            "maximum_evidence_score": max(
                item["evidence_score"]
                for item in items
            ),
            "adaptive_detections": sum(
                item["adaptive_detection"]
                for item in items
            ),
            "human_review_required": sum(
                item["human_approval_required"]
                for item in items
            ),
            "action_counts": {
                action: action_counts[action]
                for action in sorted(ACTIONS)
            },
            "real_actions_executed": 0,
            "simulation_mode": True,
        })

    return timeline


def validate_results(
    decisions,
    timeline,
    scores,
    frames,
    allowed_actions,
):
    check(
        "Decision per node observation",
        len(decisions) == len(scores) == 1200,
    )

    check(
        "All decision IDs unique",
        len({
            row["decision_id"]
            for row in decisions
        }) == len(decisions),
    )

    check(
        "All actions belong to V22.1 policy",
        all(
            item["final_action"] in allowed_actions
            for item in decisions
        ),
    )

    check(
        "Every disruptive proposal requires approval",
        all(
            item["human_approval_required"]
            for item in decisions
            if item["final_action"]
            in DISRUPTIVE_ACTIONS
        ),
    )

    check(
        "No real network actions executed",
        all(
            item["real_action_executed"] is False
            for item in decisions
        ),
    )

    check(
        "All decisions remain simulations",
        all(
            item["simulation_only"] is True
            for item in decisions
        ),
    )

    check(
        "All evidence scores bounded",
        all(
            0 <= item["evidence_score"] <= 1
            for item in decisions
        ),
    )

    check(
        "All severity levels recognized",
        all(
            item["severity"] in {
                "normal",
                "low",
                "medium",
                "high",
                "critical",
            }
            for item in decisions
        ),
    )

    check(
        "Every decision reviewed by supervisor",
        all(
            item["supervisor_status"]
            in {"VALIDATED", "ESCALATED"}
            for item in decisions
        ),
    )

    check(
        "Timeline contains 120 ticks",
        len(timeline) == 120
        and [
            row["tick"] for row in timeline
        ] == list(range(120)),
    )

    check(
        "Ten evaluated nodes per tick",
        all(
            row["evaluated_nodes"] == 10
            for row in timeline
        ),
    )

    check(
        "Timeline decision counts consistent",
        sum(
            sum(row["action_counts"].values())
            for row in timeline
        ) == len(decisions),
    )

    check(
        "Timeline review totals consistent",
        sum(
            row["human_review_required"]
            for row in timeline
        ) == sum(
            row["human_approval_required"]
            for row in decisions
        ),
    )

    check(
        "Detection flags preserve V22.2 output",
        sum(
            row["adaptive_detection"]
            for row in decisions
        ) == sum(
            row["detected"]
            for row in scores
        ),
    )

    check(
        "Decision process deterministic",
        decisions == build_decisions(
            scores,
            frames,
            allowed_actions,
        ),
    )

    check(
        "No future data required for earlier decisions",
        decisions[:600] == build_decisions(
            [
                row for row in scores
                if row["tick"] < 60
            ],
            frames[:60],
            allowed_actions,
        ),
    )


def markdown_report(result):
    metrics = result["metrics"]

    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V22.3 - Multi-Agent Defense Decision Engine",
        "",
        f"Status: {result['status']}",
        f"Checks passed: {result['checks_passed']}",
        f"Checks failed: {result['checks_failed']}",
        "",
        "### Analytical roles",
        "",
        "1. Threat Assessment Agent",
        "2. Defense Strategy Agent",
        "3. Decision Validation Supervisor",
        "",
        "These are deterministic software roles.",
        "They are not deployed autonomous AI agents.",
        "",
        "### Research results",
        "",
        f"- Simulation ticks: {metrics['ticks']}",
        f"- Network nodes: {metrics['nodes']}",
        f"- Evaluated decisions: {metrics['decisions']}",
        f"- Adaptive detections: {metrics['adaptive_detections']}",
        f"- Human-approval recommendations: {metrics['human_approval_required']}",
        "",
        "### Simulated decisions",
        "",
        "| Action | Count |",
        "|---|---:|",
    ]

    for action, count in sorted(
        metrics["action_counts"].items()
    ):
        lines.append(
            f"| {action} | {count} |"
        )

    lines += [
        "",
        "### Controls",
        "",
        "- All actions are proposals only.",
        "- No firewall changes.",
        "- No live node isolation.",
        "- Human approval is required for disruptive proposals.",
        "- Decision IDs and source fingerprints are recorded.",
        "- Synthetic injected markers are excluded from decision logic.",
        "",
        "### Limitations",
        "",
        "- Synthetic telemetry only.",
        "- Rule-based analytical roles, no LLM execution.",
        "- Evidence scores are heuristics, not attack probabilities.",
        "- Shared frame context is not node-specific proof.",
        "- No causal benefit of defense actions established.",
        "- No real-world defense effectiveness measured.",
        "",
        "### Next stage",
        "",
        "V22.4 - Defense Strategy Simulation",
        "",
    ]

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V22.3 - MULTI-AGENT DEFENSE DECISION ENGINE")
    print("=" * 70)

    V22.mkdir(
        parents=True,
        exist_ok=True,
    )

    architecture = read_json(
        ARCH_FILE
    )

    detector = read_json(
        DETECTOR_FILE
    )

    intelligence = read_json(
        INTELLIGENCE_FILE
    )

    csv_rows = read_csv(
        SCORES_FILE
    )

    frames = validate_sources(
        architecture,
        detector,
        intelligence,
    )

    scores = normalize_scores(
        csv_rows,
        frames,
    )

    check(
        "V22.2 observation count agrees",
        len(scores) == detector.get(
            "metrics", {}
        ).get("node_observations"),
    )

    check(
        "V22.2 detection total agrees",
        sum(
            row["detected"]
            for row in scores
        ) == detector.get(
            "metrics", {}
        ).get("adaptive_detections"),
    )

    if not all(
        item["passed"]
        for item in CHECKS
    ):
        raise ValueError(
            "Input consistency validation failed"
        )

    allowed_actions = {
        action["id"]
        for action in architecture[
            "architecture"
        ]["defense_actions"]
    }

    decisions = build_decisions(
        scores,
        frames,
        allowed_actions,
    )

    timeline = build_timeline(
        decisions,
        frames,
    )

    validate_results(
        decisions,
        timeline,
        scores,
        frames,
        allowed_actions,
    )

    counts = Counter(
        item["final_action"]
        for item in decisions
    )

    metrics = {
        "ticks": len(frames),
        "nodes": len(frames[0]["nodes"]),
        "decisions": len(decisions),
        "adaptive_detections": sum(
            item["adaptive_detection"]
            for item in decisions
        ),
        "human_approval_required": sum(
            item["human_approval_required"]
            for item in decisions
        ),
        "action_counts": {
            action: counts[action]
            for action in sorted(ACTIONS)
        },
        "agent_roles": len(AGENTS),
        "real_actions_executed": 0,
        "trained_ai_agents_used": False,
    }

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "DEFENSE_DECISION_PASS"
        if failed == 0
        else "DEFENSE_DECISION_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V22.3",
        "module": "Multi-Agent Defense Decision Engine",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "real_actions_executed": 0,
        "trained_ai_agents_used": False,
        "agent_roles": list(AGENTS),
        "metrics": metrics,
        "source_sha256": {
            "architecture": sha256(
                ARCH_FILE
            ),
            "detector_report": sha256(
                DETECTOR_FILE
            ),
            "detector_scores": sha256(
                SCORES_FILE
            ),
            "intelligence": sha256(
                INTELLIGENCE_FILE
            ),
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "next_stage": (
            "V22.4 Defense Strategy Simulation"
        ),
    }

    write_json(
        OUTPUT_JSON,
        result,
    )

    if failed == 0:
        write_csv(
            OUTPUT_CSV,
            decisions,
        )

        write_json(
            OUTPUT_TIMELINE,
            {
                "version": "V22.3",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "ticks": len(timeline),
                "timeline": timeline,
            },
        )

        OUTPUT_MD.write_text(
            markdown_report(result),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V22.3 DEFENSE DECISION RESULTS")
    print("=" * 70)

    print(
        "NETWORK NODES:",
        metrics["nodes"],
    )
    print(
        "SIMULATION TICKS:",
        metrics["ticks"],
    )
    print(
        "DECISIONS EVALUATED:",
        metrics["decisions"],
    )
    print(
        "AGENT ROLES:",
        metrics["agent_roles"],
    )
    print(
        "HUMAN APPROVAL REQUIRED:",
        metrics["human_approval_required"],
    )
    print(
        "REAL ACTIONS EXECUTED:",
        metrics["real_actions_executed"],
    )
    print(
        "CHECKS PASSED:",
        passed,
    )
    print(
        "CHECKS FAILED:",
        failed,
    )
    print(
        "JSON REPORT:",
        OUTPUT_JSON,
    )
    print(
        "V22.3 RESULT:",
        status,
    )

    print("=" * 70)

    return (
        0 if failed == 0 else 1
    )


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as error:
        print(
            "V22.3 FAILED:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
