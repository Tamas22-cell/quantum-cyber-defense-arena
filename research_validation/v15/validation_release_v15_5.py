
"""
QUANTUM CYBER DEFENSE ARENA
V15.5 - VALIDATION & RELEASE

Checks:
- V15.1 Threat Orchestrator results
- V15.2 Multi-Agent decisions
- V15.3 Response Simulation
- V15.4 dashboard JSON exports
- Event ID consistency
- Risk and priority consistency
- Simulated response safety
- React component integration

All checks use saved research simulation results.

No external API calls, security responses,
or Git operations are performed.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "15.5.0"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FRONTEND = ROOT / "frontend"

OUTPUT_FILE = HERE / "validation_release_v15_5_results.json"

FILENAMES = {
    "v15_1": "threat_orchestrator_v15_1_results.json",
    "v15_2": "multi_agent_decision_v15_2_results.json",
    "v15_3": "autonomous_response_v15_3_results.json",
}

EXPECTED_VERSIONS = {
    "v15_1": "15.1.0",
    "v15_2": "15.2.0",
    "v15_3": "15.3.0",
}

EXPECTED_ACTIONS = {
    "P1": "ESCALATE_CRITICAL",
    "P2": "QUEUE_HIGH_PRIORITY",
    "P3": "REQUEST_MANUAL_REVIEW",
    "P4": "CONTINUE_MONITORING",
}

VALID_DECISIONS = {"NORMAL", "REVIEW", "ANOMALY"}

CHECKS: list[dict[str, Any]] = []


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def record(
    name: str,
    passed: bool,
    detail: str,
) -> None:
    CHECKS.append({
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "detail": detail,
    })

    symbol = "PASS" if passed else "FAIL"

    print(f"[{symbol}] {name}")

    if not passed:
        print(f"       {detail}")


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(
        path.is_file(),
        f"Missing file: {path}",
    )

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    require(
        isinstance(data, dict),
        f"Invalid JSON object: {path.name}",
    )

    return data


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_structure(
    key: str,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:

    require(
        payload.get("version") == EXPECTED_VERSIONS[key],
        f"{key}: unexpected version",
    )

    require(
        payload.get("mode") == "RESEARCH_SIMULATION",
        f"{key}: invalid execution mode",
    )

    array_name = (
        "response_plans"
        if key == "v15_3"
        else "events"
    )

    rows = payload.get(array_name)

    require(
        isinstance(rows, list) and len(rows) > 0,
        f"{key}: missing or empty {array_name}",
    )

    require(
        all(isinstance(row, dict) for row in rows),
        f"{key}: invalid row object",
    )

    event_ids = [row.get("event_id") for row in rows]

    require(
        all(
            isinstance(event_id, str) and event_id
            for event_id in event_ids
        ),
        f"{key}: invalid event ID",
    )

    require(
        len(event_ids) == len(set(event_ids)),
        f"{key}: duplicate event IDs",
    )

    return rows


def validate_orchestrator(
    rows: list[dict[str, Any]],
) -> None:

    for row in rows:
        event_id = row["event_id"]

        classical = row.get("classical_score")
        quantum = row.get("quantum_score")
        fusion = row.get("fusion_score")
        risk = row.get("risk_score")

        for name, value in (
            ("classical", classical),
            ("quantum", quantum),
            ("fusion", fusion),
        ):
            require(
                type(value) in (int, float)
                and math.isfinite(value)
                and 0 <= value <= 1,
                f"{event_id}: invalid {name} score",
            )

        require(
            type(risk) is int and 0 <= risk <= 100,
            f"{event_id}: invalid risk score",
        )

        expected_classical = (
            "ANOMALY" if classical >= 0.55 else "NORMAL"
        )

        expected_quantum = (
            "ANOMALY" if quantum >= 0.55 else "NORMAL"
        )

        require(
            row.get("classical_decision")
            == expected_classical,
            f"{event_id}: incorrect classical decision",
        )

        require(
            row.get("quantum_decision")
            == expected_quantum,
            f"{event_id}: incorrect quantum decision",
        )

        agreement = (
            expected_classical == expected_quantum
        )

        require(
            row.get("model_agreement") is agreement,
            f"{event_id}: incorrect agreement flag",
        )

        expected_hybrid = (
            expected_classical if agreement else "REVIEW"
        )

        require(
            row.get("hybrid_decision") == expected_hybrid,
            f"{event_id}: incorrect hybrid decision",
        )

        expected_fusion = round(
            0.5 * classical + 0.5 * quantum,
            4,
        )

        require(
            abs(fusion - expected_fusion) <= 0.00011,
            f"{event_id}: incorrect fusion score",
        )

        require(
            risk == round(fusion * 100),
            f"{event_id}: incorrect risk conversion",
        )

        if expected_hybrid == "NORMAL":
            priority = "P4"
        elif expected_hybrid == "REVIEW":
            priority = "P3"
        elif risk >= 80:
            priority = "P1"
        else:
            priority = "P2"

        require(
            row.get("priority") == priority,
            f"{event_id}: incorrect priority",
        )

        require(
            row.get("mode") == "RESEARCH_SIMULATION",
            f"{event_id}: invalid event mode",
        )


def validate_decisions(
    source_rows: list[dict[str, Any]],
    decision_rows: list[dict[str, Any]],
) -> None:

    for source, decision in zip(
        source_rows,
        decision_rows,
    ):
        event_id = source["event_id"]

        require(
            decision.get("risk_score")
            == source["risk_score"],
            f"{event_id}: V15.2 risk mismatch",
        )

        require(
            decision.get("hybrid_decision")
            == source["hybrid_decision"],
            f"{event_id}: V15.2 hybrid mismatch",
        )

        require(
            decision.get("final_decision")
            == source["hybrid_decision"],
            f"{event_id}: unexpected final decision",
        )

        require(
            decision.get("final_priority")
            == source["priority"],
            f"{event_id}: unexpected final priority",
        )

        require(
            decision.get("manual_review_required")
            is (source["hybrid_decision"] == "REVIEW"),
            f"{event_id}: review rule mismatch",
        )

        expected_consensus = (
            "UNANIMOUS_"
            + source["hybrid_decision"]
        )

        require(
            decision.get("consensus")
            == expected_consensus,
            f"{event_id}: unexpected consensus",
        )

        for assessment_name in (
            "threat_assessment",
            "investigation_assessment",
            "decision_assessment",
        ):
            assessment = decision.get(assessment_name)

            require(
                isinstance(assessment, dict),
                f"{event_id}: missing {assessment_name}",
            )

            require(
                assessment.get("event_id") == event_id,
                f"{event_id}: wrong assessment event ID",
            )

        require(
            decision.get("mode")
            == "RESEARCH_SIMULATION",
            f"{event_id}: invalid V15.2 mode",
        )


def validate_responses(
    decision_rows: list[dict[str, Any]],
    response_rows: list[dict[str, Any]],
) -> None:

    for decision, response in zip(
        decision_rows,
        response_rows,
    ):
        event_id = decision["event_id"]
        priority = decision["final_priority"]

        require(
            priority in EXPECTED_ACTIONS,
            f"{event_id}: unknown priority",
        )

        require(
            response.get("decision")
            == decision["final_decision"],
            f"{event_id}: response decision mismatch",
        )

        require(
            response.get("priority") == priority,
            f"{event_id}: response priority mismatch",
        )

        require(
            response.get("risk_score")
            == decision["risk_score"],
            f"{event_id}: response risk mismatch",
        )

        require(
            response.get("planned_action")
            == EXPECTED_ACTIONS[priority],
            f"{event_id}: unsafe or incorrect action",
        )

        approval_required = priority != "P4"

        require(
            response.get("approval_required")
            is approval_required,
            f"{event_id}: incorrect approval flag",
        )

        expected_status = (
            "AWAITING_HUMAN_APPROVAL"
            if approval_required
            else "SIMULATED_MONITORING"
        )

        require(
            response.get("response_status")
            == expected_status,
            f"{event_id}: response status mismatch",
        )

        require(
            response.get("external_execution") is False,
            f"{event_id}: external execution detected",
        )

        require(
            response.get("simulated_execution")
            is (not approval_required),
            f"{event_id}: simulated execution mismatch",
        )

        require(
            response.get("policy_validated") is True,
            f"{event_id}: response policy failed",
        )

        require(
            response.get("mode")
            == "RESEARCH_SIMULATION",
            f"{event_id}: invalid V15.3 mode",
        )

        audit = response.get("audit_trail")

        require(
            isinstance(audit, list) and len(audit) >= 5,
            f"{event_id}: missing audit trail",
        )

        require(
            all(
                isinstance(entry, dict)
                and entry.get("event_id") == event_id
                for entry in audit
            ),
            f"{event_id}: invalid audit entries",
        )


def validate_summary(
    source: dict[str, Any],
    decisions: dict[str, Any],
    responses: dict[str, Any],
    first: list[dict[str, Any]],
    second: list[dict[str, Any]],
    third: list[dict[str, Any]],
) -> None:

    for label, payload in (
        ("V15.1", source),
        ("V15.2", decisions),
        ("V15.3", responses),
    ):
        summary = payload.get("summary")

        require(
            isinstance(summary, dict),
            f"{label}: missing summary",
        )

        require(
            summary.get("total_events") == len(first),
            f"{label}: incorrect total event count",
        )

    counts_1 = Counter(
        row["hybrid_decision"] for row in first
    )

    counts_2 = Counter(
        row["final_decision"] for row in second
    )

    counts_3 = Counter(
        row["planned_action"] for row in third
    )

    for decision in VALID_DECISIONS:
        require(
            source["summary"]["decisions"].get(decision, 0)
            == counts_1[decision],
            f"V15.1: wrong {decision} count",
        )

        require(
            decisions["summary"]["decisions"].get(
                decision, 0
            )
            == counts_2[decision],
            f"V15.2: wrong {decision} count",
        )

    for priority, action in EXPECTED_ACTIONS.items():
        require(
            responses["summary"]["actions"].get(action, 0)
            == counts_3[action],
            f"V15.3: wrong count for {priority}",
        )

    expected_approval = sum(
        row["approval_required"] for row in third
    )

    require(
        responses["summary"]["human_approval_required"]
        == expected_approval,
        "V15.3: incorrect approval count",
    )

    require(
        responses["summary"]["external_actions_executed"]
        == 0,
        "V15.3: external actions count is not zero",
    )


def validate_frontend_files() -> None:

    destination = FRONTEND / "public" / "v15"

    for key, filename in FILENAMES.items():

        source = HERE / filename
        exported = destination / filename

        require(
            exported.is_file(),
            f"Missing frontend export: {filename}",
        )

        require(
            digest(source) == digest(exported),
            f"Frontend copy differs: {filename}",
        )

    app = FRONTEND / "src" / "App.tsx"

    component = (
        FRONTEND
        / "src"
        / "components"
        / "LiveCommandCenterV15_4.tsx"
    )

    require(
        app.is_file(),
        "App.tsx was not found",
    )

    require(
        component.is_file(),
        "V15.4 component was not found",
    )

    app_text = app.read_text(encoding="utf-8")

    component_text = component.read_text(
        encoding="utf-8"
    )

    require(
        'import LiveCommandCenterV15_4 from '
        '"./components/LiveCommandCenterV15_4";'
        in app_text,
        "V15.4 import missing from App.tsx",
    )

    require(
        "<LiveCommandCenterV15_4 />" in app_text,
        "V15.4 component not rendered in App.tsx",
    )

    for filename in FILENAMES.values():
        require(
            filename in component_text,
            f"V15.4 does not reference {filename}",
        )

    require(
        "validatePayloads" in component_text,
        "V15.4 JSON validation is missing",
    )


def run_check(
    name: str,
    fn,
) -> None:
    try:
        fn()
        record(name, True, "Validation passed.")
    except Exception as exc:
        record(name, False, str(exc))


def main() -> int:

    print()
    print("=" * 72)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V15.5 VALIDATION & RELEASE")
    print("=" * 72)
    print()

    CHECKS.clear()

    payloads: dict[str, dict[str, Any]] = {}
    rows: dict[str, list[dict[str, Any]]] = {}

    for key, filename in FILENAMES.items():

        def load_and_validate(
            current_key=key,
            current_filename=filename,
        ):
            payload = load_json(
                HERE / current_filename
            )

            records = validate_structure(
                current_key,
                payload,
            )

            payloads[current_key] = payload
            rows[current_key] = records

        run_check(
            f"{key.upper()} JSON structure",
            load_and_validate,
        )

    keys = {"v15_1", "v15_2", "v15_3"}

    if keys.issubset(rows):

        def ids_check():
            a = [
                row["event_id"]
                for row in rows["v15_1"]
            ]
            b = [
                row["event_id"]
                for row in rows["v15_2"]
            ]
            c = [
                row["event_id"]
                for row in rows["v15_3"]
            ]

            require(
                a == b == c,
                "Event IDs or event order do not match.",
            )

        run_check(
            "V15.1-V15.3 event consistency",
            ids_check,
        )

        run_check(
            "V15.1 orchestration rules",
            lambda: validate_orchestrator(
                rows["v15_1"]
            ),
        )

        run_check(
            "V15.2 agent decision rules",
            lambda: validate_decisions(
                rows["v15_1"],
                rows["v15_2"],
            ),
        )

        run_check(
            "V15.3 response safety",
            lambda: validate_responses(
                rows["v15_2"],
                rows["v15_3"],
            ),
        )

        run_check(
            "Cross-version summary statistics",
            lambda: validate_summary(
                payloads["v15_1"],
                payloads["v15_2"],
                payloads["v15_3"],
                rows["v15_1"],
                rows["v15_2"],
                rows["v15_3"],
            ),
        )

    else:
        record(
            "Cross-version consistency",
            False,
            "One or more V15 datasets are unavailable.",
        )

    run_check(
        "V15.4 dashboard integration",
        validate_frontend_files,
    )

    passed = sum(
        check["status"] == "PASS"
        for check in CHECKS
    )

    failed = sum(
        check["status"] == "FAIL"
        for check in CHECKS
    )

    status = "PASS" if failed == 0 else "FAIL"

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "module": "Validation & Release",
        "generated_at": now_utc(),
        "status": status,
        "validation_scope": (
            "Saved simulation results, deterministic "
            "rules and static frontend integration"
        ),
        "checks_passed": passed,
        "checks_failed": failed,
        "checks": CHECKS,
        "source_files": list(FILENAMES.values()),
        "limitations": [
            "Does not measure real-world detection accuracy.",
            "Does not verify quantum computational advantage.",
            "Does not execute real security responses.",
            "Does not validate the live backend API.",
            "Does not replace TypeScript or Vite builds.",
            "Does not perform browser end-to-end testing.",
            "Does not verify Vercel deployment readiness.",
        ],
    }

    OUTPUT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("V15.5 VALIDATION SUMMARY")
    print("=" * 72)

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"RELEASE VALIDATION: {status}")

    print()
    print("RESULTS SAVED TO:")
    print(OUTPUT_FILE)

    print()

    if failed:
        print(
            "V15.5 VALIDATION FAILED - "
            "REVIEW THE FAILED CHECKS"
        )
        return 1

    print(
        "V15.5 VALIDATION & RELEASE COMPLETED"
    )

    print()
    print(
        "NOTE: Research simulation validation passed. "
        "Production deployment requires separate "
        "build and runtime checks."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
