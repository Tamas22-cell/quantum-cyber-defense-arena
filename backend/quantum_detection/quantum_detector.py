
"""
Quantum Cyber Defense Arena V6
Quantum Anomaly Detection Engine

Experimental quantum-simulation-based anomaly detector.

Four normalized blockchain transaction features are encoded
into a two-qubit circuit. Quantum state fidelity measures
similarity to a normal reference transaction.

This is a research prototype, not a validated security tool.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt
from typing import Sequence

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


@dataclass
class QuantumDetectionResult:
    classification: str
    anomaly_score: float
    similarity: float
    threshold: float
    model: str
    qubits: int
    features_used: int
    mode: str

    def to_dict(self) -> dict:
        return {
            "classification": self.classification,
            "anomaly_score": round(self.anomaly_score, 6),
            "similarity": round(self.similarity, 6),
            "threshold": self.threshold,
            "model": self.model,
            "qubits": self.qubits,
            "features_used": self.features_used,
            "mode": self.mode,
        }


class QuantumAnomalyDetector:
    """
    Experimental quantum similarity-based detector.

    Feature order:
        1. Transaction value
        2. Transactions per minute
        3. Failed transaction ratio
        4. Gas spike ratio

    All features must be normalized into [0, 1].
    """

    def __init__(
        self,
        threshold: float = 0.35,
        reference: Sequence[float] = (
            0.15,
            0.20,
            0.05,
            0.10,
        ),
    ) -> None:

        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "Threshold must be between 0 and 1."
            )

        self.threshold = threshold
        self.reference = self._validate_features(
            reference
        )

        self.model_name = "Quantum State Fidelity Detector"
        self.qubits = 2
        self.features_used = 4

        self.reference_state = Statevector.from_instruction(
            self._build_circuit(self.reference)
        )

    @staticmethod
    def _validate_features(
        features: Sequence[float],
    ) -> tuple[float, float, float, float]:

        if len(features) != 4:
            raise ValueError(
                "Exactly four features are required."
            )

        values = tuple(float(x) for x in features)

        if not all(0.0 <= x <= 1.0 for x in values):
            raise ValueError(
                "Every feature must be normalized to [0, 1]."
            )

        return values

    @staticmethod
    def _build_circuit(
        features: tuple[float, float, float, float],
    ) -> QuantumCircuit:

        value, frequency, failed_ratio, gas_spike = (
            features
        )

        circuit = QuantumCircuit(2)

        # Encode normalized values into rotation angles.
        circuit.ry(pi * value, 0)
        circuit.ry(pi * frequency, 1)

        # Introduce interaction between the two qubits.
        circuit.cx(0, 1)

        circuit.rz(pi * failed_ratio, 0)
        circuit.ry(pi * gas_spike, 1)

        return circuit

    def detect(
        self,
        features: Sequence[float],
    ) -> QuantumDetectionResult:

        validated = self._validate_features(features)

        circuit = self._build_circuit(validated)

        state = Statevector.from_instruction(circuit)

        # State fidelity = |<reference|state>|^2.
        overlap = self.reference_state.inner(state)
        similarity = float(abs(overlap) ** 2)

        # Protect against floating-point rounding errors.
        similarity = max(0.0, min(1.0, similarity))

        anomaly_score = 1.0 - similarity

        classification = (
            "ANOMALY"
            if anomaly_score >= self.threshold
            else "NORMAL"
        )

        return QuantumDetectionResult(
            classification=classification,
            anomaly_score=anomaly_score,
            similarity=similarity,
            threshold=self.threshold,
            model=self.model_name,
            qubits=self.qubits,
            features_used=self.features_used,
            mode="QUANTUM_SIMULATION",
        )

    def compare(
        self,
        normal_features: Sequence[float],
        suspicious_features: Sequence[float],
    ) -> dict:

        normal = self.detect(normal_features)
        suspicious = self.detect(suspicious_features)

        return {
            "engine": "Quantum Cyber Defense Arena V6",
            "status": "READY",
            "normal_transaction": normal.to_dict(),
            "suspicious_transaction": suspicious.to_dict(),
        }


def main() -> None:

    detector = QuantumAnomalyDetector(
        threshold=0.35
    )

    normal_transaction = [
        0.16,
        0.22,
        0.04,
        0.12,
    ]

    suspicious_transaction = [
        0.95,
        0.90,
        0.85,
        0.95,
    ]

    result = detector.compare(
        normal_transaction,
        suspicious_transaction,
    )

    print()
    print("=" * 60)
    print("QUANTUM CYBER DEFENSE ARENA V6")
    print("=" * 60)

    print()
    print("QUANTUM ENGINE: READY")
    print("QUBITS: 2")
    print("FEATURES: 4")
    print("MODEL: Quantum State Fidelity Detector")

    print()
    print("--- NORMAL TRANSACTION ---")

    normal = result["normal_transaction"]

    print("Classification:", normal["classification"])
    print("Anomaly score:", normal["anomaly_score"])
    print("Similarity:", normal["similarity"])

    print()
    print("--- SUSPICIOUS TRANSACTION ---")

    suspicious = result["suspicious_transaction"]

    print("Classification:", suspicious["classification"])
    print("Anomaly score:", suspicious["anomaly_score"])
    print("Similarity:", suspicious["similarity"])

    print()
    print("=" * 60)
    print("QUANTUM DETECTION TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
