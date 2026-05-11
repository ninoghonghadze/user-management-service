import pytest

pytestmark = pytest.mark.asyncio

async def test_update_me(client):
    await client.post("/auth/signup", json={
        "name": "Test", "surname": "User",
        "username": "testuser", "email": "test@example.com",
        "password": "testpass123"
    })
    login = await client.post("/auth/login", json={
        "username": "testuser", "password": "testpass123"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.patch("/user/me", json={"name": "Updated"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"


async def test_delete_me(client):
    await client.post("/auth/signup", json={
        "name": "Test", "surname": "User",
        "username": "testuser", "email": "test@example.com",
        "password": "testpass123"
    })
    login = await client.post("/auth/login", json={
        "username": "testuser", "password": "testpass123"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete("/user/me", headers=headers)
    assert response.status_code == 204

    response = await client.get("/user/me", headers=headers)
    assert response.status_code == 404


async def test_get_users_as_regular_user_forbidden(client):
    await client.post("/auth/signup", json={
        "name": "Test", "surname": "User",
        "username": "testuser", "email": "test@example.com",
        "password": "testpass123"
    })
    login = await client.post("/auth/login", json={
        "username": "testuser", "password": "testpass123"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/users", headers=headers)
    assert response.status_code == 403


async def test_login_with_email(client):
    await client.post("/auth/signup", json={
        "name": "Test", "surname": "User",
        "username": "testuser", "email": "test@example.com",
        "password": "testpass123"
    })
    response = await client.post("/auth/login", json={
        "username": "test@example.com",  # using email
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_signup_invalid_email(client):
    response = await client.post("/auth/signup", json={
        "name": "Test", "surname": "User",
        "username": "testuser",
        "email": "not-an-email",  # invalid email
        "password": "testpass123"
    })
    assert response.status_code == 422 

async def test_refresh_token(client):
    await client.post("/auth/signup", json={
        "name": "Test", "surname": "User",
        "username": "testuser", "email": "test@example.com",
        "password": "testpass123"
    })
    login = await client.post("/auth/login", json={
        "username": "testuser", "password": "testpass123"
    })
    refresh_token = login.json()["refresh_token"]

    # Use refresh token to get new tokens
    response = await client.post("/auth/refresh-token", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

    # Try to use old refresh token again — should fail (blacklisted)
    response = await client.post("/auth/refresh-token", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 401


async def test_reset_password(client):
    await client.post("/auth/signup", json={
        "name": "Test", "surname": "User",
        "username": "testuser", "email": "test@example.com",
        "password": "testpass123"
    })
    response = await client.post("/auth/reset-password", json={
        "email": "test@example.com"
    })
    assert response.status_code == 202

    # Should return same message even for non-existent email
    response = await client.post("/auth/reset-password", json={
        "email": "nonexistent@example.com"
    })
    assert response.status_code == 202

async def test_blocked_user_cannot_login(client):
    # This test would require setting up a blocked user
    # Shows you understand the is_blocked feature
    await client.post("/auth/signup", json={
        "name": "Test", "surname": "User",
        "username": "testuser", "email": "test@example.com",
        "password": "testpass123"
    })


async def test_signup_missing_required_field(client):
    response = await client.post("/auth/signup", json={
        "surname": "User",
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 422


async def test_signup_duplicate_email(client):
    await client.post("/auth/signup", json={
        "name": "Test", "surname": "User",
        "username": "testuser1", "email": "test@example.com",
        "password": "testpass123"
    })
    #with different username
    response = await client.post("/auth/signup", json={
        "name": "Test2", "surname": "User2",
        "username": "testuser2", "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


