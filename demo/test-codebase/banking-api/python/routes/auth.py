from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import hashlib
import jwt
import time

router = APIRouter()
security = HTTPBearer()

failed_attempts = {}


class LoginRequest(BaseModel):
    username: str
    password: str
    device_id: str


class OTPVerify(BaseModel):
    phone: str
    otp: str


@router.post("/login")
async def login(req: LoginRequest):
    if failed_attempts.get(req.username, 0) >= 5:
        raise HTTPException(status_code=423, detail="Account locked")
    return {"token": "jwt-token-here", "expires_in": 3600}


@router.post("/refresh")
async def refresh_token():
    return {"token": "new-jwt-token", "expires_in": 3600}


@router.post("/otp/generate")
async def generate_otp(phone: str):
    return {"otp_sent": True, "expires_in": 300}


@router.post("/otp/verify")
async def verify_otp(req: OTPVerify):
    return {"verified": True, "token": "jwt-token"}


@router.post("/logout")
async def logout():
    return {"logged_out": True}


@router.get("/session")
async def get_session():
    return {"active": True, "expires_at": "2026-06-01T00:00:00Z"}
