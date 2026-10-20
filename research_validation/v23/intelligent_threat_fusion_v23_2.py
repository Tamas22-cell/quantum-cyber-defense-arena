
"""
QUANTUM CYBER DEFENSE ARENA
V23.2 - INTELLIGENT THREAT FUSION ENGINE

Sources:
- V23.1 validated research architecture
- V22.5 simulated defense dashboard frames
- V22.2 adaptive detection scores
- V22.3 simulated defense decisions

Combines node risk, adaptive anomaly evidence,
and same-node synthetic threat alerts.

Outputs:
- intelligent_threat_fusion_v23_2_results.json
- intelligent_threat_fusion_v23_2_events.csv
- intelligent_threat_fusion_v23_2_timeline.json
- INTELLIGENT_THREAT_FUSION_V23_2.md

No trained AI model, no network changes.
Python standard library only.
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
V23 = ROOT / "research_validation" / "v23"

ARCH = V23 / (
    "advanced_cyber_defense_architecture_v23_1_results.json"
)
FRAMES = ROOT / (
    "frontend/public/v22/defense_data.json"
)
SCORES = V22 / (
    "adaptive_threat_detection_v22_2_scores.csv"
)
DECISIONS = V22 / (
    "multi_agent_defense_decision_v22_3_decisions.csv"
)
DETECTOR_REPORT = V22 / (
    "adaptive_threat_detection_v22_2_results.json"
)
DECISION_REPORT = V22 / (
    "multi_agent_defense_decision_v22_3_results.json"
)

OUTPUT_JSON = V23 / (
    "intelligent_threat_fusion_v23_2_results.json"
)
OUTPUT_CSV = V23 / (
    "intelligent_threat_fusion_v23_2_events.csv"
)
OUTPUT_TIMELINE = V23 / (
    "intelligent_threat_fusion_v23_2_timeline.json"
)
OUTPUT_MD = V23 / (
    "INTELLIGENT_THREAT_FUSION_V23_2.md"
)

CHECKS = []

RISK_WEIGHT = 0.55
DETECTION_WEIGHT = 0.25
ALERT_WEIGHT = 0.20


def check(name, condition, detail=""):
    passed = bool(condition)

    CHECKS.append({
        "name": name,
        "passed": passed,
        "detail": str(detail),
    })

    print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if not passed and detail:
        print("      ", detail)

    return passed


def read_json(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))

    with path.open("r", encoding="utf-8-sig") as file:
        result = json.load(file)

    if not isinstance(result, dict):
        raise ValueError("Expected JSON object")

    return result


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))

    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)
        records = list(reader)

    if not records:
        raise ValueError(f"Empty CSV: {path.name}")

    return records


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(
            lambda: file.read(1024 * 1024), b""
        ):
            digest.update(block)

    return digest.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            value,
            file,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )


def write_csv(path, records):
    if not records:
        raise ValueError("No fusion events generated")

    with path.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(records[0]),
        )
        writer.writeheader()
        writer.writerows(records)


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


def rounded(value):
    return round(float(value), 6)


def validate_sources(arch, frames, detector, decision):
    check(
        "V23.1 architecture passed",
        arch.get("version") == "V23.1"
        and arch.get("status")
        == "ADVANCED_CYBER_DEFENSE_ARCHITECTURE_PASS"
        and arch.get("checks_failed") == 0,
    )

    check(
        "V22.5 dashboard source passed",
        frames.get("version") == "V22.5"
        and frames.get("status") == "DEFENSE_DASHBOARD_PASS"
        and frames.get("simulation_mode") is True
        and frames.get("is_live") is False,
    )

    check(
        "V22.2 detector passed",
        detector.get("version") == "V22.2"
        and detector.get("status")
        == "ADAPTIVE_THREAT_DETECTION_PASS"
        and detector.get("checks_failed") == 0,
    )

    check(
        "V22.3 decision engine passed",
        decision.get("version") == "V22.3"
        and decision.get("status") == "DEFENSE_DECISION_PASS"
        and decision.get("checks_failed") == 0,
    )

    check(
        "V23.1 source data fingerprint valid",
        arch.get("source_manifest", {})
        .get("frames", {})
        .get("sha256") == sha256(FRAMES),
    )

    check(
        "V22.3 detector score fingerprint valid",
        decision.get("source_sha256", {})
        .get("detector_scores") == sha256(SCORES),
    )

    check(
        "V22.2 input is synthetic only",
        detector.get("simulation_mode") is True
        and detector.get("external_actions_enabled") is False,
    )

    check(
        "V22.3 input is synthetic only",
        decision.get("simulation_mode") is True
        and decision.get("real_actions_executed") == 0,
    )

    items = frames.get("frames", [])

    check(
        "120 simulation frames available",
        len(items) == 120,
    )

    check(
        "Simulation ticks continuous",
        [item.get("tick") for item in items]
        == list(range(120)),
    )

    check(
        "Network topology consistent",
        all(
            len(item.get("nodes", [])) == 10
            and len(item.get("links", [])) == 11
            for item in items
        ),
    )

    if not all(c["passed"] for c in CHECKS):
        raise ValueError("Source validation failed")

    return items


def create_index(rows, frame_map, record_type):
    indexed = {}

    for row in rows:
        tick = int(row["tick"])
        node_id = row["node_id"]
        key = (tick, node_id)

        if tick not in frame_map:
            raise ValueError(f"Unknown tick: {tick}")

        node_ids = {
            n["id"]
            for n in frame_map[tick]["nodes"]
        }

        if node_id not in node_ids or key in indexed:
            raise ValueError(
                f"Invalid {record_type} identity: {key}"
            )

        indexed[key] = row

    return indexed


def priority_level(score):
    if score >= 0.90:
        return "critical"
    if score >= 0.75:
        return "high"
    if score >= 0.50:
        return "medium"
    if score >= 0.25:
        return "low"
    return "normal"


def fuse(frames, score_index, decision_index):
    """
    Combine same-tick, same-node evidence.

    Fusion uses:
      55% current synthetic node risk
      25% adaptive anomaly strength
      20% maximum matching node alert risk

    Synthetic injected markers are NOT used as
    an input to the fusion score.

    Weights are fixed research assumptions.
    Fused score is NOT a probability of attack.
    """

    output = []

    for frame in frames:
        tick = frame["tick"]

        alerts_by_node = defaultdict(list)

        for alert in frame["source_alerts"]:
            node_id = alert["node_id"]

            alerts_by_node[node_id].append(alert)

        for node in sorted(
            frame["nodes"],
            key=lambda item: item["id"],
        ):
            node_id = node["id"]
            key = (tick, node_id)

            score = score_index[key]
            decision = decision_index[key]

            if (
                score["timestamp"] != frame["timestamp"]
                or decision["timestamp"] != frame["timestamp"]
            ):
                raise ValueError(
                    f"Timestamp mismatch: {key}"
                )

            risk = number(node["risk_score"])
            score_risk = number(score["risk_score"])
            decision_risk = number(decision["node_risk"])

            if not 0 <= risk <= 1:
                raise ValueError("Invalid node risk")

            if not math.isclose(
                risk, score_risk, abs_tol=0.000002
            ):
                raise ValueError(
                    f"Detector risk mismatch: {key}"
                )

            if not math.isclose(
                risk, decision_risk, abs_tol=0.000002
            ):
                raise ValueError(
                    f"Decision risk mismatch: {key}"
                )

            detected = boolean(
                score["detected_anomaly"]
            )

            threshold = number(
                score["adaptive_threshold"]
            )

            anomaly_score = number(
                score["anomaly_score"]
            )

            if threshold <= 0 or anomaly_score < 0:
                raise ValueError("Invalid anomaly score")

            if detected != boolean(
                decision["adaptive_detection"]
            ):
                raise ValueError(
                    f"Detection mismatch: {key}"
                )

            anomaly_strength = (
                min(1.0, anomaly_score / threshold)
                if boolean(score["baseline_ready"])
                else 0.0
            )

            matching_alerts = alerts_by_node[
                node_id
            ]

            alert_risks = [
                number(alert["risk_score"])
                for alert in matching_alerts
            ]

            if any(
                not 0 <= value <= 1
                for value in alert_risks
            ):
                raise ValueError(
                    f"Invalid alert risk: {key}"
                )

            alert_strength = max(
                alert_risks,
                default=0.0,
            )

            fused_score = (
                RISK_WEIGHT * risk
                + DETECTION_WEIGHT * anomaly_strength
                + ALERT_WEIGHT * alert_strength
            )

            fused_score = min(
                1.0,
                max(0.0, fused_score),
            )

            # Preserve exact evidence lineage.
            alert_ids = sorted(
                str(alert["event_id"])
                for alert in matching_alerts
            )

            output.append({
                "fusion_id": (
                    f"V23-FUSION-{tick:03d}-{node_id}"
                ),
                "tick": tick,
                "timestamp": frame["timestamp"],
                "node_id": node_id,
                "node_risk": rounded(risk),
                "adaptive_detection": detected,
                "anomaly_score": rounded(anomaly_score),
                "anomaly_strength": rounded(
                    anomaly_strength
                ),
                "matching_alert_count": len(
                    matching_alerts
                ),
                "matching_alert_ids": ";".join(
                    alert_ids
                ),
                "alert_strength": rounded(
                    alert_strength
                ),
                "fusion_score": rounded(
                    fused_score
                ),
                "priority": priority_level(
                    fused_score
                ),
                "v22_proposed_action": decision[
                    "final_action"
                ],
                "human_approval_required": boolean(
                    decision["human_approval_required"]
                ),
                "evidence_sources": (
                    "V22.5_network;"
                    "V22.2_detector;"
                    "V22.3_decision;"
                    "V22.5_same_node_alerts"
                ),
                "simulation_mode": True,
                "real_action_executed": False,
                "trained_ai_model_used": False,
            })

    return output


def make_timeline(events, frames):
    by_tick = defaultdict(list)

    for event in events:
        by_tick[event["tick"]].append(
            event
        )

    timeline = []

    for frame in frames:
        tick = frame["tick"]
        group = by_tick[tick]

        priorities = Counter(
            row["priority"]
            for row in group
        )

        timeline.append({
            "tick": tick,
            "timestamp": frame["timestamp"],
            "evaluated_nodes": len(group),
            "mean_fusion_score": rounded(
                sum(
                    row["fusion_score"]
                    for row in group
                ) / len(group)
            ),
            "maximum_fusion_score": max(
                row["fusion_score"]
                for row in group
            ),
            "adaptive_detections": sum(
                row["adaptive_detection"]
                for row in group
            ),
            "high_priority_nodes": [
                row["node_id"]
                for row in group
                if row["priority"] in {
                    "high", "critical"
                }
            ],
            "priority_counts": {
                priority: priorities[priority]
                for priority in (
                    "normal",
                    "low",
                    "medium",
                    "high",
                    "critical",
                )
            },
            "human_approval_required": sum(
                row["human_approval_required"]
                for row in group
            ),
            "simulation_mode": True,
            "real_actions_executed": 0,
        })

    return timeline


def validate_results(events, timeline, frames):
    check(
        "1200 fused node observations",
        len(events) == 1200,
    )

    check(
        "All fusion IDs unique",
        len({
            row["fusion_id"]
            for row in events
        }) == 1200,
    )

    check(
        "Fusion scores bounded to zero and one",
        all(
            0 <= row["fusion_score"] <= 1
            for row in events
        ),
    )

    check(
        "Every fused priority matches score",
        all(
            row["priority"]
            == priority_level(row["fusion_score"])
            for row in events
        ),
    )

    check(
        "All events have source provenance",
        all(
            "V22.2_detector" in row["evidence_sources"]
            and "V22.3_decision" in row["evidence_sources"]
            for row in events
        ),
    )

    check(
        "No real actions executed",
        all(
            row["real_action_executed"] is False
            for row in events
        ),
    )

    check(
        "No trained AI model falsely claimed",
        all(
            row["trained_ai_model_used"] is False
            for row in events
        ),
    )

    check(
        "120 timeline frames",
        len(timeline) == 120
        and [
            row["tick"]
            for row in timeline
        ] == list(range(120)),
    )

    check(
        "Ten nodes per timeline tick",
        all(
            row["evaluated_nodes"] == 10
            for row in timeline
        ),
    )

    check(
        "Priority totals consistent",
        sum(
            sum(row["priority_counts"].values())
            for row in timeline
        ) == len(events),
    )

    check(
        "Detection totals match source dashboard",
        sum(
            row["adaptive_detections"]
            for row in timeline
        ) == sum(
            frame["adaptive_detections"]
            for frame in frames
        ),
    )

    check(
        "Approval totals match source dashboard",
        sum(
            row["human_approval_required"]
            for row in timeline
        ) == sum(
            frame["human_approval_required"]
            for frame in frames
        ),
    )


def make_document(report):
    metrics = report["metrics"]

    return f"""# Quantum Cyber Defense Arena

## V23.2 - Intelligent Threat Fusion Engine

**Status:** {report['status']}

**Checks passed:** {report['checks_passed']}

**Checks failed:** {report['checks_failed']}

### Research data

- Simulation ticks: {metrics['ticks']}
- Network nodes: {metrics['nodes']}
- Fused observations: {metrics['fused_observations']}
- High-priority observations: {metrics['high_priority_observations']}
- Critical-priority observations: {metrics['critical_priority_observations']}

### Evidence fusion

The module combines four research inputs:

1. Synthetic node risk
2. Adaptive statistical detection
3. Same-node synthetic alerts
4. Auditable simulated decisions

### Fixed fusion weights

- Node risk: {RISK_WEIGHT}
- Adaptive anomaly strength: {DETECTION_WEIGHT}
- Matching alert strength: {ALERT_WEIGHT}

Scores are heuristic research indices,
not calibrated attack probabilities.

No synthetic injection labels are used
as inputs to the scoring formula.

### Research controls

- Read-only source processing
- SHA-256 input provenance
- Node and timestamp alignment
- Deterministic calculations
- No real defensive actions
- No trained AI model claimed

### Limitations

All observations are synthetic.
The evidence sources are not independent.
The scoring weights are researcher-selected.
No real attack detection performance is established.

### Next stage

V23.3 - Adaptive Defense Policy Optimization
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V23.2 - INTELLIGENT THREAT FUSION")
    print("=" * 70)

    V23.mkdir(parents=True, exist_ok=True)

    architecture = read_json(ARCH)
    data = read_json(FRAMES)
    detector = read_json(DETECTOR_REPORT)
    decision = read_json(DECISION_REPORT)

    frames = validate_sources(
        architecture,
        data,
        detector,
        decision,
    )

    score_rows = read_csv(SCORES)
    decision_rows = read_csv(DECISIONS)

    frame_map = {
        frame["tick"]: frame
        for frame in frames
    }

    score_index = create_index(
        score_rows,
        frame_map,
        "detector",
    )

    decision_index = create_index(
        decision_rows,
        frame_map,
        "decision",
    )

    expected_keys = {
        (frame["tick"], node["id"])
        for frame in frames
        for node in frame["nodes"]
    }

    check(
        "All 1200 detector keys available",
        set(score_index) == expected_keys,
    )

    check(
        "All 1200 decision keys available",
        set(decision_index) == expected_keys,
    )

    check(
        "Detector source count matches report",
        len(score_rows)
        == detector["metrics"]["node_observations"],
    )

    check(
        "Decision source count matches report",
        len(decision_rows)
        == decision["metrics"]["decisions"],
    )

    if not all(c["passed"] for c in CHECKS):
        raise ValueError(
            "Research source consistency failed"
        )

    events = fuse(
        frames,
        score_index,
        decision_index,
    )

    timeline = make_timeline(
        events,
        frames,
    )

    validate_results(
        events,
        timeline,
        frames,
    )

    check(
        "Fusion results reproducible",
        events == fuse(
            frames,
            score_index,
            decision_index,
        ),
    )

    # Prefix consistency check: later frames
    # cannot change earlier fusion results.
    prefix_frames = frames[:60]

    prefix_events = fuse(
        prefix_frames,
        score_index,
        decision_index,
    )

    check(
        "No future frames needed for earlier fusion",
        events[:len(prefix_events)] == prefix_events,
    )

    counts = Counter(
        row["priority"]
        for row in events
    )

    metrics = {
        "ticks": 120,
        "nodes": 10,
        "fused_observations": len(events),
        "adaptive_detections": sum(
            row["adaptive_detection"]
            for row in events
        ),
        "high_priority_observations": counts["high"],
        "critical_priority_observations": counts[
            "critical"
        ],
        "priority_counts": dict(counts),
        "same_node_alert_matches": sum(
            row["matching_alert_count"]
            for row in events
        ),
        "real_actions_executed": 0,
        "trained_ai_model_used": False,
    }

    passed = sum(
        item["passed"]
        for item in CHECKS
    )
    failed = len(CHECKS) - passed

    status = (
        "INTELLIGENT_THREAT_FUSION_PASS"
        if failed == 0
        else "INTELLIGENT_THREAT_FUSION_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V23.2",
        "module": "Intelligent Threat Fusion Engine",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "external_actions_enabled": False,
        "trained_ai_model_used": False,
        "fusion_weights": {
            "node_risk": RISK_WEIGHT,
            "adaptive_anomaly": DETECTION_WEIGHT,
            "same_node_alert": ALERT_WEIGHT,
        },
        "metrics": metrics,
        "source_sha256": {
            "architecture": sha256(ARCH),
            "frames": sha256(FRAMES),
            "detector_report": sha256(DETECTOR_REPORT),
            "detector_scores": sha256(SCORES),
            "decision_report": sha256(DECISION_REPORT),
            "decision_events": sha256(DECISIONS),
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "next_stage": (
            "V23.3 Adaptive Defense Policy Optimization"
        ),
    }

    write_json(
        OUTPUT_JSON,
        result,
    )

    if failed == 0:
        write_csv(
            OUTPUT_CSV,
            events,
        )

        write_json(
            OUTPUT_TIMELINE,
            {
                "version": "V23.2",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "ticks": len(timeline),
                "timeline": timeline,
            },
        )

        OUTPUT_MD.write_text(
            make_document(result),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V23.2 INTELLIGENT THREAT FUSION RESULTS")
    print("=" * 70)
    print("NETWORK NODES:", metrics["nodes"])
    print("SIMULATION TICKS:", metrics["ticks"])
    print(
        "FUSED OBSERVATIONS:",
        metrics["fused_observations"],
    )
    print(
        "ADAPTIVE DETECTIONS:",
        metrics["adaptive_detections"],
    )
    print(
        "HIGH PRIORITY:",
        metrics["high_priority_observations"],
    )
    print(
        "CRITICAL PRIORITY:",
        metrics["critical_priority_observations"],
    )
    print("REAL ACTIONS EXECUTED: 0")
    print("CHECKS PASSED:", passed)
    print("CHECKS FAILED:", failed)
    print("JSON REPORT:", OUTPUT_JSON)
    print("V23.2 RESULT:", status)
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as error:
        print(
            "V23.2 FAILED:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
