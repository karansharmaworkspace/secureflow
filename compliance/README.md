# Compliance Documentation

Regulatory compliance, governance framework, and standards mapping documentation for the SecureFlow platform. These documents ensure the zombie API decommission process meets banking, security, and data protection regulations (RBI, OWASP, NIST, GDPR, PCI-DSS, ISO 27001).

## Files

### compliance-checklist.md — Verification Checklist

Operational checklist for verifying the platform meets all compliance requirements. Organized into 7 sections with individual checkable items:

**Metadata-Only Capture (6 checks):** Zeek must NOT capture request/response body content. HTTP logs extract only: method, path, status, user-agent, host, referrer, response_size. No PII fields in Kafka topic schemas. Frontend analyzer extracts path patterns only (no credentials or tokens).

**Retention Policies (4 checks):** Kafka `raw-api-calls` topic retention: 720 hours (30 days) configured in `kafka-cluster.yaml`. Kafka `enriched-features` retention: 7,776,000,000 ms (90 days) configured in `kafka-topics.yaml`. MinIO lifecycle policies: 30 days for logs, 90 days for feature vectors. Audit records stored permanently in Git history.

**Encryption (5 checks):** MinIO AES-256 at rest via erasure coding. Kafka TLS listeners on port 9093 for in-transit encryption. Kafka persistent volume encryption for at-rest data. Redis AOF persistence with encryption. Feast/MLflow traffic encryption via K8s service mesh.

**Access Control (3 checks):** Kafka ACLs: `zeek-producer` (Write), `flink-consumer` (Read) configured in `kafka-acls.yaml`. K8s RBAC: ServiceAccounts with least-privilege roles in `rbac.yaml`. Network policies: deny-all default, allow specific ingress/egress in `network-policies.yaml`.

**PCI-DSS Req 3 (3 checks):** No card data capture (metadata-only architecture). No payload inspection at any pipeline stage. Card data redaction verified at sensor level.

**Audit Trail (5 checks):** Git-immutable decommission records in `.planning/audit/`. PR-based approval with approver identities. Timestamps for every decommission action. Rollback events logged. Workflow run URL preserved in audit record.

### governance-charter.md — Governance Framework

Defines the governance structure for automated API decommission including:

**Roles & Responsibilities:** CIO (final approval authority), CISO (security oversight), Legal (compliance verification), Platform Engineering (technical execution, no decommission authority), API Owner (respond to notifications, provide evidence).

**Classification Thresholds (OPA Policy Rules):**
- F1 >= 0.85, 100% synthetic, ensemble disagreement < 0.3 → Auto-qualify for decommission
- F1 >= 0.85, ensemble disagreement >= 0.3 → Mandatory human review
- F1 < 0.85 → No action, continue monitoring

**Approval Chain:** ML model flags zombie candidate → Stage 2 GitHub issue opened (30-day response) → Owner confirms OR deadline lapses → Stage 3 requires 2 INDEPENDENT human approvals → 24h Flagger canary → 10-day slow drain → full decommission.

**Exemption Process:** Valid for 90 days, requires CISO re-approval upon expiry. API owners must document business justification.

### regulatory-mapping.md — Standards Mapping

Maps the SecureFlow platform's capabilities to six regulatory frameworks:

**OWASP API Top 10:** API2 (Broken Authentication) via auth token detection signal and Backstage ownership tracking. API9 (Improper Inventory Management) as primary focus via Backstage catalog, continuous discovery, and zombie detection.

**NIST CSF 2.0 (All 5 Functions):** Identify (Backstage catalog, continuous discovery), Protect (Kyverno admission policies, OPA decommission policies), Detect (Zeek capture, Flink feature computation, XGBoost classification), Respond (GitHub Actions decommission workflow, auto-rollback), Recover (Flagger canary rollback, 10-day slow drain with reversal capability).

**RBI IT Framework:** Asset Inventory via Backstage catalog, Vulnerability SLAs (planned DefectDojo integration), Change Management via OPA audit trail, Access Control via ACLs + RBAC, Log Retention (30d raw / 90d features / permanent audit), Board Reporting via quarterly decommission summary reports.

**PCI-DSS v4.0:** Req 3 (metadata-only capture, card data never enters pipeline), Req 7 (access restriction via ACLs+RBAC+network policies), Req 10 (complete audit trail per decommission action), Req 12 (governance charter signed by CIO + CISO + Legal).

**GDPR Article 25:** Data minimization (metadata-only, no payload content), Purpose limitation (logs used exclusively for API discovery/decommission), Storage limitation (30d raw logs, 90d feature vectors), Integrity/confidentiality (AES-256 at rest, TLS in transit).

**ISO 27001 A8.8:** Full 8-step lifecycle coverage: Discover (Zeek/WAF/Gateway/Frontend/Scanner) → Classify (XGBoost + SHAP) → Evaluate (OPA Policy) → Notify (GitHub Issue) → Approve (Two human approvals) → Decommission (Flagger canary + slow drain) → Verify (Auto-rollback on anomaly) → Archive (Backstage + Git audit trail).
