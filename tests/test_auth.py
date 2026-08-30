"""Tests for authentication endpoints"""

def test_register_and_login(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    assert response.json()["username"] == "user1"

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user1", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody", "password": "wrong"},
    )
    assert response.status_code == 401


def test_protected_endpoint_requires_auth(client):
    response = client.get("/api/v1/documents")
    assert response.status_code == 401
