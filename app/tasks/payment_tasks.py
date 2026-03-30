from app.core.celery_app import celery_app
from app.services.use_cases.process_payment import ProcessPaymentService
import logging

logger = logging.getLogger(__name__)


@celery_app.task()
def process_payment_task(payment_id: str):
    logger.info(f"TASK RECEIVED: {payment_id}")

    try:
        service = ProcessPaymentService()
        service.execute(payment_id)

        logger.info(f"TASK COMPLETED: {payment_id}")

    except Exception as e:
        logger.error(f"TASK FAILED: {payment_id} - {str(e)}", exc_info=True)
        raise