# Zombie API Discovery & Decommission Platform

## What This Is

An end-to-end automated system that continuously monitors network traffic to discover all API endpoints, uses AI/ML to classify which are zombies (deprecated but still running), safely decommissions confirmed zombies with human approval gates, provides full audit trail for regulatory compliance, and prevents new zombies from being created via policy enforcement. Built for Union Bank of India as part of iDEA 2.0 Hackathon, Problem Statement PS9.

## Core Value

Safely identify and remove zombie API endpoints from the bank's network — converting a 15+ engineer-day manual process into 30 minutes of human attention — while ensuring zero production impact through progressive canary decommissioning.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] **LISTEN-01**: Deploy Zeek as passive network sensor on SPAN/TAP port mirroring internal traffic
- [ ] **LISTEN-02**: Stream Zeek logs into Apache Kafka topics in real-time
- [ ] **LISTEN-03**: Process Kafka streams with Apache Flink (exactly-once semantics, feature computation)
- [ ] **MEM-01**: Set up Feast ML feature store for feature definitions and serving
- [ ] **MEM-02**: Deploy Redis HA cluster for sub-millisecond feature lookups during live classification
- [ ] **MEM-03**: Set up MinIO S3-compatible storage for historical logs and model artifacts
- [ ] **DETECT-01**: Train XGBoost classifier on 20+ signals per endpoint to classify zombie vs active
- [ ] **DETECT-02**: Integrate SHAP for plain-English explanations per classification decision
- [ ] **DETECT-03**: Track model versions and performance with MLflow
- [ ] **DETECT-04**: Implement synthetic traffic detection (distinguish health-check bots from real users)
- [ ] **ENF-01**: Deploy OPA with Rego policies for decommission decision evaluation
- [ ] **ENF-02**: Configure Kyverno admission controller to reject new APIs missing sunset-date/owner labels
- [ ] **ENF-03**: Set up Backstage developer portal as canonical API catalog with ownership info
- [ ] **ACT-01**: Build 3-stage decommission workflow (Watch Only → Tell Owner → Turn It Off)
- [ ] **ACT-02**: Implement 24-hour canary shadow at 1% traffic via Flagger before decommission
- [ ] **ACT-03**: Implement 10-day slow traffic drain with automatic rollback on anomaly
- [ ] **ACT-04**: Require two independent human approvals for final decommission
- [ ] **DISC-01**: Passive network capture via SPAN/TAP port (primary discovery method)
- [ ] **DISC-02**: WAF log integration (5-min polling for external-facing APIs)
- [ ] **DISC-03**: API gateway log streaming via Kafka connector
- [ ] **DISC-04**: Frontend static analysis (JS bundle parsing, Playwright XHR interception)
- [ ] **DISC-05**: Controlled internal scanning in staging only (Kiterunner, 10 req/s max)
- [ ] **COMP-01**: Governance charter drafted and signed by CIO + CISO + Legal
- [ ] **COMP-02**: Achieve F1 >= 0.85 before any automated actions
- [ ] **COMP-03**: Metadata-only capture compliance (no PII, card data redaction)
- [ ] **COMP-04**: Full audit trail: Git PR history, approver identities, timestamps

### Out of Scope

- TLS/mTLS encrypted service mesh traffic — accepted risk, documented in governance charter
- External partner APIs not visible in WAF logs
- Legacy non-HTTP protocols (SOAP/gRPC without HTTP capture)
- Real-time enforcement on cron/batch APIs with >90-day intervals

## Context

This platform is being built for a PSB Hackathon (iDEA 2.0, PS9) by Logic Legion — K J Somaiya College of Engineering. The external OSINT approach was blocked by Union Bank's WAF, forcing a pivot to internal discovery methods. The final deliverable covers a five-layer architecture (LISTEN → REMEMBER → DETECT → ENFORCE → ACT) using 100% open-source tools with zero license cost. Regulatory compliance must cover OWASP API Top 10, NIST CSF 2.0, GDPR Article 25, PCI-DSS v4, RBI IT Framework, and ISO 27001 A8.8.

## Constraints

- **Tech Stack**: 100% open source, zero license cost (Zeek, Kafka, Flink, Feast, Redis, MinIO, XGBoost, SHAP, MLflow, OPA, Kyverno, Backstage, Flagger, GitHub Actions)
- **Network**: Must operate at Layer 2 via SPAN/TAP to bypass WAF; no payload inspection
- **Safety**: Two human approvals required before decommission; 10-day slow drain with auto-rollback
- **Accuracy**: F1 >= 0.85 threshold before automated actions; ensemble disagreement >0.3 triggers human review
- **Compliance**: Metadata-only capture, no PII, AES-256 at rest, 30-day raw log retention, 90-day feature vector retention
- **Timeline**: 3 stages across 13+ weeks (Watch Only W1-4, Tell Owner W5-12, Turn It Off W13+)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Internal discovery over external OSINT | Union Bank WAF blocked external scanning | ✓ Good |
| Zeek passive capture as primary method | Operates at Layer 2, bypasses WAF entirely | ✓ Good |
| XGBoost over deep learning | Interpretable, lower data requirements, explainable via SHAP | — Pending |
| 20+ signals per endpoint | Ensures robust classification across diverse API behaviors | — Pending |
| 3-stage decommission process | Safety-first: observe, notify, then decommission with canary | — Pending |
| 100% open-source stack | Zero license cost for PSB procurement compliance | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-26 after initialization*
