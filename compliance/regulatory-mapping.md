# Regulatory Compliance Mapping

## OWASP API Top 10

| OWASP ID | Name | Platform Coverage |
|----------|------|-------------------|
| API2:2023 | Broken Authentication | Auth token detection (feature signal), Backstage ownership tracking |
| API7:2023 | Server Side Request Forgery | N/A (platform discovers, doesn't create APIs) |
| API9:2023 | Improper Inventory Management | **Primary focus** — Backstage catalog, continuous discovery, zombie detection |

## NIST Cybersecurity Framework 2.0

| Function | Category | Platform Component |
|----------|----------|-------------------|
| **Identify** | Asset Management | Backstage API catalog, continuous endpoint discovery |
| **Protect** | Access Control | Kyverno admission policies, OPA decommission policies |
| **Detect** | Anomalies & Events | Zeek network capture, Flink feature computation, XGBoost classification |
| **Respond** | Mitigation | GitHub Actions decommission workflow, auto-rollback |
| **Recover** | Recovery | Flagger canary rollback, 10-day slow drain with reversal capability |

## RBI IT Framework for Banks

| Requirement | Implementation |
|-------------|----------------|
| Asset Inventory | Backstage catalog with all discovered API endpoints |
| Vulnerability SLAs | DefectDojo integration (planned), classification priority based on F1 score |
| Change Management | OPA audit trail, Git-immutable decommission records |
| Access Control | Kafka ACLs, K8s RBAC, network policies per namespace |
| Log Retention | 30-day raw logs (Kafka), 90-day features (Feast/MinIO), permanent audit (Git) |
| Board Reporting | Governance charter, quarterly decommission summary reports |

## PCI-DSS v4.0

| Requirement | Coverage |
|-------------|----------|
| Req 3: Protect Stored Cardholder Data | Zeek configured for metadata-only capture — card data never enters pipeline |
| Req 7: Restrict Access | Kafka ACLs, K8s RBAC, network policies |
| Req 10: Track & Monitor | Complete audit trail per decommission action |
| Req 12: Policy | Governance charter signed by CIO + CISO + Legal |

## GDPR Article 25 (Data Protection by Design)

| Principle | Implementation |
|-----------|----------------|
| Data minimization | Metadata-only capture, no payload content |
| Purpose limitation | Logs used exclusively for API discovery/decommission |
| Storage limitation | 30-day raw logs, 90-day feature vectors |
| Integrity & confidentiality | AES-256 at rest, TLS in transit (Kafka) |

## ISO 27001 A8.8 (Management of Technical Vulnerabilities)

Full lifecycle coverage:
1. Discover (Zeek/WAF/Gateway/Frontend/Scanner)
2. Classify (XGBoost + SHAP)
3. Evaluate (OPA Policy)
4. Notify (GitHub Issue)
5. Approve (Two human approvals)
6. Decommission (Flagger canary + slow drain)
7. Verify (Auto-rollback on anomaly)
8. Archive (Backstage + Git audit trail)

---
*Document version: 1.0*
*Created: 2026-05-26*
