import json
import hmac
import hashlib

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.core.config import settings
from backend.app.models import Payment
from backend.app.services.payments.payment_service import PaymentService

router = APIRouter(tags=["Payments"])


def verify_cryptobot_signature(body: bytes, signature: str) -> bool:
    expected = hmac.new(
        settings.CRYPTOBOT_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


@router.post("/payments/cryptobot/webhook")
async def cryptobot_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    # 1️⃣ читаем сырое тело
    body = await request.body()

    signature = request.headers.get("Crypto-Pay-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="No signature")

    # 2️⃣ проверяем подпись
    if not verify_cryptobot_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 3️⃣ парсим JSON
    data = json.loads(body)

    if data.get("update_type") != "invoice_paid":
        return {"status": "ignored"}

    invoice = data.get("payload")
    if not invoice:
        raise HTTPException(status_code=400, detail="No payload")

    external_id = str(invoice.get("invoice_id"))
    if not external_id:
        raise HTTPException(status_code=400, detail="No invoice_id")

    payment = (
        db.query(Payment)
        .filter(
            Payment.provider == "cryptobot",
            Payment.external_id == external_id,
        )
        .first()
    )

    # Повторный webhook — нормальная ситуация
    if not payment:
        return {"status": "payment_not_found"}

    if payment.status == "paid":
        return {"status": "already_processed"}

    # 4️⃣ фиксируем платёж
    payment.status = "paid"
    db.commit()

    # 5️⃣ бизнес-логика
    PaymentService.on_payment_success(db, payment)

    return {"status": "ok"}

