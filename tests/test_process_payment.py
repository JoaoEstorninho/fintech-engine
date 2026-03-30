from app.services.use_cases.process_payment import ProcessPaymentService


def test_process_payment_success(mocker):
    service = ProcessPaymentService()

    fake_payment = mocker.Mock()
    fake_payment.id = "123"
    fake_payment.amount = 100
    fake_payment.status = "pending"
    fake_payment.provider = None
    fake_payment.retries = 0

    mocker.patch(
        "app.services.use_cases.process_payment.repo.get",
        return_value=fake_payment
    )

    mock_update = mocker.patch(
        "app.services.use_cases.process_payment.repo.update"
    )

    mocker.patch(
        "app.services.use_cases.process_payment.router.get_best_provider",
        return_value=("stripe", {"handler": lambda x: {"status": "success"}})
    )

    mocker.patch(
        "app.services.use_cases.process_payment.retry_policy.execute",
        return_value={"status": "success"}
    )

    service.execute("123")

    assert fake_payment.status == "success"
    assert fake_payment.provider == "stripe"
    mock_update.assert_called_once()