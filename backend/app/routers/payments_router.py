from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.utils.security import get_current_user
from backend.app.models import Payment
from backend.app.services.payments.cryptobot import CryptoBotProvider

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/cryptobot/create")
def create_cryptobot_payment(
    period_days: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    price_map = {
        30: 5,
        90: 12,
        180: 20,
        365: 35,
    }

    amount = price_map.get(period_days)
    if not amount:
        raise HTTPException(status_code=400, detail="Invalid period")

    payment = Payment(
        user_id=user.id,
        provider="cryptobot",
        amount=int(amount * 100),  # USDT * 100
        currency="USDT",
        period_days=period_days,
        status="pending",
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    invoice = CryptoBotProvider.create_invoice(
        amount_usdt=amount,
        description=f"VPN subscription {period_days} days",
    )

    payment.external_id = invoice["invoice_id"]
    db.commit()

    return {
        "pay_url": invoice["pay_url"],
        "payment_id": payment.id,
    }
