# Legacy v1 API Routes

**Zombie endpoints — the primary test targets for SecureFlow's static analysis scanner.** These files contain deprecated v1 routes that should have been removed but remain accessible on the network. The scanner's regex patterns should detect the deliberate zombie indicators: deprecation comments, TODO markers, hack/temp/mock paths, and missing auth.

## Files

### v1_api.py — v1 Legacy API (49 lines, 6 routes)

Starts with explicit deprecation docstring: *"DEPRECATED - This entire file is legacy v1 API. Scheduled for removal after 2025-12-31."* No security or auth references anywhere.

Routes:
- `GET /accounts` — `# TODO: remove this, use v3`
- `GET /accounts/{id}` — `# legacy endpoint, no auth check`
- `POST /transfer` — `# old transfer, no validation`
- `GET /balance` — `# deprecated, use v3/accounts/{id}/balance`
- `GET /status` — Deprecated version info
- `GET /version` — Returns `{"deprecated": True}`
- `POST /mock/payment` — `# test endpoint, should not be in production`

**Scanner detection signals:**
- Docstring with "DEPRECATED" keyword
- `# TODO:` comments
- `# legacy endpoint, no auth check` — explicit no-auth admission
- `# test endpoint, should not be in production` — mock endpoint in prod
- `/mock/` path prefix

### old_transfer.py — Dead Transfer Code (35 lines, 5 routes)

Starts with explicit docstring: *"Legacy transfer service - DEAD CODE"* with "Last modified: 2023-06-15" and "Nobody has called these endpoints in 2 years."

Routes:
- `POST /legacy` — Returns `{"status": "legacy"}`
- `POST /old/neft` — Old NEFT stub
- `POST /old/rtgs` — Old RTGS stub
- `GET /temp/status` — `# temporary endpoint, remove me`
- `GET /hack/check` — `# quick hack for testing, do not use`

**Scanner detection signals:**
- Docstring with "DEAD CODE" keyword
- `# temporary endpoint, remove me` — temporary/hack comment
- `# quick hack for testing, do not use` — hack/mock signal
- `/temp/`, `/hack/`, `/old/` path prefixes
- "Last modified: 2023-06-15" — over 2 years stale
- No imports, no auth, no validation — bare minimum APIRouter
