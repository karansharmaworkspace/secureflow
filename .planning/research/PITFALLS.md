# Pitfalls Research: Zombie API Platform

## Critical Mistakes

### 1. Insufficient Synthetic Traffic Detection
**Warning signs**: High false positive rate during calibration, endpoint owners disputing classifications as "health checks"
**Prevention**: Implement synthetic detector BEFORE ML classifier — endpoints with 100% synthetic traffic must be explicitly flagged as zero real calls. The 7 synthetic signals (interval regularity, user-agent, payload entropy, source IP, response code, time-of-day clustering, call frequency) must all be computed.
**Phase to address**: Phase 2 (Flink feature computation)

### 2. Underestimating F1 Threshold Difficulty
**Warning signs**: F1 < 0.70 during Stage 1, frequent ensemble disagreements
**Prevention**: Start with conservative threshold (0.9+), collect labeled data during Stage 1, iterate before Stage 2 opens issues. Budget 4 weeks minimum for calibration.
**Phase to address**: Phase 4 (ML training + Stage 1)

### 3. Missing WAF/API Gateway Integration
**Warning signs**: Backstage catalog doesn't match discovered endpoints, external-facing APIs invisible
**Prevention**: Implement Methods 2-3 (WAF logs + API gateway) before Stage 2 begins. Zeek alone won't see external traffic or mTLS-encrypted internal traffic.
**Phase to address**: Phase 7 (secondary discovery methods)

### 4. Over-Engineering Before Data
**Warning signs**: Building ML pipeline without real traffic data
**Prevention**: Deploy Zeek + Kafka + Flink first (Phase 1-2), collect 2+ weeks of production traffic, THEN train XGBoost. Do not train on synthetic data — banking API traffic patterns are unique.
**Phase to address**: Phase 1-2 timing

### 5. Compliance Gaps in Audit Trail
**Warning signs**: Auditor asks "who approved this decommission and when?"
**Prevention**: Every decommission must produce: GitHub PR with endpoint metadata, two approver identities with timestamps, SHAP explanation preserved, 10-day drain logs, rollback trigger events. Immutable via Git history.
**Phase to address**: Phase 8 (compliance)

### 6. False Positive Decommission
**Warning signs**: Incident ticket: "API X stopped working after decommission"
**Prevention**: 24-hour canary shadow + 10-day slow drain + auto-rollback on any anomaly. The ensemble safety mechanism (auto human review if two models disagree by >0.3) is a hard requirement, not a nice-to-have.
**Phase to address**: Phase 6 (Act Layer)

### 7. Kyverno Rejecting Legitimate New APIs
**Warning signs**: Developers complaining about deployment failures, bypass requests
**Prevention**: Pilot Kyverno in audit-only mode first. Have clear exemption process via OPA policy with CISO override. Communicate label requirements to all API teams before enforcement.
**Phase to address**: Phase 5
