from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    account_number: str
    ifsc_code: str
    kyc_status: str
    created_at: datetime
    is_active: bool = True


class AccountBalance(BaseModel):
    account_number: str
    balance: float
    currency: str = "INR"
    last_updated: datetime


class Transaction(BaseModel):
    id: int
    from_account: str
    to_account: str
    amount: float
    status: str
    timestamp: datetime
