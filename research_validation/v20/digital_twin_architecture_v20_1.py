
"""
QUANTUM CYBER DEFENSE ARENA
V20.1 - CYBER DIGITAL TWIN ARCHITECTURE

Builds and validates a simulated cyber network.

Features:
- Network topology
- Security zones
- Assets and connections
- Sensors and telemetry
- Threat scenarios
- Risk thresholds
- Architecture validation
- JSON and Markdown exports

Standard library only.
No real network scanning.
No external network connections.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "research_validation" / "v20"

OUTPUT_JSON = (
    OUTPUT_DIR
    / "digital_twin_architecture_v20_1_results.json"
)

OUTPUT_MD = (
    OUTPUT_DIR
    / "DIGITAL_TWIN_ARCHITECTURE_V20_1.md"
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
        print(f"       {detail}")

    return passed


def build_nodes():
    return [
        {
            "id": "external",
            "label": "External Network",
            "type": "external",
            "zone": "external",
            "criticality": 1,
        },
        {
            "id": "gateway",
            "label": "Edge Gateway",
            "type": "gateway",
            "zone": "perimeter",
            "criticality": 4,
        },
        {
            "id": "firewall",
            "label": "Security Firewall",
            "type": "firewall",
            "zone": "perimeter",
            "criticality": 5,
        },
        {
            "id": "web",
            "label": "Web Server",
            "type": "server",
            "zone": "dmz",
            "criticality": 3,
        },
        {
            "id": "api",
            "label": "API Server",
            "type": "server",
            "zone": "dmz",
            "criticality": 4,
        },
        {
            "id": "switch",
            "label": "Internal Switch",
            "type": "switch",
            "zone": "internal",
            "criticality": 4,
        },
        {
            "id": "ai_engine",
            "label": "AI Threat Engine",
            "type": "ai_engine",
            "zone": "internal",
            "criticality": 5,
        },
        {
            "id": "database",
            "label": "Research Database",
            "type": "database",
            "zone": "restricted",
            "criticality": 5,
        },
        {
            "id": "telemetry",
            "label": "Telemetry Collector",
            "type": "sensor",
            "zone": "internal",
            "criticality": 4,
        },
        {
            "id": "analyst",
            "label": "Security Analyst Console",
            "type": "workstation",
            "zone": "internal",
            "criticality": 3,
        },
    ]


def build_edges():
    pairs = [
        ("external", "gateway"),
        ("gateway", "firewall"),
        ("firewall", "web"),
        ("firewall", "api"),
        ("firewall", "switch"),
        ("web", "api"),
        ("switch", "ai_engine"),
        ("switch", "database"),
        ("switch", "telemetry"),
        ("switch", "analyst"),
        ("ai_engine", "database"),
    ]

    nodes = {
        item["id"]: item
        for item in build_nodes()
    }

    edges = []

    for index, (source, target) in enumerate(
        pairs,
        start=1,
    ):
        source_zone = nodes[source]["zone"]
        target_zone = nodes[target]["zone"]

        cross_zone = source_zone != target_zone

        edges.append({
            "id": f"link_{index:03d}",
            "source": source,
            "target": target,
            "type": "simulated_link",
            "bandwidth_mbps": 1000,
            "base_latency_ms": 2.0,
            "cross_zone": cross_zone,
            "inspection_required": cross_zone,
            "status": "online",
        })

    return edges


def build_sensors():
    return [
        {
            "id": "sensor_network",
            "type": "network_monitor",
            "attached_to": "firewall",
            "metrics": [
                "traffic_rate",
                "connections",
                "blocked_events",
            ],
        },
        {
            "id": "sensor_ai",
            "type": "anomaly_monitor",
            "attached_to": "ai_engine",
            "metrics": [
                "anomaly_score",
                "model_status",
                "inference_count",
            ],
        },
        {
            "id": "sensor_database",
            "type": "asset_monitor",
            "attached_to": "database",
            "metrics": [
                "access_count",
                "failed_access",
                "resource_load",
            ],
        },
        {
            "id": "sensor_telemetry",
            "type": "event_collector",
            "attached_to": "telemetry",
            "metrics": [
                "event_count",
                "alert_count",
                "ingestion_delay",
            ],
        },
    ]


def build_scenarios():
    return [
        {
            "id": "scenario_001",
            "name": "Traffic Spike",
            "category": "traffic_anomaly",
            "target": "gateway",
            "severity": "medium",
            "synthetic": True,
        },
        {
            "id": "scenario_002",
            "name": "Simulated Port Scan",
            "category": "reconnaissance",
            "target": "firewall",
            "severity": "medium",
            "synthetic": True,
        },
        {
            "id": "scenario_003",
            "name": "Suspicious API Requests",
            "category": "application_anomaly",
            "target": "api",
            "severity": "high",
            "synthetic": True,
        },
        {
            "id": "scenario_004",
            "name": "Unusual Database Access",
            "category": "access_anomaly",
            "target": "database",
            "severity": "high",
            "synthetic": True,
        },
        {
            "id": "scenario_005",
            "name": "AI Anomaly Alert",
            "category": "model_alert",
            "target": "ai_engine",
            "severity": "medium",
            "synthetic": True,
        },
    ]


def build_architecture():
    return {
        "project": "Quantum Cyber Defense Arena",
        "version": "V20.1",
        "module": "Cyber Digital Twin Architecture",
        "simulation_mode": True,
        "network_access_enabled": False,
        "real_attack_execution": False,
        "architecture": {
            "name": "Cyber Defense Digital Twin",
            "model_type": "simulated_network_graph",
            "zones": [
                "external",
                "perimeter",
                "dmz",
                "internal",
                "restricted",
            ],
            "nodes": build_nodes(),
            "edges": build_edges(),
            "sensors": build_sensors(),
            "threat_scenarios": build_scenarios(),
        },
        "simulation_config": {
            "tick_interval_ms": 1000,
            "random_seed": 42,
            "initial_state": "idle",
            "event_stream_enabled": False,
            "event_stream_planned_for": "V20.4",
            "risk_thresholds": {
                "low": 0.25,
                "medium": 0.50,
                "high": 0.75,
                "critical": 0.90,
            },
            "maximum_risk_score": 1.0,
        },
        "planned_modules": {
            "V20.2": "Network Simulation Engine",
            "V20.3": "AI Threat Scenario Engine",
            "V20.4": "Event Streaming Engine",
            "V20.5": "Interactive Digital Twin Dashboard",
            "V20.6": "Research Validation and Release",
        },
    }


def network_connected(nodes, edges):
    if not nodes:
        return False

    graph = {
        node["id"]: set()
        for node in nodes
    }

    for edge in edges:
        source = edge["source"]
        target = edge["target"]

        if source not in graph or target not in graph:
            return False

        graph[source].add(target)
        graph[target].add(source)

    start = nodes[0]["id"]

    visited = {start}
    queue = deque([start])

    while queue:
        current = queue.popleft()

        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return len(visited) == len(nodes)


def validate_architecture(model):
    architecture = model["architecture"]
    config = model["simulation_config"]

    nodes = architecture["nodes"]
    edges = architecture["edges"]
    sensors = architecture["sensors"]
    scenarios = architecture["threat_scenarios"]
    zones = architecture["zones"]

    node_ids = [node["id"] for node in nodes]
    node_map = {
        node["id"]: node
        for node in nodes
    }

    check(
        "Correct architecture version",
        model["version"] == "V20.1",
    )

    check(
        "Simulation mode enabled",
        model["simulation_mode"] is True,
    )

    check(
        "External network access disabled",
        model["network_access_enabled"] is False,
    )

    check(
        "Real attack execution disabled",
        model["real_attack_execution"] is False,
    )

    check(
        "Ten simulated nodes configured",
        len(nodes) == 10,
    )

    check(
        "Node IDs are unique",
        len(node_ids) == len(set(node_ids)),
    )

    check(
        "Node IDs are nonempty",
        all(
            isinstance(node_id, str) and node_id
            for node_id in node_ids
        ),
    )

    check(
        "All required security zones defined",
        set(zones) == {
            "external",
            "perimeter",
            "dmz",
            "internal",
            "restricted",
        },
    )

    check(
        "Every node has a valid zone",
        all(node["zone"] in zones for node in nodes),
    )

    check(
        "Node criticality within 1-5",
        all(
            type(node["criticality"]) is int
            and 1 <= node["criticality"] <= 5
            for node in nodes
        ),
    )

    check(
        "All eleven connections configured",
        len(edges) == 11,
    )

    check(
        "All edges reference existing nodes",
        all(
            edge["source"] in node_map
            and edge["target"] in node_map
            for edge in edges
        ),
    )

    check(
        "No self-loop connections",
        all(
            edge["source"] != edge["target"]
            for edge in edges
        ),
    )

    pairs = [
        tuple(sorted((
            edge["source"],
            edge["target"],
        )))
        for edge in edges
    ]

    check(
        "No duplicate network links",
        len(pairs) == len(set(pairs)),
    )

    check(
        "Network graph is connected",
        network_connected(nodes, edges),
    )

    check(
        "Positive simulated bandwidth",
        all(
            edge["bandwidth_mbps"] > 0
            for edge in edges
        ),
    )

    check(
        "Nonnegative simulated latency",
        all(
            edge["base_latency_ms"] >= 0
            for edge in edges
        ),
    )

    check(
        "Cross-zone links marked correctly",
        all(
            edge["cross_zone"]
            == (
                node_map[edge["source"]]["zone"]
                != node_map[edge["target"]]["zone"]
            )
            for edge in edges
        ),
    )

    check(
        "Cross-zone inspection requirement recorded",
        all(
            not edge["cross_zone"]
            or edge["inspection_required"] is True
            for edge in edges
        ),
    )

    check(
        "At least four sensors configured",
        len(sensors) >= 4,
    )

    check(
        "Sensors attached to existing nodes",
        all(
            sensor["attached_to"] in node_map
            for sensor in sensors
        ),
    )

    check(
        "Each sensor defines measurements",
        all(
            len(sensor["metrics"]) > 0
            for sensor in sensors
        ),
    )

    check(
        "Five threat scenarios defined",
        len(scenarios) == 5,
    )

    check(
        "Threat scenarios are synthetic",
        all(
            scenario["synthetic"] is True
            for scenario in scenarios
        ),
    )

    check(
        "Threat targets reference known nodes",
        all(
            scenario["target"] in node_map
            for scenario in scenarios
        ),
    )

    check(
        "Threat severity values valid",
        all(
            scenario["severity"]
            in {"low", "medium", "high", "critical"}
            for scenario in scenarios
        ),
    )

    thresholds = config["risk_thresholds"]
    values = list(thresholds.values())

    check(
        "Risk thresholds monotonically increase",
        0 < values[0] < values[1]
        < values[2] < values[3] <= 1,
    )

    check(
        "Simulation tick interval positive",
        config["tick_interval_ms"] > 0,
    )

    check(
        "Event streaming not falsely enabled",
        config["event_stream_enabled"] is False,
    )

    check(
        "Dashboard stage is registered",
        "V20.5" in model["planned_modules"],
    )


def write_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


def architecture_fingerprint(model):
    serialized = json.dumps(
        model,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(serialized).hexdigest()


def create_markdown(model, passed, failed, fingerprint):
    architecture = model["architecture"]

    return f"""# Quantum Cyber Defense Arena

## V20.1 - Cyber Digital Twin Architecture

**Status:** ARCHITECTURE_PASS

**Validation:** {passed} passed / {failed} failed

### Architecture overview

- Nodes: {len(architecture['nodes'])}
- Network links: {len(architecture['edges'])}
- Security zones: {len(architecture['zones'])}
- Sensors: {len(architecture['sensors'])}
- Synthetic threat scenarios: {len(architecture['threat_scenarios'])}

### Security zones

- External
- Perimeter
- DMZ
- Internal
- Restricted

### Core components

- External network
- Edge gateway
- Security firewall
- Web server
- API server
- Internal switch
- AI threat engine
- Research database
- Telemetry collector
- Analyst console

### Digital Twin research goals

Create a reproducible, simulated cyber environment.

The topology defines network assets,
relationships, simulated telemetry sources,
and potential threat scenarios.

No real attack or network scan is performed.

### Integrity fingerprint

`{fingerprint}`

### Important limitations

- This is a topology specification, not a running simulator.
- Network links are synthetic.
- Cross-zone inspection requirements are metadata,
  not enforced firewall rules.
- Threat scenarios are specifications, not executed events.
- AI threat detection is not executed by V20.1.
- No live backend or frontend integration occurs here.

### Next stage

V20.2 - Network Simulation Engine

Future integration:
V20.5 - Interactive Digital Twin Dashboard
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V20.1 - CYBER DIGITAL TWIN ARCHITECTURE")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model = build_architecture()

    validate_architecture(model)

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "ARCHITECTURE_PASS"
        if failed == 0
        else "ARCHITECTURE_FAIL"
    )

    fingerprint = architecture_fingerprint(model)

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V20.1",
        "module": "Cyber Digital Twin Architecture",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "architecture_sha256": fingerprint,
        "architecture_model": model,
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "next_stage": "V20.2 Network Simulation Engine",
    }

    write_json(OUTPUT_JSON, result)

    if failed == 0:
        OUTPUT_MD.write_text(
            create_markdown(
                model,
                passed,
                failed,
                fingerprint,
            ),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V20.1 ARCHITECTURE RESULTS")
    print("=" * 70)
    print(
        "NETWORK NODES:",
        len(model["architecture"]["nodes"]),
    )
    print(
        "NETWORK LINKS:",
        len(model["architecture"]["edges"]),
    )
    print(
        "SENSORS:",
        len(model["architecture"]["sensors"]),
    )
    print(
        "THREAT SCENARIOS:",
        len(model["architecture"]["threat_scenarios"]),
    )
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {OUTPUT_JSON}")

    if failed == 0:
        print(f"RESEARCH DOCUMENT: {OUTPUT_MD}")

    print(f"V20.1 RESULT: {status}")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
