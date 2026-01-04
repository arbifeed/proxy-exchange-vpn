from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading

from backend.app.core.config import settings
from backend.app.db import engine
from backend.app.models import Base

from backend.app.api import router as api_router
from backend.app.routers.proxy_router import router as proxy_router
from backend.app.routers.user_router import router as user_router
from backend.app.routers.admin_router import router as admin_router
from backend.app.tasks.subscription_checker import subscription_watcher
from backend.app.routers.payments_router import router as payments_router
from backend.app.routers.cryptobot_webhook_router import (
    router as cryptobot_webhook_router
)


from fastapi import BackgroundTasks
from backend.app.services.subscription_service import SubscriptionService
from backend.app.db import SessionLocal

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

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.on_event("startup")
def enforce_subscriptions():
    db = SessionLocal()
    try:
        SubscriptionService.enforce(db)
    finally:
        db.close()

@app.on_event("startup")
def start_background_tasks():
    threading.Thread(
        target=subscription_watcher,
        daemon=True
    ).start()