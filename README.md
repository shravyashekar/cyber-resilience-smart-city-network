# Cyber Resilience Smart City Network

A local educational simulation for a fictional smart city. Phase 2 focuses on an Isolation Forest intrusion detection system (IDS), a transparent service risk assessment, and tier-aware simulated self-healing.

## Safety and scope

The app does not scan devices, send traffic, connect to city infrastructure, or change real systems. Synthetic traffic and all network response actions are simulated in memory. An uploaded public CSV is read locally for offline detector evaluation. The malware-like scenario is synthetic feature data, not malware and contains no executable payload. This is a classroom prototype, not production security or autonomous incident response.

## Architecture

- `dashboard.py` — Streamlit interface. IDS and Risk Assessment are the primary sections; Network Overview and Self-Healing are additional sections.
- `data_generator.py` — seeded normal and synthetic incident traffic with ground-truth labels.
- `anomaly_detector.py` — fits and applies scikit-learn Isolation Forest; also computes label-based evaluation metrics.
- `risk_assessment.py` — maps threat severity, service tier, and civic impact to a documented 0–100 score.
- `network_topology.py` — fictional NetworkX city network and service-tier metadata.
- `self_healing.py` — risk- and tier-dependent failover, safe fallback, monitoring, isolation, and connectivity verification.
- `simulation.py` — runs one selected scenario and target service through the generator, detector, risk assessment, and response policy.
- `benchmark_data.py` — bounded public-CSV loading and held-out, normal-trained detector evaluation.
- `tests/test_phase2.py` — focused Phase 2 behavior and scenario tests.

## Setup and launch (Windows PowerShell)

From the project directory, activate the existing environment if needed. If the `venv` folder is in the parent directory:

```powershell
..\venv\Scripts\Activate.ps1
```

Install dependencies if they are not already installed:

```powershell
python -m pip install -r requirements.txt
```

Launch the dashboard from this project directory:

```powershell
..\venv\Scripts\python.exe -m streamlit run dashboard.py
```

If the environment is activated, the equivalent command is:

```powershell
python -m streamlit run dashboard.py
```

Open the local address printed by Streamlit. Press `Ctrl+C` to stop it.

## IDS methodology and generated scenarios

The Isolation Forest is trained only on generated normal records (`contamination=0.08`). Each record is scored with `IsolationForest.predict`; `-1` is an anomaly and `1` is normal. Dashboard anomaly counts and percentages are computed from these predictions, not scenario names or constants.

With no selected scenario, generated records contain 78% normal and 22% attack traffic across DoS, port scans, and malware-like activity. A selected attack drill uses a deterministic 25% selected-attack / 75% normal mix; the Normal drill contains only normal records. Ground-truth `is_anomaly` labels are retained separately from model output. When labels are present, detection rate is `TP / (TP + FN)` and false positive rate is `FP / (FP + TN)`. A rate is shown as N/A when its denominator is zero. Detection rate is recall, not the percentage of all records flagged.

The optional **Labeled public CSV** path uses a stratified held-out sample. The Isolation Forest trains on normal-labeled training rows and predictions are evaluated against held-out labels. Results depend on the dataset, chosen label column and normal label, sample, and numeric features. A model flag is not proof of an attack.

## Risk assessment and recovery policy

Threat severity is mapped as Normal=None (0), Port Scan=Medium (50), Malware-like=High (75), and DoS=Critical (100). Service criticality is derived from tier: Tier 1=100, Tier 2=65, Tier 3=30. Civic-impact ratings are explicit in `network_topology.py` on a 0–100 scale: Hospital 100, Emergency Dispatch 95, Traffic Control 70, Water Supply 85, Power Grid 100, and Public Display 25.

The transparent score is:

```text
Risk = round(0.50 × threat severity
           + 0.25 × service criticality
           + 0.25 × civic impact)
```

For a Normal drill, threat severity is zero; the displayed score still reflects the selected service's baseline criticality and civic impact, but no recovery action is taken because there is no active incident.

Recovery uses both tier and risk:

- Tier 1: risk ≥ 70 isolates the affected primary, activates its backup, reroutes service links, and verifies critical-service connectivity; lower risk uses safe fallback.
- Tier 2: risk ≥ 55 uses safe fallback; lower risk is monitored without disruption.
- Tier 3: risk ≥ 55 isolates the service and leaves its backup on standby; lower risk is monitored without disruption.

The weights, ratings, and thresholds are illustrative teaching assumptions, not a validated operational standard. One run supports one selected incident and target service; simultaneous incident queues and competing recovery actions are not implemented.

## Run tests

From the project directory, run:

```powershell
..\venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Public dataset option

The public CSV option accepts labeled network-flow data, such as a suitable Kaggle IoT intrusion CSV or the University of New Brunswick Canadian Institute for Cybersecurity's CIC IoT Attack Dataset 2023. The app reads at most 50,000 rows, trains on normal-labeled training records, and reports held-out metrics. Review the dataset's terms and cite its source in presentations. Public IoT data is not traffic from a real hospital or smart city.
