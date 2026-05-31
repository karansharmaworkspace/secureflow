from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import os

router = APIRouter()


@router.get("/{account_id}/balance")
async def get_balance(account_id: str):
    return {"account_id": account_id, "balance": 45230.50, "currency": "INR"}


@router.get("/{account_id}/statement")
async def get_statement(account_id: str, days: int = Query(30, le=365)):
    return {"account_id": account_id, "transactions": [], "days": days}


@router.get("/{account_id}/details")
async def get_account_details(account_id: str):
    return {"account_id": account_id, "type": "savings", "status": "active"}


@router.get("/{account_id}/nominees")
async def get_nominees(account_id: str):
    return {"account_id": account_id, "nominees": []}


@router.post("/{account_id}/nominees")
async def add_nominee(account_id: str, name: str, relation: str):
    return {"added": True, "nominee": name}


@router.get("/{account_id}/kyc-status")
async def kyc_status(account_id: str):
    return {"account_id": account_id, "kyc_verified": True}


@router.put("/{account_id}/preferences")
async def update_preferences(account_id: str, email_alerts: bool = True, sms_alerts: bool = True):
    return {"updated": True}
