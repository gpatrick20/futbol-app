from fastapi.testclient import TestClient


def test_create_availability_vote(
    client: TestClient,
    second_auth_headers: dict[str, str],
    match_id: str,
):
    response = client.post(
        f"/matches/{match_id}/availability",
        headers=second_auth_headers,
        json={
            "proposed_date": "2026-11-15",
            "proposed_time": "19:30:00",
            "availability": "available",
        },
    )

    assert response.status_code == 201
    assert response.json()["availability"] == "available"


def test_invalid_availability_value(
    client: TestClient,
    second_auth_headers: dict[str, str],
    match_id: str,
):
    response = client.post(
        f"/matches/{match_id}/availability",
        headers=second_auth_headers,
        json={
            "proposed_date": "2026-11-15",
            "proposed_time": "19:30:00",
            "availability": "perhaps",
        },
    )

    assert response.status_code == 422


def test_duplicate_availability_vote(
    client: TestClient,
    second_auth_headers: dict[str, str],
    match_id: str,
):
    payload = {
        "proposed_date": "2026-11-15",
        "proposed_time": "19:30:00",
        "availability": "available",
    }

    first = client.post(
        f"/matches/{match_id}/availability",
        headers=second_auth_headers,
        json=payload,
    )
    second = client.post(
        f"/matches/{match_id}/availability",
        headers=second_auth_headers,
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == (
        "Ya registraste disponibilidad para esta fecha y hora"
    )


def test_list_availability_votes(
    client: TestClient,
    second_auth_headers: dict[str, str],
    match_id: str,
):
    client.post(
        f"/matches/{match_id}/availability",
        headers=second_auth_headers,
        json={
            "proposed_date": "2026-11-15",
            "proposed_time": "19:30:00",
            "availability": "available",
        },
    )

    response = client.get(
        f"/matches/{match_id}/availability",
        headers=second_auth_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
