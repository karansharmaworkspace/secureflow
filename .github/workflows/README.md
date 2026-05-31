# GitHub Actions - Three-Stage Decommission Workflows

This directory contains the CI/CD workflows that orchestrate the progressive three-stage decommission process for zombie API endpoints. Each workflow is triggered manually (`workflow_dispatch`) or on a schedule, and enforces policy decisions via OPA (Open Policy Agent) at every stage.

## Files

### stage1-watch-only.yml — Observation and Reporting

**Trigger:** Scheduled daily at 06:00 UTC, or manual dispatch.

**Pipeline Steps:**
1. **Query MLflow** — Fetches the champion (best-performing) model from the MLflow Model Registry using the alias API at `$MLFLOW_URI/api/2.0/mlflow/registered-models/alias?name=zombie-classifier&alias=champion`. Extracts the run ID into `model_run_id.txt`.
2. **Fetch features from Feast** — Uses the Feast Python SDK (`from feast import FeatureStore`) to retrieve online features (`real_calls`, `is_100pct_synthetic`) for all registered entities. Writes to `features.json`.
3. **Run classification** — Executes `ml-pipeline/predict.py features.json > classification.json` to get ML predictions with confidence scores.
4. **Query OPA for policy decisions** — For each classified endpoint, sends a POST to the OPA policy engine at `$OPA_URL/v1/data/zombie/decommission` with the classification result, F1 score, and ensemble disagreement. Stores the policy decision back into `classification.json`.
5. **Generate report** — Python script filters zombie candidates (where `r['classification'] == 'zombie'`) and writes a markdown report with endpoint keys, confidence scores, and SHAP explanations.
6. **Upload artifact** — Archives the report as a workflow artifact named `stage1-report-{run_id}`.

**Policy Gate:** No automated actions are taken in this stage. Pure observation and documentation. The exit criterion for graduating to Stage 2 is `F1 >= 0.85`.

### stage2-tell-owner.yml — Notify and Gather Feedback

**Trigger:** Manual dispatch with required inputs (endpoint_key, f1_score, confidence, explanation, owner_team).

**Pipeline Steps:**
1. **Validate with OPA** — Sends the endpoint metadata to OPA at `/v1/data/zombie/decommission` for real-time policy evaluation. Includes the endpoint key, F1 score, `is_100pct_synthetic` flag, `ensemble_disagreement` (hardcoded 0.1 in template), and timestamp. Writes the policy result to `policy_result.json`.
2. **Create GitHub Issue** — Uses `actions/github-script@v7` to programmatically create a GitHub issue via the REST API. The issue body includes the endpoint identifier, model F1 score and confidence, owner team name from Backstage, full SHAP explanation text, and a 3-option checkbox response: Confirm (zombie), Dispute (with evidence), or Request Exemption. An auto-calculated 30-day deadline is included. Labels applied: `zombie-candidate`, `needs-response`.
3. **Upload policy result** — Archives the OPA decision as a workflow artifact.

**Policy Gate:** The endpoint owner has 30 days to respond. If they confirm, or if the deadline lapses without response, the endpoint graduates to Stage 3. Owners may dispute or request an exemption (valid for 90 days, requires CISO re-approval).

### stage3-turn-it-off.yml — Canary, Drain, and Decommission

**Trigger:** Manual dispatch with required inputs (endpoint_key, ingress_name, namespace, approver1, approver2).

**Job 1 — preflight:** Validates that two different GitHub usernames are provided as approvers using `len(set(approvers)) < 2`.

**Job 2 — canary (24 hours):**
1. Applies a Flagger `Canary` custom resource via `kubectl apply` that mirrors 1% of traffic (`trafficWeight: 1`) and monitors `request-success-rate` (threshold: 99%) and `request-duration` p99 (threshold: 500ms) every 1 minute. Registers an OPA rollback webhook at `opa.enforce.svc:8181/v1/data/zombie/safeguards`.
2. Sleeps for 86400 seconds (24 hours) while Flagger runs the canary analysis.

**Job 3 — slow-drain (10 days):**
1. Loops for 10 days, each day draining an additional 10% of traffic.
2. Before each drain step, checks with OPA at `$OPA_URL/v1/data/zombie/safeguards` sending `{drain_percent, day}`.
3. Sleeps 86400 seconds between each iteration.

**Job 4 — decommission (final):**
1. Remove the ingress: `kubectl delete ingress {name} -n {namespace}`
2. Archive in Backstage: POSTs a `decommissioned-api` entity to the Backstage catalog API with annotations recording the endpoint key, decommission date, and both approver identities.
3. Commit audit trail: Creates a JSON file at `.planning/audit/decommission-{run_id}.json` with full metadata (endpoint key, ingress, namespace, approvers, timestamp, run URL), then commits and pushes to Git.

**Safety Gates:**
- Two different human approvers required
- 24-hour canary at 1% before any real traffic impact
- 10-day gradual drain with OPA checks at each increment
- Automatic rollback on error rate spikes or latency degradation
- Full Git-immutable audit trail with approver identities
