# Quantum Cyber Defense Arena

## V21.3 - Multi-Agent Threat Correlation

**Status:** THREAT_CORRELATION_PASS

**Validation:** 46 passed,
0 failed.

### Research inputs

- V20.3 synthetic threat alerts
- V21.2 statistical behavioral anomalies
- V20.4 digital twin replay frames
- V21.1 architecture

### Correlation results

| Metric | Value |
|---|---:|
| Simulation ticks | 120 |
| Source alerts | 21 |
| Behavioral detections | 61 |
| Same-tick correlations | 21 |
| Nearby-tick correlations | 0 |
| Alert-only events | 0 |
| Maximum correlation score | 0.950366 |

### Correlation method

Three deterministic analytical roles:
1. Alert Evidence Agent
2. Behavioral Evidence Agent
3. Correlation Supervisor

Alerts are matched to same-node behavioral
detections, either at the same tick or within
a +/- 2 tick research window.

Scores are ordinal heuristics, not
calibrated probabilities of attack.

### Limitations

- Only synthetic network data are used
- No trained or LLM-based agents execute
- No real attacks are independently verified
- Temporal proximity is not causal proof
- Synthetic risk inputs may share provenance
- No real-world threat detection accuracy measured
- No autonomous external actions

### Next stage

V21.4 - Predictive Risk Analytics
