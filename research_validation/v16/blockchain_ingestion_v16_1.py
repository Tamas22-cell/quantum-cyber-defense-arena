
"""
QUANTUM CYBER DEFENSE ARENA
V16.1 - REAL BLOCKCHAIN DATA INGESTION

Ethereum mainnet read-only data collection.

Features:
- Public Ethereum JSON-RPC endpoints
- Real block and transaction data
- Transaction value in ETH
- Gas and fee information
- Basic schema validation
- JSON research output
- RPC fallback and error handling

No wallet connection.
No private keys.
No blockchain transactions submitted.
No threat classification is performed.

Python 3.11+ - standard library only.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "16.1.0"

HERE = Path(__file__).resolve().parent

OUTPUT_FILE = (
    HERE / "blockchain_ingestion_v16_1_results.json"
)

# Public endpoints can impose rate limits or change
# their access policies without notice.
RPC_ENDPOINTS = (
    "https://ethereum-rpc.publicnode.com",
    "https://eth.llamarpc.com",
    "https://cloudflare-eth.com",
)

MAX_TRANSACTIONS = 20

TIMEOUT_SECONDS = 12

NETWORK = "ethereum-mainnet"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def hex_to_int(value: Any) -> int:
    if not isinstance(value, str):
        raise ValueError(
            f"Expected hex string, got {type(value).__name__}"
        )

    if not value.startswith("0x"):
        raise ValueError(
            f"Invalid Ethereum hex value: {value}"
        )

    return int(value, 16)


def wei_to_eth(wei: int) -> str:
    return f"{wei / 10**18:.9f}"


def wei_to_gwei(wei: int) -> str:
    return f"{wei / 10**9:.6f}"


def rpc_request(
    endpoint: str,
    method: str,
    params: list[Any],
) -> Any:

    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "QuantumCyberDefenseArena/16.1",
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=TIMEOUT_SECONDS,
    ) as response:
        payload = json.loads(
            response.read().decode("utf-8")
        )

    if not isinstance(payload, dict):
        raise ValueError("Invalid RPC response.")

    if "error" in payload:
        raise RuntimeError(
            f"RPC error: {payload['error']}"
        )

    if "result" not in payload:
        raise ValueError(
            "RPC response has no result."
        )

    return payload["result"]


def get_block() -> tuple[dict, str]:

    errors = []

    for endpoint in RPC_ENDPOINTS:
        print(f"Trying Ethereum RPC: {endpoint}")

        try:
            chain_id = rpc_request(
                endpoint,
                "eth_chainId",
                [],
            )

            if hex_to_int(chain_id) != 1:
                raise ValueError(
                    "RPC endpoint is not Ethereum mainnet."
                )

            block = rpc_request(
                endpoint,
                "eth_getBlockByNumber",
                ["latest", True],
            )

            if not isinstance(block, dict):
                raise ValueError(
                    "RPC did not return a block object."
                )

            required = (
                "number",
                "hash",
                "timestamp",
                "transactions",
            )

            missing = [
                key
                for key in required
                if key not in block
            ]

            if missing:
                raise ValueError(
                    f"Missing block fields: {missing}"
                )

            if not isinstance(
                block["transactions"],
                list,
            ):
                raise ValueError(
                    "Invalid block transaction list."
                )

            print("Ethereum RPC connected.")
            return block, endpoint

        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
            ValueError,
            RuntimeError,
            json.JSONDecodeError,
        ) as error:
            errors.append(
                f"{endpoint}: {error}"
            )
            print(f"Endpoint failed: {error}")

    raise RuntimeError(
        "All Ethereum RPC endpoints failed.\n"
        + "\n".join(errors)
    )


def normalize_transaction(
    transaction: dict[str, Any],
) -> dict[str, Any]:

    required = (
        "hash",
        "from",
        "value",
        "gas",
        "nonce",
    )

    for key in required:
        if key not in transaction:
            raise ValueError(
                f"Transaction missing field: {key}"
            )

    value_wei = hex_to_int(
        transaction["value"]
    )

    gas_limit = hex_to_int(
        transaction["gas"]
    )

    nonce = hex_to_int(
        transaction["nonce"]
    )

    gas_price = transaction.get("gasPrice")

    max_fee = transaction.get("maxFeePerGas")

    max_priority_fee = transaction.get(
        "maxPriorityFeePerGas"
    )

    return {
        "transaction_hash": transaction["hash"],
        "from_address": transaction["from"],
        "to_address": transaction.get("to"),
        "value_wei": str(value_wei),
        "value_eth": wei_to_eth(value_wei),
        "gas_limit": gas_limit,
        "nonce": nonce,
        "gas_price_gwei": (
            wei_to_gwei(hex_to_int(gas_price))
            if gas_price is not None
            else None
        ),
        "max_fee_per_gas_gwei": (
            wei_to_gwei(hex_to_int(max_fee))
            if max_fee is not None
            else None
        ),
        "max_priority_fee_gwei": (
            wei_to_gwei(
                hex_to_int(max_priority_fee)
            )
            if max_priority_fee is not None
            else None
        ),
        "transaction_type": (
            hex_to_int(transaction["type"])
            if transaction.get("type") is not None
            else None
        ),
        "classification": "NOT_EVALUATED",
    }


def main() -> None:

    print()
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA V16.1")
    print("REAL BLOCKCHAIN DATA INGESTION")
    print("=" * 70)

    print()
    print("Network: Ethereum Mainnet")
    print("Mode: READ ONLY")
    print()

    try:
        block, endpoint = get_block()

        block_number = hex_to_int(
            block["number"]
        )

        timestamp = hex_to_int(
            block["timestamp"]
        )

        block_time = datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        ).isoformat()

        all_transactions = block["transactions"]

        selected_transactions = (
            all_transactions[:MAX_TRANSACTIONS]
        )

        processed = []
        skipped = []

        for index, transaction in enumerate(
            selected_transactions
        ):
            try:
                if not isinstance(transaction, dict):
                    raise ValueError(
                        "Transaction is not a JSON object."
                    )

                processed.append(
                    normalize_transaction(
                        transaction
                    )
                )

            except (ValueError, KeyError, TypeError) as error:
                skipped.append(
                    {
                        "index": index,
                        "reason": str(error),
                    }
                )

        if not processed:
            raise RuntimeError(
                "No valid transaction could be processed."
            )

        base_fee = block.get(
            "baseFeePerGas"
        )

        report = {
            "project": "Quantum Cyber Defense Arena",
            "version": VERSION,
            "module": "Real Blockchain Data Ingestion",
            "mode": "READ_ONLY_PUBLIC_BLOCKCHAIN",
            "network": NETWORK,
            "collected_at": utc_now(),
            "rpc_endpoint": endpoint,
            "block": {
                "number": block_number,
                "hash": block["hash"],
                "timestamp": timestamp,
                "datetime_utc": block_time,
                "transaction_count": len(
                    all_transactions
                ),
                "base_fee_gwei": (
                    wei_to_gwei(
                        hex_to_int(base_fee)
                    )
                    if base_fee is not None
                    else None
                ),
            },
            "collection": {
                "selection": "first_transactions_in_block",
                "requested_limit": MAX_TRANSACTIONS,
                "processed": len(processed),
                "skipped": len(skipped),
                "errors": skipped,
            },
            "transactions": processed,
            "limitations": [
                "Public RPC availability is not guaranteed.",
                "Only one block is sampled.",
                "Only the first transactions are retained.",
                "Gas limit is not actual gas used.",
                "Transaction receipt status is not fetched.",
                "No historical labeling is performed.",
                "No AI model is executed.",
                "No threat classification is performed.",
                "No blockchain transaction is submitted.",
            ],
        }

        OUTPUT_FILE.write_text(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print()
        print("-" * 70)
        print("REAL ETHEREUM BLOCK")
        print("-" * 70)

        print("Block number:", block_number)
        print("Block hash:", block["hash"])
        print("Block time:", block_time)

        print(
            "Transactions in block:",
            len(all_transactions),
        )

        print(
            "Transactions processed:",
            len(processed),
        )

        print()
        print("SAMPLE TRANSACTIONS")
        print("-" * 70)

        for transaction in processed[:5]:
            print()
            print(
                "Hash:",
                transaction["transaction_hash"],
            )
            print(
                "Value:",
                transaction["value_eth"],
                "ETH",
            )
            print(
                "Gas limit:",
                transaction["gas_limit"],
            )

        print()
        print("=" * 70)
        print("V16.1 REAL BLOCKCHAIN INGESTION COMPLETED")
        print("=" * 70)

        print()
        print("RESULTS SAVED TO:")
        print(OUTPUT_FILE)

        print()
        print(
            "NOTE: Real public blockchain data. "
            "No attack detection or wallet operations."
        )

    except Exception as error:
        print()
        print("V16.1 DATA INGESTION FAILED")
        print(str(error))
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
