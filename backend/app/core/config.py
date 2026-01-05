from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from typing import ClassVar
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Proxy Service"
    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"
    CRYPTOBOT_TOKEN: str
    CRYPTOBOT_WEBHOOK_SECRET: str

    # WireGuard server
    WG_SERVER_PUBLIC_KEY: str
    WG_SERVER_ENDPOINT: str
    WG_SERVER_ALLOWED_IPS: str = "0.0.0.0/0"
    WG_NETWORK: str = "10.10.0.0/24"

    ADMIN_API_KEY: str

    BASE_WEBHOOK_URL: str = "http://localhost:8000" 
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    BOT_TOKEN: ClassVar[str] = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ADMIN_IDS: ClassVar[list] = [123456789]  # Ваш ID в Telegram

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid",   # 🔒 правильно
    )
settings = Settings()
