
"""
QUANTUM CYBER DEFENSE ARENA
V19.2 - AUTONOMOUS RESEARCH AGENT

Evidence-grounded research agent.

Reads:
- V19.1 agent architecture
- V17.5 AI research release
- V18.6 quantum-classical release
- V18.4 comparison
- V18.5 statistical validation

Produces:
- Structured findings with evidence references
- Research limitations
- Agent execution report

Standard library only.
No network access, LLM calls, or external actions.
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

SOURCES = {
    "v19_architecture": V19 / "multi_agent_architecture_v19_1_results.json",
    "v17_release": V17 / "ai_training_research_release_v17_5_results.json",
    "v18_release": V18 / "research_release_v18_6_results.json",
    "v18_comparison": V18 / "quantum_classical_comparison_v18_4_results.json",
    "v18_statistics": V18 / "statistical_validation_v18_5_results.json",
}

EXPECTED = {
    "v19_architecture": ("V19.1", "ARCHITECTURE_PASS"),
    "v17_release": ("V17.5", "RESEARCH_RELEASE_PASS"),
    "v18_release": ("V18.6", "RESEARCH_RELEASE_PASS"),
    "v18_comparison": ("V18.4", "COMPARISON_PASS"),
    "v18_statistics": ("V18.5", "STATISTICAL_VALIDATION_PASS"),
}

OUTPUT_JSON = V19 / "research_agent_v19_2_results.json"
OUTPUT_MD = V19 / "RESEARCH_AGENT_V19_2.md"

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


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as file:
        result = json.load(file)

    if not isinstance(result, dict):
        raise ValueError(
            f"Expected JSON object: {path.name}"
        )

    return result


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def finite_number(value):
    if isinstance(value, bool):
        return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(result):
        return None

    return result


def evidence(source, path):
    return {
        "source": source,
        "json_path": path,
        "file": str(SOURCES[source].relative_to(ROOT)),
    }


def add_finding(
    findings,
    finding_id,
    title,
    statement,
    evidence_items,
    confidence="artifact_verified",
):
    findings.append({
        "finding_id": finding_id,
        "title": title,
        "statement": statement,
        "confidence_scope": confidence,
        "evidence": evidence_items,
    })


def validate_sources():
    reports = {}

    for key, path in SOURCES.items():
        if not check(
            f"Source exists: {key}",
            path.is_file(),
            str(path),
        ):
            continue

        try:
            reports[key] = read_json(path)
            check(f"Readable JSON: {key}", True)
        except (OSError, ValueError) as exc:
            check(
                f"Readable JSON: {key}",
                False,
                str(exc),
            )

    for key, (version, status) in EXPECTED.items():
        report = reports.get(key)

        check(
            f"Validated release: {key}",
            report is not None
            and report.get("version") == version
            and report.get("status") == status
            and report.get("checks_failed") == 0,
        )

    return reports


def validate_architecture(reports):
    architecture = reports.get("v19_architecture", {})

    agents = architecture.get("agents", [])

    check(
        "Research Agent configured",
        isinstance(agents, list)
        and any(
            agent.get("id") == "research_agent"
            and agent.get("permissions", {}).get(
                "external_actions"
            ) is False
            for agent in agents
            if isinstance(agent, dict)
        ),
    )

    source_manifest = architecture.get(
        "source_artifacts", {}
    )

    for key in (
        "v17_release",
        "v18_release",
        "v18_comparison",
        "v18_statistics",
    ):
        expected_hash = source_manifest.get(
            key, {}
        ).get("sha256")

        actual_hash = (
            sha256(SOURCES[key])
            if SOURCES[key].is_file()
            else None
        )

        check(
            f"V19.1 source fingerprint: {key}",
            expected_hash is not None
            and expected_hash == actual_hash,
        )


def validate_metrics(reports):
    v17 = reports["v17_release"].get(
        "research_results", {}
    )

    v18 = reports["v18_release"].get(
        "dataset", {}
    )

    comparison = reports["v18_comparison"].get(
        "comparison", {}
    )

    statistics_report = reports["v18_statistics"]

    statistical_spearman = statistics_report.get(
        "spearman", {}
    )

    statistical_top = statistics_report.get(
        "top_k", {}
    )

    samples = v18.get("samples")
    features = v18.get("feature_count")

    check(
        "Consistent research sample count",
        isinstance(samples, int)
        and samples > 0
        and samples == v17.get("v17_2_samples")
        and samples == reports[
            "v18_comparison"
        ].get("dataset", {}).get("samples"),
    )

    check(
        "Research feature count valid",
        isinstance(features, int)
        and features > 0,
    )

    rho = finite_number(
        comparison.get("spearman_rank_correlation")
    )

    rho_statistics = finite_number(
        statistical_spearman.get(
            "observed_correlation"
        )
    )

    check(
        "Rank correlation consistent",
        rho is not None
        and rho_statistics is not None
        and -1.0 <= rho <= 1.0
        and abs(rho - rho_statistics) <= 1e-5,
    )

    k = comparison.get("top_k")
    overlap = comparison.get("top_k_overlap")

    check(
        "Top-K comparison consistent",
        isinstance(k, int)
        and isinstance(overlap, int)
        and 0 <= overlap <= k <= samples
        and statistical_top.get("k") == k
        and statistical_top.get(
            "observed_overlap"
        ) == overlap,
    )

    lower = finite_number(
        statistical_spearman.get(
            "bootstrap", {}
        ).get("ci_lower")
    )

    upper = finite_number(
        statistical_spearman.get(
            "bootstrap", {}
        ).get("ci_upper")
    )

    check(
        "Bootstrap interval valid",
        lower is not None
        and upper is not None
        and -1 <= lower <= upper <= 1,
    )

    permutation_p = finite_number(
        statistical_spearman.get(
            "permutation", {}
        ).get("p_value_two_sided")
    )

    top_p = finite_number(
        statistical_top.get(
            "hypergeometric_tail_p_value"
        )
    )

    check(
        "Statistical p-values valid",
        permutation_p is not None
        and top_p is not None
        and 0 <= permutation_p <= 1
        and 0 <= top_p <= 1,
    )

    return all(item["passed"] for item in CHECKS)


def produce_findings(reports):
    findings = []

    v17 = reports["v17_release"]
    v18 = reports["v18_release"]
    comparison_report = reports["v18_comparison"]
    statistical_report = reports["v18_statistics"]

    v17_results = v17["research_results"]
    v18_dataset = v18["dataset"]
    comparison = comparison_report["comparison"]

    stats = statistical_report["spearman"]
    top = statistical_report["top_k"]

    samples = v18_dataset["samples"]
    features = v18_dataset["feature_count"]

    add_finding(
        findings,
        "RESEARCH-001",
        "AI research dataset",
        (
            f"The research used {samples} blockchain-derived "
            f"transaction samples with {features} numerical features."
        ),
        [
            evidence(
                "v18_release",
                "$.dataset.samples",
            ),
            evidence(
                "v18_release",
                "$.dataset.feature_count",
            ),
        ],
    )

    add_finding(
        findings,
        "RESEARCH-002",
        "Classical AI training",
        (
            "The Isolation Forest research model was trained "
            f"on {v17_results['v17_2_samples']} samples. "
            f"It flagged {v17_results['v17_2_training_anomalies']} "
            "statistical anomalies in its training data."
        ),
        [
            evidence(
                "v17_release",
                "$.research_results.v17_2_samples",
            ),
            evidence(
                "v17_release",
                "$.research_results.v17_2_training_anomalies",
            ),
        ],
    )

    rho = comparison["spearman_rank_correlation"]

    add_finding(
        findings,
        "RESEARCH-003",
        "Cross-method rank association",
        (
            "The classical and simulated quantum novelty "
            f"rankings had a Spearman correlation of {rho}. "
            "This is a ranking association, not detection accuracy."
        ),
        [
            evidence(
                "v18_comparison",
                "$.comparison.spearman_rank_correlation",
            ),
        ],
    )

    k = comparison["top_k"]
    overlap = comparison["top_k_overlap"]

    add_finding(
        findings,
        "RESEARCH-004",
        "Top-K overlap",
        (
            f"The two methods shared {overlap} of their "
            f"top {k} highest-scoring transaction samples. "
            "Overlap is not a ground-truth accuracy measure."
        ),
        [
            evidence(
                "v18_comparison",
                "$.comparison.top_k",
            ),
            evidence(
                "v18_comparison",
                "$.comparison.top_k_overlap",
            ),
        ],
    )

    lower = stats["bootstrap"]["ci_lower"]
    upper = stats["bootstrap"]["ci_upper"]

    add_finding(
        findings,
        "RESEARCH-005",
        "Bootstrap uncertainty",
        (
            "The exploratory paired-bootstrap 95% interval "
            f"for rank correlation was [{lower}, {upper}]. "
            "Its interpretation depends on sampling assumptions."
        ),
        [
            evidence(
                "v18_statistics",
                "$.spearman.bootstrap.ci_lower",
            ),
            evidence(
                "v18_statistics",
                "$.spearman.bootstrap.ci_upper",
            ),
        ],
        "exploratory_statistical_result",
    )

    permutation_p = (
        stats["permutation"]["p_value_two_sided"]
    )

    top_p = top["hypergeometric_tail_p_value"]

    add_finding(
        findings,
        "RESEARCH-006",
        "Exploratory significance tests",
        (
            f"The permutation-test p-value was {permutation_p}, "
            f"and the exact Top-K overlap p-value was {top_p}. "
            "They test different null models and do not prove "
            "cyberattack detection or quantum advantage."
        ),
        [
            evidence(
                "v18_statistics",
                "$.spearman.permutation.p_value_two_sided",
            ),
            evidence(
                "v18_statistics",
                "$.top_k.hypergeometric_tail_p_value",
            ),
        ],
        "exploratory_statistical_result",
    )

    add_finding(
        findings,
        "RESEARCH-007",
        "Research validation",
        (
            f"V17.5 passed {v17['checks_passed']} "
            "release checks, and V18.6 passed "
            f"{v18['checks_passed']} release checks. "
            "These establish artifact-level validation, "
            "not operational security effectiveness."
        ),
        [
            evidence(
                "v17_release",
                "$.checks_passed",
            ),
            evidence(
                "v18_release",
                "$.checks_passed",
            ),
        ],
    )

    return findings


def render_markdown(findings, status, passed, failed):
    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V19.2 - Research Agent",
        "",
        f"**Execution status:** {status}",
        f"**Checks:** {passed} passed, {failed} failed",
        "",
        "### Evidence-grounded findings",
        "",
    ]

    for finding in findings:
        lines.extend([
            f"#### {finding['finding_id']} - {finding['title']}",
            "",
            finding["statement"],
            "",
            "**Evidence:**",
            "",
        ])

        for source in finding["evidence"]:
            lines.append(
                f"- `{source['file']}` — `{source['json_path']}`"
            )

        lines.append("")

    lines.extend([
        "### Scientific limitations",
        "",
        "- Small transaction dataset",
        "- No verified malicious-transaction labels",
        "- In-sample exploratory results",
        "- Possible dependence between observations",
        "- Qiskit used local simulation, not quantum hardware",
        "- No measured quantum computational advantage",
        "- No demonstrated production threat-detection ability",
        "- Research Agent is deterministic, not LLM-based",
        "",
        "### Next stage",
        "",
        "V19.3 - Validation Agent",
        "",
    ])

    return "\n".join(lines)


def main():
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V19.2 - RESEARCH AGENT")
    print("=" * 68)

    V19.mkdir(
        parents=True,
        exist_ok=True,
    )

    reports = validate_sources()

    if len(reports) == len(SOURCES):
        validate_architecture(reports)

    if (
        len(reports) == len(SOURCES)
        and all(item["passed"] for item in CHECKS)
    ):
        validate_metrics(reports)

    inputs_valid = (
        len(reports) == len(SOURCES)
        and all(item["passed"] for item in CHECKS)
    )

    findings = (
        produce_findings(reports)
        if inputs_valid
        else []
    )

    check(
        "Evidence-grounded findings generated",
        len(findings) == 7,
    )

    check(
        "Every finding contains source references",
        bool(findings)
        and all(
            finding.get("evidence")
            and all(
                SOURCES.get(reference["source"])
                for reference in finding["evidence"]
            )
            for finding in findings
        ),
    )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "RESEARCH_AGENT_PASS"
        if failed == 0
        else "RESEARCH_AGENT_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V19.2",
        "module": "Research Agent",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "agent_id": "research_agent",
        "agent_type": "deterministic_evidence_analysis",
        "llm_enabled": False,
        "external_actions_enabled": False,
        "source_artifacts": {
            key: {
                "file": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
            }
            for key, path in SOURCES.items()
            if path.is_file()
        },
        "findings": findings,
        "findings_count": len(findings),
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "scientific_limitations": [
            "Research sample contains only 20 transactions.",
            "No verified malicious transaction labels.",
            "No independent threat-detection test set.",
            "Statistical tests rely on their null assumptions.",
            "No physical quantum hardware was used.",
            "No quantum advantage demonstrated.",
            "Agent does not make autonomous external decisions.",
        ],
        "next_stage": "V19.3 Validation Agent",
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
        OUTPUT_MD.write_text(
            render_markdown(
                findings,
                status,
                passed,
                failed,
            ),
            encoding="utf-8",
        )

    print()
    print("=" * 68)
    print("V19.2 RESEARCH AGENT RESULTS")
    print("=" * 68)
    print(f"FINDINGS GENERATED: {len(findings)}")
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {OUTPUT_JSON}")

    if failed == 0:
        print(f"RESEARCH DOCUMENT: {OUTPUT_MD}")

    print(f"V19.2 RESULT: {status}")
    print("=" * 68)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print()
        print(
            f"V19.2 FAILED: "
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)
