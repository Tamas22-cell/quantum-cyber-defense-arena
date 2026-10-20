
"""
QUANTUM CYBER DEFENSE ARENA
V22.2 - ADAPTIVE THREAT DETECTION

Adaptive, historical-only statistical anomaly detection.

Sources:
  V22.1 architecture
  V21.5 intelligence frames
  V21.2 behavioral anomaly scores

Outputs:
  adaptive_threat_detection_v22_2_results.json
  adaptive_threat_detection_v22_2_scores.csv
  adaptive_threat_detection_v22_2_timeline.json
  ADAPTIVE_THREAT_DETECTION_V22_2.md

Research only. Synthetic data, no network actions.
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
V21 = ROOT / "research_validation" / "v21"
V22 = ROOT / "research_validation" / "v22"

ARCH_FILE = V22 / (
    "autonomous_defense_architecture_v22_1_results.json"
)
DATA_FILE = ROOT / (
    "frontend/public/v21/intelligence_data.json"
)
BASELINE_FILE = V21 / (
    "behavioral_anomaly_detection_v21_2_scores.csv"
)
BASELINE_REPORT = V21 / (
    "behavioral_anomaly_detection_v21_2_results.json"
)

OUTPUT_JSON = V22 / (
    "adaptive_threat_detection_v22_2_results.json"
)
OUTPUT_CSV = V22 / (
    "adaptive_threat_detection_v22_2_scores.csv"
)
OUTPUT_TIMELINE = V22 / (
    "adaptive_threat_detection_v22_2_timeline.json"
)
OUTPUT_MD = V22 / (
    "ADAPTIVE_THREAT_DETECTION_V22_2.md"
)

MIN_HISTORY = 12
HISTORY_WINDOW = 24
ADAPTATION_WINDOW = 24
ADAPTATION_MIN = 12
EWMA_ALPHA = 0.20
MIN_SCALE = 0.05
DEFAULT_THRESHOLD = 2.5
HOLDOUT_START = 90

CHECKS = []


def check(label, condition, detail=""):
    passed = bool(condition)
    CHECKS.append({
        "name": label,
        "passed": passed,
        "detail": str(detail),
    })
    print(f"[{'PASS' if passed else 'FAIL'}] {label}")
    if not passed and detail:
        print("       ", detail)
    return passed


def read_json(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))
    with path.open("r", encoding="utf-8-sig") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError(f"Invalid JSON: {path.name}")
    return value


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))
    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"Empty CSV: {path.name}")
    return rows


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(
            value, f, indent=2,
            ensure_ascii=False, allow_nan=False
        )


def write_csv(path, rows):
    if not rows:
        raise ValueError("No records to export")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=list(rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024), b""
        ):
            digest.update(block)
    return digest.hexdigest()


def num(value):
    if isinstance(value, bool):
        raise ValueError("Boolean numeric measurement")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite measurement")
    return result


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


def quantile(values, probability):
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Empty quantile input")
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    fraction = position - lower
    return (
        ordered[lower] * (1 - fraction)
        + ordered[upper] * fraction
    )


def validate_input(architecture, data, baseline_report):
    check(
        "V22.1 architecture passed",
        architecture.get("version") == "V22.1"
        and architecture.get("status")
        == "AUTONOMOUS_DEFENSE_ARCHITECTURE_PASS"
        and architecture.get("checks_failed") == 0,
    )

    check(
        "V21.2 baseline report passed",
        baseline_report.get("version") == "V21.2"
        and baseline_report.get("status")
        == "BEHAVIORAL_ANOMALY_PASS"
        and baseline_report.get("checks_failed") == 0,
    )

    check(
        "V21.5 synthetic export passed",
        data.get("version") == "V21.5"
        and data.get("status") == "DASHBOARD_INTEGRATION_PASS"
        and data.get("simulation_mode") is True
        and data.get("is_live") is False,
    )

    sources = architecture.get("source_manifest", {})
    check(
        "V22.1 input fingerprint valid",
        sources.get("v21_data", {}).get("sha256")
        == sha256(DATA_FILE),
    )

    model = architecture.get("architecture", {})
    policy = model.get("policy", {})

    check(
        "Real security actions disabled",
        policy.get("simulation_mode") is True
        and policy.get("real_network_changes_allowed") is False
        and policy.get("automatic_node_isolation") is False,
    )

    frames = data.get("frames", [])
    check(
        "120 ordered frames available",
        len(frames) == 120
        and [f.get("tick") for f in frames]
        == list(range(120)),
    )

    check(
        "Ten nodes per frame",
        all(len(f.get("nodes", [])) == 10 for f in frames),
    )

    check(
        "Eleven links per frame",
        all(len(f.get("links", [])) == 11 for f in frames),
    )

    if not all(item["passed"] for item in CHECKS):
        raise ValueError("Source checks failed")

    return frames


def make_features(frames):
    records = []

    for frame in frames:
        tick = frame["tick"]
        traffic = defaultdict(float)

        nodes = frame["nodes"]
        identifiers = [n["id"] for n in nodes]

        if len(set(identifiers)) != 10:
            raise ValueError(f"Duplicate node ID at {tick}")

        for link in frame["links"]:
            volume = num(link["traffic_mbps"])
            if volume < 0:
                raise ValueError("Negative traffic")
            traffic[link["source"]] += volume
            traffic[link["target"]] += volume

        for node in nodes:
            load = num(node["load"])
            risk = num(node["risk_score"])

            if not (0 <= load <= 1 and 0 <= risk <= 1):
                raise ValueError("Invalid load or risk")

            records.append({
                "tick": tick,
                "timestamp": frame["timestamp"],
                "node_id": node["id"],
                "load": load,
                "risk": risk,
                "traffic": traffic[node["id"]],
                "injected_anomaly": boolean(
                    node["injected_anomaly"]
                ),
            })

    records.sort(
        key=lambda x: (x["tick"], x["node_id"])
    )
    return records


def adaptive_feature_score(value, history):
    """
    Exponentially weighted historical baseline.
    Current value is never in the baseline.

    This is statistical detection, not trained AI.
    """
    values = history[-HISTORY_WINDOW:]

    if len(values) < MIN_HISTORY:
        return 0.0

    mean = values[0]
    variance = MIN_SCALE ** 2

    for historical in values[1:]:
        difference = historical - mean
        mean += EWMA_ALPHA * difference
        variance = (
            (1 - EWMA_ALPHA) * variance
            + EWMA_ALPHA * difference ** 2
        )

    scale = max(math.sqrt(variance), MIN_SCALE)
    return max(0.0, (value - mean) / scale)


def detect(records):
    """
    All baselines and thresholds use earlier ticks.

    Adaptation uses the previous scores for
    the SAME node; the current score is not
    included in its own threshold.
    """
    histories = defaultdict(
        lambda: {
            "load": [],
            "risk": [],
            "traffic": [],
            "scores": [],
        }
    )

    output = []

    for record in records:
        h = histories[record["node_id"]]
        ready = len(h["load"]) >= MIN_HISTORY

        if ready:
            scores = {
                field: adaptive_feature_score(
                    record[field], h[field]
                )
                for field in ("load", "risk", "traffic")
            }
            anomaly_score = max(scores.values())
        else:
            scores = {
                "load": 0.0,
                "risk": 0.0,
                "traffic": 0.0,
            }
            anomaly_score = 0.0

        recent_scores = h["scores"][
            -ADAPTATION_WINDOW:
        ]

        if len(recent_scores) >= ADAPTATION_MIN:
            threshold = max(
                2.0,
                min(
                    4.5,
                    quantile(recent_scores, 0.90)
                )
            )
        else:
            threshold = DEFAULT_THRESHOLD

        detected = (
            ready and anomaly_score >= threshold
        )

        output.append({
            "tick": record["tick"],
            "timestamp": record["timestamp"],
            "node_id": record["node_id"],
            "load": rnd(record["load"]),
            "risk_score": rnd(record["risk"]),
            "incident_traffic_mbps": rnd(
                record["traffic"]
            ),
            "load_z": rnd(scores["load"]),
            "risk_z": rnd(scores["risk"]),
            "traffic_z": rnd(scores["traffic"]),
            "anomaly_score": rnd(anomaly_score),
            "adaptive_threshold": rnd(threshold),
            "baseline_ready": ready,
            "detected_anomaly": detected,
            "injected_anomaly": record[
                "injected_anomaly"
            ],
            "detector": "adaptive_ewma_zscore",
        })

        for field in ("load", "risk", "traffic"):
            h[field].append(record[field])

        if ready:
            h["scores"].append(anomaly_score)

    return output


def map_baseline(rows):
    indexed = {}

    for row in rows:
        key = (
            int(row["tick"]),
            row["node_id"],
        )

        if key in indexed:
            raise ValueError(
                f"Duplicate baseline observation: {key}"
            )

        indexed[key] = {
            "ready": boolean(row["baseline_ready"]),
            "detected": boolean(row["detected_anomaly"]),
            "injected": boolean(row["injected_anomaly"]),
        }

    return indexed


def evaluate(rows, reference, start_tick):
    """
    Compare two detectors on the SAME eligible
    synthetic node observations.

    Injected markers are simulator metadata,
    not independently verified attacks.
    """
    eligible = [
        row for row in rows
        if row["tick"] >= start_tick
        and row["baseline_ready"]
        and reference[
            (row["tick"], row["node_id"])
        ]["ready"]
    ]

    def confusion(use_adaptive):
        tp = fp = fn = tn = 0

        for row in eligible:
            old = reference[
                (row["tick"], row["node_id"])
            ]
            predicted = (
                row["detected_anomaly"]
                if use_adaptive
                else old["detected"]
            )
            label = row["injected_anomaly"]

            if predicted and label:
                tp += 1
            elif predicted and not label:
                fp += 1
            elif not predicted and label:
                fn += 1
            else:
                tn += 1

        return {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "detections": tp + fp,
            "precision": (
                rnd(tp / (tp + fp))
                if tp + fp else None
            ),
            "recall": (
                rnd(tp / (tp + fn))
                if tp + fn else None
            ),
        }

    return {
        "start_tick": start_tick,
        "eligible_observations": len(eligible),
        "adaptive_detector": confusion(True),
        "v21_baseline_detector": confusion(False),
        "label_type": "synthetic_node_injection_marker",
        "real_attack_labels": False,
        "thresholds_selected_independently": False,
    }


def build_timeline(rows):
    by_tick = defaultdict(list)
    for row in rows:
        by_tick[row["tick"]].append(row)

    return [
        {
            "tick": tick,
            "timestamp": by_tick[tick][0]["timestamp"],
            "evaluated_nodes": len(by_tick[tick]),
            "detections": sum(
                row["detected_anomaly"]
                for row in by_tick[tick]
            ),
            "detected_nodes": [
                row["node_id"]
                for row in by_tick[tick]
                if row["detected_anomaly"]
            ],
            "max_adaptive_score": max(
                row["anomaly_score"]
                for row in by_tick[tick]
            ),
            "mean_adaptive_threshold": rnd(
                statistics.mean(
                    row["adaptive_threshold"]
                    for row in by_tick[tick]
                )
            ),
            "injected_node_markers": sum(
                row["injected_anomaly"]
                for row in by_tick[tick]
            ),
        }
        for tick in range(120)
    ]


def validate_results(rows, reference, timeline, evaluation):
    keys = [
        (row["tick"], row["node_id"])
        for row in rows
    ]

    check(
        "1200 node observations generated",
        len(rows) == 1200,
    )
    check(
        "Every node/tick identity unique",
        len(set(keys)) == len(keys),
    )
    check(
        "Baseline covers identical node/tick keys",
        set(keys) == set(reference),
    )
    check(
        "Injected labels agree with V21.2",
        all(
            row["injected_anomaly"]
            == reference[
                (row["tick"], row["node_id"])
            ]["injected"]
            for row in rows
        ),
    )
    check(
        "Adaptive scores finite and nonnegative",
        all(
            math.isfinite(row["anomaly_score"])
            and row["anomaly_score"] >= 0
            for row in rows
        ),
    )
    check(
        "Adaptive thresholds bounded",
        all(
            2.0 <= row["adaptive_threshold"] <= 4.5
            for row in rows
        ),
    )
    check(
        "No detections before baseline warmup",
        all(
            not row["detected_anomaly"]
            for row in rows
            if row["tick"] < MIN_HISTORY
        ),
    )
    check(
        "Every detection satisfies threshold",
        all(
            row["detected_anomaly"] == (
                row["baseline_ready"]
                and row["anomaly_score"]
                >= row["adaptive_threshold"]
            )
            for row in rows
        ),
    )
    check(
        "Timeline contains all 120 ticks",
        len(timeline) == 120
        and [
            row["tick"] for row in timeline
        ] == list(range(120)),
    )
    check(
        "Timeline detection totals consistent",
        sum(row["detections"] for row in timeline)
        == sum(row["detected_anomaly"] for row in rows),
    )
    check(
        "Holdout comparison has 300 node observations",
        evaluation["eligible_observations"] == 300,
    )
    check(
        "Confusion matrices sum to holdout size",
        all(
            sum(
                result[key]
                for key in ("tp", "fp", "fn", "tn")
            ) == evaluation["eligible_observations"]
            for result in (
                evaluation["adaptive_detector"],
                evaluation["v21_baseline_detector"],
            )
        ),
    )


def document(result):
    evaluation = result["evaluation"]

    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V22.2 - Adaptive Threat Detection",
        "",
        f"Status: {result['status']}",
        f"Checks passed: {result['checks_passed']}",
        f"Checks failed: {result['checks_failed']}",
        "",
        "### Method",
        "",
        "- Historical EWMA baseline",
        "- Previous observations only",
        f"- Baseline window: {HISTORY_WINDOW}",
        f"- Minimum history: {MIN_HISTORY}",
        "- Adapted threshold from previous scores",
        "- Three features: load, risk, incident traffic",
        "",
        "### Synthetic holdout comparison",
        "",
        "| Metric | Adaptive V22.2 | V21.2 baseline |",
        "|---|---:|---:|",
    ]

    adaptive = evaluation["adaptive_detector"]
    baseline = evaluation["v21_baseline_detector"]

    for label, key in (
        ("Detections", "detections"),
        ("TP", "tp"),
        ("FP", "fp"),
        ("FN", "fn"),
        ("TN", "tn"),
        ("Precision", "precision"),
        ("Recall", "recall"),
    ):
        lines.append(
            f"| {label} | {adaptive[key]} | {baseline[key]} |"
        )

    lines += [
        "",
        "### Research limitations",
        "",
        "- Dataset is entirely synthetic.",
        "- Source risk scores are simulated.",
        "- Synthetic injection markers are not real attack labels.",
        "- Adaptive and baseline methods use related source features.",
        "- Thresholds were researcher-selected, not independently tuned.",
        "- One 120-tick run is not sufficient for generalization claims.",
        "- No production detection accuracy is established.",
        "- The detector cannot change a real network.",
        "",
        "### Next stage",
        "",
        "V22.3 - Multi-Agent Defense Decision Engine",
        "",
    ]

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V22.2 - ADAPTIVE THREAT DETECTION")
    print("=" * 70)

    architecture = read_json(ARCH_FILE)
    data = read_json(DATA_FILE)
    baseline_report = read_json(BASELINE_REPORT)
    baseline_csv = read_csv(BASELINE_FILE)

    frames = validate_input(
        architecture, data, baseline_report
    )

    features = make_features(frames)
    rows = detect(features)
    reference = map_baseline(baseline_csv)

    timeline = build_timeline(rows)

    evaluation = evaluate(
        rows, reference, HOLDOUT_START
    )

    validate_results(
        rows, reference, timeline, evaluation
    )

    check(
        "Detection is reproducible",
        rows == detect(features),
    )

    half_features = [
        item for item in features
        if item["tick"] < 60
    ]

    half_scores = detect(half_features)

    check(
        "No future-data leakage in first 60 ticks",
        rows[:len(half_scores)] == half_scores,
    )

    counts = Counter(
        row["node_id"]
        for row in rows
        if row["detected_anomaly"]
    )

    metrics = {
        "simulation_ticks": 120,
        "network_nodes": 10,
        "node_observations": len(rows),
        "adaptive_detections": sum(
            row["detected_anomaly"] for row in rows
        ),
        "affected_nodes": len(counts),
        "detections_by_node": dict(counts),
        "maximum_anomaly_score": max(
            row["anomaly_score"] for row in rows
        ),
        "detector": "adaptive_ewma_zscore",
        "trained_ai_model_used": False,
        "live_security_actions": False,
    }

    passed = sum(x["passed"] for x in CHECKS)
    failed = len(CHECKS) - passed

    status = (
        "ADAPTIVE_THREAT_DETECTION_PASS"
        if failed == 0
        else "ADAPTIVE_THREAT_DETECTION_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V22.2",
        "module": "Adaptive Threat Detection Engine",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "external_actions_enabled": False,
        "trained_ai_model_used": False,
        "configuration": {
            "minimum_history": MIN_HISTORY,
            "history_window": HISTORY_WINDOW,
            "adaptation_window": ADAPTATION_WINDOW,
            "adaptation_minimum": ADAPTATION_MIN,
            "ewma_alpha": EWMA_ALPHA,
            "holdout_start": HOLDOUT_START,
        },
        "metrics": metrics,
        "evaluation": evaluation,
        "source_sha256": {
            "architecture": sha256(ARCH_FILE),
            "data": sha256(DATA_FILE),
            "baseline_report": sha256(BASELINE_REPORT),
            "baseline_scores": sha256(BASELINE_FILE),
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "next_stage": (
            "V22.3 Multi-Agent Defense Decision Engine"
        ),
    }

    write_json(OUTPUT_JSON, result)

    if failed == 0:
        write_csv(OUTPUT_CSV, rows)

        write_json(
            OUTPUT_TIMELINE,
            {
                "version": "V22.2",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "ticks": 120,
                "timeline": timeline,
            },
        )

        OUTPUT_MD.write_text(
            document(result),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V22.2 ADAPTIVE DETECTION RESULTS")
    print("=" * 70)
    print("NETWORK NODES:", metrics["network_nodes"])
    print("SIMULATION TICKS:", metrics["simulation_ticks"])
    print("NODE OBSERVATIONS:", metrics["node_observations"])
    print("ADAPTIVE DETECTIONS:", metrics["adaptive_detections"])
    print("AFFECTED NODES:", metrics["affected_nodes"])
    print("HOLDOUT OBSERVATIONS:",
          evaluation["eligible_observations"])
    print("CHECKS PASSED:", passed)
    print("CHECKS FAILED:", failed)
    print("JSON REPORT:", OUTPUT_JSON)
    print("V22.2 RESULT:", status)
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(
            "V22.2 FAILED:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
