# Quantum Cyber Defense Arena

## V18 - Quantum-Classical Benchmark Lab

**Research release:** V18.6

**Release validation:** PASS

**Release checks passed:** 46

### Completed stages

| Version | Research module |
|---|---|
| V18.1 | Benchmark Architecture |
| V18.2 | Classical Isolation Forest Baseline |
| V18.3 | Qiskit Quantum Kernel Simulator |
| V18.4 | Quantum-Classical Comparison |
| V18.5 | Statistical Validation |
| V18.6 | Research Release and Data Export |

### Research dataset

- Blockchain-derived transaction samples: 20
- Original numerical features: 10
- Independently verified malicious labels: No
- Independent test-set evaluation: No

### Classical baseline

- Method: Isolation Forest
- Statistical anomalies: 5
- Recorded total runtime: 0.211153 seconds

### Quantum simulator

- Framework: Qiskit
- Qubits: 3
- Circuit layers: 2
- Kernel: fidelity-based quantum kernel
- Kernel dimensions: [20, 20]
- Recorded total runtime: 0.150035 seconds

### Cross-method results

| Statistic | Result |
|---|---|
| Spearman correlation | 0.79608751 |
| Top-K size | 5 |
| Shared Top-K samples | 3 |
| Top-K Jaccard | 0.42857143 |
| Bootstrap 95% lower bound | 0.45202401 |
| Bootstrap 95% upper bound | 0.94082278 |
| Permutation p-value | 0.00019996 |
| Exact Top-K p-value | 0.07262642 |

### Scientific interpretation

The methods exhibit a positive anomaly-ranking
association on this small research dataset.

The experiment does not demonstrate:
- Confirmed cyberattack detection accuracy
- Better quantum predictive performance
- Quantum computational advantage
- Production readiness

The two methods use different anomaly scoring
definitions and different computational pipelines.

### Limitations

1. Small sample size.
2. No verified malicious-transaction labels.
3. In-sample exploratory comparison.
4. Possible dependence between transactions.
5. No physical quantum hardware.
6. No repeated controlled runtime benchmark.
7. Exploratory statistics require larger independent datasets.

### Reproducibility

The release JSON contains SHA-256 fingerprints
for the underlying research artifacts.

### Dashboard export

`frontend/public/v18/quantum_classical_v18_dashboard.json`

This is a static data export. It does not connect
the results to the React interface automatically.

### Next development stage

V19 - Autonomous Multi-Agent Research.
