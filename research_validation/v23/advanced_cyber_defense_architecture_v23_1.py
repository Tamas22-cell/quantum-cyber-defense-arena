
"""
QUANTUM CYBER DEFENSE ARENA
V23.1 - ADVANCED CYBER DEFENSE ARCHITECTURE

Final development phase: V23.1 to V23.6.

Inputs:
  V22.6 validated research release
  V22.5 simulated defense dashboard data
  V22.4 defense strategy research results

Outputs:
  research_validation/v23/
    advanced_cyber_defense_architecture_v23_1_results.json
    ADVANCED_CYBER_DEFENSE_ARCHITECTURE_V23_1.md

Read-only research architecture.
No live network activity.
No real defensive or offensive actions.
Python standard library only.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V22 = ROOT / "research_validation" / "v22"
V23 = ROOT / "research_validation" / "v23"
PUBLIC = ROOT / "frontend" / "public" / "v22"

SOURCES = {
    "release": V22 / (
        "autonomous_defense_release_v22_6_results.json"
    ),
    "architecture": V22 / (
        "autonomous_defense_architecture_v22_1_results.json"
    ),
    "detector": V22 / (
        "adaptive_threat_detection_v22_2_results.json"
    ),
    "decision": V22 / (
        "multi_agent_defense_decision_v22_3_results.json"
    ),
    "strategy": V22 / (
        "defense_strategy_simulation_v22_4_results.json"
    ),
    "dashboard": V22 / (
        "autonomous_defense_dashboard_v22_5_results.json"
    ),
    "frames": PUBLIC / "defense_data.json",
}

OUTPUT_JSON = V23 / (
    "advanced_cyber_defense_architecture_v23_1_results.json"
)
OUTPUT_MD = V23 / (
    "ADVANCED_CYBER_DEFENSE_ARCHITECTURE_V23_1.md"
)

CHECKS = []

EXPECTED = {
    "release": (
        "V22.6",
        "AUTONOMOUS_DEFENSE_RELEASE_PASS",
    ),
    "architecture": (
        "V22.1",
        "AUTONOMOUS_DEFENSE_ARCHITECTURE_PASS",
    ),
    "detector": (
        "V22.2",
        "ADAPTIVE_THREAT_DETECTION_PASS",
    ),
    "decision": (
        "V22.3",
        "DEFENSE_DECISION_PASS",
    ),
    "strategy": (
        "V22.4",
        "DEFENSE_STRATEGY_SIMULATION_PASS",
    ),
    "dashboard": (
        "V22.5",
        "DEFENSE_DASHBOARD_PASS",
    ),
    "frames": (
        "V22.5",
        "DEFENSE_DASHBOARD_PASS",
    ),
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
        print("      ", detail)
    return passed


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid JSON: {path.name}")
    return data


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(
            data, f, indent=2,
            ensure_ascii=False, allow_nan=False
        )


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024), b""
        ):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_object(data):
    raw = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def finite_unit(value):
    if isinstance(value, bool):
        return False
    try:
        value = float(value)
        return math.isfinite(value) and 0 <= value <= 1
    except (ValueError, TypeError):
        return False


def load_sources():
    reports = {}
    for name, path in SOURCES.items():
        exists = check(
            f"Source exists: {name}",
            path.is_file(),
            str(path),
        )
        if not exists:
            continue
        try:
            reports[name] = read_json(path)
            check(f"Source readable: {name}", True)
        except (OSError, ValueError) as error:
            check(
                f"Source readable: {name}",
                False,
                str(error),
            )
    return reports


def validate_sources(reports):
    for name, (version, status) in EXPECTED.items():
        item = reports[name]
        check(
            f"{name}: version",
            item.get("version") == version,
        )
        check(
            f"{name}: PASS status",
            item.get("status") == status,
        )
        check(
            f"{name}: synthetic only",
            item.get("simulation_mode") is True,
        )

    release = reports["release"]
    prior_checks = release.get("checks", [])

    check(
        "V22.6 validated with zero failures",
        release.get("checks_failed") == 0
        and release.get("checks_passed", 0) > 0,
    )

    check(
        "V22.6 validation records consistent",
        isinstance(prior_checks, list)
        and len(prior_checks) == release.get("checks_passed")
        and all(
            item.get("passed") is True
            for item in prior_checks
        ),
    )

    manifest = release.get("source_manifest", {})

    for name, manifest_key in (
        ("architecture", "architecture"),
        ("detector", "detector"),
        ("decision", "decision"),
        ("strategy", "strategy"),
        ("dashboard", "dashboard"),
        ("frames", "dashboard_data"),
    ):
        recorded = manifest.get(manifest_key, {})
        check(
            f"Release SHA-256: {name}",
            isinstance(recorded, dict)
            and recorded.get("sha256")
            == sha256_file(SOURCES[name]),
        )

    metrics = release.get("metrics", {})
    check(
        "V22 network topology verified",
        metrics.get("network_nodes") == 10
        and metrics.get("network_links") == 11,
    )
    check(
        "V22 simulation duration verified",
        metrics.get("simulation_ticks") == 120,
    )
    check(
        "V22 decision records verified",
        metrics.get("defense_decisions") == 1200
        and metrics.get("strategy_simulations") == 1200,
    )
    check(
        "V22 performed no real actions",
        metrics.get("real_actions_executed") == 0,
    )

    frames = reports["frames"].get("frames", [])
    check(
        "Dashboard has 120 ordered frames",
        len(frames) == 120
        and [f.get("tick") for f in frames]
        == list(range(120)),
    )
    check(
        "Network topology stable across frames",
        all(
            len(f.get("nodes", [])) == 10
            and len(f.get("links", [])) == 11
            for f in frames
        ),
    )
    check(
        "Simulated risk values bounded",
        all(
            finite_unit(f.get("original_risk"))
            and finite_unit(f.get("residual_risk"))
            and finite_unit(f.get("service_impact"))
            for f in frames
        ),
    )
    check(
        "No real dashboard actions",
        all(
            f.get("real_actions_executed") == 0
            for f in frames
        ),
    )
    check(
        "All decision records represented",
        sum(
            len(f.get("decisions", []))
            for f in frames
        ) == 1200,
    )

    return frames


def build_architecture(reports):
    source_metrics = reports["release"]["metrics"]

    components = [
        {
            "id": "telemetry",
            "version": "V22.5",
            "status": "source_available",
            "role": "Validated synthetic network telemetry",
        },
        {
            "id": "threat_fusion",
            "version": "V23.2",
            "status": "planned",
            "role": (
                "Fuse detections, alerts and risk "
                "with timestamp and provenance"
            ),
        },
        {
            "id": "policy_optimizer",
            "version": "V23.3",
            "status": "planned",
            "role": (
                "Compare simulated defense policies "
                "under risk and service constraints"
            ),
        },
        {
            "id": "orchestration",
            "version": "V23.4",
            "status": "planned",
            "role": (
                "Coordinate simulated multi-role "
                "decision and approval workflows"
            ),
        },
        {
            "id": "dashboard",
            "version": "V23.5",
            "status": "planned",
            "role": (
                "Visualize fusion, strategy comparisons "
                "and replayable simulated decisions"
            ),
        },
        {
            "id": "release",
            "version": "V23.6",
            "status": "planned",
            "role": (
                "Validate artifacts, evidence, "
                "reproducibility and limitations"
            ),
        },
    ]

    pipeline = [
        {"id": "ingest", "depends_on": []},
        {"id": "fuse", "depends_on": ["ingest"]},
        {"id": "optimize", "depends_on": ["fuse"]},
        {"id": "orchestrate", "depends_on": ["optimize"]},
        {"id": "visualize", "depends_on": ["orchestrate"]},
        {"id": "validate", "depends_on": ["visualize"]},
    ]

    return {
        "version": "V23.1",
        "name": "Advanced Cyber Defense Research Architecture",
        "status": "architecture_specification",
        "source_release": "V22.6",
        "simulation_mode": True,
        "live_operations": False,
        "trained_ai_model_deployed": False,
        "network": {
            "nodes": source_metrics["network_nodes"],
            "links": source_metrics["network_links"],
            "ticks": source_metrics["simulation_ticks"],
            "decisions": source_metrics["defense_decisions"],
        },
        "components": components,
        "pipeline": pipeline,
        "actions": [
            "observe",
            "increase_monitoring",
            "rate_limit",
            "isolate_node",
            "request_review",
        ],
        "safety_policy": {
            "real_network_access": False,
            "real_firewall_changes": False,
            "real_node_isolation": False,
            "automated_disruptive_actions": False,
            "approval_for_disruptive_proposals": True,
            "decision_audit": True,
            "simulation_rollback": True,
        },
        "evaluation_policy": {
            "chronological_holdout": True,
            "compare_baselines": True,
            "measure_service_impact": True,
            "record_uncertainty": True,
            "prevent_future_data_leakage": True,
            "separate_synthetic_markers_from_real_labels": True,
            "preserve_input_sha256": True,
        },
        "limitations": [
            "Synthetic network telemetry only.",
            "No verified real cyberattack labels.",
            "No actual autonomous network defense.",
            "Strategy effects are model assumptions.",
            "Future V23 modules are not yet implemented.",
        ],
    }


def validate_architecture(model):
    components = model["components"]
    ids = [c["id"] for c in components]
    pipeline = model["pipeline"]
    positions = {
        stage["id"]: i
        for i, stage in enumerate(pipeline)
    }

    check(
        "Six research components",
        len(components) == 6
        and len(set(ids)) == 6,
    )
    check(
        "Five future components planned",
        sum(
            c["status"] == "planned"
            for c in components
        ) == 5,
    )
    check(
        "Six unique processing stages",
        len(pipeline) == len(positions) == 6,
    )
    check(
        "Pipeline dependency order valid",
        all(
            dependency in positions
            and positions[dependency] < i
            for i, stage in enumerate(pipeline)
            for dependency in stage["depends_on"]
        ),
    )
    check(
        "Five defense action types",
        len(model["actions"]) == 5
        and len(set(model["actions"])) == 5,
    )

    safety = model["safety_policy"]
    check(
        "All real security operations disabled",
        all(
            safety[key] is False
            for key in (
                "real_network_access",
                "real_firewall_changes",
                "real_node_isolation",
                "automated_disruptive_actions",
            )
        ),
    )
    check(
        "Human approval required",
        safety["approval_for_disruptive_proposals"] is True,
    )
    check(
        "Decision audit enabled",
        safety["decision_audit"] is True,
    )
    check(
        "Simulation rollback specified",
        safety["simulation_rollback"] is True,
    )

    evaluation = model["evaluation_policy"]
    check(
        "All scientific controls specified",
        all(evaluation.values()),
    )
    check(
        "Source network size preserved",
        model["network"]["nodes"] == 10
        and model["network"]["links"] == 11,
    )
    check(
        "Source research sample counts preserved",
        model["network"]["ticks"] == 120
        and model["network"]["decisions"] == 1200,
    )
    check(
        "No trained AI model claimed",
        model["trained_ai_model_deployed"] is False,
    )


def markdown_document(result):
    model = result["architecture"]

    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V23.1 - Advanced Cyber Defense Architecture",
        "",
        f"**Status:** {result['status']}",
        f"**Checks passed:** {result['checks_passed']}",
        f"**Checks failed:** {result['checks_failed']}",
        "",
        "### Research foundation",
        "",
        "- V22.6 validated source release",
        "- 10 synthetic nodes and 11 links",
        "- 120 historical simulation ticks",
        "- 1200 simulated defense decisions",
        "",
        "### V23 roadmap",
        "",
        "| Version | Research module | Status |",
        "|---|---|---|",
        "| V23.1 | Architecture | Complete |",
        "| V23.2 | Intelligent Threat Fusion | Planned |",
        "| V23.3 | Adaptive Defense Policy Optimization | Planned |",
        "| V23.4 | Multi-Agent Orchestration Simulation | Planned |",
        "| V23.5 | Advanced Defense Dashboard | Planned |",
        "| V23.6 | Final Validation & Release | Planned |",
        "",
        "### Security boundaries",
        "",
        "- No real network access",
        "- No real firewall changes",
        "- No real isolation or blocking",
        "- Approval required for disruptive proposals",
        "- Auditable simulated decisions",
        "",
        "### Evaluation requirements",
        "",
    ]

    for key, value in model["evaluation_policy"].items():
        lines.append(f"- {key}: {value}")

    lines += [
        "",
        "### Scientific limitations",
        "",
        "This is a research architecture specification.",
        "The V23.2-V23.6 modules are not implemented here.",
        "No production security effectiveness is demonstrated.",
        "All existing strategy outcomes are hypothetical.",
        "",
        "### Next stage",
        "",
        "V23.2 - Intelligent Threat Fusion Engine",
        "",
    ]
    return "\n".join(lines)


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V23.1 - ADVANCED CYBER DEFENSE ARCHITECTURE")
    print("=" * 70)

    V23.mkdir(parents=True, exist_ok=True)

    reports = load_sources()
    architecture = None
    error = None

    if len(reports) == len(SOURCES):
        try:
            validate_sources(reports)

            if not all(item["passed"] for item in CHECKS):
                raise ValueError(
                    "V22 source validation failed"
                )

            architecture = build_architecture(reports)
            validate_architecture(architecture)

            check(
                "Architecture deterministic",
                architecture == build_architecture(reports),
            )

        except (
            OSError, ValueError, TypeError,
            KeyError, IndexError
        ) as exc:
            error = f"{type(exc).__name__}: {exc}"
            check("Architecture evaluation completed", False, error)
    else:
        error = f"Loaded {len(reports)}/{len(SOURCES)} sources"
        check("All research sources loaded", False, error)

    passed = sum(c["passed"] for c in CHECKS)
    failed = len(CHECKS) - passed

    status = (
        "ADVANCED_CYBER_DEFENSE_ARCHITECTURE_PASS"
        if failed == 0 and architecture is not None
        else "ADVANCED_CYBER_DEFENSE_ARCHITECTURE_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V23.1",
        "status": status,
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "simulation_mode": True,
        "real_network_actions_enabled": False,
        "architecture": architecture,
        "architecture_sha256": (
            sha256_object(architecture)
            if architecture is not None else None
        ),
        "source_manifest": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
            for name, path in SOURCES.items()
            if path.is_file()
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error,
        "next_stage": "V23.2 Intelligent Threat Fusion",
    }

    write_json(OUTPUT_JSON, result)

    if status == "ADVANCED_CYBER_DEFENSE_ARCHITECTURE_PASS":
        OUTPUT_MD.write_text(
            markdown_document(result),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V23.1 ADVANCED CYBER DEFENSE RESULTS")
    print("=" * 70)

    if architecture is not None:
        print("NETWORK NODES:", architecture["network"]["nodes"])
        print("NETWORK LINKS:", architecture["network"]["links"])
        print("SIMULATION TICKS:", architecture["network"]["ticks"])
        print("DEFENSE DECISIONS:", architecture["network"]["decisions"])
        print("RESEARCH COMPONENTS:", len(architecture["components"]))

    print("CHECKS PASSED:", passed)
    print("CHECKS FAILED:", failed)
    print("JSON REPORT:", OUTPUT_JSON)
    if error:
        print("ERROR:", error)
    print("V23.1 RESULT:", status)
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(
            "V23.1 FAILED:",
            f"{type(exc).__name__}: {exc}",
        )
        sys.exit(1)
