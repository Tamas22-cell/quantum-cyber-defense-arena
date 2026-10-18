
"""
Quantum Cyber Defense Arena
Threat Simulation Engine V2

Generates simulated blockchain security events
with machine-learning-compatible telemetry.

Simulation only — not real blockchain transactions.
"""

import json
import random
import time
from datetime import datetime, timezone
from uuid import uuid4


THREAT_TYPES = [
    "SUSPICIOUS_TRANSACTION",
    "WALLET_ANOMALY",
    "UNUSUAL_NETWORK_ACTIVITY",
    "SMART_CONTRACT_ALERT",
    "LARGE_TOKEN_TRANSFER",
]

NETWORKS = [
    "Ethereum",
    "Polygon",
    "Arbitrum",
    "Base",
]


def generate_threat() -> dict:
    # Simulated baseline traffic with occasional outliers.
    suspicious = random.random() < 0.12

    if suspicious:
        transaction_value = round(
            random.uniform(10_000, 250_000), 2
        )
        transactions_per_minute = random.randint(100, 850)
        failed_transaction_ratio = round(
            random.uniform(0.50, 0.95), 4
        )
        gas_spike_ratio = round(
            random.uniform(3.0, 12.0), 4
        )
        unique_counterparties = random.randint(60, 350)
    else:
        transaction_value = round(
            random.lognormvariate(4.0, 0.8), 2
        )
        transactions_per_minute = max(
            0, round(random.gauss(12, 3.5))
        )
        failed_transaction_ratio = round(
            random.betavariate(2, 25), 4
        )
        gas_spike_ratio = round(
            random.lognormvariate(0, 0.2), 4
        )
        unique_counterparties = max(
            0, round(random.gauss(8, 3))
        )

    # Rule-based risk score, separate from ML inference.
    risk_score = random.randint(80, 100) if suspicious else (
        random.randint(1, 59)
    )

    if risk_score >= 80:
        severity = "CRITICAL"
    elif risk_score >= 60:
        severity = "HIGH"
    elif risk_score >= 35:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    return {
        "id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "network": random.choice(NETWORKS),
        "type": random.choice(THREAT_TYPES),
        "risk_score": risk_score,
        "severity": severity,
        "source": f"0x{random.getrandbits(160):040x}",
        "destination": f"0x{random.getrandbits(160):040x}",
        "transaction_value": transaction_value,
        "transactions_per_minute": transactions_per_minute,
        "failed_transaction_ratio": failed_transaction_ratio,
        "gas_spike_ratio": gas_spike_ratio,
        "unique_counterparties": unique_counterparties,
        "simulation_label": (
            "INJECTED_ANOMALY" if suspicious else "BASELINE"
        ),
        "mode": "SIMULATION",
    }


def main() -> None:
    print("=" * 55)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("THREAT SIMULATION ENGINE V2")
    print("=" * 55)
    print("SIMULATED EVENTS — NOT REAL ATTACKS")
    print("-" * 55)

    try:
        while True:
            event = generate_threat()
            print(json.dumps(event, indent=2))
            print("-" * 55)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nSimulation stopped.")


if __name__ == "__main__":
    main()
