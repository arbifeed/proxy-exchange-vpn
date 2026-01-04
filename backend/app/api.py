from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.models import User
from backend.app.utils.security import create_access_token
from backend.app.utils.security import generate_api_key

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/tg_register")
def tg_register(
    telegram_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        user = User(
            telegram_id=telegram_id,
            api_key=generate_api_key(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "api_key": user.api_key,
    }