import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis(mocker):
    mocker.patch("app.api.routes.redis_client.get", return_value=None)
    mocker.patch("app.api.routes.redis_client.set", return_value=True)


def test_create_and_get_payment():
    response = client.post(
        "/payments",
        json={"amount": 100, "currency": "EUR"},
        headers={"Idempotency-Key": "test-key"}
    )

    assert response.status_code == 200

    data = response.json()
    payment_id = data["data"]["id"]

    response = client.get(f"/payments/{payment_id}")

    assert response.status_code == 200