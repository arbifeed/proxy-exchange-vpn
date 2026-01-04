from sqlalchemy.orm import Session
from backend.app.models import Payment, User, ProxyPeer
from backend.app.services.payments.cryptobot import CryptoBotProvider
from datetime import timedelta, datetime
from backend.app.services.wireguard_service import WireGuardService


class PaymentService:

    @staticmethod
    def create_cryptobot_payment(db, user_id: int, amount: float):
        payment = Payment(
            user_id=user_id,
            provider="cryptobot",
            amount=amount,
            currency="USDT",
            status="pending",
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        invoice = CryptoBotProvider.create_invoice(
            amount=amount,
            asset="USDT",
            payload=f"payment_id:{payment.id}",
        )

        payment.external_id = str(invoice["invoice_id"])
        db.commit()

        return {
            "payment_id": payment.id,
            "pay_url": invoice["pay_url"],
        }
    
    @staticmethod
    def on_payment_success(db: Session, payment: Payment):
        user = db.query(User).get(payment.user_id)
        if not user:
            return

        now = datetime.utcnow()
        base = user.subscription_until or now
        if base < now:
            base = now

        # ✅ используем period_days из платежа
        user.subscription_until = base + timedelta(days=payment.period_days)
        user.is_active = True

        peers = (
            db.query(ProxyPeer)
            .filter(
                ProxyPeer.user_id == user.id,
                ProxyPeer.protocol == "wireguard",
                ProxyPeer.is_active == False,
            )
            .all()
        )

        for peer in peers:
            WireGuardService.enable_peer(peer, db)

        db.commit()
