from fastapi.testclient import TestClient


def mark_match_played(client: TestClient, auth_headers: dict[str, str], match_id: str) -> None:
    response = client.patch(
        f"/matches/{match_id}/date",
        headers=auth_headers,
        json={"match_date": "2026-11-15", "start_time": "19:30:00"},
    )
    assert response.status_code == 200


def test_create_result(
    client: TestClient,
    auth_headers: dict[str, str],
    team_id: str,
    match_id: str,
):
    mark_match_played(client, auth_headers, match_id)

    response = client.post(
        f"/matches/{match_id}/results",
        headers=auth_headers,
        json={
            "team_id": team_id,
            "goals_for": 3,
            "goals_against": 1,
            "result": "win",
        },
    )

    assert response.status_code == 201
    assert response.json()["result"] == "win"


def test_invalid_result_consistency(
    client: TestClient,
    auth_headers: dict[str, str],
    team_id: str,
    match_id: str,
):
    mark_match_played(client, auth_headers, match_id)

    response = client.post(
        f"/matches/{match_id}/results",
        headers=auth_headers,
        json={
            "team_id": team_id,
            "goals_for": 1,
            "goals_against": 3,
            "result": "win",
        },
    )

    assert response.status_code == 422


def test_non_creator_cannot_create_result(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
    team_id: str,
    match_id: str,
):
    mark_match_played(client, auth_headers, match_id)

    response = client.post(
        f"/matches/{match_id}/results",
        headers=second_auth_headers,
        json={
            "team_id": team_id,
            "goals_for": 3,
            "goals_against": 1,
            "result": "win",
        },
    )

    assert response.status_code == 403


def test_duplicate_result(
    client: TestClient,
    auth_headers: dict[str, str],
    team_id: str,
    match_id: str,
):
    mark_match_played(client, auth_headers, match_id)
    payload = {
        "team_id": team_id,
        "goals_for": 3,
        "goals_against": 1,
        "result": "win",
    }

    first = client.post(
        f"/matches/{match_id}/results",
        headers=auth_headers,
        json=payload,
    )
    second = client.post(
        f"/matches/{match_id}/results",
        headers=auth_headers,
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_list_results(
    client: TestClient,
    auth_headers: dict[str, str],
    team_id: str,
    match_id: str,
):
    mark_match_played(client, auth_headers, match_id)

    client.post(
        f"/matches/{match_id}/results",
        headers=auth_headers,
        json={
            "team_id": team_id,
            "goals_for": 2,
            "goals_against": 2,
            "result": "draw",
        },
    )

    response = client.get(f"/matches/{match_id}/results", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
