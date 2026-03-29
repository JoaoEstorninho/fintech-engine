import time
import random
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


class RetryPolicy:
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        jitter: float = 0.5,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    def execute(self, func: Callable[..., Any], *args, **kwargs) -> dict:
        attempt = 0

        while attempt < self.max_retries:
            try:
                result = func(*args, **kwargs)

                if result.get("status") == "success":
                    logger.info(
                        "RetryPolicy success",
                        extra={"attempt": attempt + 1}
                    )
                    return result

                raise Exception("Operation failed")

            except Exception as e:
                attempt += 1

                if attempt >= self.max_retries:
                    logger.error(
                        "Max retries reached",
                        extra={
                            "attempts": attempt,
                            "error": str(e),
                            "function": func.__name__,
                        }
                    )
                    return {"status": "failed"}

                delay = self.base_delay * (2 ** (attempt - 1))
                delay = min(delay, self.max_delay)

                jitter_value = random.uniform(0, self.jitter)
                total_delay = delay + jitter_value

                logger.warning(
                    "Retrying operation",
                    extra={
                        "attempt": attempt,
                        "max_retries": self.max_retries,
                        "delay": round(total_delay, 2),
                        "function": func.__name__,
                        "error": str(e),
                    }
                )

                time.sleep(total_delay)