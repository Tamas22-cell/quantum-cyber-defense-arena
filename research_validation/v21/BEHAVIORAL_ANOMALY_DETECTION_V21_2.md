# Quantum Cyber Defense Arena

## V21.2 - Behavioral Anomaly Detection

**Status:** BEHAVIORAL_ANOMALY_PASS

**Checks passed:** 28

**Checks failed:** 0

### Dataset

- Source: V20.4 simulated network frames
- Time steps: 120
- Nodes: 10
- Observations: 1200

### Method

Historical rolling z-score detector.

- Window: 12
- Minimum historical observations: 6
- Detection threshold: 2.5
- Features: node load, node risk and incident traffic

The baseline uses previous time steps only.
The current observation is scored before it
is added to the history.

### Results

- Flagged node observations: 61
- Affected nodes: 10
- Maximum anomaly score: 32.157305

### Synthetic injection comparison

- Eligible observations: 1140
- TP: 21
- FP: 40
- FN: 0
- TN: 1079
- Synthetic marker precision: 0.344262
- Synthetic marker recall: 1.0

These figures describe agreement with simulator
injection markers, not real cyberattack labels.

### Limitations

- Entire dataset is synthetic.
- Input risk scores are themselves simulated.
- Threshold is research-selected, not calibrated.
- Temporal and cross-node dependence remain.
- Synthetic evaluation is not independent validation.
- No trained AI model runs in this module.
- No production security effectiveness established.
- No external actions are performed.

### Exports

- behavioral_anomaly_detection_v21_2_results.json
- behavioral_anomaly_detection_v21_2_scores.csv
- behavioral_anomaly_detection_v21_2_timeline.json

### Next stage

V21.3 - Multi-Agent Threat Correlation
