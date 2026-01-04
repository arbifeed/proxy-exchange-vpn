from sqlalchemy.orm import Session
from backend.app.models import ProxyPeer


def get_by_device(db: Session, device_id: int) -> ProxyPeer | None:
    return db.query(ProxyPeer).filter(ProxyPeer.device_id == device_id).first()


def create(
    db: Session,
    *,
    user_id: int,
    device_id: int,
    protocol: str,
    config: str,
) -> ProxyPeer:
    peer = ProxyPeer(
        user_id=user_id,
        device_id=device_id,
        protocol=protocol,
        config=config,
    )
    db.add(peer)
    db.commit()
    db.refresh(peer)
    return peer

def delete(db: Session, peer):
    db.delete(peer)
    db.commit()