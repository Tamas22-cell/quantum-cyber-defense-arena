
"""
QUANTUM CYBER DEFENSE ARENA
V21.2 - BEHAVIORAL ANOMALY DETECTION

Historical rolling-baseline anomaly detection.

Inputs:
    V21.1 architecture report
    V20.4 event streaming frames

Outputs:
    behavioral_anomaly_detection_v21_2_results.json
    behavioral_anomaly_detection_v21_2_scores.csv
    behavioral_anomaly_detection_v21_2_timeline.json
    BEHAVIORAL_ANOMALY_DETECTION_V21_2.md

Method:
    Rolling mean and standard deviation
    Previous observations only, no future data
    Node load / node risk / incident link traffic

Evaluation:
    Synthetic injected anomaly markers
    These are not real attack labels

Standard library only.
No real network access or external actions.
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

V20 = ROOT / "research_validation" / "v20"
V21 = ROOT / "research_validation" / "v21"

ARCH_FILE = V21 / (
    "threat_intelligence_architecture_v21_1_results.json"
)

FRAMES_FILE = V20 / (
    "event_streaming_v20_4_frames.json"
)

OUTPUT_JSON = V21 / (
    "behavioral_anomaly_detection_v21_2_results.json"
)

OUTPUT_CSV = V21 / (
    "behavioral_anomaly_detection_v21_2_scores.csv"
)

OUTPUT_TIMELINE = V21 / (
    "behavioral_anomaly_detection_v21_2_timeline.json"
)

OUTPUT_MD = V21 / (
    "BEHAVIORAL_ANOMALY_DETECTION_V21_2.md"
)

WINDOW = 12
MIN_HISTORY = 6
Z_THRESHOLD = 2.5
EPSILON = 0.05

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
        print("       " + str(detail))

    return passed


def read_json(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing source: {path}"
        )

    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid JSON object: {path.name}"
        )

    return data


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def sha256_object(value):
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


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


def write_csv(path, rows):
    if not rows:
        raise ValueError("No score records to export")

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0]),
        )
        writer.writeheader()
        writer.writerows(rows)


def safe_number(value):
    if isinstance(value, bool):
        raise ValueError(
            "Boolean value used as numeric measurement"
        )

    result = float(value)

    if not math.isfinite(result):
        raise ValueError("Non-finite measurement")

    return result


def rounded(value):
    return round(float(value), 6)


def validate_sources(architecture, export):
    check(
        "V21.1 architecture passed",
        architecture.get("version") == "V21.1"
        and architecture.get("status")
        == "THREAT_INTELLIGENCE_ARCHITECTURE_PASS"
        and architecture.get("checks_failed") == 0,
    )

    model = architecture.get("architecture")

    if not isinstance(model, dict):
        raise ValueError(
            "V21.1 architecture model missing"
        )

    check(
        "V21.1 architecture fingerprint verified",
        sha256_object(model)
        == architecture.get("architecture_sha256"),
    )

    check(
        "V21.1 simulation-only configuration",
        model.get("simulation_mode") is True
        and model.get("external_actions_enabled") is False,
    )

    check(
        "V21.2 registered as planned component",
        any(
            component.get("version") == "V21.2"
            for component in model.get("components", [])
        ),
    )

    manifest = architecture.get(
        "source_artifacts", {}
    )

    expected_hash = manifest.get(
        "v20_frames", {}
    ).get("sha256")

    check(
        "V20.4 frame source fingerprint matches V21.1",
        expected_hash == sha256_file(FRAMES_FILE),
    )

    check(
        "V20.4 frame export validated",
        export.get("version") == "V20.4"
        and export.get("status") == "EVENT_STREAMING_PASS"
        and export.get("simulation_mode") is True
        and export.get("is_live") is False,
    )

    frames = export.get("frames")

    if not isinstance(frames, list) or not frames:
        raise ValueError("V20.4 frames are missing")

    check(
        "Frame count agrees with metadata",
        len(frames) == export.get("frame_count"),
    )

    check(
        "120 research frames available",
        len(frames) == 120,
    )

    check(
        "Frame sequences continuous",
        [
            frame.get("sequence")
            for frame in frames
        ] == list(range(len(frames))),
    )

    check(
        "All observations explicitly simulated",
        all(
            frame.get("simulation_mode") is True
            for frame in frames
        ),
    )

    topology = model.get("source_topology", {})
    expected_nodes = set(
        topology.get("node_ids", [])
    )
    expected_links = set(
        topology.get("link_ids", [])
    )

    check(
        "Topology has ten unique nodes",
        len(expected_nodes) == 10,
    )

    check(
        "Topology has eleven unique links",
        len(expected_links) == 11,
    )

    for tick, frame in enumerate(frames):
        network = frame.get("network", {})

        nodes = network.get("nodes", [])
        links = network.get("links", [])

        node_ids = [n["id"] for n in nodes]
        link_ids = [link["id"] for link in links]

        if (
            len(node_ids) != len(expected_nodes)
            or set(node_ids) != expected_nodes
            or len(link_ids) != len(expected_links)
            or set(link_ids) != expected_links
        ):
            raise ValueError(
                f"Topology mismatch at tick {tick}"
            )

        for node in nodes:
            load = safe_number(node["load"])
            risk = safe_number(node["risk_score"])

            if not (0 <= load <= 1 and 0 <= risk <= 1):
                raise ValueError(
                    f"Invalid node values at tick {tick}"
                )

            if not isinstance(
                node.get("injected_anomaly"), bool
            ):
                raise ValueError(
                    "Invalid synthetic marker"
                )

        for link in links:
            if (
                link["source"] not in expected_nodes
                or link["target"] not in expected_nodes
                or safe_number(link["traffic_mbps"]) < 0
            ):
                raise ValueError(
                    f"Invalid link at tick {tick}"
                )

    check(
        "All frame topologies and measurements valid",
        True,
    )

    return frames, sorted(expected_nodes)


def rolling_score(value, historical):
    """
    Historical-only score.

    Score is a positive deviation from the
    previous WINDOW observations.

    Never uses the current observation in
    the reference baseline.
    """

    history = historical[-WINDOW:]

    if len(history) < MIN_HISTORY:
        return {
            "z": 0.0,
            "ready": False,
        }

    mean = statistics.mean(history)
    std = statistics.pstdev(history)

    denominator = max(std, EPSILON)

    z = max(
        0.0,
        (value - mean) / denominator,
    )

    return {
        "z": rounded(z),
        "ready": True,
    }


def build_feature_records(frames, node_ids):
    records = []

    for frame in frames:
        tick = frame["sequence"]

        nodes = {
            node["id"]: node
            for node in frame["network"]["nodes"]
        }

        traffic = defaultdict(float)
        link_injected_nodes = set()

        for link in frame["network"]["links"]:
            volume = safe_number(
                link["traffic_mbps"]
            )

            traffic[link["source"]] += volume
            traffic[link["target"]] += volume

            if link.get("injected_anomaly") is True:
                link_injected_nodes.add(link["source"])
                link_injected_nodes.add(link["target"])

        for node_id in node_ids:
            node = nodes[node_id]

            records.append({
                "tick": tick,
                "timestamp": frame["timestamp"],
                "node_id": node_id,
                "load": safe_number(node["load"]),
                "risk_score": safe_number(
                    node["risk_score"]
                ),
                "incident_traffic_mbps": traffic[
                    node_id
                ],
                "injected_anomaly": (
                    node["injected_anomaly"] is True
                ),
                "near_injected_link": (
                    node_id in link_injected_nodes
                ),
            })

    return records


def detect_anomalies(records):
    """
    Rolling historical baseline per node.

    Each observation is evaluated before
    updating its node's history.
    """

    history = defaultdict(
        lambda: {
            "load": [],
            "risk": [],
            "traffic": [],
        }
    )

    output = []

    for record in records:
        node_id = record["node_id"]
        node_history = history[node_id]

        load_result = rolling_score(
            record["load"],
            node_history["load"],
        )

        risk_result = rolling_score(
            record["risk_score"],
            node_history["risk"],
        )

        traffic_result = rolling_score(
            record["incident_traffic_mbps"],
            node_history["traffic"],
        )

        ready = (
            load_result["ready"]
            and risk_result["ready"]
            and traffic_result["ready"]
        )

        scores = [
            load_result["z"],
            risk_result["z"],
            traffic_result["z"],
        ]

        # Max-z strategy: flag a strong positive
        # deviation in any monitored feature.
        anomaly_score = max(scores) if ready else 0.0

        detected = (
            ready
            and anomaly_score >= Z_THRESHOLD
        )

        output.append({
            "tick": record["tick"],
            "timestamp": record["timestamp"],
            "node_id": node_id,
            "load": rounded(record["load"]),
            "risk_score": rounded(
                record["risk_score"]
            ),
            "incident_traffic_mbps": rounded(
                record["incident_traffic_mbps"]
            ),
            "load_z": load_result["z"],
            "risk_z": risk_result["z"],
            "traffic_z": traffic_result["z"],
            "anomaly_score": rounded(anomaly_score),
            "baseline_ready": ready,
            "detected_anomaly": detected,
            "injected_anomaly": record[
                "injected_anomaly"
            ],
            "near_injected_link": record[
                "near_injected_link"
            ],
            "detection_method": (
                "historical_rolling_z_score"
            ),
        })

        node_history["load"].append(
            record["load"]
        )
        node_history["risk"].append(
            record["risk_score"]
        )
        node_history["traffic"].append(
            record["incident_traffic_mbps"]
        )

    return output


def build_timeline(scores, frames):
    by_tick = defaultdict(list)

    for row in scores:
        by_tick[row["tick"]].append(row)

    timeline = []

    for frame in frames:
        tick = frame["sequence"]
        rows = by_tick[tick]

        detected = [
            row["node_id"]
            for row in rows
            if row["detected_anomaly"]
        ]

        timeline.append({
            "tick": tick,
            "timestamp": frame["timestamp"],
            "evaluated_nodes": len(rows),
            "detected_nodes": detected,
            "detections": len(detected),
            "maximum_anomaly_score": max(
                row["anomaly_score"]
                for row in rows
            ),
            "synthetic_injection_present": bool(
                frame["metrics"]["anomaly_injected"]
            ),
            "total_traffic_mbps": frame[
                "metrics"
            ]["total_traffic_mbps"],
        })

    return timeline


def evaluate_synthetic_markers(scores):
    """
    Compare detected flags to V20 injected
    node markers after warmup only.

    These markers are simulator metadata.
    This is NOT real-world detection accuracy.
    """

    eligible = [
        row
        for row in scores
        if row["baseline_ready"]
    ]

    tp = sum(
        row["detected_anomaly"]
        and row["injected_anomaly"]
        for row in eligible
    )

    fp = sum(
        row["detected_anomaly"]
        and not row["injected_anomaly"]
        for row in eligible
    )

    fn = sum(
        not row["detected_anomaly"]
        and row["injected_anomaly"]
        for row in eligible
    )

    tn = sum(
        not row["detected_anomaly"]
        and not row["injected_anomaly"]
        for row in eligible
    )

    precision = (
        tp / (tp + fp)
        if tp + fp else None
    )

    recall = (
        tp / (tp + fn)
        if tp + fn else None
    )

    return {
        "evaluation_type": "synthetic_injection_marker_agreement",
        "ground_truth_is_real_attack_labels": False,
        "warmup_observations_excluded": True,
        "eligible_observations": len(eligible),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "synthetic_marker_precision": (
            rounded(precision)
            if precision is not None else None
        ),
        "synthetic_marker_recall": (
            rounded(recall)
            if recall is not None else None
        ),
        "note": (
            "In-simulation agreement only. "
            "Not production detection performance."
        ),
    }


def validate_results(scores, timeline, frames, node_ids):
    ticks = len(frames)

    check(
        "All node observations scored",
        len(scores) == ticks * len(node_ids),
    )

    check(
        "One score per node per tick",
        len({
            (row["tick"], row["node_id"])
            for row in scores
        }) == len(scores),
    )

    check(
        "All node identifiers valid",
        all(
            row["node_id"] in node_ids
            for row in scores
        ),
    )

    check(
        "Scores nonnegative and finite",
        all(
            math.isfinite(row["anomaly_score"])
            and row["anomaly_score"] >= 0
            for row in scores
        ),
    )

    check(
        "Every detection uses an initialized baseline",
        all(
            not row["detected_anomaly"]
            or row["baseline_ready"]
            for row in scores
        ),
    )

    check(
        "No detections before history warmup",
        all(
            not row["detected_anomaly"]
            for row in scores
            if row["tick"] < MIN_HISTORY
        ),
    )

    check(
        "Every detection satisfies threshold",
        all(
            not row["detected_anomaly"]
            or row["anomaly_score"] >= Z_THRESHOLD
            for row in scores
        ),
    )

    check(
        "Detection flags exactly match scoring rule",
        all(
            row["detected_anomaly"] == (
                row["baseline_ready"]
                and row["anomaly_score"] >= Z_THRESHOLD
            )
            for row in scores
        ),
    )

    check(
        "All scores use declared method",
        all(
            row["detection_method"]
            == "historical_rolling_z_score"
            for row in scores
        ),
    )

    check(
        "Timeline covers all 120 ticks",
        len(timeline) == ticks
        and [
            item["tick"] for item in timeline
        ] == list(range(ticks)),
    )

    check(
        "Timeline detections consistent",
        sum(
            item["detections"]
            for item in timeline
        ) == sum(
            row["detected_anomaly"]
            for row in scores
        ),
    )

    check(
        "All historical node observations bounded",
        all(
            0 <= row["load"] <= 1
            and 0 <= row["risk_score"] <= 1
            and row["incident_traffic_mbps"] >= 0
            for row in scores
        ),
    )


def make_markdown(result):
    metrics = result["metrics"]
    evaluation = result["synthetic_evaluation"]

    return f"""# Quantum Cyber Defense Arena

## V21.2 - Behavioral Anomaly Detection

**Status:** {result['status']}

**Checks passed:** {result['checks_passed']}

**Checks failed:** {result['checks_failed']}

### Dataset

- Source: V20.4 simulated network frames
- Time steps: {metrics['ticks']}
- Nodes: {metrics['nodes']}
- Observations: {metrics['observations']}

### Method

Historical rolling z-score detector.

- Window: {WINDOW}
- Minimum historical observations: {MIN_HISTORY}
- Detection threshold: {Z_THRESHOLD}
- Features: node load, node risk and incident traffic

The baseline uses previous time steps only.
The current observation is scored before it
is added to the history.

### Results

- Flagged node observations: {metrics['detected_observations']}
- Affected nodes: {metrics['affected_nodes']}
- Maximum anomaly score: {metrics['maximum_anomaly_score']}

### Synthetic injection comparison

- Eligible observations: {evaluation['eligible_observations']}
- TP: {evaluation['true_positive']}
- FP: {evaluation['false_positive']}
- FN: {evaluation['false_negative']}
- TN: {evaluation['true_negative']}
- Synthetic marker precision: {evaluation['synthetic_marker_precision']}
- Synthetic marker recall: {evaluation['synthetic_marker_recall']}

These figures describe agreement with simulator
injection markers, not real cyberattack labels.

### Limitations

- Entire dataset is synthetic.
- Input risk scores are themselves simulated.
- Threshold is research-selected, not calibrated.
- Temporal and cross-node dependence remain.
- Synthetic evaluation is not independent validation.
- No trained AI model runs in this module.
- No production security effectiveness established.
- No external actions are performed.

### Exports

- behavioral_anomaly_detection_v21_2_results.json
- behavioral_anomaly_detection_v21_2_scores.csv
- behavioral_anomaly_detection_v21_2_timeline.json

### Next stage

V21.3 - Multi-Agent Threat Correlation
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V21.2 - BEHAVIORAL ANOMALY DETECTION")
    print("=" * 70)

    V21.mkdir(parents=True, exist_ok=True)

    architecture = read_json(ARCH_FILE)
    frame_export = read_json(FRAMES_FILE)

    frames, node_ids = validate_sources(
        architecture,
        frame_export,
    )

    features = build_feature_records(
        frames,
        node_ids,
    )

    scores = detect_anomalies(features)

    timeline = build_timeline(
        scores,
        frames,
    )

    validate_results(
        scores,
        timeline,
        frames,
        node_ids,
    )

    # Re-run in memory to verify identical results.
    second_run = detect_anomalies(features)

    check(
        "Anomaly detection is reproducible",
        scores == second_run,
    )

    # Verify that the baseline does not depend on
    # any later time step. The first half must
    # remain unchanged when the future is removed.
    midpoint = len(frames) // 2

    prefix_features = [
        row for row in features
        if row["tick"] < midpoint
    ]

    prefix_scores = detect_anomalies(
        prefix_features
    )

    check(
        "No future-data leakage in rolling scores",
        scores[:len(prefix_scores)] == prefix_scores,
    )

    evaluation = evaluate_synthetic_markers(
        scores
    )

    check(
        "Synthetic confusion matrix sums correctly",
        sum(
            evaluation[key]
            for key in (
                "true_positive",
                "false_positive",
                "false_negative",
                "true_negative",
            )
        ) == evaluation["eligible_observations"],
    )

    counts = Counter(
        row["node_id"]
        for row in scores
        if row["detected_anomaly"]
    )

    metrics = {
        "ticks": len(frames),
        "nodes": len(node_ids),
        "observations": len(scores),
        "detected_observations": sum(
            row["detected_anomaly"]
            for row in scores
        ),
        "affected_nodes": len(counts),
        "detections_by_node": dict(counts),
        "maximum_anomaly_score": rounded(
            max(
                row["anomaly_score"]
                for row in scores
            )
        ),
        "method": "historical_rolling_z_score",
        "window": WINDOW,
        "minimum_history": MIN_HISTORY,
        "z_threshold": Z_THRESHOLD,
        "trained_ai_model_used": False,
        "real_attack_detection_accuracy_measured": False,
    }

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "BEHAVIORAL_ANOMALY_PASS"
        if failed == 0
        else "BEHAVIORAL_ANOMALY_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V21.2",
        "module": "Behavioral Anomaly Detection",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "execution_mode": "deterministic_read_only",
        "external_actions_enabled": False,
        "source_sha256": {
            "architecture": sha256_file(
                ARCH_FILE
            ),
            "frames": sha256_file(
                FRAMES_FILE
            ),
        },
        "metrics": metrics,
        "synthetic_evaluation": evaluation,
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "limitations": [
            "Synthetic network telemetry only.",
            "Rolling statistical detector, not a trained AI.",
            "Injected anomalies are not real attack labels.",
            "No independent real-world accuracy evaluation.",
            "No live security actions.",
        ],
        "next_stage": (
            "V21.3 Multi-Agent Threat Correlation"
        ),
    }

    write_json(
        OUTPUT_JSON,
        result,
    )

    if failed == 0:
        write_csv(
            OUTPUT_CSV,
            scores,
        )

        write_json(
            OUTPUT_TIMELINE,
            {
                "version": "V21.2",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "ticks": len(timeline),
                "timeline": timeline,
            },
        )

        OUTPUT_MD.write_text(
            make_markdown(result),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V21.2 BEHAVIORAL ANOMALY RESULTS")
    print("=" * 70)

    print(f"NETWORK NODES: {metrics['nodes']}")
    print(f"SIMULATION TICKS: {metrics['ticks']}")
    print(
        "NODE OBSERVATIONS:",
        metrics["observations"],
    )
    print(
        "DETECTED ANOMALIES:",
        metrics["detected_observations"],
    )
    print(
        "AFFECTED NODES:",
        metrics["affected_nodes"],
    )

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {OUTPUT_JSON}")

    if failed == 0:
        print(f"SCORES CSV: {OUTPUT_CSV}")
        print(f"TIMELINE: {OUTPUT_TIMELINE}")
        print(f"RESEARCH DOCUMENT: {OUTPUT_MD}")

    print(f"V21.2 RESULT: {status}")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print()
        print(
            "V21.2 FAILED:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
