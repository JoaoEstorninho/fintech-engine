import time
import logging

logger = logging.getLogger(__name__)


class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_time=5):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"

    def can_execute(self):
        if self.state == "OPEN":
            elapsed = time.time() - self.last_failure_time

            if elapsed > self.recovery_time:
                logger.info(
                    "Circuit HALF-OPEN — testing provider",
                    extra={
                        "state": self.state,
                        "failure_count": self.failure_count
                    }
                )
                self.state = "HALF_OPEN"
                return True

            logger.warning(
                "Circuit OPEN — skipping execution",
                extra={
                    "state": self.state,
                    "failure_count": self.failure_count,
                    "time_since_last_failure": round(elapsed, 2)
                }
            )
            return False

        return True

    def record_success(self):
        logger.info(
            "Circuit CLOSED — provider healthy",
            extra={
                "previous_failures": self.failure_count
            }
        )

        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        logger.warning(
            "Circuit failure recorded",
            extra={
                "failure_count": self.failure_count,
                "threshold": self.failure_threshold
            }
        )

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

            logger.error(
                "Circuit OPEN — provider blocked",
                extra={
                    "failure_count": self.failure_count,
                    "threshold": self.failure_threshold
                }
            )