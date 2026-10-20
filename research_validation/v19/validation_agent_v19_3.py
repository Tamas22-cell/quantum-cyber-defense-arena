
"""
QUANTUM CYBER DEFENSE ARENA
V19.3 - VALIDATION AGENT

Validates the seven V19.2 research findings.

Checks:
- Research Agent output and architecture
- Trusted source files and SHA-256 fingerprints
- Exact evidence references and JSON paths
- Numerical claims against source values
- Scientific scope and limitations
- No external execution permissions

Standard library only.
No LLM, API key or network access.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V17 = ROOT / "research_validation" / "v17"
V18 = ROOT / "research_validation" / "v18"
V19 = ROOT / "research_validation" / "v19"

ARCH_FILE = V19 / "multi_agent_architecture_v19_1_results.json"
RESEARCH_FILE = V19 / "research_agent_v19_2_results.json"

SOURCE_FILES = {
    "v17_release": V17 / "ai_training_research_release_v17_5_results.json",
    "v18_release": V18 / "research_release_v18_6_results.json",
    "v18_comparison": V18 / "quantum_classical_comparison_v18_4_results.json",
    "v18_statistics": V18 / "statistical_validation_v18_5_results.json",
}

OUTPUT_JSON = V19 / "validation_agent_v19_3_results.json"
OUTPUT_MD = V19 / "VALIDATION_AGENT_V19_3.md"

CHECKS = []
FINDING_RESULTS = []


def check(name, condition, detail=""):
    passed = bool(condition)

    CHECKS.append({
        "name": name,
        "passed": passed,
        "detail": str(detail),
    })

    print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if not passed and detail:
        print(f"       {detail}")

    return passed


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(f"Missing file: {path}")

    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path.name}")

    return data


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def get_json_value(data, path):
    """
    Resolve the simple $.name.child JSON paths
    produced by the V19.2 Research Agent.
    """
    if not isinstance(path, str) or not path.startswith("$."):
        raise ValueError(f"Unsupported JSON path: {path}")

    current = data

    for part in path[2:].split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f"Missing evidence field: {path}")

        current = current[part]

    if isinstance(current, (dict, list)):
        raise ValueError(f"Evidence is not a scalar: {path}")

    return current


def expected_findings(sources):
    v17 = sources["v17_release"]["research_results"]
    v18 = sources["v18_release"]
    comparison = sources["v18_comparison"]["comparison"]
    statistics = sources["v18_statistics"]

    samples = v18["dataset"]["samples"]
    features = v18["dataset"]["feature_count"]
    rho = comparison["spearman_rank_correlation"]
    k = comparison["top_k"]
    overlap = comparison["top_k_overlap"]

    ci = statistics["spearman"]["bootstrap"]
    p = statistics["spearman"]["permutation"]["p_value_two_sided"]
    top_p = statistics["top_k"]["hypergeometric_tail_p_value"]

    return {
        "RESEARCH-001": {
            "title": "AI research dataset",
            "statement": (
                f"The research used {samples} blockchain-derived "
                f"transaction samples with {features} numerical features."
            ),
            "evidence": [
                ("v18_release", "$.dataset.samples"),
                ("v18_release", "$.dataset.feature_count"),
            ],
        },
        "RESEARCH-002": {
            "title": "Classical AI training",
            "statement": (
                "The Isolation Forest research model was trained "
                f"on {v17['v17_2_samples']} samples. "
                f"It flagged {v17['v17_2_training_anomalies']} "
                "statistical anomalies in its training data."
            ),
            "evidence": [
                ("v17_release", "$.research_results.v17_2_samples"),
                (
                    "v17_release",
                    "$.research_results.v17_2_training_anomalies",
                ),
            ],
        },
        "RESEARCH-003": {
            "title": "Cross-method rank association",
            "statement": (
                "The classical and simulated quantum novelty "
                f"rankings had a Spearman correlation of {rho}. "
                "This is a ranking association, not detection accuracy."
            ),
            "evidence": [
                (
                    "v18_comparison",
                    "$.comparison.spearman_rank_correlation",
                ),
            ],
        },
        "RESEARCH-004": {
            "title": "Top-K overlap",
            "statement": (
                f"The two methods shared {overlap} of their "
                f"top {k} highest-scoring transaction samples. "
                "Overlap is not a ground-truth accuracy measure."
            ),
            "evidence": [
                ("v18_comparison", "$.comparison.top_k"),
                ("v18_comparison", "$.comparison.top_k_overlap"),
            ],
        },
        "RESEARCH-005": {
            "title": "Bootstrap uncertainty",
            "statement": (
                "The exploratory paired-bootstrap 95% interval "
                f"for rank correlation was "
                f"[{ci['ci_lower']}, {ci['ci_upper']}]. "
                "Its interpretation depends on sampling assumptions."
            ),
            "evidence": [
                ("v18_statistics", "$.spearman.bootstrap.ci_lower"),
                ("v18_statistics", "$.spearman.bootstrap.ci_upper"),
            ],
        },
        "RESEARCH-006": {
            "title": "Exploratory significance tests",
            "statement": (
                f"The permutation-test p-value was {p}, "
                f"and the exact Top-K overlap p-value was {top_p}. "
                "They test different null models and do not prove "
                "cyberattack detection or quantum advantage."
            ),
            "evidence": [
                (
                    "v18_statistics",
                    "$.spearman.permutation.p_value_two_sided",
                ),
                (
                    "v18_statistics",
                    "$.top_k.hypergeometric_tail_p_value",
                ),
            ],
        },
        "RESEARCH-007": {
            "title": "Research validation",
            "statement": (
                f"V17.5 passed {sources['v17_release']['checks_passed']} "
                "release checks, and V18.6 passed "
                f"{v18['checks_passed']} release checks. "
                "These establish artifact-level validation, "
                "not operational security effectiveness."
            ),
            "evidence": [
                ("v17_release", "$.checks_passed"),
                ("v18_release", "$.checks_passed"),
            ],
        },
    }


def validate_finding(finding, expected, sources):
    finding_id = finding["finding_id"]
    failures = []
    resolved = []

    if finding.get("title") != expected["title"]:
        failures.append("Title differs from expected finding")

    if finding.get("statement") != expected["statement"]:
        failures.append("Statement differs from source-derived claim")

    references = finding.get("evidence", [])

    if not isinstance(references, list):
        references = []
        failures.append("Evidence must be a list")

    expected_refs = expected["evidence"]

    actual_refs = [
        (
            item.get("source"),
            item.get("json_path"),
        )
        for item in references
        if isinstance(item, dict)
    ]

    if actual_refs != expected_refs:
        failures.append("Evidence references differ from expected")

    for item in references:
        if not isinstance(item, dict):
            failures.append("Malformed evidence item")
            continue

        source_key = item.get("source")
        json_path = item.get("json_path")

        if source_key not in sources:
            failures.append(f"Unknown source: {source_key}")
            continue

        expected_file = str(
            SOURCE_FILES[source_key].relative_to(ROOT)
        )

        if item.get("file") != expected_file:
            failures.append(f"Wrong evidence file: {source_key}")

        try:
            value = get_json_value(
                sources[source_key],
                json_path,
            )

            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError("Non-finite evidence value")

            resolved.append({
                "source": source_key,
                "json_path": json_path,
                "value": value,
            })

        except (ValueError, KeyError, TypeError) as error:
            failures.append(str(error))

    passed = len(failures) == 0

    check(
        f"Finding {finding_id} supported by sources",
        passed,
        "; ".join(failures),
    )

    return {
        "finding_id": finding_id,
        "title": finding.get("title"),
        "status": "VALIDATED" if passed else "REJECTED",
        "evidence_values": resolved,
        "issues": failures,
    }


def validate_sources(architecture, research, sources):
    check(
        "V19.1 architecture PASS",
        architecture.get("version") == "V19.1"
        and architecture.get("status") == "ARCHITECTURE_PASS"
        and architecture.get("checks_failed") == 0,
    )

    check(
        "V19.2 research agent PASS",
        research.get("version") == "V19.2"
        and research.get("status") == "RESEARCH_AGENT_PASS"
        and research.get("checks_failed") == 0,
    )

    check(
        "External agent actions disabled",
        architecture.get("external_actions_enabled") is False
        and research.get("external_actions_enabled") is False,
    )

    configured_agents = architecture.get("agents", [])

    check(
        "Validation Agent registered in architecture",
        any(
            isinstance(agent, dict)
            and agent.get("id") == "validation_agent"
            and agent.get("permissions", {}).get(
                "external_actions"
            ) is False
            for agent in configured_agents
        ),
    )

    source_manifest = architecture.get("source_artifacts", {})
    research_manifest = research.get("source_artifacts", {})

    for key, path in SOURCE_FILES.items():
        digest = sha256_file(path)

        check(
            f"Architecture SHA-256 matches: {key}",
            source_manifest.get(key, {}).get("sha256") == digest,
        )

        check(
            f"Research Agent SHA-256 matches: {key}",
            research_manifest.get(key, {}).get("sha256") == digest,
        )

    expected_statuses = {
        "v17_release": "RESEARCH_RELEASE_PASS",
        "v18_release": "RESEARCH_RELEASE_PASS",
        "v18_comparison": "COMPARISON_PASS",
        "v18_statistics": "STATISTICAL_VALIDATION_PASS",
    }

    for key, expected_status in expected_statuses.items():
        report = sources[key]

        check(
            f"Upstream release validated: {key}",
            report.get("status") == expected_status
            and report.get("checks_failed") == 0,
        )

    check(
        "V18 and V17 samples consistent",
        sources["v18_release"].get(
            "dataset", {}
        ).get("samples")
        == sources["v17_release"].get(
            "research_results", {}
        ).get("v17_2_samples"),
    )


def write_markdown(results, passed, failed, status):
    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V19.3 - Validation Agent",
        "",
        f"**Status:** {status}",
        f"**Checks passed:** {passed}",
        f"**Checks failed:** {failed}",
        "",
        "### Research finding validation",
        "",
        "| Finding | Result |",
        "|---|---|",
    ]

    for item in results:
        lines.append(
            f"| {item['finding_id']} | {item['status']} |"
        )

    lines.extend([
        "",
        "### Validation scope",
        "",
        "This agent checks file hashes, evidence paths,",
        "source values and exact deterministic claim text.",
        "",
        "It does not provide independent scientific peer review.",
        "It does not verify cyberattack detection accuracy.",
        "It does not establish quantum advantage.",
        "",
        "### Next stage",
        "",
        "V19.4 - Benchmark Agent",
        "",
    ])

    OUTPUT_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main():
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V19.3 - VALIDATION AGENT")
    print("=" * 68)

    V19.mkdir(parents=True, exist_ok=True)

    architecture = load_json(ARCH_FILE)
    research = load_json(RESEARCH_FILE)

    sources = {
        key: load_json(path)
        for key, path in SOURCE_FILES.items()
    }

    validate_sources(
        architecture,
        research,
        sources,
    )

    findings = research.get("findings", [])
    expected = expected_findings(sources)

    valid_structure = (
        isinstance(findings, list)
        and len(findings) == 7
        and all(
            isinstance(item, dict)
            and isinstance(item.get("finding_id"), str)
            for item in findings
        )
    )

    check(
        "Seven research findings available",
        valid_structure,
    )

    check(
        "Research finding IDs unique",
        valid_structure
        and len({
            item["finding_id"] for item in findings
        }) == len(findings),
    )

    check(
        "Expected finding IDs present",
        valid_structure
        and {
            item["finding_id"] for item in findings
        } == set(expected),
    )

    if valid_structure:
        for finding in findings:
            finding_id = finding["finding_id"]

            if finding_id in expected:
                result = validate_finding(
                    finding,
                    expected[finding_id],
                    sources,
                )
            else:
                check(
                    f"Unexpected finding: {finding_id}",
                    False,
                )
                result = {
                    "finding_id": finding_id,
                    "status": "REJECTED",
                    "issues": ["Unexpected finding ID"],
                }

            FINDING_RESULTS.append(result)

    validated_count = sum(
        item["status"] == "VALIDATED"
        for item in FINDING_RESULTS
    )

    check(
        "All seven research findings validated",
        validated_count == 7
        and len(FINDING_RESULTS) == 7,
    )

    passed = sum(
        item["passed"] for item in CHECKS
    )
    failed = len(CHECKS) - passed

    status = (
        "VALIDATION_AGENT_PASS"
        if failed == 0
        else "VALIDATION_AGENT_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V19.3",
        "module": "Validation Agent",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "agent_id": "validation_agent",
        "agent_type": "deterministic_evidence_validation",
        "llm_enabled": False,
        "external_actions_enabled": False,
        "research_agent_sha256": sha256_file(RESEARCH_FILE),
        "architecture_sha256": sha256_file(ARCH_FILE),
        "findings_total": len(findings),
        "findings_validated": validated_count,
        "finding_results": FINDING_RESULTS,
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "limitations": [
            "Source consistency is not independent peer review.",
            "Exact claim-text matching assumes V19.2 templates.",
            "No verified malicious transaction labels.",
            "Only 20 blockchain transactions were studied.",
            "No physical quantum hardware was used.",
            "No operational threat-detection accuracy proven.",
            "No quantum advantage demonstrated.",
        ],
        "next_stage": "V19.4 Benchmark Agent",
    }

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            result,
            handle,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

    if failed == 0:
        write_markdown(
            FINDING_RESULTS,
            passed,
            failed,
            status,
        )

    print()
    print("=" * 68)
    print("V19.3 VALIDATION AGENT RESULTS")
    print("=" * 68)
    print(f"FINDINGS CHECKED: {len(findings)}")
    print(f"FINDINGS VALIDATED: {validated_count}")
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {OUTPUT_JSON}")

    if failed == 0:
        print(f"RESEARCH DOCUMENT: {OUTPUT_MD}")

    print(f"V19.3 RESULT: {status}")
    print("=" * 68)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print()
        print(
            f"V19.3 FAILED: "
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)
