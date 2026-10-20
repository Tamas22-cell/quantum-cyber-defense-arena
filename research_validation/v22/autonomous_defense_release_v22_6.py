
"""
QUANTUM CYBER DEFENSE ARENA
V22.6 - AUTONOMOUS DEFENSE RESEARCH RELEASE

Final verification of V22.1 through V22.5.

Checks:
- Module status and check records
- Source SHA-256 fingerprints
- Network topology and timeline consistency
- 1200 synthetic decisions
- Adaptive detections and simulated strategy effects
- Approval requirements and no real actions
- D3 dashboard assets and data
- Deterministic cross-module consistency

Outputs:
 research_validation/v22/
   autonomous_defense_release_v22_6_results.json
   V22_RESEARCH_RELEASE.md

 frontend/public/v22/
   release_summary.json

This is research integrity validation, not a
production cybersecurity certification.

Python standard library only.
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
V22 = ROOT / "research_validation" / "v22"
PUBLIC = ROOT / "frontend" / "public" / "v22"

FILES = {
    "architecture": V22 / (
        "autonomous_defense_architecture_v22_1_results.json"
    ),
    "detector": V22 / (
        "adaptive_threat_detection_v22_2_results.json"
    ),
    "detector_scores": V22 / (
        "adaptive_threat_detection_v22_2_scores.csv"
    ),
    "detector_timeline": V22 / (
        "adaptive_threat_detection_v22_2_timeline.json"
    ),
    "decision": V22 / (
        "multi_agent_defense_decision_v22_3_results.json"
    ),
    "decision_events": V22 / (
        "multi_agent_defense_decision_v22_3_decisions.csv"
    ),
    "decision_timeline": V22 / (
        "multi_agent_defense_decision_v22_3_timeline.json"
    ),
    "strategy": V22 / (
        "defense_strategy_simulation_v22_4_results.json"
    ),
    "strategy_events": V22 / (
        "defense_strategy_simulation_v22_4_events.csv"
    ),
    "strategy_timeline": V22 / (
        "defense_strategy_simulation_v22_4_timeline.json"
    ),
    "dashboard": V22 / (
        "autonomous_defense_dashboard_v22_5_results.json"
    ),
    "dashboard_data": PUBLIC / "defense_data.json",
    "dashboard_html": PUBLIC / "dashboard.html",
    "v21_intelligence": ROOT / (
        "frontend/public/v21/intelligence_data.json"
    ),
}

EXPECTED = {
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
}

TIMELINES = {
    "detector_timeline": (
        "V22.2", "ADAPTIVE_THREAT_DETECTION_PASS"
    ),
    "decision_timeline": (
        "V22.3", "DEFENSE_DECISION_PASS"
    ),
    "strategy_timeline": (
        "V22.4", "DEFENSE_STRATEGY_SIMULATION_PASS"
    ),
}

ACTIONS = {
    "observe",
    "increase_monitoring",
    "rate_limit",
    "isolate_node",
    "request_review",
}

APPROVAL_ACTIONS = {
    "rate_limit",
    "isolate_node",
    "request_review",
}

RESULT_FILE = V22 / (
    "autonomous_defense_release_v22_6_results.json"
)
DOCUMENT_FILE = V22 / "V22_RESEARCH_RELEASE.md"
SUMMARY_FILE = PUBLIC / "release_summary.json"

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


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected JSON object: {path.name}"
        )

    return data


def read_csv(path):
    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError(f"Empty CSV: {path.name}")

    return rows


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024), b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def hash_object(obj):
    payload = json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


def write_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


def number(value):
    if isinstance(value, bool):
        raise ValueError("Boolean numeric measurement")

    value = float(value)

    if not math.isfinite(value):
        raise ValueError("Non-finite numeric value")

    return value


def boolean(value):
    if isinstance(value, bool):
        return value

    if str(value).lower() == "true":
        return True

    if str(value).lower() == "false":
        return False

    raise ValueError(f"Invalid boolean: {value}")


def near(a, b, tolerance=0.00001):
    return math.isclose(
        number(a),
        number(b),
        rel_tol=tolerance,
        abs_tol=tolerance,
    )


def load_inputs():
    reports = {}

    for name, path in FILES.items():
        exists = path.is_file()

        check(
            f"File exists: {name}",
            exists,
            str(path),
        )

        if not exists:
            continue

        try:
            if path.suffix == ".json":
                reports[name] = read_json(path)
            elif path.suffix == ".csv":
                reports[name] = read_csv(path)
            elif path.suffix == ".html":
                reports[name] = path.read_text(
                    encoding="utf-8-sig"
                )

            check(f"File readable: {name}", True)

        except (
            OSError, ValueError,
            TypeError, json.JSONDecodeError
        ) as error:
            check(
                f"File readable: {name}",
                False,
                str(error),
            )

    return reports


def verify_modules(data):
    for name, (version, status) in EXPECTED.items():
        report = data[name]

        check(
            f"{name}: expected version",
            report.get("version") == version,
        )

        check(
            f"{name}: successful result",
            report.get("status") == status,
        )

        prior_checks = report.get("checks", [])

        check(
            f"{name}: internal checks consistent",
            isinstance(prior_checks, list)
            and len(prior_checks) > 0
            and report.get("checks_failed") == 0
            and report.get("checks_passed")
            == len(prior_checks)
            and all(
                isinstance(item, dict)
                and item.get("passed") is True
                for item in prior_checks
            ),
        )

        check(
            f"{name}: simulation only",
            report.get("simulation_mode") is True,
        )

    for name, (version, status) in TIMELINES.items():
        timeline = data[name]

        check(
            f"{name}: version and PASS",
            timeline.get("version") == version
            and timeline.get("status") == status
            and timeline.get("simulation_mode") is True
            and timeline.get("is_live") is False,
        )

        check(
            f"{name}: 120 ticks",
            timeline.get("ticks") == 120
            and len(timeline.get("timeline", [])) == 120,
        )


def verify_fingerprints(data):
    arch = data["architecture"]
    model = arch.get("architecture")

    check(
        "V22.1 architecture SHA-256",
        isinstance(model, dict)
        and hash_object(model)
        == arch.get("architecture_sha256"),
    )

    sources = data["detector"].get(
        "source_sha256", {}
    )

    for source_key, filename in (
        ("architecture", "architecture"),
        ("data", "v21_intelligence"),
    ):
        check(
            f"V22.2 fingerprint: {source_key}",
            sources.get(source_key)
            == sha256(FILES[filename]),
        )

    sources = data["decision"].get(
        "source_sha256", {}
    )

    for source_key, filename in (
        ("architecture", "architecture"),
        ("detector_report", "detector"),
        ("detector_scores", "detector_scores"),
        ("intelligence", "v21_intelligence"),
    ):
        check(
            f"V22.3 fingerprint: {source_key}",
            sources.get(source_key)
            == sha256(FILES[filename]),
        )

    sources = data["strategy"].get(
        "source_sha256", {}
    )

    for source_key, filename in (
        ("architecture", "architecture"),
        ("decision_report", "decision"),
        ("decision_csv", "decision_events"),
        ("intelligence", "v21_intelligence"),
    ):
        check(
            f"V22.4 fingerprint: {source_key}",
            sources.get(source_key)
            == sha256(FILES[filename]),
        )

    sources = data["dashboard"].get(
        "source_sha256", {}
    )

    mappings = {
        "network": "v21_intelligence",
        "detector": "detector",
        "detector_timeline": "detector_timeline",
        "decisions": "decision",
        "decision_timeline": "decision_timeline",
        "strategy": "strategy",
        "strategy_timeline": "strategy_timeline",
        "strategy_events": "strategy_events",
    }

    for source_key, filename in mappings.items():
        check(
            f"V22.5 fingerprint: {source_key}",
            sources.get(source_key)
            == sha256(FILES[filename]),
        )


def verify_data(data):
    network = data["v21_intelligence"].get(
        "frames", []
    )

    detector = data["detector_timeline"].get(
        "timeline", []
    )

    decision = data["decision_timeline"].get(
        "timeline", []
    )

    strategy = data["strategy_timeline"].get(
        "timeline", []
    )

    dashboard = data["dashboard_data"].get(
        "frames", []
    )

    groups = (
        network, detector, decision,
        strategy, dashboard,
    )

    check(
        "Five complete 120-tick series",
        all(
            isinstance(group, list)
            and len(group) == 120
            for group in groups
        ),
    )

    if not all(len(group) == 120 for group in groups):
        raise ValueError("Incomplete simulation timeline")

    check(
        "All tick indices aligned",
        all(
            network[i]["tick"]
            == detector[i]["tick"]
            == decision[i]["tick"]
            == strategy[i]["tick"]
            == dashboard[i]["tick"]
            == i
            for i in range(120)
        ),
    )

    check(
        "All timestamps aligned",
        all(
            len({
                network[i]["timestamp"],
                detector[i]["timestamp"],
                decision[i]["timestamp"],
                strategy[i]["timestamp"],
                dashboard[i]["timestamp"],
            }) == 1
            for i in range(120)
        ),
    )

    check(
        "Ten nodes and eleven links per tick",
        all(
            len(frame["nodes"]) == 10
            and len(frame["links"]) == 11
            for frame in dashboard
        ),
    )

    check(
        "Network nodes preserved",
        all(
            source["nodes"] == output["nodes"]
            for source, output
            in zip(network, dashboard)
        ),
    )

    check(
        "Network links preserved",
        all(
            source["links"] == output["links"]
            for source, output
            in zip(network, dashboard)
        ),
    )

    check(
        "Detector counts aligned",
        all(
            source["detections"]
            == output["adaptive_detections"]
            and source["detected_nodes"]
            == output["detected_nodes"]
            for source, output
            in zip(detector, dashboard)
        ),
    )

    check(
        "Decision approval totals aligned",
        all(
            source["human_review_required"]
            == output["human_approval_required"]
            for source, output
            in zip(decision, dashboard)
        ),
    )

    check(
        "Strategy action totals aligned",
        all(
            source["action_counts"]
            == output["action_counts"]
            for source, output
            in zip(strategy, dashboard)
        ),
    )

    check(
        "Original and residual risk aligned",
        all(
            near(
                source["mean_original_risk"],
                output["original_risk"],
            )
            and near(
                source["mean_simulated_residual_risk"],
                output["residual_risk"],
            )
            for source, output
            in zip(strategy, dashboard)
        ),
    )

    check(
        "Service impact values aligned",
        all(
            near(
                source["mean_simulated_service_impact"],
                output["service_impact"],
            )
            for source, output
            in zip(strategy, dashboard)
        ),
    )

    check(
        "Simulated risk and impact bounded",
        all(
            0 <= number(frame["residual_risk"])
            <= number(frame["original_risk"]) <= 1
            and 0 <= number(
                frame["service_impact"]
            ) <= 1
            for frame in dashboard
        ),
    )

    return network, detector, decision, strategy, dashboard


def verify_decisions(data, dashboard):
    decisions = data["decision_events"]
    strategies = data["strategy_events"]
    scores = data["detector_scores"]

    check(
        "1200 decision events",
        len(decisions) == 1200,
    )

    check(
        "1200 strategy events",
        len(strategies) == 1200,
    )

    check(
        "1200 detector observations",
        len(scores) == 1200,
    )

    decision_keys = {
        (int(row["tick"]), row["node_id"])
        for row in decisions
    }

    strategy_keys = {
        (int(row["tick"]), row["node_id"])
        for row in strategies
    }

    detector_keys = {
        (int(row["tick"]), row["node_id"])
        for row in scores
    }

    check(
        "All node-tick keys consistent",
        len(decision_keys) == 1200
        and decision_keys == strategy_keys
        == detector_keys,
    )

    check(
        "All decision identifiers unique",
        len({
            row["decision_id"]
            for row in decisions
        }) == 1200,
    )

    check(
        "All defense action IDs recognized",
        all(
            row["final_action"] in ACTIONS
            for row in decisions
        ),
    )

    check(
        "All strategy action IDs recognized",
        all(
            row["proposed_action"] in ACTIONS
            for row in strategies
        ),
    )

    decision_index = {
        (int(row["tick"]), row["node_id"]): row
        for row in decisions
    }

    check(
        "Strategy proposals match decision engine",
        all(
            row["proposed_action"]
            == decision_index[
                (int(row["tick"]), row["node_id"])
            ]["final_action"]
            for row in strategies
        ),
    )

    check(
        "All restrictive actions require approval",
        all(
            boolean(row["human_approval_required"])
            for row in decisions
            if row["final_action"] in APPROVAL_ACTIONS
        ),
    )

    check(
        "No decision reports an executed action",
        all(
            not boolean(
                row["real_action_executed"]
            )
            for row in decisions
        ),
    )

    check(
        "No strategy reports an executed action",
        all(
            not boolean(
                row["real_action_executed"]
            )
            for row in strategies
        ),
    )

    check(
        "Every strategy remains hypothetical",
        all(
            row["evaluation_type"]
            == "hypothetical_counterfactual"
            and boolean(row["simulation_mode"])
            for row in strategies
        ),
    )

    check(
        "No approval falsely granted",
        all(
            row["approval_status"] != "APPROVED"
            for row in strategies
        ),
    )

    check(
        "All strategy results bounded",
        all(
            0 <= number(
                row["simulated_residual_risk"]
            ) <= number(row["original_risk"]) <= 1
            and 0 <= number(
                row["simulated_service_impact"]
            ) <= 1
            for row in strategies
        ),
    )

    check(
        "All dashboard decisions are simulations",
        all(
            frame["real_actions_executed"] == 0
            and len(frame["decisions"]) == 10
            for frame in dashboard
        ),
    )

    check(
        "Dashboard decisions agree with strategy CSV",
        all(
            any(
                int(row["tick"]) == frame["tick"]
                and row["node_id"] == item["node_id"]
                and row["proposed_action"]
                == item["action"]
                and near(
                    row["simulated_residual_risk"],
                    item["residual_risk"],
                )
                for row in strategies
            )
            for frame in dashboard
            for item in frame["decisions"]
        ),
    )


def verify_dashboard(data):
    export = data["dashboard_data"]
    html = data["dashboard_html"]

    check(
        "Dashboard export successful",
        export.get("version") == "V22.5"
        and export.get("status")
        == "DEFENSE_DASHBOARD_PASS",
    )

    check(
        "Dashboard is simulated and not live",
        export.get("simulation_mode") is True
        and export.get("is_live") is False
        and export.get(
            "effects_empirically_verified"
        ) is False,
    )

    required_markers = {
        "HTML document": "<!DOCTYPE html>",
        "D3 library": "d3@7",
        "Network visualization": 'id="network"',
        "Risk chart": 'id="chart"',
        "Play/Pause control": 'id="play"',
        "Restart control": 'id="restart"',
        "Speed control": 'id="speed"',
        "Timeline slider": 'id="slider"',
        "Decision feed": 'id="decisions"',
        "Data loader": "defense_data.json",
        "Simulation warning": "NO REAL DEFENSE ACTIONS",
        "Closing HTML tag": "</html>",
    }

    for label, marker in required_markers.items():
        check(
            f"Dashboard HTML: {label}",
            marker in html,
        )

    check(
        "V20 dashboard still present",
        (
            ROOT / "frontend/public/v20/dashboard.html"
        ).is_file(),
    )

    check(
        "V21 dashboard still present",
        (
            ROOT / "frontend/public/v21/dashboard.html"
        ).is_file(),
    )


def verify_safety(data):
    arch = data["architecture"].get(
        "architecture", {}
    )

    policy = arch.get("policy", {})

    check(
        "Simulation policy enforced",
        policy.get("simulation_mode") is True,
    )

    check(
        "Real network changes disabled",
        policy.get(
            "real_network_changes_allowed"
        ) is False,
    )

    check(
        "Firewall access disabled",
        policy.get("live_firewall_access") is False,
    )

    check(
        "Automatic isolation disabled",
        policy.get(
            "automatic_node_isolation"
        ) is False,
    )

    check(
        "Human approval requirement preserved",
        policy.get(
            "human_approval_for_disruptive_actions"
        ) is True,
    )

    check(
        "V22.2 no external actions",
        data["detector"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "V22.3 no real actions",
        data["decision"].get(
            "real_actions_executed"
        ) == 0,
    )

    check(
        "V22.4 no external actions",
        data["strategy"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "V22.4 effectiveness not empirically verified",
        data["strategy"].get(
            "effects_empirically_verified"
        ) is False,
    )

    check(
        "V22.5 effects not empirically verified",
        data["dashboard"].get(
            "effects_empirically_verified"
        ) is False,
    )


def collect_metrics(data, dashboard):
    actions = Counter(
        row["final_action"]
        for row in data["decision_events"]
    )

    evaluation = data["strategy"]["evaluation"]

    return {
        "network_nodes": 10,
        "network_links": 11,
        "simulation_ticks": 120,
        "node_observations": len(
            data["detector_scores"]
        ),
        "defense_decisions": len(
            data["decision_events"]
        ),
        "strategy_simulations": len(
            data["strategy_events"]
        ),
        "adaptive_detections": sum(
            frame["adaptive_detections"]
            for frame in dashboard
        ),
        "human_approval_required": sum(
            frame["human_approval_required"]
            for frame in dashboard
        ),
        "action_counts": {
            action: actions[action]
            for action in sorted(ACTIONS)
        },
        "mean_original_risk": evaluation[
            "mean_original_risk"
        ],
        "mean_simulated_residual_risk": evaluation[
            "mean_simulated_residual_risk"
        ],
        "mean_modelled_service_impact": evaluation[
            "mean_modelled_service_impact"
        ],
        "real_actions_executed": 0,
        "dashboard_frames": len(dashboard),
    }


def verify_metrics(data, metrics):
    check(
        "Detector counts match validated report",
        metrics["adaptive_detections"]
        == data["detector"]["metrics"][
            "adaptive_detections"
        ],
    )

    check(
        "Decision totals match validated report",
        metrics["defense_decisions"]
        == data["decision"]["metrics"][
            "decisions"
        ],
    )

    check(
        "Approval totals match validated report",
        metrics["human_approval_required"]
        == data["decision"]["metrics"][
            "human_approval_required"
        ],
    )

    check(
        "Strategy totals match validated report",
        metrics["strategy_simulations"]
        == data["strategy"]["evaluation"][
            "evaluated_decisions"
        ],
    )

    check(
        "Dashboard frames match validated report",
        metrics["dashboard_frames"]
        == data["dashboard"]["metrics"]["ticks"],
    )

    check(
        "Action totals sum to 1200",
        sum(
            metrics["action_counts"].values()
        ) == 1200,
    )


def source_manifest():
    return {
        key: {
            "path": str(
                path.relative_to(ROOT)
            ),
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size,
        }
        for key, path in FILES.items()
        if path.is_file()
    }


def make_document(result):
    m = result["metrics"]

    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V22 - Autonomous Defense Research Release",
        "",
        f"**Version:** {result['version']}",
        f"**Status:** {result['status']}",
        "",
        f"**Checks passed:** {result['checks_passed']}",
        f"**Checks failed:** {result['checks_failed']}",
        "",
        "### Completed modules",
        "",
        "| Version | Research module |",
        "|---|---|",
        "| V22.1 | Autonomous Defense Architecture |",
        "| V22.2 | Adaptive Threat Detection |",
        "| V22.3 | Multi-Agent Defense Decision Engine |",
        "| V22.4 | Defense Strategy Simulation |",
        "| V22.5 | Autonomous Defense Dashboard |",
        "| V22.6 | Research Validation and Release |",
        "",
        "### Network research",
        "",
        f"- Nodes: {m['network_nodes']}",
        f"- Links: {m['network_links']}",
        f"- Simulation ticks: {m['simulation_ticks']}",
        f"- Node observations: {m['node_observations']}",
        f"- Adaptive detections: {m['adaptive_detections']}",
        "",
        "### Defense research",
        "",
        f"- Evaluated decisions: {m['defense_decisions']}",
        f"- Strategy simulations: {m['strategy_simulations']}",
        f"- Approval-required proposals: {m['human_approval_required']}",
        f"- Real actions executed: {m['real_actions_executed']}",
        "",
        "### Simulated strategy outcomes",
        "",
        f"- Mean original risk: {m['mean_original_risk']}",
        f"- Mean modeled residual risk: {m['mean_simulated_residual_risk']}",
        f"- Mean modeled service impact: {m['mean_modelled_service_impact']}",
        "",
        "These outcomes are based on hypothetical",
        "strategy-effect assumptions.",
        "",
        "### Dashboard",
        "",
        "`frontend/public/v22/dashboard.html`",
        "",
        "The dashboard replays 120 synthetic frames",
        "with D3 network movement, detection markers,",
        "proposed strategies and simulated risk charts.",
        "",
        "### Validation scope",
        "",
        "- Module result consistency",
        "- SHA-256 integrity of source dependencies",
        "- Timeline and network topology alignment",
        "- Detector, decision and strategy consistency",
        "- Simulation-only safety checks",
        "- Dashboard data integrity and HTML markers",
        "",
        "### Scientific limitations",
        "",
        "- All network data are synthetic.",
        "- No independently verified real attacks.",
        "- Agent roles are deterministic software.",
        "- Strategy effects are assumptions, not measured outcomes.",
        "- No real defense actions are executed.",
        "- No production detection efficacy established.",
        "- HTML checks are not browser or performance tests.",
        "",
        "### Next development stage",
        "",
        "V23 - Advanced Cyber Defense Research",
        "",
    ]

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V22.6 - AUTONOMOUS DEFENSE RESEARCH RELEASE")
    print("=" * 70)

    V22.mkdir(
        parents=True,
        exist_ok=True,
    )

    reports = load_inputs()
    metrics = {}
    error = None

    if len(reports) == len(FILES):
        try:
            verify_modules(reports)
            verify_fingerprints(reports)
            verify_safety(reports)

            _, _, _, _, dashboard = verify_data(
                reports
            )

            verify_decisions(
                reports,
                dashboard,
            )

            verify_dashboard(reports)

            metrics = collect_metrics(
                reports,
                dashboard,
            )

            verify_metrics(
                reports,
                metrics,
            )

        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            IndexError,
        ) as exc:
            error = (
                f"{type(exc).__name__}: {exc}"
            )

            check(
                "Complete V22 release evaluation",
                False,
                error,
            )

    else:
        error = (
            f"Loaded {len(reports)} "
            f"of {len(FILES)} required inputs"
        )

        check(
            "All V22 source files available",
            False,
            error,
        )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "AUTONOMOUS_DEFENSE_RELEASE_PASS"
        if failed == 0
        and metrics
        else "AUTONOMOUS_DEFENSE_RELEASE_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V22.6",
        "module": "Autonomous Defense Research Release",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "is_live": False,
        "trained_ai_defense_agents": False,
        "real_network_actions_enabled": False,
        "effects_empirically_verified": False,
        "metrics": metrics,
        "source_manifest": source_manifest(),
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error,
        "limitations": [
            "Synthetic network research only.",
            "No real-world attack ground truth.",
            "Deterministic defense decision roles.",
            "Hypothetical defense effectiveness assumptions.",
            "No real network modifications.",
            "No production security certification.",
        ],
        "next_stage": (
            "V23 Advanced Cyber Defense Research"
        ),
    }

    write_json(
        RESULT_FILE,
        result,
    )

    if status == "AUTONOMOUS_DEFENSE_RELEASE_PASS":
        DOCUMENT_FILE.write_text(
            make_document(result),
            encoding="utf-8",
        )

        write_json(
            SUMMARY_FILE,
            {
                "project": "Quantum Cyber Defense Arena",
                "version": "V22.6",
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
    print("V22.6 FINAL RESEARCH RELEASE")
    print("=" * 70)

    if metrics:
        for label, key in (
            ("NETWORK NODES", "network_nodes"),
            ("NETWORK LINKS", "network_links"),
            ("SIMULATION TICKS", "simulation_ticks"),
            ("NODE OBSERVATIONS", "node_observations"),
            ("DEFENSE DECISIONS", "defense_decisions"),
            ("STRATEGY SIMULATIONS", "strategy_simulations"),
            ("ADAPTIVE DETECTIONS", "adaptive_detections"),
            ("DASHBOARD FRAMES", "dashboard_frames"),
            ("REAL ACTIONS EXECUTED", "real_actions_executed"),
        ):
            print(f"{label}: {metrics[key]}")

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {RESULT_FILE}")

    if status == "AUTONOMOUS_DEFENSE_RELEASE_PASS":
        print(f"RESEARCH DOCUMENT: {DOCUMENT_FILE}")
        print(f"DASHBOARD SUMMARY: {SUMMARY_FILE}")

    if error:
        print(f"ERROR: {error}")

    print(f"V22.6 RESULT: {status}")
    print("=" * 70)

    return (
        0
        if status == "AUTONOMOUS_DEFENSE_RELEASE_PASS"
        else 1
    )


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as exc:
        print()
        print(
            "V22.6 FATAL ERROR:",
            f"{type(exc).__name__}: {exc}",
        )
        sys.exit(1)
