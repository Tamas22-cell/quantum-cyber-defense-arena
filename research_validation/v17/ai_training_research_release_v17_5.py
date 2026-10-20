
"""
QUANTUM CYBER DEFENSE ARENA
V17.5 - AI TRAINING RESEARCH RELEASE

Consolidates and validates V17.1-V17.4 outputs.

Standard library only.
Does not retrain models or modify earlier results.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V17 = ROOT / "research_validation" / "v17"

FILES = {
    "v17_1": "training_data_pipeline_v17_1_results.json",
    "v17_2": "ai_model_training_v17_2_results.json",
    "v17_3": "ai_model_validation_v17_3_results.json",
    "v17_4": "ai_model_robustness_v17_4_results.json",
    "training_csv": "training_features_v17_1.csv",
    "model": "isolation_forest_model_v17_2.joblib",
    "scores_csv": "anomaly_scores_v17_2.csv",
    "robustness_csv": "ai_model_robustness_v17_4_scores.csv",
}

OUTPUT_JSON = V17 / "ai_training_research_release_v17_5_results.json"
OUTPUT_MD = V17 / "V17_RESEARCH_RELEASE.md"

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
        print(f"       {detail}")

    return passed


def load_json(path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def count_csv_rows(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        if not reader.fieldnames:
            raise ValueError(f"No CSV header: {path.name}")

        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"Duplicate CSV headers: {path.name}")

        return sum(1 for _ in reader), reader.fieldnames


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def main():
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V17.5 - AI TRAINING RESEARCH RELEASE")
    print("=" * 68)

    V17.mkdir(parents=True, exist_ok=True)

    paths = {
        key: V17 / filename
        for key, filename in FILES.items()
    }

    for key, path in paths.items():
        check(
            f"Required artifact: {key}",
            path.is_file(),
            path.name,
        )

    reports = {}
    for key in ("v17_1", "v17_2", "v17_3", "v17_4"):
        path = paths[key]

        if not path.is_file():
            continue

        try:
            reports[key] = load_json(path)
            check(f"Readable JSON: {key}", True)
        except (OSError, ValueError) as exc:
            check(f"Readable JSON: {key}", False, exc)

    expected = {
        "v17_1": ("V17.1", "FEATURE_PREPARATION_PASS"),
        "v17_2": ("V17.2", "MODEL_TRAINING_PASS"),
        "v17_3": ("V17.3", "VALIDATION_PASS"),
        "v17_4": ("V17.4", "ROBUSTNESS_BENCHMARK_PASS"),
    }

    for key, (version, status) in expected.items():
        report = reports.get(key)

        if report is None:
            continue

        check(
            f"{version} version",
            report.get("version") == version,
        )

        check(
            f"{version} status",
            report.get("status") == status,
            f"Expected {status}",
        )

    csv_info = {}

    for key in ("training_csv", "scores_csv", "robustness_csv"):
        path = paths[key]

        if not path.is_file():
            continue

        try:
            count, columns = count_csv_rows(path)
            csv_info[key] = {
                "rows": count,
                "columns": columns,
            }
            check(f"Readable CSV: {key}", count > 0)
        except (OSError, ValueError) as exc:
            check(f"Readable CSV: {key}", False, exc)

    a = reports.get("v17_1", {})
    b = reports.get("v17_2", {})
    c = reports.get("v17_3", {})
    d = reports.get("v17_4", {})

    if c:
        passed = c.get("checks_passed")
        failed = c.get("checks_failed")
        details = c.get("checks", [])

        check(
            "V17.3 validation checks",
            isinstance(passed, int)
            and isinstance(failed, int)
            and isinstance(details, list)
            and passed > 0
            and failed == 0
            and len(details) == passed
            and all(item.get("passed") is True for item in details),
            f"Passed={passed}, Failed={failed}",
        )

    if a and b and d and "training_csv" in csv_info:
        sample_count = csv_info["training_csv"]["rows"]
        feature_names = csv_info["training_csv"]["columns"]

        check(
            "V17.1 sample count consistency",
            a.get("prepared_rows") == sample_count,
        )

        check(
            "V17.2 sample count consistency",
            b.get("samples") == sample_count,
        )

        check(
            "V17.4 sample count consistency",
            d.get("samples") == sample_count,
        )

        check(
            "V17.2 feature consistency",
            b.get("feature_names") == feature_names,
        )

        check(
            "V17.4 feature consistency",
            d.get("feature_names") == feature_names,
        )

    if b and "scores_csv" in csv_info:
        check(
            "Model score row count",
            csv_info["scores_csv"]["rows"] == b.get("samples"),
        )

        results = b.get("training_set_results", {})
        anomalies = results.get("anomalies")
        normal = results.get("normal")

        check(
            "Model counts sum to samples",
            isinstance(anomalies, int)
            and isinstance(normal, int)
            and anomalies + normal == b.get("samples"),
        )

    if d:
        runs = d.get("model_runs")
        comparisons = d.get("pairwise_results", [])
        seeds = d.get("random_seeds", [])

        check(
            "Robustness run count",
            isinstance(runs, int)
            and runs >= 2
            and isinstance(seeds, list)
            and len(seeds) == runs
            and len(set(seeds)) == runs,
        )

        check(
            "Pairwise comparison count",
            isinstance(runs, int)
            and isinstance(comparisons, list)
            and len(comparisons) == runs * (runs - 1) // 2,
        )

        if "robustness_csv" in csv_info:
            check(
                "Robustness score row count",
                isinstance(runs, int)
                and csv_info["robustness_csv"]["rows"]
                == runs * d.get("samples", -1),
            )

    fingerprints = {}

    for key, path in paths.items():
        if path.is_file():
            fingerprints[key] = {
                "file": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }

    passed = sum(item["passed"] for item in CHECKS)
    failed = len(CHECKS) - passed

    status = (
        "RESEARCH_RELEASE_PASS"
        if failed == 0
        else "RESEARCH_RELEASE_FAIL"
    )

    release = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V17.5",
        "module": "AI Training Research Release",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "checks_passed": passed,
        "checks_failed": failed,
        "checks": CHECKS,
        "artifacts": fingerprints,
        "research_results": {
            "v17_1_prepared_rows": a.get("prepared_rows"),
            "v17_2_samples": b.get("samples"),
            "v17_2_features": b.get("feature_count"),
            "v17_2_training_anomalies": b.get(
                "training_set_results", {}
            ).get("anomalies"),
            "v17_3_checks_passed": c.get("checks_passed"),
            "v17_3_checks_failed": c.get("checks_failed"),
            "v17_4_model_runs": d.get("model_runs"),
            "v17_4_pairwise_comparisons": d.get(
                "summary", {}
            ).get("pairwise_comparisons"),
            "v17_4_mean_flag_agreement": d.get(
                "summary", {}
            ).get("mean_flag_agreement"),
            "v17_4_mean_anomaly_jaccard": d.get(
                "summary", {}
            ).get("mean_anomaly_jaccard"),
            "v17_4_mean_rank_correlation": d.get(
                "summary", {}
            ).get("mean_score_rank_correlation"),
        },
        "scientific_scope": (
            "Small-sample, in-sample unsupervised "
            "anomaly detection research"
        ),
        "verified_attack_labels": False,
        "out_of_sample_performance_verified": False,
        "production_ready": False,
        "limitations": [
            "Anomaly flags are not proven cyberattacks.",
            "The source sample contains only 20 transactions.",
            "No verified fraud or threat labels are available.",
            "No independent test-set performance was measured.",
            "Random-seed stability does not imply accuracy.",
            "Model artifacts are research outputs, not a "
            "production threat detection system.",
        ],
        "next_stage": (
            "V18 - Quantum-Classical Benchmark Lab"
        ),
    }

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            release,
            handle,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

    metrics = release["research_results"]

    markdown = f"""# Quantum Cyber Defense Arena

## V17 - AI Training Research Release

**Release status:** {status}

**Validation:** {passed} passed / {failed} failed

### Research pipeline

1. V17.1 - AI Training Data Pipeline
2. V17.2 - Isolation Forest Training
3. V17.3 - Model Evaluation and Validation
4. V17.4 - Random Seed Robustness Benchmark
5. V17.5 - Research Release Validation

### Results

| Metric | Value |
|---|---|
| Prepared transaction samples | {metrics['v17_1_prepared_rows']} |
| Model features | {metrics['v17_2_features']} |
| Training-set anomaly flags | {metrics['v17_2_training_anomalies']} |
| V17.3 checks passed | {metrics['v17_3_checks_passed']} |
| V17.3 checks failed | {metrics['v17_3_checks_failed']} |
| Robustness model runs | {metrics['v17_4_model_runs']} |
| Pairwise comparisons | {metrics['v17_4_pairwise_comparisons']} |
| Mean flag agreement | {metrics['v17_4_mean_flag_agreement']} |
| Mean anomaly Jaccard | {metrics['v17_4_mean_anomaly_jaccard']} |
| Mean rank correlation | {metrics['v17_4_mean_rank_correlation']} |

### Scientific limitations

- Only 20 transactions were available for this study.
- No verified malicious transaction labels were provided.
- Evaluation was conducted on training data.
- Seed stability does not measure predictive accuracy.
- No production-readiness claim is made.

### Artifact integrity

SHA-256 hashes for all input artifacts are stored in
`ai_training_research_release_v17_5_results.json`.

### Next stage

V18 - Quantum-Classical Benchmark Lab.

The next research stage should use controlled,
clearly separated baselines and independently
evaluated test data wherever possible.
"""

    OUTPUT_MD.write_text(
        markdown,
        encoding="utf-8",
    )

    print()
    print("=" * 68)
    print("V17 RESEARCH RELEASE SUMMARY")
    print("=" * 68)
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"RELEASE STATUS: {status}")
    print(f"JSON REPORT: {OUTPUT_JSON}")
    print(f"RESEARCH DOCUMENT: {OUTPUT_MD}")
    print("=" * 68)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print()
        print(
            f"V17.5 FATAL ERROR: "
            f"{type(exc).__name__}: {exc}"
        )
        sys.exit(1)
