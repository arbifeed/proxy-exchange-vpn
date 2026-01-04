# backend/app/routers/user_router.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.app.models import User
from backend.app.utils.security import get_current_user
from backend.app.db import get_db
from sqlalchemy.orm import Session

from backend.app.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["User"])


class RegisterDeviceSchema(BaseModel):
    device_id: str


class UnregisterDeviceSchema(BaseModel):
    device_id: str


@router.post("/device/register")
def register_device(payload: RegisterDeviceSchema, user=Depends(get_current_user)):
    device = UserService.register_device(user, payload.device_id)
    if device is None:
        raise HTTPException(status_code=403, detail="Device limit reached")
    return {"status": "ok", "device_id": device.device_id}


@router.post("/device/unregister")
def unregister_device(
    payload: UnregisterDeviceSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return UserService.unregister_device(
        db=db,
        user=user,
        device_id=payload.device_id,
    )


@router.get("/status")
def user_status(user=Depends(get_current_user)):
    return {
        "api_key": user.api_key,
        "subscription_until": user.subscription_until,
        "devices_limit": user.devices_limit,
        "active_devices": len(user.devices),
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "telegram_id": current_user.telegram_id,
        "devices_limit": current_user.devices_limit,
        "subscription_until": current_user.subscription_until,
        "is_active": current_user.is_active,
    }
