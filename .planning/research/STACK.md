# Stack Research: Zombie API Discovery Platform

## Technology Choices

| Category | Tool | Version | Rationale |
|----------|------|---------|-----------|
| Network Capture | Zeek | 6.x | Industry-standard NSM, BSD license, extensive HTTP log scripting |
| Event Streaming | Apache Kafka | 3.7+ | De facto standard for log streaming, exactly-once semantics via Flink |
| Stream Processing | Apache Flink | 1.19+ | Stateful exactly-once processing, ideal for feature computation |
| Feature Store | Feast | 0.39+ | Open-source feature store, integrates with XGBoost and Redis |
| Cache | Redis | 7.x | Sub-millisecond lookups, Sentinel for HA auto-failover |
| Object Storage | MinIO | latest | S3-compatible, AGPL v3, no license cost |
| ML Classifier | XGBoost | 2.x | Gradient boosting, interpretable, SHAP-compatible |
| Explainability | SHAP | 0.45+ | Game-theoretic feature attribution, produces plain-English explanations |
| Model Tracking | MLflow | 2.13+ | Open-source ML lifecycle, model registry, experiment tracking |
| Policy Engine | OPA | 0.66+ | Cloud-native policy engine, Rego language, Git-backed policies |
| K8s Admission | Kyverno | 1.12+ | Kubernetes-native policy, rejects non-compliant API deployments |
| API Catalog | Backstage | 1.28+ | Spotify's developer portal, entity catalog with ownership |
| Canary Deploy | Flagger | 1.36+ | Progressive delivery on K8s, traffic shadowing, metric-based rollback |
| CI/CD | GitHub Actions | N/A | Native GitHub integration, no additional infrastructure |

## Anti-Re commendations

- **Deep learning (NN/Transformers)**: Excessive data requirements, black-box predictions — avoid for compliance-sensitive banking context
- **Elasticsearch**: License changes (SSPL) create compliance risk — use MinIO + Flink instead
- **Prometheus/Alertmanager**: Good for monitoring but not designed for audit-trail decommission workflows
- **Custom policy engine**: OPA is battle-tested, do not build custom
