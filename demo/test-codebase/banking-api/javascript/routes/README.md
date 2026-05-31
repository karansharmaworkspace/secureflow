# JavaScript Routes (Express)

Express.js route handlers for the JavaScript banking API: 10 active card endpoints + 5 zombie notification endpoints.

## Files

### cards.js — Card Management Router (45 lines, 10 routes)

Uses `express.Router()` and `module.exports`. All routes under implicit `/api/v3/cards` prefix (set in `server.js`). No auth middleware.

Routes: GET/POST for transactions, statement, block/unblock, PIN status/change, rewards, limits, international enable, EMI options.

### notifications.js — **Zombie** Legacy Notifications (36 lines, 5 routes)

Uses `express.Router()` with `/v1/` path prefix. Starts with deprecation docstring: *"DEPRECATED - notifications v1 API. All endpoints here are legacy and scheduled for removal."*

Routes: `GET /v1/history`, `POST /v1/send` (with `// TODO: migrate to v3`), `GET /v1/prefs`, `POST /v1/subscribe`, `GET /v1/templates`, `POST /v1/mock/send` (with `// test endpoint, remove before production`).

**Scanner signals:** DEPRECATED keyword, TODO comments, mock endpoint, v1 path prefix.
