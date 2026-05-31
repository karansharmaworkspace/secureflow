#!/bin/bash
set -euo pipefail

echo "=========================================="
echo " Zombie Platform — Full Demo Deploy"
echo "=========================================="

echo ""
echo "=== Phase 1: Infrastructure ==="
kubectl create ns listen remember detect enforce act 2>/dev/null || true
kubectl apply -f infra/k8s/rbac.yaml

echo "--- Strimzi Kafka Operator ---"
kubectl apply -f infra/k8s/kafka/strimzi-operator.yaml
sleep 10
kubectl wait --for=condition=Ready pods -l name=strimzi-operator -n kafka --timeout=120s 2>/dev/null || true

echo "--- Kafka Cluster ---"
kubectl apply -f infra/k8s/kafka/kafka-cluster.yaml
kubectl wait kafka/kafka-cluster -n listen --for=condition=Ready --timeout=300s

echo "--- Kafka Topics ---"
kubectl apply -f infra/k8s/kafka/kafka-acls.yaml
kubectl apply -f infra/k8s/flink/kafka-topics.yaml

echo "--- Network Policies ---"
kubectl apply -f infra/k8s/network-policies.yaml

echo ""
echo "=== Phase 2: Streaming Pipeline ==="
echo "--- Flink Operator ---"
kubectl apply -f infra/k8s/flink/flink-operator.yaml
sleep 10
kubectl wait --for=condition=Ready pods -l app.kubernetes.io/name=flink-kubernetes-operator -n flink --timeout=120s 2>/dev/null || true

echo "--- MinIO ---"
kubectl apply -f infra/k8s/minio/minio-deployment.yaml
kubectl rollout status deployment/minio -n remember --timeout=120s
kubectl apply -f infra/k8s/minio/minio-buckets.yaml
kubectl wait --for=condition=Complete job/minio-create-buckets -n remember --timeout=60s

echo "--- Redis ---"
kubectl apply -f infra/k8s/redis/redis-sentinel.yaml
kubectl rollout status statefulset/redis -n remember --timeout=180s

echo "--- Feast ---"
kubectl apply -f infra/k8s/feast/feast-deployment.yaml
kubectl rollout status deployment/feast-serving -n remember --timeout=120s

echo ""
echo "=== Phase 4: ML Pipeline ==="
kubectl create ns detect 2>/dev/null || true
kubectl apply -f infra/k8s/mlflow/mlflow-deployment.yaml
kubectl rollout status deployment/mlflow -n detect --timeout=120s

echo ""
echo "=== Phase 5: Policy & Catalog ==="
kubectl create ns enforce 2>/dev/null || true
kubectl apply -f infra/k8s/opa/opa-deployment.yaml
kubectl rollout status deployment/opa -n enforce --timeout=60s
kubectl apply -f infra/k8s/backstage/backstage-deployment.yaml
kubectl rollout status deployment/backstage -n enforce --timeout=120s

echo ""
echo "=== Phase 6: Flagger ==="
kubectl apply -f infra/k8s/flagger/flagger-install.yaml
sleep 10

echo ""
echo "=== Starting Traffic Generator ==="
kubectl run traffic-generator -n listen --image=python:3.11-slim --restart=Never -- \
  sh -c "pip install -q pandas pyarrow numpy && python -c \"$(cat demo/traffic-generator/simulate.py)\""

echo ""
echo "=========================================="
echo " Deploy complete! Run verify.sh to check."
echo "=========================================="
