# Quantum Cyber Defense Arena

## V17 - AI Training Research Release

**Release status:** RESEARCH_RELEASE_PASS

**Validation:** 34 passed / 0 failed

### Research pipeline

1. V17.1 - AI Training Data Pipeline
2. V17.2 - Isolation Forest Training
3. V17.3 - Model Evaluation and Validation
4. V17.4 - Random Seed Robustness Benchmark
5. V17.5 - Research Release Validation

### Results

| Metric | Value |
|---|---|
| Prepared transaction samples | 20 |
| Model features | 10 |
| Training-set anomaly flags | 5 |
| V17.3 checks passed | 21 |
| V17.3 checks failed | 0 |
| Robustness model runs | 10 |
| Pairwise comparisons | 45 |
| Mean flag agreement | 0.98 |
| Mean anomaly Jaccard | 0.942857 |
| Mean rank correlation | 0.996553 |

### Scientific limitations

- Only 20 transactions were available for this study.
- No verified malicious transaction labels were provided.
- Evaluation was conducted on training data.
- Seed stability does not measure predictive accuracy.
- No production-readiness claim is made.

### Artifact integrity

SHA-256 hashes for all input artifacts are stored in
`ai_training_research_release_v17_5_results.json`.

### Next stage

V18 - Quantum-Classical Benchmark Lab.

The next research stage should use controlled,
clearly separated baselines and independently
evaluated test data wherever possible.
