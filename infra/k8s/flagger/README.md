# Flagger — Canary Deployment Controller

Flagger v1.36.0 canary controller installed in `flagger` namespace. Used in Stage 3 decommission to safely shift traffic away from zombie endpoints: 24h canary at 1% traffic → 10-day slow drain.

## Files

### flagger-install.yaml — Operator Installation (18 lines)

HelmChart installing Flagger v1.36.0 from `https://flagger.app`. Configured with:
- `metricsServer`: Prometheus at `http://prometheus.act.svc:9090` (metrics-based canary analysis)
- `meshProvider`: `kubernetes` (uses native K8s Service traffic routing, no service mesh required)

**Usage in Stage 3 Decommission (GitHub Actions workflow):**

1. **Canary Phase (24h):** Applies a Flagger `Canary` CR with `trafficWeight: 1` (1% traffic). Flagger monitors:
   - `request-success-rate` (threshold: 99%) — Prometheus metric
   - `request-duration` p99 (threshold: 500ms)
   - OPA rollback webhook at `opa.enforce.svc:8181/v1/data/zombie/safeguards`
   
2. **Slow Drain Phase (10d):** Manual loop reducing traffic by 10% daily, with OPA policy check at each increment.

3. **Rollback:** Automatic rollback if error rate spikes or latency degrades during any phase.
