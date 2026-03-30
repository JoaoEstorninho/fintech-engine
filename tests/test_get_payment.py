import pytest
from app.services.use_cases.get_payment import GetPaymentService
from app.core.exceptions import NotFoundException
from app.models.payment import Payment


def test_get_payment_success(mocker):
    service = GetPaymentService()

    fake_payment = Payment(
        id="123",
        amount=100,
        currency="EUR",
        status="pending",
        provider=None,
        retries=0
    )

    mocker.patch(
        "app.services.use_cases.get_payment.repo.get",
        return_value=fake_payment
    )

    result = service.execute("123")

    assert result.id == "123"
    assert result.amount == 100
    assert result.status == "pending"


def test_get_payment_not_found(mocker):
    service = GetPaymentService()

    mocker.patch(
        "app.services.use_cases.get_payment.repo.get",
        return_value=None
    )

    with pytest.raises(NotFoundException):
        service.execute("invalid-id")