# Main Java Source

Main Java source directory for the Spring Boot banking API. Contains 2 controller classes under `com.unionbank.api`:

- **LoanController.java** (42 lines) — `@RestController` mapped to `/api/v3/loans`, 4 endpoints for loan status, schedule, prepayment, documents
- **ZombieController.java** (39 lines) — `@RestController` mapped to `/api/v1/admin`, 5 zombie endpoints (deprecated, unsupported, mock/temp paths)
