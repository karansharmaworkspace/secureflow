# Demo Scripts

Automation scripts for setting up the demo environment, generating synthetic test data, and deploying the SecureFlow platform on a local kind Kubernetes cluster.

## Files

### deploy-all.sh — Full Platform Deployment

**Language:** Bash. Uses `set -euo pipefail` for strict error handling.

**Deployment Phases (6 phases):**

Phase 1 — **Infrastructure:** Creates namespaces (listen, remember, detect, enforce, act) via `kubectl create ns`. Applies RBAC config from `infra/k8s/rbac.yaml`. Deploys Strimzi Kafka Operator, waits for readiness, then deploys 3-broker Kafka cluster (`kubectl wait kafka/kafka-cluster -n listen --for=condition=Ready --timeout=300s`). Creates Kafka topics and ACLs. Applies network policies.

Phase 2 — **Streaming Pipeline:** Deploys Flink Operator, waits 10s for CRD registration. Deploys MinIO with PVCs and bucket initialization job. Deploys Redis Sentinel 3-node StatefulSet. Deploys Feast serving layer.

Phase 4 — **ML Pipeline:** Deploys MLflow tracking server in `detect` namespace.

Phase 5 — **Policy & Catalog:** Deploys OPA policy engine in `enforce` namespace. Deploys Backstage developer portal.

Phase 6 — **Canary:** Installs Flagger canary controller. Starts a traffic generator pod that runs `simulate.py` inline (`python -c "$(cat demo/traffic-generator/simulate.py)"`).

**Error Handling:** Uses `2>/dev/null || true` on namespace creation (ignore already-exists errors). Deploy continues even if some components have transient failures.

### generate-test-data.ps1 — Synthetic Data Generation (Windows)

**Language:** PowerShell.

**Pipeline:**
1. Creates output directory `demo/test-data`
2. Installs Python dependencies: `pandas`, `pyarrow`, `numpy`
3. Runs `simulate.py --generate-features` to generate ~1,13,836 endpoint features
4. Verifies output by loading the parquet file with pandas and printing shape

### run-ml-demo.sh — End-to-End ML Pipeline

**Language:** Bash.

**Pipeline (6 steps):**
1. **Generate feature data:** Runs `simulate.py --generate-features` to create `endpoint_features.parquet` with 1,13,836 rows x 30 columns
2. **Install dependencies:** `pip install -q -r ml-pipeline/requirements.txt`
3. **Start MLflow:** Launches `mlflow server --host 0.0.0.0 --port 5000` in background, captures PID
4. **Train XGBoost model:** Sets `MLFLOW_TRACKING_URI`, `MLFLOW_EXPERIMENT_NAME`, `DATA_PATH` environment variables and runs `train.py`. Trains 500-tree XGBoost classifier with SHAP explainer, logs metrics/artifacts to MLflow
5. **Test prediction:** Creates a test JSON with 2 endpoints (1 zombie: 100% synthetic, 0 real calls; 1 active: diverse traffic, auth ratio 0.95). Fetches latest model from MLflow and runs `predict.py` with SHAP explanations
6. **OPA policy evaluation:** Tests 3 scenarios against OPA (`/v1/data/zombie/decommission`):
   - v1 zombie (F1=0.92, 100% synthetic, low disagreement) → should `allow: true`
   - v3 active (F1=0.92, real traffic, low disagreement) → should `allow: false`
   - disputed (F1=0.92, synthetic, high disagreement=0.4) → should require human review
   Prints `allow`, `decision`, and `human_review` for each case

### setup-kind.sh — kind Cluster + MetalLB

**Language:** Bash.

**Process:**
1. Creates a kind cluster named `zombie-platform-demo` using config from `demo/kind-config.yaml` with Kubernetes version `v1.29.2` (configurable via `K8S_VERSION` env var)
2. Verifies cluster connectivity with `kubectl cluster-info --context kind-zombie-platform-demo`
3. Installs MetalLB v0.14.5 from raw GitHub manifests for LoadBalancer support
4. Waits for MetalLB pods to be ready (`--timeout=120s`)
5. Creates an IP address pool using the Docker kind network subnet (auto-detected) with range `{subnet}.255.200-{subnet}.255.250`
6. Creates L2Advertisement for the pool

### verify.sh — Component Health Verification

**Language:** Bash. Uses counters (`PASS`/`FAIL`) and color-coded output.

**Verification Checks (16 total):**
1. **Cluster:** `kubectl cluster-info` with kind context
2. **Namespaces:** Checks all 8 namespaces (listen, remember, detect, enforce, act, kafka, flink, flagger, kyverno)
3. **Kafka:** Checks KafkaCluster CRD status (True/False), checks `raw-api-calls` topic exists
4. **Zeek:** Checks DaemonSet exists in `listen` namespace
5. **Flink:** Checks `FlinkDeployment` CRD exists
6. **MinIO:** Checks deployment exists in `remember`
7. **Redis:** Checks StatefulSet exists in `remember`
8. **Feast:** Checks `feast-serving` deployment exists
9. **MLflow:** Checks deployment exists in `detect`
10. **OPA:** Checks deployment + pod phase (Running)
11. **Backstage:** Checks deployment exists in `enforce`
12. **Flagger:** Checks flagger namespace exists
13. **Traffic Generator:** Checks pod phase (Running)
14. **OPA Policy Test:** Executes a test policy evaluation inside the OPA pod using `wget` with POST data: `{"input":{"endpoint_key":"test","f1_score":0.92,"is_100pct_synthetic":true,"ensemble_disagreement":0.1,...}}`. Asserts `"allow":true` in response

**Exit Code:** Returns number of failures (0 = all passed).
