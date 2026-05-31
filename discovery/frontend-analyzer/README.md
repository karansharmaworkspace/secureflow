# Frontend Analyzer

Playwright-based static analysis tool that discovers API endpoints by crawling the frontend application. Uses two complementary techniques: **XHR/Fetch interception** (captures live API calls) and **inline script analysis** (extracts hardcoded API paths from JS bundles). Outputs Backstage-compatible YAML catalog files.

## Files

### main.js — Playwright Discovery Agent (151 lines)

**Architecture:** Single Node.js script using Playwright's `chromium` module. Imports `fs` and `path` for file output.

**Config (from env vars):**
- `TARGET_URL` — Banking app URL to crawl (default: `https://bank.example.com`)
- `OUTPUT_DIR` — Directory for output YAML files (default: `/opt/discovery/output`)

**Initialization (lines 70-78):**
Creates output directory, launches headless Chromium browser, creates a new browser context with custom user agent: `Mozilla/5.0 ... ZombieDiscovery/1.0`.

**Technique 1 — Network Interception (lines 12-37, `interceptRequests`):**
Registers a route handler via `page.route("**/*")` that intercepts every network request. Filters for API paths by checking if `url.pathname` starts with `/api/`, `/v1/`, `/v2/`, or `/v3/`. Captures: HTTP method, path, host, request headers, resource type, and timestamp. Deduplicates via `discoveredEndpoints` Set.

**Technique 2 — Inline Script Analysis (lines 40-68, `extractJsApis`):**
Uses `page.evaluate()` to run code in the browser context. Queries for `<script:not([src])>` elements (inline scripts). Extracts API paths using regex: `/["'](\/api\/[a-zA-Z0-9_\-/{}]+)["']/g`. Tags these with `source: "static-analysis"`.

**Crawl Strategy (lines 84-95):**
Navigates to `TARGET_URL`, waits for `networkidle`. Extracts all internal `<a href>` links (up to 20). Crawls each linked page, calling `extractJsApis` on each.

**Output Generation (lines 97-146):**
Creates two types of Backstage-compatible YAML files:
1. `catalog-info.yaml` — A `Location` catalog entity referencing all discovered APIs
2. `api-{i}.yaml` — Individual `API` entities with annotations for discovery metadata (path, method, host, source)

Outputs summary count and JSON dump of all discovered patterns to stdout.

### package.json — Node.js Configuration (16 lines)

Dependencies: `playwright ^1.44.0`. Dev dependencies: `jest ^30.4.2`. Scripts: `start` (runs `node main.js`), `test` (runs `jest`).

### __tests__/
Jest test suite for the analyzer logic. Tests endpoint extraction, URL parsing, and catalog output format.
