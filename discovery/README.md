# Discovery

API discovery methods for finding zombie endpoints across different sources. Three complementary approaches: frontend JS static analysis, staging environment path scanning, and WAF log integration.

## Subdirectories

### frontend-analyzer/
**Method:** Client-side static analysis via Playwright.
**How it works:** Launches a headless Chromium browser, navigates to the target banking application URL, intercepts all network requests (`page.route("**/*")`), and extracts API endpoints from both XHR/Fetch calls and inline `<script>` content.
**Output:** Backstage-compatible YAML catalog files with discovered endpoint metadata.
**Zombie relevance:** Finds API URLs hardcoded in production JS bundles — endpoints that might not be in any active documentation.
**Dependencies:** Node.js, Playwright, Jest (for tests).

### staging-scanner/
**Method:** Active path probing (Kiterunner-style).
**How it works:** Bash script with a built-in wordlist of 50+ common API paths. Uses `curl` with `--rate` flag for rate-limited probing (10 req/s default). Reports any non-404 response as a finding.
**Output:** JSONL file with discovered URLs, HTTP status codes, and timestamps.
**Zombie relevance:** Discovers endpoints that respond but aren't in any API catalog — classic zombie signal.
**Constraint:** Staging environments only — never runs against production.
**Dependencies:** curl, bash.

### waf-poller/
**Method:** Passive WAF log integration.
**How it works:** Python service that polls the WAF API at configurable intervals (300s default), normalizes WAF log records to a standard schema, and publishes them to Kafka topic `raw-api-calls` for downstream processing.
**Output:** Kafka messages with normalized WAF records.
**Zombie relevance:** Captures external-facing API traffic — endpoints called by external users that may not be in internal documentation.
**Dependencies:** Python, requests, confluent-kafka.
