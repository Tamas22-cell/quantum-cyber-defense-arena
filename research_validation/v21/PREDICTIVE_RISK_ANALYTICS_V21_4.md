# Quantum Cyber Defense Arena

## V21.4 - Predictive Risk Analytics

**Status:** PREDICTIVE_RISK_PASS

**Validation:** 22 passed,
0 failed.

### Forecast target

Next-tick maximum observed synthetic
network node risk.

### Method

- Forecast horizon: 1 tick
- Historical mean window: 6
- Minimum history: 12
- Holdout begins: tick 90
- Fixed causal forecasting coefficients
- No fitted AI or ML model
- No external data

### Chronological evaluation

| Metric | Result |
|---|---:|
| Holdout predictions | 30 |
| Forecast MAE | 0.076364 |
| Forecast RMSE | 0.188957 |
| Persistence baseline MAE | 0.074295 |
| Forecast beats baseline | False |
| Nominal interval coverage | 95% |
| Observed holdout coverage | 1.0 |

### Uncertainty

Prediction intervals use absolute errors
from earlier calibration observations.

Coverage is measured on a later
chronological holdout.

The nominal 95% level is not a guarantee
of true coverage because observations
may be temporally dependent.

### Scientific limitations

- All input data are synthetic.
- Source risk scores are simulated.
- Forecast rule is heuristic.
- No fitted machine-learning model is used.
- The evaluation covers one simulated run.
- No independently verified attack labels.
- This is not real-world predictive accuracy.
- No autonomous security actions.

### Next stage

V21.5 - Intelligence Dashboard Integration
