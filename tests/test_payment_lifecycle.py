import pytest


def test_payment_lifecycle(client):
    response = client.post(
        "/payments",
        json={"amount": 100, "currency": "EUR"},
        headers={"Idempotency-Key": "lifecycle-test"}
    )

    assert response.status_code == 200

    create_data = response.json()

    payment_id = create_data["data"]["id"]

    response = client.get(f"/payments/{payment_id}")

    assert response.status_code == 200

    get_data = response.json()

    assert "data" in get_data
    assert get_data["data"]["id"] == payment_id

    assert get_data["data"]["status"] in ["success", "failed"]