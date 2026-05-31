# Streamlit Dashboard

Interactive web UI for SecureFlow with two modes: Demo (runs synthetic pipeline on ~1,13,836 endpoints) and Real (uploads a codebase zip for static analysis).

## Files

### app.py — Main Streamlit Application (505 lines)

**Architecture:** Single-file Streamlit app with session state management (`st.session_state`) to persist scan data across filter interactions without re-scanning.

**Two Modes:**
- **Demo Mode** (`render_demo_mode`): Reads `registry_scan.json` from the synthetic pipeline. Shows summary cards (total endpoints, active/deprecated/orphaned counts, avg security score). Renders 6 Plotly charts: classification donut, risk distribution bar, security findings bar, framework breakdown (code mode), language breakdown (code mode), security score histogram. Endpoint table with multi-select classification filters. Cost analysis section.
- **Real Mode** (`render_upload` + `render_real_mode`): Accepts a zip file upload via `st.file_uploader`. Calls `scan_codebase(upload_bytes)` which uses 20+ regex patterns across 7 framework types to discover API routes. Then scores each endpoint with `score_code_endpoint()` for security posture and zombie detection. Supports mode switching between "active/zombie" (code analysis) and "active/deprecated/orphaned" (traffic analysis).

**Route Detection Engine (`scan_codebase` function):**
The function extracts files from the uploaded zip, identifies the framework type based on file extensions and content patterns, then applies framework-specific regex patterns:

- **Python Flask:** `@app.route('/path')`, `@app.get/post/put/delete/patch`, `@app.add_url_rule`
- **Python FastAPI:** `@app.get/post/put/delete/patch`, `@app.add_api_route`
- **Python Django:** `path('...')`, `url(r'...')`
- **JavaScript Express:** `app.get/post/put/delete/patch('/path')`, `router.*`, `server.*`
- **JavaScript NestJS:** `@Get/@Post/@Put/@Delete/@Patch('/path')`
- **Java Spring:** `@GetMapping/@PostMapping/@PutMapping/@DeleteMapping/@RequestMapping`
- **Go Gin:** `r.GET/POST/PUT/DELETE/PATCH('/path')`

**Security Analysis (`score_code_endpoint` function):**
For each discovered endpoint, applies 4 categories of regex-based analysis:

1. **Good patterns** (add to security score): Auth decorators, auth middleware, rate limiting, input validation, CSRF/CORS protection, password hashing, TLS/HTTPS references
2. **Bad patterns** (deduct from security score): Code injection risks (`eval`, `exec`), SQL injection risks (`SELECT...%s`), hardcoded credentials, debug mode enabled, disabled verification
3. **Zombie indicators** (increase zombie probability): Deprecated markers, legacy naming, old versions, temporary/hack code, removal markers, mock/stub/test endpoints, debug/dev paths, health check/ping endpoints
4. Vulnerability scoring via secret scanning patterns

**UI Features:**
- Custom CSS with dark theme (background `#1a1a2e`, cards `#16213e`, accent `#e94560`)
- Logo display with base64 encoding
- Session state persistence for filters and data
- Plotly interactive charts with dark template
- Expandable endpoint table with color-coded risk levels
- Summary cards with KPI metrics

### registry_scanner.py — API Registry Scanner (187 lines)

**Input:** Parquet file with endpoint features (from traffic simulator or real data).

**Processing Pipeline:**
1. Reads parquet using `pandas.read_parquet()`
2. For each row, runs 3 analysis functions:

**`classify_endpoint(row)` — Classification Logic:**
- `is_zombie=1 AND real_calls=0 AND days_since_last_real_call > 90` → `orphaned`
- `is_zombie=1 OR (real_calls <= 100 AND days_stale > 30 AND <= 90)` → `deprecated`
- Otherwise → `active`

**`compute_security_score(row)` — 0-100 Scoring:**
- Auth coverage (`min(auth_ratio, 1.0) * 25`) — up to 25 points
- UA diversity (`min(ua/10, 1.0) * 15`) — up to 15 points
- IP diversity (`min(ips/8, 1.0) * 15`) — up to 15 points
- Low error rate (`max(0, 1.0 - r4xx - r5xx) * 20`) — up to 20 points
- Recency (`max(0, 1.0 - days/90) * 15`) — up to 15 points
- Not synthetic (`(1 - is_synth) * 10`) — up to 10 points

**`find_issues(row)` — Security Findings:**
Flags issues including: low auth coverage (<30%), minimal UA diversity (<=2), minimal IP diversity (<=2), high error rate (>10%), no recent real traffic (>60 days), 100% synthetic traffic, zombie classification.

**Output JSON structure:**
```json
{
  "scan_timestamp": "ISO datetime",
  "total_endpoints": 113836,
  "summary": { "active": N, "deprecated": N, "orphaned": N, "avg_security_score": 64.5, "total_annual_cost_inr": 1234567, "zombie_annual_cost_inr": 480000 },
  "finding_counts": { "Low authentication coverage": 1234, ... },
  "endpoints": [{ "endpoint_key", "host", "domain", "api_version", "method", "path", "traffic_level", "classification", "security_score", "is_zombie", "annual_cost_inr", "risk_level", "findings" }]
}
```

### report_generator.py — HTML Report Generator (253 lines)

**Input:** `registry_scan.json` from the scanner.

**Output:** Self-contained HTML file with embedded CSS (no external dependencies).

**Content sections:**
1. **Summary Cards (4):** Active count (green #53d769), Deprecated count (yellow #ffcc00), Orphaned count (red #e94560), Average Security Score
2. **Cost Analysis (3-column grid):** Total annual API cost, Zombie endpoint cost, Potential savings/year
3. **Classification Distribution:** CSS conic-gradient pie chart (no JS/drawing library needed), with legend showing percentages
4. **Domain Breakdown:** Sortable table with per-domain active/deprecated/orphaned counts and avg scores
5. **Security Findings:** Horizontal bar chart with per-category counts (color-coded: critical=#e94560, high=#ff8c00, medium=#ffcc00)
6. **Endpoint Inventory:** Full endpoint table with color-coded risk rows (row background tinting), showing host, method, path, domain, version, classification, score, risk badge, annual cost
   - `tr.risk-critical` gets rgba(233,69,96,0.1) background
   - Truncated path display (60 char max) with tooltip via title attribute

### run_demo.py — CLI Demo Runner (128 lines)

**Architecture:** Command-line entry point that orchestrates the full demo pipeline:

1. **Step 1:** Checks for `endpoint_features.parquet`, generates it if missing via `simulate.py --generate-features`
2. **Step 2:** Runs `registry_scanner.py --input parquet --output scan_json`
3. **Step 3:** Runs `report_generator.py --input scan_json --output report_html`
4. **Step 4:** Prints terminal-formatted summary with classification counts, top security findings (with severity tags: [CRITICAL]/[HIGH]/[MEDIUM]), and cost impact analysis

Uses `subprocess.run(capture_output=True, text=True)` for executing each step with captured output. Exits with code 1 on any step failure.
