
"""
QUANTUM CYBER DEFENSE ARENA
V19.6 - MULTI-AGENT RESEARCH RELEASE

Final V19 release:
- Verify V19.1 to V19.5 outputs
- Verify source fingerprints
- Validate research, validation and benchmark findings
- Check Supervisor approval and workflow
- Export JSON, Markdown and dashboard data

Standard library only.
No LLM calls, network calls or security actions.
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
PUBLIC = ROOT / "frontend" / "public" / "v19"

FILES = {
    "architecture": "multi_agent_architecture_v19_1_results.json",
    "research": "research_agent_v19_2_results.json",
    "validation": "validation_agent_v19_3_results.json",
    "benchmark": "benchmark_agent_v19_4_results.json",
    "supervisor": "autonomous_supervisor_v19_5_results.json",
}

EXPECTED = {
    "architecture": ("V19.1", "ARCHITECTURE_PASS"),
    "research": ("V19.2", "RESEARCH_AGENT_PASS"),
    "validation": ("V19.3", "VALIDATION_AGENT_PASS"),
    "benchmark": ("V19.4", "BENCHMARK_AGENT_PASS"),
    "supervisor": ("V19.5", "SUPERVISOR_PASS"),
}

OUTPUT = V19 / "multi_agent_research_release_v19_6_results.json"
MARKDOWN = V19 / "V19_RESEARCH_RELEASE.md"
DASHBOARD = PUBLIC / "multi_agent_v19_dashboard.json"

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
        print("      ", detail)

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


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid JSON object: {path.name}")

    return data


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(
            data,
            handle,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )


def finite(value):
    if isinstance(value, bool):
        return False

    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_reports():
    reports = {}

    for key, filename in FILES.items():
        path = V19 / filename

        if not check(
            f"File exists: {filename}",
            path.is_file(),
        ):
            continue

        try:
            reports[key] = read_json(path)
            check(f"Readable JSON: {key}", True)
        except (OSError, ValueError) as error:
            check(
                f"Readable JSON: {key}",
                False,
                str(error),
            )

    return reports


def validate_reports(reports):
    for key, (version, status) in EXPECTED.items():
        report = reports.get(key)

        if report is None:
            check(f"{key}: report available", False)
            continue

        check(
            f"{key}: correct version",
            report.get("version") == version,
        )

        check(
            f"{key}: successful status",
            report.get("status") == status,
        )

        checks = report.get("checks", [])
        passed = report.get("checks_passed")
        failed = report.get("checks_failed")

        valid_checks = (
            isinstance(checks, list)
            and len(checks) > 0
            and type(passed) is int
            and type(failed) is int
            and failed == 0
            and passed == len(checks)
            and all(
                isinstance(item, dict)
                and item.get("passed") is True
                for item in checks
            )
        )

        check(
            f"{key}: internal checks consistent",
            valid_checks,
        )


def validate_fingerprints(reports):
    validation = reports["validation"]
    supervisor = reports["supervisor"]

    research_path = V19 / FILES["research"]
    architecture_path = V19 / FILES["architecture"]

    check(
        "Validation references current Research Agent",
        validation.get("research_agent_sha256")
        == sha256_file(research_path),
    )

    check(
        "Validation references current architecture",
        validation.get("architecture_sha256")
        == sha256_file(architecture_path),
    )

    fingerprints = supervisor.get(
        "source_fingerprints", {}
    )

    for key in (
        "architecture",
        "research",
        "validation",
        "benchmark",
    ):
        actual = sha256_file(V19 / FILES[key])

        check(
            f"Supervisor fingerprint: {key}",
            fingerprints.get(key) == actual,
        )


def validate_agents(reports):
    architecture = reports["architecture"]
    research = reports["research"]
    validation = reports["validation"]
    benchmark = reports["benchmark"]
    supervisor = reports["supervisor"]

    expected_agents = {
        "research_agent",
        "validation_agent",
        "benchmark_agent",
        "supervisor_agent",
    }

    agents = architecture.get("agents", [])

    agent_ids = [
        agent.get("id")
        for agent in agents
        if isinstance(agent, dict)
    ]

    check(
        "Four unique research agents",
        len(agent_ids) == 4
        and set(agent_ids) == expected_agents,
    )

    check(
        "No external agent actions",
        all(
            isinstance(agent, dict)
            and agent.get("permissions", {}).get(
                "external_actions"
            ) is False
            for agent in agents
        )
        and len(agents) == 4,
    )

    findings = research.get("findings", [])

    finding_ids = [
        item.get("finding_id")
        for item in findings
        if isinstance(item, dict)
    ]

    check(
        "Seven unique research findings",
        len(findings) == 7
        and len(finding_ids) == 7
        and len(set(finding_ids)) == 7,
    )

    validated = validation.get("finding_results", [])

    validated_ids = [
        item.get("finding_id")
        for item in validated
        if isinstance(item, dict)
        and item.get("status") == "VALIDATED"
    ]

    check(
        "All findings validated",
        len(validated) == 7
        and set(validated_ids) == set(finding_ids)
        and len(set(validated_ids)) == 7
        and validation.get("findings_validated") == 7,
    )

    data = benchmark.get("benchmark") or {}

    check(
        "Benchmark result present",
        isinstance(data, dict)
        and type(data.get("samples")) is int
        and data["samples"] >= 10
        and finite(data.get("spearman")),
    )

    check(
        "Benchmark matches research sample count",
        data.get("samples")
        == architecture.get(
            "research_dataset", {}
        ).get("samples"),
    )

    check(
        "Benchmark scientific limitations respected",
        data.get("verified_attack_labels") is False
        and data.get(
            "quantum_advantage_demonstrated"
        ) is False
        and data.get(
            "runtime_comparison_is_fair"
        ) is False,
    )

    check(
        "Supervisor has approved research validation",
        supervisor.get("supervisor_decision")
        == "RESEARCH_APPROVED_FOR_RELEASE_VALIDATION",
    )

    tasks = supervisor.get("workflow_tasks", [])

    expected_tasks = {
        "TASK-001",
        "TASK-002",
        "TASK-003",
        "TASK-004",
    }

    completed_ids = [
        item.get("task_id")
        for item in tasks
        if isinstance(item, dict)
        and item.get("status") == "COMPLETED"
    ]

    check(
        "Four unique workflow tasks completed",
        len(tasks) == 4
        and len(completed_ids) == 4
        and set(completed_ids) == expected_tasks,
    )

    check(
        "Human review requirement retained",
        supervisor.get(
            "human_review_required_for_high_impact_actions"
        ) is True,
    )

    check(
        "Supervisor external actions disabled",
        supervisor.get("external_actions_enabled") is False,
    )

    check(
        "Research Agent is deterministic",
        research.get("llm_enabled") is False,
    )

    check(
        "Supervisor is deterministic",
        supervisor.get("llm_enabled") is False,
    )


def source_manifest():
    result = {}

    for key, filename in FILES.items():
        path = V19 / filename

        if path.is_file():
            result[key] = {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }

    return result


def dashboard_data(reports, status):
    benchmark = reports["benchmark"]["benchmark"]
    research = reports["research"]
    validation = reports["validation"]
    supervisor = reports["supervisor"]

    return {
        "project": "Quantum Cyber Defense Arena",
        "version": "V19.6",
        "status": status,
        "data_mode": "SAVED_RESEARCH_RESULTS",
        "is_live": False,
        "agent_type": "deterministic_rule_based",
        "llm_enabled": False,
        "external_actions_enabled": False,
        "agents": [
            {
                "id": "research_agent",
                "label": "Research Agent",
                "status": "VALIDATED",
            },
            {
                "id": "validation_agent",
                "label": "Validation Agent",
                "status": "VALIDATED",
            },
            {
                "id": "benchmark_agent",
                "label": "Benchmark Agent",
                "status": "VALIDATED",
            },
            {
                "id": "supervisor_agent",
                "label": "Supervisor Agent",
                "status": "VALIDATED",
            },
        ],
        "research": {
            "findings_generated": research.get(
                "findings_count"
            ),
            "findings_validated": validation.get(
                "findings_validated"
            ),
            "samples": benchmark.get("samples"),
            "spearman": benchmark.get("spearman"),
            "top_k": benchmark.get("top_k"),
            "top_k_overlap": benchmark.get(
                "top_k_overlap"
            ),
        },
        "supervisor": {
            "decision": supervisor.get(
                "supervisor_decision"
            ),
            "completed_tasks": len(
                supervisor.get("workflow_tasks", [])
            ),
            "human_review_required": True,
        },
        "scientific_disclaimers": [
            "Research results are not live.",
            "Only a small blockchain sample was used.",
            "No independently verified attack labels.",
            "No demonstrated quantum advantage.",
            "No production security effectiveness established.",
            "No external actions are performed.",
        ],
    }


def markdown_report(reports, checks_passed):
    research = reports["research"]
    validation = reports["validation"]
    benchmark = reports["benchmark"]["benchmark"]
    supervisor = reports["supervisor"]

    return f"""# Quantum Cyber Defense Arena

## V19 - Multi-Agent Research Release

**Version:** V19.6

**Release status:** RESEARCH_RELEASE_PASS

**Release validation checks:** {checks_passed}

### Research modules

| Version | Component |
|---|---|
| V19.1 | Multi-Agent Architecture |
| V19.2 | Research Agent |
| V19.3 | Validation Agent |
| V19.4 | Benchmark Agent |
| V19.5 | Autonomous Supervisor |
| V19.6 | Research Release |

### Research results

| Metric | Result |
|---|---|
| Research findings | {research.get('findings_count')} |
| Validated findings | {validation.get('findings_validated')} |
| Transaction samples | {benchmark.get('samples')} |
| Spearman correlation | {benchmark.get('spearman')} |
| Top-K overlap | {benchmark.get('top_k_overlap')}/{benchmark.get('top_k')} |
| Completed workflow tasks | {len(supervisor.get('workflow_tasks', []))} |

### Supervisor decision

`{supervisor.get('supervisor_decision')}`

This is an internal research workflow decision,
not authorization for live security responses.

### Agent architecture

The four configured agents use deterministic
rules and saved research artifacts.

The system does not execute LLM-based autonomous
research or perform external security actions.

### Scientific limitations

- Small blockchain-derived sample
- No verified malicious transaction labels
- No independent predictive test set
- Quantum computations used local simulation
- No proven quantum computational advantage
- No production threat-detection effectiveness established
- Artifact verification is not independent peer review

### Integrity

The V19.6 JSON report contains SHA-256 fingerprints
for the five upstream V19 research artifacts.

### Dashboard data

`frontend/public/v19/multi_agent_v19_dashboard.json`

This is a static JSON export. React integration
is a separate development task.

### Next research stage

**V20 - Cyber Digital Twin**
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V19.6 - MULTI-AGENT RESEARCH RELEASE")
    print("=" * 70)

    V19.mkdir(parents=True, exist_ok=True)

    reports = load_reports()

    if len(reports) == len(FILES):
        validate_reports(reports)

        validate_fingerprints(reports)

        validate_agents(reports)

    else:
        check(
            "All upstream reports loaded",
            False,
            f"Loaded {len(reports)} of {len(FILES)}",
        )

    passed = sum(
        item["passed"] for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "RESEARCH_RELEASE_PASS"
        if failed == 0
        else "RESEARCH_RELEASE_FAIL"
    )

    release = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V19.6",
        "module": "Multi-Agent Research Release",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "checks_passed": passed,
        "checks_failed": failed,
        "checks": CHECKS,
        "source_artifacts": source_manifest(),
        "research_type": "deterministic_multi_agent_workflow",
        "llm_enabled": False,
        "external_actions_enabled": False,
        "verified_attack_detection": False,
        "quantum_advantage_demonstrated": False,
        "research_limitations": [
            "Small blockchain-derived transaction sample.",
            "No verified malicious transaction labels.",
            "No independent holdout performance evaluation.",
            "No demonstrated quantum computational advantage.",
            "No autonomous external actions.",
            "No independent scientific peer review.",
        ],
        "outputs": {
            "release_json": str(
                OUTPUT.relative_to(ROOT)
            ),
            "research_markdown": str(
                MARKDOWN.relative_to(ROOT)
            ),
            "dashboard_json": str(
                DASHBOARD.relative_to(ROOT)
            ),
        },
        "next_stage": "V20 Cyber Digital Twin",
    }

    # Save a validation report even if checks fail.
    write_json(OUTPUT, release)

    if failed != 0:
        print()
        print(f"CHECKS PASSED: {passed}")
        print(f"CHECKS FAILED: {failed}")
        print("V19.6 RESULT: RESEARCH_RELEASE_FAIL")
        print(f"REPORT SAVED: {OUTPUT}")
        return 1

    dashboard = dashboard_data(
        reports,
        status,
    )

    write_json(DASHBOARD, dashboard)

    MARKDOWN.write_text(
        markdown_report(reports, passed),
        encoding="utf-8",
    )

    print()
    print("=" * 70)
    print("V19 FINAL RESEARCH RELEASE")
    print("=" * 70)
    print("AGENTS: 4")
    print("WORKFLOW TASKS: 4")
    print(
        "FINDINGS VALIDATED:",
        reports["validation"]["findings_validated"],
    )
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"RELEASE REPORT: {OUTPUT}")
    print(f"RESEARCH DOCUMENT: {MARKDOWN}")
    print(f"DASHBOARD DATA: {DASHBOARD}")
    print()
    print("V19.6 RESULT: RESEARCH_RELEASE_PASS")
    print("=" * 70)
    print(
        "NOTE: Dashboard data exported; "
        "React integration not yet performed."
    )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print()
        print(
            "V19.6 FAILED:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
