
"""
QUANTUM CYBER DEFENSE ARENA
V21.3 - MULTI-AGENT THREAT CORRELATION

Combines:
- V21.1 Intelligence Architecture
- V21.2 Behavioral Anomaly Detection
- V20.3 Synthetic Threat Scenario Alerts
- V20.4 Digital Twin Frames

Three deterministic analytical roles:
1. Alert Evidence Agent
2. Behavioral Evidence Agent
3. Correlation Supervisor

No LLM execution, autonomous attacks or external actions.

Outputs:
- multi_agent_threat_correlation_v21_3_results.json
- multi_agent_threat_correlation_v21_3_events.csv
- multi_agent_threat_correlation_v21_3_timeline.json
- MULTI_AGENT_THREAT_CORRELATION_V21_3.md
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
V20 = ROOT / "research_validation" / "v20"
V21 = ROOT / "research_validation" / "v21"

SOURCES = {
    "architecture": V21 / (
        "threat_intelligence_architecture_v21_1_results.json"
    ),
    "behavior_report": V21 / (
        "behavioral_anomaly_detection_v21_2_results.json"
    ),
    "behavior_scores": V21 / (
        "behavioral_anomaly_detection_v21_2_scores.csv"
    ),
    "threat_report": V20 / (
        "ai_threat_scenario_v20_3_results.json"
    ),
    "threat_events": V20 / (
        "ai_threat_scenario_v20_3_events.csv"
    ),
    "frames": V20 / (
        "event_streaming_v20_4_frames.json"
    ),
}

OUTPUT_JSON = V21 / (
    "multi_agent_threat_correlation_v21_3_results.json"
)
OUTPUT_CSV = V21 / (
    "multi_agent_threat_correlation_v21_3_events.csv"
)
OUTPUT_TIMELINE = V21 / (
    "multi_agent_threat_correlation_v21_3_timeline.json"
)
OUTPUT_MD = V21 / (
    "MULTI_AGENT_THREAT_CORRELATION_V21_3.md"
)

TIME_WINDOW = 2
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
        print("      ", detail)
    return passed


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024), b""
        ):
            digest.update(block)
    return digest.hexdigest()


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid JSON: {path.name}")
    return data


def read_csv(path):
    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames or []
    if not rows or not columns:
        raise ValueError(f"Empty CSV: {path.name}")
    if len(columns) != len(set(columns)):
        raise ValueError(f"Duplicate columns: {path.name}")
    return rows


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(
            data, f, indent=2,
            ensure_ascii=False, allow_nan=False
        )


def write_csv(path, rows):
    if not rows:
        raise ValueError("No correlation events to export")
    with path.open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=list(rows[0])
        )
        writer.writeheader()
        writer.writerows(rows)


def to_float(value):
    if isinstance(value, bool):
        raise ValueError("Boolean numeric value")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite numeric value")
    return result


def to_bool(value):
    if isinstance(value, bool):
        return value
    if str(value).lower() == "true":
        return True
    if str(value).lower() == "false":
        return False
    raise ValueError(f"Invalid boolean: {value}")


def load_sources():
    data = {}
    for name, path in SOURCES.items():
        exists = path.is_file()
        check(f"Source available: {name}", exists, str(path))
        if not exists:
            continue
        try:
            if path.suffix == ".csv":
                data[name] = read_csv(path)
            else:
                data[name] = read_json(path)
            check(f"Source readable: {name}", True)
        except (OSError, ValueError, TypeError) as exc:
            check(
                f"Source readable: {name}",
                False, str(exc)
            )
    return data


def validate_sources(data):
    arch = data["architecture"]
    behavior = data["behavior_report"]
    threat = data["threat_report"]
    frames = data["frames"]

    expected = [
        ("architecture", "V21.1",
         "THREAT_INTELLIGENCE_ARCHITECTURE_PASS"),
        ("behavior_report", "V21.2",
         "BEHAVIORAL_ANOMALY_PASS"),
        ("threat_report", "V20.3",
         "THREAT_SCENARIO_PASS"),
        ("frames", "V20.4", "EVENT_STREAMING_PASS"),
    ]

    for name, version, status in expected:
        report = data[name]
        check(
            f"{name}: correct version and status",
            report.get("version") == version
            and report.get("status") == status
        )
        if name != "frames":
            check(
                f"{name}: zero failed checks",
                report.get("checks_failed") == 0
            )

    check(
        "Behavioral source fingerprints",
        behavior.get("source_sha256", {}).get(
            "architecture"
        ) == sha256(SOURCES["architecture"])
        and behavior.get("source_sha256", {}).get(
            "frames"
        ) == sha256(SOURCES["frames"])
    )

    check(
        "V20 threat source is current",
        threat.get("source_sha256", {}).get(
            "architecture"
        ) == sha256(
            V20 /
            "digital_twin_architecture_v20_1_results.json"
        )
    )

    check(
        "Research mode is simulated",
        arch.get("simulation_mode") is True
        and frames.get("simulation_mode") is True
        and frames.get("is_live") is False
        and behavior.get("simulation_mode") is True
        and threat.get("simulation_mode") is True
    )

    check(
        "No autonomous external actions",
        arch.get("external_actions_enabled") is False
        and behavior.get("external_actions_enabled") is False
        and threat.get("external_actions_enabled") is False
    )

    frame_items = frames.get("frames", [])
    check(
        "120 ordered source frames",
        len(frame_items) == 120
        and [f.get("sequence") for f in frame_items]
        == list(range(120))
    )

    check(
        "Ten nodes per frame",
        all(
            len(f.get("network", {}).get("nodes", []))
            == 10 for f in frame_items
        )
    )

    check(
        "Eleven links per frame",
        all(
            len(f.get("network", {}).get("links", []))
            == 11 for f in frame_items
        )
    )


def normalize_behavior(rows, frames):
    frame_count = len(frames)
    expected_ids = {
        item["id"]
        for item in frames[0]["network"]["nodes"]
    }
    records = []
    seen = set()

    for row in rows:
        tick = int(row["tick"])
        node = row["node_id"]
        key = (tick, node)

        if (
            tick < 0
            or tick >= frame_count
            or node not in expected_ids
            or key in seen
        ):
            raise ValueError(
                f"Invalid behavioral identity: {key}"
            )

        seen.add(key)

        score = to_float(row["anomaly_score"])
        if score < 0:
            raise ValueError("Negative anomaly score")

        records.append({
            "tick": tick,
            "node_id": node,
            "score": score,
            "detected": to_bool(
                row["detected_anomaly"]
            ),
            "baseline_ready": to_bool(
                row["baseline_ready"]
            ),
            "injected": to_bool(
                row["injected_anomaly"]
            ),
        })

    expected_keys = {
        (tick, node)
        for tick in range(frame_count)
        for node in expected_ids
    }

    check(
        "All behavioral node observations present",
        seen == expected_keys
    )

    check(
        "Detected behavior requires ready baseline",
        all(
            not r["detected"] or r["baseline_ready"]
            for r in records
        )
    )

    check(
        "Behavior scores are nonnegative",
        all(r["score"] >= 0 for r in records)
    )

    return records


def normalize_alerts(rows, frames):
    frame_count = len(frames)
    ids = set()
    records = []

    for row in rows:
        event_id = row["event_id"]
        tick = int(row["tick"])
        node = row["node_id"]

        if (
            event_id in ids
            or tick < 0
            or tick >= frame_count
        ):
            raise ValueError(
                f"Invalid alert: {event_id}"
            )

        ids.add(event_id)
        frame_nodes = {
            n["id"]
            for n in frames[tick]["network"]["nodes"]
        }
        if node not in frame_nodes:
            raise ValueError(
                f"Unknown alert node: {node}"
            )

        risk = to_float(
            row["enriched_risk_score"]
        )
        if not 0 <= risk <= 1:
            raise ValueError("Invalid alert risk")

        if not to_bool(row["synthetic"]):
            raise ValueError("Non-synthetic alert")

        records.append({
            "event_id": event_id,
            "tick": tick,
            "node_id": node,
            "scenario_id": row["scenario_id"],
            "category": row["threat_category"],
            "risk": risk,
            "injected": to_bool(
                row["injected_anomaly"]
            ),
        })

    records.sort(
        key=lambda x: (
            x["tick"], x["node_id"], x["event_id"]
        )
    )

    check(
        "Alert identifiers unique",
        len(ids) == len(records)
    )
    check(
        "All alert risks bounded",
        all(0 <= x["risk"] <= 1 for x in records)
    )

    return records


def correlate(behavior, alerts):
    """
    Correlate alert evidence with behavior evidence.

    Same-node exact tick: strongest temporal match.
    Same-node +/- 2 ticks: nearby temporal match.
    Otherwise: alert evidence only.

    Correlation is not proof of a cyberattack.
    """
    behavior_by_node = defaultdict(list)
    exact = {}

    for item in behavior:
        behavior_by_node[item["node_id"]].append(
            item
        )
        exact[
            (item["tick"], item["node_id"])
        ] = item

    for items in behavior_by_node.values():
        items.sort(key=lambda x: x["tick"])

    output = []

    for alert in alerts:
        tick = alert["tick"]
        node = alert["node_id"]

        exact_row = exact.get((tick, node))
        candidates = [
            item
            for item in behavior_by_node[node]
            if item["detected"]
            and abs(item["tick"] - tick) <= TIME_WINDOW
        ]

        candidates.sort(
            key=lambda x: (
                abs(x["tick"] - tick),
                -x["score"],
                x["tick"],
            )
        )

        match = candidates[0] if candidates else None

        if match is None:
            level = "ALERT_ONLY"
            time_distance = None
            behavior_score = 0.0

        else:
            time_distance = abs(
                match["tick"] - tick
            )
            behavior_score = match["score"]

            if time_distance == 0:
                level = "SAME_TICK_CORRELATION"
            else:
                level = "NEARBY_TICK_CORRELATION"

        # This is an ordinal research score,
        # not a calibrated attack probability.
        match_bonus = (
            0.20 if level == "SAME_TICK_CORRELATION"
            else 0.10
            if level == "NEARBY_TICK_CORRELATION"
            else 0.0
        )

        score = min(
            1.0,
            alert["risk"] * 0.80 + match_bonus
        )

        output.append({
            "event_id": alert["event_id"],
            "tick": tick,
            "node_id": node,
            "scenario_id": alert["scenario_id"],
            "category": alert["category"],
            "source_alert_risk": round(
                alert["risk"], 6
            ),
            "correlation_level": level,
            "matched_behavior_tick": (
                match["tick"] if match else ""
            ),
            "time_distance_ticks": (
                time_distance
                if time_distance is not None
                else ""
            ),
            "behavior_score": round(
                behavior_score, 6
            ),
            "exact_tick_behavior_detected": (
                exact_row["detected"]
                if exact_row else False
            ),
            "correlation_score": round(
                score, 6
            ),
            "injected_anomaly": alert["injected"],
            "evidence_sources": (
                "V20.3_alert;V21.2_behavior"
                if match
                else "V20.3_alert"
            ),
            "simulation_mode": True,
            "analysis_method": "rule_based_correlation",
        })

    return output


def build_timeline(correlated, behavior, frames):
    alerts_by_tick = defaultdict(list)
    behavior_by_tick = defaultdict(list)

    for row in correlated:
        alerts_by_tick[row["tick"]].append(row)

    for row in behavior:
        if row["detected"]:
            behavior_by_tick[row["tick"]].append(
                row
            )

    timeline = []

    for frame in frames:
        tick = frame["sequence"]
        alerts = alerts_by_tick[tick]
        detected = behavior_by_tick[tick]

        timeline.append({
            "tick": tick,
            "timestamp": frame["timestamp"],
            "source_alerts": len(alerts),
            "behavioral_detections": len(detected),
            "same_tick_correlations": sum(
                item["correlation_level"]
                == "SAME_TICK_CORRELATION"
                for item in alerts
            ),
            "nearby_tick_correlations": sum(
                item["correlation_level"]
                == "NEARBY_TICK_CORRELATION"
                for item in alerts
            ),
            "alert_only": sum(
                item["correlation_level"]
                == "ALERT_ONLY"
                for item in alerts
            ),
            "maximum_correlation_score": round(
                max(
                    (
                        item["correlation_score"]
                        for item in alerts
                    ),
                    default=0.0,
                ), 6
            ),
            "synthetic_injection": bool(
                frame["metrics"]["anomaly_injected"]
            ),
        })

    return timeline


def validate_results(
    correlated, alerts, behavior,
    timeline, frames
):
    check(
        "All source alerts preserved",
        len(correlated) == len(alerts)
        and {
            x["event_id"] for x in correlated
        } == {
            x["event_id"] for x in alerts
        }
    )

    check(
        "Correlation scores bounded",
        all(
            0 <= x["correlation_score"] <= 1
            for x in correlated
        )
    )

    check(
        "Correlation levels supported",
        all(
            x["correlation_level"] in {
                "ALERT_ONLY",
                "SAME_TICK_CORRELATION",
                "NEARBY_TICK_CORRELATION",
            }
            for x in correlated
        )
    )

    check(
        "Matched time differences valid",
        all(
            x["correlation_level"] == "ALERT_ONLY"
            or (
                isinstance(
                    x["time_distance_ticks"], int
                )
                and 0 <= x[
                    "time_distance_ticks"
                ] <= TIME_WINDOW
            )
            for x in correlated
        )
    )

    check(
        "Exactly matched rows use zero distance",
        all(
            x["correlation_level"]
            != "SAME_TICK_CORRELATION"
            or x["time_distance_ticks"] == 0
            for x in correlated
        )
    )

    check(
        "Every correlated record is synthetic",
        all(
            x["simulation_mode"] is True
            for x in correlated
        )
    )

    check(
        "Timeline includes 120 ticks",
        len(timeline) == len(frames) == 120
    )

    check(
        "Timeline sequence continuous",
        [
            item["tick"] for item in timeline
        ] == list(range(120))
    )

    check(
        "Timeline alert totals correct",
        sum(
            item["source_alerts"]
            for item in timeline
        ) == len(correlated)
    )

    check(
        "Timeline behavior totals correct",
        sum(
            item["behavioral_detections"]
            for item in timeline
        ) == sum(
            item["detected"]
            for item in behavior
        )
    )

    check(
        "Correlation outcome counts add up",
        sum(
            item["same_tick_correlations"]
            + item["nearby_tick_correlations"]
            + item["alert_only"]
            for item in timeline
        ) == len(correlated)
    )

    check(
        "No non-finite correlation metrics",
        all(
            math.isfinite(x["correlation_score"])
            for x in correlated
        )
    )

    check(
        "Correlation reproducible",
        correlated == correlate(
            behavior, alerts
        )
    )


def make_markdown(result):
    metrics = result["metrics"]

    return f"""# Quantum Cyber Defense Arena

## V21.3 - Multi-Agent Threat Correlation

**Status:** {result['status']}

**Validation:** {result['checks_passed']} passed,
{result['checks_failed']} failed.

### Research inputs

- V20.3 synthetic threat alerts
- V21.2 statistical behavioral anomalies
- V20.4 digital twin replay frames
- V21.1 architecture

### Correlation results

| Metric | Value |
|---|---:|
| Simulation ticks | {metrics['ticks']} |
| Source alerts | {metrics['source_alerts']} |
| Behavioral detections | {metrics['behavioral_detections']} |
| Same-tick correlations | {metrics['same_tick_correlations']} |
| Nearby-tick correlations | {metrics['nearby_tick_correlations']} |
| Alert-only events | {metrics['alert_only']} |
| Maximum correlation score | {metrics['maximum_correlation_score']} |

### Correlation method

Three deterministic analytical roles:
1. Alert Evidence Agent
2. Behavioral Evidence Agent
3. Correlation Supervisor

Alerts are matched to same-node behavioral
detections, either at the same tick or within
a +/- {TIME_WINDOW} tick research window.

Scores are ordinal heuristics, not
calibrated probabilities of attack.

### Limitations

- Only synthetic network data are used
- No trained or LLM-based agents execute
- No real attacks are independently verified
- Temporal proximity is not causal proof
- Synthetic risk inputs may share provenance
- No real-world threat detection accuracy measured
- No autonomous external actions

### Next stage

V21.4 - Predictive Risk Analytics
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V21.3 - MULTI-AGENT THREAT CORRELATION")
    print("=" * 70)

    V21.mkdir(parents=True, exist_ok=True)

    data = load_sources()
    correlated = []
    timeline = []
    metrics = {}
    error = None

    if len(data) == len(SOURCES):
        try:
            validate_sources(data)

            frames = data["frames"]["frames"]

            behavior = normalize_behavior(
                data["behavior_scores"], frames
            )
            alerts = normalize_alerts(
                data["threat_events"], frames
            )

            check(
                "Behavioral record count matches V21.2",
                len(behavior) == data[
                    "behavior_report"
                ]["metrics"]["observations"]
            )

            check(
                "Alert record count matches V20.3",
                len(alerts) == data[
                    "threat_report"
                ]["metrics"]["total_alerts"]
            )

            correlated = correlate(
                behavior, alerts
            )

            timeline = build_timeline(
                correlated, behavior, frames
            )

            validate_results(
                correlated, alerts,
                behavior, timeline, frames
            )

            counts = Counter(
                row["correlation_level"]
                for row in correlated
            )

            metrics = {
                "ticks": len(frames),
                "network_nodes": len(
                    frames[0]["network"]["nodes"]
                ),
                "source_alerts": len(alerts),
                "behavioral_detections": sum(
                    r["detected"] for r in behavior
                ),
                "same_tick_correlations": counts[
                    "SAME_TICK_CORRELATION"
                ],
                "nearby_tick_correlations": counts[
                    "NEARBY_TICK_CORRELATION"
                ],
                "alert_only": counts["ALERT_ONLY"],
                "maximum_correlation_score": max(
                    (
                        row["correlation_score"]
                        for row in correlated
                    ),
                    default=0.0
                ),
                "temporal_window_ticks": TIME_WINDOW,
                "method": "rule_based_correlation",
                "trained_ai_agents_used": False,
                "real_attack_accuracy_measured": False,
            }

        except (
            OSError, ValueError, KeyError,
            TypeError, IndexError
        ) as exc:
            error = f"{type(exc).__name__}: {exc}"
            check(
                "Correlation evaluation completed",
                False, error
            )
    else:
        check(
            "All source files loaded",
            False,
            f"{len(data)}/{len(SOURCES)}"
        )

    passed = sum(x["passed"] for x in CHECKS)
    failed = len(CHECKS) - passed

    status = (
        "THREAT_CORRELATION_PASS"
        if failed == 0 and metrics
        else "THREAT_CORRELATION_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V21.3",
        "module": "Multi-Agent Threat Correlation",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "execution_mode": "deterministic_read_only",
        "external_actions_enabled": False,
        "agent_roles": [
            "alert_evidence_agent",
            "behavioral_evidence_agent",
            "correlation_supervisor",
        ],
        "metrics": metrics,
        "source_sha256": {
            key: sha256(path)
            for key, path in SOURCES.items()
            if path.is_file()
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error,
        "limitations": [
            "Synthetic telemetry and alerts only.",
            "Agents are deterministic analytical roles.",
            "Temporal correlation is not causal evidence.",
            "No verified real attack labels.",
            "No real-world detection accuracy measured.",
            "No external security actions.",
        ],
        "next_stage": "V21.4 Predictive Risk Analytics",
    }

    write_json(OUTPUT_JSON, result)

    if status == "THREAT_CORRELATION_PASS":
        write_csv(OUTPUT_CSV, correlated)

        write_json(
            OUTPUT_TIMELINE,
            {
                "version": "V21.3",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "ticks": len(timeline),
                "timeline": timeline,
            }
        )

        OUTPUT_MD.write_text(
            make_markdown(result),
            encoding="utf-8"
        )

    print()
    print("=" * 70)
    print("V21.3 THREAT CORRELATION RESULTS")
    print("=" * 70)

    if metrics:
        print(
            "SIMULATION TICKS:",
            metrics["ticks"]
        )
        print(
            "SOURCE ALERTS:",
            metrics["source_alerts"]
        )
        print(
            "BEHAVIORAL DETECTIONS:",
            metrics["behavioral_detections"]
        )
        print(
            "SAME-TICK CORRELATIONS:",
            metrics["same_tick_correlations"]
        )
        print(
            "NEARBY CORRELATIONS:",
            metrics["nearby_tick_correlations"]
        )
        print(
            "ALERT-ONLY EVENTS:",
            metrics["alert_only"]
        )

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {OUTPUT_JSON}")

    if status == "THREAT_CORRELATION_PASS":
        print(f"CORRELATION CSV: {OUTPUT_CSV}")
        print(f"TIMELINE: {OUTPUT_TIMELINE}")
        print(f"RESEARCH DOCUMENT: {OUTPUT_MD}")

    print(f"V21.3 RESULT: {status}")
    print("=" * 70)

    return 0 if status == "THREAT_CORRELATION_PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(
            "V21.3 FAILED:",
            f"{type(exc).__name__}: {exc}"
        )
        sys.exit(1)
