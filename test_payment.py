import asyncio
import sys

sys.path.append(".")


async def test_cryptobot():
    """Тест создания инвойса в CryptoBot"""
    from backend.app.services.payments.cryptobot import crypto_provider

    # Проверяем подключение
    print("Testing CryptoBot connection...")

    # Создаем тестовый инвойс (небольшая сумма)
    invoice = await crypto_provider.create_invoice(
        amount=0.01,  # Минимальная сумма для теста
        currency="USD",
        description="Test payment",
        user_id=123456,  # Тестовый ID
    )

    if invoice:
        print(f"✅ Invoice created successfully!")
        print(f"Pay URL: {invoice.get('pay_url')}")
        print(f"Invoice ID: {invoice.get('invoice_id')}")
    else:
        print("❌ Failed to create invoice")
        print("Check your CRYPTOBOT_TOKEN in .env file")


asyncio.run(test_cryptobot())
