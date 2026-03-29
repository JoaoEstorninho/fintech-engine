from app.core.celery_app import celery_app
from app.services.payment_service import PaymentService

service = PaymentService()


@celery_app.task(name="app.tasks.process_payment")
def process_payment_task(payment_id: str):
    service.process_payment(payment_id)