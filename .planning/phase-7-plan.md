# Phase 7 Plan: Secondary Discovery Methods

**Goal:** Layer secondary discovery methods on top of core pipeline — WAF logs, API gateway, frontend analysis, staging scanning.

## Tasks

### 7.1 WAF Log Integration
- Poll WAF log export API every 5 minutes
- Parse WAF log format and normalize to Zeek-compatible schema
- Push normalized records to Kafka topic `raw-api-calls`
- Covers external-facing APIs invisible to internal Zeek capture

### 7.2 API Gateway Log Streaming
- Deploy Kafka Connect source connector for API gateway logs
- Extract endpoint ownership data (upstream service name, team)
- Stream into `raw-api-calls` topic
- Enrich records with ownership metadata for Backstage

### 7.3 Frontend Static Analysis
- Build Playwright script to crawl production JS bundles
- Intercept XHR/Fetch calls via page route interception
- Extract API URL patterns, methods, and parameter structures
- Output discovered endpoints as catalog-info.yaml for Backstage

### 7.4 Controlled Staging Scanning
- Deploy Kiterunner in staging environment (rate limited to 10 req/s)
- Probe known API path patterns (swagger.json, api-docs, /v1/, /v2/, /actuator)
- Discover undocumented endpoints for catalog enrichment
- Never run in production

## Success Criteria
1. WAF logs flowing into Kafka every 5 minutes
2. API gateway logs streaming with ownership metadata
3. Playwright extracting API URLs from frontend bundles
4. Kiterunner discovering endpoints in staging (10 req/s max)
5. All discovered endpoints registered in Backstage catalog

---
*Created: 2026-05-26*
