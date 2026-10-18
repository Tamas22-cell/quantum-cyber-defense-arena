
"""
Quantum Cyber Defense Arena
AI Threat Detection Engine V2

Isolation Forest anomaly detection.
Supports individual predictions, batch processing,
feature validation and model statistics.

RESEARCH / SIMULATION ONLY.
Predictions are not verified security incidents.
"""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


FEATURE_NAMES = (
    "transaction_value",
    "transactions_per_minute",
    "failed_transaction_ratio",
    "gas_spike_ratio",
    "unique_counterparties",
)


class AIThreatDetector:

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.scaler = StandardScaler()

        self.model = IsolationForest(
            n_estimators=200,
            contamination=0.05,
            random_state=seed,
            n_jobs=-1,
        )

        self.trained = False
        self.training_samples = 0
        self.total_predictions = 0
        self.total_anomalies = 0
        self.last_prediction_ms = 0.0

    def train(self, samples: np.ndarray) -> None:
        data = np.asarray(samples, dtype=float)

        if data.ndim != 2:
            raise ValueError(
                "Training data must be a 2D array"
            )

        if data.shape[1] != len(FEATURE_NAMES):
            raise ValueError(
                f"Expected {len(FEATURE_NAMES)} features"
            )

        if len(data) < 100:
            raise ValueError(
                "At least 100 training samples required"
            )

        if not np.isfinite(data).all():
            raise ValueError(
                "Training samples contain invalid values"
            )

        scaled = self.scaler.fit_transform(data)
        self.model.fit(scaled)

        self.training_samples = len(data)
        self.trained = True

    def _validate_samples(
        self,
        samples: np.ndarray,
    ) -> np.ndarray:

        if not self.trained:
            raise RuntimeError(
                "Model must be trained first"
            )

        data = np.asarray(samples, dtype=float)

        if data.ndim == 1:
            data = data.reshape(1, -1)

        if data.ndim != 2:
            raise ValueError("Invalid sample dimensions")

        if data.shape[1] != len(FEATURE_NAMES):
            raise ValueError(
                f"Expected {len(FEATURE_NAMES)} features"
            )

        if not np.isfinite(data).all():
            raise ValueError(
                "Samples contain invalid values"
            )

        if len(data) == 0:
            raise ValueError("Empty sample batch")

        if (data[:, [0, 1, 4]] < 0).any():
            raise ValueError(
                "Transaction value, rate and "
                "counterparties cannot be negative"
            )

        if (
            (data[:, 2] < 0)
            | (data[:, 2] > 1)
        ).any():
            raise ValueError(
                "Failure ratio must be between 0 and 1"
            )

        if (data[:, 3] < 0).any():
            raise ValueError(
                "Gas spike ratio cannot be negative"
            )

        return data

    def predict_batch(
        self,
        samples: np.ndarray,
    ) -> list[dict[str, Any]]:

        data = self._validate_samples(samples)

        start = perf_counter()

        scaled = self.scaler.transform(data)

        predictions = self.model.predict(scaled)
        decisions = self.model.decision_function(scaled)

        elapsed_ms = (
            perf_counter() - start
        ) * 1000

        per_sample_ms = elapsed_ms / len(data)

        results = []

        for prediction, decision in zip(
            predictions,
            decisions,
        ):
            is_anomaly = int(prediction) == -1
            score = float(-decision)

            if is_anomaly:
                classification = "ANOMALY"
            else:
                classification = "NORMAL"

            results.append(
                {
                    "timestamp": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "model": "IsolationForest",
                    "model_version": "2.0.0",
                    "is_anomaly": is_anomaly,
                    "classification": classification,
                    "anomaly_score": round(score, 6),
                    "decision_function": round(
                        float(decision), 6
                    ),
                    "inference_ms": round(
                        per_sample_ms, 4
                    ),
                    "mode": "SIMULATION",
                }
            )

        self.total_predictions += len(results)

        self.total_anomalies += sum(
            int(result["is_anomaly"])
            for result in results
        )

        self.last_prediction_ms = round(
            elapsed_ms, 4
        )

        return results

    def predict(
        self,
        sample: np.ndarray,
    ) -> dict[str, Any]:

        return self.predict_batch(sample)[0]

    def predict_event(
        self,
        event: dict[str, Any],
    ) -> dict[str, Any]:

        missing = [
            name
            for name in FEATURE_NAMES
            if name not in event
            or event[name] is None
        ]

        if missing:
            return {
                "event_id": event.get("id"),
                "classification": "INSUFFICIENT_DATA",
                "is_anomaly": None,
                "anomaly_score": None,
                "missing_features": missing,
                "mode": "SIMULATION",
            }

        sample = np.array(
            [event[name] for name in FEATURE_NAMES],
            dtype=float,
        )

        result = self.predict(sample)
        result["event_id"] = event.get("id")

        return result

    def get_status(self) -> dict[str, Any]:

        anomaly_rate = (
            self.total_anomalies
            / self.total_predictions
            if self.total_predictions
            else 0.0
        )

        return {
            "engine": "AI Threat Detection V2",
            "model": "IsolationForest",
            "model_version": "2.0.0",
            "trained": self.trained,
            "training_samples": self.training_samples,
            "features": list(FEATURE_NAMES),
            "total_predictions": self.total_predictions,
            "total_anomalies": self.total_anomalies,
            "anomaly_rate": round(
                anomaly_rate, 4
            ),
            "last_prediction_ms":
                self.last_prediction_ms,
            "mode": "SIMULATION",
        }


def generate_training_data(
    count: int = 2000,
    seed: int = 42,
) -> np.ndarray:

    rng = np.random.default_rng(seed)

    transaction_value = rng.lognormal(
        4.0, 0.8, count
    )

    transaction_rate = rng.poisson(
        12, count
    )

    failure_ratio = rng.beta(
        2, 25, count
    )

    gas_spike = rng.lognormal(
        0.0, 0.2, count
    )

    counterparties = rng.poisson(
        8, count
    )

    return np.column_stack(
        [
            transaction_value,
            transaction_rate,
            failure_ratio,
            gas_spike,
            counterparties,
        ]
    )


def main() -> None:

    print("=" * 55)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("AI THREAT DETECTION ENGINE V2")
    print("=" * 55)

    detector = AIThreatDetector()

    training_data = generate_training_data()
    detector.train(training_data)

    normal_sample = np.array(
        [55.0, 12.0, 0.04, 1.05, 8.0]
    )

    suspicious_sample = np.array(
        [250000.0, 850.0, 0.91, 12.0, 350.0]
    )

    print("\nNORMAL TRANSACTION:")
    print(detector.predict(normal_sample))

    print("\nSUSPICIOUS TRANSACTION:")
    print(detector.predict(suspicious_sample))

    print("\nMODEL STATUS:")
    print(detector.get_status())

    print("\nEVENT WITHOUT REQUIRED TELEMETRY:")
    print(
        detector.predict_event(
            {
                "id": "simulation-001",
                "network": "Ethereum",
                "risk_score": 85,
            }
        )
    )

    print("\nResearch simulation only.")
    print("No real attacks have been verified.")


if __name__ == "__main__":
    main()
