# JavaScript Banking API (Express)

Node.js/Express.js implementation with 15 routes: 9 active card endpoints (v3) + 5 zombie notification endpoints (v1) + 1 health check.

## Files

### server.js — Express Server (19 lines)

Creates Express app with `express.json()` middleware. Mounts 2 routers:
- `cardsRouter` at `/api/v3/cards` — 9 card management endpoints
- `notificationsRouter` at `/api/v3/notifications` — 5 legacy v1 notification endpoints

Exposes `GET /health` returning `{"status": "ok", "version": "3.2.0"}`. Listens on `process.env.PORT || 3000`.

### routes/cards.js — Card Management Router (45 lines, 9 routes)

All routes use Express `Router` pattern with path parameters `:cardId`. No auth middleware applied.

Routes (all v3 active):
- `GET /:cardId/transactions` — Transaction list
- `GET /:cardId/statement` — Card statement
- `POST /:cardId/block` — Block card
- `POST /:cardId/unblock` — Unblock card
- `GET /:cardId/pin/status` — PIN status check
- `POST /:cardId/pin/change` — PIN change
- `GET /:cardId/rewards` — Rewards points (12500)
- `GET /:cardId/limits` — Daily (50K) and monthly (10L) limits
- `POST /:cardId/international/enable` — International usage enable
- `GET /:cardId/emi/options` — EMI plan availability

### routes/notifications.js — **Zombie** Legacy Notifications (36 lines, 5 routes)

Starts with docstring: *"DEPRECATED - notifications v1 API. All endpoints here are legacy and scheduled for removal."* All routes use `/v1/` prefix.

Routes (all zombie candidates):
- `GET /v1/history` — Returns `{"deprecated": true}`
- `POST /v1/send` — `# TODO: migrate to v3` — **Scanner detects TODO comment**
- `GET /v1/prefs` — Notification preferences
- `POST /v1/subscribe` — Subscribe to notifications
- `GET /v1/templates` — Notification templates
- `POST /v1/mock/send` — `# test endpoint, remove before production` — **Scanner detects mock+hack signal**

**Scanner detection signals:**
- Docstring with "DEPRECATED" keyword
- `# TODO: migrate to v3` comment
- `# test endpoint, remove before production` comment
- `/v1/` path prefix (legacy version)
- `/mock/` path segment
