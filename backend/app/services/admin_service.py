from datetime import datetime, timedelta
from fastapi import HTTPException

from backend.app.models import User, ProxyPeer
from backend.app.services.wireguard_service import WireGuardService


class AdminService:

    @staticmethod
    def list_users(db):
        return db.query(User).all()

    @staticmethod
    def disable_user(db, user_id: int):
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_active = False

        peers = db.query(ProxyPeer).filter(
            ProxyPeer.user_id == user.id,
            ProxyPeer.is_active == True,
        ).all()

        for peer in peers:
            WireGuardService.disable_peer(peer, db)

        db.commit()

    @staticmethod
    def enable_user(db, user_id: int):
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_active = True

        peers = db.query(ProxyPeer).filter(
            ProxyPeer.user_id == user.id,
            ProxyPeer.is_active == False,
        ).all()

        for peer in peers:
            WireGuardService.enable_peer(peer, db)

        db.commit()

    @staticmethod
    def extend_subscription(db, user_id: int, days: int):
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        now = datetime.utcnow()
        base = user.subscription_until or now

        if base < now:
            base = now

        user.subscription_until = base + timedelta(days=days)
        user.is_active = True

        db.commit()
