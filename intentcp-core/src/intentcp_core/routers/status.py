# src/intentcp_core/routers/status.py
from fastapi import APIRouter, HTTPException
from ..services.tuya_client import tuya_client

router = APIRouter(prefix="/status", tags=["status"])


@router.get("/")
async def status_root():
    return {"ok": True, "service": "intentcp-core", "scope": "status"}


@router.get("/tuya-test/{device_id}")
async def tuya_test(device_id: str):
    try:
        status = tuya_client.get_status(device_id)
        return {
            "ok": True,
            "device_id": device_id,
            "status": status,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")