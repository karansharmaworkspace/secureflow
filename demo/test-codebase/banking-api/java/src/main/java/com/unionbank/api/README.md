# Java API Controllers (Spring Boot)

Two Spring Boot controllers in the `com.unionbank.api` package: `LoanController` (4 active v3 endpoints) and `ZombieController` (5 zombie v1 endpoints — deprecated admin routes).

## Files

### LoanController.java — Loan Management (42 lines, 4 routes)

Spring `@RestController` mapped to `/api/v3/loans`. Returns `HashMap<String, Object>` with manual result construction.

Routes: GET status, GET schedule, POST prepayment, GET documents — all using `@PathVariable String loanId`.

### ZombieController.java — **Zombie** v1 Admin (39 lines, 5 routes)

Spring `@RestController` mapped to `/api/v1/admin`. Javadoc explicitly marks it as DEPRECATED with `TODO: remove this entire class`.

Routes: GET users (returns deprecated flag), POST create user, GET config (debug mode), GET temp health, POST mock deploy.

**Scanner signals:** DEPRECATED javadoc, TODO comment, v1 path, temp/mock paths, debug=true in response.
