<div align="center">

<img src="logo.jpeg" alt="SecureFlow Logo" width="200">

# SecureFlow

### PSB Hackathon iDEA 2.0 -- Problem Statement PS9

**Live Demo:** https://secureflowll.streamlit.app/

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Java](https://img.shields.io/badge/Java-11+-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-1.29+-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-Classifier-FF6F00?style=for-the-badge&logo=databricks&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

**An end-to-end automated platform that discovers forgotten ("zombie") API endpoints in banking networks using passive traffic analysis and ML classification, then safely decommissions them with human approval gates and full audit trails.**

---

<table>
<tr>
<td align="center" width="33%">

### 15 Days to 30 Min
Manual decommission time reduced by **99.8%**

</td>
<td align="center" width="33%">

### Rs.4.8L/Year Saved
Per zombie endpoint decommissioned

</td>
<td align="center" width="33%">

### F1 >= 0.85
ML threshold before any automated action

</td>
</tr>
</table>

</div>

---

## Table of Contents

- [The Problem](#the-problem)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Streamlit Dashboard](#streamlit-dashboard)
- [Generating Synthetic Data](#generating-synthetic-data)
- [Dependencies](#dependencies)
- [How It Works](#how-it-works)
- [Known Limitations](#known-limitations)
- [License](#license)

---

## The Problem

> **Every bank running APIs for 5+ years has zombie endpoints -- old, forgotten API routes that haunt your infrastructure.**

| The Zombie Threat | Business Impact |
|-------------------|-----------------|
| Still run on the network and are accessible | Manual discovery: **15+ engineer-days per endpoint** |
| No longer used by real users or services | Cost per zombie: **~Rs.4.8 Lakhs/year** |
| Excluded from security scanning | Security risk: **High -- unpatched, forgotten** |
| Create unmonitored attack surfaces | Compliance: **OWASP API Top 10 violations** |
| Cost money to maintain (compute, logging, monitoring) | |

### Platform Lifecycle

```
DISCOVER --> CLASSIFY --> NOTIFY --> DECOMMISSION

  Zeek/WAF     XGBoost      GitHub Issues    Canary Deploy
  Kafka        SHAP         Owner Response   Slow Drain
  Flink        MLflow       30-Day Window    Audit Trail
```

---

## Architecture

```
                    CORE SWITCH (SPAN/TAP)
               Layer 2 Mirroring - Bypasses WAF
                              |
            +-----------------------------------------+
            |            LISTEN LAYER                  |
            |   ZEEK --> KAFKA --> FLINK              |
            |  (Sensor)  (Cluster)  (Feature Job)     |
            +-----------------------------------------+
                              |
            +-----------------------------------------+
            |           REMEMBER LAYER                 |
            |   FEAST    REDIS    MINIO               |
            |  (Store)  (Sent.)  (S3 Compat)          |
            +-----------------------------------------+
                              |
            +-----------------------------------------+
            |            DETECT LAYER                  |
            |  XGBoost    SHAP    MLflow              |
            | (Classifier) (Exp.)  (Tracking)         |
            +-----------------------------------------+
                              |
            +-----------------------------------------+
            |           ENFORCE LAYER                  |
            |    OPA    KYVERNO   BACKSTAGE           |
            |  (Policy) (Admit.)  (Catalog)           |
            +-----------------------------------------+
                              |
            +-----------------------------------------+
            |             ACT LAYER                    |
            |  GitHub Actions --> Flagger             |
            |  (Orchestrate)     (Canary)             |
            +-----------------------------------------+
```

---

## Getting Started

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | ML pipeline, traffic generator |
| Java | 11+ | Flink job compilation |
| Maven | 3.8+ | Flink job build |
| Docker | 24+ | Container builds |
| kind | 0.20+ | Local Kubernetes cluster |
| kubectl | 1.29+ | Kubernetes management |

### Quick Start -- ML Pipeline Only

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Generate synthetic training data (1,13,836 endpoints)
python demo/traffic-generator/simulate.py --generate-features

# 3. Start MLflow tracking server
mlflow server --host 127.0.0.1 --port 5000

# 4. Train XGBoost model
MLFLOW_TRACKING_URI=http://localhost:5000 \
MLFLOW_EXPERIMENT_NAME=zombie-classification \
DATA_PATH=demo/test-data/endpoint_features.parquet \
  python ml-pipeline/train.py

# 5. Test prediction
python ml-pipeline/predict.py test_features.json
```

### Full Platform -- Local Kubernetes

```bash
# One command (Windows)
./demo-all.ps1

# Or step by step
bash demo/scripts/setup-kind.sh     # Create kind cluster + MetalLB
bash demo/scripts/deploy-all.sh     # Deploy all 8 phases
bash demo/scripts/verify.sh         # Verify components
```

**What gets deployed:**
- Kafka (Strimzi operator, 3 brokers)
- Zeek sensor (DaemonSet)
- Flink feature computation job
- MinIO (S3-compatible storage)
- Redis Sentinel (3-node HA)
- Feast feature store
- MLflow tracking server
- OPA (policy engine)
- Backstage (developer portal)
- Kyverno (admission controller)
- Flagger (canary controller)

---

## Streamlit Dashboard

**Live:** https://secureflowll.streamlit.app/

Two modes:

### Demo Mode
Runs the synthetic traffic pipeline on 1,13,836 simulated banking API endpoints across 17 domains. Classifies active/deprecated/orphaned and scores security posture.

### Real Mode
Upload your codebase as a `.zip` file. Scans for API routes across multiple frameworks:
- Python: Flask, FastAPI, Django
- JavaScript: Express, NestJS
- Java: Spring Boot
- Go: Gin

Detects zombie endpoints, security vulnerabilities (hardcoded secrets, SQL injection, debug mode), and generates a full security posture report.

**Test it:** Upload `demo/test-codebase/banking-api.zip` -- 74 routes across 5 frameworks, 9 zombie APIs detected.

---

## Generating Synthetic Data

The traffic simulator generates realistic Union Bank-scale data with 1,13,836 API endpoints across 17 banking domains.

```bash
python demo/traffic-generator/simulate.py --generate-features
# Output: demo/test-data/endpoint_features.parquet
```

**What the simulator models:**
- 17 banking domains (Accounts, UPI, NEFT, IMPS, RTGS, Cards, Loans, KYC, etc.)
- 1,13,836 unique endpoints with version drift (v1/v2/v3)
- Realistic traffic patterns per domain (critical, high, moderate, low, batch)
- Overlapping feature distributions (forces multi-feature learning)
- 20+ user-agents (real browsers, mobile apps, monitoring tools)
- Annual cost estimation in INR per endpoint

---

## Dependencies

### Python

```
xgboost          # Gradient boosting classifier
shap             # SHAP explanations
mlflow           # Experiment tracking + model registry
pandas           # Data manipulation
numpy            # Numerical computation
scikit-learn     # Metrics, train/test split
pyarrow          # Parquet file support
boto3            # S3/MinIO client
optuna           # Hyperparameter optimization
cloudpickle      # Model serialization
requests         # HTTP client (WAF poller)
confluent-kafka  # Kafka producer
streamlit        # Dashboard
```

### Java (Flink Job)

```
Apache Flink 1.19.0 (streaming, Kafka connector, Avro)
Jackson 2.17.0 (JSON parsing)
```

### Infrastructure (Kubernetes)

| Component | Version | Namespace |
|-----------|---------|-----------|
| Strimzi Kafka Operator | 0.39+ | listen |
| Apache Flink Operator | 1.8+ | listen |
| MinIO | latest | remember |
| Redis Sentinel | 7.x | remember |
| Feast | 0.37+ | remember |
| MLflow | 2.x | detect |
| OPA | 0.62+ | enforce |
| Backstage | 1.x | enforce |
| Kyverno | 1.11+ | enforce |
| Flagger | 1.x | flagger |
| MetalLB | 0.14+ | metallb-system |

---

## How It Works

### Discovery Methods

| Method | Layer | Coverage | Status |
|--------|-------|----------|--------|
| Passive Network Capture (Zeek) | Layer 2 | All internal HTTP traffic | Primary |
| WAF Log Integration | Application | External-facing APIs | Active |
| API Gateway Integration | Application | All routed traffic | Planned |
| Frontend Static Analysis | Build time | Client-side API calls | Active |
| Staging Scanner (Kiterunner) | Application | Staging environments only | Active |

### ML Classification

**Model:** XGBoost classifier (500 trees, max depth 8)

**Features:** 16 signals per endpoint measuring traffic volume, synthetic ratio, authentication patterns, HTTP status distribution, payload characteristics, and timing regularity.

**Explainability:** SHAP TreeExplainer generates human-readable explanations for every prediction.

**Safety:** Ensemble disagreement > 0.3 triggers automatic human review.

### Three-Stage Decommission

| Stage | Timeline | Action | Gate |
|-------|----------|--------|------|
| 1 -- Watch Only | Weeks 1-4 | Classify + report, no actions | F1 >= 0.85 + governance charter signed |
| 2 -- Tell Owner | Weeks 5-12 | Auto-open GitHub issue per zombie | Owner responds (confirm/dispute/exempt) |
| 3 -- Turn It Off | Week 13+ | Canary -> slow drain -> remove | 2 human approvers + 24h canary + 10-day drain |

---

## Known Limitations

1. **TLS/mTLS encrypted traffic** -- Zeek cannot inspect metadata from end-to-end encrypted service mesh traffic. Documented as accepted risk.

2. **Cron/batch APIs** -- Endpoints called once daily or weekly require a 90-day minimum observation window to avoid false positives.

3. **External partner APIs** -- Only visible through WAF logs, not internal Zeek capture. Requires WAF log integration to be active.

4. **Legacy non-HTTP protocols** -- SOAP/gRPC traffic may not be captured by HTTP log scripts. Fallback: Zeek conn.log for connection-level metadata.

5. **Model cold start** -- XGBoost requires sufficient labeled data. Initial training uses synthetic data; real-world accuracy improves with Stage 2 owner feedback.

---

## License

MIT

---

**Built for PSB Hackathon iDEA 2.0 -- Problem Statement PS9**

**Team Logic Legion** -- Sunandan Basantia, Rudra Pratap Sahoo, Karan Sharma, Ayush Pandey

---

![Footer](https://img.shields.io/badge/Union_Bank_of_India-Hackathon_2026-blue?style=for-the-badge)
