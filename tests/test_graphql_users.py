import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_graphql_get_user(client):
    query = '{ user(id: 1) { email userType isActive } }'
    response = await client.post(
        "/graphql",
        json={"query": query},
    )
    assert response.status_code == 200
    data = response.json()["data"]["user"]
    assert data["email"]
    assert data["userType"]
    assert isinstance(data["isActive"], bool)

@pytest.mark.asyncio
async def test_graphql_get_current_user(client):
    query = '{ currentUser { email userType isActive } }'
    response = await client.post(
        "/graphql",
        json={"query": query},
    )
    assert response.status_code == 200
    data = response.json()["data"]["currentUser"]
    assert data["email"]
    assert data["userType"]
    assert isinstance(data["isActive"], bool) 