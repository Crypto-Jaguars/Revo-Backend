import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    data = {
        "email": "user1@example.com",
        "password": "password123",
        "user_type": "FARMER"
    }
    response = await client.post("/api/users/register", json=data)
    print("RESPONSE JSON:", response.json())  # Debug print
    assert response.status_code == 201
    user = response.json()
    assert user["email"] == data["email"]
    assert user["user_type"] == data["user_type"]
    assert user["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    data = {
        "email": "user2@example.com",
        "password": "password123",
        "user_type": "CONSUMER"
    }
    await client.post("/api/users/register", json=data)
    response = await client.post("/api/users/register", json=data)
    assert response.status_code == 400
    assert "already registered" in response.text


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    data = {
        "email": "user3@example.com",
        "password": "password123",
        "user_type": "FARMER"
    }
    await client.post("/api/users/register", json=data)
    login_data = {"username": data["email"], "password": data["password"]}
    response = await client.post("/api/users/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    login_data = {"username": "notfound@example.com", "password": "wrongpass"}
    response = await client.post("/api/users/login", data=login_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    data = {
        "email": "user4@example.com",
        "password": "password123",
        "user_type": "CONSUMER"
    }
    await client.post("/api/users/register", json=data)
    login_data = {"username": data["email"], "password": data["password"]}
    login_resp = await client.post("/api/users/login", data=login_data)
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = await client.get("/api/users/me", headers=headers)
    assert me_resp.status_code == 200
    user = me_resp.json()
    assert user["email"] == data["email"]
    assert user["user_type"] == data["user_type"]
    assert user["is_active"] is True


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/users/me")
    assert response.status_code == 401 