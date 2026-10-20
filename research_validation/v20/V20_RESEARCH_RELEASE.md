# Quantum Cyber Defense Arena

## V20 - Cyber Digital Twin Research Release

**Release version:** V20.6

**Status:** CYBER_DIGITAL_TWIN_RELEASE_PASS

**Checks passed:** 80

**Checks failed:** 0

### Modules

| Version | Module |
|---|---|
| V20.1 | Cyber Digital Twin Architecture |
| V20.2 | Network Simulation Engine |
| V20.3 | Rule-Based Threat Scenario Engine |
| V20.4 | Event Streaming and Replay |
| V20.5 | Interactive D3 Dashboard |
| V20.6 | Research Validation and Release |

### Validated dataset

| Metric | Value |
|---|---|
| Simulated nodes | 10 |
| Simulated links | 11 |
| Simulation ticks | 120 |
| Node observations | 1200 |
| Link observations | 1320 |
| Synthetic alerts | 21 |
| Dashboard frames | 120 |
| Replay messages | 120 |
| Maximum enriched risk | 0.937957 |

### Interactive dashboard

`frontend/public/v20/dashboard.html`

The dashboard replays the validated V20.4 frames.

Features include a fixed network topology,
animated data particles, risk indicators,
alerts, playback controls and timeline scrubbing.

### Reproducibility

The release report records SHA-256 fingerprints
for the upstream research files and frontend assets.

### Scientific limitations

- Network data are synthetic
- No real packet capture
- No live cyberattack detection
- No trained AI threat detector in V20.3
- No independent verified attack labels
- No production security guarantees
- This validation does not replace browser testing
- Dashboard D3 dependency is loaded from a CDN

### Next development stage

V21 - Advanced Cyber Defense Intelligence
