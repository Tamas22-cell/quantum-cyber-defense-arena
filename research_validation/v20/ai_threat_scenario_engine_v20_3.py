
"""
QUANTUM CYBER DEFENSE ARENA
V20.3 - AI THREAT SCENARIO ENGINE

Reads V20.1 topology and V20.2 simulation results.

Features:
- Source integrity verification
- Synthetic threat scenario matching
- Rule-based risk evaluation
- Alert enrichment
- Synthetic event classification
- Reproducible evaluation
- JSON, CSV and Markdown exports

This is a deterministic research prototype,
not a trained AI threat detection model.

Standard library only.
No scanning or external security actions.
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

ARCH_FILE = (
    V20 / "digital_twin_architecture_v20_1_results.json"
)
SIM_FILE = (
    V20 / "network_simulation_v20_2_results.json"
)
EVENTS_FILE = (
    V20 / "network_simulation_v20_2_events.json"
)
NODES_FILE = (
    V20 / "network_simulation_v20_2_nodes.csv"
)
LINKS_FILE = (
    V20 / "network_simulation_v20_2_links.csv"
)

RESULT_FILE = (
    V20 / "ai_threat_scenario_v20_3_results.json"
)
CLASSIFIED_FILE = (
    V20 / "ai_threat_scenario_v20_3_events.csv"
)
TIMELINE_FILE = (
    V20 / "ai_threat_scenario_v20_3_timeline.json"
)
REPORT_FILE = (
    V20 / "AI_THREAT_SCENARIO_V20_3.md"
)

CHECKS = []

SEVERITY_WEIGHT = {
    "low": 0.15,
    "medium": 0.35,
    "high": 0.60,
    "critical": 0.85,
}

THREAT_CATEGORIES = {
    "traffic_anomaly",
    "reconnaissance",
    "application_anomaly",
    "access_anomaly",
    "model_alert",
}


def check(name, condition, detail=""):
    passed = bool(condition)

    CHECKS.append({
        "name": name,
        "passed": passed,
        "detail": str(detail),
    })

    print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if detail and not passed:
        print("       ", detail)

    return passed


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing required file: {path}"
        )

    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid JSON structure: {path.name}"
        )

    return data


def load_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing required CSV: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        raise ValueError(
            f"Empty CSV: {path.name}"
        )

    return rows


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def sha256_model(model):
    raw = json.dumps(
        model,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def write_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )


def write_csv(path, rows):
    if not rows:
        raise ValueError(
            "No classified records to export"
        )

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)


def clamp(value):
    return max(0.0, min(1.0, float(value)))


def rounded(value):
    return round(float(value), 6)


def risk_level(score):
    if score >= 0.90:
        return "critical"
    if score >= 0.75:
        return "high"
    if score >= 0.50:
        return "medium"
    if score >= 0.25:
        return "low"
    return "normal"


def validate_sources(architecture, simulation, events):
    check(
        "V20.1 architecture passed",
        architecture.get("version") == "V20.1"
        and architecture.get("status") == "ARCHITECTURE_PASS"
        and architecture.get("checks_failed") == 0,
    )

    check(
        "V20.2 simulation passed",
        simulation.get("version") == "V20.2"
        and simulation.get("status") == "NETWORK_SIMULATION_PASS"
        and simulation.get("checks_failed") == 0,
    )

    model = architecture["architecture_model"]

    check(
        "Architecture fingerprint verified",
        sha256_model(model)
        == architecture.get("architecture_sha256"),
    )

    check(
        "V20.2 uses current architecture",
        simulation.get("architecture_file_sha256")
        == sha256_file(ARCH_FILE)
        and simulation.get("architecture_model_sha256")
        == sha256_model(model),
    )

    check(
        "Simulation-only operation enforced",
        model.get("simulation_mode") is True
        and model.get("network_access_enabled") is False
        and model.get("real_attack_execution") is False
        and simulation.get("simulation_mode") is True
        and simulation.get("real_network_access") is False
        and simulation.get("real_attack_execution") is False,
    )

    check(
        "Event export version verified",
        events.get("version") == "V20.2"
        and events.get("simulation_mode") is True,
    )

    exported = events.get("events", [])

    check(
        "Event count matches source metadata",
        len(exported) == events.get("event_count")
        and len(exported)
        == simulation.get("metrics", {}).get("alerts"),
    )

    check(
        "Source simulation has no failed checks",
        simulation.get("checks_failed") == 0,
    )

    return model


def get_scenarios(model):
    scenarios = model["architecture"]["threat_scenarios"]

    ids = [item["id"] for item in scenarios]

    check(
        "Five scenarios available",
        len(scenarios) == 5,
    )

    check(
        "Scenario identifiers unique",
        len(set(ids)) == len(ids),
    )

    check(
        "Scenario categories supported",
        all(
            item["category"] in THREAT_CATEGORIES
            for item in scenarios
        ),
    )

    check(
        "All scenarios are synthetic",
        all(
            item["synthetic"] is True
            for item in scenarios
        ),
    )

    check(
        "Scenario severity values valid",
        all(
            item["severity"] in SEVERITY_WEIGHT
            for item in scenarios
        ),
    )

    return scenarios


def index_node_observations(rows):
    observations = {}

    for row in rows:
        key = (
            int(row["tick"]),
            row["node_id"],
        )

        if key in observations:
            raise ValueError(
                f"Duplicate node observation: {key}"
            )

        observations[key] = {
            "tick": int(row["tick"]),
            "node_id": row["node_id"],
            "load": float(row["load"]),
            "risk_score": float(row["risk_score"]),
            "risk_level": row["risk_level"],
            "injected_anomaly": (
                row["injected_anomaly"].lower()
                == "true"
            ),
        }

    return observations


def index_link_observations(rows):
    indexed = defaultdict(list)

    for row in rows:
        tick = int(row["tick"])

        indexed[tick].append({
            "source": row["source"],
            "target": row["target"],
            "traffic_mbps": float(
                row["traffic_mbps"]
            ),
            "latency_ms": float(
                row["latency_ms"]
            ),
            "injected_anomaly": (
                row["injected_anomaly"].lower()
                == "true"
            ),
        })

    return indexed


def match_scenario(event, scenarios, node):
    """
    Match an event with a configured scenario
    using its target node.

    This is explicit rule-based correlation,
    not trained model inference.
    """

    node_id = event["node_id"]

    candidates = [
        scenario
        for scenario in scenarios
        if scenario["target"] == node_id
    ]

    if not candidates:
        return {
            "scenario_id": "unmapped_alert",
            "scenario_name": "Unmapped Risk Alert",
            "category": "unclassified",
            "severity": event["severity"],
            "match_type": "no_configured_target",
        }

    scenario = candidates[0]

    return {
        "scenario_id": scenario["id"],
        "scenario_name": scenario["name"],
        "category": scenario["category"],
        "severity": scenario["severity"],
        "match_type": "target_node_rule",
    }


def enriched_risk(event, node, scenario):
    """
    Explainable synthetic risk combination.

    This is an engineered scoring rule, not
    a learned or calibrated probability.
    """

    source_risk = float(event["risk_score"])
    node_load = float(node["load"])

    severity = SEVERITY_WEIGHT.get(
        scenario["severity"],
        0.0,
    )

    injected = bool(
        event.get("injected_anomaly")
    )

    score = (
        source_risk * 0.65
        + node_load * 0.15
        + severity * 0.15
        + (0.05 if injected else 0.0)
    )

    return rounded(clamp(score))


def classify_events(
    events,
    scenarios,
    node_observations,
    link_observations,
):
    classified = []

    for event in events:
        tick = int(event["tick"])
        node_id = event["node_id"]

        node = node_observations.get(
            (tick, node_id)
        )

        if node is None:
            raise ValueError(
                f"Missing node observation: {tick}/{node_id}"
            )

        if event.get("synthetic") is not True:
            raise ValueError(
                "Non-synthetic event encountered"
            )

        scenario = match_scenario(
            event,
            scenarios,
            node,
        )

        score = enriched_risk(
            event,
            node,
            scenario,
        )

        links = [
            link
            for link in link_observations.get(
                tick, []
            )
            if node_id in (
                link["source"],
                link["target"],
            )
        ]

        related_traffic = sum(
            link["traffic_mbps"]
            for link in links
        )

        related_spikes = sum(
            1
            for link in links
            if link["injected_anomaly"]
        )

        classified.append({
            "event_id": event["event_id"],
            "tick": tick,
            "timestamp": event["timestamp"],
            "node_id": node_id,
            "scenario_id": scenario["scenario_id"],
            "scenario_name": scenario["scenario_name"],
            "threat_category": scenario["category"],
            "match_type": scenario["match_type"],
            "original_severity": event["severity"],
            "source_risk_score": rounded(
                event["risk_score"]
            ),
            "enriched_risk_score": score,
            "enriched_risk_level": risk_level(
                score
            ),
            "node_load": rounded(node["load"]),
            "related_traffic_mbps": rounded(
                related_traffic
            ),
            "related_injected_link_spikes": related_spikes,
            "injected_anomaly": bool(
                event["injected_anomaly"]
            ),
            "synthetic": True,
            "classification_method": (
                "deterministic_rule_based"
            ),
        })

    return classified


def build_timeline(classified, simulation):
    by_tick = defaultdict(list)

    for item in classified:
        by_tick[item["tick"]].append(item)

    timeline = []

    for tick in simulation["tick_summaries"]:
        tick_id = int(tick["tick"])
        alerts = by_tick.get(tick_id, [])

        timeline.append({
            "tick": tick_id,
            "timestamp": tick["timestamp"],
            "total_traffic_mbps": tick[
                "total_traffic_mbps"
            ],
            "mean_latency_ms": tick[
                "mean_latency_ms"
            ],
            "alert_count": len(alerts),
            "highest_enriched_risk": rounded(
                max(
                    (
                        item["enriched_risk_score"]
                        for item in alerts
                    ),
                    default=0.0,
                )
            ),
            "anomaly_injected": bool(
                tick["injected_anomaly_tick"]
            ),
            "scenario_ids": sorted({
                item["scenario_id"]
                for item in alerts
            }),
        })

    return timeline


def validate_classifications(
    raw_events,
    classified,
    timeline,
    scenarios,
    simulation,
):
    ids = [e["event_id"] for e in classified]

    check(
        "All source events classified",
        len(classified) == len(raw_events),
    )

    check(
        "Unique classified event IDs",
        len(set(ids)) == len(ids),
    )

    check(
        "All classifications remain synthetic",
        all(
            item["synthetic"] is True
            for item in classified
        ),
    )

    check(
        "Classification is explicitly rule-based",
        all(
            item["classification_method"]
            == "deterministic_rule_based"
            for item in classified
        ),
    )

    check(
        "Risk scores are finite and bounded",
        all(
            math.isfinite(
                item["enriched_risk_score"]
            )
            and 0 <= item["enriched_risk_score"] <= 1
            for item in classified
        ),
    )

    check(
        "Enriched risk levels consistent",
        all(
            item["enriched_risk_level"]
            == risk_level(
                item["enriched_risk_score"]
            )
            for item in classified
        ),
    )

    configured_ids = {
        s["id"] for s in scenarios
    }

    check(
        "Only configured or unmapped scenarios used",
        all(
            item["scenario_id"] in configured_ids
            or item["scenario_id"] == "unmapped_alert"
            for item in classified
        ),
    )

    check(
        "Traffic context nonnegative",
        all(
            item["related_traffic_mbps"] >= 0
            for item in classified
        ),
    )

    check(
        "Timeline covers all simulation ticks",
        len(timeline)
        == simulation["metrics"]["ticks"],
    )

    check(
        "Timeline tick sequence continuous",
        [
            item["tick"] for item in timeline
        ] == list(
            range(simulation["metrics"]["ticks"])
        ),
    )

    check(
        "Timeline alert counts consistent",
        sum(
            item["alert_count"]
            for item in timeline
        ) == len(classified),
    )

    check(
        "Classified events retain source IDs",
        set(ids) == {
            item["event_id"]
            for item in raw_events
        },
    )

    check(
        "Threat scenarios do not require real attacks",
        all(
            item["synthetic"] is True
            for item in scenarios
        ),
    )


def create_metrics(classified, timeline, scenarios):
    categories = Counter(
        item["threat_category"]
        for item in classified
    )

    levels = Counter(
        item["enriched_risk_level"]
        for item in classified
    )

    injected_alerts = sum(
        item["injected_anomaly"]
        for item in classified
    )

    covered = {
        item["scenario_id"]
        for item in classified
        if item["scenario_id"] != "unmapped_alert"
    }

    return {
        "total_alerts": len(classified),
        "simulation_ticks": len(timeline),
        "configured_scenarios": len(scenarios),
        "scenarios_matched_by_alerts": len(covered),
        "unmapped_alerts": categories.get(
            "unclassified", 0
        ),
        "synthetically_injected_alerts": (
            injected_alerts
        ),
        "alert_categories": dict(categories),
        "enriched_risk_levels": dict(levels),
        "maximum_enriched_risk": rounded(
            max(
                (
                    item["enriched_risk_score"]
                    for item in classified
                ),
                default=0.0,
            )
        ),
        "classification_type": "rule_based",
        "trained_ai_model_used": False,
        "real_world_detection_accuracy_measured": False,
    }


def create_markdown(result):
    metrics = result["metrics"]

    return f"""# Quantum Cyber Defense Arena

## V20.3 - AI Threat Scenario Engine

**Status:** {result['status']}

### Research summary

- Simulation ticks: {metrics['simulation_ticks']}
- Source alerts classified: {metrics['total_alerts']}
- Configured threat scenarios: {metrics['configured_scenarios']}
- Scenarios matched by alerts: {metrics['scenarios_matched_by_alerts']}
- Unmapped alerts: {metrics['unmapped_alerts']}
- Alerts marked as injected anomalies: {metrics['synthetically_injected_alerts']}
- Maximum enriched risk: {metrics['maximum_enriched_risk']}

### Scenario categories

- Traffic anomaly
- Reconnaissance
- Application anomaly
- Access anomaly
- Model alert

### Detection and risk methodology

The engine uses target-node correlation and an
explicit deterministic risk scoring formula.

It enriches existing V20.2 simulated risk alerts
with scenario metadata and traffic context.

A scenario matching rule does not establish
that an attack actually occurred.

### Scientific limitations

- Synthetic observations only
- No independently verified attack labels
- No trained AI model executed in this module
- No real-world detection accuracy measured
- No autonomous external security actions
- Scenario coverage is not detection recall

### Exports

- ai_threat_scenario_v20_3_results.json
- ai_threat_scenario_v20_3_events.csv
- ai_threat_scenario_v20_3_timeline.json

### Validation

- Passed: {result['checks_passed']}
- Failed: {result['checks_failed']}

### Next stage

V20.4 - Event Streaming Engine
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V20.3 - AI THREAT SCENARIO ENGINE")
    print("=" * 70)

    V20.mkdir(parents=True, exist_ok=True)

    architecture = load_json(ARCH_FILE)
    simulation = load_json(SIM_FILE)
    event_export = load_json(EVENTS_FILE)

    node_rows = load_csv(NODES_FILE)
    link_rows = load_csv(LINKS_FILE)

    model = validate_sources(
        architecture,
        simulation,
        event_export,
    )

    scenarios = get_scenarios(model)

    observations = index_node_observations(
        node_rows
    )

    links = index_link_observations(
        link_rows
    )

    source_events = event_export["events"]

    classified = classify_events(
        source_events,
        scenarios,
        observations,
        links,
    )

    timeline = build_timeline(
        classified,
        simulation,
    )

    validate_classifications(
        source_events,
        classified,
        timeline,
        scenarios,
        simulation,
    )

    # Repeat classification to verify determinism.
    repeated = classify_events(
        source_events,
        scenarios,
        observations,
        links,
    )

    check(
        "Classification reproducible",
        classified == repeated,
    )

    metrics = create_metrics(
        classified,
        timeline,
        scenarios,
    )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "THREAT_SCENARIO_PASS"
        if failed == 0
        else "THREAT_SCENARIO_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V20.3",
        "module": "AI Threat Scenario Engine",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "execution_mode": "deterministic_read_only",
        "simulation_mode": True,
        "trained_ai_model_used": False,
        "real_network_access": False,
        "external_actions_enabled": False,
        "source_sha256": {
            "architecture": sha256_file(
                ARCH_FILE
            ),
            "simulation": sha256_file(
                SIM_FILE
            ),
            "events": sha256_file(
                EVENTS_FILE
            ),
            "nodes_csv": sha256_file(
                NODES_FILE
            ),
            "links_csv": sha256_file(
                LINKS_FILE
            ),
        },
        "metrics": metrics,
        "scenarios": scenarios,
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "limitations": [
            "Synthetic observations only.",
            "Rule-based scenario matching.",
            "No trained model executed.",
            "No verified attack labels.",
            "No validated real-world accuracy.",
            "No external security actions.",
        ],
        "next_stage": "V20.4 Event Streaming Engine",
    }

    write_json(RESULT_FILE, result)

    if failed == 0:
        write_csv(
            CLASSIFIED_FILE,
            classified,
        )

        write_json(
            TIMELINE_FILE,
            {
                "version": "V20.3",
                "simulation_mode": True,
                "is_live": False,
                "ticks": len(timeline),
                "timeline": timeline,
            },
        )

        REPORT_FILE.write_text(
            create_markdown(result),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V20.3 THREAT SCENARIO RESULTS")
    print("=" * 70)

    print(
        "SIMULATION TICKS:",
        metrics["simulation_ticks"],
    )

    print(
        "ALERTS CLASSIFIED:",
        metrics["total_alerts"],
    )

    print(
        "SCENARIOS CONFIGURED:",
        metrics["configured_scenarios"],
    )

    print(
        "SCENARIOS MATCHED:",
        metrics["scenarios_matched_by_alerts"],
    )

    print(
        "MAXIMUM ENRICHED RISK:",
        metrics["maximum_enriched_risk"],
    )

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {RESULT_FILE}")
    print(f"V20.3 RESULT: {status}")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print()
        print(
            "V20.3 FAILED:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
