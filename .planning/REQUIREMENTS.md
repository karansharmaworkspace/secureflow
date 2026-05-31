# Requirements: Zombie API Discovery & Decommission Platform

**Defined:** 2026-05-26
**Core Value:** Safely identify and remove zombie API endpoints — converting 15+ engineer-days into 30 minutes of human attention — with zero production impact through progressive canary decommissioning.

## v1 Requirements

### LISTEN Layer — Traffic Capture & Streaming

- [ ] **LSTN-01**: Deploy Zeek as passive network sensor on SPAN/TAP port mirroring internal traffic
- [ ] **LSTN-02**: Configure Zeek to extract HTTP metadata (path, method, status code, user-agent, frequency) without payload content
- [ ] **LSTN-03**: Stream Zeek logs into Apache Kafka topics in real time
- [ ] **LSTN-04**: Deploy Apache Flink to consume Kafka streams with exactly-once semantics
- [ ] **LSTN-05**: Compute 20+ features per endpoint in Flink (frequency, auth, response codes, user-agent diversity, entropy, etc.)

### REMEMBER Layer — Storage & Feature Serving

- [ ] **MEM-01**: Set up Feast ML feature store with feature definitions for all 20+ signals
- [ ] **MEM-02**: Deploy Redis HA cluster (Sentinel 3-node auto-failover) for sub-millisecond feature lookups
- [ ] **MEM-03**: Set up MinIO S3-compatible storage for historical logs, model artifacts, feature snapshots

### DETECT Layer — ML Classification

- [ ] **DET-01**: Train XGBoost classifier to produce zombie probability per endpoint
- [ ] **DET-02**: Integrate SHAP for plain-English explanations per classification decision
- [ ] **DET-03**: Implement synthetic traffic detection (7 signals: interval regularity, user-agent, payload entropy, source IP, response code, time clustering, call frequency)
- [ ] **DET-04**: Track model versions, parameters, and performance with MLflow
- [ ] **DET-05**: Achieve F1 >= 0.85 before any automated actions
- [ ] **DET-06**: Ensemble safety — auto human review when two models disagree by >0.3

### ENFORCE Layer — Policy & Catalog

- [ ] **ENF-01**: Deploy OPA with Rego policies for decommission decision evaluation
- [ ] **ENF-02**: Store decommission policies in Git with version history
- [ ] **ENF-03**: Configure Kyverno admission controller to reject new APIs missing x-api-sunset-date and x-api-owner-team labels
- [ ] **ENF-04**: Run Kyverno in audit-only mode first, then switch to enforcement
- [ ] **ENF-05**: Set up Backstage developer portal as canonical API catalog with ownership information

### ACT Layer — Decommission Workflow

- [ ] **ACT-01**: Implement Stage 1 (Watch Only): full pipeline deployed, no automated actions, F1 calibration, governance charter signed
- [ ] **ACT-02**: Implement Stage 2 (Tell the Owner): auto-open GitHub issues for zombie candidates with SHAP explanation, confidence score, owner team, 30-day response window
- [ ] **ACT-03**: Implement Stage 3 (Turn It Off): 24-hour canary shadow at 1% traffic via Flagger
- [ ] **ACT-04**: Two independent human approvals required before final decommission
- [ ] **ACT-05**: 10-day slow traffic drain with automatic rollback on anomaly
- [ ] **ACT-06**: Complete audit trail written to Git (PR history, approver identities, timestamps)

### Discovery Methods

- [ ] **DSC-01**: Passive network capture via SPAN/TAP port (primary method)
- [ ] **DSC-02**: WAF log integration with 5-minute polling interval
- [ ] **DSC-03**: API gateway log streaming via Kafka source connector
- [ ] **DSC-04**: Frontend static analysis — parse JS bundles and mobile app binaries for API URL patterns
- [ ] **DSC-05**: Controlled internal scanning in staging only (Kiterunner, 10 req/s max)

### Compliance & Governance

- [ ] **CMP-01**: Governance charter drafted and signed by CIO + CISO + Legal
- [ ] **CMP-02**: Metadata-only capture compliance (no PII)
- [ ] **CMP-03**: Raw logs 30-day retention, feature vectors 90-day retention
- [ ] **CMP-04**: Zeek-level redaction of card data (PCI-DSS v4 Req 3)
- [ ] **CMP-05**: AES-256 encryption at rest for all stored data
- [ ] **CMP-06**: Kafka ACLs for access control
- [ ] **CMP-07**: OWASP API Top 10 coverage (API2, API7, API9)
- [ ] **CMP-08**: NIST CSF 2.0 coverage (Identify, Protect, Detect, Respond, Recover)
- [ ] **CMP-09**: RBI IT Framework compliance

## v2 Requirements

- **TLS/mTLS traffic handling**: Currently accepted risk in governance charter; future integration with service mesh telemetry
- **External partner API discovery**: Requires deeper WAF/API gateway integration
- **Legacy non-HTTP protocol support**: SOAP/gRPC capture via conn.log fallback

## Out of Scope

| Feature | Reason |
|---------|--------|
| Payload content inspection | Legally prohibited in banking context; not needed for classification |
| External OSINT scanning | Blocked by Union Bank WAF; unreliable for production use |
| Fully automatic decommission | Unacceptable risk for PSB production; human approval always required |
| Real-time enforcement on cron/batch APIs | Requires 90-day minimum observation window; addressed in v2 |
| Custom authentication/authorization | Leverage bank's existing IAM via Backstage integrations |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| LSTN-01 | Phase 1 | Pending |
| LSTN-02 | Phase 1 | Pending |
| LSTN-03 | Phase 2 | Pending |
| LSTN-04 | Phase 2 | Pending |
| LSTN-05 | Phase 2 | Pending |
| MEM-01 | Phase 3 | Pending |
| MEM-02 | Phase 3 | Pending |
| MEM-03 | Phase 3 | Pending |
| DET-01 | Phase 4 | Pending |
| DET-02 | Phase 4 | Pending |
| DET-03 | Phase 2 | Pending |
| DET-04 | Phase 4 | Pending |
| DET-05 | Phase 4 | Pending |
| DET-06 | Phase 4 | Pending |
| ENF-01 | Phase 5 | Pending |
| ENF-02 | Phase 5 | Pending |
| ENF-03 | Phase 5 | Pending |
| ENF-04 | Phase 5 | Pending |
| ENF-05 | Phase 5 | Pending |
| ACT-01 | Phase 6 | Pending |
| ACT-02 | Phase 6 | Pending |
| ACT-03 | Phase 6 | Pending |
| ACT-04 | Phase 6 | Pending |
| ACT-05 | Phase 6 | Pending |
| ACT-06 | Phase 6 | Pending |
| DSC-01 | Phase 1 | Pending |
| DSC-02 | Phase 7 | Pending |
| DSC-03 | Phase 7 | Pending |
| DSC-04 | Phase 7 | Pending |
| DSC-05 | Phase 7 | Pending |
| CMP-01 | Phase 8 | Pending |
| CMP-02 | Phase 8 | Pending |
| CMP-03 | Phase 8 | Pending |
| CMP-04 | Phase 8 | Pending |
| CMP-05 | Phase 8 | Pending |
| CMP-06 | Phase 8 | Pending |
| CMP-07 | Phase 8 | Pending |
| CMP-08 | Phase 8 | Pending |
| CMP-09 | Phase 8 | Pending |

**Coverage:**
- v1 requirements: 39 total
- Mapped to phases: 39
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-26*
*Last updated: 2026-05-26 after initial definition*
