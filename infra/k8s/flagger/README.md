# Flagger - Canary Deployments

Flagger canary deployment controller that manages progressive traffic shifting during the decommission process. Handles the 24-hour canary phase where 1% of traffic is routed before full removal.

## Configuration

- Canary deployment configurations for endpoint removal
- Automatic rollback on error rate spikes
- Traffic mirroring for impact analysis
- Integration with Prometheus for metrics-based analysis
