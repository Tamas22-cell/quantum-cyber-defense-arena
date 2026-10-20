# Quantum Cyber Defense Arena

## V19.4 - Benchmark Agent

**Status:** BENCHMARK_AGENT_PASS

**Validation checks:** 45 passed, 0 failed

### Research dataset

- Blockchain-derived samples: 20
- Shared dataset SHA-256: `a675d916a012a1fd8f2df2a8c6d6f318c541848af541e8ebbaedf0bc962cb95e`

### Compared methods

- Classical: Isolation Forest
- Quantum: Qiskit simulated fidelity kernel

### Benchmark results

| Metric | Value |
|---|---|
| Spearman correlation | 0.79608751 |
| Top-K size | 5 |
| Shared Top-K samples | 3 |
| Top-K Jaccard | 0.42857143 |
| Bootstrap 95% CI | [0.45202401, 0.94082278] |
| Permutation p-value | 0.00019996 |
| Top-K exact p-value | 0.07262642 |
| Classical runtime (s) | 0.211153 |
| Quantum simulation runtime (s) | 0.150035 |

### Scientific interpretation

The two methods show an exploratory positive
rank association on the shared transaction sample.

The runtime figures measure different computational
procedures and do not establish a speed advantage.

Top-K overlap measures agreement between methods,
not the accuracy of attack detection.

### Limitations

- Only a small transaction sample is used
- No independently verified attack labels
- No out-of-sample performance measurements
- No physical quantum hardware
- No demonstrated quantum advantage
- Statistical tests have assumptions and uncertainty

### Next stage

V19.5 - Autonomous Supervisor
