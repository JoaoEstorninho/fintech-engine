from app.repositories.payment_repository import PaymentRepository
from app.core.exceptions import NotFoundException

repo = PaymentRepository()


class GetPaymentService:

    def execute(self, payment_id: str):
        payment = repo.get(payment_id)

        if not payment:
            raise NotFoundException("Payment not found")

        return {
            "id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "provider": payment.provider,
            "retries": payment.retries
        }