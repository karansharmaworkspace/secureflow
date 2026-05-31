# Features Research: Zombie API Platform

## Table Stakes (Must Have)

- Passive network traffic capture without payload inspection
- Real-time stream processing of API call metadata
- ML classification of endpoint activity status
- Synthetic traffic detection (health checks, monitoring bots)
- Per-endpoint explainability for classification decisions
- Human approval gates before any decommission action
- API catalog with ownership tracking
- Policy enforcement for new API deployments (sunset date, owner labels)
- Audit trail for all decommission actions
- Regulatory compliance (OWASP, NIST, GDPR, PCI-DSS, RBI, ISO 27001)

## Differentiators

- F1 >= 0.85 accuracy threshold with ensemble safety (auto human review if models disagree by >0.3)
- 20+ distinct signals per endpoint spanning frequency, auth, payload, dependency, and ownership dimensions
- 3-stage decommission pipeline (Watch → Notify → Decommission) with progressive canary
- 10-day slow traffic drain with automatic rollback on anomaly detection
- Synthetic vs real traffic discrimination — critical for banking environments dominated by monitoring traffic
- 5 discovery methods (passive capture, WAF logs, API gateway logs, frontend analysis, staging scanning)
- Zero PII architecture — metadata-only capture with card data redaction at the sensor level

## Anti-Features (Deliberately Not Building)

- Payload content inspection — legally prohibited in banking context, not needed for classification
- External OSINT scanning — blocked by WAF, unreliable for production use
- Automatic decommission without human approval — unacceptable risk for PSB production
- Real-time enforcement on long-interval APIs (cron/batch) — 90-day observation window required first
- Custom authentication system — leverage bank's existing IAM via Backstage integrations
