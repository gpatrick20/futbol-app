from fastapi.testclient import TestClient


def test_create_team(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/teams",
        headers=auth_headers,
        json={"name": "Los Cóndores", "commune": "Providencia"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Los Cóndores"
    assert body["commune"] == "Providencia"


def test_create_team_requires_authentication(client: TestClient):
    response = client.post("/teams", json={"name": "Sin Token"})

    assert response.status_code == 401


def test_get_team(client: TestClient, auth_headers: dict[str, str], team_id: str):
    response = client.get(f"/teams/{team_id}")

    assert response.status_code == 200
    assert response.json()["id"] == team_id


def test_get_missing_team(client: TestClient):
    response = client.get("/teams/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_leader_can_add_member(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    team_id: str,
):
    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]

    response = client.post(
        f"/teams/{team_id}/members",
        headers=auth_headers,
        json={"user_id": second_user_id, "role": "player"},
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == second_user_id


def test_non_leader_cannot_add_member(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    team_id: str,
):
    me_response = client.get("/auth/me", headers=auth_headers)
    leader_id = me_response.json()["id"]

    response = client.post(
        f"/teams/{team_id}/members",
        headers=second_auth_headers,
        json={"user_id": leader_id, "role": "player"},
    )

    assert response.status_code == 403


def test_cannot_add_same_member_twice(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    team_id: str,
):
    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]
    payload = {"user_id": second_user_id, "role": "player"}

    first = client.post(f"/teams/{team_id}/members", headers=auth_headers, json=payload)
    second = client.post(f"/teams/{team_id}/members", headers=auth_headers, json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_leader_can_remove_member(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    team_id: str,
):
    me_response = client.get("/auth/me", headers=second_auth_headers)
    second_user_id = me_response.json()["id"]

    client.post(
        f"/teams/{team_id}/members",
        headers=auth_headers,
        json={"user_id": second_user_id, "role": "player"},
    )

    response = client.delete(
        f"/teams/{team_id}/members/{second_user_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204
