
"""
QUANTUM CYBER DEFENSE ARENA
V17.4 - AI MODEL ROBUSTNESS BENCHMARK

Research objectives:
- Train Isolation Forest with multiple random seeds
- Compare anomaly decisions between model runs
- Measure score stability
- Calculate anomaly-set overlap
- Export reproducible benchmark results

This is an in-sample stability benchmark.
It does not measure real-world threat detection accuracy.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:
    print(f"DEPENDENCY ERROR: {exc}")
    print("Install: python -m pip install numpy scikit-learn")
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[2]
V17 = ROOT / "research_validation" / "v17"

INPUT_FILE = V17 / "training_features_v17_1.csv"

OUTPUT_JSON = V17 / "ai_model_robustness_v17_4_results.json"
OUTPUT_CSV = V17 / "ai_model_robustness_v17_4_scores.csv"

SEEDS = [42, 7, 21, 99, 123, 2026, 314, 777, 1001, 1729]

N_ESTIMATORS = 200
CONTAMINATION = "auto"
MIN_SAMPLES = 10


def load_data():
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            f"Missing training data: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        features = reader.fieldnames or []
        rows = list(reader)

    if not features:
        raise ValueError("Training CSV has no feature columns.")

    if len(features) != len(set(features)):
        raise ValueError("Duplicate feature columns detected.")

    if len(rows) < MIN_SAMPLES:
        raise ValueError(
            f"At least {MIN_SAMPLES} samples required. "
            f"Found: {len(rows)}"
        )

    matrix = []

    for row_index, row in enumerate(rows, start=2):
        values = []

        for feature in features:
            raw = row.get(feature)

            if raw is None or not str(raw).strip():
                value = float("nan")
            else:
                try:
                    value = float(raw)
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid value at row {row_index}, "
                        f"feature {feature}: {raw}"
                    ) from exc

            if math.isinf(value):
                raise ValueError(
                    f"Infinite value at row {row_index}, "
                    f"feature {feature}"
                )

            values.append(value)

        matrix.append(values)

    data = np.asarray(matrix, dtype=np.float64)

    if np.any(np.all(np.isnan(data), axis=0)):
        raise ValueError(
            "At least one feature contains only missing values."
        )

    return features, data


def build_model(seed):
    return Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "detector",
                IsolationForest(
                    n_estimators=N_ESTIMATORS,
                    contamination=CONTAMINATION,
                    random_state=seed,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def fit_model(data, seed):
    model = build_model(seed)
    model.fit(data)

    predictions = model.predict(data)

    # Higher score means more unusual.
    scores = -model.score_samples(data)

    flags = (predictions == -1).astype(int)

    if not np.all(np.isfinite(scores)):
        raise ValueError("Model generated non-finite scores.")

    return scores, flags


def agreement(a, b):
    return float(np.mean(a == b))


def jaccard(a, b):
    first = set(np.where(a == 1)[0].tolist())
    second = set(np.where(b == 1)[0].tolist())

    union = first | second

    if not union:
        return 1.0

    return len(first & second) / len(union)


def rank_values(values):
    # Deterministic average ranks, including ties.
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)

    position = 0

    while position < len(values):
        end = position + 1

        while (
            end < len(values)
            and values[order[end]] == values[order[position]]
        ):
            end += 1

        average_rank = (position + end - 1) / 2.0 + 1.0

        ranks[order[position:end]] = average_rank
        position = end

    return ranks


def rank_correlation(a, b):
    rank_a = rank_values(a)
    rank_b = rank_values(b)

    if np.std(rank_a) == 0 or np.std(rank_b) == 0:
        return None

    result = float(np.corrcoef(rank_a, rank_b)[0, 1])

    if not math.isfinite(result):
        return None

    return result


def rounded(value):
    if value is None:
        return None

    return round(float(value), 6)


def mean_or_none(values):
    if not values:
        return None

    return float(statistics.mean(values))


def save_score_table(runs, sample_count):
    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "sample_index",
            "seed",
            "anomaly_score",
            "is_anomaly",
        ])

        for run in runs:
            for i in range(sample_count):
                writer.writerow([
                    i + 1,
                    run["seed"],
                    rounded(run["scores"][i]),
                    int(run["flags"][i]),
                ])


def main():
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V17.4 - AI MODEL ROBUSTNESS BENCHMARK")
    print("=" * 68)

    features, data = load_data()

    print(f"INPUT: {INPUT_FILE}")
    print(f"SAMPLES: {len(data)}")
    print(f"FEATURES: {len(features)}")
    print(f"MODEL RUNS: {len(SEEDS)}")
    print(f"TREES PER MODEL: {N_ESTIMATORS}")
    print()

    runs = []

    for seed in SEEDS:
        scores, flags = fit_model(data, seed)

        anomaly_count = int(np.sum(flags))

        runs.append({
            "seed": seed,
            "scores": scores,
            "flags": flags,
            "anomalies": anomaly_count,
        })

        print(
            f"[PASS] SEED {seed:>4} "
            f"| ANOMALIES: {anomaly_count:>3} "
            f"| NORMAL: {len(data) - anomaly_count:>3}"
        )

    comparisons = []

    for first, second in combinations(runs, 2):
        correlation = rank_correlation(
            first["scores"],
            second["scores"],
        )

        comparisons.append({
            "seed_a": first["seed"],
            "seed_b": second["seed"],
            "flag_agreement": agreement(
                first["flags"],
                second["flags"],
            ),
            "anomaly_jaccard": jaccard(
                first["flags"],
                second["flags"],
            ),
            "score_rank_correlation": correlation,
        })

    agreement_values = [
        item["flag_agreement"]
        for item in comparisons
    ]

    jaccard_values = [
        item["anomaly_jaccard"]
        for item in comparisons
    ]

    correlation_values = [
        item["score_rank_correlation"]
        for item in comparisons
        if item["score_rank_correlation"] is not None
    ]

    anomaly_counts = [
        run["anomalies"]
        for run in runs
    ]

    score_matrix = np.stack(
        [run["scores"] for run in runs],
        axis=0,
    )

    # Variability of each sample's scores across seeds.
    per_sample_std = np.std(
        score_matrix,
        axis=0,
        ddof=0,
    )

    average_score_std = float(
        np.mean(per_sample_std)
    )

    reference = runs[0]

    reference_agreements = [
        agreement(
            reference["flags"],
            run["flags"],
        )
        for run in runs[1:]
    ]

    V17.mkdir(parents=True, exist_ok=True)

    save_score_table(
        runs,
        len(data),
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V17.4",
        "module": "AI Model Robustness Benchmark",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "ROBUSTNESS_BENCHMARK_PASS",
        "source": str(INPUT_FILE.relative_to(ROOT)),
        "model": "IsolationForest",
        "samples": int(len(data)),
        "features": len(features),
        "feature_names": features,
        "model_runs": len(SEEDS),
        "random_seeds": SEEDS,
        "n_estimators": N_ESTIMATORS,
        "contamination": CONTAMINATION,
        "evaluation_type": (
            "In-sample random-seed stability"
        ),
        "anomaly_counts": anomaly_counts,
        "summary": {
            "mean_anomaly_count": rounded(
                statistics.mean(anomaly_counts)
            ),
            "min_anomaly_count": min(anomaly_counts),
            "max_anomaly_count": max(anomaly_counts),
            "pairwise_comparisons": len(comparisons),
            "mean_flag_agreement": rounded(
                mean_or_none(agreement_values)
            ),
            "min_flag_agreement": rounded(
                min(agreement_values)
            ),
            "mean_anomaly_jaccard": rounded(
                mean_or_none(jaccard_values)
            ),
            "mean_score_rank_correlation": rounded(
                mean_or_none(correlation_values)
            ),
            "mean_per_sample_score_std": rounded(
                average_score_std
            ),
            "mean_reference_flag_agreement": rounded(
                mean_or_none(reference_agreements)
            ),
        },
        "per_seed": [
            {
                "seed": run["seed"],
                "anomalies": run["anomalies"],
                "normal": len(data) - run["anomalies"],
                "anomaly_percentage": rounded(
                    100 * run["anomalies"] / len(data)
                ),
            }
            for run in runs
        ],
        "pairwise_results": [
            {
                key: rounded(value)
                if key not in ("seed_a", "seed_b")
                else value
                for key, value in item.items()
            }
            for item in comparisons
        ],
        "verified_threat_labels": False,
        "out_of_sample_validation": False,
        "limitations": [
            "Only 20 samples are expected from V17.1.",
            "The same dataset is used in all runs.",
            "Random-seed stability is not accuracy.",
            "No independently verified attack labels.",
            "No unseen transaction evaluation.",
            "Results do not establish production readiness.",
        ],
        "outputs": {
            "scores_csv": str(
                OUTPUT_CSV.relative_to(ROOT)
            ),
            "report_json": str(
                OUTPUT_JSON.relative_to(ROOT)
            ),
        },
    }

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

    summary = report["summary"]

    print()
    print("=" * 68)
    print("ROBUSTNESS BENCHMARK RESULTS")
    print("=" * 68)

    print(f"MODEL RUNS: {len(SEEDS)}")
    print(f"PAIRWISE COMPARISONS: {len(comparisons)}")
    print(
        "MEAN FLAG AGREEMENT: "
        f"{summary['mean_flag_agreement']}"
    )
    print(
        "MIN FLAG AGREEMENT: "
        f"{summary['min_flag_agreement']}"
    )
    print(
        "MEAN ANOMALY JACCARD: "
        f"{summary['mean_anomaly_jaccard']}"
    )
    print(
        "MEAN SCORE RANK CORRELATION: "
        f"{summary['mean_score_rank_correlation']}"
    )
    print(
        "MEAN SCORE STD: "
        f"{summary['mean_per_sample_score_std']}"
    )

    if len(data) < 100:
        print()
        print(
            "WARNING: Small dataset. "
            "These results are preliminary."
        )

    print()
    print(f"SCORES SAVED: {OUTPUT_CSV}")
    print(f"REPORT SAVED: {OUTPUT_JSON}")
    print()
    print("V17.4 RESULT: ROBUSTNESS_BENCHMARK_PASS")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print()
        print(
            "V17.4 FAILED: "
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)
