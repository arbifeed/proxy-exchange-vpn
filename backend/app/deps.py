# backend/app/deps.py
from fastapi import Header, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.services.user_service import UserService
from backend.app.services.device_service import DeviceService
from backend.app.db import SessionLocal
from backend.app.models import User, Device

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db),
) -> User:
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    user = UserService.get_by_api_key(db, api_key)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not user.subscription_until or user.subscription_until < datetime.utcnow():
        raise HTTPException(status_code=402, detail="Subscription expired")

    return user


# ✅ РЕАЛЬНАЯ зависимость (для запросов)
def get_current_user_and_device(
    device_id: str = Header(..., alias="X-Device-Id"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> tuple[User, Device]:
    device = DeviceService.check_and_register_device(
        db=db,
        user=user,
        device_id=device_id,
    )
    return user, device


# ✅ ЗАГЛУШКА (ТОЛЬКО ДЛЯ SWAGGER)
def get_current_user_and_device_swagger() -> tuple[User, Device]:
    fake_user = User(
        id=1,
        api_key="swagger",
        is_active=True,
        devices_limit=1,
    )
    fake_device = Device(
        id=1,
        user_id=1,
        device_id="swagger-device",
    )
    return fake_user, fake_device

def admin_required(
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")
):
    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Admin access denied")