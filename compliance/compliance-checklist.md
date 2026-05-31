# Compliance Verification Checklist

## Metadata-Only Capture

- [ ] Zeek configured to NOT capture request/response body
- [ ] Zeek HTTP log script extracts only: method, path, status, user-agent, host, referrer, response_size
- [ ] No PII fields in Kafka topic schema
- [ ] Frontend analyzer extracts path patterns only (no credentials)

## Retention Policies

- [ ] Kafka `raw-api-calls` retention: 720 hours (30 days) ✓ (kafka-cluster.yaml)
- [ ] Kafka `enriched-features` retention: 7776000000 ms (90 days) ✓ (kafka-topics.yaml)
- [ ] MinIO lifecycle policies: 30d logs, 90d features
- [ ] Audit records: permanent (Git history)

## Encryption

- [ ] MinIO: AES-256 at rest (default for MinIO with erasure coding)
- [ ] Kafka: TLS listeners configured (port 9093)
- [ ] Kafka: Encryption at rest via persistent volume encryption
- [ ] Redis: AOF persistence with encryption
- [ ] Feast/MLflow: traffic encryption via K8s service mesh

## Access Control

- [ ] Kafka ACLs: zeek-producer (Write), flink-consumer (Read) ✓ (kafka-acls.yaml)
- [ ] K8s RBAC: ServiceAccounts with least-privilege roles ✓ (rbac.yaml)
- [ ] Network policies: deny-all default, allow specific ingress/egress ✓ (network-policies.yaml)

## PCI-DSS Req 3

- [ ] Zeek sensor: no card data capture (metadata-only architecture)
- [ ] No payload inspection at any pipeline stage
- [ ] Card data redaction verified at sensor level

## Audit Trail

- [ ] Git-immutable decommission records (`.planning/audit/`)
- [ ] PR-based approval with approver identities
- [ ] Timestamps for every decommission action
- [ ] Rollback events logged
- [ ] Workflow run URL preserved in audit record

---
*Version: 1.0*
*Last verified: 2026-05-26*
