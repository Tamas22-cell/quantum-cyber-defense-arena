# Quantum Cyber Defense Arena

## V14 - Professional Research Release

Generated: 2026-10-19T12:17:05.099128+00:00

**Release audit status: SOURCE_AND_RESULT_AUDIT_PASS**

## Project overview

Research prototype combining:

- Cybersecurity monitoring and dashboards
- Classical anomaly detection
- Quantum state-fidelity simulation
- Hybrid decision rules
- Multi-agent AI research components
- Synthetic and real-data evaluation

## V11.3 - Synthetic benchmark

| Model | Mean F1 |
|---|---:|
| Classical | 73.57% |
| Quantum | 93.91% |
| Hybrid | 94.06% |

The V11 results use synthetic datasets.
They do not establish real-world accuracy or quantum computational advantage.

## V12 - Robustness experiments

Result file status: **PASS**

V12 tests noise, rare anomalies, and overlapping synthetic distributions.
A saved report does not by itself prove robustness.

## V13.2 - Real Elliptic Bitcoin dataset

| Model | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|
| Classical | 0.00% | 0 | 45 | 32 |
| Quantum | 12.19% | 32 | 461 | 0 |
| Hybrid | 0.00% | 0 | 45 | 32 |

## V13.3 - Calibrated detection

| Model | F1 | TP | FP | FN |
|---|---:|---:|---:|---:|
| classical | 0.00% | 0 | 46 | 32 |
| quantum | 0.00% | 0 | 34 | 32 |
| hybrid_and | 0.00% | 0 | 9 | 32 |
| hybrid_or | 0.00% | 0 | 71 | 32 |

## V13.4 - Supervised reference baselines

| Model | Test F1 | Precision | Recall |
|---|---:|---:|---:|
| dummy | 12.21% | 6.50% | 100.00% |
| logistic_regression | 24.65% | 14.19% | 93.85% |
| random_forest | 77.73% | 82.05% | 73.85% |

The supervised reference models are different from the original unsupervised detectors.
Their results must not be presented as an improvement in quantum or hybrid detection.

## Source-code checks

- main.py: PASS
- research_validation\v11\benchmark_v11.py: PASS
- research_validation\v12\robustness_benchmark_v12.py: PASS
- research_validation\v13\elliptic_prepare_v13.py: PASS
- research_validation\v13\elliptic_validation_v13_2.py: PASS
- research_validation\v13\model_calibration_v13_3.py: PASS
- research_validation\v13\model_diagnostic_v13_4.py: PASS

## Project structure

- FastAPI application: FOUND
- React application: FOUND
- V11.4 Research Dashboard: FOUND
- Classical AI detector: FOUND
- Quantum detector: FOUND
- V13.4 diagnostic program: FOUND

## Git

- Branch: feature/cyber-network-v2
- Last commit: b09d142 V13.4 Real Blockchain Model Diagnostics

## Scientific limitations

- Earlier high F1 results used synthetic data.
- V13 real-data anomaly detectors performed poorly.
- V13.4 supervised baselines use labeled training data.
- The historical test period was previously inspected.
- Some comparisons use different test sample sizes.
- Test results therefore are not directly equivalent.
- Quantum components run in classical simulation.
- No quantum computational speedup is demonstrated.
- No production cybersecurity certification exists.
- Further independent validation is needed.

## Release scope

V14 represents the completion of the planned research prototype development cycle.
It is not a production security certification.

## Checks not performed by this script

- Running FastAPI integration tests
- Building the React frontend
- Testing all interactive dashboard controls
- Dependency and vulnerability scanning
- Verifying the external dataset provenance
- Reproducing the complete benchmarks
- Confirming remote GitHub publication
