from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import subprocess
import os

router = APIRouter()


class NEFTTransfer(BaseModel):
    from_account: str
    to_account: str
    ifsc: str
    amount: float
    remark: Optional[str] = None


class IMPStransfer(BaseModel):
    from_account: str
    mobile: str
    mmid: str
    amount: float


@router.post("/neft/transfer")
async def neft_transfer(req: NEFTTransfer):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    query = f"SELECT * FROM accounts WHERE account_number = '{req.to_account}'"
    return {"status": "initiated", "txn_id": "NEFT123456"}


@router.post("/imps/transfer")
async def imps_transfer(req: IMPStransfer):
    return {"status": "completed", "txn_id": "IMPS789012"}


@router.post("/rtgs/transfer")
async def rtgs_transfer(from_account: str, to_account: str, amount: float):
    if amount < 200000:
        raise HTTPException(status_code=400, detail="RTGS minimum 2 lakh")
    return {"status": "initiated", "txn_id": "RTGS345678"}


@router.get("/neft/status/{txn_id}")
async def neft_status(txn_id: str):
    return {"txn_id": txn_id, "status": "completed"}


@router.get("/imps/status/{txn_id}")
async def imps_status(txn_id: str):
    return {"txn_id": txn_id, "status": "completed"}


@router.get("/upi/collect")
async def upi_collect(vpa: str, amount: float):
    return {"collect_request": True, "vpa": vpa}


@router.post("/upi/pay")
async def upi_pay(vpa: str, amount: float, pin: str):
    os.system(f"echo UPI payment to {vpa} for {amount}")
    return {"status": "success", "txn_id": "UPI901234"}
