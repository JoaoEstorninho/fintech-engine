import uuid
from app.models.payment import Payment
from app.repositories.payment_repository import PaymentRepository
from app.core.exceptions import ValidationException
from app.models.schemas import PaymentResponse

repo = PaymentRepository()

ALLOWED_CURRENCIES = {"EUR", "USD", "GBP"}
MAX_AMOUNT = 10000


class CreatePaymentService:

    def execute(self, amount: float, currency: str):
        self._validate(amount, currency)

        payment = Payment(
            id=str(uuid.uuid4()),
            amount=amount,
            currency=currency,
            status="pending",
            provider=None,
            retries=0
        )

        payment = repo.create(payment)

        return self._to_response(payment)

    def _validate(self, amount, currency):
        if amount <= 0:
            raise ValidationException("Amount must be greater than zero")

        if amount > MAX_AMOUNT:
            raise ValidationException(f"Amount exceeds max limit ({MAX_AMOUNT})")

        if currency not in ALLOWED_CURRENCIES:
            raise ValidationException(f"Unsupported currency: {currency}")

    def _to_response(self, payment) -> PaymentResponse:
        return PaymentResponse(
            id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            provider=payment.provider,
            retries=payment.retries
        )