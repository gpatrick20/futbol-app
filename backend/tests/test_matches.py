from fastapi.testclient import TestClient


def register_and_login(
    client: TestClient,
    email: str,
) -> dict[str, str]:
    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "SecurePass123",
            "full_name": "Test Player",
            "role": "player",
        },
    )
    assert register_response.status_code == 201, register_response.text

    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": "SecurePass123"},
        headers={"Origin": "http://localhost:5173"},
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]
    return {"Authorization": "Bearer " + token}


def create_match(
    client: TestClient,
    headers: dict[str, str],
    *,
    max_players: int = 10,
):
    response = client.post(
        "/matches",
        headers=headers,
        json={
            "format": "futbol5",
            "venue_name": "Cancha Central",
            "min_players": 0,
            "max_players": max_players,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


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


def test_list_available_matches_requires_authentication(
    client: TestClient,
):
    response = client.get("/matches/available")

    assert response.status_code == 401


def test_list_available_matches_filters_by_user_status_and_capacity(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
):
    third_auth_headers = register_and_login(
        client, "third@example.com"
    )

    visible_match_id = create_match(client, auth_headers)
    own_match_id = create_match(client, second_auth_headers)

    joined_match_id = create_match(client, auth_headers)
    join_response = client.post(
        f"/matches/{joined_match_id}/participants",
        headers=second_auth_headers,
    )
    assert join_response.status_code == 201, join_response.text

    cancelled_match_id = create_match(client, auth_headers)
    cancel_response = client.patch(
        f"/matches/{cancelled_match_id}/cancel",
        headers=auth_headers,
    )
    assert cancel_response.status_code == 200, cancel_response.text

    played_match_id = create_match(client, auth_headers)
    confirm_response = client.patch(
        f"/matches/{played_match_id}/date",
        headers=auth_headers,
        json={
            "match_date": "2026-11-15",
            "start_time": "19:30:00",
        },
    )
    assert confirm_response.status_code == 200, confirm_response.text
    finish_response = client.patch(
        f"/matches/{played_match_id}/finish",
        headers=auth_headers,
    )
    assert finish_response.status_code == 200, finish_response.text

    full_match_id = create_match(
        client,
        auth_headers,
        max_players=1,
    )
    fill_response = client.post(
        f"/matches/{full_match_id}/participants",
        headers=third_auth_headers,
    )
    assert fill_response.status_code == 201, fill_response.text

    no_slots_match_id = create_match(
        client,
        auth_headers,
        max_players=0,
    )

    response = client.get(
        "/matches/available",
        headers=second_auth_headers,
    )

    assert response.status_code == 200
    returned_ids = {match["id"] for match in response.json()}
    assert visible_match_id in returned_ids
    assert own_match_id not in returned_ids
    assert joined_match_id not in returned_ids
    assert cancelled_match_id not in returned_ids
    assert played_match_id not in returned_ids
    assert full_match_id not in returned_ids
    assert no_slots_match_id not in returned_ids


def test_user_cannot_join_cancelled_or_played_match(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    match_id: str,
):
    cancel_response = client.patch(
        f"/matches/{match_id}/cancel",
        headers=auth_headers,
    )
    assert cancel_response.status_code == 200, cancel_response.text

    cancelled_join = client.post(
        f"/matches/{match_id}/participants",
        headers=second_auth_headers,
    )
    assert cancelled_join.status_code == 409

    played_match_id = create_match(client, auth_headers)
    confirm_response = client.patch(
        f"/matches/{played_match_id}/date",
        headers=auth_headers,
        json={
            "match_date": "2026-11-15",
            "start_time": "19:30:00",
        },
    )
    assert confirm_response.status_code == 200, confirm_response.text
    finish_response = client.patch(
        f"/matches/{played_match_id}/finish",
        headers=auth_headers,
    )
    assert finish_response.status_code == 200, finish_response.text

    played_join = client.post(
        f"/matches/{played_match_id}/participants",
        headers=second_auth_headers,
    )
    assert played_join.status_code == 409


def test_user_cannot_join_match_without_slots(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
):
    match_without_slots = create_match(
        client,
        auth_headers,
        max_players=0,
    )
    response = client.post(
        f"/matches/{match_without_slots}/participants",
        headers=second_auth_headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Este partido no tiene cupos habilitados"


def test_user_cannot_join_when_match_is_full_and_status_updates(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
):
    third_auth_headers = register_and_login(
        client, "third-full@example.com"
    )
    full_match_id = create_match(
        client,
        auth_headers,
        max_players=1,
    )

    first_join = client.post(
        f"/matches/{full_match_id}/participants",
        headers=second_auth_headers,
    )
    second_join = client.post(
        f"/matches/{full_match_id}/participants",
        headers=third_auth_headers,
    )

    assert first_join.status_code == 201, first_join.text
    assert second_join.status_code == 409

    match_response = client.get(
        f"/matches/{full_match_id}",
        headers=auth_headers,
    )
    assert match_response.status_code == 200
    assert match_response.json()["status"] == "full"


def test_updating_participant_status_releases_and_recovers_capacity(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
):
    third_auth_headers = register_and_login(
        client, "third-capacity@example.com"
    )
    full_match_id = create_match(
        client,
        auth_headers,
        max_players=1,
    )
    join_response = client.post(
        f"/matches/{full_match_id}/participants",
        headers=second_auth_headers,
    )
    assert join_response.status_code == 201, join_response.text

    second_user = client.get(
        "/auth/me",
        headers=second_auth_headers,
    )
    second_user_id = second_user.json()["id"]

    release_response = client.patch(
        f"/matches/{full_match_id}/participants/{second_user_id}",
        headers=auth_headers,
        json={"status": "tentative"},
    )
    assert release_response.status_code == 200, release_response.text

    match_after_release = client.get(
        f"/matches/{full_match_id}",
        headers=auth_headers,
    )
    assert match_after_release.status_code == 200
    assert match_after_release.json()["status"] == "confirmed"

    new_join_response = client.post(
        f"/matches/{full_match_id}/participants",
        headers=third_auth_headers,
    )
    assert new_join_response.status_code == 201, new_join_response.text


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
