import httpx
import logging
from typing import Optional, Dict, Any
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class CryptoBotProvider:
    """Провайдер для работы с CryptoBot API (исправленная версия)"""
    
    def __init__(self):
        self.api_url = "https://pay.crypt.bot/api"
        # Используем вашу переменную из .env
        self.token = settings.CRYPTOBOT_TOKEN
        self.headers = {
            "Crypto-Pay-API-Token": self.token,
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def create_invoice(
        self,
        amount: float,
        currency: str = "USD",
        description: str = "VPN Subscription",
        user_id: int = None
    ) -> dict:
        """
        Создаёт счёт в CryptoBot.
    
        Args:
            amount: Сумма (например, 10.0 для 10 USD)
            currency: Валюта (USD, EUR, RUB, USDT, etc.)
            description: Описание счёта
            user_id: ID пользователя в Telegram для привязки
    
        Returns:
            Словарь с данными счёта или None при ошибке
        """
        payload = {
            "amount": str(amount),
            "currency": currency.upper(),
            "description": description[:1024],  # Ограничение CryptoBot
        }
    
        if user_id:
            payload["payload"] = str(user_id)
            # После оплаты пользователь вернётся в бота
            payload["paid_btn_url"] = f"https://t.me/your_bot_username?start=paid_{user_id}"
            payload["paid_btn_name"] = "open_bot"
    
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/createInvoice",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
            
                if data.get("ok"):
                    logger.info(f"Invoice created: {data['result']['invoice_id']} for user {user_id}")
                    return data["result"]
                else:
                    logger.error(f"CryptoBot API error: {data}")
                    return None
                
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    async def get_invoice_status(self, invoice_id: str) -> dict:
        """
        Проверяет статус счёта по ID.
    
        Args:
            invoice_id: ID счёта в CryptoBot
    
        Returns:
            Словарь с информацией о счёте или None
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.api_url}/getInvoices",
                    headers=self.headers,
                    params={"invoice_ids": invoice_id}
                )
                response.raise_for_status()
                data = response.json()
            
                if data.get("ok") and data.get("result", {}).get("items"):
                    return data["result"]["items"][0]
                return None
            
        except Exception as e:
            logger.error(f"Failed to get invoice status: {e}")
            return None

    async def get_exchange_rates(self) -> list:
        """
        Получает текущие курсы обмена в CryptoBot.
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.api_url}/getExchangeRates",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                return data.get("result", []) if data.get("ok") else []
        except Exception as e:
            logger.error(f"Failed to get exchange rates: {e}")
            return []

# Создаём экземпляр провайдера (как у вас, вероятно, уже было)
crypto_provider = CryptoBotProvider()