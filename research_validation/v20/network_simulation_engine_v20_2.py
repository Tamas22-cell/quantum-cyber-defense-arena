
"""
QUANTUM CYBER DEFENSE ARENA
V20.2 - NETWORK SIMULATION ENGINE

Deterministic, reproducible cyber digital twin simulation.

Features:
- Loads and verifies V20.1 architecture
- Simulates node loads and risk scores
- Simulates network traffic and latency
- Produces synthetic anomalies and alerts
- Creates timestamped event records
- Validates simulation integrity
- Exports JSON, CSV and Markdown reports

Standard Python library only.
No real network traffic.
No real attack execution.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
import sys

from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V20 = ROOT / "research_validation" / "v20"

ARCHITECTURE_FILE = (
    V20 / "digital_twin_architecture_v20_1_results.json"
)

RESULT_FILE = (
    V20 / "network_simulation_v20_2_results.json"
)

NODES_FILE = (
    V20 / "network_simulation_v20_2_nodes.csv"
)

LINKS_FILE = (
    V20 / "network_simulation_v20_2_links.csv"
)

EVENTS_FILE = (
    V20 / "network_simulation_v20_2_events.json"
)

REPORT_FILE = (
    V20 / "NETWORK_SIMULATION_V20_2.md"
)

TICKS = 120

SIMULATION_START = datetime(
    2026, 1, 1, 0, 0, 0,
    tzinfo=timezone.utc,
)

CHECKS = []


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

    if detail and not passed:
        print("    ", detail)

    return passed


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
    data = json.dumps(
        model,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(data).hexdigest()


def load_architecture():
    if not ARCHITECTURE_FILE.is_file():
        raise FileNotFoundError(
            "V20.1 architecture report is missing: "
            + str(ARCHITECTURE_FILE)
        )

    with ARCHITECTURE_FILE.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        report = json.load(file)

    if not isinstance(report, dict):
        raise ValueError("Invalid V20.1 report")

    if (
        report.get("version") != "V20.1"
        or report.get("status") != "ARCHITECTURE_PASS"
        or report.get("checks_failed") != 0
    ):
        raise ValueError(
            "V20.1 architecture has not passed validation"
        )

    model = report.get("architecture_model")

    if not isinstance(model, dict):
        raise ValueError("Missing architecture model")

    expected_hash = report.get("architecture_sha256")
    actual_hash = sha256_model(model)

    if expected_hash != actual_hash:
        raise ValueError(
            "V20.1 architecture fingerprint mismatch"
        )

    if (
        model.get("simulation_mode") is not True
        or model.get("network_access_enabled") is not False
        or model.get("real_attack_execution") is not False
    ):
        raise ValueError(
            "Architecture must remain simulation-only"
        )

    architecture = model.get("architecture", {})

    nodes = architecture.get("nodes", [])
    edges = architecture.get("edges", [])
    sensors = architecture.get("sensors", [])

    if not nodes or not edges or not sensors:
        raise ValueError(
            "Incomplete digital twin architecture"
        )

    node_ids = [node["id"] for node in nodes]

    if len(set(node_ids)) != len(node_ids):
        raise ValueError("Duplicate network node ID")

    edge_ids = [edge["id"] for edge in edges]

    if len(set(edge_ids)) != len(edge_ids):
        raise ValueError("Duplicate network link ID")

    for edge in edges:
        if (
            edge["source"] not in node_ids
            or edge["target"] not in node_ids
        ):
            raise ValueError(
                f"Invalid link endpoints: {edge['id']}"
            )

    config = model.get("simulation_config", {})

    if int(config.get("tick_interval_ms", 0)) <= 0:
        raise ValueError("Invalid simulation tick interval")

    return report, model


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def round6(value):
    return round(float(value), 6)


def simulation_time(tick, interval_ms):
    value = SIMULATION_START + timedelta(
        milliseconds=tick * interval_ms
    )

    return value.isoformat()


def classify_risk(score, thresholds):
    if score >= thresholds["critical"]:
        return "critical"

    if score >= thresholds["high"]:
        return "high"

    if score >= thresholds["medium"]:
        return "medium"

    if score >= thresholds["low"]:
        return "low"

    return "normal"


def simulate(model, seed, ticks):
    architecture = model["architecture"]
    config = model["simulation_config"]

    nodes = architecture["nodes"]
    edges = architecture["edges"]
    thresholds = config["risk_thresholds"]

    interval_ms = int(config["tick_interval_ms"])

    rng = random.Random(seed)

    node_records = []
    link_records = []
    events = []
    tick_summaries = []

    # Persistent synthetic state for each node.
    loads = {
        node["id"]: 0.20
        for node in nodes
    }

    # Explicitly planned synthetic anomaly events.
    anomaly_ticks = {
        17, 34, 51, 68, 85, 102, 119
    }

    anomaly_ticks = {
        value for value in anomaly_ticks
        if value < ticks
    }

    event_id = 0

    for tick in range(ticks):
        timestamp = simulation_time(
            tick,
            interval_ms,
        )

        is_anomaly_tick = tick in anomaly_ticks

        total_traffic = 0.0
        all_latencies = []
        alerts_this_tick = 0

        # Simulate all network links.
        for edge in edges:
            baseline = 35.0 + rng.uniform(
                -8.0, 25.0
            )

            periodic_load = 12.0 * (
                1.0 + math.sin(tick / 8.0)
            )

            traffic = max(
                0.0,
                baseline + periodic_load,
            )

            # Synthetic traffic spike at the edge gateway.
            injected_spike = (
                is_anomaly_tick
                and edge["source"] == "external"
            )

            if injected_spike:
                traffic *= 5.0

            latency = (
                float(edge["base_latency_ms"])
                + traffic / 200.0
                + rng.uniform(0.0, 1.5)
            )

            if injected_spike:
                latency += 18.0

            utilization = clamp(
                traffic
                / float(edge["bandwidth_mbps"])
            )

            link_records.append({
                "tick": tick,
                "timestamp": timestamp,
                "link_id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "traffic_mbps": round6(traffic),
                "latency_ms": round6(latency),
                "utilization": round6(utilization),
                "injected_anomaly": injected_spike,
            })

            total_traffic += traffic
            all_latencies.append(latency)

        # Simulate loads and risk for each node.
        for node in nodes:
            node_id = node["id"]

            previous_load = loads[node_id]

            baseline = (
                0.15
                + 0.10 * math.sin(
                    tick / 9.0 + len(node_id)
                )
            )

            random_component = rng.uniform(
                0.0, 0.24
            )

            load = clamp(
                previous_load * 0.55
                + baseline * 0.45
                + random_component * 0.30
            )

            injected_anomaly = (
                is_anomaly_tick
                and node_id in {
                    "gateway",
                    "firewall",
                    "api",
                }
            )

            if injected_anomaly:
                load = clamp(
                    load + 0.65
                )

            loads[node_id] = load

            criticality = (
                int(node["criticality"]) / 5.0
            )

            risk = clamp(
                load * 0.65
                + criticality * 0.10
                + (
                    0.30
                    if injected_anomaly
                    else 0.0
                )
            )

            risk_level = classify_risk(
                risk,
                thresholds,
            )

            node_records.append({
                "tick": tick,
                "timestamp": timestamp,
                "node_id": node_id,
                "zone": node["zone"],
                "node_type": node["type"],
                "load": round6(load),
                "risk_score": round6(risk),
                "risk_level": risk_level,
                "injected_anomaly": injected_anomaly,
            })

            if risk_level in {"high", "critical"}:
                event_id += 1
                alerts_this_tick += 1

                events.append({
                    "event_id": f"EVT-{event_id:06d}",
                    "tick": tick,
                    "timestamp": timestamp,
                    "event_type": "risk_alert",
                    "node_id": node_id,
                    "severity": risk_level,
                    "risk_score": round6(risk),
                    "synthetic": True,
                    "injected_anomaly": injected_anomaly,
                    "description": (
                        "Synthetic node risk threshold exceeded"
                    ),
                })

        tick_summaries.append({
            "tick": tick,
            "timestamp": timestamp,
            "total_traffic_mbps": round6(
                total_traffic
            ),
            "mean_latency_ms": round6(
                statistics.mean(all_latencies)
            ),
            "alerts": alerts_this_tick,
            "injected_anomaly_tick": (
                is_anomaly_tick
            ),
        })

    return {
        "nodes": node_records,
        "links": link_records,
        "events": events,
        "ticks": tick_summaries,
        "injected_anomaly_ticks": sorted(
            anomaly_ticks
        ),
    }


def validate_simulation(model, data, ticks):
    nodes = model["architecture"]["nodes"]
    edges = model["architecture"]["edges"]

    node_records = data["nodes"]
    link_records = data["links"]
    events = data["events"]
    tick_records = data["ticks"]

    valid_node_ids = {
        node["id"] for node in nodes
    }

    valid_link_ids = {
        edge["id"] for edge in edges
    }

    check(
        "Simulation generated all ticks",
        len(tick_records) == ticks,
    )

    check(
        "Correct number of node observations",
        len(node_records) == ticks * len(nodes),
    )

    check(
        "Correct number of link observations",
        len(link_records) == ticks * len(edges),
    )

    check(
        "Tick indices are continuous",
        [
            row["tick"] for row in tick_records
        ] == list(range(ticks)),
    )

    check(
        "Node references are valid",
        all(
            row["node_id"] in valid_node_ids
            for row in node_records
        ),
    )

    check(
        "Link references are valid",
        all(
            row["link_id"] in valid_link_ids
            for row in link_records
        ),
    )

    check(
        "One node observation per node and tick",
        len({
            (row["tick"], row["node_id"])
            for row in node_records
        }) == len(node_records),
    )

    check(
        "One link observation per link and tick",
        len({
            (row["tick"], row["link_id"])
            for row in link_records
        }) == len(link_records),
    )

    check(
        "Node loads bounded between zero and one",
        all(
            0 <= row["load"] <= 1
            for row in node_records
        ),
    )

    check(
        "Risk scores bounded between zero and one",
        all(
            0 <= row["risk_score"] <= 1
            for row in node_records
        ),
    )

    check(
        "No negative traffic",
        all(
            row["traffic_mbps"] >= 0
            for row in link_records
        ),
    )

    check(
        "No negative latency",
        all(
            row["latency_ms"] >= 0
            for row in link_records
        ),
    )

    check(
        "Network utilization valid",
        all(
            0 <= row["utilization"] <= 1
            for row in link_records
        ),
    )

    check(
        "Risk categories valid",
        all(
            row["risk_level"]
            in {
                "normal",
                "low",
                "medium",
                "high",
                "critical",
            }
            for row in node_records
        ),
    )

    check(
        "Risk categories match thresholds",
        all(
            row["risk_level"] == classify_risk(
                row["risk_score"],
                model["simulation_config"][
                    "risk_thresholds"
                ],
            )
            for row in node_records
        ),
    )

    check(
        "All events explicitly synthetic",
        all(
            event["synthetic"] is True
            for event in events
        ),
    )

    check(
        "Event IDs unique",
        len({
            event["event_id"]
            for event in events
        }) == len(events),
    )

    check(
        "Event timeline sorted",
        [
            event["tick"] for event in events
        ] == sorted(
            event["tick"] for event in events
        ),
    )

    check(
        "Events reference valid nodes",
        all(
            event["node_id"] in valid_node_ids
            for event in events
        ),
    )

    check(
        "Events correspond to recorded high-risk nodes",
        {
            (
                event["tick"],
                event["node_id"],
            )
            for event in events
        } == {
            (
                row["tick"],
                row["node_id"],
            )
            for row in node_records
            if row["risk_level"]
            in {"high", "critical"}
        },
    )

    check(
        "Synthetic anomaly schedule executed",
        all(
            any(
                row["tick"] == tick
                and row["injected_anomaly"]
                for row in node_records
            )
            for tick in data["injected_anomaly_ticks"]
        ),
    )

    check(
        "At least one simulated alert generated",
        len(events) > 0,
    )

    check(
        "Tick summaries contain nonnegative traffic",
        all(
            row["total_traffic_mbps"] >= 0
            for row in tick_records
        ),
    )

    check(
        "Tick alert totals match event count",
        sum(
            row["alerts"]
            for row in tick_records
        ) == len(events),
    )

    check(
        "Tick summary traffic agrees with link data",
        all(
            math.isclose(
                row["total_traffic_mbps"],
                sum(
                    link["traffic_mbps"]
                    for link in link_records
                    if link["tick"] == row["tick"]
                ),
                rel_tol=1e-6,
                abs_tol=1e-4,
            )
            for row in tick_records
        ),
    )

    check(
        "Finite numerical observations",
        all(
            math.isfinite(row["risk_score"])
            and math.isfinite(row["load"])
            for row in node_records
        )
        and all(
            math.isfinite(row["traffic_mbps"])
            and math.isfinite(row["latency_ms"])
            for row in link_records
        ),
    )


def write_json(path, payload):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


def write_csv(path, rows):
    if not rows:
        raise ValueError(
            "Cannot export an empty CSV dataset"
        )

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


def create_markdown(result):
    metrics = result["metrics"]

    return f"""# Quantum Cyber Defense Arena

## V20.2 - Network Simulation Engine

**Status:** {result['status']}

### Simulation

- Simulation ticks: {metrics['ticks']}
- Network nodes: {metrics['network_nodes']}
- Network links: {metrics['network_links']}
- Node observations: {metrics['node_observations']}
- Link observations: {metrics['link_observations']}
- Generated alerts: {metrics['alerts']}
- Synthetic anomaly ticks: {metrics['anomaly_ticks']}
- Maximum observed risk: {metrics['maximum_risk_score']}
- Mean traffic per link observation: {metrics['mean_link_traffic_mbps']} Mbps
- Mean simulated latency: {metrics['mean_latency_ms']} ms

### Integrity

- V20.1 source SHA-256: `{result['architecture_file_sha256']}`
- V20.1 model SHA-256: `{result['architecture_model_sha256']}`
- Validation checks passed: {result['checks_passed']}
- Validation checks failed: {result['checks_failed']}

### Exported data

- Node observations: `network_simulation_v20_2_nodes.csv`
- Link observations: `network_simulation_v20_2_links.csv`
- Event timeline: `network_simulation_v20_2_events.json`
- Main results: `network_simulation_v20_2_results.json`

### Research interpretation

The engine reproduces synthetic traffic, loads,
risk scores and timestamped alerts from a fixed
random seed.

This is a model-driven simulation. It does not
observe real network packets or execute attacks.

Alerts are based on synthetic risk thresholds,
not on a validated production threat detector.

### Next stage

V20.3 - AI Threat Scenario Engine
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V20.2 - NETWORK SIMULATION ENGINE")
    print("=" * 70)

    V20.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_report, model = load_architecture()

    config = model["simulation_config"]
    seed = int(config["random_seed"])

    check(
        "V20.1 architecture loaded successfully",
        source_report["status"] == "ARCHITECTURE_PASS",
    )

    check(
        "V20.1 integrity fingerprint verified",
        sha256_model(model)
        == source_report["architecture_sha256"],
    )

    check(
        "Simulation-only execution enforced",
        model["simulation_mode"] is True
        and model["network_access_enabled"] is False
        and model["real_attack_execution"] is False,
    )

    data = simulate(
        model,
        seed,
        TICKS,
    )

    validate_simulation(
        model,
        data,
        TICKS,
    )

    # Re-run in memory to verify reproducibility.
    repeated = simulate(
        model,
        seed,
        TICKS,
    )

    check(
        "Simulation reproducible with fixed seed",
        data == repeated,
    )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "NETWORK_SIMULATION_PASS"
        if failed == 0
        else "NETWORK_SIMULATION_FAIL"
    )

    node_records = data["nodes"]
    link_records = data["links"]
    events = data["events"]

    risk_counts = dict(
        Counter(
            row["risk_level"]
            for row in node_records
        )
    )

    metrics = {
        "ticks": TICKS,
        "network_nodes": len(
            model["architecture"]["nodes"]
        ),
        "network_links": len(
            model["architecture"]["edges"]
        ),
        "node_observations": len(node_records),
        "link_observations": len(link_records),
        "alerts": len(events),
        "anomaly_ticks": len(
            data["injected_anomaly_ticks"]
        ),
        "maximum_risk_score": round6(
            max(
                row["risk_score"]
                for row in node_records
            )
        ),
        "mean_link_traffic_mbps": round6(
            statistics.mean(
                row["traffic_mbps"]
                for row in link_records
            )
        ),
        "mean_latency_ms": round6(
            statistics.mean(
                row["latency_ms"]
                for row in link_records
            )
        ),
        "risk_level_observations": risk_counts,
    }

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V20.2",
        "module": "Network Simulation Engine",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "live_data": False,
        "real_network_access": False,
        "real_attack_execution": False,
        "random_seed": seed,
        "tick_interval_ms": config[
            "tick_interval_ms"
        ],
        "architecture_file_sha256": sha256_file(
            ARCHITECTURE_FILE
        ),
        "architecture_model_sha256": sha256_model(
            model
        ),
        "metrics": metrics,
        "tick_summaries": data["ticks"],
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "outputs": {
            "nodes_csv": str(
                NODES_FILE.relative_to(ROOT)
            ),
            "links_csv": str(
                LINKS_FILE.relative_to(ROOT)
            ),
            "events_json": str(
                EVENTS_FILE.relative_to(ROOT)
            ),
            "report_markdown": str(
                REPORT_FILE.relative_to(ROOT)
            ),
        },
        "limitations": [
            "Synthetic observations only.",
            "No real network monitoring.",
            "Alerts are generated by synthetic risk rules.",
            "No validated threat detection accuracy.",
            "No production security controls.",
        ],
        "next_stage": "V20.3 AI Threat Scenario Engine",
    }

    write_json(
        RESULT_FILE,
        result,
    )

    if failed == 0:
        write_csv(
            NODES_FILE,
            node_records,
        )

        write_csv(
            LINKS_FILE,
            link_records,
        )

        write_json(
            EVENTS_FILE,
            {
                "version": "V20.2",
                "simulation_mode": True,
                "event_count": len(events),
                "events": events,
            },
        )

        REPORT_FILE.write_text(
            create_markdown(result),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V20.2 NETWORK SIMULATION RESULTS")
    print("=" * 70)

    print(
        f"NETWORK NODES: {metrics['network_nodes']}"
    )
    print(
        f"NETWORK LINKS: {metrics['network_links']}"
    )
    print(
        f"SIMULATION TICKS: {metrics['ticks']}"
    )
    print(
        f"NODE OBSERVATIONS: {metrics['node_observations']}"
    )
    print(
        f"LINK OBSERVATIONS: {metrics['link_observations']}"
    )
    print(
        f"SYNTHETIC ALERTS: {metrics['alerts']}"
    )

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")

    print(f"JSON REPORT: {RESULT_FILE}")
    print(f"V20.2 RESULT: {status}")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print()
        print(
            "V20.2 FAILED:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
