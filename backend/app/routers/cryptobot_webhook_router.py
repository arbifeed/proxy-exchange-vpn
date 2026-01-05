from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from backend.app.services.payments.cryptobot import crypto_provider  # Импортируем ваш экземпляр
from backend.app.services.payments.payment_service import PaymentService
from backend.app.services.subscription_service import SubscriptionService
from backend.app.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db import get_db
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook/cryptobot", tags=["cryptobot-webhook"])

@router.post("/payment")
async def handle_payment_webhook(
    request: Request, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Вебхук для CryptoBot. 
    Настройте в CryptoBot: /setWebhook https://ВАШ_NGROK_URL/webhook/cryptobot/payment
    """
    try:
        webhook_data = await request.json()
        logger.info(f"Received CryptoBot webhook: {webhook_data}")
    except Exception as e:
        logger.error(f"Failed to parse webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Запускаем обработку в фоне и сразу отвечаем CryptoBot
    background_tasks.add_task(process_webhook_background, webhook_data, db)
    return {"status": "received"}

async def process_webhook_background(webhook_data: Dict[str, Any], db: AsyncSession):
    """Фоновая обработка вебхука"""
    try:
        update_type = webhook_data.get("update_type")
        if update_type != "invoice_paid":
            logger.info(f"Ignoring webhook type: {update_type}")
            return
        
        invoice = webhook_data.get("invoice", {})
        invoice_id = invoice.get("invoice_id")
        payload = invoice.get("payload")  # user_id из create_invoice
        
        if not payload:
            logger.error(f"No payload in invoice {invoice_id}")
            return
        
        # Дополнительная проверка через API CryptoBot
        invoice_info = await crypto_provider.get_invoice(invoice_id)
        if not invoice_info or invoice_info.get("status") != "paid":
            logger.warning(f"Invoice {invoice_id} not confirmed as paid")
            return
        
        try:
            user_id = int(payload)
        except ValueError:
            logger.error(f"Invalid payload: {payload}")
            return
        
        # Обрабатываем успешный платёж
        await process_successful_payment(
            db=db,
            user_id=user_id,
            invoice_id=invoice_id,
            amount=invoice.get("amount", "0"),
            currency=invoice.get("currency", "USD")
        )
        
    except Exception as e:
        logger.error(f"Error in background webhook processing: {e}", exc_info=True)

async def process_successful_payment(
    db: AsyncSession,
    user_id: int,
    invoice_id: str,
    amount: str,
    currency: str
):
    """Обновляет данные пользователя после успешной оплаты"""
    try:
        payment_service = PaymentService(db)
        subscription_service = SubscriptionService(db)
        user_service = UserService(db)
        
        user = await user_service.get_user_by_telegram_id(user_id)
        if not user:
            logger.error(f"User {user_id} not found in database")
            return
        
        # Создаём запись о платеже
        payment = await payment_service.create_payment(
            user_id=user.id,
            amount=float(amount),
            currency=currency,
            provider="cryptobot",
            provider_payment_id=invoice_id,
            status="completed",
            description=f"Оплата через CryptoBot #{invoice_id}"
        )
        
        # Активируем премиум подписку
        await subscription_service.activate_subscription(
            user_id=user.id,
            subscription_type="premium",  # или можно определить по сумме платежа
            days=30
        )
        
        logger.info(f"✅ User {user_id} subscription activated until {subscription.expires_at}")
        
        # TODO: Отправить уведомление в Telegram бот
        # await notify_user_success(user.telegram_id, subscription.expires_at)
        
    except Exception as e:
        logger.error(f"Failed to process successful payment: {e}", exc_info=True)