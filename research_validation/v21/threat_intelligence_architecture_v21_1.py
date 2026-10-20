
"""
QUANTUM CYBER DEFENSE ARENA
V21.1 - ADVANCED THREAT INTELLIGENCE ARCHITECTURE

Builds and validates the research architecture for V21.

Integrates:
- V19 multi-agent research release
- V20 digital twin architecture
- V20 threat scenario analysis
- V20 event streaming
- V20 validated research release

Prepares:
- V21.2 Behavioral Anomaly Detection
- V21.3 Multi-Agent Threat Correlation
- V21.4 Predictive Risk Analytics
- V21.5 Intelligence Dashboard
- V21.6 Research Release

Standard Python library only.
No external network calls or security actions.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

V19 = ROOT / "research_validation" / "v19"
V20 = ROOT / "research_validation" / "v20"
V21 = ROOT / "research_validation" / "v21"

SOURCES = {
    "v19_release": V19 / (
        "multi_agent_research_release_v19_6_results.json"
    ),
    "v20_architecture": V20 / (
        "digital_twin_architecture_v20_1_results.json"
    ),
    "v20_threat": V20 / (
        "ai_threat_scenario_v20_3_results.json"
    ),
    "v20_stream": V20 / (
        "event_streaming_v20_4_results.json"
    ),
    "v20_frames": V20 / (
        "event_streaming_v20_4_frames.json"
    ),
    "v20_release": V20 / (
        "cyber_digital_twin_release_v20_6_results.json"
    ),
}

OUTPUT_JSON = V21 / (
    "threat_intelligence_architecture_v21_1_results.json"
)

OUTPUT_MD = V21 / (
    "THREAT_INTELLIGENCE_ARCHITECTURE_V21_1.md"
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
        print("       ", detail)

    return passed


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def sha256_object(data):
    payload = json.dumps(
        data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


def read_json(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing file: {path}"
        )

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
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )


def valid_number(value):
    if isinstance(value, bool):
        return False

    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_sources():
    reports = {}

    for name, path in SOURCES.items():
        exists = path.is_file()

        check(
            f"Source available: {name}",
            exists,
            str(path),
        )

        if not exists:
            continue

        try:
            reports[name] = read_json(path)

            check(
                f"Source readable: {name}",
                True,
            )

        except (OSError, ValueError) as error:
            check(
                f"Source readable: {name}",
                False,
                str(error),
            )

    return reports


def validate_source_versions(reports):
    expected = {
        "v19_release": (
            "V19.6",
            "RESEARCH_RELEASE_PASS",
        ),
        "v20_architecture": (
            "V20.1",
            "ARCHITECTURE_PASS",
        ),
        "v20_threat": (
            "V20.3",
            "THREAT_SCENARIO_PASS",
        ),
        "v20_stream": (
            "V20.4",
            "EVENT_STREAMING_PASS",
        ),
        "v20_release": (
            "V20.6",
            "CYBER_DIGITAL_TWIN_RELEASE_PASS",
        ),
    }

    for name, (version, status) in expected.items():
        report = reports[name]

        check(
            f"{name}: version",
            report.get("version") == version,
        )

        check(
            f"{name}: successful status",
            report.get("status") == status
            and report.get("checks_failed") == 0,
        )

    frames = reports["v20_frames"]

    check(
        "V20.4 frame export version",
        frames.get("version") == "V20.4",
    )

    check(
        "V20.4 frames are simulated",
        frames.get("simulation_mode") is True
        and frames.get("is_live") is False,
    )


def validate_integrity(reports):
    model_report = reports["v20_architecture"]
    model = model_report.get("architecture_model")

    check(
        "Architecture model exists",
        isinstance(model, dict),
    )

    if not isinstance(model, dict):
        return

    actual_hash = sha256_object(model)

    check(
        "V20 architecture SHA-256 valid",
        actual_hash
        == model_report.get("architecture_sha256"),
    )

    release = reports["v20_release"]
    manifest = release.get("source_manifest", {})

    for name, source_key in (
        ("v20_architecture", "architecture"),
        ("v20_threat", "threat"),
        ("v20_stream", "streaming"),
        ("v20_frames", "frames"),
    ):
        item = manifest.get(source_key, {})
        current_hash = sha256_file(SOURCES[name])

        check(
            f"V20 release fingerprint: {source_key}",
            isinstance(item, dict)
            and item.get("sha256") == current_hash,
        )

    check(
        "V20 final release passed 80 checks",
        release.get("checks_passed") == 80
        and release.get("checks_failed") == 0,
    )


def build_intelligence_architecture(reports):
    model = reports[
        "v20_architecture"
    ]["architecture_model"]

    topology = model["architecture"]

    nodes = topology["nodes"]
    edges = topology["edges"]

    return {
        "name": "Advanced Cyber Defense Intelligence",
        "version": "V21.1",
        "mode": "research_prototype",
        "execution_type": "deterministic_architecture",
        "simulation_mode": True,
        "external_actions_enabled": False,
        "trained_ai_detector_deployed": False,
        "components": [
            {
                "id": "digital_twin",
                "name": "Cyber Digital Twin",
                "source": "V20.1-V20.4",
                "responsibility": (
                    "Maintain synthetic network state "
                    "and replayable telemetry"
                ),
            },
            {
                "id": "behavioral_analyzer",
                "name": "Behavioral Anomaly Analyzer",
                "version": "V21.2",
                "status": "planned",
                "responsibility": (
                    "Analyze node behavior across "
                    "multiple time steps"
                ),
            },
            {
                "id": "threat_correlator",
                "name": "Multi-Agent Threat Correlator",
                "version": "V21.3",
                "status": "planned",
                "responsibility": (
                    "Correlate alerts and behavioral "
                    "observations with provenance"
                ),
            },
            {
                "id": "risk_forecaster",
                "name": "Predictive Risk Analyzer",
                "version": "V21.4",
                "status": "planned",
                "responsibility": (
                    "Estimate future synthetic risk "
                    "with uncertainty and backtesting"
                ),
            },
            {
                "id": "intelligence_dashboard",
                "name": "Intelligence Dashboard",
                "version": "V21.5",
                "status": "planned",
                "responsibility": (
                    "Visualize observed and predicted "
                    "simulation data"
                ),
            },
            {
                "id": "release_validator",
                "name": "Research Release Validator",
                "version": "V21.6",
                "status": "planned",
                "responsibility": (
                    "Validate dependencies, data "
                    "integrity and research claims"
                ),
            },
        ],
        "pipeline": [
            {
                "step": 1,
                "id": "synthetic_telemetry",
                "depends_on": [],
            },
            {
                "step": 2,
                "id": "behavioral_features",
                "depends_on": [
                    "synthetic_telemetry"
                ],
            },
            {
                "step": 3,
                "id": "alert_correlation",
                "depends_on": [
                    "synthetic_telemetry",
                    "behavioral_features",
                ],
            },
            {
                "step": 4,
                "id": "risk_prediction",
                "depends_on": [
                    "behavioral_features",
                    "alert_correlation",
                ],
            },
            {
                "step": 5,
                "id": "dashboard_export",
                "depends_on": [
                    "alert_correlation",
                    "risk_prediction",
                ],
            },
            {
                "step": 6,
                "id": "research_validation",
                "depends_on": [
                    "dashboard_export",
                ],
            },
        ],
        "source_topology": {
            "nodes": len(nodes),
            "edges": len(edges),
            "node_ids": sorted(
                node["id"] for node in nodes
            ),
            "link_ids": sorted(
                edge["id"] for edge in edges
            ),
        },
        "input_contract": {
            "version": "V20.4",
            "source": (
                "event_streaming_v20_4_frames.json"
            ),
            "required_frame_fields": [
                "sequence",
                "timestamp",
                "simulation_mode",
                "network",
                "metrics",
                "alerts",
            ],
            "required_node_fields": [
                "id",
                "load",
                "risk_score",
                "risk_level",
            ],
            "required_link_fields": [
                "id",
                "source",
                "target",
                "traffic_mbps",
                "latency_ms",
            ],
        },
        "research_controls": {
            "data_is_synthetic": True,
            "human_review_required": True,
            "allow_real_network_scanning": False,
            "allow_attack_execution": False,
            "allow_automatic_blocking": False,
            "separate_observed_and_predicted_data": True,
            "measure_out_of_sample_performance": True,
            "report_model_uncertainty": True,
            "preserve_source_provenance": True,
        },
        "risk_policy": {
            "score_min": 0.0,
            "score_max": 1.0,
            "levels": {
                "normal": [0.0, 0.25],
                "low": [0.25, 0.50],
                "medium": [0.50, 0.75],
                "high": [0.75, 0.90],
                "critical": [0.90, 1.0],
            },
        },
    }


def validate_architecture(architecture, reports):
    topology = architecture["source_topology"]

    check(
        "Ten source nodes preserved",
        topology["nodes"] == 10
        and len(topology["node_ids"]) == 10
        and len(set(topology["node_ids"])) == 10,
    )

    check(
        "Eleven source links preserved",
        topology["edges"] == 11
        and len(topology["link_ids"]) == 11
        and len(set(topology["link_ids"])) == 11,
    )

    components = architecture["components"]

    ids = [item["id"] for item in components]

    check(
        "Six intelligence components configured",
        len(components) == 6
        and len(set(ids)) == 6,
    )

    check(
        "Future research components not marked active",
        all(
            item.get("status") == "planned"
            for item in components
            if item["id"] != "digital_twin"
        ),
    )

    pipeline = architecture["pipeline"]

    pipeline_ids = [
        item["id"] for item in pipeline
    ]

    check(
        "Six pipeline stages configured",
        len(pipeline) == 6
        and len(set(pipeline_ids)) == 6,
    )

    positions = {
        item["id"]: index
        for index, item in enumerate(pipeline)
    }

    check(
        "Pipeline dependencies correctly ordered",
        all(
            dependency in positions
            and positions[dependency] < index
            for index, item in enumerate(pipeline)
            for dependency in item["depends_on"]
        ),
    )

    controls = architecture["research_controls"]

    check(
        "Synthetic-only security controls enabled",
        architecture["simulation_mode"] is True
        and controls["data_is_synthetic"] is True
        and controls["allow_real_network_scanning"] is False
        and controls["allow_attack_execution"] is False
        and controls["allow_automatic_blocking"] is False,
    )

    check(
        "Human review required",
        controls["human_review_required"] is True,
    )

    check(
        "Research provenance required",
        controls["preserve_source_provenance"] is True,
    )

    check(
        "Predictive uncertainty required",
        controls["report_model_uncertainty"] is True
        and controls["measure_out_of_sample_performance"]
        is True,
    )

    check(
        "Observed and predicted values separated",
        controls["separate_observed_and_predicted_data"]
        is True,
    )

    frames_report = reports["v20_frames"]
    frames = frames_report.get("frames", [])

    check(
        "120 source frames available",
        len(frames) == 120
        and frames_report.get("frame_count") == 120,
    )

    expected_nodes = set(
        topology["node_ids"]
    )

    expected_links = set(
        topology["link_ids"]
    )

    check(
        "Every frame has correct node topology",
        all(
            {
                node.get("id")
                for node in frame.get(
                    "network", {}
                ).get("nodes", [])
            } == expected_nodes
            for frame in frames
        ),
    )

    check(
        "Every frame has correct link topology",
        all(
            {
                link.get("id")
                for link in frame.get(
                    "network", {}
                ).get("links", [])
            } == expected_links
            for frame in frames
        ),
    )

    check(
        "Frame sequences are continuous",
        [
            frame.get("sequence")
            for frame in frames
        ] == list(range(len(frames))),
    )

    check(
        "All source frames are simulated",
        all(
            frame.get("simulation_mode") is True
            for frame in frames
        ),
    )

    check(
        "Node risk scores bounded",
        all(
            valid_number(node.get("risk_score"))
            and 0 <= float(
                node["risk_score"]
            ) <= 1
            for frame in frames
            for node in frame["network"]["nodes"]
        ),
    )

    check(
        "Frame metrics contain traffic and latency",
        all(
            valid_number(
                frame.get("metrics", {}).get(
                    "total_traffic_mbps"
                )
            )
            and valid_number(
                frame.get("metrics", {}).get(
                    "mean_latency_ms"
                )
            )
            for frame in frames
        ),
    )

    check(
        "All alerts retained in source frames",
        sum(
            len(frame.get("alerts", []))
            for frame in frames
        ) == reports["v20_threat"][
            "metrics"
        ]["total_alerts"],
    )

    policy = architecture["risk_policy"]["levels"]

    check(
        "Risk policy has five levels",
        set(policy) == {
            "normal",
            "low",
            "medium",
            "high",
            "critical",
        },
    )

    ranges = list(policy.values())

    check(
        "Risk intervals cover zero to one",
        ranges[0][0] == 0.0
        and ranges[-1][1] == 1.0
        and all(
            left[1] == right[0]
            for left, right in zip(
                ranges, ranges[1:]
            )
        ),
    )


def source_manifest():
    return {
        key: {
            "path": str(
                path.relative_to(ROOT)
            ),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for key, path in SOURCES.items()
        if path.is_file()
    }


def make_markdown(result):
    topology = result["architecture"][
        "source_topology"
    ]

    return f"""# Quantum Cyber Defense Arena

## V21.1 - Advanced Threat Intelligence Architecture

**Status:** {result['status']}

**Validation checks passed:** {result['checks_passed']}

**Validation checks failed:** {result['checks_failed']}

### Existing research foundations

- V19: Deterministic multi-agent research workflow
- V20: Cyber Digital Twin and synthetic telemetry
- V20.4: Replayable network events
- V20.6: Validated research release

### Network topology

- Nodes: {topology['nodes']}
- Links: {topology['edges']}
- Source simulation frames: 120

### Intelligence research architecture

| Version | Component |
|---|---|
| V21.1 | Advanced Threat Intelligence Architecture |
| V21.2 | Behavioral Anomaly Detection |
| V21.3 | Multi-Agent Threat Correlation |
| V21.4 | Predictive Risk Analytics |
| V21.5 | Intelligence Dashboard Integration |
| V21.6 | Research Validation and Release |

### Research pipeline

1. Synthetic telemetry ingestion
2. Behavioral feature engineering
3. Threat alert correlation
4. Synthetic risk forecasting
5. Dashboard export
6. Release validation

### Research requirements

- Preserve source provenance
- Separate observations from predictions
- Quantify uncertainty
- Evaluate predictions on future unseen time steps
- Use simulation-only data
- Require human review before high-impact actions

### Limitations

V21.1 is an architectural research specification.

It does not train or deploy a new AI model.
It does not demonstrate real-world attack detection.
It does not perform network scanning or attacks.
V21.2-V21.6 are not implemented by this module.

### Next step

V21.2 - Behavioral Anomaly Detection
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V21.1 - ADVANCED THREAT INTELLIGENCE ARCHITECTURE")
    print("=" * 70)

    V21.mkdir(parents=True, exist_ok=True)

    reports = load_sources()

    architecture = None
    error = None

    if len(reports) == len(SOURCES):
        try:
            validate_source_versions(reports)
            validate_integrity(reports)

            architecture = build_intelligence_architecture(
                reports
            )

            validate_architecture(
                architecture,
                reports,
            )

        except (
            ValueError,
            TypeError,
            KeyError,
            IndexError,
            OSError,
        ) as exc:
            error = (
                f"{type(exc).__name__}: {exc}"
            )

            check(
                "Architecture evaluation completed",
                False,
                error,
            )
    else:
        check(
            "All V19/V20 source reports loaded",
            False,
            f"{len(reports)}/{len(SOURCES)}",
        )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "THREAT_INTELLIGENCE_ARCHITECTURE_PASS"
        if failed == 0 and architecture is not None
        else "THREAT_INTELLIGENCE_ARCHITECTURE_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V21.1",
        "module": "Advanced Threat Intelligence Architecture",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "live_network_monitoring": False,
        "trained_ai_detector_deployed": False,
        "external_actions_enabled": False,
        "architecture": architecture,
        "architecture_sha256": (
            sha256_object(architecture)
            if architecture is not None
            else None
        ),
        "source_artifacts": source_manifest(),
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error,
        "next_stage": (
            "V21.2 Behavioral Anomaly Detection"
        ),
    }

    write_json(
        OUTPUT_JSON,
        result,
    )

    if failed == 0 and architecture is not None:
        OUTPUT_MD.write_text(
            make_markdown(result),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V21.1 THREAT INTELLIGENCE RESULTS")
    print("=" * 70)

    if architecture is not None:
        print(
            "NETWORK NODES:",
            architecture["source_topology"][
                "nodes"
            ],
        )

        print(
            "NETWORK LINKS:",
            architecture["source_topology"][
                "edges"
            ],
        )

        print(
            "INTELLIGENCE COMPONENTS:",
            len(architecture["components"]),
        )

        print(
            "RESEARCH PIPELINE STAGES:",
            len(architecture["pipeline"]),
        )

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {OUTPUT_JSON}")

    if failed == 0:
        print(f"RESEARCH DOCUMENT: {OUTPUT_MD}")

    print(f"V21.1 RESULT: {status}")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(
            "V21.1 FATAL ERROR:",
            f"{type(exc).__name__}: {exc}",
        )
        sys.exit(1)
