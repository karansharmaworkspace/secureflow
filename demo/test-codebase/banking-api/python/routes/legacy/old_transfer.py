"""
Legacy transfer service - DEAD CODE
Last modified: 2023-06-15
Nobody has called these endpoints in 2 years.
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/legacy")
async def legacy_transfer():
    return {"status": "legacy"}


@router.post("/old/neft")
async def old_neft():
    return {"status": "old-neft"}


@router.post("/old/rtgs")
async def old_rtgs():
    return {"status": "old-rtgs"}


@router.get("/temp/status")
async def temp_status():
    # temporary endpoint, remove me
    return {"temp": True}


@router.get("/hack/check")
async def hack_check():
    # quick hack for testing, do not use
    return {"hack": True}
