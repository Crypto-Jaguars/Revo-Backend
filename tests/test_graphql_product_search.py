import pytest
import time
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.graphql.resolvers.product_resolver import ProductResolver
from app.graphql.types.product_type import (
    ProductType,
    ProductCategoryType,
    ProductSearchInput,
)
from app.graphql.types.farmer_type import FarmerType
from app.main import app
from app.core.database import get_db


class InfoMock:
    def __init__(self, db):
        self.context = {"db": db}


# Helper para devolver un awaitable real
async def async_return(val):
    return val


@pytest.mark.asyncio
async def test_product_search_multi_filter():
    mock_session = AsyncMock()
    fake_category = ProductCategoryType(id=1, name="Verduras", description=None)
    fake_farmer = FarmerType(
        id=1, name="Farmer 1", email="f@x.com", phone=None, location=None, verified=True
    )
    fake_products = [
        ProductType(
            id=1,
            name="Tomate",
            description=None,
            price=10.0,
            stock=5,
            seasonal_availability=None,
            category=fake_category,
            farmer=fake_farmer,
        ),
        ProductType(
            id=2,
            name="Tomate",
            description=None,
            price=12.0,
            stock=3,
            seasonal_availability=None,
            category=fake_category,
            farmer=fake_farmer,
        ),
    ]

    async def fake_service(*args, **kwargs):
        return fake_products

    with patch(
        "app.graphql.resolvers.product_resolver.search_products_service",
        new=fake_service,
    ):
        resolver = ProductResolver()
        filters = ProductSearchInput(name="Tomate", category_id=1, available=True)
        info = InfoMock(mock_session)
        result = await resolver.search_products(info, filters)
        assert isinstance(result, list)
        assert all(p.name == "Tomate" for p in result)
        assert all(p.category.name == "Verduras" for p in result)


@pytest.mark.asyncio
async def test_product_search_performance(client: AsyncClient):
    class MockResult:
        def scalars(self):
            class All:
                def all(self):
                    class Product:
                        def __init__(self, i):
                            self.id = i
                            self.name = f"Producto {i}"
                            self.description = None
                            self.price = 0.0
                            self.stock = 0
                            self.seasonal_availability = None
                            self.category_id = 1
                            self.farmer_id = 1

                    return [Product(i) for i in range(1000)]

            return All()

    class MockSession:
        async def execute(self, query):
            return MockResult()

        async def get(self, model, id):
            # Simula categoría/farmer dummy
            class Dummy:
                id = id
                name = "Mock"
                description = None
                email = "mock@example.com"
                phone = None
                location = None
                verified = True

            return Dummy()

    async def _get_db_override():
        yield MockSession()

    app.dependency_overrides[get_db] = _get_db_override
    query = """
    query { searchProducts { id name } }
    """
    start = time.perf_counter()
    response = await client.post("/graphql", json={"query": query})
    elapsed = (time.perf_counter() - start) * 1000  # ms
    assert response.status_code == 200
    data = response.json()["data"]["searchProducts"]
    assert len(data) == 1000
    assert elapsed < 500  # ms
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_product_search_invalid_filter(client: AsyncClient):
    class MockResult:
        def scalars(self):
            class All:
                def all(self):
                    return []

            return All()

    class MockSession:
        async def execute(self, query):
            return MockResult()

        async def get(self, model, id):
            class Dummy:
                id = id
                name = "Mock"
                description = None

            return Dummy()

    async def _get_db_override():
        yield MockSession()

    app.dependency_overrides[get_db] = _get_db_override
    query = """
    query {
      searchProducts(filters: {price: "not_a_number"}) {
        id
        name
      }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert "errors" in response.json()
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_product_query_invalid_field(client: AsyncClient):
    class MockResult:
        def scalars(self):
            class All:
                def all(self):
                    class Product:
                        id = 1
                        name = "Test"
                        description = None
                        price = 0.0
                        stock = 0
                        seasonal_availability = None
                        category_id = 1
                        farmer_id = 1

                    return [Product()]

            return All()

    class MockSession:
        async def execute(self, query):
            return MockResult()

        async def get(self, model, id):
            class Dummy:
                id = id
                name = "Mock"
                description = None

            return Dummy()

    async def _get_db_override():
        yield MockSession()

    app.dependency_overrides[get_db] = _get_db_override
    query = """
    query { searchProducts { id name nonExistentField } }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    body = response.json()
    assert "errors" in body
    app.dependency_overrides.clear()
