from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.deps import admin_required
from backend.app.services.admin_service import AdminService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(admin_required)],
)

@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    return AdminService.list_users(db)


@router.post("/user/{user_id}/disable")
def disable_user(user_id: int, db: Session = Depends(get_db)):
    AdminService.disable_user(db, user_id)
    return {"status": "disabled"}


@router.post("/user/{user_id}/enable")
def enable_user(user_id: int, db: Session = Depends(get_db)):
    AdminService.enable_user(db, user_id)
    return {"status": "enabled"}


@router.post("/user/{user_id}/extend")
def extend_subscription(user_id: int, days: int, db: Session = Depends(get_db)):
    AdminService.extend_subscription(db, user_id, days)
    return {"status": "extended"}
