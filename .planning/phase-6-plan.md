# Phase 6 Plan: Decommission Workflow

**Goal:** Full 3-stage decommission pipeline with Flagger canary, human approvals, and audit trail.

## Tasks

### 6.1 GitHub Actions Workflow — Stage 1 (Watch Only)
- Daily classification report: endpoints classified, confidence scores, ensemble disagreement
- No automated actions — all output logged to `.planning/reports/`
- F1 calibration tracking against human-labeled ground truth
- Governance charter draft generated

### 6.2 GitHub Actions Workflow — Stage 2 (Tell the Owner)
- Auto-open GitHub issue for zombie candidates with F1 >= 0.85
- Issue template: endpoint path, SHAP explanation, confidence score, owner team, 30-day response window
- Owner response options: Confirm (zombie), Dispute (evidence needed), Request Exemption (business justification)
- Owner responses fed back as labelled training data (retrain trigger)

### 6.3 GitHub Actions Workflow — Stage 3 (Turn It Off)
- Triggered after owner confirms + 2 human approvals
- Pre-decommission: 24h Flagger canary shadow at 1% traffic
- If canary passes: initiate 10-day slow traffic drain (10% per day)
- Auto-rollback on: error rate spike, latency increase, dependency failure
- After drain complete: remove endpoint config, archive in Backstage

### 6.4 Flagger Canary Configuration
- Deploy Flagger on K8s
- Configure canary resource: 1% traffic shadow, 24h analysis window
- Metrics: request success rate (99%), request duration (p99 < 500ms), no 5xx spike
- Automatic promotion or rollback based on metric thresholds

### 6.5 Approval & Audit Trail
- Two independent human approvals via GitHub PR review
- PR contains: endpoint metadata, classification evidence, SHAP explanation, canary results
- Complete audit trail: PR history, approver identities, timestamps, rollback events
- All artifacts stored in `.planning/audit/`

## Success Criteria
1. Stage 1: daily reports generated, no automated actions
2. Stage 2: GitHub issues auto-opened with full context
3. Stage 3: Flagger canary operational with auto-rollback
4. Two human approvals enforced before decommission
5. Complete audit trail: PR history, approvers, timestamps

---
*Created: 2026-05-26*
