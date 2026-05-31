# OPA — Policy Engine

Open Policy Agent v0.66.0 deployment (2 replicas) in the `enforce` namespace. Provides Rego-based policy enforcement for the 3-stage decommission process. Queried by GitHub Actions workflows before every automated action. Exposes REST API at port 8181.

## Files

### opa-deployment.yaml — OPA Server + Rego Policies (121 lines)

**Deployment:** 2 replicas of `openpolicyagent/opa:0.66.0`
- Args: `run --server --addr=0.0.0.0:8181 --log-level=info --set=decision_logs.console=true /policies`
- Liveness/Readiness: HTTP GET `/health` on port 8181
- Loads policies from ConfigMap `opa-policies` mounted at `/policies`

**Service:** ClusterIP exposing port 8181, used by GitHub Actions and Flagger webhooks.

**Embedded Rego Policies (ConfigMap `opa-policies`):**

**1. `decommission.rego` — Decommission Approval Gate (30 lines):**
- `allow` returns `true` only if ALL: F1 >= 0.85, 100% synthetic, ensemble disagreement < 0.3
- `require_human_review` is `true` if ensemble disagreement >= 0.3
- `decommission_decision` returns one of: `"approve"`, `"human_review"`, `"reject"`

**2. `safeguards.rego` — Safety Checks (17 lines):**
- `require_two_approvals = true` — Always requires 2 human approvers
- `require_canary` — 24-hour canary at 1% traffic before full decommission
- `require_slow_drain` — 10-day gradual traffic drain
- `auto_rollback_on_anomaly = true` — Automatic rollback if error rate spikes

**3. `audit.rego` — Audit Logging (5 lines):**
Formats a structured audit string: `endpoint={key}, f1={score}, synthetic={bool}, ensemble_disagreement={val}, decision={decision}, ts={timestamp}`

**OPA Query Pattern (from GitHub Actions):**
```bash
curl -s $OPA_URL/v1/data/zombie/decommission \
  -H "Content-Type: application/json" \
  -d '{"input": {"endpoint_key":"...", "f1_score":0.92, "is_100pct_synthetic":true, "ensemble_disagreement":0.1}}'
# Returns: {"result": {"allow": true, "decommission_decision": "approve", ...}}
```
