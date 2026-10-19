
"""
QUANTUM CYBER DEFENSE ARENA
V14 - PROFESSIONAL RESEARCH RELEASE

Final release audit and research report generator.

Checks:
- Project structure
- V11 research benchmark
- V11.3 statistical analysis
- V12 robustness benchmark
- V13 real-data experiments
- V13.4 supervised diagnostic
- React dashboard source
- Python source compilation
- Git repository status

Outputs:
- release_v14_results.json
- RESEARCH_REPORT_V14.md

IMPORTANT:
This audit does not change earlier files.
It does not certify cybersecurity effectiveness.
It does not claim quantum computational advantage.
"""

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


VERSION = "14.0.0"

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

JSON_OUTPUT = HERE / "release_v14_results.json"
REPORT_OUTPUT = HERE / "RESEARCH_REPORT_V14.md"

RESEARCH_FILES = {
    "V11 benchmark": (
        "research_validation/v11/"
        "benchmark_v11_results.json"
    ),
    "V11.2 extended benchmark": (
        "research_validation/v11/"
        "benchmark_v11_2_results.json"
    ),
    "V11.3 statistical research": (
        "research_validation/v11/"
        "research_analysis_v11_3_results.json"
    ),
    "V12 robustness testing": (
        "research_validation/v12/"
        "robustness_benchmark_v12_results.json"
    ),
    "V13.1 data preparation": (
        "research_validation/v13/"
        "elliptic_processed/dataset_report.json"
    ),
    "V13.2 real-data validation": (
        "research_validation/v13/"
        "elliptic_validation_v13_2_results.json"
    ),
    "V13.3 model calibration": (
        "research_validation/v13/"
        "model_calibration_v13_3_results.json"
    ),
    "V13.4 model diagnostics": (
        "research_validation/v13/"
        "model_diagnostic_v13_4_results.json"
    ),
}

PROJECT_FILES = {
    "FastAPI application": "main.py",
    "React application": "frontend/src/App.tsx",
    "V11.4 Research Dashboard": (
        "frontend/src/ResearchDashboardV11_4.tsx"
    ),
    "Classical AI detector": (
        "backend/ai_detection/detector.py"
    ),
    "Quantum detector": (
        "backend/quantum_detection/"
        "quantum_detector.py"
    ),
    "V13.4 diagnostic program": (
        "research_validation/v13/"
        "model_diagnostic_v13_4.py"
    ),
}

MODELS = (
    "classical",
    "quantum",
    "hybrid",
)


def heading(text: str) -> None:
    print()
    print("=" * 68)
    print(text)
    print("=" * 68, flush=True)


def load_json(path: Path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as stream:
        return json.load(stream)


def check_project_files() -> dict:
    heading("STEP 1 - PROJECT STRUCTURE")

    results = {}

    for name, relative_path in PROJECT_FILES.items():
        path = ROOT / relative_path
        exists = path.is_file()

        results[name] = {
            "path": relative_path,
            "exists": exists,
        }

        print(
            f"{'PASS' if exists else 'MISSING':7s} "
            f"{name}"
        )

    return results


def check_research_files() -> tuple[dict, dict]:
    heading("STEP 2 - RESEARCH RESULT FILES")

    results = {}
    documents = {}

    for name, relative_path in RESEARCH_FILES.items():
        path = ROOT / relative_path

        if not path.is_file():
            results[name] = {
                "status": "MISSING",
                "path": relative_path,
            }
            print("MISSING:", name)
            continue

        try:
            data = load_json(path)

            if not isinstance(data, dict):
                raise ValueError(
                    "Expected a JSON object."
                )

            documents[name] = data

            results[name] = {
                "status": "PASS",
                "path": relative_path,
                "version": data.get("version"),
            }

            print("PASS:", name)

        except (ValueError, OSError) as error:
            results[name] = {
                "status": "INVALID",
                "path": relative_path,
                "error": str(error),
            }

            print("INVALID:", name, error)

    return results, documents


def get_v11_results(documents: dict) -> dict:
    data = documents.get(
        "V11.3 statistical research",
        {}
    )

    models = data.get("models", {})

    results = {}

    for model in MODELS:
        value = models.get(model, {}).get(
            "mean_f1"
        )

        if value is not None:
            results[model] = float(value)

    return results


def get_v13_2_results(documents: dict) -> dict:
    data = documents.get(
        "V13.2 real-data validation",
        {}
    )

    results = data.get("results", {})

    output = {}

    for model in MODELS:
        if model in results:
            output[model] = {
                key: results[model].get(key)
                for key in (
                    "f1",
                    "precision",
                    "recall",
                    "tp",
                    "tn",
                    "fp",
                    "fn",
                )
            }

    return output


def get_v13_3_results(documents: dict) -> dict:
    data = documents.get(
        "V13.3 model calibration",
        {}
    )

    return data.get(
        "results",
        {},
    ).get(
        "metrics",
        {},
    )


def get_v13_4_results(documents: dict) -> dict:
    data = documents.get(
        "V13.4 model diagnostics",
        {}
    )

    models = data.get("models", {})

    output = {}

    for name, model_data in models.items():
        output[name] = {
            "calibration_f1": model_data.get(
                "calibration_f1"
            ),
            "test_metrics": model_data.get(
                "test_metrics",
                {},
            ),
        }

    return output


def check_python_syntax() -> dict:
    heading("STEP 3 - PYTHON SYNTAX CHECK")

    paths = [
        ROOT / "main.py",
        ROOT / (
            "research_validation/v11/"
            "benchmark_v11.py"
        ),
        ROOT / (
            "research_validation/v12/"
            "robustness_benchmark_v12.py"
        ),
        ROOT / (
            "research_validation/v13/"
            "elliptic_prepare_v13.py"
        ),
        ROOT / (
            "research_validation/v13/"
            "elliptic_validation_v13_2.py"
        ),
        ROOT / (
            "research_validation/v13/"
            "model_calibration_v13_3.py"
        ),
        ROOT / (
            "research_validation/v13/"
            "model_diagnostic_v13_4.py"
        ),
    ]

    results = {}

    for path in paths:
        relative = str(
            path.relative_to(ROOT)
        )

        if not path.is_file():
            results[relative] = "MISSING"
            print("MISSING:", relative)
            continue

        try:
            py_compile.compile(
                str(path),
                doraise=True,
            )

            results[relative] = "PASS"
            print("PASS:", relative)

        except (py_compile.PyCompileError, OSError) as error:
            results[relative] = str(error)
            print("FAIL:", relative)
            print(error)

    return results


def git_information() -> dict:
    heading("STEP 4 - GIT STATUS")

    def command(*args):
        return subprocess.run(
            ["git", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )

    try:
        branch_result = command(
            "branch",
            "--show-current",
        )

        commit_result = command(
            "log",
            "-1",
            "--format=%h %s",
        )

        status_result = command(
            "status",
            "--porcelain",
            "--untracked-files=no",
        )

        if any(
            result.returncode != 0
            for result in (
                branch_result,
                commit_result,
                status_result,
            )
        ):
            print("Git status unavailable.")

            return {
                "available": False,
            }

        branch = branch_result.stdout.strip()
        commit = commit_result.stdout.strip()

        tracked_changes = [
            line
            for line in status_result.stdout.splitlines()
            if line.strip()
        ]

        print("BRANCH:", branch)
        print("LAST COMMIT:", commit)

        print(
            "TRACKED MODIFIED FILES:",
            len(tracked_changes),
        )

        return {
            "available": True,
            "branch": branch,
            "last_commit": commit,
            "tracked_modified_count": len(
                tracked_changes
            ),
            "note": (
                "Untracked files are excluded "
                "from this Git check."
            ),
        }

    except (
        FileNotFoundError,
        OSError,
        subprocess.TimeoutExpired,
    ) as error:
        print("Git check unavailable:", error)

        return {
            "available": False,
            "error": str(error),
        }


def format_percent(value) -> str:
    if value is None:
        return "N/A"

    return f"{float(value) * 100:.2f}%"


def create_report(
    research: dict,
    syntax: dict,
    project: dict,
    git: dict,
    v11: dict,
    v13_2: dict,
    v13_3: dict,
    v13_4: dict,
    release_status: str,
) -> str:

    lines = [
        "# Quantum Cyber Defense Arena",
        "",
        "## V14 - Professional Research Release",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"**Release audit status: {release_status}**",
        "",
        "## Project overview",
        "",
        "Research prototype combining:",
        "",
        "- Cybersecurity monitoring and dashboards",
        "- Classical anomaly detection",
        "- Quantum state-fidelity simulation",
        "- Hybrid decision rules",
        "- Multi-agent AI research components",
        "- Synthetic and real-data evaluation",
        "",
        "## V11.3 - Synthetic benchmark",
        "",
        "| Model | Mean F1 |",
        "|---|---:|",
    ]

    for name in MODELS:
        lines.append(
            f"| {name.title()} | "
            f"{format_percent(v11.get(name))} |"
        )

    lines.extend([
        "",
        "The V11 results use synthetic datasets.",
        "They do not establish real-world accuracy "
        "or quantum computational advantage.",
        "",
        "## V12 - Robustness experiments",
        "",
        f"Result file status: "
        f"**{research.get('V12 robustness testing', {}).get('status', 'MISSING')}**",
        "",
        "V12 tests noise, rare anomalies, "
        "and overlapping synthetic distributions.",
        "A saved report does not by itself prove robustness.",
        "",
        "## V13.2 - Real Elliptic Bitcoin dataset",
        "",
        "| Model | F1 | TP | FP | FN |",
        "|---|---:|---:|---:|---:|",
    ])

    for name in MODELS:
        metric = v13_2.get(name, {})

        lines.append(
            f"| {name.title()} "
            f"| {format_percent(metric.get('f1'))} "
            f"| {metric.get('tp', 'N/A')} "
            f"| {metric.get('fp', 'N/A')} "
            f"| {metric.get('fn', 'N/A')} |"
        )

    lines.extend([
        "",
        "## V13.3 - Calibrated detection",
        "",
        "| Model | F1 | TP | FP | FN |",
        "|---|---:|---:|---:|---:|",
    ])

    for name in (
        "classical",
        "quantum",
        "hybrid_and",
        "hybrid_or",
    ):
        metric = v13_3.get(name, {})

        lines.append(
            f"| {name} "
            f"| {format_percent(metric.get('f1'))} "
            f"| {metric.get('tp', 'N/A')} "
            f"| {metric.get('fp', 'N/A')} "
            f"| {metric.get('fn', 'N/A')} |"
        )

    lines.extend([
        "",
        "## V13.4 - Supervised reference baselines",
        "",
        "| Model | Test F1 | Precision | Recall |",
        "|---|---:|---:|---:|",
    ])

    for name, data in v13_4.items():
        metric = data.get("test_metrics", {})

        lines.append(
            f"| {name} "
            f"| {format_percent(metric.get('f1'))} "
            f"| {format_percent(metric.get('precision'))} "
            f"| {format_percent(metric.get('recall'))} |"
        )

    lines.extend([
        "",
        "The supervised reference models are different "
        "from the original unsupervised detectors.",
        "Their results must not be presented as an "
        "improvement in quantum or hybrid detection.",
        "",
        "## Source-code checks",
        "",
    ])

    for name, result in syntax.items():
        lines.append(
            f"- {name}: {result}"
        )

    lines.extend([
        "",
        "## Project structure",
        "",
    ])

    for name, entry in project.items():
        lines.append(
            f"- {name}: "
            f"{'FOUND' if entry['exists'] else 'MISSING'}"
        )

    lines.extend([
        "",
        "## Git",
        "",
        f"- Branch: {git.get('branch', 'unknown')}",
        f"- Last commit: {git.get('last_commit', 'unknown')}",
        "",
        "## Scientific limitations",
        "",
        "- Earlier high F1 results used synthetic data.",
        "- V13 real-data anomaly detectors performed poorly.",
        "- V13.4 supervised baselines use labeled training data.",
        "- The historical test period was previously inspected.",
        "- Some comparisons use different test sample sizes.",
        "- Test results therefore are not directly equivalent.",
        "- Quantum components run in classical simulation.",
        "- No quantum computational speedup is demonstrated.",
        "- No production cybersecurity certification exists.",
        "- Further independent validation is needed.",
        "",
        "## Release scope",
        "",
        "V14 represents the completion of the planned "
        "research prototype development cycle.",
        "It is not a production security certification.",
        "",
        "## Checks not performed by this script",
        "",
        "- Running FastAPI integration tests",
        "- Building the React frontend",
        "- Testing all interactive dashboard controls",
        "- Dependency and vulnerability scanning",
        "- Verifying the external dataset provenance",
        "- Reproducing the complete benchmarks",
        "- Confirming remote GitHub publication",
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    heading(
        "QUANTUM CYBER DEFENSE ARENA V14"
    )

    project = check_project_files()

    research, documents = check_research_files()

    syntax = check_python_syntax()

    git = git_information()

    heading("STEP 5 - EXTRACTING RESEARCH METRICS")

    v11 = get_v11_results(documents)
    v13_2 = get_v13_2_results(documents)
    v13_3 = get_v13_3_results(documents)
    v13_4 = get_v13_4_results(documents)

    for name, score in v11.items():
        print(
            f"V11 {name.upper():10s}: "
            f"{format_percent(score)}"
        )

    for name, score in v13_2.items():
        print(
            f"V13.2 {name.upper():10s}: "
            f"{format_percent(score.get('f1'))}"
        )

    for name, data in v13_4.items():
        score = data["test_metrics"].get("f1")

        print(
            f"V13.4 {name.upper():20s}: "
            f"{format_percent(score)}"
        )

    missing_project = [
        name
        for name, entry in project.items()
        if not entry["exists"]
    ]

    failed_research = [
        name
        for name, entry in research.items()
        if entry["status"] != "PASS"
    ]

    failed_syntax = [
        name
        for name, status in syntax.items()
        if status != "PASS"
    ]

    audit_passed = not (
        missing_project
        or failed_research
        or failed_syntax
    )

    # This is a limited source/result audit,
    # not a full release certification.
    release_status = (
        "SOURCE_AND_RESULT_AUDIT_PASS"
        if audit_passed
        else "ACTION_REQUIRED"
    )

    report_data = {
        "project": "Quantum Cyber Defense Arena",
        "version": VERSION,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "release_status": release_status,
        "audit_scope": (
            "Source files, Python syntax, "
            "saved research JSON and Git metadata"
        ),
        "project_files": project,
        "research_files": research,
        "python_syntax": syntax,
        "git": git,
        "research_metrics": {
            "v11_synthetic": v11,
            "v13_2_real_data": v13_2,
            "v13_3_calibration": v13_3,
            "v13_4_baselines": v13_4,
        },
        "unverified_checks": [
            "FastAPI runtime and integration tests",
            "React production build",
            "Frontend functionality",
            "Security vulnerability analysis",
            "Independent benchmark reproduction",
            "Remote GitHub publication",
        ],
        "quantum_advantage_proven": False,
        "production_ready_certified": False,
    }

    HERE.mkdir(
        parents=True,
        exist_ok=True,
    )

    JSON_OUTPUT.write_text(
        json.dumps(
            report_data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    REPORT_OUTPUT.write_text(
        create_report(
            research,
            syntax,
            project,
            git,
            v11,
            v13_2,
            v13_3,
            v13_4,
            release_status,
        ),
        encoding="utf-8",
    )

    heading("V14 RELEASE VALIDATION COMPLETED")

    print()
    print("AUDIT STATUS:", release_status)

    print()
    print("JSON REPORT:")
    print(JSON_OUTPUT)

    print()
    print("MARKDOWN REPORT:")
    print(REPORT_OUTPUT)

    print()
    print(
        "NOTE: Full frontend/backend testing "
        "and final Git release remain separate steps."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print()
        print("V14 RELEASE AUDIT FAILED")
        print(
            type(error).__name__,
            str(error),
        )
        sys.exit(1)
