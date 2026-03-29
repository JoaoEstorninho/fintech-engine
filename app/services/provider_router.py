import logging
from app.providers import stripe, adyen

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
                "stats": ProviderStats()
            },
            "adyen": {
                "handler": adyen.process_payment,
                "stats": ProviderStats()
            }
        }

    def get_best_provider(self):
        name, provider = max(
            self.providers.items(),
            key=lambda p: p[1]["stats"].success_rate()
        )

        stats = provider["stats"]

        logger.info(
            "Selected provider",
            extra={
                "provider": name,
                "success": stats.success,
                "fail": stats.fail,
                "success_rate": round(stats.success_rate(), 2)
            }
        )

        return name, provider

    def record_success(self, name):
        stats = self.providers[name]["stats"]
        stats.success += 1

        logger.info(
            "Provider success recorded",
            extra={
                "provider": name,
                "success": stats.success,
                "fail": stats.fail,
                "success_rate": round(stats.success_rate(), 2)
            }
        )

    def record_failure(self, name):
        stats = self.providers[name]["stats"]
        stats.fail += 1

        logger.warning(
            "Provider failure recorded",
            extra={
                "provider": name,
                "success": stats.success,
                "fail": stats.fail,
                "success_rate": round(stats.success_rate(), 2)
            }
        )