
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = (
    ROOT
    / "research_validation"
    / "v23"
    / "intelligent_threat_fusion_v23_2_events.csv"
)
OUTPUT = Path(__file__).with_name(
    "autonomous_defense_validation_v23_7_results.json"
)

REQUIRED = {
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
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(f"Invalid boolean: {value!r}")


def validate() -> dict:
    if not INPUT.is_file():
        raise FileNotFoundError(INPUT)

    with INPUT.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Missing CSV columns: {sorted(missing)}"
            )

        total = 0
        valid = 0
        violations = Counter()
        priorities = Counter()
        actions = Counter()
        scores = []
        seen_ids = set()

        for row in reader:
            total += 1
            errors = []

            fusion_id = row["fusion_id"].strip()

            if not fusion_id:
                errors.append("missing_fusion_id")
            elif fusion_id in seen_ids:
                errors.append("duplicate_fusion_id")
            seen_ids.add(fusion_id)

            try:
                tick = int(row["tick"])
                if tick < 0:
                    errors.append("negative_tick")
            except (ValueError, TypeError):
                errors.append("invalid_tick")

            if not row["node_id"].strip():
                errors.append("missing_node_id")

            try:
                score = float(row["fusion_score"])
                if not 0 <= score <= 1:
                    errors.append("score_out_of_range")
                else:
                    scores.append(score)
            except (ValueError, TypeError):
                errors.append("invalid_score")

            try:
                simulation = parse_bool(
                    row["simulation_mode"]
                )
                executed = parse_bool(
                    row["real_action_executed"]
                )
                approval = parse_bool(
                    row["human_approval_required"]
                )
                trained_model = parse_bool(
                    row["trained_ai_model_used"]
                )

                if simulation and executed:
                    errors.append(
                        "real_action_in_simulation_mode"
                    )

                if executed and approval:
                    errors.append(
                        "executed_action_requires_approval"
                    )

                if not simulation:
                    errors.append(
                        "non_simulation_record_requires_review"
                    )

                if trained_model:
                    errors.append(
                        "trained_model_claim_requires_evidence"
                    )

            except (ValueError, AttributeError):
                errors.append("invalid_boolean")

            priorities[row["priority"]] += 1
            actions[row["v22_proposed_action"]] += 1

            if errors:
                violations.update(set(errors))
            else:
                valid += 1

    result = {
        "version": "23.7",
        "engine": "Autonomous Defense Validation",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "dataset": str(INPUT.relative_to(ROOT)),
        "validation": {
            "total_events": total,
            "valid_events": valid,
            "invalid_events": total - valid,
            "validity_rate": round(
                valid / total, 6
            ) if total else None,
            "average_fusion_score": round(
                sum(scores) / len(scores), 6
            ) if scores else None,
            "priority_distribution": dict(priorities),
            "action_distribution": dict(actions),
            "violations": dict(violations),
        },
        "limitations": {
            "real_attack_ground_truth": False,
            "precision_recall_f1_available": False,
            "production_accuracy_verified": False,
            "autonomous_intervention_verified": False,
        },
        "status": (
            "RESEARCH_VALIDATION_PASS"
            if total > 0 and valid == total
            else "RESEARCH_VALIDATION_REVIEW_REQUIRED"
        ),
    }

    OUTPUT.write_text(
        json.dumps(
            result, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    return result


if __name__ == "__main__":
    report = validate()
    print(json.dumps({
        "version": report["version"],
        "status": report["status"],
        **report["validation"],
    }, indent=2))
    print(f"\nSaved: {OUTPUT}")
