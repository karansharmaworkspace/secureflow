# Discovery

API discovery methods for finding zombie endpoints across different sources.

## Subdirectories

### frontend-analyzer/
Playwright-based tool that intercepts XHR/Fetch calls from frontend JavaScript bundles. Finds API URLs hardcoded in production JS.

| File | Purpose |
|------|---------|
| `main.js` | Entry point. Launches headless browser, navigates to target URL, intercepts network requests, extracts API endpoints. |
| `__tests__/main.test.js` | Unit tests for endpoint extraction logic. |
| `package.json` | Node.js dependencies (playwright). |

### staging-scanner/
Kiterunner-style path scanner for staging environments only. Never runs in production.

| File | Purpose |
|------|---------|
| `scanner.sh` | Bash script that probes common API paths against a staging URL. Rate-limited to 10 req/s. Outputs findings as JSONL. |
| `Dockerfile` | Container for running scanner in CI/CD pipeline. |

### waf-poller/
Polls WAF log API to discover external-facing endpoints.

| File | Purpose |
|------|---------|
| `main.py` | Python script that polls WAF API on configurable interval. Normalizes WAF records to standard format. Publishes to Kafka topic `raw-api-calls`. |
| `Dockerfile` | Container for running as Kubernetes CronJob or Deployment. |
