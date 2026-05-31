<div align="center">

<img src="logo.jpeg" alt="SecureFlow Logo" width="200">

# SecureFlow

### PSB Hackathon iDEA 2.0 — Problem Statement PS9

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

### [TIME] 15 Days → 30 Min
Manual decommission time reduced by **99.8%**

</td>
<td align="center" width="33%">

### [COST] ₹4.8L/Year Saved
Per zombie endpoint decommissioned

</td>
<td align="center" width="33%">

### [TARGET] F1 ≥ 0.85
ML threshold before any automated action

</td>
</tr>
</table>

</div>

---

## [DOC] Table of Contents

<details>
<summary><strong>[DIR] Navigation</strong></summary>

- [[TARGET] The Problem](#-the-problem)
- [[BUILD] Architecture](#️-architecture)
- [[FOLDER] Repository Structure](#-repository-structure)
- [[LAUNCH] Getting Started](#-getting-started)
  - [[SETUP] Prerequisites](#️-prerequisites)
  - [[FAST] Quick Start — ML Pipeline Only](#-quick-start--ml-pipeline-only)
  - [[K8S] Full Platform — Local Kubernetes](#️-full-platform--local-kubernetes)
- [[DATA] Generating Synthetic Data](#-generating-synthetic-data)
- [[PKG] Dependencies](#-dependencies)
- [[WRENCH] How It Works](#-how-it-works)
  - [[SEARCH] Discovery Methods](#-discovery-methods)
  - [[BOT] ML Classification](#-ml-classification)
  - [[CYCLE] Three-Stage Decommission](#-three-stage-decommission)
- [[SETUP] Configuration](#️-configuration)
- [[WARN] Known Limitations](#️-known-limitations)
- [[SCROLL] Regulatory Compliance](#-regulatory-compliance)
- [[LIC] License](#-license)

</details>

---

## [TARGET] The Problem

<div align="center">

> **Every bank running APIs for 5+ years has zombie endpoints — old, forgotten API routes that haunt your infrastructure.**

</div>

<table>
<tr>
<td width="50%">

### [ALERT] The Zombie Threat

- [OK] Still run on the network and are accessible
- [OK] No longer used by real users or services
- [OK] Excluded from security scanning
- [OK] Create unmonitored attack surfaces
- [OK] Cost money to maintain

</td>
<td width="50%">

### [MONEY] Business Impact

| Metric | Value |
|--------|-------|
| Manual discovery time | **15+ engineer-days per endpoint** |
| Cost per zombie/year | **~₹4.8 Lakhs** |
| Security risk | **High — unpatched, forgotten** |
| Compliance exposure | **OWASP API Top 10 violations** |

</td>
</tr>
</table>

### [CYCLE] Platform Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│   │ DISCOVER │ →  │ CLASSIFY │ →  │  NOTIFY  │ →  │ DECOMMISSION │          │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘              │
│                                                                             │
│   • Zeek/WAF     • XGBoost      • GitHub Issues   • Canary Deploy           │
│   • Kafka        • SHAP         • Owner Response  • Slow Drain              │
│   • Flink        • MLflow       • 30-Day Window   • Audit Trail             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## [BUILD] Architecture

<div align="center">

### Five-Layer Platform Architecture

</div>

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CORE SWITCH (SPAN/TAP)                              │
│                    Layer 2 Mirroring — Bypasses WAF                         │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼─────────────────────────────────────┐
│  [EYE]️  LISTEN LAYER                                                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│  │    ZEEK     │ →  │    KAFKA    │ →  │    FLINK    │                      │
│  │   Sensor    │    │   Cluster   │    │ Feature Job │                      │
│  │  (DaemonSet)│    │ (3 Brokers) │    │   (Java)    │                      │
│  └─────────────┘    └─────────────┘    └─────────────┘                      │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼─────────────────────────────────────┐
│  [BRAIN] REMEMBER LAYER                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│  │    FEAST    │    │    REDIS    │    │    MINIO    │                      │
│  │Feature Store│    │  (Sentinel) │    │ S3 Compat   │                      │
│  └─────────────┘    └─────────────┘    └─────────────┘                      │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼─────────────────────────────────────┐
│  [SEARCH] DETECT LAYER                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│  │   XGBOOST   │    │    SHAP     │    │   MLFLOW    │                      │
│  │ Classifier  │    │  Explainer  │    │  Tracking   │                      │
│  │ (500 Trees) │    │  (Explain)  │    │  (Registry) │                      │
│  └─────────────┘    └─────────────┘    └─────────────┘                      │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼─────────────────────────────────────┐
│  [SHIELD]  ENFORCE LAYER                                                    │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│  │     OPA     │    │   KYVERNO   │    │  BACKSTAGE  │                      │
│  │Policy Engine│    │  Admission  │    │  Developer  │                      │
│  │   (Rego)    │    │ Controller  │    │   Portal    │                      │
│  └─────────────┘    └─────────────┘    └─────────────┘                      │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼─────────────────────────────────────┐
│  [FAST] ACT LAYER                                                           │
│  ┌─────────────────────────┐    ┌─────────────────────────┐                 │
│  │    GITHUB ACTIONS       │ →  │        FLAGGER          │                 │
│  │   (Orchestration)       │    │   (Canary Deployment)   │                 │
│  └─────────────────────────┘    └─────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## [FOLDER] Repository Structure

<details>
<summary><strong>[DIR] Click to Expand Full Directory Tree</strong></summary>

```
.
├── .github/workflows/          # [CYCLE] GitHub Actions for 3-stage decommission
│   ├── stage1-watch-only.yml   # [CHART] Daily classification report
│   ├── stage2-tell-owner.yml   # [MAIL] Open GitHub issue for zombie candidates
│   └── stage3-turn-it-off.yml  # [PLUG] Canary → slow drain → remove
│
├── compliance/                 # [SCROLL] Regulatory documentation
│   ├── compliance-checklist.md # [OK] Compliance verification
│   ├── governance-charter.md   # [DOC] Governance framework
│   └── regulatory-mapping.md   # [LINK] Standards mapping
│
├── demo/                       # [GAME] Demo and testing
│   ├── kind-config.yaml        # [K8S] kind cluster config (3 nodes)
│   ├── scripts/
│   │   ├── deploy-all.sh       # [LAUNCH] Full platform deployment
│   │   ├── generate-test-data.ps1 # [DATA] Generate synthetic data
│   │   ├── run-ml-demo.sh      # [BOT] ML pipeline demo
│   │   ├── setup-kind.sh       # [SETUP] kind + MetalLB setup
│   │   └── verify.sh           # [SEARCH] Component health checks
│   └── traffic-generator/
│       ├── simulate.py         # [TARGET] Union Bank-scale traffic simulator
│       └── Dockerfile          # [WHALE] Container build
│
├── discovery/                  # [SEARCH] API discovery methods
│   ├── frontend-analyzer/      # [GLOBE] Playwright-based JS bundle analysis
│   ├── staging-scanner/        # [TARGET] Kiterunner-style path scanner
│   │   ├── scanner.sh          # [SEARCH] Scanner script
│   │   └── Dockerfile          # [WHALE] Container build
│   └── waf-poller/             # [SIGNAL] WAF log integration
│       ├── main.py             # [PY] Python poller
│       └── Dockerfile          # [WHALE] Container build
│
├── flink-job/                  # [FAST] Apache Flink feature computation (Java)
│   ├── pom.xml                 # [PKG] Maven dependencies
│   └── src/                    # [DIR] Source code
│
├── infra/                      # [K8S] Kubernetes infrastructure
│   ├── k8s/
│   │   ├── kafka/              # [INBOX] Strimzi operator + cluster + ACLs
│   │   ├── flink/              # [FAST] Flink operator + deployment + topics
│   │   ├── minio/              # [DISK] MinIO deployment + buckets
│   │   ├── redis/              # [FAST] Redis Sentinel (3-node)
│   │   ├── feast/              # [BRAIN] Feast feature store
│   │   ├── mlflow/             # [CHART] MLflow tracking server
│   │   ├── opa/                # [SHIELD]  Open Policy Agent
│   │   ├── backstage/          # [MASK] Backstage developer portal
│   │   ├── kyverno/            # [LOCK] Kyverno admission controller + policies
│   │   ├── flagger/            # [FLAG] Flagger canary controller
│   │   ├── rbac.yaml           # [USER] Role-based access control
│   │   ├── network-policies.yaml # [GLOBE] Network segmentation
│   │   └── namespaces.yaml     # [DIR] Namespace definitions
│   └── zeek/
│       ├── zeek-daemonset.yaml # [EYE]️ Zeek sensor deployment
│       └── scripts/
│           └── stream-to-kafka.py # [INBOX] Zeek → Kafka bridge
│
├── ml-pipeline/                # [BOT] ML training and inference
│   ├── train.py                # [HAT] XGBoost training with MLflow tracking
│   ├── predict.py              # [CRYSTAL] Classification with SHAP explanations
│   ├── features.py             # [CHART] Feature column definitions
│   ├── requirements.txt        # [PKG] Python dependencies
│   ├── Dockerfile              # [WHALE] Container build
│   └── tests/                  # [FLASK] Unit tests
│
├── demo-all.ps1                # [GAME] One-command full demo (Windows)
├── requirements.txt            # [PKG] Root Python dependencies
└── Plan.md                     # [DOC] Full architecture and design document
```

</details>

---

## [LAUNCH] Getting Started

### [SETUP] Prerequisites

<table>
<tr>
<td width="50%">

#### [WRENCH] Core Tools

| Tool | Version | Purpose |
|------|---------|---------|
| [PY] Python | 3.11+ | ML pipeline, traffic generator |
| [JAVA] Java | 11+ | Flink job compilation |
| [PKG] Maven | 3.8+ | Flink job build |
| [WHALE] Docker | 24+ | Container builds |

</td>
<td width="50%">

#### [K8S] Kubernetes Tools

| Tool | Version | Purpose |
|------|---------|---------|
| [K8S] kind | 0.20+ | Local Kubernetes cluster |
| [WRENCH] kubectl | 1.29+ | Kubernetes management |
| [CHART] MLflow | 2.x | Model tracking |

</td>
</tr>
</table>

---

### [FAST] Quick Start — ML Pipeline Only

<div align="center">

**Run the ML pipeline locally without Kubernetes**

</div>

```bash
# [PKG] 1. Install Python dependencies
pip install -r requirements.txt

# [DATA] 2. Generate synthetic training data (10,000+ endpoints)
python demo/traffic-generator/simulate.py --generate-features
# Output: demo/test-data/endpoint_features.parquet

# [CHART] 3. Start MLflow tracking server
mlflow server --host 127.0.0.1 --port 5000

# [HAT] 4. Train XGBoost model
MLFLOW_TRACKING_URI=http://localhost:5000 \
MLFLOW_EXPERIMENT_NAME=zombie-classification \
DATA_PATH=demo/test-data/endpoint_features.parquet \
  python ml-pipeline/train.py

# [CRYSTAL] 5. Test prediction
python ml-pipeline/predict.py test_features.json
```

<div align="center">

**Or use the demo script:**

```bash
# [PENGUIN] Linux/macOS
bash demo/scripts/run-ml-demo.sh

# [WIN] Windows (PowerShell)
./demo-all.ps1
```

</div>

---

### [K8S] Full Platform — Local Kubernetes

<div align="center">

**Deploy the entire 5-layer platform on a local kind cluster**

</div>

<table>
<tr>
<td width="50%">

#### [LAUNCH] Option A: One Command (Windows)

```powershell
./demo-all.ps1
```

#### [WRENCH] Option B: Step by Step

```bash
# 1️⃣ Create kind cluster + MetalLB
bash demo/scripts/setup-kind.sh

# 2️⃣ Deploy all 8 phases
bash demo/scripts/deploy-all.sh

# 3️⃣ Verify components
bash demo/scripts/verify.sh
```

</td>
<td width="50%">

#### [PKG] What Gets Deployed

| Component | Status |
|-----------|--------|
| [INBOX] Kafka (Strimzi, 3 Brokers) | [OK] |
| [EYE]️ Zeek Sensor (DaemonSet) | [OK] |
| [FAST] Flink Feature Job | [OK] |
| [DISK] MinIO (S3 Compat) | [OK] |
| [FAST] Redis Sentinel (3-Node HA) | [OK] |
| [BRAIN] Feast Feature Store | [OK] |
| [CHART] MLflow Tracking | [OK] |
| [SHIELD] OPA Policy Engine | [OK] |
| [MASK] Backstage Portal | [OK] |
| [LOCK] Kyverno Admission | [OK] |
| [FLAG] Flagger Canary | [OK] |

</td>
</tr>
</table>

#### [PLUG] Access Services After Deployment

```bash
# [CHART] MLflow UI
kubectl port-forward -n detect svc/mlflow 5000:5000

# [SHIELD] OPA Policy API
kubectl port-forward -n enforce svc/opa 8181:8181

# [MASK] Backstage Developer Portal
kubectl port-forward -n enforce svc/backstage 7007:7007

# [DISK] MinIO Console
kubectl port-forward -n remember svc/minio-console 9001:9001
```

---

## [DATA] Generating Synthetic Data

<div align="center">

**The traffic simulator generates realistic Union Bank-scale data with 10,000+ API endpoints across 17 banking domains.**

</div>

```bash
# [DATA] Generate feature dataset
python demo/traffic-generator/simulate.py --generate-features

# [FOLDER] Output: demo/test-data/endpoint_features.parquet
# [CHART] ~10,000 rows × 30 columns (16 features + metadata + labels)
```

<table>
<tr>
<td width="50%">

#### [TARGET] What the Simulator Models

- [BANK] **17 banking domains** (Accounts, UPI, NEFT, IMPS, RTGS, Cards, Loans, KYC, etc.)
- [NUM] **10,000+ unique endpoints** with version drift (v1/v2/v3)
- [CHART] **Realistic traffic patterns** per domain (critical, high, moderate, low, batch)
- [DATA] **Overlapping feature distributions** (forces multi-feature learning)
- [GLOBE] **20+ user-agents** (real browsers, mobile apps, monitoring tools)
- [COST] **Annual cost estimation** in INR per endpoint

</td>
<td width="50%">

#### [CHART] Dataset Columns

| Column | Description |
|--------|-------------|
| `endpoint_key` | Unique identifier: `host\|method\|path` |
| `total_calls` | Daily call volume |
| `synthetic_calls` | Calls from bots/monitors |
| `real_calls` | Calls from real users |
| `days_since_last_real_call` | Staleness indicator |
| `unique_user_agents` | UA diversity (1 = likely bot) |
| `unique_source_ips` | IP diversity |
| `auth_ratio` | Fraction of calls with auth tokens |
| `ratio_2xx / 4xx / 5xx` | HTTP status distribution |
| `response_size_mean / stddev` | Response payload stats |
| `interarrival_mean_ms / stddev_ms` | Call timing patterns |
| `unique_hours_of_day` | Time-of-day spread |
| `is_100pct_synthetic` | Flag: zero real traffic |
| `is_zombie` | **Label**: 1 = zombie, 0 = active |

</td>
</tr>
</table>

---

## [PKG] Dependencies

<details>
<summary><strong>[PY] Python Dependencies</strong></summary>

```
# [PKG] requirements.txt
xgboost          # [LAUNCH] Gradient boosting classifier
shap             # [CRYSTAL] SHAP explanations
mlflow           # [CHART] Experiment tracking + model registry
pandas           # [PANDA] Data manipulation
numpy            # [NUM] Numerical computation
scikit-learn     # [TARGET] Metrics, train/test split
pyarrow          # [FOLDER] Parquet file support
boto3            # ☁️ S3/MinIO client
optuna           # [FAST] Hyperparameter optimization
cloudpickle      # [PKG] Model serialization

# [SEARCH] Discovery components
requests         # [GLOBE] HTTP client (WAF poller)
confluent-kafka  # [INBOX] Kafka producer (WAF/Zeek → Kafka)
```

</details>

<details>
<summary><strong>[JAVA] Java Dependencies</strong></summary>

```xml
<!-- flink-job/pom.xml -->
Apache Flink 1.19.0 (streaming, Kafka connector, Avro)
Jackson 2.17.0 (JSON parsing)
```

</details>

<details>
<summary><strong>[K8S] Infrastructure Dependencies</strong></summary>

| Component | Version | Namespace |
|-----------|---------|-----------|
| Strimzi Kafka Operator | 0.39+ | `listen` |
| Apache Flink Operator | 1.8+ | `listen` |
| MinIO | latest | `remember` |
| Redis Sentinel | 7.x | `remember` |
| Feast | 0.37+ | `remember` |
| MLflow | 2.x | `detect` |
| OPA | 0.62+ | `enforce` |
| Backstage | 1.x | `enforce` |
| Kyverno | 1.11+ | `enforce` |
| Flagger | 1.x | `flagger` |
| MetalLB | 0.14+ | `metallb-system` |

</details>

---

## [WRENCH] How It Works

### [SEARCH] Discovery Methods

<table>
<tr>
<td width="60%">

| Method | Layer | Coverage | Status |
|--------|-------|----------|--------|
| [EYE]️ Passive Network Capture (Zeek) | Layer 2 | All internal HTTP traffic | [DOT] Primary |
| [SIGNAL] WAF Log Integration | Application | External-facing APIs | [DOT] Active |
| [PLUG] API Gateway Integration | Application | All routed traffic | [DOT] Planned |
| [GLOBE] Frontend Static Analysis | Build time | Client-side API calls | [DOT] Active |
| [TARGET] Staging Scanner (Kiterunner) | Application | Staging environments only | [DOT] Active |

</td>
<td width="40%">

#### [KEY] Key Insight

> **Layer 2 mirroring bypasses WAF completely** — Zeek sees everything on the internal network, regardless of WAF rules.

This is critical because Union Bank's WAF blocks external OSINT approaches.

</td>
</tr>
</table>

---

### [BOT] ML Classification

<table>
<tr>
<td width="50%">

#### [TARGET] Model Specifications

| Parameter | Value |
|-----------|-------|
| **Algorithm** | XGBoost Classifier |
| **Trees** | 500 |
| **Max Depth** | 8 |
| **Learning Rate** | 0.05 |
| **Subsample** | 0.8 |
| **Colsample** | 0.8 |
| **Early Stopping** | 20 rounds |

</td>
<td width="50%">

#### [CHART] 16 Features Per Endpoint

| Category | Features |
|----------|----------|
| **Volume** | `total_calls`, `synthetic_calls`, `real_calls` |
| **Staleness** | `days_since_last_real_call` |
| **Diversity** | `unique_user_agents`, `unique_source_ips` |
| **Auth** | `auth_ratio` |
| **HTTP Status** | `ratio_2xx`, `ratio_4xx`, `ratio_5xx` |
| **Payload** | `response_size_mean`, `response_size_stddev` |
| **Timing** | `interarrival_mean_ms`, `interarrival_stddev_ms` |
| **Pattern** | `unique_hours_of_day`, `is_100pct_synthetic` |

</td>
</tr>
</table>

#### [CRYSTAL] SHAP Explainability

<div align="center">

**Every prediction comes with a human-readable explanation**

</div>

```
┌─────────────────────────────────────────────────────────────────────────────┐
│[CRYSTAL] SHAP Explanation for Endpoint: api.bank.example.com|GET|/api/v1/users│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  real_calls=0.00          (low,  -1.92)  ████████████████████░░░░░░░░░░░░   │
│  is_100pct_synthetic=True (low,  -1.64)  ████████████████░░░░░░░░░░░░░░░░   │
│  auth_ratio=0.00          (low,  -1.40)  ██████████████░░░░░░░░░░░░░░░░░░   │
│  unique_user_agents=1     (low,  -0.87)  █████████░░░░░░░░░░░░░░░░░░░░░░    │
│  unique_source_ips=1      (low,  -0.65)  ███████░░░░░░░░░░░░░░░░░░░░░░░░    │
│                                                                             │
│  [TARGET] Prediction: ZOMBIE (confidence: 0.94)                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### [SHIELD] Safety Mechanism

<div align="center">

**Ensemble Disagreement Detection**

</div>

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Model A Prediction:  ZOMBIE (0.92)  ─┐                                     │
│                                        ├─→ Disagreement: 0.35 > 0.30        │
│  Model B Prediction:  ACTIVE (0.57)  ─┘                                     │
│                                                                             │
│  [WARN]  AUTOMATIC HUMAN REVIEW TRIGGERED                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### [CYCLE] Three-Stage Decommission

<div align="center">

**Progressive rollout with safety gates at every stage**

</div>

<table>
<tr>
<td width="33%" align="center">

#### [CHART] Stage 1: Watch Only
**Weeks 1–4**

---

[OK] Classify endpoints
[OK] Generate reports
[OK] No automated actions

**Exit Criteria:**
- F1 ≥ 0.85
- Governance charter signed

</td>
<td width="34%" align="center">

#### [MAIL] Stage 2: Tell Owner
**Weeks 5–12**

---

[OK] Auto-open GitHub issue
[OK] Include SHAP explanation
[OK] 30-day response window

**Owner Options:**
- Confirm (zombie)
- Dispute (evidence)
- Request Exemption

</td>
<td width="33%" align="center">

#### [PLUG] Stage 3: Turn It Off
**Week 13+**

---

[OK] 24h canary at 1% traffic
[OK] 10-day slow drain
[OK] Remove endpoint

**Safety Gates:**
- 2 human approvers
- Automatic rollback on anomaly
- Full audit trail

</td>
</tr>
</table>

#### [CYCLE] Decommission Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ Zombie   │ →  │ Canary   │ →  │   Slow   │ →  │ Remove   │               │
│  │ Detected │    │  1% 24h  │    │  Drain   │    │ Endpoint │               │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘               │
│                                                                             │
│       │              │              │              │                        │
│       ▼              ▼              ▼              ▼                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │   OPA    │    │  Flagger │    │   OPA    │    │ Backstage│               │
│  │  Policy  │    │  Canary  │    │  Policy  │    │ Archive  │               │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## [SETUP] Configuration

### [WRENCH] Environment Variables

<table>
<tr>
<td width="50%">

#### [BOT] ML Pipeline

| Variable | Default |
|----------|---------|
| `MLFLOW_TRACKING_URI` | `http://mlflow.remember.svc:5000` |
| `MLFLOW_EXPERIMENT_NAME` | `zombie-classification` |
| `DATA_PATH` | `s3://feature-snapshots/endpoint_features.parquet` |
| `MODEL_URI` | `models:/zombie-classifier/latest` |

</td>
<td width="50%">

#### [BUILD] Infrastructure

| Variable | Default |
|----------|---------|
| `MINIO_ENDPOINT` | `minio.remember.svc:9000` |
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka-cluster-kafka-bootstrap.listen.svc:9092` |
| `WAF_API_URL` | `https://waf.bank.example.com/api/v1/logs` |
| `WAF_API_KEY` | _(empty)_ |
| `POLL_INTERVAL_SECONDS` | `300` |

</td>
</tr>
</table>

---

## [WARN] Known Limitations

<table>
<tr>
<td width="50%">

#### [LOCK] Technical Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **TLS/mTLS encrypted traffic** | Zeek cannot inspect metadata | Documented as accepted risk |
| **Cron/batch APIs** | Called once daily/weekly | 90-day minimum observation window |
| **Legacy non-HTTP protocols** | SOAP/gRPC not captured | Zeek `conn.log` fallback |

</td>
<td width="50%">

#### [GLOBE] Coverage Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **External partner APIs** | Only visible in WAF logs | WAF log integration required |
| **Model cold start** | Needs labeled data | Synthetic data + Stage 2 feedback |
| **Single-cluster demo** | kind (3 nodes) only | Production needs multi-node + SPAN/TAP |

</td>
</tr>
</table>

---

## [SCROLL] Regulatory Compliance

<div align="center">

**Full compliance coverage for banking regulations**

</div>

<table>
<tr>
<td width="50%">

| Standard | Coverage |
|----------|----------|
| [SHIELD] **OWASP API Top 10** | API2 (Broken Auth), API7 (Misconfiguration), API9 (Improper Inventory) |
| [LOCK] **NIST CSF 2.0** | All 5 functions: Identify, Protect, Detect, Respond, Recover |
| [EU] **GDPR Article 25** | Metadata-only capture, no PII in SHAP, 30-day raw log retention |

</td>
<td width="50%">

| Standard | Coverage |
|----------|----------|
| [CARD] **PCI-DSS v4 Req 3** | Zeek redaction of card data, AES-256 at rest, Kafka ACLs |
| [IN] **RBI IT Framework** | Asset inventory (Backstage), vuln SLAs, change management (OPA audit) |
| [GLOBE] **ISO 27001 A8.8** | Full lifecycle: detection → classification → removal |

</td>
</tr>
</table>

---

## [PAGE] License

<div align="center">

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

**MIT License**

</div>

---

<div align="center">

### [TROPHY] Built for PSB Hackathon iDEA 2.0 — Problem Statement PS9

**Team Logic Legion**

---

<table>
<tr>
<td align="center">

**Sunandan Basantia**

</td>
<td align="center">

**Rudra Pratap Sahoo**

</td>
<td align="center">

**Karan Sharma**

</td>
<td align="center">

**Ayush Pandey**

</td>
</tr>
</table>

---

![Footer](https://img.shields.io/badge/Union_Bank_of_India-Hackathon_2026-blue?style=for-the-badge)

</div>
