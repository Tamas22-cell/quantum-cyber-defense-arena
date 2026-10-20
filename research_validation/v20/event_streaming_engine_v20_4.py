
"""
QUANTUM CYBER DEFENSE ARENA
V20.4 - EVENT STREAMING ENGINE

Simulated event streaming and dashboard data preparation.

Reads:
- V20.1 architecture
- V20.2 simulation report and observations
- V20.3 threat scenario report and timeline

Generates:
- Validated dashboard frames
- Event stream in JSONL format
- Replay metadata
- Research validation report

Modes:
  Default: generate and validate files
  --replay: replay simulation frames in terminal

Python standard library only.
No real network connections or attacks.
"""

from __future__ import annotations

import argparse
import asyncio
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

ARCH_FILE = V20 / (
    "digital_twin_architecture_v20_1_results.json"
)
SIM_FILE = V20 / (
    "network_simulation_v20_2_results.json"
)
THREAT_FILE = V20 / (
    "ai_threat_scenario_v20_3_results.json"
)
TIMELINE_FILE = V20 / (
    "ai_threat_scenario_v20_3_timeline.json"
)
CLASSIFIED_FILE = V20 / (
    "ai_threat_scenario_v20_3_events.csv"
)
NODE_FILE = V20 / (
    "network_simulation_v20_2_nodes.csv"
)
LINK_FILE = V20 / (
    "network_simulation_v20_2_links.csv"
)

RESULT_FILE = V20 / (
    "event_streaming_v20_4_results.json"
)
STREAM_FILE = V20 / (
    "event_streaming_v20_4_stream.jsonl"
)
FRAMES_FILE = V20 / (
    "event_streaming_v20_4_frames.json"
)
REPORT_FILE = V20 / (
    "EVENT_STREAMING_V20_4.md"
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


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Required file missing: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid JSON object: {path.name}"
        )

    return data


def load_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Required CSV missing: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    if not rows:
        raise ValueError(
            f"CSV contains no records: {path.name}"
        )

    return rows


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
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

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            data,
            handle,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


def write_jsonl(path, records):
    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for record in records:
            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    allow_nan=False,
                    sort_keys=True,
                )
                + "\n"
            )


def number(value):
    result = float(value)

    if not math.isfinite(result):
        raise ValueError(
            "Invalid non-finite measurement"
        )

    return result


def rounded(value):
    return round(number(value), 6)


def flag(value):
    if isinstance(value, bool):
        return value

    if str(value).lower() == "true":
        return True

    if str(value).lower() == "false":
        return False

    raise ValueError(
        f"Invalid Boolean value: {value}"
    )


def validate_sources(arch, sim, threat, timeline):
    check(
        "V20.1 architecture passed",
        arch.get("version") == "V20.1"
        and arch.get("status") == "ARCHITECTURE_PASS"
        and arch.get("checks_failed") == 0,
    )

    check(
        "V20.2 simulation passed",
        sim.get("version") == "V20.2"
        and sim.get("status") == "NETWORK_SIMULATION_PASS"
        and sim.get("checks_failed") == 0,
    )

    check(
        "V20.3 threat analysis passed",
        threat.get("version") == "V20.3"
        and threat.get("status") == "THREAT_SCENARIO_PASS"
        and threat.get("checks_failed") == 0,
    )

    model = arch.get("architecture_model", {})

    check(
        "Architecture model fingerprint valid",
        sha256_model(model)
        == arch.get("architecture_sha256"),
    )

    check(
        "V20.2 references current architecture",
        sim.get("architecture_file_sha256")
        == sha256_file(ARCH_FILE),
    )

    sources = threat.get("source_sha256", {})

    for key, path in (
        ("architecture", ARCH_FILE),
        ("simulation", SIM_FILE),
        ("nodes_csv", NODE_FILE),
        ("links_csv", LINK_FILE),
    ):
        check(
            f"V20.3 source verified: {key}",
            sources.get(key) == sha256_file(path),
        )

    check(
        "Timeline version valid",
        timeline.get("version") == "V20.3"
        and timeline.get("simulation_mode") is True
        and timeline.get("is_live") is False,
    )

    check(
        "Simulation-only operation",
        model.get("simulation_mode") is True
        and model.get("network_access_enabled") is False
        and model.get("real_attack_execution") is False
        and sim.get("real_network_access") is False
        and threat.get("real_network_access") is False,
    )

    return model


def index_observations(rows, id_field):
    indexed = defaultdict(list)
    keys = set()

    for row in rows:
        tick = int(row["tick"])
        item_id = row[id_field]
        identity = (tick, item_id)

        if identity in keys:
            raise ValueError(
                f"Duplicate observation: {identity}"
            )

        keys.add(identity)
        indexed[tick].append(row)

    return indexed


def index_alerts(rows):
    indexed = defaultdict(list)
    event_ids = set()

    for row in rows:
        event_id = row["event_id"]

        if event_id in event_ids:
            raise ValueError(
                f"Duplicate event: {event_id}"
            )

        event_ids.add(event_id)
        indexed[int(row["tick"])].append(row)

    return indexed


def create_frames(
    model,
    sim,
    threat,
    timeline,
    node_rows,
    link_rows,
    alert_rows,
):
    node_index = index_observations(
        node_rows, "node_id"
    )
    link_index = index_observations(
        link_rows, "link_id"
    )
    alert_index = index_alerts(alert_rows)

    nodes = model["architecture"]["nodes"]
    edges = model["architecture"]["edges"]

    expected_nodes = {
        node["id"] for node in nodes
    }
    expected_links = {
        edge["id"] for edge in edges
    }

    frames = []

    for source in timeline["timeline"]:
        tick = int(source["tick"])

        current_nodes = []

        for row in node_index.get(tick, []):
            current_nodes.append({
                "id": row["node_id"],
                "load": rounded(row["load"]),
                "risk_score": rounded(
                    row["risk_score"]
                ),
                "risk_level": row["risk_level"],
                "injected_anomaly": flag(
                    row["injected_anomaly"]
                ),
            })

        current_links = []

        for row in link_index.get(tick, []):
            current_links.append({
                "id": row["link_id"],
                "source": row["source"],
                "target": row["target"],
                "traffic_mbps": rounded(
                    row["traffic_mbps"]
                ),
                "latency_ms": rounded(
                    row["latency_ms"]
                ),
                "utilization": rounded(
                    row["utilization"]
                ),
                "injected_anomaly": flag(
                    row["injected_anomaly"]
                ),
            })

        current_alerts = []

        for row in alert_index.get(tick, []):
            current_alerts.append({
                "event_id": row["event_id"],
                "node_id": row["node_id"],
                "scenario_id": row["scenario_id"],
                "category": row["threat_category"],
                "risk_score": rounded(
                    row["enriched_risk_score"]
                ),
                "risk_level": row[
                    "enriched_risk_level"
                ],
                "injected_anomaly": flag(
                    row["injected_anomaly"]
                ),
            })

        if {
            item["id"] for item in current_nodes
        } != expected_nodes:
            raise ValueError(
                f"Invalid nodes at tick {tick}"
            )

        if {
            item["id"] for item in current_links
        } != expected_links:
            raise ValueError(
                f"Invalid links at tick {tick}"
            )

        if len(current_alerts) != int(
            source["alert_count"]
        ):
            raise ValueError(
                f"Alert count mismatch at tick {tick}"
            )

        current_nodes.sort(
            key=lambda item: item["id"]
        )
        current_links.sort(
            key=lambda item: item["id"]
        )
        current_alerts.sort(
            key=lambda item: item["event_id"]
        )

        frames.append({
            "sequence": tick,
            "timestamp": source["timestamp"],
            "event_type": "digital_twin_frame",
            "simulation_mode": True,
            "network": {
                "nodes": current_nodes,
                "links": current_links,
            },
            "metrics": {
                "total_traffic_mbps": rounded(
                    source["total_traffic_mbps"]
                ),
                "mean_latency_ms": rounded(
                    source["mean_latency_ms"]
                ),
                "maximum_enriched_risk": rounded(
                    source["highest_enriched_risk"]
                ),
                "alert_count": len(
                    current_alerts
                ),
                "anomaly_injected": bool(
                    source["anomaly_injected"]
                ),
            },
            "alerts": current_alerts,
        })

    return frames


def create_stream(frames):
    stream = []

    for frame in frames:
        stream.append({
            "stream_version": "V20.4",
            "sequence": frame["sequence"],
            "timestamp": frame["timestamp"],
            "event_type": "digital_twin_update",
            "simulation_mode": True,
            "metrics": frame["metrics"],
            "nodes": frame["network"]["nodes"],
            "links": frame["network"]["links"],
            "alerts": frame["alerts"],
        })

    return stream


def validate_stream(
    frames,
    stream,
    sim,
    threat,
    model,
):
    count = sim["metrics"]["ticks"]

    check(
        "Correct number of frames",
        len(frames) == count,
    )

    check(
        "Correct stream message count",
        len(stream) == count,
    )

    check(
        "Sequence numbers continuous",
        [
            item["sequence"] for item in frames
        ] == list(range(count)),
    )

    check(
        "Stream sequence matches frames",
        [
            item["sequence"] for item in stream
        ] == [
            item["sequence"] for item in frames
        ],
    )

    check(
        "Frame timestamps ordered",
        [
            frame["timestamp"] for frame in frames
        ] == sorted(
            frame["timestamp"] for frame in frames
        ),
    )

    check(
        "Every frame contains all network nodes",
        all(
            len(frame["network"]["nodes"])
            == sim["metrics"]["network_nodes"]
            for frame in frames
        ),
    )

    check(
        "Every frame contains all network links",
        all(
            len(frame["network"]["links"])
            == sim["metrics"]["network_links"]
            for frame in frames
        ),
    )

    check(
        "Alert count matches V20.3",
        sum(
            len(frame["alerts"])
            for frame in frames
        ) == threat["metrics"]["total_alerts"],
    )

    check(
        "Risk values bounded",
        all(
            0 <= node["risk_score"] <= 1
            for frame in frames
            for node in frame["network"]["nodes"]
        ),
    )

    check(
        "Node loads bounded",
        all(
            0 <= node["load"] <= 1
            for frame in frames
            for node in frame["network"]["nodes"]
        ),
    )

    check(
        "Traffic values nonnegative",
        all(
            link["traffic_mbps"] >= 0
            for frame in frames
            for link in frame["network"]["links"]
        ),
    )

    check(
        "Latency values nonnegative",
        all(
            link["latency_ms"] >= 0
            for frame in frames
            for link in frame["network"]["links"]
        ),
    )

    check(
        "All messages explicitly synthetic",
        all(
            item["simulation_mode"] is True
            for item in stream
        ),
    )

    check(
        "Every alert has a valid node",
        all(
            alert["node_id"] in {
                node["id"]
                for node in frame["network"]["nodes"]
            }
            for frame in frames
            for alert in frame["alerts"]
        ),
    )

    check(
        "Tick alert totals consistent",
        all(
            frame["metrics"]["alert_count"]
            == len(frame["alerts"])
            for frame in frames
        ),
    )

    check(
        "Simulation tick interval positive",
        model["simulation_config"][
            "tick_interval_ms"
        ] > 0,
    )


def create_metrics(frames, stream):
    total_alerts = sum(
        len(frame["alerts"])
        for frame in frames
    )

    risk_levels = Counter(
        alert["risk_level"]
        for frame in frames
        for alert in frame["alerts"]
    )

    return {
        "total_frames": len(frames),
        "stream_messages": len(stream),
        "total_alerts": total_alerts,
        "network_nodes_per_frame": len(
            frames[0]["network"]["nodes"]
        ),
        "network_links_per_frame": len(
            frames[0]["network"]["links"]
        ),
        "anomaly_ticks": sum(
            frame["metrics"]["anomaly_injected"]
            for frame in frames
        ),
        "highest_enriched_risk": max(
            frame["metrics"][
                "maximum_enriched_risk"
            ]
            for frame in frames
        ),
        "alert_risk_levels": dict(risk_levels),
    }


def create_markdown(result):
    metrics = result["metrics"]

    return f"""# Quantum Cyber Defense Arena

## V20.4 - Event Streaming Engine

**Status:** {result['status']}

### Simulation results

- Dashboard frames: {metrics['total_frames']}
- Stream messages: {metrics['stream_messages']}
- Network nodes per frame: {metrics['network_nodes_per_frame']}
- Network links per frame: {metrics['network_links_per_frame']}
- Synthetic alerts: {metrics['total_alerts']}
- Anomaly ticks: {metrics['anomaly_ticks']}
- Highest enriched risk: {metrics['highest_enriched_risk']}

### Architecture

V20.1: Simulated network topology

V20.2: Network traffic and node observations

V20.3: Deterministic threat scenario matching

V20.4: Ordered replayable event stream

### Data exports

- event_streaming_v20_4_results.json
- event_streaming_v20_4_frames.json
- event_streaming_v20_4_stream.jsonl

### Replay

Run the Python module with --replay to
observe events in chronological order.

The replay reads saved simulation data.
It does not open an HTTP or WebSocket server.

### Scientific limitations

- Synthetic network data
- No real packet capture
- No trained AI detector in this stage
- No verified attack labels
- No external security actions
- No live event transport

### Next stage

V20.5 - Interactive Digital Twin Dashboard
"""


async def replay_frames(frames, delay):
    print()
    print("V20.4 SIMULATED EVENT REPLAY")
    print("Press CTRL+C to stop.")
    print()

    for frame in frames:
        metrics = frame["metrics"]

        print(
            f"TICK {frame['sequence']:03d} | "
            f"TRAFFIC {metrics['total_traffic_mbps']:.1f} Mbps | "
            f"LATENCY {metrics['mean_latency_ms']:.2f} ms | "
            f"RISK {metrics['maximum_enriched_risk']:.3f} | "
            f"ALERTS {metrics['alert_count']}"
        )

        await asyncio.sleep(delay)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replay",
        action="store_true",
        help="Replay saved simulation frames.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Delay between replay frames (seconds).",
    )

    args = parser.parse_args()

    if (
        not math.isfinite(args.delay)
        or args.delay < 0
    ):
        parser.error(
            "--delay must be a nonnegative finite number"
        )

    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V20.4 - EVENT STREAMING ENGINE")
    print("=" * 70)

    V20.mkdir(
        parents=True,
        exist_ok=True,
    )

    arch = load_json(ARCH_FILE)
    sim = load_json(SIM_FILE)
    threat = load_json(THREAT_FILE)
    timeline = load_json(TIMELINE_FILE)

    node_rows = load_csv(NODE_FILE)
    link_rows = load_csv(LINK_FILE)
    alert_rows = load_csv(CLASSIFIED_FILE)

    model = validate_sources(
        arch, sim, threat, timeline
    )

    frames = create_frames(
        model,
        sim,
        threat,
        timeline,
        node_rows,
        link_rows,
        alert_rows,
    )

    stream = create_stream(frames)

    validate_stream(
        frames,
        stream,
        sim,
        threat,
        model,
    )

    # Repeat to prove deterministic construction.
    repeated = create_frames(
        model,
        sim,
        threat,
        timeline,
        node_rows,
        link_rows,
        alert_rows,
    )

    check(
        "Frame generation is deterministic",
        frames == repeated,
    )

    metrics = create_metrics(
        frames,
        stream,
    )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )
    failed = len(CHECKS) - passed

    status = (
        "EVENT_STREAMING_PASS"
        if failed == 0
        else "EVENT_STREAMING_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V20.4",
        "module": "Event Streaming Engine",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "data_source": "saved_synthetic_simulation",
        "live_network_stream": False,
        "http_server_running": False,
        "websocket_server_running": False,
        "external_actions_enabled": False,
        "replay_supported": True,
        "metrics": metrics,
        "source_sha256": {
            path.name: sha256_file(path)
            for path in [
                ARCH_FILE,
                SIM_FILE,
                THREAT_FILE,
                TIMELINE_FILE,
                NODE_FILE,
                LINK_FILE,
                CLASSIFIED_FILE,
            ]
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "next_stage": (
            "V20.5 Interactive Digital Twin Dashboard"
        ),
    }

    write_json(
        RESULT_FILE,
        result,
    )

    if failed == 0:
        write_json(
            FRAMES_FILE,
            {
                "version": "V20.4",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "frame_count": len(frames),
                "frames": frames,
            },
        )

        write_jsonl(
            STREAM_FILE,
            stream,
        )

        REPORT_FILE.write_text(
            create_markdown(result),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V20.4 EVENT STREAMING RESULTS")
    print("=" * 70)
    print(
        f"STREAM FRAMES: {metrics['total_frames']}"
    )
    print(
        f"STREAM MESSAGES: {metrics['stream_messages']}"
    )
    print(
        f"NETWORK NODES: {metrics['network_nodes_per_frame']}"
    )
    print(
        f"NETWORK LINKS: {metrics['network_links_per_frame']}"
    )
    print(
        f"SYNTHETIC ALERTS: {metrics['total_alerts']}"
    )
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"V20.4 RESULT: {status}")
    print("=" * 70)

    if failed == 0 and args.replay:
        asyncio.run(
            replay_frames(
                frames,
                args.delay,
            )
        )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nReplay stopped.")
        sys.exit(130)
    except Exception as error:
        print()
        print(
            "V20.4 FAILED:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
