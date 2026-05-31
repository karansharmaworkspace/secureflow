# Banking API Tests

Test files for the simulated banking API. Contains deliberately placed mock/stub/fake endpoints that should be detected by SecureFlow's zombie scanner.

## Files

### test_mock.py — Mock Test Endpoints (28 lines, 4 routes)

**IMPORTANT:** Despite the filename suggesting `test_mock.py` is a test file, it actually defines FastAPI routes. This is a deliberate testing scenario for the scanner to detect test/mock endpoints that should not be in the main API bundle.

Routes:
- `GET /mock/accounts` — Returns test account data
- `POST /mock/transfer` — Mock transfer (`{"status": "mock-success"}`)
- `GET /stub/balance` — Stub balance endpoint (`{"balance": 99999}`)
- `GET /fake/user` — Fake user endpoint with test email

**Scanner detection signals:**
- Docstring: "These are mock endpoints for integration testing. Do not expose in production."
- `/mock/`, `/stub/`, `/fake/` path prefixes — all strong zombie indicators
- `import APIRouter` — detectable as a FastAPI route file
