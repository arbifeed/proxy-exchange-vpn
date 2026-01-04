# backend/app/services/user_service.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.app.db import SessionLocal
from backend.app.models import User, Device, ProxyPeer
from backend.app.utils.security import generate_api_key
from backend.app.services.wireguard_service import WireGuardService
from fastapi import HTTPException


class UserService:
    @staticmethod
    def create_user_for_bot(
        duration_days: int = 30, devices_limit: int = 1, initial_balance: int = 0
    ):
        """
        Создать пользователя (вызывается ботом после оплаты).
        duration_days — длина подписки в днях
        devices_limit — сколько устройств выдать
        initial_balance — баланс в копейках
        """
        db: Session = SessionLocal()
        try:
            api_key = generate_api_key()
            now = datetime.utcnow()
            user = User(
                api_key=api_key,
                subscription_until=now + timedelta(days=duration_days),
                devices_limit=devices_limit,
                balance=initial_balance,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    @staticmethod
    def get_by_api_key(db: Session, api_key: str) -> User | None:
        return (
            db.query(User)
            .filter(User.api_key == api_key)
            .first()
        )

    @staticmethod
    def extend_subscription(user: User, extra_days: int):
        db: Session = SessionLocal()
        try:
            if user.subscription_until and user.subscription_until > datetime.utcnow():
                user.subscription_until = user.subscription_until + timedelta(
                    days=extra_days
                )
            else:
                user.subscription_until = datetime.utcnow() + timedelta(days=extra_days)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    @staticmethod
    def register_device(user: User, device_id: str):
        db: Session = SessionLocal()
        try:
            # текущие активные devices (count)
            current_count = db.query(Device).filter(Device.user_id == user.id).count()
            if current_count >= user.devices_limit:
                return None  # переполнение лимита — нужно обработать на уровне роутера

            # Если устройство с таким device_id уже есть — обновим last_seen
            device = (
                db.query(Device)
                .filter(Device.user_id == user.id, Device.device_id == device_id)
                .first()
            )
            if device:
                device.last_seen = datetime.utcnow()
                db.add(device)
                db.commit()
                db.refresh(device)
                return device

            # иначе создаём новое
            device = Device(user_id=user.id, device_id=device_id)
            db.add(device)
            db.commit()
            db.refresh(device)
            return device
        finally:
            db.close()
    @staticmethod
    def unregister_device(db, user, device_id: str):
        device = (
            db.query(Device)
            .filter(
                Device.user_id == user.id,
                Device.device_id == device_id,
            )
            .first()
        )

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        peer = (
            db.query(ProxyPeer)
            .filter(
                ProxyPeer.device_id == device.id,
                ProxyPeer.protocol == "wireguard",
            )
            .first()
        )

        if peer:
            WireGuardService.remove_peer(peer, db)

        db.delete(device)
        db.commit()

        return {"status": "device removed"}