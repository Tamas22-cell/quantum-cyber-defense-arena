
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

NETWORKS = ["Ethereum", "Polygon", "Arbitrum", "Base"]


def generate_threat():
    risk_score = random.randint(1, 100)

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
        "mode": "SIMULATION",
    }


def main():
    print("QUANTUM CYBER DEFENSE ARENA")
    print("Threat Simulation Engine — ONLINE")
    print("SIMULATED EVENTS — NOT REAL ATTACKS")
    print("-" * 60)

    try:
        while True:
            event = generate_threat()
            print(json.dumps(event, indent=2))
            print("-" * 60)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nSimulation stopped.")


if __name__ == "__main__":
    main()
