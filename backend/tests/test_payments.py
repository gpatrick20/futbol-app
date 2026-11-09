from fastapi.testclient import TestClient


def test_create_payment(
    client: TestClient,
    second_auth_headers: dict[str, str],
    match_id: str,
):
    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]

    response = client.post(
        f"/matches/{match_id}/payments",
        headers=second_auth_headers,
        json={
            "user_id": second_user_id,
            "amount": "10000.00",
            "method": "transfer",
        },
    )

    assert response.status_code == 201
    assert response.json()["amount"] == "10000.00"
    assert response.json()["status"] == "pending"


def test_payment_amount_must_be_positive(
    client: TestClient,
    second_auth_headers: dict[str, str],
    match_id: str,
):
    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]

    response = client.post(
        f"/matches/{match_id}/payments",
        headers=second_auth_headers,
        json={
            "user_id": second_user_id,
            "amount": "0.00",
            "method": "cash",
        },
    )

    assert response.status_code == 422


def test_duplicate_payment(
    client: TestClient,
    second_auth_headers: dict[str, str],
    match_id: str,
):
    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]
    payload = {
        "user_id": second_user_id,
        "amount": "10000.00",
        "method": "transfer",
    }

    first = client.post(
        f"/matches/{match_id}/payments",
        headers=second_auth_headers,
        json=payload,
    )
    second = client.post(
        f"/matches/{match_id}/payments",
        headers=second_auth_headers,
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_creator_can_mark_payment_paid(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    match_id: str,
):
    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]

    payment_response = client.post(
        f"/matches/{match_id}/payments",
        headers=second_auth_headers,
        json={
            "user_id": second_user_id,
            "amount": "10000.00",
            "method": "transfer",
        },
    )
    payment_id = payment_response.json()["id"]

    response = client.patch(
        f"/matches/{match_id}/payments/{payment_id}",
        headers=auth_headers,
        json={"status": "paid"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "paid"
    assert response.json()["paid_at"] is not None


def test_non_creator_cannot_update_payment(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    match_id: str,
):
    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]

    payment_response = client.post(
        f"/matches/{match_id}/payments",
        headers=second_auth_headers,
        json={
            "user_id": second_user_id,
            "amount": "10000.00",
            "method": "transfer",
        },
    )
    payment_id = payment_response.json()["id"]

    response = client.patch(
        f"/matches/{match_id}/payments/{payment_id}",
        headers=second_auth_headers,
        json={"status": "paid"},
    )

    assert response.status_code == 403
