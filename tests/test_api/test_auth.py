from fastapi.testclient import TestClient

from app.core.config import settings


def test_login(client: TestClient, normal_user_token_headers) -> None:
    """
    Test that the login endpoint works
    """
    login_data = {
        "username": "user@example.com",
        "password": "password",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient) -> None:
    """
    Test that the login endpoint returns an error with incorrect password
    """
    login_data = {
        "username": "user@example.com",
        "password": "wrong_password",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert r.status_code == 400


def test_register(client: TestClient) -> None:
    """
    Test that the register endpoint works
    """
    data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "password123",
        "first_name": "New",
        "last_name": "User",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    new_user = r.json()
    assert r.status_code == 200
    assert new_user["email"] == data["email"]
    assert new_user["username"] == data["username"]
    assert new_user["first_name"] == data["first_name"]
    assert new_user["last_name"] == data["last_name"]
    assert "id" in new_user


def test_register_existing_email(client: TestClient, normal_user_token_headers) -> None:
    """
    Test that the register endpoint returns an error with existing email
    """
    data = {
        "email": "user@example.com",  # This email already exists
        "username": "different_user",
        "password": "password123",
        "first_name": "Different",
        "last_name": "User",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    assert r.status_code == 400


def test_test_token(client: TestClient, normal_user_token_headers) -> None:
    """
    Test that the test-token endpoint works
    """
    r = client.post(
        f"{settings.API_V1_STR}/auth/test-token", headers=normal_user_token_headers
    )
    result = r.json()
    assert r.status_code == 200
    assert "id" in result
    assert result["email"] == "user@example.com"
    assert result["username"] == "user"
