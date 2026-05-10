import pytest

pytestmark = pytest.mark.asyncio


async def test_signup_success(client):
    response = await client.post(
        "/auth/signup",
        json={
            "name": "Test",
            "surname": "User",
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["role"] == "USER"
    assert "password" not in data


async def test_signup_duplicate_username(client):
    await client.post(
        "/auth/signup",
        json={
            "name": "Test",
            "surname": "User",
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    response = await client.post(
        "/auth/signup",
        json={
            "name": "Test2",
            "surname": "User2",
            "username": "testuser",
            "email": "test2@example.com",
            "password": "testpass123",
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


async def test_login_success(client):
    await client.post(
        "/auth/signup",
        json={
            "name": "Test",
            "surname": "User",
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    response = await client.post(
        "/auth/login", json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client):
    await client.post(
        "/auth/signup",
        json={
            "name": "Test",
            "surname": "User",
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    response = await client.post(
        "/auth/login", json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


async def test_get_me(client):
    await client.post(
        "/auth/signup",
        json={
            "name": "Test",
            "surname": "User",
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    login_response = await client.post(
        "/auth/login", json={"username": "testuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    response = await client.get(
        "/user/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


async def test_get_me_without_token(client):
    response = await client.get("/user/me")
    assert response.status_code == 401
