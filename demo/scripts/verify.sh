#!/bin/bash
set -euo pipefail

PASS=0
FAIL=0

green() { echo -e "\033[32m✓ PASS\033[0m $1"; ((PASS++)); }
red()   { echo -e "\033[31m✗ FAIL\033[0m $1"; ((FAIL++)); }

echo "=== Zombie Platform — Component Verification ==="
echo ""

echo "--- Cluster ---"
kubectl cluster-info --context kind-zombie-platform-demo &>/dev/null && green "K8s cluster reachable" || red "K8s cluster unreachable"

echo ""
echo "--- Namespaces ---"
for ns in listen remember detect enforce act kafka flink flagger kyverno; do
  kubectl get ns "$ns" &>/dev/null && green "Namespace: $ns" || red "Namespace: $ns"
done

echo ""
echo "--- Kafka ---"
kubectl get kafka kafka-cluster -n listen -o jsonpath='{.status.conditions[0].status}' 2>/dev/null | grep -q True && green "Kafka cluster ready" || red "Kafka cluster not ready"
kubectl get kafkatopic raw-api-calls -n listen &>/dev/null && green "Kafka topic: raw-api-calls" || red "Kafka topic: raw-api-calls"

echo ""
echo "--- Zeek ---"
kubectl get daemonset zeek-sensor -n listen &>/dev/null && green "Zeek DaemonSet exists" || red "Zeek DaemonSet missing"

echo ""
echo "--- Flink ---"
kubectl get flinkdeployment feature-computation-job -n listen &>/dev/null && green "Flink deployment exists" || red "Flink deployment missing"

echo ""
echo "--- MinIO ---"
kubectl get deployment minio -n remember &>/dev/null && green "MinIO deployment exists" || red "MinIO deployment missing"

echo ""
echo "--- Redis ---"
kubectl get statefulset redis -n remember &>/dev/null && green "Redis StatefulSet exists" || red "Redis StatefulSet missing"

echo ""
echo "--- Feast ---"
kubectl get deployment feast-serving -n remember &>/dev/null && green "Feast Serving exists" || red "Feast Serving missing"

echo ""
echo "--- MLflow ---"
kubectl get deployment mlflow -n detect &>/dev/null && green "MLflow exists" || red "MLflow missing"

echo ""
echo "--- OPA ---"
kubectl get deployment opa -n enforce &>/dev/null && green "OPA exists" || red "OPA missing"
OPA_POD=$(kubectl get pods -n enforce -l app=opa -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
[ "$OPA_POD" = "Running" ] && green "OPA pod running" || red "OPA pod not running"

echo ""
echo "--- Backstage ---"
kubectl get deployment backstage -n enforce &>/dev/null && green "Backstage exists" || red "Backstage missing"

echo ""
echo "--- Flagger ---"
kubectl get pods -n flagger &>/dev/null && green "Flagger namespace exists" || red "Flagger namespace missing"

echo ""
echo "--- Traffic Generator ---"
kubectl get pod traffic-generator -n listen -o jsonpath='{.status.phase}' 2>/dev/null | grep -q Running && green "Traffic generator running" || {
  PHASE=$(kubectl get pod traffic-generator -n listen -o jsonpath='{.status.phase}' 2>/dev/null || echo "absent")
  red "Traffic generator not running (phase: $PHASE)"
}

echo ""
echo "--- OPA Policy Test ---"
OPA_RESULT=$(kubectl exec -n enforce deploy/opa -- wget -q -O- --post-data='{"input":{"endpoint_key":"test","f1_score":0.92,"is_100pct_synthetic":true,"ensemble_disagreement":0.1,"timestamp":"2026-05-26T00:00:00Z"}}' http://localhost:8181/v1/data/zombie/decommission 2>/dev/null || echo "failed")
echo "$OPA_RESULT" | grep -q '"allow":true' && green "OPA policy: zombie decommission allowed" || red "OPA policy: zombie decommission check failed"

echo ""
echo "=========================================="
echo " Results: $PASS passed, $FAIL failed"
echo "=========================================="

exit $FAIL
