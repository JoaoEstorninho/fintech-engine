import logging
from app.core.retry_policy import RetryPolicy
from app.services.provider_router import ProviderRouter
from app.repositories.payment_repository import PaymentRepository
from app.core.exceptions import NotFoundException, ExternalServiceException

logger = logging.getLogger(__name__)

retry_policy = RetryPolicy(max_retries=3, base_delay=1)
router = ProviderRouter()
repo = PaymentRepository()


class ProcessPaymentService:

    def execute(self, payment_id: str):
        payment = repo.get(payment_id)

        if not payment:
            logger.error(f"Payment {payment_id} not found")
            raise NotFoundException("Payment not found")

        logger.info(
            "processing_payment",
            extra={"payment_id": payment_id}
        )

        name, provider = router.get_best_provider()

        logger.info(
            "selected_provider",
            extra={"payment_id": payment_id, "provider": name}
        )

        if self._try_provider(payment, name, provider):
            repo.update(payment)
            return

        for fallback_name, fallback_provider in router.providers.items():
            if fallback_name == name:
                continue

            logger.info(
                "trying_fallback_provider",
                extra={"payment_id": payment_id, "provider": fallback_name}
            )

            if self._try_provider(payment, fallback_name, fallback_provider):
                repo.update(payment)
                return

        payment.status = "failed"
        repo.update(payment)

        logger.error(
            "payment_failed_all_providers",
            extra={"payment_id": payment_id}
        )

        raise ExternalServiceException("All payment providers failed")

    def _try_provider(self, payment, name, provider):
        result = retry_policy.execute(provider["handler"], payment.amount)

        if result["status"] == "success":
            router.record_success(name)

            payment.status = "success"
            payment.provider = name

            logger.info(
                "payment_success",
                extra={
                    "payment_id": payment.id,
                    "provider": name
                }
            )

            return True

        logger.warning(
            "provider_failed",
            extra={
                "payment_id": payment.id,
                "provider": name
            }
        )

        router.record_failure(name)
        return False