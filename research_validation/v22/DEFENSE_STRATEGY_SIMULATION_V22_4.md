# Quantum Cyber Defense Arena

## V22.4 - Defense Strategy Simulation

Status: DEFENSE_STRATEGY_SIMULATION_PASS
Checks passed: 32
Checks failed: 0

### Strategy assumptions

| Strategy | Model risk reduction | Service impact |
|---|---:|---:|
| observe | 0% | 0% |
| increase_monitoring | 5% | 2% |
| rate_limit | 35% | 25% |
| isolate_node | 75% | 85% |
| request_review | 0% | 3% |

These values are hypothetical assumptions.
They were not fitted to real security incidents.

### Results

- Evaluated decisions: 1200
- Mean original risk: 0.248355
- Mean simulated residual risk: 0.235404
- Total modeled risk reduction: 15.541263
- Mean modeled service impact: 0.015475
- Mean model regret: 0.002849
- Human approval required: 21
- Real network actions: 0

### Method

Each V22.3 decision is evaluated using a
deterministic hypothetical action-effect model.
The strategy is compared to observation only
and to the model-optimal assumed strategy.

### Limitations

- All events are synthetic.
- No real actions or interventions.
- Effects are assumed, not measured.
- No causal effectiveness established.
- Service impact is an abstract model score.
- Results must not be presented as field performance.

### Next stage

V22.5 - Autonomous Defense Dashboard
