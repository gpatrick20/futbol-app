from fastapi.testclient import TestClient


def test_create_match(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/matches",
        headers=auth_headers,
        json={
            "format": "futbol5",
            "venue_name": "Cancha Central",
            "total_cost": "50000.00",
            "min_players": 4,
            "max_players": 10,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["format"] == "futbol5"
    assert body["status"] == "proposed"
    assert body["match_date"] is None


def test_create_match_with_invalid_capacity(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/matches",
        headers=auth_headers,
        json={
            "format": "futbol5",
            "venue_name": "Cancha Central",
            "min_players": 10,
            "max_players": 5,
        },
    )

    assert response.status_code == 422


def test_create_match_with_invalid_format(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/matches",
        headers=auth_headers,
        json={
            "format": "futbol6",
            "venue_name": "Cancha Central",
            "min_players": 4,
            "max_players": 10,
        },
    )

    assert response.status_code == 422


def test_list_matches(client: TestClient, match_id: str):
    response = client.get("/matches")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == match_id


def test_get_missing_match(client: TestClient):
    response = client.get("/matches/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_creator_can_confirm_date(client: TestClient, auth_headers: dict[str, str], match_id: str):
    response = client.patch(
        f"/matches/{match_id}/date",
        headers=auth_headers,
        json={"match_date": "2026-11-15", "start_time": "19:30:00"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["match_date"] == "2026-11-15"
    assert body["start_time"] == "19:30:00"
    assert body["status"] == "confirmed"


def test_non_creator_cannot_confirm_date(
    client: TestClient,
    second_auth_headers: dict[str, str],
    match_id: str,
):
    response = client.patch(
        f"/matches/{match_id}/date",
        headers=second_auth_headers,
        json={"match_date": "2026-11-15", "start_time": "19:30:00"},
    )

    assert response.status_code == 403


def test_creator_can_cancel_match(client: TestClient, auth_headers: dict[str, str], match_id: str):
    response = client.patch(f"/matches/{match_id}/cancel", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_user_can_join_match(client: TestClient, second_auth_headers: dict[str, str], match_id: str):
    response = client.post(
        f"/matches/{match_id}/participants",
        headers=second_auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["status"] == "confirmed"


def test_user_cannot_join_twice(client: TestClient, second_auth_headers: dict[str, str], match_id: str):
    first = client.post(f"/matches/{match_id}/participants", headers=second_auth_headers)
    second = client.post(f"/matches/{match_id}/participants", headers=second_auth_headers)

    assert first.status_code == 201
    assert second.status_code == 409


def test_creator_can_update_participant_status(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    match_id: str,
):
    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]

    client.post(f"/matches/{match_id}/participants", headers=second_auth_headers)

    response = client.patch(
        f"/matches/{match_id}/participants/{second_user_id}",
        headers=auth_headers,
        json={"status": "tentative"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "tentative"
