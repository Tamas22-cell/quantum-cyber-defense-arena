# Quantum Cyber Defense Arena

## Quantum Cyber Defense Arena — Full Visual Showcase

![Quantum Cyber Defense Arena — AI, Quantum and Cyber Defense command center](https://raw.githubusercontent.com/Tamas22-cell/quantum-cyber-defense-arena/feature/cyber-network-v2/1ba63f4a-9a52-4d7d-abe1-471c0d9038b4.png)

**[▶ OPEN FULL INTERACTIVE QUANTUM CYBER DEFENSE DASHBOARD](https://quantum-cyber-defense-full-dashboard-f3xh5pdib.vercel.app)**

![Quantum Cyber Defense Arena — Interactive Dashboard Visual](https://raw.githubusercontent.com/Tamas22-cell/quantum-cyber-defense-arena/feature/cyber-network-v2/0abd9865-16f5-4ce8-92c8-10fa9b2e08d5.png) · [Research data directory](./frontend/public/v23/)

The V23.5 D3 dashboard uses animated SVG network links and data particles, 120 simulation ticks, 10 nodes, 11 links and simulated response proposals. Open it via the local React/Vite frontend at `/v23/dashboard.html` (for example, `http://localhost:5174/v23/dashboard.html` if Vite uses port 5174). The link above opens the deployed React dashboard. The separate V23.5 D3 HTML file can also be viewed in the repository; its GitHub file view shows source code rather than running it.


## Research Platform Overview

Quantum Cyber Defense Arena combines **AI-driven anomaly detection**, **quantum-inspired security research**, **hybrid decision-making**, and **interactive 3D network visualization** in one unified research platform.

**🧠 AI Detection** — Threat scoring, anomaly monitoring and incident investigation.

**⚛️ Quantum Research** — Quantum-inspired simulations and benchmark validation.

**🔗 Hybrid Fusion** — Classical and quantum-inspired signals combined for decision support.

**🌐 Interactive 3D** — Animated cyber network visualization and synthetic dashboard telemetry.

**AI-Powered Cybersecurity Research | Quantum Simulation | Hybrid Threat Detection | Multi-Agent Investigation**

Quantum Cyber Defense Arena is a research-oriented cybersecurity platform combining classical machine learning, quantum-inspired anomaly detection, hybrid decision-making, autonomous investigation workflows, and interactive security dashboards.

The project explores how different detection architectures perform under synthetic security simulations and on labeled blockchain transaction data.

**Research development:** V23.6 final research release; V23.7–V23.8 additional validation and decision benchmarks  
**Status:** Research and demonstration environment  
**Technology:** Python, FastAPI, React, TypeScript, Qiskit, scikit-learn

---

## 1. Project Overview

Quantum Cyber Defense Arena brings several experimental cybersecurity components into a unified research platform.

Core capabilities include:

- Simulated blockchain security monitoring
- Classical AI-based anomaly detection
- Quantum state-fidelity anomaly detection using classical simulation
- Hybrid quantum-classical decision policies
- Autonomous incident investigation workflows
- Multi-agent cybersecurity research
- Statistical research validation
- Robustness and stress testing
- Evaluation using the real Elliptic Bitcoin Dataset
- Interactive 3D network visualization and research dashboards

The system is designed for research, learning, experimentation, and technical demonstration.

It is not a production-ready intrusion detection system.

## 2. System Architecture

```text
Quantum Cyber Defense Arena
|
|-- FastAPI Backend
|   |-- Threat Simulation
|   |-- Classical AI Detection
|   |-- Quantum Anomaly Detection
|   |-- Hybrid Fusion Engine
|   |-- Autonomous Investigation
|   |-- Multi-Agent Cyber Defense
|   |-- Research Validation APIs
|
|-- React / TypeScript Frontend
|   |-- Security Operations Dashboard
|   |-- Cyber Network 3D Visualization
|   |-- AI Threat Intelligence
|   |-- Quantum Research Panel
|   |-- Hybrid Fusion Panel
|   |-- Autonomous Investigation Panel
|   |-- Multi-Agent Panel
|   |-- Research Validation Dashboard
|
|-- Research Validation
|   |-- V11: Synthetic Benchmarking
|   |-- V12: Robustness Testing
|   |-- V13: Real Blockchain Data Evaluation
|
|-- Release
    |-- V14: Research Audit and Documentation
```

## 3. Classical AI Detection

The classical anomaly-detection research uses Isolation Forest and numerical transaction or security features.

The system evaluates detection performance using:

- Precision
- Recall
- F1-score
- Accuracy
- False-positive rate
- Confusion matrices

In later experiments, supervised baseline models were introduced to determine whether the Elliptic dataset contains useful discriminatory information.

## 4. Quantum Anomaly Detection

The quantum research component uses a Qiskit-based state-fidelity simulation to evaluate anomaly scores.

The experiments investigate whether quantum-state representations can provide useful anomaly signals.

**Important:** The quantum computations are simulated on classical hardware. The project does not demonstrate a computational speedup from quantum hardware.

## 5. Hybrid Quantum AI Fusion

The Hybrid Fusion research combines outputs from classical and quantum-based anomaly detectors.

The experimental decision policies include:

- Agreement-based classification
- REVIEW decisions when detectors disagree
- Logical AND fusion
- Logical OR fusion

The project evaluates the trade-offs between anomaly detection, false positives, and manual review requirements.

Hybrid fusion is experimental and should not be interpreted as a validated production security solution.

## 6. Multi-Agent Cyber Defense

The platform also includes research components for multi-agent investigation and cybersecurity decision support.

These modules explore autonomous workflows for interpreting simulated security events, coordinating investigations, and presenting findings in the dashboard.

## 7. V11 – Synthetic Research Benchmark

The extended benchmark evaluated classical, quantum-simulated, and hybrid detection across 30 reproducible synthetic runs.

| Model | Mean F1-score |
|---|---:|
| Classical AI | 73.57% |
| Quantum AI | 93.91% |
| Hybrid Fusion | **94.06%** |

The statistical analysis used paired comparisons and Holm multiple-testing correction.

These results describe performance on the chosen synthetic distributions. They do not establish real-world effectiveness or quantum computational advantage.

## 8. V12 – Robustness and Stress Testing

The V12 experiments investigated how the detection models respond to changing synthetic conditions:

- Baseline distributions
- Noisy observations
- Rare anomalies
- Overlapping anomaly distributions

Detailed results are stored in:

`research_validation/v12/robustness_benchmark_v12_results.json`

## 9. V13 – Real Blockchain Dataset Validation

The V13 research uses the **Elliptic Bitcoin Dataset**, containing labeled Bitcoin transactions and anonymized numerical features.

The dataset was prepared using a chronological split, retaining 165 original numerical features and excluding transactions with unknown labels from supervised evaluation.

### V13.2 – Initial Real-Data Evaluation

| Model | F1-score |
|---|---:|
| Classical AI | 0.00% |
| Quantum AI | 12.19% |
| Hybrid Fusion | 0.00% |

The substantial decline from synthetic benchmark performance revealed limitations in model generalization, feature adaptation, and fixed decision thresholds.

### V13.3 – Model Calibration

Following calibration, the evaluated detection policies still failed to identify the 32 labeled illicit transactions in the sampled test set.

| Model | F1-score |
|---|---:|
| Classical AI | 0.00% |
| Quantum AI | 0.00% |
| Hybrid AND | 0.00% |
| Hybrid OR | 0.00% |

These findings highlight the need for stronger models and independent validation.

### V13.4 – Supervised Baseline Diagnostics

To investigate whether useful predictive information existed in the Elliptic features, supervised reference models were evaluated separately.

| Model | F1-score | Average Precision |
|---|---:|---:|
| Dummy Baseline | 12.21% | 6.50% |
| Logistic Regression | 24.65% | 19.52% |
| Random Forest | **77.73%** | **79.91%** |

The Random Forest achieved:

- Precision: 82.05%
- Recall: 73.85%
- False-positive rate: 1.12%
- ROC AUC: 0.9218

This is a **supervised classical reference model**, not an improved quantum detector.

The test period had already been examined during earlier experiments. Therefore, these results remain exploratory rather than a fully independent final validation.

## 10. V14 – Professional Research Release

The V14 release audit checks:

- Project source-file presence
- Python syntax validity
- Research JSON files
- Previously generated benchmark results
- Git repository metadata
- Research report generation

Additional checks performed during release preparation:

- React production build completed successfully
- FastAPI research status endpoint returned HTTP 200

The audit does not replace automated integration testing, dependency security scanning, independent benchmark reproduction, or deployment verification.

## 11. Installation

### Requirements

- Python with project-compatible dependencies
- Node.js and npm
- A supported web browser
- Git

The development environment used Python 3.11 for key project components.

### Backend

From the project root, use the configured Python environment to run:

```powershell
.\.venv\Scripts\python.exe main.py
```

The FastAPI backend is expected at:

`http://127.0.0.1:8000`

### Frontend

In a separate terminal:

```powershell
cd frontend
npm install
npm run dev
```

The development dashboard is expected at:

`http://127.0.0.1:5173`

Actual startup behavior depends on the local environment and installed dependencies.

## 12. Research Reproducibility

The research programs and their generated JSON outputs are organized under:

`research_validation/`

Selected entry points:

```text
research_validation/v11/benchmark_v11.py
research_validation/v11/benchmark_v11_2.py
research_validation/v11/research_analysis_v11_3.py
research_validation/v12/robustness_benchmark_v12.py
research_validation/v13/elliptic_prepare_v13.py
research_validation/v13/elliptic_validation_v13_2.py
research_validation/v13/model_calibration_v13_3.py
research_validation/v13/model_diagnostic_v13_4.py
release/v14/release_validation_v14.py
```

The original large external dataset files are not included in the documented Git commits.

The Elliptic dataset must be obtained separately from a legitimate source, subject to its applicable licensing and access terms.

## 13. Research Limitations

- The original synthetic benchmark results do not generalize reliably to the tested real dataset.
- The quantum component relies on classical quantum simulation.
- The real-data quantum experiments use PCA-derived coordinates.
- The supervised Random Forest baseline is not directly comparable to the original anomaly detectors as proof of quantum or hybrid improvement.
- Real-data thresholds, class imbalance, feature semantics, and dataset shifts materially affect results.
- The final historical test period was previously inspected.
- No production security certification has been performed.
- The project does not claim verified quantum computational advantage.

## 14. Research Purpose

Quantum Cyber Defense Arena demonstrates an integrated research workflow spanning machine learning, quantum simulation, hybrid systems, cybersecurity analytics, statistical validation, and interactive software development.

The project represents the completion of the planned V14 research-prototype development cycle.

**Research prototype — not a certified production cybersecurity system.**

---

## 15. V15 — Autonomous Quantum AI Cyber Defense (Research Simulation)

**Status:** V15.1–V15.5 implemented and locally validated. **Validation:** PASS (0 failed checks). The V15 features are research prototypes based on saved synthetic observations; they are not production cybersecurity controls.

| Version | Module | What it provides |
|---|---|---|
| **V15.1** | Intelligent Threat Orchestrator | Combines normalized classical and quantum detector *inputs* using a deterministic hybrid fusion policy, prioritizes findings, and exports JSON reports. The standalone run uses synthetic scores; it does not execute trained detectors. |
| **V15.2** | Multi-Agent Decision Engine | Three sequential, explainable, rule-based assessment stages: Threat Analysis, Investigation, and Decision. These are not independent LLM agents. |
| **V15.3** | Autonomous Response Simulation | Produces policy-checked response plans, human-approval flags, and audit trails. No external action, blocking, or remediation is executed. |
| **V15.4** | Live Command Center | React dashboard panel featuring animated playback, priority metrics, event stream, decision inspector, and response status. Reads saved V15.1–V15.3 JSON exports from `frontend/public/v15/`. |
| **V15.5** | Validation & Release | Checks stored result structures, event consistency, deterministic decision rules, response safety, summary counts, and static React/JSON integration. Local report status: **PASS**. |

### V15 source and artifacts

- `research_validation/v15/threat_orchestrator_v15_1.py`
- `research_validation/v15/multi_agent_decision_v15_2.py`
- `research_validation/v15/autonomous_response_v15_3.py`
- `research_validation/v15/validation_release_v15_5.py`
- `research_validation/v15/*_results.json`
- `frontend/src/components/LiveCommandCenterV15_4.tsx`
- `frontend/public/v15/*_results.json`

### V15 execution pipeline

```text
Synthetic detector scores (V15.1)
   |
   v
Threat Orchestrator: classical + quantum inputs -> hybrid decision -> priority
   |
   v
Multi-Agent Decision Engine (V15.2)
   |-- Threat Analysis role
   |-- Investigation role
   '-- Decision role
   |
   v
Autonomous Response Simulator (V15.3)
   |-- Proposed action & human-approval gate
   '-- Audit trail (no actual security action)
   |
   v
JSON exports -> React V15.4 Live Command Center (animated saved-event playback)
   |
   v
V15.5 saved-result validation (local PASS; not production certification)
```

### Local full-dashboard workflow

Run the FastAPI backend from the repository root and the React/Vite frontend from `frontend/` in **separate terminals**. Use the repository's current backend entry point and configured Python environment. The developer dashboard runs at `http://127.0.0.1:5173`; its local API uses `http://127.0.0.1:8000`. A browser loading a public Vercel URL cannot reach a developer's `127.0.0.1` backend. A public full-stack deployment will require a hosted API, configuration for its address, and separate browser/integration tests.

The V15.4 component loads the three JSON snapshots from `frontend/public/v15/` and checks their event IDs and versions. If these files are unavailable, it explicitly shows labeled **sample demo data**. Stored results can be played back with animation, but are not real-time inference.

### Release checklist and verified scope

| Item | Status |
|---|---|
| V15.1 / V15.2 / V15.3 Python execution | Completed locally on synthetic inputs |
| V15.4 React integration and Vite production build | Completed locally |
| V15.5 saved-result research validation | **PASS; 0 failed checks** |
| Code pushed to GitHub | `feature/cyber-network-v2` |
| Full original dashboard publicly deployed | **Not yet verified or completed** |
| Live blockchain ingestion / production defense | **Not implemented in V15** |

### Run V15 validation

```powershell
python research_validation/v15/validation_release_v15_5.py
cd frontend
npm run build
```

**Important distinction:** The V15 dashboard replays stored research events. Animated playback does not mean live threat detection. The V15.5 validation covers saved simulation outputs and static frontend integration; backend connectivity, browser end-to-end behavior, and production/Vercel deployment require separate testing. The existing V14 research findings and limitations remain applicable.


---

## 16. V16 – Blockchain Intelligence and AI–Quantum Integration

The V16 research pipeline introduces blockchain transaction ingestion, numerical feature engineering, anomaly scoring, and a simulation-based AI–quantum integration layer.

| Stage | Module | Reproducible artifact |
|---|---|---|
| V16.1 | Blockchain transaction ingestion | `research_validation/v16/blockchain_ingestion_v16_1_results.json` |
| V16.2 | Transaction feature engineering | `research_validation/v16/transaction_features_v16_2_results.json` |
| V16.3 | Blockchain anomaly detection | `research_validation/v16/blockchain_anomaly_v16_3_results.json` |
| V16.4 | AI–Quantum threat integration | `research_validation/v16/ai_quantum_integration_v16_4_results.json` |
| V16.6 | Research release validation | `research_validation/v16/validation_release_v16_6_results.json` |

These artifacts represent research pipelines and saved experimental results, not validated real-time blockchain surveillance.

## 17. V17 – AI Training Research

The V17 pipeline covers training data preparation, Isolation Forest model training and evaluation, random-seed robustness, and release checks.

- **V17.5 release:** 34 checks passed, 0 failed.
- **Research sample:** 20 transactions with 10 numerical features.
- **Robustness:** 10 model runs, 45 pairwise comparisons, mean anomaly-flag agreement 0.98.

See [V17 research release](research_validation/v17/V17_RESEARCH_RELEASE.md). These are small-sample, mostly in-sample research outcomes; stability is not attack-detection accuracy.

## 18. V18 – Quantum-Classical Benchmark Lab

V18 compares an Isolation Forest baseline with a **Qiskit simulated, 3-qubit fidelity-kernel** workflow.

- **V18.6 release:** 46 checks passed.
- **Dataset:** 20 samples, 10 features; no independently verified malicious labels.
- **Exploratory anomaly-rank association:** Spearman correlation 0.79608751; 3 overlapping samples in the Top-5 selections.
- **Quantum hardware:** not used.

See [V18 research release](research_validation/v18/V18_RESEARCH_RELEASE.md). This is not evidence of quantum speedup or superior predictive accuracy.

## 19. V19 – Autonomous Multi-Agent Research

V19.1–V19.6 organizes research, validation, benchmarking, and supervision into deterministic software-agent roles.

- **V19.6 release:** 44 validation checks passed.
- **Research findings:** 7, all validated by the implemented research rules.
- **Completed workflow tasks:** 4.
- **Safety:** supervisor approval refers to a simulated research workflow, not permission to execute network actions.

See [V19 research release](research_validation/v19/V19_RESEARCH_RELEASE.md). The research agents are deterministic roles, not independent LLM agents.

## 20. V20 – Cyber Digital Twin and D3 Dashboard

V20 introduces the cyber digital-twin research stage and D3-oriented research visualization, building on synthetic network telemetry and previously saved results.

- Research code and results: [V20 directory](research_validation/v20/).
- The visual demonstration does not imply live production sensor ingestion.
- Browser runtime, API connectivity, and public hosting require separate integration checks.

## 21. V21 – Advanced Threat Intelligence

V21 extends the research pipeline with threat-intelligence analysis and structured synthetic security observations.

Research artifacts are stored in [V21 directory](research_validation/v21/). Outputs are research evidence and should not be presented as independently verified threat intelligence.

## 22. V22 – Autonomous Defense Research

V22 develops research workflows for simulated detection, decision support, and cyber-network observations that feed later V23 fusion experiments.

Research artifacts are stored in [V22 directory](research_validation/v22/). Defense responses remain proposed or simulated; no production remediation is claimed.

## 23. V23 – Advanced Cyber Defense Research

**V23.6 final research release:** `ADVANCED_CYBER_DEFENSE_RELEASE_PASS`, with **117 checks passed** and **0 failed**.

| Version | Module |
|---|---|
| V23.1 | Advanced Cyber Defense Architecture |
| V23.2 | Intelligent Threat Fusion |
| V23.3 | Adaptive Defense Policy Optimization |
| V23.4 | Multi-Agent Defense Orchestration |
| V23.5 | Advanced Cyber Defense Dashboard |
| V23.6 | Final Cyber Defense Research Validation and Release |

**Saved simulated research scope:** 10 network nodes, 11 links, 120 simulation ticks, 1,200 fused node observations, 3,600 orchestration events, 1,265 pending approvals, and **0 real network actions**.

- [V23 research release report](research_validation/v23/V23_RESEARCH_RELEASE.md)
- [V23 research dashboard HTML](frontend/public/v23/dashboard.html)
- [V23.6 validation results](research_validation/v23/advanced_cyber_defense_release_v23_6_results.json)

The dashboard replays synthetic research observations. File-level dashboard validation does not establish browser performance or real-world detection accuracy.

### V23.7 – Autonomous Defense Validation

The follow-up validator checked the structure and safety rules of **1,200 synthetic fusion events**.

| Metric | Result |
|---|---:|
| Valid events | 1,200 / 1,200 |
| Invalid events | 0 |
| Average fusion score | 0.202126 |
| Policy-validation status | `RESEARCH_VALIDATION_PASS` |

Source: [V23.7 Python module](research_validation/v23_7/autonomous_defense_validation_v23_7.py) and [results JSON](research_validation/v23_7/autonomous_defense_validation_v23_7_results.json).

### V23.8 – AI Defense Decision Benchmark

The final supplementary benchmark analyzes the relationship between simulated priorities, recommended actions, and human-approval requirements.

| Metric | Result |
|---|---:|
| Total events | 1,200 |
| Validated events | 1,200 |
| Normal / low priority | 919 / 260 |
| High / critical priority | 1 / 20 |
| `observe` / `increase_monitoring` / `isolate_node` | 1,143 / 36 / 21 |
| Events flagged for human approval | 21 |
| Policy violations under implemented assumptions | 0 |
| Benchmark status | `AI_DEFENSE_BENCHMARK_PASS` |

Source: [V23.8 Python module](research_validation/v23_8/ai_defense_decision_benchmark_v23_8.py) and [results JSON](research_validation/v23_8/ai_defense_decision_benchmark_v23_8_results.json).

**Research limitations:** V23.7/V23.8 PASS means the saved synthetic events satisfy implemented consistency and safety rules. The dataset lacks independent attack ground-truth labels; therefore **precision, recall, F1, false-positive rate, autonomous intervention effectiveness, and production detection accuracy have not been established**.

## 24. Current Dashboard and Local Development

The repository contains a React/TypeScript frontend, a FastAPI backend, saved experiment outputs, and independent visualization/demo assets. The complete application and the separate public portfolio demonstration must not be conflated.

```powershell
# Terminal 1, at repository root
python -m uvicorn main:app --reload --port 8000

# Terminal 2
cd frontend
npm install
npm run dev
```

- Backend API reference: `http://127.0.0.1:8000/docs`
- Frontend: typically `http://localhost:5173`; Vite may use another available port, such as 5174.
- Research status endpoints and frontend rendering were checked locally during development, but these checks are not a full automated end-to-end or public deployment certification.
- The [animated Vercel portfolio demo](https://quantum-cyber-defense-live-demo-tamas-quantum-lab.vercel.app) is **separate** from the complete React/FastAPI stack.

**Project status: research prototype / simulation and demonstration platform — not a certified production cyber-defense system.**
