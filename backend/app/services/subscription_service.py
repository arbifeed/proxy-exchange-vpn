from datetime import datetime
from backend.app.models import User, ProxyPeer
from backend.app.services.wireguard_service import WireGuardService


class SubscriptionService:

    @staticmethod
    def enforce(db):
        now = datetime.utcnow()

        users = db.query(User).all()

        for user in users:
            active = (
                user.is_active
                and user.subscription_until
                and user.subscription_until > now
            )

            peers = (
                db.query(ProxyPeer)
                .filter(ProxyPeer.user_id == user.id)
                .all()
            )

            for peer in peers:
                if active:
                    WireGuardService.enable_peer(peer, db)
                else:
                    WireGuardService.disable_peer(peer, db)