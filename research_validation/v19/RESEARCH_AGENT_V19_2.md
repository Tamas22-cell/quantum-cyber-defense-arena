# Quantum Cyber Defense Arena

## V19.2 - Research Agent

**Execution status:** RESEARCH_AGENT_PASS
**Checks:** 28 passed, 0 failed

### Evidence-grounded findings

#### RESEARCH-001 - AI research dataset

The research used 20 blockchain-derived transaction samples with 10 numerical features.

**Evidence:**

- `research_validation\v18\research_release_v18_6_results.json` — `$.dataset.samples`
- `research_validation\v18\research_release_v18_6_results.json` — `$.dataset.feature_count`

#### RESEARCH-002 - Classical AI training

The Isolation Forest research model was trained on 20 samples. It flagged 5 statistical anomalies in its training data.

**Evidence:**

- `research_validation\v17\ai_training_research_release_v17_5_results.json` — `$.research_results.v17_2_samples`
- `research_validation\v17\ai_training_research_release_v17_5_results.json` — `$.research_results.v17_2_training_anomalies`

#### RESEARCH-003 - Cross-method rank association

The classical and simulated quantum novelty rankings had a Spearman correlation of 0.79608751. This is a ranking association, not detection accuracy.

**Evidence:**

- `research_validation\v18\quantum_classical_comparison_v18_4_results.json` — `$.comparison.spearman_rank_correlation`

#### RESEARCH-004 - Top-K overlap

The two methods shared 3 of their top 5 highest-scoring transaction samples. Overlap is not a ground-truth accuracy measure.

**Evidence:**

- `research_validation\v18\quantum_classical_comparison_v18_4_results.json` — `$.comparison.top_k`
- `research_validation\v18\quantum_classical_comparison_v18_4_results.json` — `$.comparison.top_k_overlap`

#### RESEARCH-005 - Bootstrap uncertainty

The exploratory paired-bootstrap 95% interval for rank correlation was [0.45202401, 0.94082278]. Its interpretation depends on sampling assumptions.

**Evidence:**

- `research_validation\v18\statistical_validation_v18_5_results.json` — `$.spearman.bootstrap.ci_lower`
- `research_validation\v18\statistical_validation_v18_5_results.json` — `$.spearman.bootstrap.ci_upper`

#### RESEARCH-006 - Exploratory significance tests

The permutation-test p-value was 0.00019996, and the exact Top-K overlap p-value was 0.07262642. They test different null models and do not prove cyberattack detection or quantum advantage.

**Evidence:**

- `research_validation\v18\statistical_validation_v18_5_results.json` — `$.spearman.permutation.p_value_two_sided`
- `research_validation\v18\statistical_validation_v18_5_results.json` — `$.top_k.hypergeometric_tail_p_value`

#### RESEARCH-007 - Research validation

V17.5 passed 34 release checks, and V18.6 passed 46 release checks. These establish artifact-level validation, not operational security effectiveness.

**Evidence:**

- `research_validation\v17\ai_training_research_release_v17_5_results.json` — `$.checks_passed`
- `research_validation\v18\research_release_v18_6_results.json` — `$.checks_passed`

### Scientific limitations

- Small transaction dataset
- No verified malicious-transaction labels
- In-sample exploratory results
- Possible dependence between observations
- Qiskit used local simulation, not quantum hardware
- No measured quantum computational advantage
- No demonstrated production threat-detection ability
- Research Agent is deterministic, not LLM-based

### Next stage

V19.3 - Validation Agent
