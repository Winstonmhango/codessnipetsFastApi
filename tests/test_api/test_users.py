from fastapi.testclient import TestClient

from app.core.config import settings


def test_get_users_superuser(client: TestClient, superuser_token_headers) -> None:
    """
    Test that a superuser can get the list of users
    """
    r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    users = r.json()
    assert r.status_code == 200
    assert len(users) >= 2  # At least the superuser and normal user
    assert users[0]["email"] == "admin@example.com"
    assert users[1]["email"] == "user@example.com"


def test_get_users_normal_user(client: TestClient, normal_user_token_headers) -> None:
    """
    Test that a normal user cannot get the list of users
    """
    r = client.get(f"{settings.API_V1_STR}/users/", headers=normal_user_token_headers)
    assert r.status_code == 400  # Not enough permissions


def test_get_user_me(client: TestClient, normal_user_token_headers) -> None:
    """
    Test that a user can get their own information
    """
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert r.status_code == 200
    assert current_user["email"] == "user@example.com"
    assert current_user["username"] == "user"
    assert current_user["first_name"] == "Normal"
    assert current_user["last_name"] == "User"
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False


def test_update_user_me(client: TestClient, normal_user_token_headers) -> None:
    """
    Test that a user can update their own information
    """
    data = {
        "first_name": "Updated",
        "last_name": "Name",
    }
    r = client.put(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=data,
    )
    updated_user = r.json()
    assert r.status_code == 200
    assert updated_user["first_name"] == data["first_name"]
    assert updated_user["last_name"] == data["last_name"]


def test_get_user_by_id_superuser(client: TestClient, superuser_token_headers) -> None:
    """
    Test that a superuser can get another user's information
    """
    r = client.get(
        f"{settings.API_V1_STR}/users/11111111-1111-1111-1111-111111111111",
        headers=superuser_token_headers,
    )
    user = r.json()
    assert r.status_code == 200
    assert user["email"] == "user@example.com"
    assert user["username"] == "user"


def test_get_user_by_id_normal_user(client: TestClient, normal_user_token_headers) -> None:
    """
    Test that a normal user cannot get another user's information
    """
    r = client.get(
        f"{settings.API_V1_STR}/users/00000000-0000-0000-0000-000000000000",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 400  # Not enough permissions


def test_update_user_superuser(client: TestClient, superuser_token_headers) -> None:
    """
    Test that a superuser can update another user's information
    """
    data = {
        "first_name": "Super",
        "last_name": "Updated",
    }
    r = client.put(
        f"{settings.API_V1_STR}/users/11111111-1111-1111-1111-111111111111",
        headers=superuser_token_headers,
        json=data,
    )
    updated_user = r.json()
    assert r.status_code == 200
    assert updated_user["first_name"] == data["first_name"]
    assert updated_user["last_name"] == data["last_name"]
