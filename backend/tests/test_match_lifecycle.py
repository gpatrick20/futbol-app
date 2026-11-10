from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


def confirm_match(client, headers, match_id):
    response = client.patch(
        f"/matches/{match_id}/date",
        headers=headers,
        json={
            "match_date": "2026-11-15",
            "start_time": "19:30:00",
        },
    )
    assert response.status_code == 200, response.text


def test_creator_can_finish_confirmed_match(
    client: TestClient, auth_headers, match_id
):
    confirm_match(client, auth_headers, match_id)

    response = client.patch(
        f"/matches/{match_id}/finish",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "played"

    saved = client.get(f"/matches/{match_id}")
    assert saved.json()["status"] == "played"


def test_non_creator_cannot_finish_match(
    client: TestClient, auth_headers, second_auth_headers, match_id
):
    confirm_match(client, auth_headers, match_id)

    response = client.patch(
        f"/matches/{match_id}/finish",
        headers=second_auth_headers,
    )

    assert response.status_code == 403


def test_finish_requires_authentication(client: TestClient, match_id):
    response = client.patch(f"/matches/{match_id}/finish")

    assert response.status_code == 401


def test_finish_missing_match(client: TestClient, auth_headers):
    response = client.patch(
        f"/matches/{uuid4()}/finish",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.parametrize("cancelled", [False, True])
def test_cannot_finish_proposed_or_cancelled_match(
    client: TestClient, auth_headers, match_id, cancelled
):
    if cancelled:
        response = client.patch(
            f"/matches/{match_id}/cancel",
            headers=auth_headers,
        )
        assert response.status_code == 200

    response = client.patch(
        f"/matches/{match_id}/finish",
        headers=auth_headers,
    )

    assert response.status_code == 409


def test_finishing_twice_is_idempotent(
    client: TestClient, auth_headers, match_id
):
    confirm_match(client, auth_headers, match_id)

    for _ in range(2):
        response = client.patch(
            f"/matches/{match_id}/finish",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "played"


def test_played_match_cannot_be_rescheduled_or_cancelled(
    client: TestClient, auth_headers, match_id
):
    confirm_match(client, auth_headers, match_id)
    finish = client.patch(
        f"/matches/{match_id}/finish",
        headers=auth_headers,
    )
    assert finish.status_code == 200

    reschedule = client.patch(
        f"/matches/{match_id}/date",
        headers=auth_headers,
        json={
            "match_date": "2026-11-16",
            "start_time": "20:00:00",
        },
    )
    cancel = client.patch(
        f"/matches/{match_id}/cancel",
        headers=auth_headers,
    )

    assert reschedule.status_code == 409
    assert cancel.status_code == 409