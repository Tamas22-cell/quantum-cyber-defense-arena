# Quantum Cyber Defense Arena

## V22.2 - Adaptive Threat Detection

Status: ADAPTIVE_THREAT_DETECTION_PASS
Checks passed: 22
Checks failed: 0

### Method

- Historical EWMA baseline
- Previous observations only
- Baseline window: 24
- Minimum history: 12
- Adapted threshold from previous scores
- Three features: load, risk, incident traffic

### Synthetic holdout comparison

| Metric | Adaptive V22.2 | V21.2 baseline |
|---|---:|---:|
| Detections | 23 | 19 |
| TP | 6 | 6 |
| FP | 17 | 13 |
| FN | 0 | 0 |
| TN | 277 | 281 |
| Precision | 0.26087 | 0.315789 |
| Recall | 1.0 | 1.0 |

### Research limitations

- Dataset is entirely synthetic.
- Source risk scores are simulated.
- Synthetic injection markers are not real attack labels.
- Adaptive and baseline methods use related source features.
- Thresholds were researcher-selected, not independently tuned.
- One 120-tick run is not sufficient for generalization claims.
- No production detection accuracy is established.
- The detector cannot change a real network.

### Next stage

V22.3 - Multi-Agent Defense Decision Engine
