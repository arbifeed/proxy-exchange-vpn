from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading

from backend.app.core.config import settings
from backend.app.db import engine, async_session_maker
from backend.app.models import Base

from backend.app.routers.payment_create_router import router as payment_create_router
from backend.app.api import router as api_router
from backend.app.routers.proxy_router import router as proxy_router
from backend.app.routers.user_router import router as user_router
from backend.app.routers.admin_router import router as admin_router
from backend.app.tasks.subscription_checker import subscription_watcher
from backend.app.routers.payments_router import router as payments_router
from backend.app.routers.cryptobot_webhook_router import (
    router as cryptobot_webhook_router
)

from backend.app.services.subscription_service import SubscriptionService

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(proxy_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(payments_router)
app.include_router(cryptobot_webhook_router)
app.include_router(payment_create_router)

@app.on_event("startup")
async def startup_event():
    """Все startup задачи в одном асинхронном обработчике"""
    # 1. Асинхронно создаём таблицы в БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. Проверяем и исправляем подписки
    async with async_session_maker() as db:
        await SubscriptionService.enforce(db)
    
    # 3. Запускаем фоновую задачу проверки подписок
    threading.Thread(
        target=subscription_watcher,
        daemon=True
    ).start()
    
    print("✅ Application started successfully!")

@app.get("/ping")
def ping():
    return {"status": "ok"}