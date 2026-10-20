
"""
QUANTUM CYBER DEFENSE ARENA
V23.6 - FINAL ADVANCED CYBER DEFENSE RESEARCH RELEASE

Final research validation for V23.1 - V23.5.

Verifies:
- Research module versions and status
- Previous validation check records
- Source integrity through SHA-256
- Synthetic network topology
- 120 time steps and 1200 node observations
- Three optimization profiles
- 3600 orchestration events
- Simulation-only safety constraints
- V23 dashboard export and HTML assets

Produces:
- advanced_cyber_defense_release_v23_6_results.json
- V23_RESEARCH_RELEASE.md
- frontend/public/v23/release_summary.json

No real network access or defensive actions.
Standard library only.
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
    "optimization": V23 / (
        "adaptive_defense_policy_optimization_v23_3_results.json"
    ),
    "optimization_events": V23 / (
        "adaptive_defense_policy_optimization_v23_3_policies.csv"
    ),
    "optimization_timeline": V23 / (
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
    "dashboard_data": PUBLIC / "defense_data.json",
    "dashboard_html": PUBLIC / "dashboard.html",
    "source_network": ROOT / (
        "frontend/public/v22/defense_data.json"
    ),
}

EXPECTED = {
    "architecture": (
        "V23.1",
        "ADVANCED_CYBER_DEFENSE_ARCHITECTURE_PASS",
    ),
    "fusion": (
        "V23.2",
        "INTELLIGENT_THREAT_FUSION_PASS",
    ),
    "optimization": (
        "V23.3",
        "DEFENSE_POLICY_OPTIMIZATION_PASS",
    ),
    "orchestration": (
        "V23.4",
        "DEFENSE_ORCHESTRATION_PASS",
    ),
}

TIMELINE_VERSIONS = {
    "fusion_timeline": "V23.2",
    "optimization_timeline": "V23.3",
    "orchestration_timeline": "V23.4",
}

RESULT_FILE = V23 / (
    "advanced_cyber_defense_release_v23_6_results.json"
)
DOCUMENT_FILE = V23 / "V23_RESEARCH_RELEASE.md"
SUMMARY_FILE = PUBLIC / "release_summary.json"

PROFILES = {
    "balanced",
    "service_first",
    "risk_first",
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

    if not passed and detail:
        print("    " + str(detail))

    return passed


def load_json(path):
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")

    return data


def load_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise ValueError(f"Empty CSV: {path}")

    return rows


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def sha256_object(data):
    raw = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def number(value):
    if isinstance(value, bool):
        raise ValueError("Boolean is not a measurement")

    n = float(value)

    if not math.isfinite(n):
        raise ValueError("Non-finite measurement")

    return n


def boolean(value):
    if isinstance(value, bool):
        return value

    if str(value).lower() == "true":
        return True

    if str(value).lower() == "false":
        return False

    raise ValueError(f"Invalid boolean: {value}")


def successful(status):
    return (
        isinstance(status, str)
        and status.endswith("_PASS")
    )


def load_sources():
    data = {}

    for name, path in FILES.items():
        if not check(
            f"Source exists: {name}",
            path.is_file(),
            path,
        ):
            continue

        try:
            if path.suffix == ".json":
                data[name] = load_json(path)

            elif path.suffix == ".csv":
                data[name] = load_csv(path)

            else:
                data[name] = path.read_text(
                    encoding="utf-8-sig"
                )

            check(f"Source readable: {name}", True)

        except (OSError, ValueError) as error:
            check(
                f"Source readable: {name}",
                False,
                error,
            )

    return data


def validate_modules(data):
    for name, (version, status) in EXPECTED.items():
        report = data[name]

        check(
            f"{name}: version",
            report.get("version") == version,
        )

        check(
            f"{name}: successful status",
            report.get("status") == status,
        )

        check(
            f"{name}: no validation failures",
            report.get("checks_failed") == 0,
        )

        recorded = report.get("checks", [])

        check(
            f"{name}: check records consistent",
            isinstance(recorded, list)
            and len(recorded) > 0
            and len(recorded)
            == report.get("checks_passed")
            and all(
                isinstance(c, dict)
                and c.get("passed") is True
                for c in recorded
            ),
        )

        check(
            f"{name}: simulation only",
            report.get("simulation_mode") is True,
        )

    dashboard = data["dashboard"]

    check(
        "V23.5 dashboard version",
        dashboard.get("version") == "V23.5",
    )

    check(
        "V23.5 dashboard completed successfully",
        successful(dashboard.get("status"))
        and dashboard.get("checks_failed") == 0,
    )

    check(
        "V23.5 dashboard simulated",
        dashboard.get("simulation_mode") is True,
    )

    dashboard_checks = dashboard.get("checks", [])

    check(
        "V23.5 validation records consistent",
        isinstance(dashboard_checks, list)
        and len(dashboard_checks) > 0
        and len(dashboard_checks)
        == dashboard.get("checks_passed")
        and all(
            isinstance(c, dict)
            and c.get("passed") is True
            for c in dashboard_checks
        ),
    )

    for name, version in TIMELINE_VERSIONS.items():
        report = data[name]

        check(
            f"{name}: version",
            report.get("version") == version,
        )

        check(
            f"{name}: successful simulation export",
            successful(report.get("status"))
            and report.get("simulation_mode") is True
            and report.get("is_live") is False,
        )

        check(
            f"{name}: 120 timeline records",
            isinstance(report.get("timeline"), list)
            and len(report["timeline"]) == 120,
        )


def validate_hashes(data):
    architecture = data["architecture"]
    model = architecture.get("architecture")

    check(
        "V23.1 architecture SHA-256",
        isinstance(model, dict)
        and sha256_object(model)
        == architecture.get("architecture_sha256"),
    )

    chains = [
        ("fusion", {
            "architecture": "architecture",
        }),
        ("optimization", {
            "architecture": "architecture",
            "fusion_report": "fusion",
            "fusion_events": "fusion_events",
        }),
        ("orchestration", {
            "architecture": "architecture",
            "fusion_report": "fusion",
            "policy_report": "optimization",
            "policy_events": "optimization_events",
        }),
    ]

    for report_name, mappings in chains:
        hashes = data[report_name].get(
            "source_sha256", {}
        )

        for source_name, file_name in mappings.items():
            check(
                f"{report_name} SHA-256: {source_name}",
                hashes.get(source_name)
                == sha256_file(FILES[file_name]),
            )

    # V23.5 export schemas can add optional fields.
    # When a known dependency fingerprint exists,
    # it must agree with the current source.
    dashboard_hashes = data["dashboard"].get(
        "source_sha256", {}
    )

    for candidate_names, file_name in (
        (("fusion", "fusion_report"), "fusion"),
        (("optimization", "policy_report"), "optimization"),
        (("orchestration", "orchestration_report"), "orchestration"),
    ):
        present = [
            name for name in candidate_names
            if name in dashboard_hashes
        ]

        for name in present:
            check(
                f"Dashboard SHA-256: {name}",
                dashboard_hashes[name]
                == sha256_file(FILES[file_name]),
            )

    check(
        "Research inputs have source fingerprints",
        all(
            len(data[key].get("source_sha256", {})) > 0
            for key in (
                "fusion",
                "optimization",
                "orchestration",
            )
        ),
    )


def validate_rows(data):
    fusion = data["fusion_events"]
    optimized = data["optimization_events"]
    orchestration = data["orchestration_events"]

    check(
        "1200 fused observations",
        len(fusion) == 1200,
    )

    check(
        "1200 optimized observations",
        len(optimized) == 1200,
    )

    check(
        "3600 orchestration events",
        len(orchestration) == 3600,
    )

    fusion_keys = {
        (int(r["tick"]), r["node_id"])
        for r in fusion
    }

    optimization_keys = {
        (int(r["tick"]), r["node_id"])
        for r in optimized
    }

    orchestration_keys = {
        (
            int(r["tick"]),
            r["node_id"],
            r["profile"],
        )
        for r in orchestration
    }

    expected_keys = {
        (tick, node)
        for tick in range(120)
        for node in {
            r["node_id"]
            for r in fusion
        }
    }

    check(
        "Ten distinct research nodes",
        len({r["node_id"] for r in fusion}) == 10,
    )

    check(
        "Fusion identities complete",
        len(fusion_keys) == 1200
        and fusion_keys == expected_keys,
    )

    check(
        "Optimization identities match fusion",
        len(optimization_keys) == 1200
        and optimization_keys == fusion_keys,
    )

    check(
        "Orchestration identities complete",
        len(orchestration_keys) == 3600
        and orchestration_keys
        == {
            (tick, node, profile)
            for tick, node in fusion_keys
            for profile in PROFILES
        },
    )

    check(
        "Fusion scores bounded",
        all(
            0 <= number(r["fusion_score"]) <= 1
            for r in fusion
        ),
    )

    check(
        "Optimized action profiles available",
        all(
            all(
                f"{profile}_action" in r
                for profile in PROFILES
            )
            for r in optimized
        ),
    )

    check(
        "Orchestration has no real actions",
        all(
            not boolean(r["real_action_executed"])
            and boolean(r["simulation_mode"])
            for r in orchestration
        ),
    )

    check(
        "All approval-required proposals held",
        all(
            r["orchestration_status"]
            == "PENDING_HUMAN_APPROVAL"
            and r["approval_status"] == "NOT_GRANTED"
            and r["effective_simulated_action"]
            == "observe"
            for r in orchestration
            if boolean(r["human_approval_required"])
        ),
    )

    check(
        "No approvals invented",
        all(
            r["approval_status"] != "APPROVED"
            for r in orchestration
        ),
    )

    optimization_map = {
        (int(r["tick"]), r["node_id"]): r
        for r in optimized
    }

    check(
        "Orchestration matches optimized proposals",
        all(
            r["proposed_action"]
            == optimization_map[
                (int(r["tick"]), r["node_id"])
            ][f"{r['profile']}_action"]
            for r in orchestration
        ),
    )

    return {
        "fused_observations": len(fusion),
        "optimized_observations": len(optimized),
        "orchestration_events": len(orchestration),
        "pending_approvals": sum(
            r["orchestration_status"]
            == "PENDING_HUMAN_APPROVAL"
            for r in orchestration
        ),
    }


def validate_timelines(data):
    for name in TIMELINE_VERSIONS:
        timeline = data[name]["timeline"]

        check(
            f"{name}: tick sequence",
            [r.get("tick") for r in timeline]
            == list(range(120)),
        )

        check(
            f"{name}: ten nodes per tick",
            all(
                r.get("evaluated_nodes", 10) == 10
                or (
                    name == "orchestration_timeline"
                    and r.get("total_proposals") == 30
                )
                for r in timeline
            ),
        )

    orchestration_timeline = data[
        "orchestration_timeline"
    ]["timeline"]

    check(
        "Orchestration timeline has 30 proposals per tick",
        all(
            row.get("total_proposals") == 30
            for row in orchestration_timeline
        ),
    )

    check(
        "Three profiles on each orchestration tick",
        all(
            set(row.get("profiles", {})) == PROFILES
            for row in orchestration_timeline
        ),
    )


def validate_dashboard(data):
    dashboard = data["dashboard_data"]
    html = data["dashboard_html"]

    check(
        "V23 dashboard export version",
        dashboard.get("version") == "V23.5",
    )

    check(
        "V23 dashboard data reports success",
        successful(dashboard.get("status")),
    )

    check(
        "V23 dashboard simulated and not live",
        dashboard.get("simulation_mode") is True
        and dashboard.get("is_live") is False,
    )

    frames = dashboard.get("frames")

    check(
        "Dashboard export has 120 frames",
        isinstance(frames, list)
        and len(frames) == 120,
    )

    if isinstance(frames, list) and len(frames) == 120:
        check(
            "Dashboard frame sequence",
            all(
                frame.get("tick") == index
                for index, frame in enumerate(frames)
            ),
        )

        check(
            "Dashboard network contains ten nodes",
            all(
                len(frame.get("nodes", [])) == 10
                for frame in frames
            ),
        )

        check(
            "Dashboard network contains eleven links",
            all(
                len(frame.get("links", [])) == 11
                for frame in frames
            ),
        )

    markers = {
        "HTML document": "<!DOCTYPE html>",
        "D3 library": "d3",
        "Network visualization": "network",
        "Dashboard data loader": "defense_data.json",
        "HTML closing tag": "</html>",
    }

    for name, marker in markers.items():
        check(
            f"Dashboard HTML: {name}",
            marker.lower() in html.lower(),
        )

    for version in ("v20", "v21", "v22"):
        check(
            f"Previous {version} dashboard preserved",
            (
                ROOT / "frontend" / "public"
                / version / "dashboard.html"
            ).is_file(),
        )


def validate_safety(data):
    check(
        "Architecture forbids real actions",
        data["architecture"].get(
            "real_network_actions_enabled"
        ) is False,
    )

    check(
        "Fusion forbids external actions",
        data["fusion"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "Optimization forbids external actions",
        data["optimization"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "Orchestration forbids external actions",
        data["orchestration"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "No trained orchestration agents claimed",
        data["orchestration"].get(
            "metrics", {}
        ).get("trained_ai_agents_used") is False,
    )

    check(
        "Hypothetical strategy effects preserved",
        data["optimization"].get(
            "effects_empirically_verified"
        ) is False,
    )

    check(
        "All source modules use synthetic data",
        all(
            data[name].get("simulation_mode") is True
            for name in EXPECTED
        ),
    )


def source_manifest():
    return {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for name, path in FILES.items()
        if path.is_file()
    }


def markdown_report(report):
    metrics = report["metrics"]

    return f"""# Quantum Cyber Defense Arena

## V23 - Final Advanced Cyber Defense Research Release

**Version:** V23.6

**Status:** {report['status']}

**Validation checks passed:** {report['checks_passed']}

**Validation checks failed:** {report['checks_failed']}

### Completed research modules

| Version | Research module |
|---|---|
| V23.1 | Advanced Cyber Defense Architecture |
| V23.2 | Intelligent Threat Fusion |
| V23.3 | Adaptive Defense Policy Optimization |
| V23.4 | Multi-Agent Defense Orchestration |
| V23.5 | Advanced Cyber Defense Dashboard |
| V23.6 | Final Research Validation and Release |

### Synthetic research dataset

- Network nodes: 10
- Network links: 11
- Simulation ticks: 120
- Fused node observations: {metrics['fused_observations']}
- Optimized node observations: {metrics['optimized_observations']}
- Orchestration events: {metrics['orchestration_events']}
- Pending approvals: {metrics['pending_approvals']}
- Real network actions: 0

### Research controls

- Validated research dependencies
- SHA-256 provenance verification
- Chronological timeline consistency
- Simulation-only defense decisions
- Approval requirements for disruptive proposals
- No automatic real-world intervention
- Independent V23 dashboard export

### Dashboard

`frontend/public/v23/dashboard.html`

This is a synthetic research replay, not live
network monitoring.

### Limitations

- No verified real-world attack ground truth
- Fusion scores are heuristic indices
- Policy effects are hypothetical assumptions
- Agents are deterministic software roles
- No actual autonomous defensive intervention
- No established production attack-detection accuracy
- Dashboard file checks are not browser performance tests

### Research release status

{report['status']}
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V23.6 - FINAL RESEARCH VALIDATION")
    print("=" * 70)

    V23.mkdir(parents=True, exist_ok=True)

    data = load_sources()
    metrics = {}
    error = None

    if len(data) == len(FILES):
        try:
            validate_modules(data)
            validate_hashes(data)
            validate_safety(data)

            metrics = validate_rows(data)

            validate_timelines(data)
            validate_dashboard(data)

            metrics.update({
                "network_nodes": 10,
                "network_links": 11,
                "simulation_ticks": 120,
                "policy_profiles": 3,
                "real_actions_executed": 0,
            })

        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            IndexError,
        ) as exc:
            error = f"{type(exc).__name__}: {exc}"

            check(
                "Complete V23 release validation",
                False,
                error,
            )

    else:
        error = (
            f"Loaded {len(data)} of {len(FILES)} "
            f"required source files"
        )

        check(
            "All required files loaded",
            False,
            error,
        )

    passed = sum(c["passed"] for c in CHECKS)
    failed = len(CHECKS) - passed

    status = (
        "ADVANCED_CYBER_DEFENSE_RELEASE_PASS"
        if failed == 0 and metrics
        else "ADVANCED_CYBER_DEFENSE_RELEASE_FAIL"
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V23.6",
        "module": "Final Advanced Cyber Defense Research Release",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "is_live": False,
        "real_network_actions_enabled": False,
        "effects_empirically_verified": False,
        "metrics": metrics,
        "source_manifest": source_manifest(),
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error,
    }

    write_json(RESULT_FILE, report)

    if status == "ADVANCED_CYBER_DEFENSE_RELEASE_PASS":
        DOCUMENT_FILE.write_text(
            markdown_report(report),
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
    print("V23.6 FINAL CYBER DEFENSE RELEASE")
    print("=" * 70)

    if metrics:
        print(
            "NETWORK NODES:",
            metrics["network_nodes"],
        )
        print(
            "NETWORK LINKS:",
            metrics["network_links"],
        )
        print(
            "SIMULATION TICKS:",
            metrics["simulation_ticks"],
        )
        print(
            "FUSED OBSERVATIONS:",
            metrics["fused_observations"],
        )
        print(
            "OPTIMIZED OBSERVATIONS:",
            metrics["optimized_observations"],
        )
        print(
            "ORCHESTRATION EVENTS:",
            metrics["orchestration_events"],
        )
        print(
            "PENDING APPROVALS:",
            metrics["pending_approvals"],
        )
        print("REAL ACTIONS EXECUTED: 0")

    print("CHECKS PASSED:", passed)
    print("CHECKS FAILED:", failed)
    print("JSON REPORT:", RESULT_FILE)

    if status == "ADVANCED_CYBER_DEFENSE_RELEASE_PASS":
        print("RESEARCH DOCUMENT:", DOCUMENT_FILE)
        print("DASHBOARD SUMMARY:", SUMMARY_FILE)

    if error:
        print("ERROR:", error)

    print("V23.6 RESULT:", status)
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as exc:
        print(
            "V23.6 FATAL ERROR:",
            f"{type(exc).__name__}: {exc}",
        )
        sys.exit(1)
