# Quantum Cyber Defense Arena

## V20.2 - Network Simulation Engine

**Status:** NETWORK_SIMULATION_PASS

### Simulation

- Simulation ticks: 120
- Network nodes: 10
- Network links: 11
- Node observations: 1200
- Link observations: 1320
- Generated alerts: 21
- Synthetic anomaly ticks: 7
- Maximum observed risk: 1.0
- Mean traffic per link observation: 58.214674 Mbps
- Mean simulated latency: 3.132748 ms

### Integrity

- V20.1 source SHA-256: `7e5d02e5a3005a0738aba0deb0f3dbd40575c5eaf5258853993f2fea6ea4ee5d`
- V20.1 model SHA-256: `09bc12e4013cc06af59b4f66dee1199c63b2a2a439f325e8e3aea2cde3ca6d1c`
- Validation checks passed: 30
- Validation checks failed: 0

### Exported data

- Node observations: `network_simulation_v20_2_nodes.csv`
- Link observations: `network_simulation_v20_2_links.csv`
- Event timeline: `network_simulation_v20_2_events.json`
- Main results: `network_simulation_v20_2_results.json`

### Research interpretation

The engine reproduces synthetic traffic, loads,
risk scores and timestamped alerts from a fixed
random seed.

This is a model-driven simulation. It does not
observe real network packets or execute attacks.

Alerts are based on synthetic risk thresholds,
not on a validated production threat detector.

### Next stage

V20.3 - AI Threat Scenario Engine
