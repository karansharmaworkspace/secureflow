# Frontend Analyzer Tests

Jest test suite for the Playwright-based frontend static analysis tool.

## Files

### main.test.js — Unit Tests (78 lines)

Tests the core logic of `main.js` by extracting the pure functions from the side-effect-heavy Playwright code. 3 test suites:

1. **`interceptRequests logic`** — Tests path prefix matching:
   - `/api/`, `/v1/`, `/v2/`, `/v3/` paths → `true` (API endpoints)
   - `/about`, `/static/css/style.css` → `false` (non-API resources)

2. **`extractJsApis logic`** — Tests regex extraction from inline script content:
   - `"/api/users"` and `"/api/v1/data"` → extracted
   - Non-API strings (like `"/v1/other"` that doesn't start with `/api/`) → filtered out
   - Empty/irrelevant content → empty array

3. **`discoveredPatterns structure`** — Tests the pattern object creation format:
   - Verifies method, path, host, headers, resourceType, and timestamp fields
   - Uses a mock request object to validate structure without Playwright
