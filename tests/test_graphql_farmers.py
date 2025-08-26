import pytest
from httpx import AsyncClient

from app.main import app

pytestmark = pytest.mark.asyncio

async def _register_and_login(client: AsyncClient):
    # create a user (farmer type) and login to obtain token
    register = await client.post("/api/users/register", json={
        "email": "farmer@example.com",
        "password": "StrongP@ss123",
        "user_type": "FARMER"
    })
    assert register.status_code == 201

    login = await client.post("/api/users/login", data={
        "username": "farmer@example.com",
        "password": "StrongP@ss123",
    })
    assert login.status_code == 200
    token = login.json()["access_token"]
    return token

async def _graphql(client: AsyncClient, query: str, variables: dict | None = None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = await client.post("/graphql", json=payload)
    assert resp.status_code == 200
    return resp.json()

async def test_query_farmers_by_location(client: AsyncClient):
    token = await _register_and_login(client)

    # create two farmers at different locations via GraphQL mutation
    create_mut = """
    mutation CreateFarmer($input: FarmerInput!, $token: String!) {
      createFarmer(farmerInput: $input, token: $token) {
        id
        farmName
        location { latitude longitude city }
      }
    }
    """

    f1 = await _graphql(client, create_mut, {
        "input": {
          "userId": "00000000-0000-0000-0000-000000000001",
          "farmName": "Andes Farm",
          "organicCertified": true,
          "location": {"latitude": 4.65, "longitude": -74.05, "city": "Bogotá"}
        },
        "token": token
    })
    assert "errors" not in f1

    f2 = await _graphql(client, create_mut, {
        "input": {
          "userId": "00000000-0000-0000-0000-000000000001",
          "farmName": "Valley Farm",
          "organicCertified": false,
          "location": {"latitude": 9.93, "longitude": -84.08, "city": "San José"}
        },
        "token": token
    })
    assert "errors" not in f2

    # query by location near San José
    q = """
    query NearSJ {
      farmersByLocation(latitude: 9.93, longitude: -84.08, radiusKm: 50) {
        farmName
        location { city }
      }
    }
    """
    data = await _graphql(client, q)
    assert "errors" not in data
    names = [f["farmName"] for f in data["data"]["farmersByLocation"]]
    assert "Valley Farm" in names

async def test_mutations_require_auth(client: AsyncClient):
    # try without token
    create_mut = """
    mutation CreateFarmer($input: FarmerInput!, $token: String!) {
      createFarmer(farmerInput: $input, token: $token) { id }
    }
    """
    result = await _graphql(client, create_mut, {
        "input": {
          "userId": "00000000-0000-0000-0000-000000000001",
          "farmName": "NoAuth Farm",
          "organicCertified": false
        },
        "token": "invalid"
    })
    assert "errors" in result  # should error due to auth

async def test_nested_farmer_location_fields(client: AsyncClient):
    token = await _register_and_login(client)

    create_mut = """
    mutation CreateFarmer($input: FarmerInput!, $token: String!) {
      createFarmer(farmerInput: $input, token: $token) {
        id
        farmName
        location { latitude longitude city country }
      }
    }
    """
    created = await _graphql(client, create_mut, {
        "input": {
          "userId": "00000000-0000-0000-0000-000000000001",
          "farmName": "Nested Farm",
          "organicCertified": true,
          "location": {"latitude": 10.0, "longitude": -84.0, "city": "Alajuela", "country": "CR"}
        },
        "token": token
    })
    assert "errors" not in created
    fid = created["data"]["createFarmer"]["id"]

    q = f"""
    query One {{
      farmer(id: "{fid}") {{
        farmName
        location {{ city country latitude longitude }}
      }}
    }}
    """
    data = await _graphql(client, q)
    assert "errors" not in data
    loc = data["data"]["farmer"]["location"]
    assert loc["city"] == "Alajuela"
    assert loc["country"] == "CR"
