from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    func,
    Text,
)
from sqlalchemy.orm import relationship
from backend.app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # 🔹 Telegram
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)

    # 🔹 Auth
    api_key = Column(String(length=128), unique=True, index=True, nullable=False)

    # 🔹 Business logic
    subscription_until = Column(DateTime, nullable=True)
    devices_limit = Column(Integer, default=1)
    balance = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # 🔹 Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    devices = relationship(
        "Device",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # ID, приходящий от клиента
    device_id = Column(String, index=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="devices")


class ProxyPeer(Base):
    __tablename__ = "proxy_peers"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, unique=True)

    protocol = Column(String(32), nullable=False)  # wireguard / vless
    is_active = Column(Boolean, default=True)

    # 🔐 WireGuard data (SOURCE OF TRUTH)
    public_key = Column(String(128), nullable=False)
    private_key = Column(String(128), nullable=False)
    address = Column(String(32), nullable=False)  # 10.10.0.X/32

    config = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    device = relationship("Device")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    provider = Column(String(32), nullable=False)
    # sbp | card | cryptobot | stars

    amount = Column(Integer, nullable=False)
    # RUB → копейки
    # USDT → центы
    # Stars → целое число

    currency = Column(String(8), nullable=False)
    # RUB | USDT | STAR

    period_days = Column(Integer, nullable=False)

    status = Column(String(16), nullable=False, default="pending")
    # pending | paid | failed | canceled

    external_id = Column(String(128), nullable=True)
    # id от агрегатора / CryptoBot / TG

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

