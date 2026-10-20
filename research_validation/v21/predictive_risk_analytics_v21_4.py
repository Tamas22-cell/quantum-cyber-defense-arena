
"""
QUANTUM CYBER DEFENSE ARENA
V21.4 - PREDICTIVE RISK ANALYTICS

One-step-ahead synthetic network risk forecasting.

Inputs:
- V21.3 threat correlation results and timeline
- V20.4 digital twin frames

Method:
- Fixed causal forecasting rule
- Persistence baseline
- Rolling historical mean
- Prior threat correlation as a feature
- Chronological holdout evaluation
- Historical calibration for prediction intervals

No trained ML model and no real attack detection.
Python standard library only.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import sys

from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V20 = ROOT / "research_validation" / "v20"
V21 = ROOT / "research_validation" / "v21"

CORRELATION_REPORT = V21 / (
    "multi_agent_threat_correlation_v21_3_results.json"
)

CORRELATION_TIMELINE = V21 / (
    "multi_agent_threat_correlation_v21_3_timeline.json"
)

FRAMES_FILE = V20 / (
    "event_streaming_v20_4_frames.json"
)

OUTPUT_JSON = V21 / (
    "predictive_risk_analytics_v21_4_results.json"
)

OUTPUT_CSV = V21 / (
    "predictive_risk_analytics_v21_4_forecasts.csv"
)

OUTPUT_TIMELINE = V21 / (
    "predictive_risk_analytics_v21_4_timeline.json"
)

OUTPUT_MD = V21 / (
    "PREDICTIVE_RISK_ANALYTICS_V21_4.md"
)

HISTORY_WINDOW = 6
MIN_HISTORY = 12
HOLDOUT_START = 90
INTERVAL_ALPHA = 0.05

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
        print("       " + str(detail))

    return passed


def read_json(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Required source missing: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid JSON object: {path.name}"
        )

    return data


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def write_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            data,
            handle,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


def write_csv(path, records):
    if not records:
        raise ValueError("No forecast records to export")

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(records[0]),
        )

        writer.writeheader()
        writer.writerows(records)


def number(value):
    if isinstance(value, bool):
        raise ValueError("Boolean is not a measurement")

    value = float(value)

    if not math.isfinite(value):
        raise ValueError("Non-finite measurement")

    return value


def clamp(value):
    return min(1.0, max(0.0, value))


def rounded(value):
    return round(float(value), 6)


def validate_sources(report, timeline, frames_export):
    check(
        "V21.3 correlation successfully validated",
        report.get("version") == "V21.3"
        and report.get("status") == "THREAT_CORRELATION_PASS"
        and report.get("checks_failed") == 0,
    )

    check(
        "V21.3 source fingerprints verified",
        report.get("source_sha256", {}).get("frames")
        == sha256(FRAMES_FILE),
    )

    check(
        "V21.3 timeline status valid",
        timeline.get("version") == "V21.3"
        and timeline.get("status") == "THREAT_CORRELATION_PASS"
        and timeline.get("simulation_mode") is True
        and timeline.get("is_live") is False,
    )

    check(
        "V20.4 frame export validated",
        frames_export.get("version") == "V20.4"
        and frames_export.get("status")
        == "EVENT_STREAMING_PASS"
        and frames_export.get("simulation_mode") is True
        and frames_export.get("is_live") is False,
    )

    frames = frames_export.get("frames", [])
    correlation = timeline.get("timeline", [])

    check(
        "120 source frames available",
        len(frames) == 120
        and frames_export.get("frame_count") == 120,
    )

    check(
        "120 correlation records available",
        len(correlation) == 120
        and timeline.get("ticks") == 120,
    )

    check(
        "Source timeline sequences match",
        len(frames) == len(correlation)
        and all(
            frame["sequence"] == index
            and corr["tick"] == index
            and frame["timestamp"] == corr["timestamp"]
            for index, (frame, corr)
            in enumerate(zip(frames, correlation))
        ),
    )

    check(
        "All source data is synthetic",
        all(
            frame.get("simulation_mode") is True
            for frame in frames
        ),
    )

    check(
        "No external actions enabled",
        report.get("external_actions_enabled") is False,
    )

    if not all(item["passed"] for item in CHECKS):
        raise ValueError(
            "Source validation failed; forecasting blocked"
        )

    return frames, correlation


def build_series(frames, correlation):
    records = []

    for frame, corr in zip(frames, correlation):
        nodes = frame["network"]["nodes"]

        if len(nodes) != 10:
            raise ValueError("Unexpected network node count")

        risks = [
            number(node["risk_score"])
            for node in nodes
        ]

        if any(not 0 <= risk <= 1 for risk in risks):
            raise ValueError("Node risk out of bounds")

        corr_score = number(
            corr["maximum_correlation_score"]
        )

        if not 0 <= corr_score <= 1:
            raise ValueError("Correlation score out of bounds")

        records.append({
            "tick": frame["sequence"],
            "timestamp": frame["timestamp"],
            "observed_risk": max(risks),
            "correlation_score": corr_score,
            "alert_count": int(corr["source_alerts"]),
            "behavioral_detections": int(
                corr["behavioral_detections"]
            ),
        })

    return records


def predict_next(history):
    """
    One-step-ahead prediction.

    No current or future observation is used
    as part of the prediction target.

    Fixed coefficients, not learned weights.
    """

    last = history[-1]

    recent = [
        row["observed_risk"]
        for row in history[-HISTORY_WINDOW:]
    ]

    mean_risk = statistics.mean(recent)
    previous_risk = last["observed_risk"]

    correlation = last["correlation_score"]

    prediction = clamp(
        0.70 * previous_risk
        + 0.30 * mean_risk
        + 0.03 * correlation
    )

    baseline = previous_risk

    return {
        "prediction": prediction,
        "baseline": baseline,
    }


def produce_forecasts(series):
    forecasts = []

    for target_index in range(MIN_HISTORY, len(series)):
        history = series[:target_index]
        target = series[target_index]

        forecast = predict_next(history)

        prediction = forecast["prediction"]
        baseline = forecast["baseline"]
        actual = target["observed_risk"]

        forecasts.append({
            "target_tick": target_index,
            "source_tick": target_index - 1,
            "timestamp": target["timestamp"],
            "actual_risk": rounded(actual),
            "predicted_risk": rounded(prediction),
            "baseline_risk": rounded(baseline),
            "absolute_error": rounded(
                abs(actual - prediction)
            ),
            "baseline_absolute_error": rounded(
                abs(actual - baseline)
            ),
            "evaluation_split": (
                "holdout"
                if target_index >= HOLDOUT_START
                else "calibration"
            ),
            "simulation_mode": True,
            "prediction_horizon_ticks": 1,
        })

    return forecasts


def empirical_quantile(values, probability):
    """
    Conservative order-statistic quantile.

    Used on calibration errors only.
    """
    ordered = sorted(values)

    if not ordered:
        raise ValueError("No calibration errors")

    rank = math.ceil(
        (len(ordered) + 1) * probability
    )

    index = max(
        0,
        min(len(ordered) - 1, rank - 1),
    )

    return ordered[index]


def add_intervals(forecasts):
    calibration = [
        row["absolute_error"]
        for row in forecasts
        if row["evaluation_split"] == "calibration"
    ]

    if len(calibration) < 20:
        raise ValueError(
            "Insufficient historical calibration data"
        )

    radius = empirical_quantile(
        calibration,
        1.0 - INTERVAL_ALPHA,
    )

    for row in forecasts:
        predicted = row["predicted_risk"]

        row["interval_lower"] = rounded(
            clamp(predicted - radius)
        )

        row["interval_upper"] = rounded(
            clamp(predicted + radius)
        )

        row["within_interval"] = (
            row["interval_lower"]
            <= row["actual_risk"]
            <= row["interval_upper"]
        )

    return radius, len(calibration)


def evaluate(forecasts):
    holdout = [
        row for row in forecasts
        if row["evaluation_split"] == "holdout"
    ]

    if not holdout:
        raise ValueError("Empty chronological holdout")

    errors = [
        row["absolute_error"]
        for row in holdout
    ]

    baseline_errors = [
        row["baseline_absolute_error"]
        for row in holdout
    ]

    actuals = [
        row["actual_risk"]
        for row in holdout
    ]

    predictions = [
        row["predicted_risk"]
        for row in holdout
    ]

    mae = statistics.mean(errors)
    baseline_mae = statistics.mean(baseline_errors)

    rmse = math.sqrt(
        statistics.mean(
            (a - p) ** 2
            for a, p in zip(actuals, predictions)
        )
    )

    coverage = statistics.mean(
        row["within_interval"]
        for row in holdout
    )

    return {
        "holdout_start_tick": HOLDOUT_START,
        "holdout_observations": len(holdout),
        "forecast_mae": rounded(mae),
        "forecast_rmse": rounded(rmse),
        "persistence_baseline_mae": rounded(
            baseline_mae
        ),
        "forecast_beats_persistence_baseline": (
            mae < baseline_mae
        ),
        "nominal_interval_coverage": 0.95,
        "observed_holdout_interval_coverage": rounded(
            coverage
        ),
        "calibration_assumption": (
            "Historical residual distribution is "
            "representative of future errors"
        ),
    }


def build_timeline(series, forecasts):
    indexed = {
        row["target_tick"]: row
        for row in forecasts
    }

    timeline = []

    for row in series:
        tick = row["tick"]
        predicted = indexed.get(tick)

        timeline.append({
            "tick": tick,
            "timestamp": row["timestamp"],
            "observed_risk": rounded(
                row["observed_risk"]
            ),
            "predicted_risk": (
                predicted["predicted_risk"]
                if predicted else None
            ),
            "baseline_risk": (
                predicted["baseline_risk"]
                if predicted else None
            ),
            "interval_lower": (
                predicted["interval_lower"]
                if predicted else None
            ),
            "interval_upper": (
                predicted["interval_upper"]
                if predicted else None
            ),
            "correlation_score": rounded(
                row["correlation_score"]
            ),
            "evaluation_split": (
                predicted["evaluation_split"]
                if predicted else "warmup"
            ),
        })

    return timeline


def validate_forecasts(series, forecasts, timeline, evaluation):
    check(
        "Correct number of evaluated forecasts",
        len(forecasts) == len(series) - MIN_HISTORY,
    )

    check(
        "Thirty chronological holdout forecasts",
        evaluation["holdout_observations"] == 30,
    )

    check(
        "Every forecast uses a previous tick",
        all(
            row["source_tick"]
            == row["target_tick"] - 1
            for row in forecasts
        ),
    )

    check(
        "Forecast values bounded",
        all(
            0 <= row["predicted_risk"] <= 1
            and 0 <= row["actual_risk"] <= 1
            for row in forecasts
        ),
    )

    check(
        "Prediction intervals bounded and ordered",
        all(
            0 <= row["interval_lower"]
            <= row["predicted_risk"]
            <= row["interval_upper"] <= 1
            for row in forecasts
        ),
    )

    check(
        "Metrics are finite",
        all(
            math.isfinite(evaluation[key])
            for key in (
                "forecast_mae",
                "forecast_rmse",
                "persistence_baseline_mae",
                "observed_holdout_interval_coverage",
            )
        ),
    )

    check(
        "Forecasts reproducible",
        forecasts_without_intervals(forecasts)
        == produce_forecasts(series),
    )

    check(
        "No future leakage into early predictions",
        produce_forecasts(
            series[:HOLDOUT_START]
        ) == [
            row for row in produce_forecasts(series)
            if row["target_tick"] < HOLDOUT_START
        ],
    )

    check(
        "Timeline covers 120 ticks",
        len(timeline) == 120
        and [
            row["tick"] for row in timeline
        ] == list(range(120)),
    )

    check(
        "Forecast warmup is explicitly marked",
        all(
            row["evaluation_split"] == "warmup"
            for row in timeline[:MIN_HISTORY]
        ),
    )

    check(
        "Holdout errors are independently evaluated",
        all(
            row["target_tick"] >= HOLDOUT_START
            for row in forecasts
            if row["evaluation_split"] == "holdout"
        ),
    )


def forecasts_without_intervals(forecasts):
    extra = {
        "interval_lower",
        "interval_upper",
        "within_interval",
    }

    return [
        {
            key: value
            for key, value in row.items()
            if key not in extra
        }
        for row in forecasts
    ]


def make_markdown(result):
    e = result["evaluation"]
    c = result["configuration"]

    return f"""# Quantum Cyber Defense Arena

## V21.4 - Predictive Risk Analytics

**Status:** {result['status']}

**Validation:** {result['checks_passed']} passed,
{result['checks_failed']} failed.

### Forecast target

Next-tick maximum observed synthetic
network node risk.

### Method

- Forecast horizon: 1 tick
- Historical mean window: {c['history_window']}
- Minimum history: {c['minimum_history']}
- Holdout begins: tick {c['holdout_start']}
- Fixed causal forecasting coefficients
- No fitted AI or ML model
- No external data

### Chronological evaluation

| Metric | Result |
|---|---:|
| Holdout predictions | {e['holdout_observations']} |
| Forecast MAE | {e['forecast_mae']} |
| Forecast RMSE | {e['forecast_rmse']} |
| Persistence baseline MAE | {e['persistence_baseline_mae']} |
| Forecast beats baseline | {e['forecast_beats_persistence_baseline']} |
| Nominal interval coverage | 95% |
| Observed holdout coverage | {e['observed_holdout_interval_coverage']} |

### Uncertainty

Prediction intervals use absolute errors
from earlier calibration observations.

Coverage is measured on a later
chronological holdout.

The nominal 95% level is not a guarantee
of true coverage because observations
may be temporally dependent.

### Scientific limitations

- All input data are synthetic.
- Source risk scores are simulated.
- Forecast rule is heuristic.
- No fitted machine-learning model is used.
- The evaluation covers one simulated run.
- No independently verified attack labels.
- This is not real-world predictive accuracy.
- No autonomous security actions.

### Next stage

V21.5 - Intelligence Dashboard Integration
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V21.4 - PREDICTIVE RISK ANALYTICS")
    print("=" * 70)

    V21.mkdir(parents=True, exist_ok=True)

    report = read_json(CORRELATION_REPORT)
    correlation_timeline = read_json(
        CORRELATION_TIMELINE
    )
    frames_export = read_json(FRAMES_FILE)

    frames, correlation = validate_sources(
        report,
        correlation_timeline,
        frames_export,
    )

    series = build_series(
        frames,
        correlation,
    )

    forecasts = produce_forecasts(series)

    interval_radius, calibration_count = (
        add_intervals(forecasts)
    )

    evaluation = evaluate(forecasts)

    timeline = build_timeline(
        series,
        forecasts,
    )

    validate_forecasts(
        series,
        forecasts,
        timeline,
        evaluation,
    )

    check(
        "Calibration excludes holdout observations",
        calibration_count == HOLDOUT_START - MIN_HISTORY,
    )

    check(
        "Interval radius nonnegative and finite",
        math.isfinite(interval_radius)
        and interval_radius >= 0,
    )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )
    failed = len(CHECKS) - passed

    status = (
        "PREDICTIVE_RISK_PASS"
        if failed == 0
        else "PREDICTIVE_RISK_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V21.4",
        "module": "Predictive Risk Analytics",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "live_data": False,
        "trained_ai_model_used": False,
        "external_actions_enabled": False,
        "configuration": {
            "history_window": HISTORY_WINDOW,
            "minimum_history": MIN_HISTORY,
            "holdout_start": HOLDOUT_START,
            "horizon_ticks": 1,
            "calibration_observations": calibration_count,
            "interval_alpha": INTERVAL_ALPHA,
            "calibrated_interval_radius": rounded(
                interval_radius
            ),
        },
        "evaluation": evaluation,
        "source_sha256": {
            "correlation_report": sha256(
                CORRELATION_REPORT
            ),
            "correlation_timeline": sha256(
                CORRELATION_TIMELINE
            ),
            "frames": sha256(FRAMES_FILE),
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "next_stage": (
            "V21.5 Intelligence Dashboard Integration"
        ),
    }

    write_json(
        OUTPUT_JSON,
        result,
    )

    if failed == 0:
        write_csv(
            OUTPUT_CSV,
            forecasts,
        )

        write_json(
            OUTPUT_TIMELINE,
            {
                "version": "V21.4",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "ticks": len(timeline),
                "timeline": timeline,
            },
        )

        OUTPUT_MD.write_text(
            make_markdown(result),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V21.4 PREDICTIVE RISK RESULTS")
    print("=" * 70)

    print(f"SIMULATION TICKS: {len(series)}")
    print(
        "HOLDOUT PREDICTIONS:",
        evaluation["holdout_observations"],
    )
    print(
        "FORECAST MAE:",
        evaluation["forecast_mae"],
    )
    print(
        "BASELINE MAE:",
        evaluation["persistence_baseline_mae"],
    )
    print(
        "FORECAST BEATS BASELINE:",
        evaluation["forecast_beats_persistence_baseline"],
    )
    print(
        "HOLDOUT INTERVAL COVERAGE:",
        evaluation["observed_holdout_interval_coverage"],
    )

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {OUTPUT_JSON}")
    print(f"V21.4 RESULT: {status}")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(
            "V21.4 FAILED:",
            f"{type(error).__name__}: {error}",
        )
        sys.exit(1)
