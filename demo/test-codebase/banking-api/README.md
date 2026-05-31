# Union Bank API

## Running

```bash
# Python (FastAPI)
cd python && pip install -r requirements.txt && uvicorn app:app --reload

# JavaScript (Express)
cd javascript && npm install && node server.java

# Java (Spring Boot)
cd java && mvn spring-boot:run

# Go (Gin)
cd go && go run main.go
```

## API Versions

- v1: DEPRECATED - will be removed 2025-12-31
- v2: DEPRECATED - migrated to v3
- v3: Current stable

## Endpoints

### Auth
- POST /api/v3/auth/login
- POST /api/v3/auth/refresh
- POST /api/v3/auth/otp/generate
- POST /api/v3/auth/otp/verify

### Accounts
- GET /api/v3/accounts/{id}/balance
- GET /api/v3/accounts/{id}/statement
- GET /api/v3/accounts/{id}/details

### Payments
- POST /api/v3/payments/neft/transfer
- POST /api/v3/payments/imps/transfer
- POST /api/v3/payments/rtgs/transfer

### Cards
- GET /api/v3/cards/{id}/transactions
- POST /api/v3/cards/{id}/block

### Loans
- GET /api/v3/loans/{id}/status
- POST /api/v3/loans/{id}/prepayment

### Forex
- GET /api/v3/forex/rates
- POST /api/v3/forex/convert
