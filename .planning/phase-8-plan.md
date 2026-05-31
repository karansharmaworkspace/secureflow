# Phase 8 Plan: Compliance & Governance

**Goal:** Governance charter, regulatory compliance documentation, audit trail hardening.

## Tasks

### 8.1 Governance Charter
- Draft charter defining roles (CIO, CISO, Legal), decision authority, decommission policy
- Include: acceptance criteria for zombie classification, approval chain, exemption process
- Template for signature by CIO + CISO + Legal

### 8.2 Compliance Verification
- Verify metadata-only capture: no PII, no payload content in pipeline
- Verify retention policies: 30-day raw logs (Kafka), 90-day feature vectors (Feast)
- Verify Zeek-level card data redaction (PCI-DSS v4 Req 3)
- Verify AES-256 encryption at rest (MinIO, Kafka, Redis)
- Verify Kafka ACLs enforced

### 8.3 Regulatory Mapping
- OWASP API Top 10: API2 (Broken Auth), API7 (Misconfiguration), API9 (Improper Inventory Management)
- NIST CSF 2.0: Identify → Backstage catalog, Protect → Kyverno/OPA, Detect → ML classification, Respond → GitHub Actions workflow, Recover → Flagger rollback
- RBI IT Framework: Asset inventory, vulnerability SLAs, change management audit trail
- ISO 27001 A8.8: Full lifecycle from detection to removal

### 8.4 Audit Trail Documentation
- Standardize audit format: PR URL, approver identities, timestamps, endpoint metadata
- Archive all decommission records in `.planning/audit/`
- Generate compliance summary report

## Success Criteria
1. Governance charter drafted, ready for CIO + CISO + Legal signature
2. All compliance checks verified (no PII, retention, encryption, ACLs)
3. Regulatory mapping documented for OWASP/NIST/RBI/ISO
4. Audit trail format standardized and populated
5. Phase 8 exit: F1 >= 0.85 AND charter signed

---
*Created: 2026-05-26*
