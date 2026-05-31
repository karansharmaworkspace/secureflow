# Zombie Platform — Demo Guide

## Prerequisites

- Docker Desktop
- kind (Kubernetes in Docker)
- kubectl
- Python 3.11+
- Java 11+ (for Flink job build)

## Quick Start

```bash
# 1. Create kind cluster
bash demo/scripts/setup-kind.sh

# 2. Deploy all platform components
bash demo/scripts/deploy-all.sh

# 3. Verify everything is running
bash demo/scripts/verify.sh

# 4. Run ML demo (generates test data, trains XGBoost, shows predictions)
bash demo/scripts/run-ml-demo.sh
```

## Demo Script (5 min)

| Time | Step | What to Show |
|------|------|-------------|
| 0:00 | **Architecture walkthrough** | Open `Plan.md` — 5-layer diagram |
| 0:30 | **Traffic capture** | `kubectl logs -n listen traffic-generator` — show real vs zombie traffic |
| 1:00 | **Kafka streaming** | `kubectl exec -n listen kafka-cluster-kafka-0 -- bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic raw-api-calls --max-messages 3` |
| 1:30 | **ML classification** | Run `run-ml-demo.sh` steps 4-5 — show training metrics, SHAP explanation |
| 2:30 | **OPA policy** | OPA test from verify.sh — show policy decision |
| 3:00 | **Stage 2 workflow** | Trigger `stage2-tell-owner.yml` — show GitHub issue with SHAP explanation |
| 3:30 | **Backstage catalog** | Port-forward 7007 → localhost:7007 — show API catalog |
| 4:00 | **Governance charter** | Open `compliance/governance-charter.md` — show sign-off page |
| 4:30 | **Q&A** | |

## Traffic Generator

Generates 2 types of traffic:
- **Active endpoints**: `/api/v3/accounts/{id}/balance` — diverse UAs, IPs, status codes
- **Zombie endpoints**: `/api/v1/accounts/{id}/balance` — Prometheus/kube-probe UAs, single IP, identical payloads, perfect intervals

## Component URLs (port-forward)

| Component | Port | Command |
|-----------|------|---------|
| MLflow | 5000 | `kubectl port-forward -n detect svc/mlflow 5000:5000` |
| OPA | 8181 | `kubectl port-forward -n enforce svc/opa 8181:8181` |
| Backstage | 7007 | `kubectl port-forward -n enforce svc/backstage 7007:7007` |
| Kafka | 9092 | `kubectl port-forward -n listen svc/kafka-cluster-kafka-bootstrap 9092:9092` |
| MinIO Console | 9001 | `kubectl port-forward -n remember svc/minio 9001:9001` |

## Test Data

Pre-generated: `demo/test-data/endpoint_features.parquet` (200 endpoints, 50% zombie)
