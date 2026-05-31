<#
.SYNOPSIS
  Zombie API Platform - Full Demo Pipeline
.DESCRIPTION
  Run everything: ML test data, XGBoost training, kind cluster, all 8 phases, verification.
#>

$PASS = 0; $FAIL = 0
$GREEN = "Green"; $RED = "Red"; $YELLOW = "Yellow"; $CYAN = "Cyan"

function Write-Step($msg) { Write-Host "`n=== $msg ===" -ForegroundColor $CYAN }
function Write-Ok   { param($m) Write-Host "  OK $m" -ForegroundColor $GREEN; $script:PASS++ }
function Write-Fail { param($m) Write-Host "  FAIL $m" -ForegroundColor $RED;   $script:FAIL++ }
function Write-Info { param($m) Write-Host "  $m"   -ForegroundColor $YELLOW }

function Run-Native {
  param([scriptblock]$Cmd, [string]$Label)
  $output = & $Cmd 2>&1
  $ok = $LASTEXITCODE -eq 0
  if ($ok) { Write-Ok $Label } else { Write-Fail $Label }
  return $ok
}

# ===========================================================================
Write-Step "Zombie API Platform - Full Demo Pipeline"
Write-Host "This will:"
Write-Host "  1. Generate ML test data - 100K+ endpoints (Union Bank scale)"
Write-Host "  2. Train XGBoost and run prediction"
Write-Host "  3. Create kind cluster"
Write-Host "  4. Deploy all 8 platform phases"
Write-Host "  5. Run component verification"
Write-Host ""
$confirm = Read-Host "Proceed? (y/N)"
if ($confirm -notmatch '^[Yy]') { Write-Host "Aborted."; exit 0 }

# ===========================================================================
Write-Step "1 - ML Test Data"

$null = New-Item -ItemType Directory -Path "demo/test-data" -Force
Write-Info "Output directory: demo/test-data"

if (-not (Run-Native { python -m pip install pandas pyarrow numpy -q } "Python dependencies installed")) { exit 1 }

if (-not (Run-Native { python demo/traffic-generator/simulate.py --generate-features } "Test data generated (100K+ endpoints)")) { exit 1 }

# ===========================================================================
Write-Step "2 - Install ML Dependencies"

if (-not (Run-Native { python -m pip install -q -r ml-pipeline/requirements.txt } "ML dependencies installed")) { exit 1 }

# ===========================================================================
Write-Step "3 - Start MLflow"

# Kill ANY process holding port 5000 (MLflow runs as python.exe on Windows)
function Free-Port($port) {
  $foundPids = netstat -ano | Select-String ":$port\s" | ForEach-Object {
    $parts = $_ -split '\s+'
    $found = $parts[-1]
    if ($found -match '^\d+$') { $found }
  } | Select-Object -Unique
  foreach ($foundPid in $foundPids) {
    Stop-Process -Id $foundPid -Force -ErrorAction SilentlyContinue
    Write-Info "Killed PID $foundPid on port $port"
  }
}
Free-Port(5000)
Start-Sleep -Seconds 1

$mlflowProc = Start-Process -FilePath "mlflow" -ArgumentList "server --host 127.0.0.1 --port 5000 --workers 1" -PassThru -NoNewWindow
Start-Sleep -Seconds 3

# Health check: verify MLflow is actually responding
$healthy = $false
for ($i = 0; $i -lt 10; $i++) {
  try {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/3.0/mlflow/server-info" -ErrorAction Stop
    $healthy = $true
    break
  } catch { Start-Sleep -Seconds 2 }
}
if ($healthy -and -not $mlflowProc.HasExited) {
  Write-Ok "MLflow running (PID $($mlflowProc.Id))"
} else {
  Write-Fail "MLflow failed to start or respond"
  try { $mlflowProc.Kill() } catch { }
  exit 1
}

# ===========================================================================
Write-Step "4 - Train XGBoost Model"

$env:MLFLOW_TRACKING_URI = "http://localhost:5000"
$env:MLFLOW_EXPERIMENT_NAME = "zombie-classification"
$env:DATA_PATH = "demo/test-data/endpoint_features.parquet"

if (-not (Run-Native { python ml-pipeline/train.py } "XGBoost model trained")) { try { $mlflowProc.Kill() } catch { }; exit 1 }

# ===========================================================================
Write-Step "5 - Test Prediction"

$testJson = @"
[
  {"endpoint_key":"api.bank.example.com|GET|/api/v1/accounts/1234","total_calls":10000,"synthetic_calls":10000,"real_calls":0,"days_since_last_real_call":60,"unique_user_agents":1,"unique_source_ips":1,"auth_ratio":0.0,"ratio_2xx":1.0,"ratio_4xx":0.0,"ratio_5xx":0.0,"response_size_mean":256,"response_size_stddev":5,"interarrival_mean_ms":60000,"interarrival_stddev_ms":10,"unique_hours_of_day":1,"is_100pct_synthetic":true},
  {"endpoint_key":"api.bank.example.com|GET|/api/v3/accounts/5678/balance","total_calls":2500,"synthetic_calls":200,"real_calls":2300,"days_since_last_real_call":0,"unique_user_agents":12,"unique_source_ips":8,"auth_ratio":0.95,"ratio_2xx":0.92,"ratio_4xx":0.05,"ratio_5xx":0.03,"response_size_mean":1200,"response_size_stddev":150,"interarrival_mean_ms":5000,"interarrival_stddev_ms":2000,"unique_hours_of_day":14,"is_100pct_synthetic":false}
]
"@
$testJson | Out-File -FilePath "$env:TEMP\zombie_test_features.json" -Encoding utf8

$env:MODEL_URI = "models:/zombie-classifier/latest"
if (-not (Run-Native { python ml-pipeline/predict.py "$env:TEMP\zombie_test_features.json" } "Prediction ran successfully")) { Write-Fail "Prediction failed" }

# ===========================================================================
Write-Step "6 - Create kind Cluster"

$clusterExists = $false
kind get clusters 2>$null | ForEach-Object { if ($_ -eq "zombie-platform-demo") { $clusterExists = $true } }

if (-not $clusterExists) {
  if (-not (Run-Native { kind create cluster --config demo/kind-config.yaml } "kind cluster created")) { try { $mlflowProc.Kill() } catch { }; exit 1 }
} else {
  Write-Info "kind cluster already exists"
}

kubectl cluster-info --context kind-zombie-platform-demo 2>$null
if ($LASTEXITCODE -eq 0) { Write-Ok "Cluster reachable" }
else { Write-Fail "Cluster unreachable"; try { $mlflowProc.Kill() } catch { }; exit 1 }

# ===========================================================================
Write-Step "7 - Install MetalLB"

kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.5/config/manifests/metallb-native.yaml 2>&1 | Out-Null
kubectl wait --namespace metallb-system --for=condition=ready pod --selector=app=metallb --timeout=120s 2>$null

$subnetExtract = @'
import sys, json
data = json.load(sys.stdin)
subnet = data[0]["IPAM"]["Config"][0]["Subnet"]
parts = subnet.split(".")
print(f"{parts[0]}.{parts[1]}")
'@
$subnet = docker network inspect kind | python -c $subnetExtract 2>$null
if (-not $subnet) { $subnet = "172.18" }

$poolYaml = @"
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: demo-pool
  namespace: metallb-system
spec:
  addresses:
  - ${subnet}.255.200-${subnet}.255.250
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: demo-l2
  namespace: metallb-system
spec:
  ipAddressPools:
  - demo-pool
"@
$poolYaml | kubectl apply -f - 2>&1 | Out-Null
Write-Ok "MetalLB configured"

# ===========================================================================
Write-Step "8 - Deploy Platform Components"

Write-Info "Creating namespaces..."
kubectl create ns listen 2>$null; kubectl create ns remember 2>$null
kubectl create ns detect 2>$null; kubectl create ns enforce 2>$null
kubectl create ns act 2>$null

Write-Info "Phase 1 - RBAC + Network Policies..."
kubectl apply -f infra/k8s/rbac.yaml 2>$null
kubectl apply -f infra/k8s/network-policies.yaml 2>$null

Write-Info "Strimzi Kafka Operator..."
kubectl apply -f infra/k8s/kafka/strimzi-operator.yaml 2>&1 | Out-Null
Start-Sleep -Seconds 15

Write-Info "Kafka Cluster..."
kubectl apply -f infra/k8s/kafka/kafka-cluster.yaml 2>&1 | Out-Null
kubectl wait kafka/kafka-cluster -n listen --for=condition=Ready --timeout=300s 2>$null
if ($LASTEXITCODE -eq 0) { Write-Ok "Kafka cluster ready" }
else { Write-Fail "Kafka cluster not ready" }

Write-Info "Kafka ACLs + Topics..."
kubectl apply -f infra/k8s/kafka/kafka-acls.yaml 2>$null
kubectl apply -f infra/k8s/flink/kafka-topics.yaml 2>$null

Write-Info "Zeek DaemonSet..."
kubectl apply -f infra/k8s/zeek/ 2>$null

Write-Info "Flink Operator..."
kubectl apply -f infra/k8s/flink/flink-operator.yaml 2>&1 | Out-Null
Start-Sleep -Seconds 15

Write-Info "MinIO..."
kubectl apply -f infra/k8s/minio/minio-deployment.yaml 2>&1 | Out-Null
kubectl rollout status deployment/minio -n remember --timeout=120s 2>$null
kubectl apply -f infra/k8s/minio/minio-buckets.yaml 2>$null

Write-Info "Redis..."
kubectl apply -f infra/k8s/redis/redis-sentinel.yaml 2>&1 | Out-Null
kubectl rollout status statefulset/redis -n remember --timeout=180s 2>$null

Write-Info "Feast..."
kubectl apply -f infra/k8s/feast/feast-deployment.yaml 2>&1 | Out-Null
kubectl rollout status deployment/feast-serving -n remember --timeout=120s 2>$null

Write-Info "MLflow..."
kubectl apply -f infra/k8s/mlflow/mlflow-deployment.yaml 2>&1 | Out-Null
kubectl rollout status deployment/mlflow -n detect --timeout=120s 2>$null

Write-Info "OPA..."
kubectl apply -f infra/k8s/opa/opa-deployment.yaml 2>&1 | Out-Null
kubectl rollout status deployment/opa -n enforce --timeout=60s 2>$null

Write-Info "Backstage..."
kubectl apply -f infra/k8s/backstage/backstage-deployment.yaml 2>&1 | Out-Null
kubectl rollout status deployment/backstage -n enforce --timeout=120s 2>$null

Write-Info "Kyverno..."
kubectl apply -f infra/k8s/kyverno/ 2>&1 | Out-Null

Write-Info "Flagger..."
kubectl apply -f infra/k8s/flagger/flagger-install.yaml 2>&1 | Out-Null

Write-Ok "All 8 phases deployed"

# ===========================================================================
Write-Step "9 - Component Verification"

function Check-Cmd {
  param($c, $l)
  $null = Invoke-Expression $c 2>$null
  if ($LASTEXITCODE -eq 0) { Write-Ok $l } else { Write-Fail $l }
}

Check-Cmd 'kubectl cluster-info --context kind-zombie-platform-demo 2>$null' "K8s cluster reachable"

foreach ($ns in @("listen","remember","detect","enforce","act","kafka")) {
  Check-Cmd "kubectl get ns $ns 2>`$null" "Namespace: $ns"
}

Check-Cmd 'kubectl get kafka kafka-cluster -n listen 2>$null' "Kafka cluster exists"
Check-Cmd 'kubectl get kafkatopic raw-api-calls -n listen 2>$null' "Kafka topic: raw-api-calls"
Check-Cmd 'kubectl get daemonset zeek-sensor -n listen 2>$null' "Zeek DaemonSet exists"
Check-Cmd 'kubectl get flinkdeployment feature-computation-job -n listen 2>$null' "Flink deployment exists"
Check-Cmd 'kubectl get deployment minio -n remember 2>$null' "MinIO exists"
Check-Cmd 'kubectl get statefulset redis -n remember 2>$null' "Redis exists"
Check-Cmd 'kubectl get deployment feast-serving -n remember 2>$null' "Feast exists"
Check-Cmd 'kubectl get deployment mlflow -n detect 2>$null' "MLflow exists"
Check-Cmd 'kubectl get deployment opa -n enforce 2>$null' "OPA exists"
Check-Cmd 'kubectl get deployment backstage -n enforce 2>$null' "Backstage exists"
Check-Cmd 'kubectl get pods -n flagger 2>$null' "Flagger namespace exists"

# ===========================================================================
Write-Step "10 - OPA Policy Test"

$opaInput = '{"input":{"endpoint_key":"test","f1_score":0.92,"is_100pct_synthetic":true,"ensemble_disagreement":0.1,"timestamp":"2026-05-26T00:00:00Z"}}'
$opaResult = kubectl exec -n enforce deploy/opa -- wget -q -O- --post-data=$opaInput http://localhost:8181/v1/data/zombie/decommission 2>$null
if ($opaResult -match '"allow":true') { Write-Ok "OPA policy: zombie decommission allowed" }
else { Write-Fail "OPA policy check failed" }

# ===========================================================================
Write-Step "DONE"

Write-Host "==========================================" -ForegroundColor $CYAN
Write-Host " Results: $PASS passed, $FAIL failed" -ForegroundColor $CYAN
Write-Host "==========================================" -ForegroundColor $CYAN

Write-Host "`nMLflow PID: $($mlflowProc.Id) - run 'Stop-Process -Id $($mlflowProc.Id)' to kill" -ForegroundColor $YELLOW
Write-Host "Port-forward commands:" -ForegroundColor $YELLOW
Write-Host "  kubectl port-forward -n detect svc/mlflow 5000:5000"
Write-Host "  kubectl port-forward -n enforce svc/opa 8181:8181"
Write-Host "  kubectl port-forward -n enforce svc/backstage 7007:7007"

if ($FAIL -gt 0) { exit 1 }
