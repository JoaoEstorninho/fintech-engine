import logging
import json
from fastapi import APIRouter, Header

from app.tasks.payment_tasks import process_payment_task
from app.core.redis_client import redis_client
from app.services.use_cases.create_payment import CreatePaymentService
from app.services.use_cases.get_payment import GetPaymentService
from app.core.exceptions import ValidationException
from app.models.schemas import PaymentRequest, PaymentResponse
from app.models.responses import ApiResponse
from app.core.db import SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
def health_check():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}


@router.post("/payments", response_model=ApiResponse[PaymentResponse])
def create_payment(
    payment: PaymentRequest,
    idempotency_key: str = Header(None)
):

    logger.info(
        "incoming_payment_request",
        extra={
            "amount": payment.amount,
            "currency": payment.currency,
            "idempotency_key": idempotency_key
        }
    )

    if not idempotency_key:
        logger.warning("missing_idempotency_key")
        raise ValidationException("Missing Idempotency-Key header")

    cached = redis_client.get(idempotency_key)

    if cached:
        logger.info(
            "returning_cached_payment",
            extra={"idempotency_key": idempotency_key}
        )

        return ApiResponse[PaymentResponse](
            success=True,
            data=PaymentResponse(**json.loads(cached))
        )

    create_service = CreatePaymentService()
    payment_obj = create_service.execute(payment.amount, payment.currency)

    logger.info(
        "payment_created",
        extra={
            "payment_id": payment_obj.id,
            "idempotency_key": idempotency_key
        }
    )

    process_payment_task.delay(payment_obj.id)

    logger.info(
        "payment_task_dispatched",
        extra={"payment_id": payment_obj.id}
    )

    redis_client.set(
        idempotency_key,
        json.dumps(payment_obj.model_dump(mode="json")),
        ex=3600
    )

    return ApiResponse[PaymentResponse](
        success=True,
        data=payment_obj
    )


@router.get("/payments/{payment_id}", response_model=ApiResponse[PaymentResponse])
def get_payment(payment_id: str):

    logger.info(
        "fetching_payment",
        extra={"payment_id": payment_id}
    )

    get_service = GetPaymentService()
    payment = get_service.execute(payment_id)

    logger.info(
        "payment_retrieved",
        extra={
            "payment_id": payment_id,
            "status": payment.status
        }
    )

    return ApiResponse[PaymentResponse](
        success=True,
        data=payment
    )