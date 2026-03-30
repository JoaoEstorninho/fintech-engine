import logging
from app.providers import stripe, adyen
from app.core.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class ProviderStats:
    def __init__(self):
        self.success = 0
        self.fail = 0

    def success_rate(self):
        total = self.success + self.fail
        if total == 0:
            return 1.0
        return self.success / total


class ProviderRouter:
    def __init__(self):
        self.providers = {
            "stripe": {
                "handler": stripe.process_payment,
                "stats": ProviderStats(),
                "breaker": CircuitBreaker(), 
            },
            "adyen": {
                "handler": adyen.process_payment,
                "stats": ProviderStats(),
                "breaker": CircuitBreaker(),  
            }
        }

    def get_best_provider(self):
        available = {
            name: p
            for name, p in self.providers.items()
            if p["breaker"].can_execute()
        }

        if not available:
            logger.error("All providers blocked by circuit breaker")
            available = self.providers

        name, provider = max(
            available.items(),
            key=lambda p: p[1]["stats"].success_rate()
        )

        stats = provider["stats"]

        logger.info(
            "selected_provider",
            extra={
                "provider": name,
                "success": stats.success,
                "fail": stats.fail,
                "success_rate": round(stats.success_rate(), 2),
                "circuit_state": provider["breaker"].state
            }
        )

        return name, provider

    def record_success(self, name):
        provider = self.providers[name]
        stats = provider["stats"]

        stats.success += 1
        provider["breaker"].record_success()

        logger.info(
            "provider_success_recorded",
            extra={
                "provider": name,
                "success": stats.success,
                "fail": stats.fail,
                "success_rate": round(stats.success_rate(), 2),
                "circuit_state": provider["breaker"].state
            }
        )

    def record_failure(self, name):
        provider = self.providers[name]
        stats = provider["stats"]

        stats.fail += 1
        provider["breaker"].record_failure() 

        logger.warning(
            "provider_failure_recorded",
            extra={
                "provider": name,
                "success": stats.success,
                "fail": stats.fail,
                "success_rate": round(stats.success_rate(), 2),
                "circuit_state": provider["breaker"].state
            }
        )