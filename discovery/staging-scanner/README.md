# Staging Scanner

Kiterunner-style active path scanner that probes staging environments for undocumented API endpoints. Discovers endpoints that respond but aren't in any API catalog — a key zombie signal. **Never runs against production.**

## Files

### scanner.sh — Active Path Scanner (86 lines, built-in wordlist)

**Architecture:** Single Bash script with `set -euo pipefail` strict mode. Self-contained wordlist (no external files needed).

**Config (from env vars):**
- `STAGING_URL` — Target URL (default: `https://staging.bank.example.com`)
- `RATE_LIMIT` — Requests per second (default: 10)
- `OUTPUT_DIR` — Output directory (default: `/opt/discovery/output`)

**Built-in Wordlist (lines 19-68, 50 API paths):**
Systematically probes common API endpoints across these categories:
- **Common REST paths:** `/api`, `/api/v1`, `/api/v2`, `/api/v3`
- **API documentation:** `/swagger.json`, `/api-docs`, `/openapi.json`, `/openapi.yaml`
- **Spring Boot Actuator:** `/actuator`, `/actuator/health`, `/actuator/info`
- **Health/Version:** `/health`, `/healthcheck`, `/version`, `/status`
- **API gateways:** `/docs`, `/graphql`, `/rest`, `/soap`
- **Monitoring:** `/management`, `/monitor`, `/metrics`, `/prometheus`
- **Auth endpoints:** `/oauth/token`, `/oauth2`, `/login`, `/logout`, `/register`
- **Admin panels:** `/admin`, `/console`, `/h2-console`, `/druid`
- **Business domains:** `/users`, `/catalog`, `/inventory`, `/orders`, `/payments`, `/refunds`, `/settlements`

**Scan Loop (lines 72-83):**
For each path in the wordlist:
1. Constructs full URL: `{STAGING_URL}{path}`
2. Sends HTTP HEAD request via `curl -s -o /dev/null -w "%{http_code}" --max-time 5 --rate "${RATE_LIMIT}"`
3. Records any response that is **not** 404 or 000 (connection error)
4. Appends JSONL finding with url, path, status code, and timestamp

**Output:**
Writes to `$OUTPUT_DIR/findings.jsonl` in JSONL format (one JSON object per line for easy streaming/import).

### Dockerfile
Container build based on a lightweight base image (likely Alpine). Packages `scanner.sh` and `curl`. Designed for running as a Kubernetes Job or in CI/CD pipelines.
