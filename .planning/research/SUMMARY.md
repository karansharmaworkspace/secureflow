# Research Summary: Zombie API Discovery Platform

## Key Findings

**Stack**: Fully open-source (Zeek, Kafka, Flink, Feast, Redis, MinIO, XGBoost, SHAP, MLflow, OPA, Kyverno, Backstage, Flagger, GitHub Actions) — zero license cost, all Apache/BSD/MIT licensed except MinIO (AGPL v3).

**Table Stakes**: Passive capture, real-time processing, ML classification, synthetic traffic detection, explainability, human approval gates, API catalog with ownership, policy enforcement, audit trail, regulatory compliance (OWASP, NIST, GDPR, PCI-DSS, RBI, ISO 27001).

**Critical Differentiators**: 20+ signals per endpoint, 3-stage decommission pipeline, ensemble safety mechanism, synthetic vs real traffic discrimination, 5 discovery methods, zero PII architecture.

**Watch Out For**:
1. Synthetic traffic detection must precede ML classification — otherwise high false positive rate
2. F1 >= 0.85 requires real production traffic data, not synthetic training — budget 4 weeks for Stage 1 calibration
3. Zeek alone misses external-facing and mTLS-encrypted APIs — WAF and API gateway integration are essential
4. False positive decommission is the #1 risk — canary + slow drain + auto-rollback are non-negotiable
5. Kyverno must start in audit-only mode to avoid developer friction

**Build Order**: Infrastructure → Listen → Remember → Detect → Enforce → Act → Discovery Methods → Compliance
