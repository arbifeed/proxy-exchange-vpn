from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.app.models import User
import logging

logger = logging.getLogger(__name__)

class SubscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def activate_subscription(
        self, 
        user_id: int, 
        subscription_type: str = "premium",  # "standard" или "premium"
        days: int = 30,
        payment_id: int = None
    ) -> User:
        """
        Активирует или продлевает подписку пользователя.
        Работает с полями subscription_expires_at и subscription_type в таблице User.
        """
        try:
            # Находим пользователя
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise Exception(f"User with id {user_id} not found")
            
            # Вычисляем новую дату окончания
            now = datetime.utcnow()
            
            # Если у пользователя уже есть активная подписка - продлеваем
            if user.subscription_expires_at and user.subscription_expires_at > now:
                new_expires_at = user.subscription_expires_at + timedelta(days=days)
            else:
                # Новая подписка
                new_expires_at = now + timedelta(days=days)
            
            # Обновляем пользователя
            user.subscription_type = subscription_type
            user.subscription_expires_at = new_expires_at
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"✅ Subscription activated for user {user_id}: {subscription_type} for {days} days")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error activating subscription: {e}")
            raise
    
    async def check_subscription_status(self, user_id: int) -> dict:
        """
        Проверяет статус подписки пользователя.
        Возвращает словарь с информацией.
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return {"has_active_subscription": False, "error": "User not found"}
        
        if not user.subscription_expires_at:
            return {"has_active_subscription": False}
        
        now = datetime.utcnow()
        is_active = user.subscription_expires_at > now
        
        return {
            "has_active_subscription": is_active,
            "subscription_type": user.subscription_type,
            "expires_at": user.subscription_expires_at,
            "days_left": max((user.subscription_expires_at - now).days, 0) if is_active else 0,
            "is_premium": user.subscription_type == "premium"
        }
    
    async def deactivate_subscription(self, user_id: int) -> bool:
        """Деактивирует подписку пользователя (при отмене/просрочке)"""
        try:
            stmt = update(User).where(User.id == user_id).values(
                subscription_expires_at=None,
                subscription_type="standard"
            )
            await self.db.execute(stmt)
            await self.db.commit()
            logger.info(f"Subscription deactivated for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deactivating subscription: {e}")
            return False
        
    @staticmethod
    async def enforce(db: AsyncSession):
        """
        Фоновая задача: проверяет и деактивирует просроченные подписки.
        Вызывается при старте приложения из main.py.
        """
        try:
            from backend.app.models import User
            from sqlalchemy import select
            
            now = datetime.utcnow()
            
            # Находим пользователей с просроченной подпиской
            stmt = select(User).where(
                User.subscription_expires_at < now,
                User.subscription_type != 'standard'
            )
            result = await db.execute(stmt)
            expired_users = result.scalars().all()
            
            count = 0
            for user in expired_users:
                user.subscription_type = 'standard'
                count += 1
            
            if count > 0:
                await db.commit()
                logger.info(f"🔄 Enforced subscriptions: {count} users deactivated")
            
        except Exception as e:
            logger.error(f"❌ Error in enforce subscriptions: {e}")