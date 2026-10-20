
"""
QUANTUM CYBER DEFENSE ARENA
V21.6 - ADVANCED THREAT INTELLIGENCE RESEARCH RELEASE

Validates:
 V21.1 - Intelligence Architecture
 V21.2 - Behavioral Anomaly Detection
 V21.3 - Multi-Agent Threat Correlation
 V21.4 - Predictive Risk Analytics
 V21.5 - Intelligence Dashboard Integration

Outputs:
 - advanced_threat_intelligence_release_v21_6_results.json
 - V21_RESEARCH_RELEASE.md
 - frontend/public/v21/release_summary.json

Standard Python library only.
Research validation, not production security certification.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V20 = ROOT / "research_validation" / "v20"
V21 = ROOT / "research_validation" / "v21"
PUBLIC = ROOT / "frontend" / "public" / "v21"

FILES = {
    "architecture": V21 / "threat_intelligence_architecture_v21_1_results.json",
    "behavior": V21 / "behavioral_anomaly_detection_v21_2_results.json",
    "correlation": V21 / "multi_agent_threat_correlation_v21_3_results.json",
    "prediction": V21 / "predictive_risk_analytics_v21_4_results.json",
    "dashboard": V21 / "intelligence_dashboard_integration_v21_5_results.json",
    "behavior_timeline": V21 / "behavioral_anomaly_detection_v21_2_timeline.json",
    "correlation_timeline": V21 / "multi_agent_threat_correlation_v21_3_timeline.json",
    "prediction_timeline": V21 / "predictive_risk_analytics_v21_4_timeline.json",
    "source_frames": V20 / "event_streaming_v20_4_frames.json",
    "dashboard_data": PUBLIC / "intelligence_data.json",
    "dashboard_html": PUBLIC / "dashboard.html",
}

EXPECTED = {
    "architecture": ("V21.1", "THREAT_INTELLIGENCE_ARCHITECTURE_PASS"),
    "behavior": ("V21.2", "BEHAVIORAL_ANOMALY_PASS"),
    "correlation": ("V21.3", "THREAT_CORRELATION_PASS"),
    "prediction": ("V21.4", "PREDICTIVE_RISK_PASS"),
    "dashboard": ("V21.5", "DASHBOARD_INTEGRATION_PASS"),
}

RESULT_FILE = V21 / (
    "advanced_threat_intelligence_release_v21_6_results.json"
)
DOCUMENT_FILE = V21 / "V21_RESEARCH_RELEASE.md"
SUMMARY_FILE = PUBLIC / "release_summary.json"

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


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def sha256_object(obj):
    raw = json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as handle:
        obj = json.load(handle)

    if not isinstance(obj, dict):
        raise ValueError(
            f"Expected JSON object: {path.name}"
        )

    return obj


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(
            obj,
            handle,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


def number(value):
    if isinstance(value, bool):
        raise ValueError("Boolean is not a numeric value")

    result = float(value)

    if not math.isfinite(result):
        raise ValueError("Non-finite numeric value")

    return result


def close(a, b, tolerance=1e-5):
    return math.isclose(
        number(a),
        number(b),
        rel_tol=tolerance,
        abs_tol=tolerance,
    )


def load_inputs():
    reports = {}

    for key, path in FILES.items():
        exists = path.is_file()

        check(
            f"Source available: {key}",
            exists,
            str(path),
        )

        if not exists:
            continue

        try:
            if path.suffix == ".json":
                reports[key] = read_json(path)

            elif path.suffix == ".html":
                reports[key] = path.read_text(
                    encoding="utf-8-sig"
                )

            check(
                f"Source readable: {key}",
                True,
            )

        except (OSError, ValueError) as error:
            check(
                f"Source readable: {key}",
                False,
                str(error),
            )

    return reports


def validate_versions(reports):
    for key, (version, status) in EXPECTED.items():
        report = reports[key]

        check(
            f"{key}: version correct",
            report.get("version") == version,
        )

        check(
            f"{key}: PASS result",
            report.get("status") == status,
        )

        previous_checks = report.get("checks", [])

        check(
            f"{key}: internal checks valid",
            isinstance(previous_checks, list)
            and len(previous_checks) > 0
            and report.get("checks_failed") == 0
            and report.get("checks_passed")
            == len(previous_checks)
            and all(
                isinstance(item, dict)
                and item.get("passed") is True
                for item in previous_checks
            ),
        )

    expected_timelines = {
        "behavior_timeline": ("V21.2", "BEHAVIORAL_ANOMALY_PASS"),
        "correlation_timeline": ("V21.3", "THREAT_CORRELATION_PASS"),
        "prediction_timeline": ("V21.4", "PREDICTIVE_RISK_PASS"),
    }

    for key, (version, status) in expected_timelines.items():
        report = reports[key]

        check(
            f"{key}: validated export",
            report.get("version") == version
            and report.get("status") == status
            and report.get("simulation_mode") is True
            and report.get("is_live") is False,
        )

    frames = reports["source_frames"]

    check(
        "V20.4 source frames passed",
        frames.get("version") == "V20.4"
        and frames.get("status") == "EVENT_STREAMING_PASS"
        and frames.get("simulation_mode") is True
        and frames.get("is_live") is False,
    )

    exported = reports["dashboard_data"]

    check(
        "V21.5 frontend data passed",
        exported.get("version") == "V21.5"
        and exported.get("status") == "DASHBOARD_INTEGRATION_PASS"
        and exported.get("simulation_mode") is True
        and exported.get("is_live") is False,
    )


def validate_integrity(reports):
    architecture = reports["architecture"]
    model = architecture.get("architecture")

    check(
        "V21.1 architecture fingerprint",
        isinstance(model, dict)
        and sha256_object(model)
        == architecture.get("architecture_sha256"),
    )

    behavior_sources = reports["behavior"].get(
        "source_sha256", {}
    )

    check(
        "V21.2 architecture fingerprint",
        behavior_sources.get("architecture")
        == sha256_file(FILES["architecture"]),
    )

    check(
        "V21.2 frame fingerprint",
        behavior_sources.get("frames")
        == sha256_file(FILES["source_frames"]),
    )

    correlation_sources = reports["correlation"].get(
        "source_sha256", {}
    )

    check(
        "V21.3 behavioral report fingerprint",
        correlation_sources.get("behavior_report")
        == sha256_file(FILES["behavior"]),
    )

    check(
        "V21.3 frame fingerprint",
        correlation_sources.get("frames")
        == sha256_file(FILES["source_frames"]),
    )

    prediction_sources = reports["prediction"].get(
        "source_sha256", {}
    )

    for source_key, file_key in (
        ("correlation_report", "correlation"),
        ("correlation_timeline", "correlation_timeline"),
        ("frames", "source_frames"),
    ):
        check(
            f"V21.4 fingerprint: {source_key}",
            prediction_sources.get(source_key)
            == sha256_file(FILES[file_key]),
        )

    dashboard_sources = reports["dashboard"].get(
        "source_sha256", {}
    )

    for source_key, file_key in (
        ("frames", "source_frames"),
        ("behavior_report", "behavior"),
        ("behavior", "behavior_timeline"),
        ("correlation_report", "correlation"),
        ("correlation", "correlation_timeline"),
        ("prediction_report", "prediction"),
        ("prediction", "prediction_timeline"),
    ):
        check(
            f"V21.5 fingerprint: {source_key}",
            dashboard_sources.get(source_key)
            == sha256_file(FILES[file_key]),
        )


def validate_timelines(reports):
    frames = reports["source_frames"]["frames"]
    behavior = reports["behavior_timeline"]["timeline"]
    correlation = reports["correlation_timeline"]["timeline"]
    prediction = reports["prediction_timeline"]["timeline"]
    combined = reports["dashboard_data"]["frames"]

    groups = [
        frames, behavior, correlation,
        prediction, combined,
    ]

    check(
        "Five complete 120-tick data series",
        all(
            isinstance(group, list)
            and len(group) == 120
            for group in groups
        ),
    )

    check(
        "All timestamps and tick indices aligned",
        all(
            frames[i]["sequence"]
            == behavior[i]["tick"]
            == correlation[i]["tick"]
            == prediction[i]["tick"]
            == combined[i]["tick"]
            == i
            and len({
                frames[i]["timestamp"],
                behavior[i]["timestamp"],
                correlation[i]["timestamp"],
                prediction[i]["timestamp"],
                combined[i]["timestamp"],
            }) == 1
            for i in range(120)
        ),
    )

    check(
        "Network topology preserved",
        all(
            len(frame["network"]["nodes"]) == 10
            and len(frame["network"]["links"]) == 11
            and len(item["nodes"]) == 10
            and len(item["links"]) == 11
            for frame, item in zip(frames, combined)
        ),
    )

    check(
        "Dashboard nodes match simulation",
        all(
            frame["network"]["nodes"] == item["nodes"]
            for frame, item in zip(frames, combined)
        ),
    )

    check(
        "Dashboard links match simulation",
        all(
            frame["network"]["links"] == item["links"]
            for frame, item in zip(frames, combined)
        ),
    )

    check(
        "Dashboard alerts match simulation",
        all(
            frame["alerts"] == item["alerts"]
            for frame, item in zip(frames, combined)
        ),
    )

    check(
        "Behavioral detection totals align",
        all(
            item["behavioral_detections"]
            == source["detections"]
            and item["detected_nodes"]
            == source["detected_nodes"]
            for item, source in zip(combined, behavior)
        ),
    )

    check(
        "Threat correlations align",
        all(
            item["same_tick_correlations"]
            == source["same_tick_correlations"]
            and item["nearby_correlations"]
            == source["nearby_tick_correlations"]
            and close(
                item["correlation_score"],
                source["maximum_correlation_score"],
            )
            for item, source in zip(combined, correlation)
        ),
    )

    check(
        "Observed risk values align",
        all(
            close(item["observed_risk"], source["observed_risk"])
            for item, source in zip(combined, prediction)
        ),
    )

    check(
        "Forecast values align",
        all(
            (
                item["predicted_risk"] is None
                and source["predicted_risk"] is None
            )
            or (
                item["predicted_risk"] is not None
                and source["predicted_risk"] is not None
                and close(
                    item["predicted_risk"],
                    source["predicted_risk"],
                )
            )
            for item, source in zip(combined, prediction)
        ),
    )

    check(
        "Forecast uncertainty intervals align",
        all(
            (
                item["interval_lower"] is None
                and item["interval_upper"] is None
                and source["interval_lower"] is None
                and source["interval_upper"] is None
            )
            or (
                item["interval_lower"] is not None
                and item["interval_upper"] is not None
                and source["interval_lower"] is not None
                and source["interval_upper"] is not None
                and close(
                    item["interval_lower"],
                    source["interval_lower"],
                )
                and close(
                    item["interval_upper"],
                    source["interval_upper"],
                )
            )
            for item, source in zip(combined, prediction)
        ),
    )

    check(
        "Observed risk bounded to zero and one",
        all(
            0 <= number(item["observed_risk"]) <= 1
            for item in combined
        ),
    )

    check(
        "Forecast bounds valid",
        all(
            (
                item["predicted_risk"] is None
                and item["interval_lower"] is None
                and item["interval_upper"] is None
            )
            or (
                item["predicted_risk"] is not None
                and 0 <= number(item["interval_lower"])
                <= number(item["predicted_risk"])
                <= number(item["interval_upper"]) <= 1
            )
            for item in combined
        ),
    )

    check(
        "Warmup and forecast windows valid",
        sum(
            item["predicted_risk"] is None
            for item in combined
        ) == 12
        and sum(
            item["predicted_risk"] is not None
            for item in combined
        ) == 108,
    )

    check(
        "30 holdout observations preserved",
        sum(
            item["evaluation_split"] == "holdout"
            for item in combined
        ) == 30,
    )

    check(
        "Synthetic alerts preserved",
        sum(len(item["alerts"]) for item in combined)
        == reports["correlation"]["metrics"]["source_alerts"],
    )

    return {
        "network_nodes": 10,
        "network_links": 11,
        "simulation_ticks": len(combined),
        "source_alerts": sum(
            len(item["alerts"]) for item in combined
        ),
        "behavioral_detections": sum(
            item["behavioral_detections"]
            for item in combined
        ),
        "same_tick_correlations": sum(
            item["same_tick_correlations"]
            for item in combined
        ),
        "nearby_correlations": sum(
            item["nearby_correlations"]
            for item in combined
        ),
        "forecasts_available": sum(
            item["predicted_risk"] is not None
            for item in combined
        ),
        "holdout_predictions": sum(
            item["evaluation_split"] == "holdout"
            for item in combined
        ),
    }


def validate_dashboard(reports):
    html = reports["dashboard_html"]

    features = {
        "HTML document": "<!DOCTYPE html>",
        "D3 dependency": "d3@7",
        "Network graph": 'id="network"',
        "Risk chart": 'id="chart"',
        "Play/Pause": 'id="play"',
        "Restart": 'id="restart"',
        "Speed control": 'id="speed"',
        "Timeline slider": 'id="slider"',
        "Intelligence data loader": "intelligence_data.json",
        "Simulation label": "SIMULATED",
        "Threat event feed": 'id="events"',
    }

    for name, marker in features.items():
        check(
            f"Dashboard feature: {name}",
            marker in html,
        )

    check(
        "Dashboard closes HTML document",
        "</html>" in html,
    )

    check(
        "Existing V20 dashboard preserved",
        (
            ROOT / "frontend" / "public"
            / "v20" / "dashboard.html"
        ).is_file(),
    )


def validate_research_limits(reports):
    check(
        "Synthetic-only architecture",
        reports["architecture"].get("simulation_mode") is True
        and reports["architecture"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "Behavior analysis uses synthetic data",
        reports["behavior"].get("simulation_mode") is True
        and reports["behavior"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "Correlation uses no external actions",
        reports["correlation"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "Prediction is not live monitoring",
        reports["prediction"].get("live_data") is False
        and reports["prediction"].get(
            "trained_ai_model_used"
        ) is False,
    )

    check(
        "Dashboard integration is synthetic",
        reports["dashboard"].get("simulation_mode") is True
        and reports["dashboard"].get(
            "live_network_monitoring"
        ) is False,
    )

    evaluation = reports["prediction"].get(
        "evaluation", {}
    )

    check(
        "Prediction reports holdout metrics",
        evaluation.get("holdout_observations") == 30
        and all(
            key in evaluation
            for key in (
                "forecast_mae",
                "forecast_rmse",
                "persistence_baseline_mae",
                "observed_holdout_interval_coverage",
            )
        ),
    )


def source_manifest():
    return {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for name, path in FILES.items()
        if path.is_file()
    }


def create_markdown(report, reports):
    metrics = report["metrics"]
    forecast = reports["prediction"]["evaluation"]

    return f"""# Quantum Cyber Defense Arena

## V21 - Advanced Threat Intelligence Research Release

**Version:** V21.6

**Status:** {report['status']}

**Checks passed:** {report['checks_passed']}

**Checks failed:** {report['checks_failed']}

### Completed modules

| Version | Research component |
|---|---|
| V21.1 | Threat Intelligence Architecture |
| V21.2 | Behavioral Anomaly Detection |
| V21.3 | Multi-Agent Threat Correlation |
| V21.4 | Predictive Risk Analytics |
| V21.5 | Intelligence Dashboard Integration |
| V21.6 | Research Validation & Release |

### Network simulation

- Network nodes: {metrics['network_nodes']}
- Network links: {metrics['network_links']}
- Simulation ticks: {metrics['simulation_ticks']}
- Synthetic alerts: {metrics['source_alerts']}

### Intelligence analysis

- Behavioral detections: {metrics['behavioral_detections']}
- Same-tick correlations: {metrics['same_tick_correlations']}
- Nearby correlations: {metrics['nearby_correlations']}
- Forecast observations: {metrics['forecasts_available']}
- Chronological holdout forecasts: {metrics['holdout_predictions']}

### Forecast evaluation

| Metric | Value |
|---|---|
| Forecast MAE | {forecast['forecast_mae']} |
| Forecast RMSE | {forecast['forecast_rmse']} |
| Persistence baseline MAE | {forecast['persistence_baseline_mae']} |
| Forecast beats baseline | {forecast['forecast_beats_persistence_baseline']} |
| Holdout interval coverage | {forecast['observed_holdout_interval_coverage']} |

### Interactive dashboard

`frontend/public/v21/dashboard.html`

The V21 dashboard uses saved synthetic results.
It includes a network visualization, intelligence
metrics, a risk forecast chart, and replay controls.

The V20 dashboard remains a separate page.

### Research validation

SHA-256 fingerprints in the V21.6 release JSON
identify the input research artifacts.

Checks verify saved data integrity,
cross-module alignment and required HTML markers.

These checks do not establish browser compatibility,
web performance, security certification or
production readiness.

### Scientific limitations

- Synthetic network observations only
- No independently verified real attack labels
- Behavioral detection is statistical, not trained AI
- Multi-agent roles are deterministic
- Risk forecasting uses a fixed heuristic
- No demonstrated real-world prediction accuracy
- No external defensive or offensive actions
- Forecast uncertainty is not guaranteed coverage

### Next development stage

V22 - Next-Generation Cyber Defense Research
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V21.6 - ADVANCED THREAT INTELLIGENCE RELEASE")
    print("=" * 70)

    V21.mkdir(parents=True, exist_ok=True)

    reports = load_inputs()
    metrics = {}
    error = None

    if len(reports) == len(FILES):
        try:
            validate_versions(reports)
            validate_integrity(reports)
            validate_research_limits(reports)
            metrics = validate_timelines(reports)
            validate_dashboard(reports)

        except (
            OSError, ValueError, KeyError,
            TypeError, IndexError
        ) as exc:
            error = f"{type(exc).__name__}: {exc}"
            check(
                "Complete release validation",
                False,
                error,
            )

    else:
        check(
            "All V21 release sources loaded",
            False,
            f"Loaded {len(reports)}/{len(FILES)}",
        )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )

    failed = len(CHECKS) - passed

    status = (
        "ADVANCED_THREAT_INTELLIGENCE_RELEASE_PASS"
        if failed == 0 and metrics
        else "ADVANCED_THREAT_INTELLIGENCE_RELEASE_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V21.6",
        "module": "Advanced Threat Intelligence Research Release",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "live_network_monitoring": False,
        "trained_ai_threat_detector": False,
        "external_actions_enabled": False,
        "metrics": metrics,
        "source_manifest": source_manifest(),
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error,
        "limitations": [
            "Synthetic telemetry only.",
            "No independently verified attack labels.",
            "Rule-based correlation and forecasting.",
            "No production threat detection validation.",
            "No live security actions.",
            "HTML marker validation is not a browser test.",
        ],
        "next_stage": (
            "V22 Next-Generation Cyber Defense Research"
        ),
    }

    write_json(
        RESULT_FILE,
        result,
    )

    if status == "ADVANCED_THREAT_INTELLIGENCE_RELEASE_PASS":
        DOCUMENT_FILE.write_text(
            create_markdown(result, reports),
            encoding="utf-8",
        )

        write_json(
            SUMMARY_FILE,
            {
                "project": "Quantum Cyber Defense Arena",
                "version": "V21.6",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "metrics": metrics,
                "checks_passed": passed,
                "checks_failed": failed,
            },
        )

    print()
    print("=" * 70)
    print("V21.6 FINAL RESEARCH RELEASE")
    print("=" * 70)

    if metrics:
        print(
            "NETWORK NODES:",
            metrics["network_nodes"],
        )
        print(
            "NETWORK LINKS:",
            metrics["network_links"],
        )
        print(
            "SIMULATION TICKS:",
            metrics["simulation_ticks"],
        )
        print(
            "BEHAVIORAL DETECTIONS:",
            metrics["behavioral_detections"],
        )
        print(
            "FORECASTS AVAILABLE:",
            metrics["forecasts_available"],
        )

    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")
    print(f"JSON REPORT: {RESULT_FILE}")

    if status == "ADVANCED_THREAT_INTELLIGENCE_RELEASE_PASS":
        print(f"RESEARCH DOCUMENT: {DOCUMENT_FILE}")
        print(f"DASHBOARD SUMMARY: {SUMMARY_FILE}")

    if error:
        print(f"ERROR: {error}")

    print(f"V21.6 RESULT: {status}")
    print("=" * 70)

    return (
        0
        if status == "ADVANCED_THREAT_INTELLIGENCE_RELEASE_PASS"
        else 1
    )


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as exc:
        print()
        print(
            "V21.6 FATAL ERROR:",
            f"{type(exc).__name__}: {exc}",
        )
        sys.exit(1)
