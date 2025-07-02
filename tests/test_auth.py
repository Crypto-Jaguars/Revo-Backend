import pytest

@pytest.mark.asyncio
async def test_login_returns_token(client, sample_user_data):
    response = await client.post(
        "/auth/token",
        data={"username": sample_user_data["email"], "password": sample_user_data["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_protected_route_requires_token(client):
    response = await client.get("/protected")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_route_rejects_invalid_token(client):
    response = await client.get(
        "/protected",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_route_accepts_valid_token(client, sample_user_data):
    login_resp = await client.post(
        "/auth/token",
        data={"username": sample_user_data["email"], "password": sample_user_data["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_resp.json()["access_token"]
    response = await client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["message"] == "Access granted" 