import time
import random
import logging
from typing import Callable, Any

from app.core.exceptions import RetryableException, NonRetryableException

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
                        "retry_success",
                        extra={"attempt": attempt + 1}
                    )
                    return result

                raise RetryableException("Operation failed")

            except NonRetryableException:
                logger.error(
                    "non_retryable_error",
                    extra={"function": func.__name__}
                )
                raise 

            except RetryableException as e:
                attempt += 1

                if attempt >= self.max_retries:
                    logger.error(
                        "retry_exhausted",
                        extra={
                            "attempts": attempt,
                            "function": func.__name__,
                            "error": str(e),
                        }
                    )
                    raise 

                delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
                jitter_value = random.uniform(0, self.jitter)
                total_delay = delay + jitter_value

                logger.warning(
                    "retrying",
                    extra={
                        "attempt": attempt,
                        "delay": round(total_delay, 2),
                        "function": func.__name__,
                        "error": str(e),
                    }
                )

                time.sleep(total_delay)