from app.core.celery_app import celery_app
from app.services.use_cases.process_payment import ProcessPaymentService

service = ProcessPaymentService()


@celery_app.task(name="app.tasks.process_payment")
def process_payment_task(payment_id: str):
    service.execute(payment_id)