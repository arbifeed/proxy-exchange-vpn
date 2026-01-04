from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.deps import (
    get_db,
    get_current_user,
    get_current_user_and_device,
    get_current_user_and_device_swagger,
)
from backend.app.services.proxy_service import proxy_service
from backend.app.models import Device, User
from backend.app.crud import device as device_crud


router = APIRouter(prefix="/proxy", tags=["Proxy"])


@router.get(
    "/generate",
    summary="Generate VPN configuration",
)
def generate_proxy(
    data=Depends(get_current_user_and_device),
    db: Session = Depends(get_db),
):
    user, device = data

    return proxy_service.generate_proxy(
        db=db,
        user=user,
        device=device,
    )


@router.get(
    "/generate",
    include_in_schema=False,
)
def generate_proxy_swagger(
    data=Depends(get_current_user_and_device_swagger),
):
    return {}


@router.get(
    "/devices",
    summary="Get my devices",
)
def my_devices(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Device)
        .filter(Device.user_id == user.id)
        .all()
    )


@router.delete(
    "/{device_id}",
    summary="Revoke VPN for device",
)
def revoke_proxy(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    device = device_crud.get(db, device_id)

    if not device or device.user_id != user.id:
        raise HTTPException(status_code=404, detail="Device not found")

    proxy_service.revoke_proxy(
        db=db,
        device=device,
    )

    return {"status": "revoked"}
