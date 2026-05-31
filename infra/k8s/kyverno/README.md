# Kyverno — Admission Controller

Kyverno v3.2.4 admission controller (2 replicas) installed in `kyverno` namespace. Provides governance policies that enforce API labeling standards — every Ingress and HTTPRoute must declare a sunset date, owner team, and owner Slack channel.

## Files

### kyverno-install.yaml — Operator Installation (33 lines)

HelmChart installing Kyverno v3.2.4 from `https://kyverno.github.io/kyverno/`. Components enabled: admissionController (2 replicas), backgroundController, cleanupController, reportsController. Resource filters exclude Events, kyverno/kube-system/kube-public/kube-node-lease namespaces.

### kyverno-policies.yaml — API Governance Policies (79 lines)

**ClusterPolicy 1: `require-api-labels`** (severity: medium, Audit mode)

3 rules that validate all Ingress and HTTPRoute resources:
1. **`require-sunset-date`** — Must have label `x-api-sunset-date` (prevents deploying routes without a planned removal date)
2. **`require-owner-team`** — Must have label `x-api-owner-team` (ensures ownership accountability)
3. **`require-owner-slack`** — Must have annotation `x-api-owner-slack` (for automated notification routing)

**ClusterPolicy 2: `api-sunset-enforcement`** (severity: high, Audit mode)

1 rule:
1. **`reject-expired-sunset`** — Uses Kyverno's `time.now()` function to compare against `x-api-sunset-date` label. If current date >= sunset date, the resource is flagged: "API has passed its sunset date. Create PR to extend or schedule decommission."

Both policies use `validationFailureAction: Audit` — violations are reported but not blocked (observability-first approach matching Stage 1 "watch only" philosophy).
