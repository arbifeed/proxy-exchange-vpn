import requests
from backend.app.core.config import settings


class CryptoBotProvider:
    API_URL = "https://pay.crypt.bot/api"

    @classmethod
    def _headers(cls):
        return {
            "Crypto-Pay-API-Token": settings.CRYPTOBOT_TOKEN,
            "Content-Type": "application/json",
        }

    @classmethod
    def create_invoice(cls, amount_usdt: float, description: str):
        r = requests.post(
            f"{cls.API_URL}/createInvoice",
            json={
                "asset": "USDT",
                "amount": amount_usdt,
                "description": description,
            },
            headers=cls._headers(),
            timeout=10,
        )

        r.raise_for_status()
        data = r.json()

        if not data.get("ok"):
            raise RuntimeError(f"CryptoBot error: {data}")

        return data["result"]
