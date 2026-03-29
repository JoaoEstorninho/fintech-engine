import uuid
import logging

from app.core.retry_policy import RetryPolicy
from app.services.provider_router import ProviderRouter
from app.core.circuit_breaker import CircuitBreaker
from app.core.db import SessionLocal
from app.models.payment import Payment

logger = logging.getLogger(__name__)

retry_policy = RetryPolicy(max_retries=3, base_delay=1)
router = ProviderRouter()


class PaymentService:

    def create_payment(self, amount: float, currency: str):
        db = SessionLocal()

        payment = Payment(
            id=str(uuid.uuid4()),
            amount=amount,
            currency=currency,
            status="pending",
            provider=None,
            retries=0
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)
        db.close()

        return {
            "id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "provider": payment.provider,
            "retries": payment.retries
        }

    def process_payment(self, payment_id: str):
        db = SessionLocal()

        payment = db.query(Payment).filter(Payment.id == payment_id).first()

        if not payment:
            logger.error(f"Payment {payment_id} not found in DB")
            db.close()
            return

        logger.info(f"Processing payment {payment_id}")

        name, provider = router.get_best_provider()

        logger.info(f"Selected provider: {name}")

        result = retry_policy.execute(provider["handler"], payment.amount)

        if result["status"] == "success":
            router.record_success(name)

            payment.status = "success"
            payment.provider = name

            logger.info(f"Payment {payment_id} succeeded via {name}")

            db.commit()
            db.close()
            return

        logger.warning(f"Provider {name} failed for payment {payment_id}")
        router.record_failure(name)

        for fallback_name, fallback_provider in router.providers.items():
            if fallback_name == name:
                continue

            logger.info(f"Trying fallback provider: {fallback_name}")

            result = retry_policy.execute(
                fallback_provider["handler"],
                payment.amount
            )

            if result["status"] == "success":
                router.record_success(fallback_name)

                payment.status = "success"
                payment.provider = fallback_name

                logger.info(
                    f"Payment {payment_id} succeeded via fallback {fallback_name}"
                )

                db.commit()
                db.close()
                return

            logger.warning(
                f"Fallback provider {fallback_name} failed for payment {payment_id}"
            )
            router.record_failure(fallback_name)

        payment.status = "failed"

        logger.error(f"Payment {payment_id} failed after all attempts")

        db.commit()
        db.close()

    def get_payment(self, payment_id: str):
        db = SessionLocal()

        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        db.close()

        if not payment:
            return None

        return {
            "id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "provider": payment.provider,
            "retries": payment.retries
        }