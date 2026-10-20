
"""
QUANTUM CYBER DEFENSE ARENA
V22.4 - DEFENSE STRATEGY SIMULATION

Evaluates simulated defense proposals from V22.3.

Research outputs:
- defense_strategy_simulation_v22_4_results.json
- defense_strategy_simulation_v22_4_events.csv
- defense_strategy_simulation_v22_4_timeline.json
- DEFENSE_STRATEGY_SIMULATION_V22_4.md

All effects are hypothetical model assumptions.
No real network actions, no firewall operations.
Python standard library only.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import sys

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V22 = ROOT / "research_validation" / "v22"

ARCH_FILE = V22 / (
    "autonomous_defense_architecture_v22_1_results.json"
)
DECISION_FILE = V22 / (
    "multi_agent_defense_decision_v22_3_results.json"
)
DECISION_CSV = V22 / (
    "multi_agent_defense_decision_v22_3_decisions.csv"
)
INTELLIGENCE_FILE = ROOT / (
    "frontend/public/v21/intelligence_data.json"
)

OUTPUT_JSON = V22 / (
    "defense_strategy_simulation_v22_4_results.json"
)
OUTPUT_CSV = V22 / (
    "defense_strategy_simulation_v22_4_events.csv"
)
OUTPUT_TIMELINE = V22 / (
    "defense_strategy_simulation_v22_4_timeline.json"
)
OUTPUT_MD = V22 / (
    "DEFENSE_STRATEGY_SIMULATION_V22_4.md"
)

CHECKS = []

# Hypothetical effectiveness and service impact.
# These values are modelling assumptions, NOT
# empirical estimates of real cyber-defense effects.
STRATEGIES = {
    "observe": {
        "risk_reduction_fraction": 0.00,
        "service_impact": 0.00,
    },
    "increase_monitoring": {
        "risk_reduction_fraction": 0.05,
        "service_impact": 0.02,
    },
    "rate_limit": {
        "risk_reduction_fraction": 0.35,
        "service_impact": 0.25,
    },
    "isolate_node": {
        "risk_reduction_fraction": 0.75,
        "service_impact": 0.85,
    },
    "request_review": {
        "risk_reduction_fraction": 0.00,
        "service_impact": 0.03,
    },
}

APPROVAL_REQUIRED = {
    "rate_limit",
    "isolate_node",
    "request_review",
}

# Decision recommendations are never treated as
# authorization to execute disruptive actions.
# Only virtual outcomes are calculated.
RISK_WEIGHT = 0.70
SERVICE_WEIGHT = 0.30


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


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def read_json(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))

    with path.open(
        "r", encoding="utf-8-sig"
    ) as file:
        value = json.load(file)

    if not isinstance(value, dict):
        raise ValueError(
            f"Invalid JSON object: {path.name}"
        )

    return value


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))

    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("Decision CSV is empty")

    return rows


def write_json(path, value):
    path.parent.mkdir(
        parents=True, exist_ok=True
    )

    with path.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(
            value,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


def write_csv(path, rows):
    if not rows:
        raise ValueError("No simulation records")

    path.parent.mkdir(
        parents=True, exist_ok=True
    )

    with path.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=list(rows[0])
        )
        writer.writeheader()
        writer.writerows(rows)


def num(value):
    if isinstance(value, bool):
        raise ValueError("Boolean numeric value")

    result = float(value)

    if not math.isfinite(result):
        raise ValueError("Non-finite value")

    return result


def truth(value):
    if isinstance(value, bool):
        return value

    if str(value).lower() == "true":
        return True

    if str(value).lower() == "false":
        return False

    raise ValueError(
        f"Invalid boolean value: {value}"
    )


def rnd(value):
    return round(float(value), 6)


def validate_sources(architecture, report, data):
    check(
        "V22.1 architecture passed",
        architecture.get("version") == "V22.1"
        and architecture.get("status")
        == "AUTONOMOUS_DEFENSE_ARCHITECTURE_PASS"
        and architecture.get("checks_failed") == 0,
    )

    check(
        "V22.3 decision engine passed",
        report.get("version") == "V22.3"
        and report.get("status")
        == "DEFENSE_DECISION_PASS"
        and report.get("checks_failed") == 0,
    )

    check(
        "V21.5 intelligence export passed",
        data.get("version") == "V21.5"
        and data.get("status")
        == "DASHBOARD_INTEGRATION_PASS"
        and data.get("simulation_mode") is True
        and data.get("is_live") is False,
    )

    hashes = report.get("source_sha256", {})

    check(
        "Decision architecture fingerprint valid",
        hashes.get("architecture")
        == sha256(ARCH_FILE),
    )

    check(
        "Decision intelligence fingerprint valid",
        hashes.get("intelligence")
        == sha256(INTELLIGENCE_FILE),
    )

    check(
        "Decision output contains no real actions",
        report.get("real_actions_executed") == 0,
    )

    policy = architecture.get(
        "architecture", {}
    ).get("policy", {})

    check(
        "Real network changes prohibited",
        policy.get("simulation_mode") is True
        and policy.get(
            "real_network_changes_allowed"
        ) is False,
    )

    check(
        "Disruptive action approval policy",
        policy.get(
            "human_approval_for_disruptive_actions"
        ) is True,
    )

    definitions = architecture.get(
        "architecture", {}
    ).get("defense_actions", [])

    check(
        "Five documented strategy identifiers match",
        {a["id"] for a in definitions}
        == set(STRATEGIES),
    )

    check(
        "All documented actions simulated",
        all(
            a.get("implementation") == "simulated"
            for a in definitions
        ),
    )

    frames = data.get("frames", [])

    check(
        "120 simulation frames available",
        len(frames) == 120
        and [
            f.get("tick") for f in frames
        ] == list(range(120)),
    )

    check(
        "Ten nodes in each simulation frame",
        all(
            len(f.get("nodes", [])) == 10
            for f in frames
        ),
    )

    if not all(
        item["passed"] for item in CHECKS
    ):
        raise ValueError(
            "Source validation failed"
        )

    return frames


def normalize_decisions(csv_rows, frames):
    known_nodes = {
        frame["tick"]: {
            node["id"] for node in frame["nodes"]
        }
        for frame in frames
    }

    seen = set()
    decisions = []

    for row in csv_rows:
        tick = int(row["tick"])
        node_id = row["node_id"]
        action = row["final_action"]
        key = (tick, node_id)

        if (
            tick not in known_nodes
            or node_id not in known_nodes[tick]
            or key in seen
            or action not in STRATEGIES
        ):
            raise ValueError(
                f"Invalid decision identity: {key}"
            )

        seen.add(key)

        evidence = num(
            row["evidence_score"]
        )
        risk = num(
            row["node_risk"]
        )

        if not (
            0 <= evidence <= 1
            and 0 <= risk <= 1
        ):
            raise ValueError(
                f"Risk out of bounds: {key}"
            )

        approval = truth(
            row["human_approval_required"]
        )

        if (
            action in APPROVAL_REQUIRED
            and not approval
        ):
            raise ValueError(
                f"Unapproved-action policy flag: {key}"
            )

        if truth(row["real_action_executed"]):
            raise ValueError(
                "Real action unexpectedly reported"
            )

        if not truth(row["simulation_only"]):
            raise ValueError(
                "Non-simulated decision encountered"
            )

        decisions.append({
            "decision_id": row["decision_id"],
            "tick": tick,
            "timestamp": row["timestamp"],
            "node_id": node_id,
            "action": action,
            "evidence_score": evidence,
            "original_risk": risk,
            "human_approval_required": approval,
            "adaptive_detection": truth(
                row["adaptive_detection"]
            ),
        })

    check(
        "1200 decision observations loaded",
        len(decisions) == 1200,
    )

    check(
        "One decision for every node and tick",
        len(seen) == 1200
        and all(
            (frame["tick"], n["id"]) in seen
            for frame in frames
            for n in frame["nodes"]
        ),
    )

    decisions.sort(
        key=lambda x: (
            x["tick"], x["node_id"]
        )
    )

    return decisions


def simulate_action(risk, action):
    parameters = STRATEGIES[action]

    reduction = (
        risk
        * parameters["risk_reduction_fraction"]
    )

    residual_risk = max(
        0.0,
        risk - reduction,
    )

    service_impact = parameters[
        "service_impact"
    ]

    utility = (
        RISK_WEIGHT * residual_risk
        + SERVICE_WEIGHT * service_impact
    )

    return {
        "risk_reduction": reduction,
        "residual_risk": residual_risk,
        "service_impact": service_impact,
        "weighted_cost": utility,
    }


def simulate_decisions(decisions):
    output = []

    for item in decisions:
        risk = item["original_risk"]

        chosen = simulate_action(
            risk, item["action"]
        )

        observation = simulate_action(
            risk, "observe"
        )

        # Oracle comparison is purely hypothetical:
        # all actions are scored with the same assumed
        # effect model. It is not a causal experiment.
        candidate_scores = {
            action: simulate_action(
                risk, action
            )["weighted_cost"]
            for action in STRATEGIES
        }

        best_action = min(
            sorted(candidate_scores),
            key=lambda a: candidate_scores[a],
        )

        output.append({
            "decision_id": item["decision_id"],
            "tick": item["tick"],
            "timestamp": item["timestamp"],
            "node_id": item["node_id"],
            "proposed_action": item["action"],
            "human_approval_required": item[
                "human_approval_required"
            ],
            "approval_status": (
                "NOT_REQUESTED_SIMULATION_ONLY"
                if item["human_approval_required"]
                else "NOT_REQUIRED"
            ),
            "original_risk": rnd(risk),
            "simulated_risk_reduction": rnd(
                chosen["risk_reduction"]
            ),
            "simulated_residual_risk": rnd(
                chosen["residual_risk"]
            ),
            "simulated_service_impact": rnd(
                chosen["service_impact"]
            ),
            "simulated_weighted_cost": rnd(
                chosen["weighted_cost"]
            ),
            "observe_weighted_cost": rnd(
                observation["weighted_cost"]
            ),
            "model_best_action": best_action,
            "model_best_cost": rnd(
                candidate_scores[best_action]
            ),
            "model_regret": rnd(
                max(
                    0.0,
                    chosen["weighted_cost"]
                    - candidate_scores[best_action],
                )
            ),
            "adaptive_detection": item[
                "adaptive_detection"
            ],
            "real_action_executed": False,
            "simulation_mode": True,
            "evaluation_type": (
                "hypothetical_counterfactual"
            ),
        })

    return output


def build_timeline(events, frames):
    grouped = defaultdict(list)

    for event in events:
        grouped[event["tick"]].append(
            event
        )

    timeline = []

    for frame in frames:
        tick = frame["tick"]
        rows = grouped[tick]

        counts = Counter(
            row["proposed_action"]
            for row in rows
        )

        timeline.append({
            "tick": tick,
            "timestamp": frame["timestamp"],
            "evaluated_nodes": len(rows),
            "mean_original_risk": rnd(
                statistics.mean(
                    row["original_risk"]
                    for row in rows
                )
            ),
            "mean_simulated_residual_risk": rnd(
                statistics.mean(
                    row["simulated_residual_risk"]
                    for row in rows
                )
            ),
            "total_simulated_risk_reduction": rnd(
                sum(
                    row["simulated_risk_reduction"]
                    for row in rows
                )
            ),
            "mean_simulated_service_impact": rnd(
                statistics.mean(
                    row["simulated_service_impact"]
                    for row in rows
                )
            ),
            "total_model_regret": rnd(
                sum(
                    row["model_regret"]
                    for row in rows
                )
            ),
            "human_approval_required": sum(
                row["human_approval_required"]
                for row in rows
            ),
            "action_counts": {
                action: counts[action]
                for action in sorted(STRATEGIES)
            },
            "real_actions_executed": 0,
            "simulation_mode": True,
        })

    return timeline


def evaluate(events):
    risks = [
        row["original_risk"]
        for row in events
    ]

    residuals = [
        row["simulated_residual_risk"]
        for row in events
    ]

    impacts = [
        row["simulated_service_impact"]
        for row in events
    ]

    counts = Counter(
        row["proposed_action"]
        for row in events
    )

    return {
        "evaluated_decisions": len(events),
        "mean_original_risk": rnd(
            statistics.mean(risks)
        ),
        "mean_simulated_residual_risk": rnd(
            statistics.mean(residuals)
        ),
        "total_modelled_risk_reduction": rnd(
            sum(
                row["simulated_risk_reduction"]
                for row in events
            )
        ),
        "mean_modelled_service_impact": rnd(
            statistics.mean(impacts)
        ),
        "mean_modelled_weighted_cost": rnd(
            statistics.mean(
                row["simulated_weighted_cost"]
                for row in events
            )
        ),
        "mean_observe_weighted_cost": rnd(
            statistics.mean(
                row["observe_weighted_cost"]
                for row in events
            )
        ),
        "mean_model_regret": rnd(
            statistics.mean(
                row["model_regret"]
                for row in events
            )
        ),
        "approval_required": sum(
            row["human_approval_required"]
            for row in events
        ),
        "action_counts": {
            action: counts[action]
            for action in sorted(STRATEGIES)
        },
        "real_actions_executed": 0,
        "effectiveness_empirically_verified": False,
    }


def validate_results(events, timeline, decisions):
    check(
        "All decisions simulated",
        len(events) == len(decisions) == 1200,
    )

    check(
        "Every simulation ID unique",
        len({
            row["decision_id"]
            for row in events
        }) == 1200,
    )

    check(
        "Residual risks bounded",
        all(
            0 <= row["simulated_residual_risk"]
            <= row["original_risk"] <= 1
            for row in events
        ),
    )

    check(
        "Service impact bounded",
        all(
            0 <= row["simulated_service_impact"] <= 1
            for row in events
        ),
    )

    check(
        "Risk reductions nonnegative",
        all(
            row["simulated_risk_reduction"] >= 0
            for row in events
        ),
    )

    check(
        "Risk reduction arithmetic consistent",
        all(
            math.isclose(
                row["original_risk"],
                row["simulated_residual_risk"]
                + row["simulated_risk_reduction"],
                abs_tol=0.000003,
            )
            for row in events
        ),
    )

    check(
        "Model regret is nonnegative",
        all(
            row["model_regret"] >= 0
            for row in events
        ),
    )

    check(
        "Disruptive actions require approval",
        all(
            row["human_approval_required"]
            for row in events
            if row["proposed_action"]
            in APPROVAL_REQUIRED
        ),
    )

    check(
        "Approval not falsely granted",
        all(
            row["approval_status"]
            != "APPROVED"
            for row in events
        ),
    )

    check(
        "No real actions executed",
        all(
            row["real_action_executed"] is False
            for row in events
        ),
    )

    check(
        "All outcomes explicitly hypothetical",
        all(
            row["evaluation_type"]
            == "hypothetical_counterfactual"
            and row["simulation_mode"] is True
            for row in events
        ),
    )

    check(
        "Timeline contains 120 ticks",
        len(timeline) == 120
        and [
            row["tick"]
            for row in timeline
        ] == list(range(120)),
    )

    check(
        "Ten simulated decisions per tick",
        all(
            row["evaluated_nodes"] == 10
            for row in timeline
        ),
    )

    check(
        "Timeline action totals consistent",
        sum(
            sum(row["action_counts"].values())
            for row in timeline
        ) == len(events),
    )

    check(
        "Simulation deterministic",
        events == simulate_decisions(
            decisions
        ),
    )

    prefix = [
        row for row in decisions
        if row["tick"] < 60
    ]

    check(
        "Earlier simulations independent of future ticks",
        events[:len(prefix)]
        == simulate_decisions(prefix),
    )


def create_document(result):
    e = result["evaluation"]

    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V22.4 - Defense Strategy Simulation",
        "",
        f"Status: {result['status']}",
        f"Checks passed: {result['checks_passed']}",
        f"Checks failed: {result['checks_failed']}",
        "",
        "### Strategy assumptions",
        "",
        "| Strategy | Model risk reduction | Service impact |",
        "|---|---:|---:|",
    ]

    for action, params in STRATEGIES.items():
        lines.append(
            f"| {action} | "
            f"{params['risk_reduction_fraction']:.0%} | "
            f"{params['service_impact']:.0%} |"
        )

    lines += [
        "",
        "These values are hypothetical assumptions.",
        "They were not fitted to real security incidents.",
        "",
        "### Results",
        "",
        f"- Evaluated decisions: {e['evaluated_decisions']}",
        f"- Mean original risk: {e['mean_original_risk']}",
        f"- Mean simulated residual risk: {e['mean_simulated_residual_risk']}",
        f"- Total modeled risk reduction: {e['total_modelled_risk_reduction']}",
        f"- Mean modeled service impact: {e['mean_modelled_service_impact']}",
        f"- Mean model regret: {e['mean_model_regret']}",
        f"- Human approval required: {e['approval_required']}",
        "- Real network actions: 0",
        "",
        "### Method",
        "",
        "Each V22.3 decision is evaluated using a",
        "deterministic hypothetical action-effect model.",
        "The strategy is compared to observation only",
        "and to the model-optimal assumed strategy.",
        "",
        "### Limitations",
        "",
        "- All events are synthetic.",
        "- No real actions or interventions.",
        "- Effects are assumed, not measured.",
        "- No causal effectiveness established.",
        "- Service impact is an abstract model score.",
        "- Results must not be presented as field performance.",
        "",
        "### Next stage",
        "",
        "V22.5 - Autonomous Defense Dashboard",
        "",
    ]

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V22.4 - DEFENSE STRATEGY SIMULATION")
    print("=" * 70)

    V22.mkdir(parents=True, exist_ok=True)

    architecture = read_json(
        ARCH_FILE
    )
    decision_report = read_json(
        DECISION_FILE
    )
    intelligence = read_json(
        INTELLIGENCE_FILE
    )
    decision_rows = read_csv(
        DECISION_CSV
    )

    frames = validate_sources(
        architecture,
        decision_report,
        intelligence,
    )

    decisions = normalize_decisions(
        decision_rows,
        frames,
    )

    check(
        "Decision count matches V22.3 report",
        len(decisions)
        == decision_report.get(
            "metrics", {}
        ).get("decisions"),
    )

    check(
        "Action distribution matches V22.3 report",
        dict(Counter(
            row["action"]
            for row in decisions
        )) == {
            action: count
            for action, count in decision_report.get(
                "metrics", {}
            ).get("action_counts", {}).items()
            if count > 0
        },
    )

    if not all(
        row["passed"]
        for row in CHECKS
    ):
        raise ValueError(
            "Input validation failed"
        )

    events = simulate_decisions(
        decisions
    )

    timeline = build_timeline(
        events,
        frames,
    )

    evaluation = evaluate(events)

    validate_results(
        events,
        timeline,
        decisions,
    )

    passed = sum(
        row["passed"] for row in CHECKS
    )
    failed = len(CHECKS) - passed

    status = (
        "DEFENSE_STRATEGY_SIMULATION_PASS"
        if failed == 0
        else "DEFENSE_STRATEGY_SIMULATION_FAIL"
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V22.4",
        "module": "Defense Strategy Simulation",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "effects_empirically_verified": False,
        "external_actions_enabled": False,
        "configuration": {
            "strategies": STRATEGIES,
            "risk_weight": RISK_WEIGHT,
            "service_weight": SERVICE_WEIGHT,
            "evaluation_method": (
                "hypothetical_counterfactual_model"
            ),
        },
        "evaluation": evaluation,
        "source_sha256": {
            "architecture": sha256(
                ARCH_FILE
            ),
            "decision_report": sha256(
                DECISION_FILE
            ),
            "decision_csv": sha256(
                DECISION_CSV
            ),
            "intelligence": sha256(
                INTELLIGENCE_FILE
            ),
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "next_stage": (
            "V22.5 Autonomous Defense Dashboard"
        ),
    }

    write_json(
        OUTPUT_JSON,
        report,
    )

    if failed == 0:
        write_csv(
            OUTPUT_CSV,
            events,
        )

        write_json(
            OUTPUT_TIMELINE,
            {
                "version": "V22.4",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "ticks": len(timeline),
                "timeline": timeline,
            },
        )

        OUTPUT_MD.write_text(
            create_document(report),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V22.4 DEFENSE STRATEGY RESULTS")
    print("=" * 70)
    print(
        "SIMULATION TICKS:",
        len(timeline),
    )
    print(
        "DECISIONS EVALUATED:",
        evaluation["evaluated_decisions"],
    )
    print(
        "STRATEGIES:",
        len(STRATEGIES),
    )
    print(
        "HUMAN APPROVAL REQUIRED:",
        evaluation["approval_required"],
    )
    print(
        "REAL ACTIONS EXECUTED:",
        evaluation["real_actions_executed"],
    )
    print(
        "MEAN SIMULATED RESIDUAL RISK:",
        evaluation["mean_simulated_residual_risk"],
    )
    print(
        "CHECKS PASSED:",
        passed,
    )
    print(
        "CHECKS FAILED:",
        failed,
    )
    print(
        "JSON REPORT:",
        OUTPUT_JSON,
    )
    print(
        "V22.4 RESULT:",
        status,
    )
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as error:
        print(
            "V22.4 FAILED:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
