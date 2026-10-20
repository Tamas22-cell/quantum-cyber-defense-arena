
"""
QUANTUM CYBER DEFENSE ARENA
V23.3 - ADAPTIVE DEFENSE POLICY OPTIMIZATION

Simulation-only policy comparison using V23.2 fusion
scores and the V22.4 hypothetical action-effect model.

Three fixed policy profiles:
- balanced
- service_first
- risk_first

All five actions are evaluated under each profile.
No strategies are executed on real systems.

Outputs:
- adaptive_defense_policy_optimization_v23_3_results.json
- adaptive_defense_policy_optimization_v23_3_policies.csv
- adaptive_defense_policy_optimization_v23_3_timeline.json
- ADAPTIVE_DEFENSE_POLICY_OPTIMIZATION_V23_3.md

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
V23 = ROOT / "research_validation" / "v23"

ARCH = V23 / (
    "advanced_cyber_defense_architecture_v23_1_results.json"
)
FUSION_REPORT = V23 / (
    "intelligent_threat_fusion_v23_2_results.json"
)
FUSION_CSV = V23 / (
    "intelligent_threat_fusion_v23_2_events.csv"
)
STRATEGY_REPORT = V22 / (
    "defense_strategy_simulation_v22_4_results.json"
)
DECISION_CSV = V22 / (
    "multi_agent_defense_decision_v22_3_decisions.csv"
)

OUT_REPORT = V23 / (
    "adaptive_defense_policy_optimization_v23_3_results.json"
)
OUT_CSV = V23 / (
    "adaptive_defense_policy_optimization_v23_3_policies.csv"
)
OUT_TIMELINE = V23 / (
    "adaptive_defense_policy_optimization_v23_3_timeline.json"
)
OUT_MD = V23 / (
    "ADAPTIVE_DEFENSE_POLICY_OPTIMIZATION_V23_3.md"
)

HOLDOUT_START = 90

PROFILES = {
    "balanced": {
        "risk_weight": 0.70,
        "service_weight": 0.30,
    },
    "service_first": {
        "risk_weight": 0.40,
        "service_weight": 0.60,
    },
    "risk_first": {
        "risk_weight": 0.90,
        "service_weight": 0.10,
    },
}

REQUIRES_APPROVAL = {
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
        print("       ", detail)

    return passed


def read_json(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))

    with path.open("r", encoding="utf-8-sig") as file:
        result = json.load(file)

    if not isinstance(result, dict):
        raise ValueError(
            f"Expected JSON object: {path.name}"
        )

    return result


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(str(path))

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        records = list(reader)

    if not records:
        raise ValueError(f"Empty CSV: {path.name}")

    return records


def write_json(path, result):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


def write_csv(path, records):
    if not records:
        raise ValueError("No optimization records")

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(records[0]),
        )
        writer.writeheader()
        writer.writerows(records)


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def number(value):
    if isinstance(value, bool):
        raise ValueError("Boolean numeric value")

    result = float(value)

    if not math.isfinite(result):
        raise ValueError("Non-finite numeric value")

    return result


def rounded(value):
    return round(float(value), 6)


def validate_sources(arch, fusion, strategy):
    check(
        "V23.1 architecture passed",
        arch.get("version") == "V23.1"
        and arch.get("status")
        == "ADVANCED_CYBER_DEFENSE_ARCHITECTURE_PASS"
        and arch.get("checks_failed") == 0,
    )

    check(
        "V23.2 fusion engine passed",
        fusion.get("version") == "V23.2"
        and fusion.get("status")
        == "INTELLIGENT_THREAT_FUSION_PASS"
        and fusion.get("checks_failed") == 0,
    )

    check(
        "V22.4 strategy simulation passed",
        strategy.get("version") == "V22.4"
        and strategy.get("status")
        == "DEFENSE_STRATEGY_SIMULATION_PASS"
        and strategy.get("checks_failed") == 0,
    )

    check(
        "V23.2 architecture fingerprint valid",
        fusion.get("source_sha256", {}).get(
            "architecture"
        ) == sha256(ARCH),
    )

    check(
        "V23.2 decision fingerprint valid",
        fusion.get("source_sha256", {}).get(
            "decision_events"
        ) == sha256(DECISION_CSV),
    )

    check(
        "All research sources simulation-only",
        arch.get("simulation_mode") is True
        and fusion.get("simulation_mode") is True
        and strategy.get("simulation_mode") is True,
    )

    check(
        "Real actions prohibited",
        arch.get("real_network_actions_enabled") is False
        and fusion.get("external_actions_enabled") is False
        and strategy.get("external_actions_enabled") is False,
    )

    check(
        "Strategy effects are hypothetical",
        strategy.get("effects_empirically_verified")
        is False,
    )

    check(
        "Three policy profiles configured",
        len(PROFILES) == 3
        and all(
            math.isclose(
                profile["risk_weight"]
                + profile["service_weight"],
                1.0,
            )
            for profile in PROFILES.values()
        ),
    )

    if not all(item["passed"] for item in CHECKS):
        raise ValueError("Source validation failed")

    return strategy["configuration"]["strategies"]


def normalize_inputs(fusion_rows, decision_rows):
    decisions = {}

    for row in decision_rows:
        key = (int(row["tick"]), row["node_id"])

        if key in decisions:
            raise ValueError(
                f"Duplicate decision: {key}"
            )

        decisions[key] = row

    normalized = []
    seen = set()

    for row in fusion_rows:
        tick = int(row["tick"])
        node_id = row["node_id"]
        key = (tick, node_id)

        if key in seen:
            raise ValueError(
                f"Duplicate fusion record: {key}"
            )

        seen.add(key)

        if key not in decisions:
            raise ValueError(
                f"Missing matching decision: {key}"
            )

        score = number(row["fusion_score"])
        risk = number(row["node_risk"])

        if not (0 <= score <= 1 and 0 <= risk <= 1):
            raise ValueError(
                f"Invalid risk or fusion score: {key}"
            )

        decision = decisions[key]

        if row["v22_proposed_action"] != decision["final_action"]:
            raise ValueError(
                f"Source action mismatch: {key}"
            )

        if row["timestamp"] != decision["timestamp"]:
            raise ValueError(
                f"Timestamp mismatch: {key}"
            )

        normalized.append({
            "tick": tick,
            "timestamp": row["timestamp"],
            "node_id": node_id,
            "fusion_score": score,
            "node_risk": risk,
            "baseline_action": decision["final_action"],
        })

    normalized.sort(
        key=lambda item: (
            item["tick"],
            item["node_id"],
        )
    )

    check(
        "1200 fused observations available",
        len(normalized) == 1200,
    )

    check(
        "1200 matching decisions available",
        len(decisions) == 1200
        and len(seen) == len(decisions),
    )

    check(
        "120 complete simulation ticks",
        all(
            sum(row["tick"] == tick for row in normalized)
            == 10
            for tick in range(120)
        ),
    )

    return normalized


def action_outcome(risk, action, strategies):
    parameters = strategies[action]

    reduction_fraction = number(
        parameters["risk_reduction_fraction"]
    )

    service_impact = number(
        parameters["service_impact"]
    )

    if not (
        0 <= risk <= 1
        and 0 <= reduction_fraction <= 1
        and 0 <= service_impact <= 1
    ):
        raise ValueError("Invalid strategy assumptions")

    residual_risk = risk * (
        1.0 - reduction_fraction
    )

    return residual_risk, service_impact


def choose_action(risk, profile, strategies):
    """
    Evaluate every available simulated strategy.

    Minimize weighted residual risk and
    hypothetical service impact.

    The selection does not authorize execution.
    """

    costs = {}

    for action in sorted(strategies):
        residual, impact = action_outcome(
            risk,
            action,
            strategies,
        )

        costs[action] = (
            profile["risk_weight"] * residual
            + profile["service_weight"] * impact
        )

    winner = min(
        sorted(costs),
        key=lambda action: costs[action],
    )

    return winner, costs[winner]


def optimize(records, strategies):
    output = []

    for item in records:
        # The fused score is a PRIORITY INDEX.
        # Using it as input risk is a hypothetical
        # policy-design choice, not causal evidence.
        risk = item["fusion_score"]

        baseline = item["baseline_action"]

        if baseline not in strategies:
            raise ValueError(
                f"Unknown baseline action: {baseline}"
            )

        result = {
            "tick": item["tick"],
            "timestamp": item["timestamp"],
            "node_id": item["node_id"],
            "fusion_score": rounded(risk),
            "v22_baseline_action": baseline,
        }

        for name, profile in PROFILES.items():
            action, cost = choose_action(
                risk,
                profile,
                strategies,
            )

            residual, impact = action_outcome(
                risk,
                action,
                strategies,
            )

            baseline_residual, baseline_impact = (
                action_outcome(
                    risk,
                    baseline,
                    strategies,
                )
            )

            baseline_cost = (
                profile["risk_weight"] * baseline_residual
                + profile["service_weight"] * baseline_impact
            )

            result[f"{name}_action"] = action
            result[f"{name}_residual_risk"] = rounded(
                residual
            )
            result[f"{name}_service_impact"] = rounded(
                impact
            )
            result[f"{name}_weighted_cost"] = rounded(
                cost
            )
            result[f"{name}_baseline_cost"] = rounded(
                baseline_cost
            )
            result[f"{name}_approval_required"] = (
                action in REQUIRES_APPROVAL
            )

        result["simulation_mode"] = True
        result["real_action_executed"] = False
        result["effects_empirically_verified"] = False

        output.append(result)

    return output


def evaluate_profiles(records):
    evaluation = {}

    for profile_name in PROFILES:
        holdout = [
            row
            for row in records
            if row["tick"] >= HOLDOUT_START
        ]

        action_counts = Counter(
            row[f"{profile_name}_action"]
            for row in holdout
        )

        costs = [
            row[f"{profile_name}_weighted_cost"]
            for row in holdout
        ]

        baseline_costs = [
            row[f"{profile_name}_baseline_cost"]
            for row in holdout
        ]

        evaluation[profile_name] = {
            "holdout_observations": len(holdout),
            "mean_modelled_weighted_cost": rounded(
                statistics.mean(costs)
            ),
            "mean_v22_baseline_weighted_cost": rounded(
                statistics.mean(baseline_costs)
            ),
            "mean_modelled_residual_risk": rounded(
                statistics.mean(
                    row[f"{profile_name}_residual_risk"]
                    for row in holdout
                )
            ),
            "mean_modelled_service_impact": rounded(
                statistics.mean(
                    row[f"{profile_name}_service_impact"]
                    for row in holdout
                )
            ),
            "approval_required": sum(
                row[f"{profile_name}_approval_required"]
                for row in holdout
            ),
            "action_counts": {
                action: action_counts[action]
                for action in sorted(action_counts)
            },
            "outcomes_empirically_verified": False,
        }

    return evaluation


def build_timeline(records):
    by_tick = defaultdict(list)

    for row in records:
        by_tick[row["tick"]].append(row)

    timeline = []

    for tick in range(120):
        items = by_tick[tick]

        entry = {
            "tick": tick,
            "timestamp": items[0]["timestamp"],
            "evaluated_nodes": len(items),
            "mean_fusion_score": rounded(
                statistics.mean(
                    row["fusion_score"]
                    for row in items
                )
            ),
            "profiles": {},
            "simulation_mode": True,
            "real_actions_executed": 0,
        }

        for name in PROFILES:
            counts = Counter(
                row[f"{name}_action"]
                for row in items
            )

            entry["profiles"][name] = {
                "mean_weighted_cost": rounded(
                    statistics.mean(
                        row[f"{name}_weighted_cost"]
                        for row in items
                    )
                ),
                "mean_residual_risk": rounded(
                    statistics.mean(
                        row[f"{name}_residual_risk"]
                        for row in items
                    )
                ),
                "mean_service_impact": rounded(
                    statistics.mean(
                        row[f"{name}_service_impact"]
                        for row in items
                    )
                ),
                "approval_required": sum(
                    row[f"{name}_approval_required"]
                    for row in items
                ),
                "action_counts": {
                    action: counts[action]
                    for action in sorted(strategies_global)
                },
            }

        timeline.append(entry)

    return timeline


# Fixed source strategy IDs are assigned during
# validation. No network or external state is used.
strategies_global = {}


def validate_results(
    optimized,
    timeline,
    evaluation,
    normalized,
    strategies,
):
    check(
        "1200 optimization records generated",
        len(optimized) == 1200,
    )

    check(
        "One record per node and tick",
        len({
            (row["tick"], row["node_id"])
            for row in optimized
        }) == len(optimized),
    )

    check(
        "All selected actions recognized",
        all(
            row[f"{name}_action"] in strategies
            for row in optimized
            for name in PROFILES
        ),
    )

    check(
        "All model residual risks bounded",
        all(
            0 <= row[f"{name}_residual_risk"] <= 1
            for row in optimized
            for name in PROFILES
        ),
    )

    check(
        "All modeled service impacts bounded",
        all(
            0 <= row[f"{name}_service_impact"] <= 1
            for row in optimized
            for name in PROFILES
        ),
    )

    check(
        "Approval required for relevant actions",
        all(
            row[f"{name}_approval_required"]
            == (
                row[f"{name}_action"]
                in REQUIRES_APPROVAL
            )
            for row in optimized
            for name in PROFILES
        ),
    )

    check(
        "Optimized cost no greater than baseline",
        all(
            row[f"{name}_weighted_cost"]
            <= row[f"{name}_baseline_cost"] + 0.000003
            for row in optimized
            for name in PROFILES
        ),
    )

    check(
        "All outcomes hypothetical",
        all(
            row["simulation_mode"] is True
            and row["real_action_executed"] is False
            and row["effects_empirically_verified"] is False
            for row in optimized
        ),
    )

    check(
        "120 ordered timeline records",
        len(timeline) == 120
        and [
            row["tick"] for row in timeline
        ] == list(range(120)),
    )

    check(
        "Ten node decisions per tick",
        all(
            row["evaluated_nodes"] == 10
            for row in timeline
        ),
    )

    check(
        "Three profiles available on every tick",
        all(
            set(row["profiles"]) == set(PROFILES)
            for row in timeline
        ),
    )

    check(
        "Chronological holdout contains 300 records",
        all(
            result["holdout_observations"] == 300
            for result in evaluation.values()
        ),
    )

    check(
        "Every profile evaluation is finite",
        all(
            math.isfinite(
                result["mean_modelled_weighted_cost"]
            )
            for result in evaluation.values()
        ),
    )

    check(
        "Optimization is reproducible",
        optimized == optimize(
            normalized,
            strategies,
        ),
    )

    prefix = [
        row for row in normalized
        if row["tick"] < 60
    ]

    check(
        "Earlier decisions independent of future ticks",
        optimized[:len(prefix)]
        == optimize(prefix, strategies),
    )


def markdown_report(result):
    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V23.3 - Adaptive Defense Policy Optimization",
        "",
        f"**Status:** {result['status']}",
        f"**Checks passed:** {result['checks_passed']}",
        f"**Checks failed:** {result['checks_failed']}",
        "",
        "### Research approach",
        "",
        "The five V22.4 hypothetical actions are",
        "compared under three fixed cost profiles.",
        "",
        "| Profile | Risk weight | Service weight |",
        "|---|---:|---:|",
    ]

    for name, profile in PROFILES.items():
        lines.append(
            f"| {name} | {profile['risk_weight']} | "
            f"{profile['service_weight']} |"
        )

    lines += [
        "",
        "### Simulation holdout",
        "",
        "| Profile | Modeled cost | Baseline cost | "
        "Residual risk | Service impact |",
        "|---|---:|---:|---:|---:|",
    ]

    for name, item in result["evaluation"].items():
        lines.append(
            f"| {name} | "
            f"{item['mean_modelled_weighted_cost']} | "
            f"{item['mean_v22_baseline_weighted_cost']} | "
            f"{item['mean_modelled_residual_risk']} | "
            f"{item['mean_modelled_service_impact']} |"
        )

    lines += [
        "",
        "### Limitations",
        "",
        "- All telemetry and alerts are synthetic.",
        "- Strategy impacts are hypothetical parameters.",
        "- Fusion scores are not attack probabilities.",
        "- Optimizer does not train an AI model.",
        "- Improvement is relative to assumed costs.",
        "- No independently established defense effectiveness.",
        "- No real network actions are performed.",
        "",
        "### Next stage",
        "",
        "V23.4 - Multi-Agent Defense Orchestration Simulation",
        "",
    ]

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V23.3 - ADAPTIVE DEFENSE POLICY OPTIMIZATION")
    print("=" * 70)

    V23.mkdir(parents=True, exist_ok=True)

    architecture = read_json(ARCH)
    fusion_report = read_json(FUSION_REPORT)
    strategy_report = read_json(STRATEGY_REPORT)

    strategies = validate_sources(
        architecture,
        fusion_report,
        strategy_report,
    )

    global strategies_global
    strategies_global = strategies

    check(
        "Five strategy types available",
        len(strategies) == 5
        and set(strategies) == {
            "observe",
            "increase_monitoring",
            "rate_limit",
            "isolate_node",
            "request_review",
        },
    )

    fusion_rows = read_csv(FUSION_CSV)
    decision_rows = read_csv(DECISION_CSV)

    normalized = normalize_inputs(
        fusion_rows,
        decision_rows,
    )

    check(
        "Fusion CSV count matches V23.2 report",
        len(normalized)
        == fusion_report["metrics"]["fused_observations"],
    )

    if not all(item["passed"] for item in CHECKS):
        raise ValueError(
            "Input validation failed"
        )

    optimized = optimize(
        normalized,
        strategies,
    )

    timeline = build_timeline(
        optimized
    )

    evaluation = evaluate_profiles(
        optimized
    )

    validate_results(
        optimized,
        timeline,
        evaluation,
        normalized,
        strategies,
    )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )
    failed = len(CHECKS) - passed

    status = (
        "DEFENSE_POLICY_OPTIMIZATION_PASS"
        if failed == 0
        else "DEFENSE_POLICY_OPTIMIZATION_FAIL"
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V23.3",
        "module": "Adaptive Defense Policy Optimization",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "is_live": False,
        "trained_ai_model_used": False,
        "external_actions_enabled": False,
        "effects_empirically_verified": False,
        "configuration": {
            "profiles": PROFILES,
            "holdout_start": HOLDOUT_START,
            "strategies": strategies,
            "optimization_method": (
                "deterministic_weighted_cost_minimization"
            ),
        },
        "metrics": {
            "simulation_ticks": 120,
            "network_nodes": 10,
            "optimized_observations": len(optimized),
            "policy_profiles": len(PROFILES),
            "actions_per_profile": len(strategies),
            "real_actions_executed": 0,
        },
        "evaluation": evaluation,
        "source_sha256": {
            "architecture": sha256(ARCH),
            "fusion_report": sha256(FUSION_REPORT),
            "fusion_events": sha256(FUSION_CSV),
            "strategy_report": sha256(STRATEGY_REPORT),
            "decision_events": sha256(DECISION_CSV),
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "next_stage": (
            "V23.4 Multi-Agent Defense Orchestration Simulation"
        ),
    }

    write_json(
        OUT_REPORT,
        report,
    )

    if failed == 0:
        write_csv(
            OUT_CSV,
            optimized,
        )

        write_json(
            OUT_TIMELINE,
            {
                "version": "V23.3",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "ticks": len(timeline),
                "timeline": timeline,
            },
        )

        OUT_MD.write_text(
            markdown_report(report),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V23.3 DEFENSE POLICY OPTIMIZATION RESULTS")
    print("=" * 70)

    print("SIMULATION TICKS: 120")
    print("NETWORK NODES: 10")
    print("OPTIMIZED OBSERVATIONS:", len(optimized))
    print("POLICY PROFILES:", len(PROFILES))
    print("SIMULATED ACTION TYPES:", len(strategies))
    print("HOLDOUT OBSERVATIONS: 300")
    print("REAL ACTIONS EXECUTED: 0")
    print("CHECKS PASSED:", passed)
    print("CHECKS FAILED:", failed)
    print("JSON REPORT:", OUT_REPORT)
    print("V23.3 RESULT:", status)
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(
            "V23.3 FAILED:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
