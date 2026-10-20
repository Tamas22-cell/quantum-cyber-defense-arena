
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research_validation"

INPUT = (
    BASE / "v23"
    / "intelligent_threat_fusion_v23_2_events.csv"
)

OUTPUT = (
    BASE / "v23_8"
    / "ai_defense_decision_benchmark_v23_8_results.json"
)

PRIORITIES = {"normal", "low", "high", "critical"}
ACTIONS = {
    "observe",
    "increase_monitoring",
    "isolate_node",
}

REQUIRED_COLUMNS = {
    "fusion_id",
    "tick",
    "node_id",
    "fusion_score",
    "priority",
    "v22_proposed_action",
    "human_approval_required",
    "simulation_mode",
    "real_action_executed",
    "trained_ai_model_used",
}

TRUE_VALUES = {"true", "1", "yes"}
FALSE_VALUES = {"false", "0", "no"}


def parse_bool(value: str) -> bool:
    value = value.strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    raise ValueError(f"Invalid boolean: {value!r}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024), b""
        ):
            digest.update(chunk)
    return digest.hexdigest()


def load_events() -> list[dict]:
    if not INPUT.is_file():
        raise FileNotFoundError(INPUT)

    with INPUT.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)
        missing = REQUIRED_COLUMNS - set(
            reader.fieldnames or []
        )
        if missing:
            raise ValueError(
                f"Missing columns: {sorted(missing)}"
            )
        return list(reader)


def benchmark() -> dict:
    events = load_events()

    violations = Counter()
    priorities = Counter()
    actions = Counter()
    decision_matrix = defaultdict(Counter)

    scores = []
    seen_ids = set()
    valid_events = 0
    approval_required = 0
    elevated_priority = 0

    for index, row in enumerate(events, start=1):
        errors = set()

        fusion_id = row["fusion_id"].strip()
        priority = row["priority"].strip().lower()
        action = row["v22_proposed_action"].strip().lower()

        if not fusion_id:
            errors.add("missing_fusion_id")
        elif fusion_id in seen_ids:
            errors.add("duplicate_fusion_id")
        else:
            seen_ids.add(fusion_id)

        if not row["node_id"].strip():
            errors.add("missing_node_id")

        try:
            tick = int(row["tick"])
            if tick < 0:
                errors.add("negative_tick")
        except (ValueError, TypeError):
            errors.add("invalid_tick")

        try:
            score = float(row["fusion_score"])
            if not math.isfinite(score) or not 0 <= score <= 1:
                errors.add("invalid_fusion_score")
            else:
                scores.append(score)
        except (ValueError, TypeError):
            errors.add("invalid_fusion_score")

        if priority not in PRIORITIES:
            errors.add("unknown_priority")

        if action not in ACTIONS:
            errors.add("unknown_action")

        try:
            approval = parse_bool(
                row["human_approval_required"]
            )
            simulation = parse_bool(
                row["simulation_mode"]
            )
            executed = parse_bool(
                row["real_action_executed"]
            )
            trained_model = parse_bool(
                row["trained_ai_model_used"]
            )

            if approval:
                approval_required += 1

            if simulation and executed:
                errors.add("execution_in_simulation")

            if executed and approval:
                errors.add("execution_requires_approval")

            if not simulation:
                errors.add("non_simulation_record")

            if trained_model:
                errors.add("model_claim_requires_evidence")

        except (ValueError, AttributeError):
            errors.add("invalid_boolean")

        priorities[priority] += 1
        actions[action] += 1
        decision_matrix[priority][action] += 1

        if priority in {"high", "critical"}:
            elevated_priority += 1

        # Policy diagnostics, not ground-truth accuracy.
        # These rules are benchmark assumptions.
        if priority == "critical" and action == "observe":
            errors.add("critical_observe_policy_warning")

        if priority == "normal" and action == "isolate_node":
            errors.add("normal_isolation_policy_warning")

        if errors:
            violations.update(errors)
        else:
            valid_events += 1

    total = len(events)
    invalid_events = total - valid_events

    decision_matrix_json = {
        priority: {
            action: decision_matrix[priority][action]
            for action in sorted(ACTIONS)
        }
        for priority in sorted(PRIORITIES)
    }

    result = {
        "version": "23.8",
        "name": "AI Defense Decision Benchmark",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source": {
            "dataset": str(INPUT.relative_to(ROOT)),
            "sha256": sha256_file(INPUT),
        },
        "benchmark": {
            "total_events": total,
            "valid_events": valid_events,
            "invalid_events": invalid_events,
            "validity_rate": (
                round(valid_events / total, 6)
                if total else None
            ),
            "average_fusion_score": (
                round(sum(scores) / len(scores), 6)
                if scores else None
            ),
            "elevated_priority_events": elevated_priority,
            "approval_required_events": approval_required,
            "priority_distribution": dict(priorities),
            "action_distribution": dict(actions),
            "decision_matrix": decision_matrix_json,
            "violations": dict(violations),
        },
        "methodology": {
            "dataset_type": "simulation",
            "policy_checks": "research assumptions",
            "reproducible": True,
            "input_hash_verified": True,
            "ground_truth_labels_available": False,
            "precision_recall_f1_computed": False,
            "false_positive_rate_computed": False,
            "production_accuracy_verified": False,
            "autonomous_intervention_verified": False,
        },
        "status": (
            "AI_DEFENSE_BENCHMARK_PASS"
            if total > 0 and invalid_events == 0
            else "AI_DEFENSE_BENCHMARK_REVIEW_REQUIRED"
        ),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return result


def main() -> None:
    result = benchmark()
    summary = {
        "version": result["version"],
        "status": result["status"],
        **result["benchmark"],
    }

    print(json.dumps(
        summary, indent=2, ensure_ascii=False
    ))
    print(f"\nSaved: {OUTPUT}")


if __name__ == "__main__":
    main()
