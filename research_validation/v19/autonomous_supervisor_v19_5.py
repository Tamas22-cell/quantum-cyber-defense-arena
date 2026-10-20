
"""
QUANTUM CYBER DEFENSE ARENA
V19.5 - AUTONOMOUS RESEARCH SUPERVISOR

Coordinates the validated V19 research workflow.

Inputs:
- V19.1 Multi-Agent Architecture
- V19.2 Research Agent
- V19.3 Validation Agent
- V19.4 Benchmark Agent

Outputs:
- Supervisor decision JSON
- Supervisor research report Markdown

Deterministic, read-only workflow.
No LLM execution or external security actions.
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

SOURCES = {
    "architecture": V19 / "multi_agent_architecture_v19_1_results.json",
    "research": V19 / "research_agent_v19_2_results.json",
    "validation": V19 / "validation_agent_v19_3_results.json",
    "benchmark": V19 / "benchmark_agent_v19_4_results.json",
}

EXPECTED = {
    "architecture": ("V19.1", "ARCHITECTURE_PASS"),
    "research": ("V19.2", "RESEARCH_AGENT_PASS"),
    "validation": ("V19.3", "VALIDATION_AGENT_PASS"),
    "benchmark": ("V19.4", "BENCHMARK_AGENT_PASS"),
}

OUTPUT_JSON = V19 / "autonomous_supervisor_v19_5_results.json"
OUTPUT_MD = V19 / "AUTONOMOUS_SUPERVISOR_V19_5.md"

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
        print(f"       {detail}")

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


def numeric(value):
    if isinstance(value, bool):
        return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    return result if math.isfinite(result) else None


def load_sources():
    reports = {}

    for key, path in SOURCES.items():
        if not check(
            f"Source available: {key}",
            path.is_file(),
            str(path),
        ):
            continue

        try:
            reports[key] = read_json(path)
            check(f"Source JSON readable: {key}", True)

        except (OSError, ValueError) as error:
            check(
                f"Source JSON readable: {key}",
                False,
                str(error),
            )

    return reports


def validate_releases(reports):
    for key, (version, status) in EXPECTED.items():
        report = reports.get(key, {})

        check(
            f"{key}: version verified",
            report.get("version") == version,
        )

        check(
            f"{key}: successful status",
            report.get("status") == status
            and report.get("checks_failed") == 0,
        )

        existing_checks = report.get("checks", [])

        check(
            f"{key}: internal checks consistent",
            isinstance(existing_checks, list)
            and len(existing_checks) > 0
            and all(
                isinstance(item, dict)
                and item.get("passed") is True
                for item in existing_checks
            )
            and len(existing_checks)
            == report.get("checks_passed"),
        )


def validate_workflow(architecture):
    agents = architecture.get("agents", [])
    workflow = architecture.get("workflow", {})
    tasks = workflow.get("tasks", [])

    expected_agents = {
        "research_agent",
        "validation_agent",
        "benchmark_agent",
        "supervisor_agent",
    }

    configured_ids = {
        agent.get("id")
        for agent in agents
        if isinstance(agent, dict)
    }

    check(
        "All four research agents configured",
        configured_ids == expected_agents
        and len(agents) == 4,
    )

    check(
        "External actions disabled",
        architecture.get("external_actions_enabled") is False
        and workflow.get(
            "automatic_external_execution"
        ) is False
        and all(
            isinstance(agent, dict)
            and agent.get("permissions", {}).get(
                "external_actions"
            ) is False
            for agent in agents
        ),
    )

    expected_tasks = {
        "TASK-001": ("research_agent", set()),
        "TASK-002": (
            "validation_agent",
            {"TASK-001"},
        ),
        "TASK-003": (
            "benchmark_agent",
            {"TASK-001"},
        ),
        "TASK-004": (
            "supervisor_agent",
            {"TASK-002", "TASK-003"},
        ),
    }

    actual_tasks = {
        item.get("task_id"): item
        for item in tasks
        if isinstance(item, dict)
    }

    check(
        "Four workflow tasks registered",
        len(tasks) == 4
        and set(actual_tasks) == set(expected_tasks),
    )

    valid_dependencies = (
        len(tasks) == 4
        and set(actual_tasks) == set(expected_tasks)
    )

    if valid_dependencies:
        for task_id, (agent, dependencies) in (
            expected_tasks.items()
        ):
            task = actual_tasks[task_id]

            if (
                task.get("agent") != agent
                or set(task.get("depends_on", []))
                != dependencies
            ):
                valid_dependencies = False

    check(
        "Workflow dependencies correct",
        valid_dependencies,
    )

    check(
        "Human review required for high-impact actions",
        workflow.get(
            "human_review_for_high_impact_actions"
        ) is True,
    )


def validate_research(research, validation):
    findings = research.get("findings", [])

    finding_ids = {
        item.get("finding_id")
        for item in findings
        if isinstance(item, dict)
    }

    check(
        "Seven research findings available",
        isinstance(findings, list)
        and len(findings) == 7
        and len(finding_ids) == 7,
    )

    validated = validation.get("finding_results", [])

    validated_ids = {
        item.get("finding_id")
        for item in validated
        if isinstance(item, dict)
        and item.get("status") == "VALIDATED"
    }

    check(
        "All research findings validated",
        validation.get("findings_total") == 7
        and validation.get("findings_validated") == 7
        and len(validated) == 7
        and finding_ids == validated_ids,
    )

    check(
        "Validation uses current Research Agent output",
        validation.get("research_agent_sha256")
        == sha256_file(SOURCES["research"]),
    )

    check(
        "Validation uses current architecture",
        validation.get("architecture_sha256")
        == sha256_file(SOURCES["architecture"]),
    )

    check(
        "Research Agent external actions disabled",
        research.get("external_actions_enabled") is False
        and validation.get("external_actions_enabled")
        is False,
    )


def validate_benchmark(benchmark):
    data = benchmark.get("benchmark", {})

    if not isinstance(data, dict):
        data = {}

    samples = data.get("samples")
    correlation = numeric(data.get("spearman"))
    k = data.get("top_k")
    overlap = data.get("top_k_overlap")

    check(
        "Benchmark uses positive sample count",
        type(samples) is int and samples >= 10,
    )

    check(
        "Benchmark correlation valid",
        correlation is not None
        and -1 <= correlation <= 1,
    )

    check(
        "Benchmark Top-K result valid",
        type(k) is int
        and type(overlap) is int
        and type(samples) is int
        and 0 <= overlap <= k <= samples,
    )

    check(
        "No quantum advantage claimed",
        data.get("quantum_advantage_demonstrated")
        is False,
    )

    check(
        "Benchmark timing not presented as fair",
        data.get("runtime_comparison_is_fair")
        is False,
    )

    check(
        "Benchmark external actions disabled",
        benchmark.get("external_actions_enabled")
        is False,
    )

    return data


def build_task_results(reports):
    mapping = [
        ("TASK-001", "research", "research_agent"),
        ("TASK-002", "validation", "validation_agent"),
        ("TASK-003", "benchmark", "benchmark_agent"),
    ]

    results = []

    for task_id, key, agent in mapping:
        report = reports[key]

        results.append({
            "task_id": task_id,
            "agent_id": agent,
            "status": "COMPLETED",
            "source_version": report["version"],
            "source_sha256": sha256_file(SOURCES[key]),
        })

    results.append({
        "task_id": "TASK-004",
        "agent_id": "supervisor_agent",
        "status": "COMPLETED",
        "dependencies": [
            "TASK-002",
            "TASK-003",
        ],
    })

    return results


def write_markdown(result):
    benchmark = result.get("benchmark_summary", {})
    decision = result["supervisor_decision"]

    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V19.5 - Autonomous Supervisor",
        "",
        f"**Status:** {result['status']}",
        f"**Decision:** {decision}",
        "",
        "### Agent coordination",
        "",
        "| Agent | Result |",
        "|---|---|",
        "| Research Agent | Validated upstream |",
        "| Validation Agent | Validated upstream |",
        "| Benchmark Agent | Validated upstream |",
        "| Supervisor | Workflow checks passed |",
        "",
        "### Benchmark summary",
        "",
        f"- Samples: {benchmark.get('samples')}",
        f"- Spearman correlation: {benchmark.get('spearman')}",
        f"- Top-K overlap: "
        f"{benchmark.get('top_k_overlap')}/"
        f"{benchmark.get('top_k')}",
        "",
        "### Research decision",
        "",
        "The research artifacts are internally consistent",
        "under the checks implemented by this workflow.",
        "",
        "This does not establish production readiness,",
        "cyberattack detection accuracy or quantum advantage.",
        "",
        "### Operational limitations",
        "",
        "- Deterministic, rule-based supervisor",
        "- No autonomous LLM reasoning",
        "- No external security actions",
        "- No independently verified threat labels",
        "- Small, in-sample blockchain dataset",
        "",
        "### Next stage",
        "",
        "V19.6 - Multi-Agent Research Release",
        "",
    ]

    OUTPUT_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main():
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V19.5 - AUTONOMOUS RESEARCH SUPERVISOR")
    print("=" * 68)

    V19.mkdir(parents=True, exist_ok=True)

    reports = load_sources()

    benchmark_data = {}
    tasks = []

    if len(reports) == len(SOURCES):
        validate_releases(reports)

        validate_workflow(
            reports["architecture"]
        )

        validate_research(
            reports["research"],
            reports["validation"],
        )

        benchmark_data = validate_benchmark(
            reports["benchmark"]
        )

        if all(item["passed"] for item in CHECKS):
            tasks = build_task_results(reports)

    check(
        "All four workflow tasks completed",
        len(tasks) == 4
        and all(
            task.get("status") == "COMPLETED"
            for task in tasks
        ),
    )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "SUPERVISOR_PASS"
        if failed == 0
        else "SUPERVISOR_FAIL"
    )

    decision = (
        "RESEARCH_APPROVED_FOR_RELEASE_VALIDATION"
        if failed == 0
        else "RESEARCH_BLOCKED"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V19.5",
        "module": "Autonomous Research Supervisor",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "supervisor_decision": decision,
        "execution_mode": "deterministic_read_only",
        "llm_enabled": False,
        "external_actions_enabled": False,
        "human_review_required_for_high_impact_actions": True,
        "agents": [
            "research_agent",
            "validation_agent",
            "benchmark_agent",
            "supervisor_agent",
        ],
        "workflow_tasks": tasks,
        "benchmark_summary": benchmark_data,
        "source_fingerprints": {
            key: sha256_file(path)
            for key, path in SOURCES.items()
            if path.is_file()
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "research_limitations": [
            "Research artifacts only.",
            "No independent scientific peer review.",
            "No verified cyberattack labels.",
            "Small blockchain dataset.",
            "No demonstrated quantum advantage.",
            "No external autonomous actions.",
        ],
        "next_stage": "V19.6 Multi-Agent Research Release",
    }

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

    if failed == 0:
        write_markdown(result)

    print()
    print("=" * 68)
    print("V19.5 SUPERVISOR RESULTS")
    print("=" * 68)

    print(f"AGENTS COORDINATED: {len(result['agents'])}")
    print(f"WORKFLOW TASKS COMPLETED: {len(tasks)}")
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"SUPERVISOR DECISION: {decision}")
    print(f"JSON REPORT: {OUTPUT_JSON}")

    if failed == 0:
        print(f"RESEARCH DOCUMENT: {OUTPUT_MD}")

    print(f"V19.5 RESULT: {status}")
    print("=" * 68)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print()
        print(
            "V19.5 FAILED: "
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)
