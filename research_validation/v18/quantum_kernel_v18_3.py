
"""
QUANTUM CYBER DEFENSE ARENA
V18.3 - QUANTUM KERNEL SIMULATOR

Qiskit quantum statevector simulation.

Pipeline:
1. Verify V18.1 dataset integrity
2. Load real blockchain-derived features
3. Standardize and reduce dimensions
4. Encode features into 3-qubit circuits
5. Simulate quantum states with Qiskit
6. Calculate quantum fidelity kernel
7. Validate mathematical properties
8. Export CSV and JSON research artifacts

Research prototype only.
Not real quantum hardware.
Not verified cyberattack detection.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import numpy as np
    import qiskit
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
except ImportError as exc:
    print("V18.3 DEPENDENCY ERROR:", exc)
    print("Install: python -m pip install numpy qiskit")
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[2]

V17 = ROOT / "research_validation" / "v17"
V18 = ROOT / "research_validation" / "v18"

INPUT_FILE = V17 / "training_features_v17_1.csv"

ARCHITECTURE_FILE = (
    V18 / "benchmark_architecture_v18_1_results.json"
)

CLASSICAL_FILE = (
    V18 / "classical_baseline_v18_2_results.json"
)

RESULTS_FILE = (
    V18 / "quantum_kernel_v18_3_results.json"
)

KERNEL_FILE = (
    V18 / "quantum_kernel_v18_3_matrix.csv"
)

SCORES_FILE = (
    V18 / "quantum_kernel_v18_3_scores.csv"
)

N_QUBITS = 3
N_LAYERS = 2
MIN_SAMPLES = 10
MAX_SAMPLES = 100

TOLERANCE = 1e-8


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def read_json(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing required file: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        return json.load(handle)


def load_dataset():
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            f"Missing input dataset: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        features = reader.fieldnames or []
        rows = list(reader)

    if not features:
        raise ValueError("Dataset has no features.")

    if len(features) != len(set(features)):
        raise ValueError("Duplicate feature names.")

    if not MIN_SAMPLES <= len(rows) <= MAX_SAMPLES:
        raise ValueError(
            f"Expected {MIN_SAMPLES}-{MAX_SAMPLES} samples. "
            f"Found {len(rows)}."
        )

    matrix = []

    for row_index, row in enumerate(rows, start=2):
        values = []

        for feature in features:
            raw = row.get(feature)

            try:
                value = float(raw)
            except (ValueError, TypeError) as exc:
                raise ValueError(
                    f"Invalid number at row {row_index}, "
                    f"feature {feature}"
                ) from exc

            if not math.isfinite(value):
                raise ValueError(
                    f"Non-finite feature at row {row_index}"
                )

            values.append(value)

        matrix.append(values)

    return features, np.asarray(
        matrix,
        dtype=np.float64,
    )


def validate_sources(features, data):
    architecture = read_json(ARCHITECTURE_FILE)
    classical = read_json(CLASSICAL_FILE)

    if architecture.get("status") != "ARCHITECTURE_PASS":
        raise ValueError("V18.1 architecture not validated.")

    if classical.get("status") != "CLASSICAL_BASELINE_PASS":
        raise ValueError("V18.2 classical baseline missing PASS.")

    dataset_hash = sha256_file(INPUT_FILE)
    dataset_info = architecture.get("dataset", {})
    classical_info = classical.get("dataset", {})

    if dataset_hash != dataset_info.get("sha256"):
        raise ValueError(
            "Dataset SHA-256 differs from V18.1."
        )

    if dataset_hash != classical_info.get("sha256"):
        raise ValueError(
            "Dataset SHA-256 differs from V18.2."
        )

    if features != dataset_info.get("feature_names"):
        raise ValueError(
            "Feature order differs from V18.1."
        )

    if features != classical_info.get("feature_names"):
        raise ValueError(
            "Feature order differs from V18.2."
        )

    if len(data) != classical_info.get("samples"):
        raise ValueError(
            "Sample count differs from V18.2."
        )

    print("[PASS] V18.1 architecture verified")
    print("[PASS] V18.2 classical baseline verified")
    print("[PASS] Dataset SHA-256 identical")
    print("[PASS] Feature order identical")

    return dataset_hash


def quantum_preprocessing(data):
    """
    Standardize then use SVD-based PCA.

    All data are used to fit preprocessing here.
    This is an in-sample exploratory experiment,
    not a holdout evaluation.
    """

    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)

    std_safe = np.where(
        std < 1e-12,
        1.0,
        std,
    )

    standardized = (data - mean) / std_safe

    _, singular_values, vt = np.linalg.svd(
        standardized,
        full_matrices=False,
    )

    if vt.shape[0] < N_QUBITS:
        raise ValueError(
            "Insufficient feature dimensions for qubits."
        )

    components = vt[:N_QUBITS].copy()

    # Fix arbitrary SVD sign choices for reproducibility.
    for i in range(N_QUBITS):
        pivot = int(np.argmax(np.abs(components[i])))

        if components[i, pivot] < 0:
            components[i] *= -1.0

    reduced = standardized @ components.T

    # Bounded angles, avoiding extreme outlier effects.
    angles = np.pi * np.tanh(reduced / 2.0)

    if not np.all(np.isfinite(angles)):
        raise ValueError("Invalid quantum encoding angles.")

    total_variance = float(
        np.sum(singular_values ** 2)
    )

    selected_variance = float(
        np.sum(singular_values[:N_QUBITS] ** 2)
    )

    variance_ratio = (
        selected_variance / total_variance
        if total_variance > 0
        else 0.0
    )

    return angles, variance_ratio


def build_quantum_circuit(angles):
    """
    Feature-encoding quantum circuit.

    Uses genuine Qiskit circuit gates:
    RY, RZ and CX.

    The statevector is simulated locally.
    """

    circuit = QuantumCircuit(N_QUBITS)

    for layer in range(N_LAYERS):

        for qubit in range(N_QUBITS):
            angle = float(angles[qubit])

            circuit.ry(
                angle * (layer + 1),
                qubit,
            )

            circuit.rz(
                angle * 0.5,
                qubit,
            )

        for qubit in range(N_QUBITS - 1):
            circuit.cx(
                qubit,
                qubit + 1,
            )

        # Additional data-dependent phase.
        for qubit in range(N_QUBITS):
            circuit.rz(
                float(angles[qubit]) * 0.25,
                qubit,
            )

    return circuit


def calculate_quantum_states(angles):
    states = []
    example_circuit = None

    for row in angles:
        circuit = build_quantum_circuit(row)

        if example_circuit is None:
            example_circuit = circuit

        state = Statevector.from_instruction(
            circuit
        )

        vector = np.asarray(
            state.data,
            dtype=np.complex128,
        )

        norm = np.vdot(vector, vector).real

        if not np.isclose(norm, 1.0, atol=TOLERANCE):
            raise ValueError(
                "Invalid quantum state normalization."
            )

        states.append(vector)

    return np.stack(states), example_circuit


def quantum_kernel(states):
    """
    Fidelity kernel:
    K(i,j) = |<psi_i | psi_j>|^2

    Kernel values should lie in [0,1].
    """

    overlap = states.conj() @ states.T

    kernel = np.abs(overlap) ** 2

    return np.asarray(
        kernel,
        dtype=np.float64,
    )


def validate_kernel(kernel):
    n = kernel.shape[0]

    if kernel.shape != (n, n):
        raise ValueError("Kernel matrix is not square.")

    if not np.all(np.isfinite(kernel)):
        raise ValueError("Kernel has non-finite values.")

    if not np.allclose(
        kernel,
        kernel.T,
        atol=TOLERANCE,
    ):
        raise ValueError("Kernel is not symmetric.")

    if not np.allclose(
        np.diag(kernel),
        np.ones(n),
        atol=TOLERANCE,
    ):
        raise ValueError("Kernel diagonal is not one.")

    if np.min(kernel) < -TOLERANCE:
        raise ValueError("Kernel contains negative fidelity.")

    if np.max(kernel) > 1.0 + TOLERANCE:
        raise ValueError("Kernel fidelity exceeds one.")

    eigenvalues = np.linalg.eigvalsh(
        (kernel + kernel.T) / 2.0
    )

    min_eigenvalue = float(
        np.min(eigenvalues)
    )

    if min_eigenvalue < -TOLERANCE:
        raise ValueError(
            "Quantum kernel is not positive semidefinite."
        )

    print("[PASS] Quantum kernel finite")
    print("[PASS] Quantum kernel symmetric")
    print("[PASS] Quantum kernel diagonal validated")
    print("[PASS] Quantum kernel PSD validated")

    return min_eigenvalue


def calculate_anomaly_scores(kernel):
    """
    Descriptive quantum similarity novelty score.

    Larger score:
    less average fidelity with other samples.

    This is NOT the same scoring algorithm as
    classical Isolation Forest.
    """

    n = kernel.shape[0]

    similarity_sum = (
        np.sum(kernel, axis=1)
        - np.diag(kernel)
    )

    average_similarity = (
        similarity_sum / (n - 1)
    )

    novelty = 1.0 - average_similarity

    if not np.all(np.isfinite(novelty)):
        raise ValueError("Invalid novelty scores.")

    return novelty


def save_kernel(kernel):
    with KERNEL_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow(
            ["sample_index"]
            + [
                f"sample_{i + 1}"
                for i in range(len(kernel))
            ]
        )

        for index, row in enumerate(kernel, start=1):
            writer.writerow(
                [index]
                + [
                    round(float(value), 10)
                    for value in row
                ]
            )


def save_scores(scores):
    ranked = np.argsort(
        -scores,
        kind="stable",
    )

    ranks = np.empty(
        len(scores),
        dtype=int,
    )

    for rank, index in enumerate(ranked, start=1):
        ranks[index] = rank

    with SCORES_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow([
            "sample_index",
            "quantum_novelty_score",
            "novelty_rank",
        ])

        for index, score in enumerate(scores):
            writer.writerow([
                index + 1,
                round(float(score), 10),
                int(ranks[index]),
            ])


def main():
    print("=" * 68)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V18.3 - QUANTUM KERNEL SIMULATOR")
    print("=" * 68)

    V18.mkdir(
        parents=True,
        exist_ok=True,
    )

    features, data = load_dataset()

    dataset_hash = validate_sources(
        features,
        data,
    )

    print()
    print(f"SAMPLES: {len(data)}")
    print(f"ORIGINAL FEATURES: {len(features)}")
    print(f"QUBITS: {N_QUBITS}")
    print(f"CIRCUIT LAYERS: {N_LAYERS}")
    print(f"QISKIT VERSION: {qiskit.__version__}")
    print()

    prep_start = time.perf_counter()

    angles, variance_ratio = (
        quantum_preprocessing(data)
    )

    prep_seconds = (
        time.perf_counter() - prep_start
    )

    simulation_start = time.perf_counter()

    states, example_circuit = (
        calculate_quantum_states(angles)
    )

    simulation_seconds = (
        time.perf_counter() - simulation_start
    )

    kernel_start = time.perf_counter()

    kernel = quantum_kernel(states)

    min_eigenvalue = validate_kernel(
        kernel
    )

    novelty = calculate_anomaly_scores(
        kernel
    )

    kernel_seconds = (
        time.perf_counter() - kernel_start
    )

    save_kernel(kernel)
    save_scores(novelty)

    total_seconds = (
        prep_seconds
        + simulation_seconds
        + kernel_seconds
    )

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V18.3",
        "module": "Quantum Kernel Simulator",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "QUANTUM_KERNEL_PASS",
        "dataset": {
            "source": str(
                INPUT_FILE.relative_to(ROOT)
            ),
            "sha256": dataset_hash,
            "samples": len(data),
            "original_features": len(features),
            "feature_names": features,
        },
        "quantum_method": {
            "framework": "Qiskit",
            "qiskit_version": qiskit.__version__,
            "backend_type": "local_statevector_simulator",
            "physical_quantum_hardware": False,
            "number_of_qubits": N_QUBITS,
            "circuit_layers": N_LAYERS,
            "gates": ["RY", "RZ", "CX"],
            "kernel_type": "fidelity_kernel",
            "kernel_formula": (
                "abs(inner_product(state_i,state_j))**2"
            ),
            "preprocessing": (
                "full-sample standardization, "
                "SVD/PCA reduction, tanh angle encoding"
            ),
            "pca_variance_explained_ratio": round(
                variance_ratio,
                8,
            ),
            "example_circuit_depth": (
                example_circuit.depth()
            ),
            "example_circuit_size": (
                example_circuit.size()
            ),
        },
        "kernel_validation": {
            "matrix_shape": list(kernel.shape),
            "symmetric": True,
            "diagonal_ones": True,
            "positive_semidefinite": True,
            "minimum_eigenvalue": round(
                min_eigenvalue,
                12,
            ),
            "min_fidelity": round(
                float(np.min(kernel)),
                8,
            ),
            "max_fidelity": round(
                float(np.max(kernel)),
                8,
            ),
        },
        "novelty_results": {
            "method": (
                "one_minus_mean_off_diagonal_fidelity"
            ),
            "mean_score": round(
                float(np.mean(novelty)),
                8,
            ),
            "min_score": round(
                float(np.min(novelty)),
                8,
            ),
            "max_score": round(
                float(np.max(novelty)),
                8,
            ),
        },
        "runtime": {
            "preprocessing_seconds": round(
                prep_seconds,
                6,
            ),
            "simulation_seconds": round(
                simulation_seconds,
                6,
            ),
            "kernel_seconds": round(
                kernel_seconds,
                6,
            ),
            "total_seconds": round(
                total_seconds,
                6,
            ),
        },
        "evaluation": {
            "type": "in_sample_quantum_kernel_exploration",
            "verified_attack_labels": False,
            "independent_test_set": False,
            "model_accuracy_available": False,
            "quantum_advantage_demonstrated": False,
            "direct_score_comparability_with_iforest": False,
        },
        "limitations": [
            "Only 20 blockchain transaction samples.",
            "All samples used to fit PCA preprocessing.",
            "No verified threat labels.",
            "No independent test set.",
            "Quantum novelty score differs from "
            "Isolation Forest anomaly score.",
            "This is an ideal statevector simulation.",
            "No physical quantum hardware was used.",
            "No quantum speedup or superiority claimed.",
        ],
        "outputs": {
            "kernel_csv": str(
                KERNEL_FILE.relative_to(ROOT)
            ),
            "novelty_scores_csv": str(
                SCORES_FILE.relative_to(ROOT)
            ),
            "report_json": str(
                RESULTS_FILE.relative_to(ROOT)
            ),
        },
        "next_stage": (
            "V18.4 Quantum-Classical Comparison"
        ),
    }

    with RESULTS_FILE.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            report,
            handle,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )

    print()
    print("=" * 68)
    print("V18.3 QUANTUM KERNEL RESULTS")
    print("=" * 68)

    print(f"QUANTUM STATES: {len(states)}")
    print(f"KERNEL SHAPE: {kernel.shape}")
    print(
        "PCA VARIANCE RATIO: "
        f"{variance_ratio:.6f}"
    )
    print(
        "CIRCUIT DEPTH: "
        f"{example_circuit.depth()}"
    )
    print(
        "MEAN NOVELTY SCORE: "
        f"{float(np.mean(novelty)):.6f}"
    )
    print(
        "SIMULATION SECONDS: "
        f"{simulation_seconds:.6f}"
    )
    print(
        "TOTAL SECONDS: "
        f"{total_seconds:.6f}"
    )

    print()
    print(f"KERNEL SAVED: {KERNEL_FILE}")
    print(f"SCORES SAVED: {SCORES_FILE}")
    print(f"REPORT SAVED: {RESULTS_FILE}")

    print()
    print("V18.3 RESULT: QUANTUM_KERNEL_PASS")
    print("=" * 68)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())

    except Exception as error:
        print()
        print(
            "V18.3 FAILED: "
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)
