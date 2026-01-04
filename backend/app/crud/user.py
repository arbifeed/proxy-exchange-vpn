from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.app.models import User
from backend.app.utils.security import generate_api_key


def create_user(
    db: Session,
    devices_limit: int = 1,
    subscription_days: int | None = None,
):
    api_key = generate_api_key()

    subscription_until = None
    if subscription_days:
        subscription_until = datetime.utcnow() + timedelta(days=subscription_days)

    user = User(
        api_key=api_key,
        devices_limit=devices_limit,
        subscription_until=subscription_until,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
