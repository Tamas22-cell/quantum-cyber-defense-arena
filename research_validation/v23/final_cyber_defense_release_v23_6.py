
"""
QUANTUM CYBER DEFENSE ARENA
V23.6 - FINAL CYBER DEFENSE RESEARCH RELEASE

Validates:
  V23.1 Architecture
  V23.2 Threat Fusion
  V23.3 Policy Optimization
  V23.4 Defense Orchestration
  V23.5 Advanced D3 Dashboard

Required outputs:
  research_validation/v23/
    final_cyber_defense_release_v23_6_results.json
    V23_FINAL_RESEARCH_RELEASE.md

  frontend/public/v23/
    release_summary.json

No real network operations.
No claims of production cybersecurity effectiveness.
Standard Python library only.
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
V23 = ROOT / "research_validation" / "v23"
PUBLIC = ROOT / "frontend" / "public" / "v23"

FILES = {
    "architecture": V23 / (
        "advanced_cyber_defense_architecture_v23_1_results.json"
    ),
    "fusion": V23 / (
        "intelligent_threat_fusion_v23_2_results.json"
    ),
    "fusion_events": V23 / (
        "intelligent_threat_fusion_v23_2_events.csv"
    ),
    "fusion_timeline": V23 / (
        "intelligent_threat_fusion_v23_2_timeline.json"
    ),
    "policy": V23 / (
        "adaptive_defense_policy_optimization_v23_3_results.json"
    ),
    "policy_events": V23 / (
        "adaptive_defense_policy_optimization_v23_3_policies.csv"
    ),
    "policy_timeline": V23 / (
        "adaptive_defense_policy_optimization_v23_3_timeline.json"
    ),
    "orchestration": V23 / (
        "multi_agent_defense_orchestration_v23_4_results.json"
    ),
    "orchestration_events": V23 / (
        "multi_agent_defense_orchestration_v23_4_events.csv"
    ),
    "orchestration_timeline": V23 / (
        "multi_agent_defense_orchestration_v23_4_timeline.json"
    ),
    "dashboard": V23 / (
        "advanced_cyber_defense_dashboard_v23_5_results.json"
    ),
}

RESULT_FILE = V23 / (
    "final_cyber_defense_release_v23_6_results.json"
)
DOCUMENT_FILE = V23 / "V23_FINAL_RESEARCH_RELEASE.md"
SUMMARY_FILE = PUBLIC / "release_summary.json"

EXPECTED = {
    "architecture": (
        "V23.1",
        "ADVANCED_CYBER_DEFENSE_ARCHITECTURE_PASS",
    ),
    "fusion": (
        "V23.2",
        "INTELLIGENT_THREAT_FUSION_PASS",
    ),
    "policy": (
        "V23.3",
        "DEFENSE_POLICY_OPTIMIZATION_PASS",
    ),
    "orchestration": (
        "V23.4",
        "DEFENSE_ORCHESTRATION_PASS",
    ),
}

PROFILES = {
    "balanced",
    "service_first",
    "risk_first",
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

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected JSON object: {path.name}"
        )

    return data


def read_csv(path):
    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        raise ValueError(
            f"Empty CSV: {path.name}"
        )

    return rows


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


def num(value):
    if isinstance(value, bool):
        raise ValueError("Boolean is not numeric")

    value = float(value)

    if not math.isfinite(value):
        raise ValueError("Non-finite measurement")

    return value


def boolean(value):
    if isinstance(value, bool):
        return value

    if str(value).lower() == "true":
        return True

    if str(value).lower() == "false":
        return False

    raise ValueError(
        f"Invalid boolean value: {value}"
    )


def close(a, b, tolerance=0.000005):
    return math.isclose(
        num(a),
        num(b),
        rel_tol=tolerance,
        abs_tol=tolerance,
    )


def load_sources():
    data = {}

    for name, path in FILES.items():
        exists = check(
            f"File available: {name}",
            path.is_file(),
            str(path),
        )

        if not exists:
            continue

        try:
            if path.suffix == ".csv":
                data[name] = read_csv(path)
            else:
                data[name] = read_json(path)

            check(
                f"File readable: {name}",
                True,
            )

        except (OSError, ValueError) as error:
            check(
                f"File readable: {name}",
                False,
                str(error),
            )

    return data


def validate_reports(data):
    for name, (version, status) in EXPECTED.items():
        report = data[name]

        check(
            f"{version} expected version",
            report.get("version") == version,
        )

        check(
            f"{version} successful status",
            report.get("status") == status,
        )

        previous = report.get("checks", [])

        check(
            f"{version} internal checks consistent",
            isinstance(previous, list)
            and len(previous) > 0
            and report.get("checks_passed") == len(previous)
            and report.get("checks_failed") == 0
            and all(
                isinstance(item, dict)
                and item.get("passed") is True
                for item in previous
            ),
        )

        check(
            f"{version} simulation only",
            report.get("simulation_mode") is True,
        )

    dashboard = data["dashboard"]

    check(
        "V23.5 dashboard version",
        dashboard.get("version") == "V23.5",
    )

    check(
        "V23.5 dashboard PASS status",
        isinstance(dashboard.get("status"), str)
        and dashboard["status"].endswith("_PASS"),
    )

    check(
        "V23.5 dashboard validation passed",
        dashboard.get("checks_failed") == 0
        and dashboard.get("checks_passed", 0) > 0
        and isinstance(dashboard.get("checks"), list)
        and len(dashboard["checks"])
        == dashboard.get("checks_passed")
        and all(
            isinstance(item, dict)
            and item.get("passed") is True
            for item in dashboard["checks"]
        ),
    )

    check(
        "V23.5 simulation mode",
        dashboard.get("simulation_mode") is True
        and dashboard.get("is_live") is False,
    )


def verify_fingerprints(data):
    fusion_hashes = data["fusion"].get(
        "source_sha256", {}
    )

    check(
        "V23.2 architecture fingerprint",
        fusion_hashes.get("architecture")
        == sha256_file(FILES["architecture"]),
    )

    policy_hashes = data["policy"].get(
        "source_sha256", {}
    )

    check(
        "V23.3 architecture fingerprint",
        policy_hashes.get("architecture")
        == sha256_file(FILES["architecture"]),
    )

    check(
        "V23.3 fusion report fingerprint",
        policy_hashes.get("fusion_report")
        == sha256_file(FILES["fusion"]),
    )

    check(
        "V23.3 fusion CSV fingerprint",
        policy_hashes.get("fusion_events")
        == sha256_file(FILES["fusion_events"]),
    )

    orchestration_hashes = data["orchestration"].get(
        "source_sha256", {}
    )

    for source, file_key in (
        ("architecture", "architecture"),
        ("fusion_report", "fusion"),
        ("policy_report", "policy"),
        ("policy_events", "policy_events"),
    ):
        check(
            f"V23.4 fingerprint: {source}",
            orchestration_hashes.get(source)
            == sha256_file(FILES[file_key]),
        )

    dashboard_hashes = data["dashboard"].get(
        "source_sha256", {}
    )

    for source, file_key in (
        ("architecture", "architecture"),
        ("fusion", "fusion"),
        ("fusion_report", "fusion"),
        ("fusion_events", "fusion_events"),
        ("policy", "policy"),
        ("policy_report", "policy"),
        ("policy_events", "policy_events"),
        ("orchestration", "orchestration"),
        ("orchestration_report", "orchestration"),
        ("orchestration_events", "orchestration_events"),
        ("orchestration_timeline", "orchestration_timeline"),
    ):
        if source in dashboard_hashes:
            check(
                f"V23.5 fingerprint: {source}",
                dashboard_hashes[source]
                == sha256_file(FILES[file_key]),
            )

    check(
        "V23.5 has source fingerprint manifest",
        isinstance(dashboard_hashes, dict)
        and len(dashboard_hashes) >= 3,
    )


def validate_timelines(data):
    timeline_specs = {
        "fusion_timeline": (
            "V23.2",
            "INTELLIGENT_THREAT_FUSION_PASS",
        ),
        "policy_timeline": (
            "V23.3",
            "DEFENSE_POLICY_OPTIMIZATION_PASS",
        ),
        "orchestration_timeline": (
            "V23.4",
            "DEFENSE_ORCHESTRATION_PASS",
        ),
    }

    groups = {}

    for name, (version, status) in timeline_specs.items():
        export = data[name]

        check(
            f"{name}: version and status",
            export.get("version") == version
            and export.get("status") == status,
        )

        check(
            f"{name}: synthetic replay",
            export.get("simulation_mode") is True
            and export.get("is_live") is False,
        )

        records = export.get("timeline", [])
        groups[name] = records

        check(
            f"{name}: 120 ordered ticks",
            len(records) == 120
            and [
                item.get("tick")
                for item in records
            ] == list(range(120)),
        )

    if not all(
        len(records) == 120
        for records in groups.values()
    ):
        raise ValueError("Timeline length mismatch")

    check(
        "All timeline timestamps aligned",
        all(
            len({
                groups[name][tick]["timestamp"]
                for name in groups
            }) == 1
            for tick in range(120)
        ),
    )

    check(
        "Fusion timeline contains ten nodes per tick",
        all(
            frame["evaluated_nodes"] == 10
            for frame in groups["fusion_timeline"]
        ),
    )

    check(
        "Policy timeline contains three profiles",
        all(
            set(frame["profiles"]) == PROFILES
            and frame["evaluated_nodes"] == 10
            for frame in groups["policy_timeline"]
        ),
    )

    check(
        "Orchestration timeline has 30 events per tick",
        all(
            frame["total_proposals"] == 30
            and set(frame["profiles"]) == PROFILES
            for frame in groups["orchestration_timeline"]
        ),
    )

    return groups


def validate_events(data, groups):
    fusion = data["fusion_events"]
    policy = data["policy_events"]
    orchestration = data["orchestration_events"]

    check(
        "1200 threat fusion observations",
        len(fusion) == 1200,
    )

    check(
        "1200 policy optimization observations",
        len(policy) == 1200,
    )

    check(
        "3600 orchestration events",
        len(orchestration) == 3600,
    )

    fusion_index = {
        (int(r["tick"]), r["node_id"]): r
        for r in fusion
    }

    policy_index = {
        (int(r["tick"]), r["node_id"]): r
        for r in policy
    }

    orchestration_index = {
        (
            int(r["tick"]),
            r["node_id"],
            r["profile"],
        ): r
        for r in orchestration
    }

    check(
        "Fusion node-tick identifiers unique",
        len(fusion_index) == len(fusion),
    )

    check(
        "Policy node-tick identifiers unique",
        len(policy_index) == len(policy),
    )

    check(
        "Orchestration identifiers unique",
        len(orchestration_index) == len(orchestration),
    )

    check(
        "Fusion and policy node-tick sets identical",
        set(fusion_index) == set(policy_index),
    )

    check(
        "Every policy has three orchestration records",
        set(orchestration_index) == {
            (tick, node, profile)
            for tick, node in policy_index
            for profile in PROFILES
        },
    )

    check(
        "Fused scores agree with policy inputs",
        all(
            close(
                fusion_index[key]["fusion_score"],
                policy_index[key]["fusion_score"],
            )
            for key in fusion_index
        ),
    )

    check(
        "Orchestrated proposals match chosen policies",
        all(
            item["proposed_action"]
            == policy_index[
                (int(item["tick"]), item["node_id"])
            ][f"{item['profile']}_action"]
            for item in orchestration
        ),
    )

    check(
        "All orchestration fusion scores agree",
        all(
            close(
                item["fusion_score"],
                fusion_index[
                    (int(item["tick"]), item["node_id"])
                ]["fusion_score"],
            )
            for item in orchestration
        ),
    )

    check(
        "Every disruptive proposal awaits approval",
        all(
            item["orchestration_status"]
            == "PENDING_HUMAN_APPROVAL"
            and item["approval_status"] == "NOT_GRANTED"
            and item["effective_simulated_action"] == "observe"
            for item in orchestration
            if item["proposed_action"] in APPROVAL_ACTIONS
        ),
    )

    check(
        "No approval falsely granted",
        all(
            item["approval_status"] != "APPROVED"
            for item in orchestration
        ),
    )

    check(
        "All simulated decisions remain non-executing",
        all(
            boolean(item["simulation_mode"])
            and not boolean(item["real_action_executed"])
            for item in orchestration
        ),
    )

    check(
        "Orchestrator records use recognized actions",
        all(
            item["proposed_action"] in ACTIONS
            and item["effective_simulated_action"] in ACTIONS
            for item in orchestration
        ),
    )

    check(
        "All policy outcomes are finite and bounded",
        all(
            0 <= num(row[f"{name}_residual_risk"]) <= 1
            and 0 <= num(row[f"{name}_service_impact"]) <= 1
            for row in policy
            for name in PROFILES
        ),
    )

    check(
        "Orchestration totals agree with report",
        len(orchestration)
        == data["orchestration"]["metrics"]["events"],
    )

    check(
        "Policy record totals agree with report",
        len(policy)
        == data["policy"]["metrics"]["optimized_observations"],
    )

    check(
        "Fusion record totals agree with report",
        len(fusion)
        == data["fusion"]["metrics"]["fused_observations"],
    )

    check(
        "Fusion timeline totals match CSV",
        sum(
            row["evaluated_nodes"]
            for row in groups["fusion_timeline"]
        ) == len(fusion),
    )

    check(
        "Orchestration timeline totals match CSV",
        sum(
            row["total_proposals"]
            for row in groups["orchestration_timeline"]
        ) == len(orchestration),
    )

    return {
        "simulation_ticks": 120,
        "network_nodes": 10,
        "fusion_observations": len(fusion),
        "policy_observations": len(policy),
        "policy_profiles": len(PROFILES),
        "orchestration_events": len(orchestration),
        "pending_approvals": sum(
            row["orchestration_status"]
            == "PENDING_HUMAN_APPROVAL"
            for row in orchestration
        ),
        "real_actions_executed": 0,
    }


def discover_dashboard_assets():
    """
    Discover existing V23 assets without modifying
    them or inventing an output filename.
    """

    html_path = PUBLIC / "dashboard.html"

    check(
        "V23 dashboard HTML available",
        html_path.is_file(),
        str(html_path),
    )

    if not html_path.is_file():
        return None, None

    html = html_path.read_text(
        encoding="utf-8-sig"
    )

    check(
        "HTML document structure",
        "<!DOCTYPE html>" in html.upper()
        or "<!doctype html>" in html.lower(),
    )

    check(
        "HTML document closed",
        "</html>" in html.lower(),
    )

    check(
        "D3 library referenced",
        "d3" in html.lower(),
    )

    check(
        "V23 dashboard labeled",
        "V23" in html.upper(),
    )

    check(
        "Simulation status visible",
        "simulat" in html.lower(),
    )

    json_candidates = [
        p for p in PUBLIC.glob("*.json")
        if p.name != "release_summary.json"
    ]

    valid_candidates = []

    for path in sorted(json_candidates):
        try:
            data = read_json(path)
        except (OSError, ValueError):
            continue

        if (
            data.get("version") == "V23.5"
            and data.get("simulation_mode") is True
            and isinstance(data.get("frames"), list)
            and len(data["frames"]) == 120
        ):
            valid_candidates.append((path, data))

    check(
        "V23 dashboard data export discovered",
        len(valid_candidates) == 1,
        f"Matching exports: {len(valid_candidates)}",
    )

    if len(valid_candidates) != 1:
        return html_path, None

    data_path, data = valid_candidates[0]

    check(
        "Dashboard data matches V23.5",
        data.get("version") == "V23.5"
        and data.get("status", "").endswith("_PASS")
        and data.get("is_live") is False,
    )

    check(
        "Dashboard data has 120 ordered frames",
        [
            frame.get("tick")
            for frame in data["frames"]
        ] == list(range(120)),
    )

    check(
        "Dashboard loads the actual data filename",
        data_path.name in html,
    )

    return html_path, data_path


def verify_safety(data):
    architecture = data["architecture"].get(
        "architecture", {}
    )

    safety = architecture.get(
        "safety_policy", {}
    )

    check(
        "Real network access prohibited",
        safety.get("real_network_access") is False,
    )

    check(
        "Real firewall modifications prohibited",
        safety.get("real_firewall_changes") is False,
    )

    check(
        "Real node isolation prohibited",
        safety.get("real_node_isolation") is False,
    )

    check(
        "Automated disruptive actions disabled",
        safety.get(
            "automated_disruptive_actions"
        ) is False,
    )

    check(
        "Human approval policy preserved",
        safety.get(
            "approval_for_disruptive_proposals"
        ) is True,
    )

    check(
        "Fusion external actions disabled",
        data["fusion"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "Policy external actions disabled",
        data["policy"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "Orchestration external actions disabled",
        data["orchestration"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "V23.3 effects not empirically verified",
        data["policy"].get(
            "effects_empirically_verified"
        ) is False,
    )

    check(
        "V20 to V22 dashboard files retained",
        all(
            (
                ROOT / "frontend" / "public"
                / version / "dashboard.html"
            ).is_file()
            for version in ("v20", "v21", "v22")
        ),
    )


def source_manifest(extra_paths=None):
    manifest = {
        key: {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for key, path in FILES.items()
        if path.is_file()
    }

    for key, path in (extra_paths or {}).items():
        if path is not None and path.is_file():
            manifest[key] = {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }

    return manifest


def make_document(result):
    metrics = result["metrics"]

    return f"""# Quantum Cyber Defense Arena

## V23.6 - Final Cyber Defense Research Release

**Status:** {result['status']}

**Checks passed:** {result['checks_passed']}

**Checks failed:** {result['checks_failed']}

### V23 research modules

| Module | Description |
|---|---|
| V23.1 | Advanced Cyber Defense Architecture |
| V23.2 | Intelligent Threat Fusion |
| V23.3 | Adaptive Defense Policy Optimization |
| V23.4 | Multi-Agent Defense Orchestration |
| V23.5 | Advanced Cyber Defense Dashboard |
| V23.6 | Final Research Validation & Release |

### Research dataset

- Synthetic network nodes: {metrics['network_nodes']}
- Simulation ticks: {metrics['simulation_ticks']}
- Threat fusion observations: {metrics['fusion_observations']}
- Policy observations: {metrics['policy_observations']}
- Policy profiles: {metrics['policy_profiles']}
- Orchestration events: {metrics['orchestration_events']}
- Pending simulated approvals: {metrics['pending_approvals']}
- Real actions executed: {metrics['real_actions_executed']}

### Integrity verification

The JSON release contains SHA-256 fingerprints
for all required V23 source research artifacts.

The validator checks cross-module consistency,
timeline alignment, unique record identities,
approval policy and dashboard assets.

### Scientific limitations

This is a research prototype using synthetic data.

- No independently verified real cyberattack labels
- Threat fusion scores are heuristic indices
- Policy optimization uses assumed effect models
- Multi-agent roles are deterministic software roles
- No actual autonomous security response
- No measured real-world defense effectiveness
- Static HTML checks are not browser performance tests
- PASS means internal research checks succeeded,
  not that production security is certified

### Release scope

V23.1 - V23.6 research artifacts and
the separate V23 replay dashboard.
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V23.6 - FINAL CYBER DEFENSE RESEARCH RELEASE")
    print("=" * 70)

    V23.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = load_sources()
    metrics = {}
    error = None
    extra_paths = {}

    if len(data) == len(FILES):
        try:
            validate_reports(data)

            verify_fingerprints(data)

            groups = validate_timelines(data)

            metrics = validate_events(
                data,
                groups,
            )

            verify_safety(data)

            html_path, dashboard_data_path = (
                discover_dashboard_assets()
            )

            extra_paths = {
                "v23_dashboard_html": html_path,
                "v23_dashboard_data": dashboard_data_path,
            }

            check(
                "All source verification steps completed",
                True,
            )

        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            IndexError,
            AttributeError,
        ) as exc:
            error = (
                f"{type(exc).__name__}: {exc}"
            )

            check(
                "Final release validation completed",
                False,
                error,
            )

    else:
        error = (
            f"Loaded {len(data)} "
            f"of {len(FILES)} source artifacts"
        )

        check(
            "All V23 sources loaded",
            False,
            error,
        )

    passed = sum(
        item["passed"] for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "FINAL_CYBER_DEFENSE_RELEASE_PASS"
        if failed == 0 and metrics
        else "FINAL_CYBER_DEFENSE_RELEASE_FAIL"
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V23.6",
        "module": "Final Cyber Defense Research Release",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "is_live": False,
        "trained_ai_defense_agents": False,
        "real_network_actions_enabled": False,
        "defense_effectiveness_empirically_verified": False,
        "metrics": metrics,
        "source_manifest": source_manifest(
            extra_paths
        ),
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error,
        "limitations": [
            "Synthetic research data only.",
            "No independently verified attack labels.",
            "Fixed heuristic threat fusion.",
            "Hypothetical defense policy effects.",
            "Deterministic orchestration roles.",
            "No real network actions.",
            "No production security certification.",
            "Browser compatibility not established by this test.",
        ],
        "next_stage": (
            "GitHub release and independent research review"
        ),
    }

    write_json(
        RESULT_FILE,
        report,
    )

    if status == "FINAL_CYBER_DEFENSE_RELEASE_PASS":
        DOCUMENT_FILE.write_text(
            make_document(report),
            encoding="utf-8",
        )

        write_json(
            SUMMARY_FILE,
            {
                "project": "Quantum Cyber Defense Arena",
                "version": "V23.6",
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
    print("V23.6 FINAL RESEARCH RELEASE RESULTS")
    print("=" * 70)

    if metrics:
        for title, field in (
            ("SIMULATION TICKS", "simulation_ticks"),
            ("NETWORK NODES", "network_nodes"),
            ("FUSION OBSERVATIONS", "fusion_observations"),
            ("POLICY OBSERVATIONS", "policy_observations"),
            ("POLICY PROFILES", "policy_profiles"),
            ("ORCHESTRATION EVENTS", "orchestration_events"),
            ("PENDING APPROVALS", "pending_approvals"),
            ("REAL ACTIONS EXECUTED", "real_actions_executed"),
        ):
            print(f"{title}: {metrics[field]}")

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {RESULT_FILE}")

    if status == "FINAL_CYBER_DEFENSE_RELEASE_PASS":
        print(f"RESEARCH DOCUMENT: {DOCUMENT_FILE}")
        print(f"DASHBOARD SUMMARY: {SUMMARY_FILE}")

    if error:
        print(f"ERROR: {error}")

    print(f"V23.6 RESULT: {status}")
    print("=" * 70)

    return (
        0
        if status == "FINAL_CYBER_DEFENSE_RELEASE_PASS"
        else 1
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(
            "V23.6 FAILED:",
            f"{type(exc).__name__}: {exc}",
        )
        sys.exit(1)
