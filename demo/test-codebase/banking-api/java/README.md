# Java Banking API (Spring Boot)

Spring Boot implementation with 9 controller methods: 4 active v3 loan endpoints + 5 zombie v1 admin endpoints.

## Directory Structure

### src/main/java/com/unionbank/api/
Main Java source code with 2 controller classes.

### src/test/
Unit tests for the Java banking API implementation (empty in this mock).

## Controller Classes

### LoanController.java — v3 Loan Management (42 lines, 4 routes)

Uses Spring annotations: `@RestController`, `@RequestMapping("/api/v3/loans")`. Methods use `@GetMapping`, `@PostMapping`, `@PathVariable`, `@RequestParam`. Returns `HashMap<String, Object>` for JSON serialization.

Routes (all v3 active):
- `GET /{loanId}/status` — Loan status + EMI remaining
- `GET /{loanId}/schedule` — EMI schedule
- `POST /{loanId}/prepayment` — Prepayment with amount param
- `GET /{loanId}/documents` — Document list

### ZombieController.java — **Zombie** v1 Admin (39 lines, 5 routes)

Javadoc: *"DEPRECATED - Legacy service endpoint. This controller is deprecated since v2 migration. TODO: remove this entire class"*

Uses Spring annotations with `@RequestMapping("/api/v1/admin")`.

Routes (all zombie candidates):
- `GET /users` — Returns `{"deprecated": true}`
- `POST /users/create` — Returns `{"legacy": true}`
- `GET /config` — Returns `{"debug": true, "version": "1.0.0"}`
- `GET /temp/health` — Returns `{"temporary": true}`
- `POST /mock/deploy` — Returns `{"mock": true}`

**Scanner detection signals:**
- Javadoc with "DEPRECATED" keyword
- `// TODO: remove this entire class` comment
- `/api/v1/` path prefix
- `/temp/`, `/mock/` path segments (temporary and mock test endpoints)
- Method names: `mockDeploy()`, `tempHealth()`
