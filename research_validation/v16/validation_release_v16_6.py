
"""
Quantum Cyber Defense Arena
V16.6 — Blockchain Intelligence Validation & Research Release

Validates:
- V16.1–V16.4 Python modules and saved JSON artifacts
- Ethereum blockchain metadata in block.number
- Transaction sample metadata
- Research CSV files
- React V16.5 dashboard component
- Frontend/research JSON file consistency

This validator does NOT prove anomaly detection accuracy,
execute quantum circuits, or verify live blockchain data.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
V16_DIR = PROJECT_ROOT / "research_validation" / "v16"
PUBLIC_DIR = PROJECT_ROOT / "frontend" / "public" / "v16"

COMPONENT = (
    PROJECT_ROOT
    / "frontend"
    / "src"
    / "components"
    / "BlockchainIntelligenceV16_5.tsx"
)

REPORT_PATH = (
    V16_DIR / "validation_release_v16_6_results.json"
)

MODULES = {
    "V16.1": (
        "blockchain_ingestion_v16_1.py",
        "blockchain_ingestion_v16_1_results.json",
    ),
    "V16.2": (
        "transaction_features_v16_2.py",
        "transaction_features_v16_2_results.json",
    ),
    "V16.3": (
        "blockchain_anomaly_v16_3.py",
        "blockchain_anomaly_v16_3_results.json",
    ),
    "V16.4": (
        "ai_quantum_integration_v16_4.py",
        "ai_quantum_integration_v16_4_results.json",
    ),
}

CSV_FILES = [
    "transaction_features_v16_2.csv",
    "blockchain_anomaly_v16_3.csv",
    "ai_quantum_integration_v16_4.csv",
]

PUBLIC_JSON_FILES = [
    "blockchain_ingestion_v16_1_results.json",
    "blockchain_anomaly_v16_3_results.json",
    "ai_quantum_integration_v16_4_results.json",
]

checks: list[dict[str, Any]] = []


def add_check(
    name: str,
    passed: bool,
    details: str = "",
) -> None:
    checks.append(
        {
            "name": name,
            "passed": bool(passed),
            "details": details,
        }
    )

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")

    if details:
        print(f"       {details}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(65536),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def read_json(path: Path) -> Any | None:
    if not path.is_file():
        add_check(
            f"JSON exists: {path.name}",
            False,
            "Required JSON file is missing.",
        )
        return None

    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
        ) as file:
            data = json.load(file)

    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
    ) as error:
        add_check(
            f"JSON valid: {path.name}",
            False,
            str(error),
        )
        return None

    valid = isinstance(data, (dict, list)) and bool(data)

    add_check(
        f"JSON valid: {path.name}",
        valid,
        f"Root type: {type(data).__name__}",
    )

    return data if valid else None


def validate_modules() -> dict[str, Any]:
    print("\n=== V16 RESEARCH MODULES ===")

    results: dict[str, Any] = {}

    for version, (
        script_name,
        result_name,
    ) in MODULES.items():

        script_path = V16_DIR / script_name
        result_path = V16_DIR / result_name

        exists = (
            script_path.is_file()
            and script_path.stat().st_size > 0
        )

        add_check(
            f"{version} Python module",
            exists,
            str(script_path.relative_to(PROJECT_ROOT)),
        )

        data = read_json(result_path)

        if data is not None:
            results[version] = data

    return results


def validate_ingestion(data: Any | None) -> None:
    print("\n=== BLOCKCHAIN INGESTION ===")

    if not isinstance(data, dict):
        add_check(
            "Ethereum block metadata",
            False,
            "V16.1 JSON root is not a valid object.",
        )
        add_check(
            "Transaction metadata",
            False,
            "V16.1 JSON unavailable.",
        )
        return

    block = data.get("block", {})
    collection = data.get("collection", {})

    if not isinstance(block, dict):
        block = {}

    if not isinstance(collection, dict):
        collection = {}

    block_number = block.get("number")

    if isinstance(block_number, str):
        try:
            block_number = int(block_number, 0)
        except ValueError:
            try:
                block_number = int(block_number)
            except ValueError:
                block_number = None

    valid_block = (
        isinstance(block_number, int)
        and not isinstance(block_number, bool)
        and block_number >= 0
    )

    add_check(
        "Ethereum block metadata",
        valid_block,
        (
            f"Block number: {block_number}"
            if valid_block
            else "Invalid or missing block.number.",
        ),
    )

    transaction_count = block.get("transaction_count")
    processed = collection.get("processed")

    valid_transactions = (
        isinstance(transaction_count, int)
        and not isinstance(transaction_count, bool)
        and transaction_count >= 0
        and isinstance(processed, int)
        and not isinstance(processed, bool)
        and 0 < processed <= transaction_count
    )

    add_check(
        "Transaction metadata",
        valid_transactions,
        (
            f"Block transactions: {transaction_count}; "
            f"processed: {processed}"
        ),
    )


def validate_csv_files() -> None:
    print("\n=== RESEARCH CSV DATA ===")

    for filename in CSV_FILES:
        path = V16_DIR / filename

        if not path.is_file():
            add_check(
                f"CSV integrity: {filename}",
                False,
                "File not found.",
            )
            continue

        try:
            with path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as file:
                reader = csv.reader(file)
                header = next(reader, None)

                row_count = 0
                consistent = bool(header) and all(
                    column.strip()
                    for column in header
                )

                for row in reader:
                    row_count += 1

                    if not header or len(row) != len(header):
                        consistent = False

            passed = bool(consistent) and row_count > 0

            add_check(
                f"CSV integrity: {filename}",
                passed,
                (
                    f"Rows: {row_count}, "
                    f"columns: {len(header) if header else 0}"
                ),
            )

        except (
            OSError,
            UnicodeError,
            csv.Error,
        ) as error:
            add_check(
                f"CSV integrity: {filename}",
                False,
                str(error),
            )


def validate_frontend() -> None:
    print("\n=== FRONTEND DATA INTEGRATION ===")

    component_exists = (
        COMPONENT.is_file()
        and COMPONENT.stat().st_size > 0
    )

    add_check(
        "V16.5 React dashboard component",
        component_exists,
        str(COMPONENT.relative_to(PROJECT_ROOT)),
    )

    for filename in PUBLIC_JSON_FILES:
        source = V16_DIR / filename
        public = PUBLIC_DIR / filename

        if not source.is_file() or not public.is_file():
            add_check(
                f"Frontend JSON sync: {filename}",
                False,
                "Research or frontend file missing.",
            )
            continue

        try:
            source_hash = sha256_file(source)
            public_hash = sha256_file(public)

            identical = source_hash == public_hash

            add_check(
                f"Frontend JSON sync: {filename}",
                identical,
                (
                    f"SHA-256: {source_hash[:16]}..."
                    if identical
                    else "File hashes do not match."
                ),
            )

        except OSError as error:
            add_check(
                f"Frontend JSON sync: {filename}",
                False,
                str(error),
            )


def save_report() -> dict[str, Any]:
    failed = sum(
        not item["passed"]
        for item in checks
    )

    passed = len(checks) - failed

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V16.6",
        "module": "Blockchain Intelligence Validation",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "release_validation": (
            "PASS" if failed == 0 else "FAIL"
        ),
        "checks_total": len(checks),
        "checks_passed": passed,
        "checks_failed": failed,
        "validation_scope": (
            "Saved research artifact integrity, "
            "Ethereum block metadata, CSV structure, "
            "and frontend JSON consistency."
        ),
        "limitations": [
            "Blockchain RPC responses are not independently verified.",
            "Only saved research results are inspected.",
            "Detection accuracy is not evaluated.",
            "Anomalies are not confirmed cyberattacks.",
            "Quantum computation is not executed.",
            "React production build is not executed.",
            "Production deployment is not tested.",
        ],
        "checks": checks,
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return report


def main() -> int:
    print("=" * 64)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V16.6 — BLOCKCHAIN INTELLIGENCE VALIDATION")
    print("=" * 64)

    results = validate_modules()
    validate_ingestion(results.get("V16.1"))
    validate_csv_files()
    validate_frontend()

    report = save_report()

    print("\n" + "=" * 64)
    print("FINAL VALIDATION RESULTS")
    print("=" * 64)

    print(f"CHECKS TOTAL:  {report['checks_total']}")
    print(f"CHECKS PASSED: {report['checks_passed']}")
    print(f"CHECKS FAILED: {report['checks_failed']}")

    print(
        "RELEASE VALIDATION:",
        report["release_validation"],
    )

    print(f"\nSaved report: {REPORT_PATH}")

    print(
        "\nNOTE: PASS validates saved artifacts only, "
        "not detection accuracy or production security."
    )

    return (
        0
        if report["checks_failed"] == 0
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())
