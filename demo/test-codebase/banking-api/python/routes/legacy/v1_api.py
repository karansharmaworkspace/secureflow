"""
DEPRECATED - This entire file is legacy v1 API.
Scheduled for removal after 2025-12-31.
Do NOT add new endpoints here.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter()


@router.get("/accounts")
async def list_accounts_v1():
    # TODO: remove this, use v3
    return {"accounts": []}


@router.get("/accounts/{id}")
async def get_account_v1(id: int):
    # legacy endpoint, no auth check
    return {"id": id, "name": "Legacy Account"}


@router.post("/transfer")
async def transfer_v1(from_acc: str, to_acc: str, amount: float):
    # old transfer, no validation
    return {"status": "ok"}


@router.get("/balance")
async def balance_v1(account: str):
    # deprecated, use v3/accounts/{id}/balance
    return {"balance": 0}


@router.get("/status")
async def status_v1():
    return {"api_version": "v1", "status": "deprecated"}


@router.get("/version")
async def version_v1():
    return {"version": "1.0.0", "deprecated": True}


@router.post("/mock/payment")
async def mock_payment():
    # test endpoint, should not be in production
    return {"mock": True, "amount": 100}
