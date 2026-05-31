# Python Routes

Route handler modules for the Python banking API (FastAPI). 21 active v3 endpoints across 3 files, plus 11 zombie v1 endpoints in `legacy/`.

## Files

### accounts.py — Account Management (40 lines, 7 routes)

Uses `APIRouter()` from FastAPI. All routes use `@router.get/post/put` decorators with path parameters `{account_id}`, typed with `str`. No auth dependency applied. Validates `days` query param with `le=365`.

Routes:
- `GET /{account_id}/balance` — Returns balance/currency
- `GET /{account_id}/statement` — Transaction history
- `GET /{account_id}/details` — Type/status
- `GET /{account_id}/nominees` — Nominee list
- `POST /{account_id}/nominees` — Add nominee
- `GET /{account_id}/kyc-status` — KYC check
- `PUT /{account_id}/preferences` — Alert prefs

### auth.py — Authentication (54 lines, 6 routes)

Uses `APIRouter()`, imports `HTTPBearer` from FastAPI security (scanner should flag this pattern). Uses `jwt` and `hashlib` imports for token handling. Tracks `failed_attempts` dict for rate limiting.

Pydantic request models: `LoginRequest`, `OTPVerify`.

Routes:
- `POST /login` — 5-attempt lockout via `failed_attempts` dict
- `POST /refresh` — Token refresh
- `POST /otp/generate` — OTP send
- `POST /otp/verify` — OTP verify
- `POST /logout` — Logout
- `GET /session` — Session status

### payments.py — Payment Processing (63 lines, 8 routes)

Most complex route file. Contains deliberate security vulnerabilities that the scanner should detect as "bad patterns":
- **Line 29:** `query = f"SELECT * FROM accounts WHERE account_number = '{req.to_account}'"` — SQL injection via f-string
- **Line 62:** `os.system(f"echo UPI payment to {vpa} for {amount}")` — OS command injection
- **Line 27:** `import subprocess` (imported but unused — untidy code signal)
- No auth/security decorators on any endpoint

Routes:
- `POST /neft/transfer` — NEFT transfer (SQL injection in query)
- `POST /imps/transfer` — IMPS transfer
- `POST /rtgs/transfer` — RTGS with min amount validation
- `GET /neft/status/{txn_id}` — Status check
- `GET /imps/status/{txn_id}` — Status check
- `GET /upi/collect` — UPI collect
- `POST /upi/pay` — UPI pay (command injection)

### legacy/
Deprecated v1 API routes — the primary zombie test targets for SecureFlow discovery.
