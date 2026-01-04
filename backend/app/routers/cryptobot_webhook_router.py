from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session

from backend.app.db import SessionLocal
from backend.app.models import Payment, User
from backend.app.services.payments.cryptobot_webhook import (
    verify_cryptobot_signature,
)

router = APIRouter(
    prefix="/webhooks/cryptobot",
    tags=["Webhooks"],
)

@router.post("")
async def cryptobot_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("Crypto-Pay-Signature")

    if not signature or not verify_cryptobot_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()

    # интересует только факт оплаты
    if payload.get("update_type") != "invoice_paid":
        return {"status": "ignored"}

    invoice = payload["payload"]
    invoice_id = str(invoice["invoice_id"])

    db: Session = SessionLocal()

    try:
        payment = db.query(Payment).filter(
            Payment.provider == "cryptobot",
            Payment.external_id == invoice_id,
        ).first()

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        if payment.status == "paid":
            return {"status": "already_processed"}

        payment.status = "paid"
        payment.paid_at = datetime.utcnow()

        user = db.query(User).get(payment.user_id)
        user.is_active = True

        # если есть подписка
        if hasattr(user, "subscription_until"):
            user.subscription_until = max(
                user.subscription_until or datetime.utcnow(),
                datetime.utcnow(),
            )

        db.commit()

    finally:
        db.close()

    return {"status": "ok"}
