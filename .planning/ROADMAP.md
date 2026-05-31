# Roadmap: Zombie API Discovery & Decommission Platform

## Summary

**8 phases** | **39 requirements mapped** | All v1 requirements covered ✓

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Infrastructure & Network Capture | Deploy base K8s cluster, Zeek sensor, and Kafka | LSTN-01, LSTN-02, DSC-01 | 4 |
| 2 | Streaming Pipeline & Feature Computation | Deploy Flink, compute 20+ features, synthetic detection | LSTN-03, LSTN-04, LSTN-05, DET-03 | 4 |
| 3 | Feature Store & Cache Layer | Deploy Feast, Redis HA, MinIO storage | MEM-01, MEM-02, MEM-03 | 4 |
| 4 | ML Classification Engine | Train XGBoost, integrate SHAP, MLflow, calibrate F1 | DET-01, DET-02, DET-04, DET-05, DET-06 | 5 |
| 5 | Policy Engine & API Catalog | OPA policies, Kyverno admission, Backstage catalog | ENF-01, ENF-02, ENF-03, ENF-04, ENF-05 | 5 |
| 6 | Decommission Workflow | 3-stage pipeline, Flagger canary, audit trail | ACT-01, ACT-02, ACT-03, ACT-04, ACT-05, ACT-06 | 6 |
| 7 | Secondary Discovery Methods | WAF logs, API gateway, frontend analysis, staging scanning | DSC-02, DSC-03, DSC-04, DSC-05 | 4 |
| 8 | Compliance & Governance | Charter, compliance, regulatory documentation | CMP-01 through CMP-09 | 7 |

---

## Phase Details

### Phase 1: Infrastructure & Network Capture
**Goal:** Deploy base K8s cluster, Zeek passive sensor on SPAN/TAP port, and initial Kafka cluster
**Mode:** mvp
**Requirements:** LSTN-01, LSTN-02, DSC-01
**Success Criteria:**
1. K8s cluster operational with node auto-scaling
2. Zeek sensor deployed on SPAN/TAP port capturing HTTP metadata
3. Zeek logs flowing to Kafka topic `raw-api-calls`
4. Zeek configured to NOT capture payload content (metadata-only)

### Phase 2: Streaming Pipeline & Feature Computation
**Goal:** Deploy Apache Flink with exactly-once semantics, compute 20+ features per endpoint including synthetic traffic detection
**Mode:** mvp
**Requirements:** LSTN-03, LSTN-04, LSTN-05, DET-03
**Success Criteria:**
1. Flink cluster deployed and consuming from Kafka
2. All 20+ features computed per endpoint in real-time
3. Synthetic traffic detector operational (7 signals: interval regularity, user-agent, payload entropy, source IP, response code, time clustering, call frequency)
4. Feature computation latency < 100ms per event

### Phase 3: Feature Store & Cache Layer
**Goal:** Deploy Feast feature store, Redis HA cluster with Sentinel, and MinIO object storage
**Mode:** mvp
**Requirements:** MEM-01, MEM-02, MEM-03
**Success Criteria:**
1. Feast feature definitions created for all signals
2. Feast serving endpoint returning features in < 10ms
3. Redis Sentinel 3-node cluster operational with auto-failover
4. MinIO buckets created for historical logs, model artifacts, and feature snapshots

### Phase 4: ML Classification Engine
**Goal:** Train XGBoost classifier, integrate SHAP explanations, track via MLflow, calibrate to F1 >= 0.85
**Mode:** mvp
**Requirements:** DET-01, DET-02, DET-04, DET-05, DET-06
**Success Criteria:**
1. XGBoost model trained on production traffic data (2+ weeks)
2. Model achieves F1 >= 0.85 on held-out test set
3. SHAP produces plain-English explanations for every classification
4. MLflow tracking model versions with performance metrics
5. Ensemble safety mechanism: auto human review when models disagree by >0.3

### Phase 5: Policy Engine & API Catalog
**Goal:** Deploy OPA for decommission policies, Kyverno for admission control, Backstage for API catalog
**Mode:** mvp
**Requirements:** ENF-01, ENF-02, ENF-03, ENF-04, ENF-05
**Success Criteria:**
1. OPA deployed with Rego policies stored in Git
2. Kyverno rejecting new API deployments missing sunset-date + owner labels (audit-first, then enforce)
3. Backstage catalog populated with all discovered API endpoints
4. Each endpoint has documented owner team and metadata

### Phase 6: Decommission Workflow
**Goal:** Implement full 3-stage decommission pipeline with Flagger canary, human approvals, and audit trail
**Mode:** mvp
**Requirements:** ACT-01, ACT-02, ACT-03, ACT-04, ACT-05, ACT-06
**Success Criteria:**
1. Stage 1: Pipeline running in watch-only mode, F1 >= 0.85 confirmed
2. Stage 2: GitHub issues auto-opened for zombie candidates with SHAP explanation
3. Stage 3: Flagger 24-hour canary shadow at 1% traffic operational
4. Two independent human approvals required before decommission
5. 10-day slow traffic drain with automatic rollback on anomaly
6. Complete audit trail: PR history, approver identities, timestamps

### Phase 7: Secondary Discovery Methods
**Goal:** Integrate WAF logs, API gateway logs, frontend static analysis, and controlled staging scanning
**Mode:** mvp
**Requirements:** DSC-02, DSC-03, DSC-04, DSC-05
**Success Criteria:**
1. WAF log export API integrated with 5-minute polling
2. API gateway logs streaming via Kafka source connector
3. Playwright headless browser intercepting XHR/Fetch calls from frontend bundles
4. Kiterunner operational in staging with 10 req/s rate limit

### Phase 8: Compliance & Governance
**Goal:** Governance charter, regulatory compliance documentation, audit trail hardening
**Mode:** mvp
**Requirements:** CMP-01, CMP-02, CMP-03, CMP-04, CMP-05, CMP-06, CMP-07, CMP-08, CMP-09
**Success Criteria:**
1. Governance charter drafted and signed by CIO + CISO + Legal
2. Metadata-only capture verified (no PII in pipeline)
3. Log retention policies configured (30-day raw logs, 90-day feature vectors)
4. Zeek-level card data redaction verified (PCI-DSS v4)
5. AES-256 encryption at rest confirmed for all stored data
6. Kafka ACLs enforced
7. OWASP API Top 10 coverage documented (API2, API7, API9)
8. NIST CSF 2.0 mapping documented (Identify, Protect, Detect, Respond, Recover)
9. RBI IT Framework compliance documented

---
*Created: 2026-05-26 after initialization*
