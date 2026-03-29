import logging
import json
from fastapi import APIRouter, Header, HTTPException, BackgroundTasks

from app.core.redis_client import redis_client
from app.models.schemas import PaymentRequest
from app.services.payment_service import PaymentService

logger = logging.getLogger(__name__)

router = APIRouter()
service = PaymentService()


@router.post("/payments")
def create_payment(
    payment: PaymentRequest,
    background_tasks: BackgroundTasks,
    idempotency_key: str = Header(None)
):

    logger.info(
        "Incoming payment request",
        extra={
            "amount": payment.amount,
            "currency": payment.currency,
            "idempotency_key": idempotency_key
        }
    )

    if not idempotency_key:
        logger.warning("Missing Idempotency-Key header")
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key")

    cached = redis_client.get(idempotency_key)

    if cached:
        logger.info(
            "Returning cached response",
            extra={"idempotency_key": idempotency_key}
        )

        return {
            "cached": True,
            "result": json.loads(cached)
        }

    payment_obj = service.create_payment(payment.amount, payment.currency)

    logger.info(
        "Payment created and scheduled for processing",
        extra={
            "payment_id": payment_obj["id"],
            "idempotency_key": idempotency_key
        }
    )

    background_tasks.add_task(service.process_payment, payment_obj["id"])

    redis_client.set(
        idempotency_key,
        json.dumps(payment_obj),
        ex=3600 
    )

    return {
        "cached": False,
        "result": payment_obj
    }


@router.get("/payments/{payment_id}")
def get_payment(payment_id: str):

    logger.info(
        "Fetching payment",
        extra={"payment_id": payment_id}
    )

    payment = service.get_payment(payment_id)

    if not payment:
        logger.warning(
            "Payment not found",
            extra={"payment_id": payment_id}
        )
        raise HTTPException(status_code=404, detail="Payment not found")

    logger.info(
        "Payment retrieved",
        extra={
            "payment_id": payment_id,
            "status": payment["status"]
        }
    )

    return payment