# Phase 5 Plan: Policy Engine & API Catalog

**Goal:** Deploy OPA for decommission policies, Kyverno for admission control, Backstage for API catalog.

## Tasks

### 5.1 Deploy OPA
- Deploy OPA as a sidecar/admission controller on K8s
- Mount Rego policies from ConfigMap (Git-backed)
- Expose REST API for policy evaluation queries

### 5.2 Write Rego Decommission Policies
- Policy: `zombie_decommission` — endpoint qualifies if F1 > 0.85 AND 100% synthetic
- Policy: `require_approval` — two humans required before decommission
- Policy: `canary_required` — 24h shadow at 1% before full removal
- Policy: `rollback_on_anomaly` — auto-rollback if error rate spikes

### 5.3 Deploy Kyverno
- Install Kyverno with audit-only mode
- Write ClusterPolicy: require labels `x-api-sunset-date` and `x-api-owner-team`
- Write ClusterPolicy: require annotation `x-api-owner-slack-channel`
- Monitor audit results before switching to enforcement

### 5.4 Deploy Backstage
- Deploy Backstage with PostgreSQL backend
- Configure catalog with API entity provider
- Import discovered endpoints into Backstage catalog
- Add ownership metadata (team, slack, pager duty)

### 5.5 Integration
- OPA integrates with GitHub Actions decommission workflow (Phase 6)
- Kyverno blocks non-compliant new API deployments
- Backstage serves as source of truth for endpoint ownership

## Success Criteria
1. OPA policies evaluated per decommission decision with audit log
2. Kyverno blocking new APIs missing required labels (after audit period)
3. Backstage catalog populated with discovered endpoints and ownership
4. All Rego policies stored in Git with version history
5. End-to-end: classification → OPA evaluation → decision logged

---
*Created: 2026-05-26*
