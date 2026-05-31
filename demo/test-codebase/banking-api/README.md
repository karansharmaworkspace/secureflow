# Mock Banking API

Multi-language simulated banking API for testing SecureFlow's static analysis and discovery pipeline. Contains 4 language implementations (Python/FastAPI, Go/Gin, JavaScript/Express, Java/Spring Boot) with a mix of active v3 endpoints and deprecated v1/v2 zombie endpoints.

## Architecture

All 4 implementations share the same logical endpoint structure but use their respective framework idioms. The test-codebase serves as a realistic target for the `scan_codebase()` function in `demo/dashboard/app.py` which uses 20+ regex patterns across 7 framework types to discover API routes.

## Language Implementations

### Python/ — FastAPI Implementation

| File | Lines | Routes | Role |
|------|-------|--------|------|
| `app.py` | 28 | FastAPI app w/ 5 routers, /health, /versions | Entry point, router aggregator |
| `config.py` | 21 | N/A | Application config (hardcoded secrets) |
| `utils.py` | 34 | N/A | Health check utilities (has hacks) |
| `models/user.py` | 31 | N/A | Pydantic models (User, AccountBalance, Transaction) |
| `routes/auth.py` | 54 | 6 | Login, refresh, OTP, logout, session |
| `routes/accounts.py` | 40 | 7 | Balance, statement, details, nominees, KYC, prefs |
| `routes/payments.py` | 63 | 8 | NEFT/IMPS/RTGS transfer, UPI, status checks |
| `routes/legacy/v1_api.py` | 49 | 6 | **Zombie** — v1 accounts, transfer, balance, status |
| `routes/legacy/old_transfer.py` | 35 | 5 | **Zombie** — legacy/old/temp/hack endpoints |

Total Python routes: **32** (21 active v3 + 11 zombie v1)

### Go/ — Gin Implementation

| File | Lines | Routes | Role |
|------|-------|--------|------|
| `main.go` | 60 | 6 | Forex API (rates, convert, history, remittance, travel card, alerts) |

All Go routes are v3 active endpoints.

### JavaScript/ — Express Implementation

| File | Lines | Routes | Role |
|------|-------|--------|------|
| `server.js` | 19 | Express server w/ 2 routers + /health | Entry point |
| `routes/cards.js` | 45 | 9 | Card transactions, statement, block/unblock, PIN, rewards, limits, EMI |
| `routes/notifications.js` | 36 | 5 | **Zombie** — v1 notification endpoints (legacy, TODO, mock) |

Total JavaScript routes: **15** (9 active + 5 zombie v1 + 1 health)

### Java/ — Spring Boot Implementation

| File | Lines | Routes | Role |
|------|-------|--------|------|
| `LoanController.java` | 42 | 4 | v3 loan status, schedule, prepayment, documents |
| `ZombieController.java` | 39 | 5 | **Zombie** — v1 admin users, config, temp health, mock deploy |

Total Java routes: **9** (4 active v3 + 5 zombie v1)

## API Versions (All Languages)

- **v1:** DEPRECATED — scheduled for removal after 2025-12-31. These are the zombie candidates the SecureFlow scanner should detect. Zero auth, minimal validation, poorly documented.
- **v2:** DEPRECATED — migrated to v3. Not implemented in this mock (simulates already-removed endpoints).
- **v3:** Current stable — properly structured with auth, validation, and documentation.

## Zombie Indicators (What the Scanner Looks For)

The mock codebase deliberately includes these zombie signals:
- **Comments:** `DEPRECATED`, `TODO: remove`, `temporary endpoint`, `quick hack`, `DEAD CODE`
- **Naming:** `legacy`, `old_`, `temp/`, `hack/`, `mock/`, `stub/`, `fake/`
- **Code smell:** No auth decorators, `os.system()` calls, hardcoded secrets, `verify=False`, `SELECT *` with string interpolation
- **Version paths:** `/api/v1/*` routes that have v3 replacements

## Running

```bash
# Python (FastAPI)
cd python && pip install -r requirements.txt && uvicorn app:app --reload

# JavaScript (Express)
cd javascript && npm install && node server.js

# Java (Spring Boot)
cd java && mvn spring-boot:run

# Go (Gin)
cd go && go run main.go
```
