
"""
QUANTUM CYBER DEFENSE ARENA
V20.6 - CYBER DIGITAL TWIN RESEARCH RELEASE

Validates the complete V20 research pipeline:
V20.1 Architecture
V20.2 Network Simulation
V20.3 Threat Scenarios
V20.4 Event Streaming
V20.5 D3 Dashboard

Exports:
- cyber_digital_twin_release_v20_6_results.json
- V20_RESEARCH_RELEASE.md
- frontend/public/v20/release_summary.json

Standard library only.
No network scanning or external actions.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V20 = ROOT / "research_validation" / "v20"
PUBLIC = ROOT / "frontend" / "public" / "v20"

INPUTS = {
    "architecture": V20 / "digital_twin_architecture_v20_1_results.json",
    "simulation": V20 / "network_simulation_v20_2_results.json",
    "threat": V20 / "ai_threat_scenario_v20_3_results.json",
    "streaming": V20 / "event_streaming_v20_4_results.json",
    "nodes": V20 / "network_simulation_v20_2_nodes.csv",
    "links": V20 / "network_simulation_v20_2_links.csv",
    "events": V20 / "network_simulation_v20_2_events.json",
    "classified": V20 / "ai_threat_scenario_v20_3_events.csv",
    "timeline": V20 / "ai_threat_scenario_v20_3_timeline.json",
    "frames": V20 / "event_streaming_v20_4_frames.json",
    "stream": V20 / "event_streaming_v20_4_stream.jsonl",
    "dashboard": PUBLIC / "dashboard.html",
    "dashboard_frames": PUBLIC / "frames.json",
}

OUTPUT_JSON = V20 / "cyber_digital_twin_release_v20_6_results.json"
OUTPUT_MD = V20 / "V20_RESEARCH_RELEASE.md"
PUBLIC_SUMMARY = PUBLIC / "release_summary.json"

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
        print("       " + str(detail))

    return passed


def digest(path):
    sha = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            sha.update(chunk)

    return sha.hexdigest()


def model_hash(model):
    raw = json.dumps(
        model,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as f:
        result = json.load(f)

    if not isinstance(result, dict):
        raise ValueError(f"Expected JSON object: {path.name}")

    return result


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError(f"Empty CSV: {path.name}")

    return rows


def read_jsonl(path):
    result = []

    with path.open("r", encoding="utf-8-sig") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                raise ValueError(
                    f"Blank JSONL line {line_number}"
                )

            item = json.loads(line)

            if not isinstance(item, dict):
                raise ValueError(
                    f"Invalid JSONL record {line_number}"
                )

            result.append(item)

    return result


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


def finite(value):
    if isinstance(value, bool):
        return False

    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def approximately(a, b, tolerance=1e-4):
    return (
        finite(a)
        and finite(b)
        and math.isclose(
            float(a),
            float(b),
            rel_tol=1e-6,
            abs_tol=tolerance,
        )
    )


def verify_inputs():
    available = True

    for key, path in INPUTS.items():
        exists = path.is_file()

        check(
            f"Required file: {key}",
            exists,
            path,
        )

        available = available and exists

    return available


def verify_versions(reports):
    expected = {
        "architecture": ("V20.1", "ARCHITECTURE_PASS"),
        "simulation": ("V20.2", "NETWORK_SIMULATION_PASS"),
        "threat": ("V20.3", "THREAT_SCENARIO_PASS"),
        "streaming": ("V20.4", "EVENT_STREAMING_PASS"),
    }

    for key, (version, status) in expected.items():
        report = reports[key]

        check(
            f"{key}: version",
            report.get("version") == version,
        )

        check(
            f"{key}: status",
            report.get("status") == status,
        )

        source_checks = report.get("checks", [])

        internal_ok = (
            isinstance(source_checks, list)
            and len(source_checks) > 0
            and report.get("checks_failed") == 0
            and report.get("checks_passed")
            == len(source_checks)
            and all(
                isinstance(item, dict)
                and item.get("passed") is True
                for item in source_checks
            )
        )

        check(
            f"{key}: internal checks",
            internal_ok,
        )


def verify_source_integrity(reports):
    architecture = reports["architecture"]
    simulation = reports["simulation"]
    threat = reports["threat"]
    streaming = reports["streaming"]

    model = architecture["architecture_model"]
    actual_model_hash = model_hash(model)

    check(
        "V20.1 model fingerprint",
        actual_model_hash
        == architecture.get("architecture_sha256"),
    )

    check(
        "V20.2 source architecture fingerprint",
        simulation.get("architecture_file_sha256")
        == digest(INPUTS["architecture"]),
    )

    check(
        "V20.2 model fingerprint",
        simulation.get("architecture_model_sha256")
        == actual_model_hash,
    )

    threat_sources = threat.get("source_sha256", {})

    threat_mapping = {
        "architecture": "architecture",
        "simulation": "simulation",
        "events": "events",
        "nodes_csv": "nodes",
        "links_csv": "links",
    }

    for source_key, input_key in threat_mapping.items():
        check(
            f"V20.3 fingerprint: {source_key}",
            threat_sources.get(source_key)
            == digest(INPUTS[input_key]),
        )

    stream_sources = streaming.get("source_sha256", {})

    for key in (
        "architecture",
        "simulation",
        "threat",
        "timeline",
        "nodes",
        "links",
        "classified",
    ):
        path = INPUTS[key]

        check(
            f"V20.4 fingerprint: {key}",
            stream_sources.get(path.name) == digest(path),
        )


def verify_safety(reports):
    architecture = reports["architecture"]["architecture_model"]
    simulation = reports["simulation"]
    threat = reports["threat"]
    streaming = reports["streaming"]

    check(
        "Architecture simulation-only",
        architecture.get("simulation_mode") is True
        and architecture.get("network_access_enabled") is False
        and architecture.get("real_attack_execution") is False,
    )

    check(
        "Simulation uses no real network",
        simulation.get("simulation_mode") is True
        and simulation.get("live_data") is False
        and simulation.get("real_network_access") is False,
    )

    check(
        "Threat engine is rule-based",
        threat.get("trained_ai_model_used") is False
        and threat.get("external_actions_enabled") is False,
    )

    check(
        "Event stream is replay-only",
        streaming.get("live_network_stream") is False
        and streaming.get("websocket_server_running") is False
        and streaming.get("external_actions_enabled") is False,
    )


def verify_dataset(reports, data):
    model = reports["architecture"]["architecture_model"]

    topology = model["architecture"]
    simulation = reports["simulation"]
    threat = reports["threat"]
    streaming = reports["streaming"]

    nodes = topology["nodes"]
    links = topology["edges"]

    node_rows = data["nodes"]
    link_rows = data["links"]
    events = data["events"]["events"]
    classified = data["classified"]
    timeline = data["timeline"]["timeline"]
    frames = data["frames"]["frames"]
    messages = data["stream"]

    ticks = simulation["metrics"]["ticks"]

    node_ids = {node["id"] for node in nodes}
    link_ids = {link["id"] for link in links}

    check(
        "Network has 10 nodes",
        len(nodes) == 10
        and len(node_ids) == 10,
    )

    check(
        "Network has 11 links",
        len(links) == 11
        and len(link_ids) == 11,
    )

    check(
        "120 simulation ticks",
        ticks == 120,
    )

    check(
        "Node observation count",
        len(node_rows) == ticks * len(nodes)
        and len(node_rows)
        == simulation["metrics"]["node_observations"],
    )

    check(
        "Link observation count",
        len(link_rows) == ticks * len(links)
        and len(link_rows)
        == simulation["metrics"]["link_observations"],
    )

    check(
        "Node identities and ticks valid",
        {
            (int(row["tick"]), row["node_id"])
            for row in node_rows
        }
        == {
            (tick, node_id)
            for tick in range(ticks)
            for node_id in node_ids
        },
    )

    check(
        "Link identities and ticks valid",
        {
            (int(row["tick"]), row["link_id"])
            for row in link_rows
        }
        == {
            (tick, link_id)
            for tick in range(ticks)
            for link_id in link_ids
        },
    )

    check(
        "Node risk measurements bounded",
        all(
            finite(row["risk_score"])
            and 0 <= float(row["risk_score"]) <= 1
            for row in node_rows
        ),
    )

    check(
        "Node load measurements bounded",
        all(
            finite(row["load"])
            and 0 <= float(row["load"]) <= 1
            for row in node_rows
        ),
    )

    check(
        "Link traffic and latency valid",
        all(
            finite(row["traffic_mbps"])
            and float(row["traffic_mbps"]) >= 0
            and finite(row["latency_ms"])
            and float(row["latency_ms"]) >= 0
            for row in link_rows
        ),
    )

    check(
        "Source events match simulation count",
        len(events) == simulation["metrics"]["alerts"]
        and data["events"].get("event_count") == len(events),
    )

    check(
        "Classified events match source alerts",
        len(classified) == len(events)
        and len(classified)
        == threat["metrics"]["total_alerts"]
        and {
            item["event_id"] for item in events
        } == {
            item["event_id"] for item in classified
        },
    )

    check(
        "Event classifications are synthetic",
        all(
            item["synthetic"] is True
            for item in events
        )
        and all(
            str(item["synthetic"]).lower() == "true"
            and item["classification_method"]
            == "deterministic_rule_based"
            for item in classified
        ),
    )

    check(
        "Threat timeline complete",
        len(timeline) == ticks
        and data["timeline"].get("ticks") == ticks
        and [
            item["tick"] for item in timeline
        ] == list(range(ticks)),
    )

    check(
        "120 dashboard frames",
        len(frames) == ticks
        and data["frames"].get("frame_count") == ticks,
    )

    check(
        "120 stream messages",
        len(messages) == ticks
        and streaming["metrics"]["stream_messages"] == ticks,
    )

    check(
        "Frame and message sequences complete",
        [
            frame["sequence"] for frame in frames
        ] == list(range(ticks))
        and [
            message["sequence"] for message in messages
        ] == list(range(ticks)),
    )

    check(
        "Frames contain complete topology",
        all(
            {node["id"] for node in frame["network"]["nodes"]}
            == node_ids
            and {
                link["id"] for link in frame["network"]["links"]
            } == link_ids
            for frame in frames
        ),
    )

    check(
        "JSONL messages reproduce frames",
        all(
            message["nodes"] == frame["network"]["nodes"]
            and message["links"] == frame["network"]["links"]
            and message["alerts"] == frame["alerts"]
            and message["metrics"] == frame["metrics"]
            and message["timestamp"] == frame["timestamp"]
            for frame, message in zip(frames, messages)
        ),
    )

    check(
        "Frame alerts match source counts",
        sum(
            len(frame["alerts"]) for frame in frames
        ) == len(classified)
        and all(
            frame["metrics"]["alert_count"]
            == len(frame["alerts"])
            for frame in frames
        ),
    )

    check(
        "Frame and timeline timestamps match",
        all(
            frame["timestamp"] == item["timestamp"]
            for frame, item in zip(frames, timeline)
        ),
    )

    check(
        "All frames explicitly simulated",
        data["frames"].get("simulation_mode") is True
        and data["frames"].get("is_live") is False
        and all(
            frame.get("simulation_mode") is True
            for frame in frames
        ),
    )

    check(
        "V20.4 reported metrics match exports",
        streaming["metrics"]["total_frames"] == len(frames)
        and streaming["metrics"]["total_alerts"]
        == len(classified)
        and streaming["metrics"]["network_nodes_per_frame"]
        == len(nodes)
        and streaming["metrics"]["network_links_per_frame"]
        == len(links),
    )

    return {
        "ticks": ticks,
        "nodes": len(nodes),
        "links": len(links),
        "node_observations": len(node_rows),
        "link_observations": len(link_rows),
        "events": len(events),
        "classified_alerts": len(classified),
        "frames": len(frames),
        "stream_messages": len(messages),
        "maximum_risk": max(
            (
                float(row["enriched_risk_score"])
                for row in classified
            ),
            default=0.0,
        ),
        "categories": dict(Counter(
            row["threat_category"] for row in classified
        )),
    }


def verify_dashboard(data):
    source_frames = data["frames"]
    dashboard_frames = data["dashboard_frames"]

    check(
        "Frontend uses current V20.4 frame export",
        source_frames == dashboard_frames,
    )

    check(
        "Dashboard explicitly labeled simulated",
        dashboard_frames.get("simulation_mode") is True
        and dashboard_frames.get("is_live") is False,
    )

    html = data["dashboard_html"]

    required_markers = {
        "D3 dependency": "d3@7",
        "Network visualization": 'id="network"',
        "Play/Pause": 'id="playPause"',
        "Restart": 'id="restart"',
        "Speed control": 'id="speed"',
        "Timeline": 'id="timeline"',
        "Simulation data loader": 'fetch("./frames.json"',
        "Risk monitoring": 'id="riskValue"',
        "Alerts panel": 'id="alerts"',
        "Simulated data label": "SIMULATED",
    }

    for label, marker in required_markers.items():
        check(
            f"Dashboard feature: {label}",
            marker in html,
        )

    check(
        "Dashboard HTML structure present",
        "<!DOCTYPE html>" in html
        and "</html>" in html,
    )


def source_manifest():
    return {
        key: {
            "path": str(path.relative_to(ROOT)),
            "sha256": digest(path),
            "size_bytes": path.stat().st_size,
        }
        for key, path in INPUTS.items()
        if path.is_file()
    }


def create_markdown(report):
    metrics = report["metrics"]

    return f"""# Quantum Cyber Defense Arena

## V20 - Cyber Digital Twin Research Release

**Release version:** V20.6

**Status:** {report['status']}

**Checks passed:** {report['checks_passed']}

**Checks failed:** {report['checks_failed']}

### Modules

| Version | Module |
|---|---|
| V20.1 | Cyber Digital Twin Architecture |
| V20.2 | Network Simulation Engine |
| V20.3 | Rule-Based Threat Scenario Engine |
| V20.4 | Event Streaming and Replay |
| V20.5 | Interactive D3 Dashboard |
| V20.6 | Research Validation and Release |

### Validated dataset

| Metric | Value |
|---|---|
| Simulated nodes | {metrics['nodes']} |
| Simulated links | {metrics['links']} |
| Simulation ticks | {metrics['ticks']} |
| Node observations | {metrics['node_observations']} |
| Link observations | {metrics['link_observations']} |
| Synthetic alerts | {metrics['classified_alerts']} |
| Dashboard frames | {metrics['frames']} |
| Replay messages | {metrics['stream_messages']} |
| Maximum enriched risk | {metrics['maximum_risk']:.6f} |

### Interactive dashboard

`frontend/public/v20/dashboard.html`

The dashboard replays the validated V20.4 frames.

Features include a fixed network topology,
animated data particles, risk indicators,
alerts, playback controls and timeline scrubbing.

### Reproducibility

The release report records SHA-256 fingerprints
for the upstream research files and frontend assets.

### Scientific limitations

- Network data are synthetic
- No real packet capture
- No live cyberattack detection
- No trained AI threat detector in V20.3
- No independent verified attack labels
- No production security guarantees
- This validation does not replace browser testing
- Dashboard D3 dependency is loaded from a CDN

### Next development stage

V21 - Advanced Cyber Defense Intelligence
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V20.6 - CYBER DIGITAL TWIN RESEARCH RELEASE")
    print("=" * 70)

    V20.mkdir(parents=True, exist_ok=True)

    available = verify_inputs()
    metrics = {}
    error_message = None

    if available:
        try:
            reports = {
                key: read_json(INPUTS[key])
                for key in (
                    "architecture",
                    "simulation",
                    "threat",
                    "streaming",
                )
            }

            data = {
                "nodes": read_csv(INPUTS["nodes"]),
                "links": read_csv(INPUTS["links"]),
                "events": read_json(INPUTS["events"]),
                "classified": read_csv(INPUTS["classified"]),
                "timeline": read_json(INPUTS["timeline"]),
                "frames": read_json(INPUTS["frames"]),
                "stream": read_jsonl(INPUTS["stream"]),
                "dashboard_frames": read_json(
                    INPUTS["dashboard_frames"]
                ),
                "dashboard_html": INPUTS["dashboard"].read_text(
                    encoding="utf-8-sig"
                ),
            }

            verify_versions(reports)
            verify_source_integrity(reports)
            verify_safety(reports)

            metrics = verify_dataset(reports, data)
            verify_dashboard(data)

        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            IndexError,
        ) as exc:
            error_message = f"{type(exc).__name__}: {exc}"
            check(
                "Complete research validation",
                False,
                error_message,
            )

    passed = sum(
        item["passed"] for item in CHECKS
    )
    failed = len(CHECKS) - passed

    status = (
        "CYBER_DIGITAL_TWIN_RELEASE_PASS"
        if failed == 0 and metrics
        else "CYBER_DIGITAL_TWIN_RELEASE_FAIL"
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V20.6",
        "module": "Cyber Digital Twin Research Release",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "real_network_monitoring": False,
        "trained_threat_detector_in_v20_3": False,
        "metrics": metrics,
        "source_manifest": source_manifest(),
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error_message,
        "outputs": {
            "release_json": str(OUTPUT_JSON.relative_to(ROOT)),
            "release_markdown": str(OUTPUT_MD.relative_to(ROOT)),
            "dashboard_summary": str(
                PUBLIC_SUMMARY.relative_to(ROOT)
            ),
        },
        "next_stage": "V21 Advanced Cyber Defense Intelligence",
    }

    write_json(OUTPUT_JSON, report)

    if status == "CYBER_DIGITAL_TWIN_RELEASE_PASS":
        OUTPUT_MD.write_text(
            create_markdown(report),
            encoding="utf-8",
        )

        write_json(
            PUBLIC_SUMMARY,
            {
                "version": "V20.6",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "metrics": metrics,
                "checks_passed": passed,
                "checks_failed": failed,
            },
        )

    print()
    print("=" * 70)
    print("V20.6 FINAL RELEASE RESULTS")
    print("=" * 70)

    if metrics:
        print(f"NETWORK NODES: {metrics['nodes']}")
        print(f"NETWORK LINKS: {metrics['links']}")
        print(f"SIMULATION TICKS: {metrics['ticks']}")
        print(f"CLASSIFIED ALERTS: {metrics['classified_alerts']}")
        print(f"DASHBOARD FRAMES: {metrics['frames']}")

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")

    if error_message:
        print(f"ERROR: {error_message}")

    print(f"JSON REPORT: {OUTPUT_JSON}")

    if status == "CYBER_DIGITAL_TWIN_RELEASE_PASS":
        print(f"RESEARCH DOCUMENT: {OUTPUT_MD}")
        print(f"DASHBOARD SUMMARY: {PUBLIC_SUMMARY}")

    print(f"V20.6 RESULT: {status}")
    print("=" * 70)

    return 0 if status == "CYBER_DIGITAL_TWIN_RELEASE_PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(
            "V20.6 FATAL ERROR:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
