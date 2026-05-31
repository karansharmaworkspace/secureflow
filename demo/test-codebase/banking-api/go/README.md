# Go Banking API (Gin)

Go/Gin implementation of the simulated banking API. Provides 6 Forex API endpoints in a single `main.go` file. All routes are active v3 endpoints.

## Files

### main.go — Forex API Server (60 lines)

Uses `github.com/gin-gonic/gin` for HTTP routing. Single-file implementation with all handlers defined in `main()` using Gin's `r.GET/POST()` pattern.

Routes (6 total, all v3 active):
- `GET /api/v3/forex/rates` — Returns exchange rates (USD 83.25, EUR 90.10, GBP 105.50, JPY 0.55)
- `POST /api/v3/forex/convert` — Currency conversion
- `GET /api/v3/forex/history` — Historical rate lookup
- `POST /api/v3/forex/remittance` — Initiate remittance
- `GET /api/v3/forex/travel-card/load` — Load travel card
- `GET /api/v3/forex/alerts` — Rate alert subscriptions

Handler pattern: `func name(c *gin.Context)` → `c.JSON(http.StatusOK, gin.H{...})`. No authentication middleware, no validation logic — designed as simple stubs for scanner testing.

### handlers/
Empty directory — all Go handlers are in `main.go`.
