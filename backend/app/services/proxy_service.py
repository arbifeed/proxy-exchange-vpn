# backend/app/services/proxy_service.py

from sqlalchemy.orm import Session
from backend.app.crud import proxy_peer as proxy_peer_crud
from backend.app.services.vpn.wireguard import WireGuardService
from backend.app.models import Device


class ProxyService:

    def generate_proxy(
        self,
        *,
        db: Session,
        user,
        device: Device,
    ):
        peer = proxy_peer_crud.get_by_device(db, device.id)
        if peer:
            return {
                "protocol": peer.protocol,
                "config": peer.config,
            }

        wg_service = WireGuardService()
        wg_data = wg_service.generate_peer_config(device)

        # 🔥 добавляем peer на сервер
        wg_service.add_peer(wg_data)

        peer = proxy_peer_crud.create(
            db,
            user_id=user.id,
            device_id=device.id,
            protocol="wireguard",
            config=wg_data["config"],
            public_key=wg_data["public_key"],
        )

        return {
            "protocol": "wireguard",
            "config": wg_data["config"],
        }

    def revoke_proxy(
        self,
        *,
        db: Session,
        device: Device,
    ):
        peer = proxy_peer_crud.get_by_device(db, device.id)
        if not peer:
            return

        wg_service = WireGuardService()

        # 🔥 УДАЛЯЕМ PEER С СЕРВЕРА
        wg_service.remove_peer(peer.public_key)

        # 🔥 УДАЛЯЕМ ИЗ БД
        proxy_peer_crud.delete(db, peer.id)

        # (опционально)
        device.is_active = False
        db.commit()


proxy_service = ProxyService()
