# Quantum Cyber Defense Arena

## V11.3 Advanced Research Analysis

Generated: 2026-10-19T11:11:43.605572+00:00

**Research type:** Synthetic simulation

## Benchmark configuration

- Benchmark runs: 30
- Source: V11.2 Extended Research Benchmark
- Quantum component: Classical quantum simulation

## Model performance

| Model | Mean F1 | Std F1 | Minimum | Maximum |
|---|---:|---:|---:|---:|
| Hybrid Fusion | 94.06% | 0.0169 | 0.9083 | 0.9709 |
| Quantum AI | 93.91% | 0.0174 | 0.9041 | 0.9709 |
| Classical AI | 73.57% | 0.0122 | 0.7117 | 0.7605 |

## Statistical comparisons

| Comparison | F1 difference (pp) | Raw p | Holm p | Significant |
|---|---:|---:|---:|---|
| hybrid vs classical | +20.4891 | 0.000050 | 0.000150 | Yes |
| hybrid vs quantum | +0.1446 | 0.004350 | 0.004350 | Yes |
| quantum vs classical | +20.3445 | 0.000050 | 0.000150 | Yes |

## Hybrid Fusion consistency

### Vs Quantum

- Wins: 9
- Losses: 0
- Ties: 21
- Mean F1 difference: +0.1446 percentage points

### Vs Classical

- Wins: 30
- Losses: 0
- Ties: 0
- Mean F1 difference: +20.4891 percentage points

## Research validation

Configuration check: **PASS**


## Research limitations

- All benchmark inputs are synthetic.
- The quantum component runs on a classical simulator.
- The tested hybrid is a specified fusion rule, not evidence that quantum hardware is superior.
- The measured F1 values depend on test-data distributions and anomaly decision thresholds.
- Correlated synthetic test runs can overstate generalization.
- Statistical significance does not prove operational usefulness.
- The sign-flip test relies on exchangeable paired differences.
- Bootstrap confidence intervals remain approximate.
- REVIEW decisions require separate operational assessment.
- Real-world security datasets and deployment testing are still required.

## Next research stage

V11.4: Research Dashboard.

V12: Robustness and Stress Testing.

V13: Real Dataset Validation.

V14: Professional Research Release.
