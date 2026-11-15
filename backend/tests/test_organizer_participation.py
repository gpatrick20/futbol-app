from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.models.match import MatchParticipant
from conftest import TestingSessionLocal


def create_match(client, headers, capacity):
    return client.post(
        '/matches',
        headers=headers,
        json={'format': 'futbol5', 'venue_name': 'Cancha prueba',
              'min_players': 0, 'max_players': capacity},
    )


def test_creator_is_confirmed_in_team_a_and_both_lists(
    client: TestClient, auth_headers: dict[str, str],
):
    response = create_match(client, auth_headers, 10)
    assert response.status_code == 201, response.text
    match = response.json()
    with TestingSessionLocal() as db:
        participants = db.query(MatchParticipant).filter(
            MatchParticipant.match_id == UUID(match['id'])
        ).all()
        assert len(participants) == 1
        assert str(participants[0].user_id) == match['created_by']
        assert participants[0].status == 'confirmed'
        assert participants[0].team == 'A'
    for path in ('organized', 'participating'):
        listing = client.get(f'/matches/{path}', headers=auth_headers)
        assert listing.status_code == 200, listing.text
        assert match['id'] in {item['id'] for item in listing.json()}
    duplicate = client.post(
        f"/matches/{match['id']}/participants", headers=auth_headers,
    )
    assert duplicate.status_code == 409


def test_organizer_occupies_only_slot_and_date_keeps_full(
    client: TestClient, auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
):
    response = create_match(client, auth_headers, 1)
    assert response.status_code == 201, response.text
    match = response.json()
    assert match['status'] == 'full'
    join = client.post(
        f"/matches/{match['id']}/participants", headers=second_auth_headers,
    )
    assert join.status_code == 409
    date_response = client.patch(
        f"/matches/{match['id']}/date", headers=auth_headers,
        json={'match_date': '2026-12-01', 'start_time': '19:30:00'},
    )
    assert date_response.status_code == 200, date_response.text
    assert date_response.json()['status'] == 'full'


@pytest.mark.parametrize('capacity', [0, -1])
def test_new_match_rejects_no_capacity(client, auth_headers, capacity):
    response = create_match(client, auth_headers, capacity)
    assert response.status_code == 422
