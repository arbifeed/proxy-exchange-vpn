from datetime import datetime
from time import sleep

from backend.app.db import SessionLocal
from backend.app.models import User, ProxyPeer
from backend.app.services.wireguard_service import WireGuardService


def subscription_watcher():
    while True:
        db = SessionLocal()
        try:
            now = datetime.utcnow()

            users = db.query(User).all()
            for user in users:
                expired = (
                    user.subscription_until
                    and user.subscription_until < now
                )

                peers = db.query(ProxyPeer).filter(
                    ProxyPeer.user_id == user.id
                ).all()

                for peer in peers:
                    if expired and peer.is_active:
                        WireGuardService.disable_peer(peer, db)

                    if not expired and user.is_active and not peer.is_active:
                        WireGuardService.enable_peer(peer, db)
        finally:
            db.close()

        sleep(60)  # раз в минуту
