from fastapi.testclient import TestClient
from uuid import UUID

from app.models.match import Match

def mark_match_played(
    client: TestClient,
    auth_headers: dict[str, str],
    match_id: str,
) -> None:
    response = client.patch(
        f"/matches/{match_id}/date",
        headers=auth_headers,
        json={
            "match_date": "2026-11-15",
            "start_time": "19:30:00",
        },
    )
    assert response.status_code == 200, response.text

    # Usar la sesión de pruebas, nunca la conexión real a Supabase.
    from conftest import TestingSessionLocal

    with TestingSessionLocal() as db:
        match = db.get(Match, UUID(match_id))
        assert match is not None

        match.status = "played"
        db.commit()


def test_create_match_event(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    match_id: str,
):
    mark_match_played(client, auth_headers, match_id)

    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]

    response = client.post(
        f"/matches/{match_id}/events",
        headers=auth_headers,
        json={
            "player_id": second_user_id,
            "event_type": "goal",
            "minute": 25,
        },
    )

    assert response.status_code == 201
    assert response.json()["event_type"] == "goal"


def test_cannot_create_event_before_match_is_played(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    match_id: str,
):
    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]

    response = client.post(
        f"/matches/{match_id}/events",
        headers=auth_headers,
        json={
            "player_id": second_user_id,
            "event_type": "goal",
            "minute": 25,
        },
    )

    assert response.status_code == 409


def test_invalid_event_type(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    match_id: str,
):
    mark_match_played(client, auth_headers, match_id)

    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]

    response = client.post(
        f"/matches/{match_id}/events",
        headers=auth_headers,
        json={
            "player_id": second_user_id,
            "event_type": "penalty",
            "minute": 25,
        },
    )

    assert response.status_code == 422


def test_list_match_events(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    match_id: str,
):
    mark_match_played(client, auth_headers, match_id)

    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]

    client.post(
        f"/matches/{match_id}/events",
        headers=auth_headers,
        json={
            "player_id": second_user_id,
            "event_type": "assist",
            "minute": 10,
        },
    )

    response = client.get(f"/matches/{match_id}/events", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
