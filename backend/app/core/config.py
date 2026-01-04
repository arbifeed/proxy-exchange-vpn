from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "Proxy Service"
    DATABASE_URL: str = "sqlite:///./dev.db"
    CRYPTOBOT_TOKEN: str
    CRYPTOBOT_WEBHOOK_SECRET: str

    # WireGuard server
    WG_SERVER_PUBLIC_KEY: str
    WG_SERVER_ENDPOINT: str
    WG_SERVER_ALLOWED_IPS: str = "0.0.0.0/0"
    WG_NETWORK: str = "10.10.0.0/24"

    admin_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid",   # 🔒 правильно
    )
settings = Settings()
