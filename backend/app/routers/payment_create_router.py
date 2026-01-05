from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db import get_db
from backend.app.services.payments.cryptobot import crypto_provider
from backend.app.services.subscription_service import SubscriptionService
from backend.app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payments", tags=["payments"])

@router.post("/create")
async def create_payment(
    user_id: int,
    tariff: str = "premium",
    period: str = "1month",
    db: AsyncSession = Depends(get_db)
):
    """
    Создаёт платёж для пользователя.
    """
    # Определяем цену по тарифу и периоду
    prices = {
        "premium": {"1month": 9.99, "3month": 24.99, "1year": 89.99},
        "standard": {"1month": 4.99, "3month": 12.99, "1year": 44.99},
    }
    
    amount = prices.get(tariff, {}).get(period, 9.99)
    days = {"1month": 30, "3month": 90, "1year": 365}[period]
    
    # Создаём инвойс в CryptoBot
    invoice = await crypto_provider.create_invoice(
        amount=amount,
        currency="USD",
        description=f"VPN {tariff} {period}",
        user_id=user_id
    )
    
    if not invoice:
        raise HTTPException(status_code=500, detail="Failed to create invoice")
    
    return {
        "invoice_url": invoice.get("pay_url"),
        "invoice_id": invoice.get("invoice_id"),
        "amount": amount,
        "status": "created",
        "user_id": user_id
    }