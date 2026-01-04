from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.models import Device, User
from backend.app.services.wireguard_service import WireGuardService


class DeviceService:

    @staticmethod
    def register_device(
        db: Session,
        user: User,
        device_id: str,
    ):
        # Проверяем существование
        device = (
            db.query(Device)
            .filter(Device.user_id == user.id, Device.device_id == device_id)
            .first()
        )

        if device:
            device.last_seen = datetime.utcnow()
            db.commit()
            return {
                "device_id": device.device_id,
                "wireguard_config": None,
            }

        # Проверка лимита
        if len(user.devices) >= user.devices_limit:
            raise HTTPException(status_code=403, detail="Device limit exceeded")

        # Создаём устройство
        device = Device(
            user_id=user.id,
            device_id=device_id,
        )

        db.add(device)
        db.commit()
        db.refresh(device)

        # 🔐 WireGuard peer
        peer = WireGuardService.create_peer(
            db=db,
            user=user,
            device=device,
        )

        return {
            "device_id": device.device_id,
            "wireguard_config": peer.config,
        }

    @staticmethod
    def unregister_device(db: Session, user: User, device_id: str):
        device = (
            db.query(Device)
            .filter(
                Device.device_id == device_id,
                Device.user_id == user.id,
            )
            .first()
        )

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # 1️⃣ ищем WireGuard peer
        peer = (
            db.query(ProxyPeer)
            .filter(
                ProxyPeer.device_id == device.id,
                ProxyPeer.protocol == "wireguard",
            )
            .first()
        )

        # 2️⃣ удаляем peer если есть
        if peer:
            WireGuardService.remove_peer(peer)

        # 3️⃣ удаляем устройство
        db.delete(device)
        db.commit()

        return {"status": "device removed"}

    

