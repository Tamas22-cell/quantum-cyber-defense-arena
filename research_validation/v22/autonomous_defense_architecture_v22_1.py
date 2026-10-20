
"""
QUANTUM CYBER DEFENSE ARENA
V22.1 - AUTONOMOUS DEFENSE ARCHITECTURE

Research architecture for simulated defense decisions.

Sources:
- V21.6 validated research release
- V21.5 intelligence dashboard data
- V21.3 threat correlation report
- V21.4 predictive risk report

Outputs:
- autonomous_defense_architecture_v22_1_results.json
- AUTONOMOUS_DEFENSE_ARCHITECTURE_V22_1.md

No live network access.
No firewall changes.
No real security actions.
No trained AI model in this architectural module.

Standard Python library only.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys

from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V21 = ROOT / "research_validation" / "v21"
V22 = ROOT / "research_validation" / "v22"
PUBLIC = ROOT / "frontend" / "public" / "v21"

SOURCES = {
    "v21_release": V21 / (
        "advanced_threat_intelligence_release_v21_6_results.json"
    ),
    "v21_dashboard": V21 / (
        "intelligence_dashboard_integration_v21_5_results.json"
    ),
    "v21_correlation": V21 / (
        "multi_agent_threat_correlation_v21_3_results.json"
    ),
    "v21_prediction": V21 / (
        "predictive_risk_analytics_v21_4_results.json"
    ),
    "v21_data": PUBLIC / "intelligence_data.json",
}

OUTPUT_JSON = V22 / (
    "autonomous_defense_architecture_v22_1_results.json"
)

OUTPUT_MD = V22 / (
    "AUTONOMOUS_DEFENSE_ARCHITECTURE_V22_1.md"
)

CHECKS = []


def check(name, condition, detail=""):
    passed = bool(condition)

    CHECKS.append({
        "name": name,
        "passed": passed,
        "detail": str(detail),
    })

    print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if detail and not passed:
        print("       " + str(detail))

    return passed


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def sha256_object(data):
    raw = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        data = json.load(handle)

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
    ) as handle:
        json.dump(
            data,
            handle,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


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


def finite_number(value):
    if isinstance(value, bool):
        return False

    try:
        return math.isfinite(float(value))

    except (TypeError, ValueError):
        return False


def validate_sources(reports):
    expected = {
        "v21_release": (
            "V21.6",
            "ADVANCED_THREAT_INTELLIGENCE_RELEASE_PASS",
        ),
        "v21_dashboard": (
            "V21.5",
            "DASHBOARD_INTEGRATION_PASS",
        ),
        "v21_correlation": (
            "V21.3",
            "THREAT_CORRELATION_PASS",
        ),
        "v21_prediction": (
            "V21.4",
            "PREDICTIVE_RISK_PASS",
        ),
        "v21_data": (
            "V21.5",
            "DASHBOARD_INTEGRATION_PASS",
        ),
    }

    for name, (version, status) in expected.items():
        report = reports[name]

        check(
            f"{name}: correct version",
            report.get("version") == version,
        )

        check(
            f"{name}: validated status",
            report.get("status") == status,
        )

        check(
            f"{name}: simulation only",
            report.get("simulation_mode") is True,
        )

    release = reports["v21_release"]

    check(
        "V21 research validation had zero failures",
        release.get("checks_failed") == 0
        and release.get("checks_passed", 0) > 0,
    )

    recorded_checks = release.get("checks", [])

    check(
        "V21 release check records consistent",
        isinstance(recorded_checks, list)
        and len(recorded_checks)
        == release.get("checks_passed")
        and all(
            isinstance(item, dict)
            and item.get("passed") is True
            for item in recorded_checks
        ),
    )

    manifest = release.get("source_manifest", {})

    for name, manifest_key in (
        ("v21_dashboard", "dashboard"),
        ("v21_correlation", "correlation"),
        ("v21_prediction", "prediction"),
        ("v21_data", "dashboard_data"),
    ):
        entry = manifest.get(manifest_key, {})

        check(
            f"V21 release SHA-256: {manifest_key}",
            isinstance(entry, dict)
            and entry.get("sha256")
            == sha256_file(SOURCES[name]),
        )

    metrics = release.get("metrics", {})

    check(
        "V21 release network topology",
        metrics.get("network_nodes") == 10
        and metrics.get("network_links") == 11,
    )

    check(
        "V21 release has 120 simulation ticks",
        metrics.get("simulation_ticks") == 120,
    )

    frames = reports["v21_data"].get("frames", [])

    check(
        "V21 dashboard contains 120 frames",
        len(frames) == 120,
    )

    check(
        "V21 frame sequence continuous",
        [
            frame.get("tick")
            for frame in frames
        ] == list(range(120)),
    )

    check(
        "V21 topology preserved in every frame",
        all(
            len(frame.get("nodes", [])) == 10
            and len(frame.get("links", [])) == 11
            for frame in frames
        ),
    )

    check(
        "V21 frame risk values finite",
        all(
            finite_number(
                frame.get("observed_risk")
            )
            and 0 <= float(
                frame["observed_risk"]
            ) <= 1
            for frame in frames
        ),
    )

    check(
        "V21 metrics agree with dashboard data",
        metrics.get("behavioral_detections")
        == sum(
            frame["behavioral_detections"]
            for frame in frames
        )
        and metrics.get("forecasts_available")
        == sum(
            frame["predicted_risk"] is not None
            for frame in frames
        ),
    )

    check(
        "V21 predictive evaluation exists",
        reports["v21_prediction"].get(
            "evaluation", {}
        ).get("holdout_observations") == 30,
    )


def build_architecture(reports):
    release_metrics = reports[
        "v21_release"
    ]["metrics"]

    return {
        "project": "Quantum Cyber Defense Arena",
        "version": "V22.1",
        "name": "Autonomous Defense Research Architecture",
        "research_mode": "simulation_only",
        "implementation_status": "architecture_specification",
        "source_release": "V21.6",
        "network": {
            "nodes": release_metrics["network_nodes"],
            "links": release_metrics["network_links"],
            "historical_ticks": release_metrics[
                "simulation_ticks"
            ],
        },
        "components": [
            {
                "id": "telemetry_adapter",
                "name": "Telemetry Adapter",
                "source": "V21.5",
                "status": "specified",
                "purpose": (
                    "Read validated synthetic network "
                    "events without modifying sources"
                ),
            },
            {
                "id": "adaptive_detector",
                "name": "Adaptive Threat Detection",
                "version": "V22.2",
                "status": "planned",
                "purpose": (
                    "Compare adaptive detection policies "
                    "against a fixed statistical baseline"
                ),
            },
            {
                "id": "decision_agent",
                "name": "Defense Decision Engine",
                "version": "V22.3",
                "status": "planned",
                "purpose": (
                    "Generate candidate simulated "
                    "responses with auditable reasoning"
                ),
            },
            {
                "id": "strategy_simulator",
                "name": "Defense Strategy Simulator",
                "version": "V22.4",
                "status": "planned",
                "purpose": (
                    "Evaluate proposed actions in a "
                    "synthetic network environment"
                ),
            },
            {
                "id": "defense_dashboard",
                "name": "Autonomous Defense Dashboard",
                "version": "V22.5",
                "status": "planned",
                "purpose": (
                    "Visualize simulated recommendations, "
                    "risks, outcomes and uncertainty"
                ),
            },
            {
                "id": "release_validator",
                "name": "Research Release Validator",
                "version": "V22.6",
                "status": "planned",
                "purpose": (
                    "Check reproducibility, integrity "
                    "and research evidence"
                ),
            },
        ],
        "pipeline": [
            {
                "id": "telemetry_ingestion",
                "depends_on": [],
            },
            {
                "id": "adaptive_detection",
                "depends_on": [
                    "telemetry_ingestion"
                ],
            },
            {
                "id": "candidate_decisions",
                "depends_on": [
                    "adaptive_detection"
                ],
            },
            {
                "id": "strategy_simulation",
                "depends_on": [
                    "candidate_decisions"
                ],
            },
            {
                "id": "dashboard_export",
                "depends_on": [
                    "strategy_simulation"
                ],
            },
            {
                "id": "research_validation",
                "depends_on": [
                    "dashboard_export"
                ],
            },
        ],
        "defense_actions": [
            {
                "id": "observe",
                "label": "Continue monitoring",
                "implementation": "simulated",
                "requires_approval": False,
            },
            {
                "id": "increase_monitoring",
                "label": "Increase synthetic monitoring",
                "implementation": "simulated",
                "requires_approval": False,
            },
            {
                "id": "rate_limit",
                "label": "Simulate traffic rate limiting",
                "implementation": "simulated",
                "requires_approval": True,
            },
            {
                "id": "isolate_node",
                "label": "Simulate node isolation",
                "implementation": "simulated",
                "requires_approval": True,
            },
            {
                "id": "request_review",
                "label": "Request human security review",
                "implementation": "simulated",
                "requires_approval": True,
            },
        ],
        "policy": {
            "risk_range": [0.0, 1.0],
            "risk_bands": {
                "normal": [0.0, 0.25],
                "low": [0.25, 0.50],
                "medium": [0.50, 0.75],
                "high": [0.75, 0.90],
                "critical": [0.90, 1.0],
            },
            "simulation_mode": True,
            "real_network_changes_allowed": False,
            "live_firewall_access": False,
            "automatic_node_isolation": False,
            "real_traffic_blocking": False,
            "human_approval_for_disruptive_actions": True,
            "default_action": "observe",
            "decision_audit_required": True,
            "rollback_simulation_required": True,
        },
        "evaluation_plan": {
            "chronological_holdout": True,
            "compare_to_baseline": True,
            "evaluate_false_alarms": True,
            "measure_simulated_service_impact": True,
            "report_uncertainty": True,
            "avoid_future_data_leakage": True,
            "separate_injected_markers_from_real_labels": True,
        },
        "research_limitations": [
            "Source data are synthetic.",
            "No real attack ground truth is available.",
            "No trained detector is introduced in V22.1.",
            "Agent roles are specifications, not running agents.",
            "Simulated actions do not change a real network.",
            "Architecture validation is not security certification.",
        ],
    }


def validate_architecture(model):
    components = model["components"]
    component_ids = [
        item["id"] for item in components
    ]

    check(
        "Six architecture components",
        len(components) == 6,
    )

    check(
        "Component identifiers unique",
        len(set(component_ids)) == 6,
    )

    check(
        "Five future components remain planned",
        sum(
            item["status"] == "planned"
            for item in components
        ) == 5,
    )

    pipeline = model["pipeline"]

    check(
        "Six processing stages",
        len(pipeline) == 6,
    )

    positions = {
        item["id"]: index
        for index, item in enumerate(pipeline)
    }

    check(
        "Pipeline stages unique",
        len(positions) == len(pipeline),
    )

    check(
        "Pipeline is dependency ordered",
        all(
            dependency in positions
            and positions[dependency] < index
            for index, item in enumerate(pipeline)
            for dependency in item["depends_on"]
        ),
    )

    actions = model["defense_actions"]
    action_ids = [
        item["id"] for item in actions
    ]

    check(
        "Five simulated defense action types",
        len(actions) == 5
        and len(set(action_ids)) == 5,
    )

    check(
        "All actions are simulation-only",
        all(
            item["implementation"] == "simulated"
            for item in actions
        ),
    )

    check(
        "Disruptive actions require human approval",
        all(
            item["requires_approval"] is True
            for item in actions
            if item["id"] in {
                "rate_limit",
                "isolate_node",
            }
        ),
    )

    policy = model["policy"]

    check(
        "Safe default action configured",
        policy["default_action"] == "observe",
    )

    check(
        "Simulation mode enforced",
        policy["simulation_mode"] is True,
    )

    check(
        "Real network modifications disabled",
        policy["real_network_changes_allowed"] is False,
    )

    check(
        "Live firewall access disabled",
        policy["live_firewall_access"] is False,
    )

    check(
        "Automatic node isolation disabled",
        policy["automatic_node_isolation"] is False,
    )

    check(
        "Real traffic blocking disabled",
        policy["real_traffic_blocking"] is False,
    )

    check(
        "Human approval required",
        policy[
            "human_approval_for_disruptive_actions"
        ] is True,
    )

    check(
        "Audit trail required",
        policy["decision_audit_required"] is True,
    )

    check(
        "Rollback simulation required",
        policy["rollback_simulation_required"] is True,
    )

    check(
        "Network topology matches V21",
        model["network"]["nodes"] == 10
        and model["network"]["links"] == 11
        and model["network"]["historical_ticks"] == 120,
    )

    bands = list(
        policy["risk_bands"].values()
    )

    check(
        "Risk bands cover zero to one",
        bands[0][0] == 0.0
        and bands[-1][1] == 1.0
        and all(
            left[1] == right[0]
            for left, right in zip(
                bands, bands[1:]
            )
        ),
    )

    evaluation = model["evaluation_plan"]

    check(
        "Chronological evaluation specified",
        evaluation["chronological_holdout"] is True,
    )

    check(
        "Baseline comparison specified",
        evaluation["compare_to_baseline"] is True,
    )

    check(
        "False alarm evaluation specified",
        evaluation["evaluate_false_alarms"] is True,
    )

    check(
        "Simulated service impact evaluation specified",
        evaluation["measure_simulated_service_impact"]
        is True,
    )

    check(
        "Future data leakage prohibited",
        evaluation["avoid_future_data_leakage"] is True,
    )


def make_document(result):
    model = result["architecture"]

    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V22.1 - Autonomous Defense Architecture",
        "",
        f"**Status:** {result['status']}",
        "",
        f"**Checks passed:** {result['checks_passed']}",
        "",
        f"**Checks failed:** {result['checks_failed']}",
        "",
        "### Research foundation",
        "",
        "- Source: V21.6 validated research release",
        "- Synthetic network nodes: 10",
        "- Synthetic network links: 11",
        "- Historical simulation ticks: 120",
        "",
        "### V22 modules",
        "",
        "| Version | Component |",
        "|---|---|",
        "| V22.1 | Autonomous Defense Architecture |",
        "| V22.2 | Adaptive Threat Detection |",
        "| V22.3 | Multi-Agent Defense Decision Engine |",
        "| V22.4 | Defense Strategy Simulation |",
        "| V22.5 | Autonomous Defense Dashboard |",
        "| V22.6 | Research Validation and Release |",
        "",
        "### Simulated defense actions",
        "",
    ]

    for action in model["defense_actions"]:
        lines.append(
            f"- `{action['id']}`: "
            f"{action['label']} "
            f"(approval required: "
            f"{action['requires_approval']})"
        )

    lines += [
        "",
        "### Safety boundaries",
        "",
        "- No real network modifications",
        "- No real firewall operations",
        "- No automatic real isolation",
        "- Human review for disruptive strategies",
        "- Decision provenance and audit required",
        "- Rollback tested inside simulation only",
        "",
        "### Research evaluation",
        "",
        "- Chronological holdout",
        "- Baseline comparison",
        "- Synthetic false alarm evaluation",
        "- Simulated service impact",
        "- Uncertainty reporting",
        "- No future-data leakage",
        "",
        "### Limitations",
        "",
        "V22.1 creates an architecture specification.",
        "It does not implement the V22.2-V22.6 modules.",
        "It does not deploy autonomous agents.",
        "All source observations are synthetic.",
        "No real-world cyber defense capability is established.",
        "",
        "### Next stage",
        "",
        "V22.2 - Adaptive Threat Detection Engine",
        "",
    ]

    return "\n".join(lines)


def source_manifest():
    return {
        name: {
            "path": str(
                path.relative_to(ROOT)
            ),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for name, path in SOURCES.items()
        if path.is_file()
    }


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V22.1 - AUTONOMOUS DEFENSE ARCHITECTURE")
    print("=" * 70)

    V22.mkdir(
        parents=True,
        exist_ok=True,
    )

    reports = load_sources()
    architecture = None
    error = None

    if len(reports) == len(SOURCES):
        try:
            validate_sources(reports)

            if not all(
                item["passed"]
                for item in CHECKS
            ):
                raise ValueError(
                    "V21 source validation failed"
                )

            architecture = build_architecture(
                reports
            )

            validate_architecture(
                architecture
            )

        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            IndexError,
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
            "All V21 source reports loaded",
            False,
            f"{len(reports)}/{len(SOURCES)}",
        )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "AUTONOMOUS_DEFENSE_ARCHITECTURE_PASS"
        if failed == 0
        and architecture is not None
        else "AUTONOMOUS_DEFENSE_ARCHITECTURE_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V22.1",
        "module": "Autonomous Defense Architecture",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "trained_ai_model_used": False,
        "real_network_actions_enabled": False,
        "architecture": architecture,
        "architecture_sha256": (
            sha256_object(architecture)
            if architecture is not None
            else None
        ),
        "source_manifest": source_manifest(),
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error,
        "next_stage": (
            "V22.2 Adaptive Threat Detection Engine"
        ),
    }

    write_json(
        OUTPUT_JSON,
        result,
    )

    if status == "AUTONOMOUS_DEFENSE_ARCHITECTURE_PASS":
        OUTPUT_MD.write_text(
            make_document(result),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V22.1 AUTONOMOUS DEFENSE RESULTS")
    print("=" * 70)

    if architecture is not None:
        print(
            "NETWORK NODES:",
            architecture["network"]["nodes"],
        )

        print(
            "NETWORK LINKS:",
            architecture["network"]["links"],
        )

        print(
            "SIMULATION TICKS:",
            architecture["network"]["historical_ticks"],
        )

        print(
            "DEFENSE COMPONENTS:",
            len(architecture["components"]),
        )

        print(
            "SIMULATED ACTION TYPES:",
            len(architecture["defense_actions"]),
        )

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {OUTPUT_JSON}")

    if status == "AUTONOMOUS_DEFENSE_ARCHITECTURE_PASS":
        print(f"RESEARCH DOCUMENT: {OUTPUT_MD}")

    if error:
        print(f"ERROR: {error}")

    print(f"V22.1 RESULT: {status}")
    print("=" * 70)

    return (
        0
        if status == "AUTONOMOUS_DEFENSE_ARCHITECTURE_PASS"
        else 1
    )


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as exc:
        print(
            "V22.1 FATAL ERROR:",
            f"{type(exc).__name__}: {exc}"
        )
        sys.exit(1)
