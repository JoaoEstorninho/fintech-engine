import uuid
import logging

from app.core.retry_policy import RetryPolicy
from app.services.provider_router import ProviderRouter
from app.repositories.payment_repository import PaymentRepository
from app.models.payment import Payment

logger = logging.getLogger(__name__)

retry_policy = RetryPolicy(max_retries=3, base_delay=1)
router = ProviderRouter()
repo = PaymentRepository()


class PaymentService:

    def create_payment(self, amount: float, currency: str):
        payment = Payment(
            id=str(uuid.uuid4()),
            amount=amount,
            currency=currency,
            status="pending",
            provider=None,
            retries=0
        )

        payment = repo.create(payment)

        return {
            "id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "provider": payment.provider,
            "retries": payment.retries
        }

    def process_payment(self, payment_id: str):
        payment = repo.get(payment_id)

        if not payment:
            logger.error(f"Payment {payment_id} not found in DB")
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

            repo.update(payment)
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

                repo.update(payment)
                return

            logger.warning(
                f"Fallback provider {fallback_name} failed for payment {payment_id}"
            )
            router.record_failure(fallback_name)

        payment.status = "failed"

        logger.error(f"Payment {payment_id} failed after all attempts")

        repo.update(payment)

    def get_payment(self, payment_id: str):
        payment = repo.get(payment_id)

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