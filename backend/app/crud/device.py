from sqlalchemy.orm import Session
from backend.app.models import Device


def get_by_device_id(db: Session, device_id: str):
    return db.query(Device).filter(Device.device_id == device_id).first()


def count_by_user(db: Session, user_id: int) -> int:
    return db.query(Device).filter(Device.user_id == user_id).count()


def create_device(db: Session, user_id: int, device_id: str):
    device = Device(
        user_id=user_id,
        device_id=device_id,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def get_by_user_and_device_id(
    db: Session,
    user_id: int,
    device_id: str,
) -> Device | None:
    return (
        db.query(Device)
        .filter(
            Device.user_id == user_id,
            Device.device_id == device_id,
        )
        .first()
    )
