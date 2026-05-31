# Infrastructure

Kubernetes manifests and configurations for the full SecureFlow platform.

## Subdirectories

### k8s/
All Kubernetes YAML manifests organized by component and namespace.

| Directory | Component | Namespace |
|-----------|-----------|-----------|
| `kafka/` | Strimzi operator, Kafka cluster (3 brokers), ACLs, topics | listen |
| `flink/` | Flink operator, feature computation job, Kafka topics | listen |
| `minio/` | MinIO deployment (S3-compatible), bucket creation | remember |
| `redis/` | Redis Sentinel (3-node HA) | remember |
| `feast/` | Feast feature store serving | remember |
| `mlflow/` | MLflow tracking server | detect |
| `opa/` | Open Policy Agent (Rego policies) | enforce |
| `backstage/` | Backstage developer portal | enforce |
| `kyverno/` | Kyverno admission controller + policies | enforce |
| `flagger/` | Flagger canary controller | flagger |

| File | Purpose |
|------|---------|
| `namespaces.yaml` | Creates all 5 namespaces: listen, remember, detect, enforce, act |
| `rbac.yaml` | Role-based access control for inter-service communication |
| `network-policies.yaml` | Network segmentation between namespaces |
| `Makefile` | Deployment automation commands |

### zeek/
Passive network sensor configuration.

| File | Purpose |
|------|---------|
| `zeek-daemonset.yaml` | Kubernetes DaemonSet for running Zeek on every node |
| `Dockerfile` | Custom Zeek image with HTTP log scripts |
| `config/local.zeek` | Local Zeek configuration |
| `config/zeek-http-log.zeek` | HTTP metadata extraction script |
| `scripts/stream-to-kafka.py` | Bridge from Zeek log output to Kafka producer |

## Deployment

```bash
cd infra/k8s
make all
```
