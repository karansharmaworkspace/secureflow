# Python Banking API (FastAPI)

FastAPI-based banking API implementation with 32 routes across 9 files. Designed to test the SecureFlow scanner's ability to detect FastAPI-style route patterns and distinguish active v3 endpoints from deprecated v1 zombie endpoints.

## Files

### app.py — Application Entry Point (28 lines)

Creates and configures the FastAPI application. Imports 5 routers from `routes/` and `routes/legacy/`, mounts them under `/api/v3` and `/api/v1` prefixes respectively. Exposes two built-in endpoints:
- `GET /health` — Returns `{"status": "ok"}`
- `GET /api/v3/versions` — Returns version info including deprecation notice

Router registration:
- `auth.router` → `/api/v3/auth` — 6 endpoints
- `accounts.router` → `/api/v3/accounts` — 7 endpoints
- `payments.router` → `/api/v3/payments` — 8 endpoints
- `v1_api.router` → `/api/v1` — 6 zombie endpoints
- `old_transfer.router` → `/api/v1/transfer` — 5 zombie endpoints

### config.py — Application Configuration (21 lines)

Centralized config with deliberately hardcoded "secrets" for scanner testing:
- `SECRET_KEY`, `DB_PASSWORD`, `API_KEY`, `JWT_SECRET`, `ENCRYPTION_KEY` — all hardcoded (bad practice the scanner flags)
- `DEBUG = True` — Flagged as security finding
- `CORS_ORIGINS = ["*"]` — Flagged as security finding
- `RATE_LIMIT = 100`, `MAX_LOGIN_ATTEMPTS = 5`, `SESSION_TIMEOUT = 3600`

### utils.py — Utility Functions (34 lines)

Contains 2 functions with deliberately poor practices for scanner detection:
- `check_service(url)` — Uses `verify=False` on SSL (flagged as security anti-pattern)
- `get_all_health()` — Aggregates health checks from 3 internal services
- `deploy_check()` — Uses `os.system("kubectl get pods...")` (flagged as command injection risk)

### models/user.py — Pydantic Data Models (31 lines)

Defines 3 data models used across route handlers:
- `User` — id, name, email, phone, account_number, ifsc_code, kyc_status, is_active
- `AccountBalance` — account_number, balance, currency (default INR), last_updated
- `Transaction` — id, from_account, to_account, amount, status, timestamp

## Route Handlers (31 total routes)

### routes/auth.py — Authentication Endpoints (54 lines, 6 routes)

Pydantic request models: `LoginRequest` (username, password, device_id), `OTPVerify` (phone, otp).
- `POST /login` — Rate-limited login (5 attempts lockout). Returns JWT token.
- `POST /refresh` — Token refresh
- `POST /otp/generate` — OTP generation
- `POST /otp/verify` — OTP verification
- `POST /logout` — Session termination
- `GET /session` — Session status

### routes/accounts.py — Account Management (40 lines, 7 routes)

- `GET /{account_id}/balance` — Returns balance with INR currency
- `GET /{account_id}/statement` — Transaction history with configurable `days` param (max 365)
- `GET /{account_id}/details` — Account type and status
- `GET /{account_id}/nominees` — Nominee list
- `POST /{account_id}/nominees` — Add nominee with name+relation
- `GET /{account_id}/kyc-status` — KYC verification status
- `PUT /{account_id}/preferences` — Update email/SMS alert preferences

### routes/payments.py — Payment Processing (63 lines, 8 routes)

Pydantic models: `NEFTTransfer` (from_account, to_account, ifsc, amount, remark), `IMPStransfer` (from_account, mobile, mmid, amount).

Contains deliberate security bad practices for scanner detection:
- SQL injection risk: `query = f"SELECT * FROM accounts WHERE account_number = '{req.to_account}'"` (line 29)
- OS command injection: `os.system(f"echo UPI payment to {vpa} for {amount}")` (line 62)
- No auth decorators on most endpoints

Routes:
- `POST /neft/transfer` — NEFT with SQL injection vulnerability
- `POST /imps/transfer` — IMPS transfer
- `POST /rtgs/transfer` — RTGS with 2 lakh minimum
- `GET /neft/status/{txn_id}` — NEFT status check
- `GET /imps/status/{txn_id}` — IMPS status check
- `GET /upi/collect` — UPI collect request
- `POST /upi/pay` — UPI payment with OS injection
