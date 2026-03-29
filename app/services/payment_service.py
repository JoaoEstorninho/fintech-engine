import uuid
import logging
import json

from app.core.redis_client import redis_client
from app.core.retry_policy import RetryPolicy
from app.services.provider_router import ProviderRouter
from app.core.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

retry_policy = RetryPolicy(max_retries=3, base_delay=1)
stripe_breaker = CircuitBreaker()
adyen_breaker = CircuitBreaker()
router = ProviderRouter()


class PaymentService:

    def create_payment(self, amount: float, currency: str):
        payment_id = str(uuid.uuid4())

        payment = {
            "id": payment_id,
            "amount": amount,
            "currency": currency,
            "status": "pending",
            "provider": None,
            "retries": 0
        }

        redis_client.set(
            f"payment:{payment_id}",
            json.dumps(payment)
        )

        return payment

    def process_payment(self, payment_id: str):
        data = redis_client.get(f"payment:{payment_id}")

        if not data:
            logger.error(f"Payment {payment_id} not found in Redis")
            return

        payment = json.loads(data)

        logger.info(f"Processing payment {payment_id}")

        name, provider = router.get_best_provider()

        logger.info(f"Selected provider: {name}")

        result = retry_policy.execute(provider["handler"], payment["amount"])

        if result["status"] == "success":
            router.record_success(name)

            payment["status"] = "success"
            payment["provider"] = name

            logger.info(f"Payment {payment_id} succeeded via {name}")

            redis_client.set(
                f"payment:{payment_id}",
                json.dumps(payment)
            )
            return

        logger.warning(f"Provider {name} failed for payment {payment_id}")
        router.record_failure(name)

        for fallback_name, fallback_provider in router.providers.items():
            if fallback_name == name:
                continue

            logger.info(f"Trying fallback provider: {fallback_name}")

            result = retry_policy.execute(
                fallback_provider["handler"],
                payment["amount"]
            )

            if result["status"] == "success":
                router.record_success(fallback_name)

                payment["status"] = "success"
                payment["provider"] = fallback_name

                logger.info(
                    f"Payment {payment_id} succeeded via fallback {fallback_name}"
                )

                redis_client.set(
                    f"payment:{payment_id}",
                    json.dumps(payment)
                )
                return

            logger.warning(
                f"Fallback provider {fallback_name} failed for payment {payment_id}"
            )
            router.record_failure(fallback_name)

        payment["status"] = "failed"

        logger.error(f"Payment {payment_id} failed after all attempts")

        redis_client.set(
            f"payment:{payment_id}",
            json.dumps(payment)
        )

    def get_payment(self, payment_id: str):
        data = redis_client.get(f"payment:{payment_id}")

        if not data:
            return None

        return json.loads(data)