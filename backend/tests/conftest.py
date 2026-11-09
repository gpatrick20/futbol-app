import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402,F401
    AvailabilityVote,
    Match,
    MatchEvent,
    MatchParticipant,
    Payment,
    Team,
    TeamMatchResult,
    TeamMember,
    User,
)

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def database() -> Iterator[None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def register_and_login(client: TestClient, email: str = "player@example.com") -> dict[str, str]:
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
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    return register_and_login(client)


@pytest.fixture
def second_auth_headers(client: TestClient) -> dict[str, str]:
    return register_and_login(client, email="second@example.com")


@pytest.fixture
def team_id(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/teams",
        headers=auth_headers,
        json={"name": "Los Cóndores", "commune": "Providencia"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.fixture
def match_id(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/matches",
        headers=auth_headers,
        json={
            "format": "futbol5",
            "venue_name": "Cancha Central",
            "commune": "Providencia",
            "total_cost": "50000.00",
            "min_players": 4,
            "max_players": 10,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]
