# Backstage — Developer Portal

Backstage v1.28.0 developer portal (single replica) in the `enforce` namespace. Provides the API catalog for discovered endpoints, ownership tracking for notification routing, and a frontend for the decommission workflow.

## Files

### backstage-deployment.yaml — Backstage + DB (126 lines)

**2 Deployments + 1 ConfigMap:**

**`backstage` (Backstage Server):**
- Image: `backstage:1.28.0` (custom-built)
- Port: 7007
- Env: POSTGRES_HOST/PORT/USER/PASSWORD (backstage-db), APP_CONFIG_backend_baseUrl
- Config: Mounted from ConfigMap `backstage-config` at `/opt/app/app-config.local.yaml`

**`backstage-db` (PostgreSQL 16):**
- Image: `postgres:16-alpine`
- Env: POSTGRES_USER=backstage, PASSWORD=backstage, DB=backstage
- Port: 5432

**ConfigMap `backstage-config` — App Configuration:**
- `app.title`: "Zombie API Platform"
- `organization.name`: "Union Bank of India"
- `backend`: Database connection to backstage-db, port 7007
- `catalog.rules`: Allows APIEntity, Component, Domain, System, Resource types
- `catalog.providers.zombieApiProvider`: Scans for `catalog-info.yaml` files every 5 minutes (frequency PT5M, timeout PT30S) — auto-discovers API entities created by the frontend-analyzer and decommission workflow

**Service:** ClusterIP exposing port 7007.
