from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from routes import accounts, payments, auth
from routes.legacy import v1_api, old_transfer
import uvicorn

app = FastAPI(title="Union Bank API", version="3.2.0")
security = HTTPBearer()

app.include_router(auth.router, prefix="/api/v3/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/api/v3/accounts", tags=["accounts"])
app.include_router(payments.router, prefix="/api/v3/payments", tags=["payments"])
app.include_router(v1_api.router, prefix="/api/v1", tags=["legacy-v1"])
app.include_router(old_transfer.router, prefix="/api/v1/transfer", tags=["legacy-transfer"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/v3/versions")
async def api_versions():
    return {"current": "v3", "deprecated": ["v1", "v2"], "sunset": "2025-12-31"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
