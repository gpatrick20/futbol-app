from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "SecurePass123",
            "full_name": "Test User",
            "role": "player",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "user@example.com"
    assert body["role"] == "player"
    assert "hashed_password" not in body


def test_register_duplicate_email(client: TestClient):
    payload = {
        "email": "duplicate@example.com",
        "password": "SecurePass123",
        "full_name": "Test User",
        "role": "player",
    }

    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 400
    assert second.json()["detail"] == "El email ya está registrado"


def test_login_success(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "SecurePass123",
            "full_name": "Login User",
            "role": "player",
        },
    )

    response = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "SecurePass123"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_with_invalid_password(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "invalid@example.com",
            "password": "SecurePass123",
            "full_name": "Invalid User",
            "role": "player",
        },
    )

    response = client.post(
        "/auth/login",
        data={"username": "invalid@example.com", "password": "WrongPassword"},
    )

    assert response.status_code == 401


def test_get_me_requires_authentication(client: TestClient):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_get_me_returns_current_user(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["email"] == "player@example.com"
