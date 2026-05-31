# Bank API - Test endpoints

These are mock endpoints for integration testing.
Do not expose in production.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/mock/accounts")
async def mock_accounts():
    return {"accounts": [{"id": 1, "name": "Test User"}]}


@router.post("/mock/transfer")
async def mock_transfer():
    return {"status": "mock-success"}


@router.get("/stub/balance")
async def stub_balance():
    return {"balance": 99999}


@router.get("/fake/user")
async def fake_user():
    return {"name": "Fake User", "email": "test@test.com"}
