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

### ⏱️ 15 Days → 30 Min
Manual decommission time reduced by **99.8%**

</td>
<td align="center" width="33%">

### 💰 ₹4.8L/Year Saved
Per zombie endpoint decommissioned

</td>
<td align="center" width="33%">

### 🎯 F1 ≥ 0.85
ML threshold before any automated action

</td>
</tr>
</table>

</div>

---

## 📋 Table of Contents

<details>
<summary><strong>📂 Navigation</strong></summary>

- [🎯 The Problem](#-the-problem)
- [🏗️ Architecture](#️-architecture)
- [📁 Repository Structure](#-repository-structure)
- [🚀 Getting Started](#-getting-started)
  - [⚙️ Prerequisites](#️-prerequisites)
  - [⚡ Quick Start — ML Pipeline Only](#-quick-start--ml-pipeline-only)
  - [☸️ Full Platform — Local Kubernetes](#️-full-platform--local-kubernetes)
- [🎲 Generating Synthetic Data](#-generating-synthetic-data)
- [📦 Dependencies](#-dependencies)
- [🔧 How It Works](#-how-it-works)
  - [🔍 Discovery Methods](#-discovery-methods)
  - [🤖 ML Classification](#-ml-classification)
  - [🔄 Three-Stage Decommission](#-three-stage-decommission)
- [⚙️ Configuration](#️-configuration)
- [⚠️ Known Limitations](#️-known-limitations)
- [📜 Regulatory Compliance](#-regulatory-compliance)
- [或许 License](#-license)

</details>

---

## 🎯 The Problem

<div align="center">

> **Every bank running APIs for 5+ years has zombie endpoints — old, forgotten API routes that haunt your infrastructure.**

</div>

<table>
<tr>
<td width="50%">

### 😱 The Zombie Threat

- ✅ Still run on the network and are accessible
- ✅ No longer used by real users or services
- ✅ Excluded from security scanning
- ✅ Create unmonitored attack surfaces
- ✅ Cost money to maintain

</td>
<td width="50%">

### 💸 Business Impact

| Metric | Value |
|--------|-------|
| Manual discovery time | **15+ engineer-days per endpoint** |
| Cost per zombie/year | **~₹4.8 Lakhs** |
| Security risk | **High — unpatched, forgotten** |
| Compliance exposure | **OWASP API Top 10 violations** |

</td>
</tr>
</table>

### 🔄 Platform Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│   │ DISCOVER │ → │ CLASSIFY │ → │   NOTIFY │ → │ DECOMMISSION │             │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘              │
│                                                                             │
│   • Zeek/WAF     • XGBoost      • GitHub Issues   • Canary Deploy           │
│   • Kafka        • SHAP         • Owner Response  • Slow Drain              │
│   • Flink        • MLflow       • 30-Day Window   • Audit Trail             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

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
│  👁️  LISTEN LAYER                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │    ZEEK     │ →  │    KAFKA    │ →  │    FLINK    │                    │
│  │   Sensor    │    │   Cluster   │    │ Feature Job │                    │
│  │  (DaemonSet)│    │ (3 Brokers) │    │   (Java)    │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼─────────────────────────────────────┐
│  🧠 REMEMBER LAYER                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │    FEAST    │    │    REDIS    │    │    MINIO    │                    │
│  │ Feature Store│   │  (Sentinel) │    │ S3 Compat   │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼─────────────────────────────────────┐
│  🔍 DETECT LAYER                                                           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   XGBOOST   │    │    SHAP     │    │   MLFLOW    │                    │
│  │ Classifier  │    │  Explainer  │    │  Tracking   │                    │
│  │ (500 Trees) │    │  (Explain)  │    │  (Registry) │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼─────────────────────────────────────┐
│  🛡️  ENFORCE LAYER                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │     OPA     │    │   KYVERNO   │    │  BACKSTAGE  │                    │
│  │ Policy Engine│   │  Admission  │    │  Developer  │                    │
│  │   (Rego)    │    │ Controller  │    │   Portal    │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼─────────────────────────────────────┐
│  ⚡ ACT LAYER                                                               │
│  ┌─────────────────────────┐    ┌─────────────────────────┐                │
│  │    GITHUB ACTIONS       │ →  │        FLAGGER          │                │
│  │   (Orchestration)       │    │   (Canary Deployment)   │                │
│  └─────────────────────────┘    └─────────────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

<details>
<summary><strong>📂 Click to Expand Full Directory Tree</strong></summary>

```
.
├── .github/workflows/          # 🔄 GitHub Actions for 3-stage decommission
│   ├── stage1-watch-only.yml   # 📊 Daily classification report
│   ├── stage2-tell-owner.yml   # 📧 Open GitHub issue for zombie candidates
│   └── stage3-turn-it-off.yml  # 🔌 Canary → slow drain → remove
│
├── compliance/                 # 📜 Regulatory documentation
│   ├── compliance-checklist.md # ✅ Compliance verification
│   ├── governance-charter.md   # 📋 Governance framework
│   └── regulatory-mapping.md   # 🔗 Standards mapping
│
├── demo/                       # 🎮 Demo and testing
│   ├── kind-config.yaml        # ☸️ kind cluster config (3 nodes)
│   ├── scripts/
│   │   ├── deploy-all.sh       # 🚀 Full platform deployment
│   │   ├── generate-test-data.ps1 # 🎲 Generate synthetic data
│   │   ├── run-ml-demo.sh      # 🤖 ML pipeline demo
│   │   ├── setup-kind.sh       # ⚙️ kind + MetalLB setup
│   │   └── verify.sh           # 🔍 Component health checks
│   └── traffic-generator/
│       ├── simulate.py         # 🎯 Union Bank-scale traffic simulator
│       └── Dockerfile          # 🐳 Container build
│
├── discovery/                  # 🔍 API discovery methods
│   ├── frontend-analyzer/      # 🌐 Playwright-based JS bundle analysis
│   ├── staging-scanner/        # 🎯 Kiterunner-style path scanner
│   │   ├── scanner.sh          # 🔍 Scanner script
│   │   └── Dockerfile          # 🐳 Container build
│   └── waf-poller/             # 📡 WAF log integration
│       ├── main.py             # 🐍 Python poller
│       └── Dockerfile          # 🐳 Container build
│
├── flink-job/                  # ⚡ Apache Flink feature computation (Java)
│   ├── pom.xml                 # 📦 Maven dependencies
│   └── src/                    # 📂 Source code
│
├── infra/                      # ☸️ Kubernetes infrastructure
│   ├── k8s/
│   │   ├── kafka/              # 📨 Strimzi operator + cluster + ACLs
│   │   ├── flink/              # ⚡ Flink operator + deployment + topics
│   │   ├── minio/              # 💾 MinIO deployment + buckets
│   │   ├── redis/              # ⚡ Redis Sentinel (3-node)
│   │   ├── feast/              # 🧠 Feast feature store
│   │   ├── mlflow/             # 📊 MLflow tracking server
│   │   ├── opa/                # 🛡️  Open Policy Agent
│   │   ├── backstage/          # 🎭 Backstage developer portal
│   │   ├── kyverno/            # 🔒 Kyverno admission controller + policies
│   │   ├── flagger/            # 🚩 Flagger canary controller
│   │   ├── rbac.yaml           # 👤 Role-based access control
│   │   ├── network-policies.yaml # 🌐 Network segmentation
│   │   └── namespaces.yaml     # 📂 Namespace definitions
│   └── zeek/
│       ├── zeek-daemonset.yaml # 👁️ Zeek sensor deployment
│       └── scripts/
│           └── stream-to-kafka.py # 📨 Zeek → Kafka bridge
│
├── ml-pipeline/                # 🤖 ML training and inference
│   ├── train.py                # 🎓 XGBoost training with MLflow tracking
│   ├── predict.py              # 🔮 Classification with SHAP explanations
│   ├── features.py             # 📊 Feature column definitions
│   ├── requirements.txt        # 📦 Python dependencies
│   ├── Dockerfile              # 🐳 Container build
│   └── tests/                  # 🧪 Unit tests
│
├── demo-all.ps1                # 🎮 One-command full demo (Windows)
├── requirements.txt            # 📦 Root Python dependencies
└── Plan.md                     # 📋 Full architecture and design document
```

</details>

---

## 🚀 Getting Started

### ⚙️ Prerequisites

<table>
<tr>
<td width="50%">

#### 🔧 Core Tools

| Tool | Version | Purpose |
|------|---------|---------|
| 🐍 Python | 3.11+ | ML pipeline, traffic generator |
| ☕ Java | 11+ | Flink job compilation |
| 📦 Maven | 3.8+ | Flink job build |
| 🐳 Docker | 24+ | Container builds |

</td>
<td width="50%">

#### ☸️ Kubernetes Tools

| Tool | Version | Purpose |
|------|---------|---------|
| ☸️ kind | 0.20+ | Local Kubernetes cluster |
| 🔧 kubectl | 1.29+ | Kubernetes management |
| 📊 MLflow | 2.x | Model tracking |

</td>
</tr>
</table>

---

### ⚡ Quick Start — ML Pipeline Only

<div align="center">

**Run the ML pipeline locally without Kubernetes**

</div>

```bash
# 📦 1. Install Python dependencies
pip install -r requirements.txt

# 🎲 2. Generate synthetic training data (10,000+ endpoints)
python demo/traffic-generator/simulate.py --generate-features
# Output: demo/test-data/endpoint_features.parquet

# 📊 3. Start MLflow tracking server
mlflow server --host 127.0.0.1 --port 5000

# 🎓 4. Train XGBoost model
MLFLOW_TRACKING_URI=http://localhost:5000 \
MLFLOW_EXPERIMENT_NAME=zombie-classification \
DATA_PATH=demo/test-data/endpoint_features.parquet \
  python ml-pipeline/train.py

# 🔮 5. Test prediction
python ml-pipeline/predict.py test_features.json
```

<div align="center">

**Or use the demo script:**

```bash
# 🐧 Linux/macOS
bash demo/scripts/run-ml-demo.sh

# 🪟 Windows (PowerShell)
./demo-all.ps1
```

</div>

---

### ☸️ Full Platform — Local Kubernetes

<div align="center">

**Deploy the entire 5-layer platform on a local kind cluster**

</div>

<table>
<tr>
<td width="50%">

#### 🚀 Option A: One Command (Windows)

```powershell
./demo-all.ps1
```

#### 🔧 Option B: Step by Step

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

#### 📦 What Gets Deployed

| Component | Status |
|-----------|--------|
| 📨 Kafka (Strimzi, 3 Brokers) | ✅ |
| 👁️ Zeek Sensor (DaemonSet) | ✅ |
| ⚡ Flink Feature Job | ✅ |
| 💾 MinIO (S3 Compat) | ✅ |
| ⚡ Redis Sentinel (3-Node HA) | ✅ |
| 🧠 Feast Feature Store | ✅ |
| 📊 MLflow Tracking | ✅ |
| 🛡️ OPA Policy Engine | ✅ |
| 🎭 Backstage Portal | ✅ |
| 🔒 Kyverno Admission | ✅ |
| 🚩 Flagger Canary | ✅ |

</td>
</tr>
</table>

#### 🔌 Access Services After Deployment

```bash
# 📊 MLflow UI
kubectl port-forward -n detect svc/mlflow 5000:5000

# 🛡️ OPA Policy API
kubectl port-forward -n enforce svc/opa 8181:8181

# 🎭 Backstage Developer Portal
kubectl port-forward -n enforce svc/backstage 7007:7007

# 💾 MinIO Console
kubectl port-forward -n remember svc/minio-console 9001:9001
```

---

## 🎲 Generating Synthetic Data

<div align="center">

**The traffic simulator generates realistic Union Bank-scale data with 10,000+ API endpoints across 17 banking domains.**

</div>

```bash
# 🎲 Generate feature dataset
python demo/traffic-generator/simulate.py --generate-features

# 📁 Output: demo/test-data/endpoint_features.parquet
# 📊 ~10,000 rows × 30 columns (16 features + metadata + labels)
```

<table>
<tr>
<td width="50%">

#### 🎯 What the Simulator Models

- 🏦 **17 banking domains** (Accounts, UPI, NEFT, IMPS, RTGS, Cards, Loans, KYC, etc.)
- 🔢 **10,000+ unique endpoints** with version drift (v1/v2/v3)
- 📈 **Realistic traffic patterns** per domain (critical, high, moderate, low, batch)
- 🎲 **Overlapping feature distributions** (forces multi-feature learning)
- 🌐 **20+ user-agents** (real browsers, mobile apps, monitoring tools)
- 💰 **Annual cost estimation** in INR per endpoint

</td>
<td width="50%">

#### 📊 Dataset Columns

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

## 📦 Dependencies

<details>
<summary><strong>🐍 Python Dependencies</strong></summary>

```
# 📦 requirements.txt
xgboost          # 🚀 Gradient boosting classifier
shap             # 🔮 SHAP explanations
mlflow           # 📊 Experiment tracking + model registry
pandas           # 🐼 Data manipulation
numpy            # 🔢 Numerical computation
scikit-learn     # 🎯 Metrics, train/test split
pyarrow          # 📁 Parquet file support
boto3            # ☁️ S3/MinIO client
optuna           # ⚡ Hyperparameter optimization
cloudpickle      # 📦 Model serialization

# 🔍 Discovery components
requests         # 🌐 HTTP client (WAF poller)
confluent-kafka  # 📨 Kafka producer (WAF/Zeek → Kafka)
```

</details>

<details>
<summary><strong>☕ Java Dependencies</strong></summary>

```xml
<!-- flink-job/pom.xml -->
Apache Flink 1.19.0 (streaming, Kafka connector, Avro)
Jackson 2.17.0 (JSON parsing)
```

</details>

<details>
<summary><strong>☸️ Infrastructure Dependencies</strong></summary>

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

## 🔧 How It Works

### 🔍 Discovery Methods

<table>
<tr>
<td width="60%">

| Method | Layer | Coverage | Status |
|--------|-------|----------|--------|
| 👁️ Passive Network Capture (Zeek) | Layer 2 | All internal HTTP traffic | 🟢 Primary |
| 📡 WAF Log Integration | Application | External-facing APIs | 🟢 Active |
| 🔌 API Gateway Integration | Application | All routed traffic | 🟡 Planned |
| 🌐 Frontend Static Analysis | Build time | Client-side API calls | 🟢 Active |
| 🎯 Staging Scanner (Kiterunner) | Application | Staging environments only | 🟢 Active |

</td>
<td width="40%">

#### 🔑 Key Insight

> **Layer 2 mirroring bypasses WAF completely** — Zeek sees everything on the internal network, regardless of WAF rules.

This is critical because Union Bank's WAF blocks external OSINT approaches.

</td>
</tr>
</table>

---

### 🤖 ML Classification

<table>
<tr>
<td width="50%">

#### 🎯 Model Specifications

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

#### 📊 16 Features Per Endpoint

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

#### 🔮 SHAP Explainability

<div align="center">

**Every prediction comes with a human-readable explanation**

</div>

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔮 SHAP Explanation for Endpoint: api.bank.example.com|GET|/api/v1/users  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  real_calls=0.00          (low,  -1.92)  ████████████████████░░░░░░░░░░░░  │
│  is_100pct_synthetic=True (low,  -1.64)  ████████████████░░░░░░░░░░░░░░░░  │
│  auth_ratio=0.00          (low,  -1.40)  ██████████████░░░░░░░░░░░░░░░░░░  │
│  unique_user_agents=1     (low,  -0.87)  █████████░░░░░░░░░░░░░░░░░░░░░░  │
│  unique_source_ips=1      (low,  -0.65)  ███████░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                                                             │
│  🎯 Prediction: ZOMBIE (confidence: 0.94)                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 🛡️ Safety Mechanism

<div align="center">

**Ensemble Disagreement Detection**

</div>

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Model A Prediction:  ZOMBIE (0.92)  ─┐                                    │
│                                        ├─→ Disagreement: 0.35 > 0.30      │
│  Model B Prediction:  ACTIVE (0.57)  ─┘                                    │
│                                                                             │
│  ⚠️  AUTOMATIC HUMAN REVIEW TRIGGERED                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 🔄 Three-Stage Decommission

<div align="center">

**Progressive rollout with safety gates at every stage**

</div>

<table>
<tr>
<td width="33%" align="center">

#### 📊 Stage 1: Watch Only
**Weeks 1–4**

---

✅ Classify endpoints
✅ Generate reports
✅ No automated actions

**Exit Criteria:**
- F1 ≥ 0.85
- Governance charter signed

</td>
<td width="34%" align="center">

#### 📧 Stage 2: Tell Owner
**Weeks 5–12**

---

✅ Auto-open GitHub issue
✅ Include SHAP explanation
✅ 30-day response window

**Owner Options:**
- Confirm (zombie)
- Dispute (evidence)
- Request Exemption

</td>
<td width="33%" align="center">

#### 🔌 Stage 3: Turn It Off
**Week 13+**

---

✅ 24h canary at 1% traffic
✅ 10-day slow drain
✅ Remove endpoint

**Safety Gates:**
- 2 human approvers
- Automatic rollback on anomaly
- Full audit trail

</td>
</tr>
</table>

#### 🔄 Decommission Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │ Zombie   │ → │ Canary   │ → │   Slow   │ → │ Remove   │             │
│  │ Detected │    │  1% 24h  │    │  Drain   │    │ Endpoint │             │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘             │
│                                                                             │
│       │              │              │              │                        │
│       ▼              ▼              ▼              ▼                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │   OPA    │    │  Flagger │    │   OPA    │    │ Backstage│             │
│  │  Policy  │    │  Canary  │    │  Policy  │    │ Archive  │             │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuration

### 🔧 Environment Variables

<table>
<tr>
<td width="50%">

#### 🤖 ML Pipeline

| Variable | Default |
|----------|---------|
| `MLFLOW_TRACKING_URI` | `http://mlflow.remember.svc:5000` |
| `MLFLOW_EXPERIMENT_NAME` | `zombie-classification` |
| `DATA_PATH` | `s3://feature-snapshots/endpoint_features.parquet` |
| `MODEL_URI` | `models:/zombie-classifier/latest` |

</td>
<td width="50%">

#### 🏗️ Infrastructure

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

## ⚠️ Known Limitations

<table>
<tr>
<td width="50%">

#### 🔒 Technical Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **TLS/mTLS encrypted traffic** | Zeek cannot inspect metadata | Documented as accepted risk |
| **Cron/batch APIs** | Called once daily/weekly | 90-day minimum observation window |
| **Legacy non-HTTP protocols** | SOAP/gRPC not captured | Zeek `conn.log` fallback |

</td>
<td width="50%">

#### 🌐 Coverage Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **External partner APIs** | Only visible in WAF logs | WAF log integration required |
| **Model cold start** | Needs labeled data | Synthetic data + Stage 2 feedback |
| **Single-cluster demo** | kind (3 nodes) only | Production needs multi-node + SPAN/TAP |

</td>
</tr>
</table>

---

## 📜 Regulatory Compliance

<div align="center">

**Full compliance coverage for banking regulations**

</div>

<table>
<tr>
<td width="50%">

| Standard | Coverage |
|----------|----------|
| 🛡️ **OWASP API Top 10** | API2 (Broken Auth), API7 (Misconfiguration), API9 (Improper Inventory) |
| 🔒 **NIST CSF 2.0** | All 5 functions: Identify, Protect, Detect, Respond, Recover |
| 🇪🇺 **GDPR Article 25** | Metadata-only capture, no PII in SHAP, 30-day raw log retention |

</td>
<td width="50%">

| Standard | Coverage |
|----------|----------|
| 💳 **PCI-DSS v4 Req 3** | Zeek redaction of card data, AES-256 at rest, Kafka ACLs |
| 🇮🇳 **RBI IT Framework** | Asset inventory (Backstage), vuln SLAs, change management (OPA audit) |
| 🌐 **ISO 27001 A8.8** | Full lifecycle: detection → classification → removal |

</td>
</tr>
</table>

---

## 📄 License

<div align="center">

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

**MIT License**

</div>

---

<div align="center">

### 🏆 Built for PSB Hackathon iDEA 2.0 — Problem Statement PS9

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
