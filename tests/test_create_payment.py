import pytest
from app.services.use_cases.create_payment import CreatePaymentService
from app.core.exceptions import ValidationException



def test_create_payment_success(mocker):
    service = CreatePaymentService()

    mocker.patch(
        "app.services.use_cases.create_payment.repo.create",
        side_effect=lambda x: x
    )

    result = service.execute(100, "EUR")

    assert result.amount == 100
    assert result.currency == "EUR"
    assert result.status == "pending"

def test_create_payment_invalid_amount():
    service = CreatePaymentService()

    with pytest.raises(ValidationException):
        service.execute(-1, "EUR")


def test_create_payment_invalid_currency():
    service = CreatePaymentService()

    with pytest.raises(ValidationException):
        service.execute(100, "BTC")