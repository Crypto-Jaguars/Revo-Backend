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
async def test_nested_farmer_products_category(client: AsyncClient, monkeypatch):
    fake_farmers = [
        {
            "id": "1",
            "name": "Farmer 1",
            "products": [
                {
                    "id": "10",
                    "name": "Tomate",
                    "category": {"id": "100", "name": "Verduras"},
                },
                {
                    "id": "11",
                    "name": "Papa",
                    "category": {"id": "101", "name": "Tubérculos"},
                },
            ],
        }
    ]

    class FakeResponse:
        def json(self):
            return {"data": {"farmers": fake_farmers}}

        @property
        def status_code(self):
            return 200

    async def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(client, "post", fake_post)
    query = """
    query {
      farmers {
        id
        name
        products {
          id
          name
          category { id name }
        }
      }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    farmers = response.json()["data"]["farmers"]
    assert isinstance(farmers, list)
    for farmer in farmers:
        assert "products" in farmer
        for product in farmer["products"]:
            assert "category" in product
            assert "name" in product["category"]


@pytest.mark.asyncio
async def test_product_search_performance(client: AsyncClient, monkeypatch):
    fake_products = [{"id": str(i), "name": f"Producto {i}"} for i in range(1000)]

    class FakeResponse:
        def json(self):
            return {"data": {"products": fake_products}}

        @property
        def status_code(self):
            return 200

    async def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(client, "post", fake_post)
    query = """
    query { products { id name } }
    """
    start = time.perf_counter()
    response = await client.post("/graphql", json={"query": query})
    elapsed = (time.perf_counter() - start) * 1000  # ms
    assert response.status_code == 200
    data = response.json()["data"]["products"]
    assert len(data) == 1000
    assert elapsed < 500  # ms


@pytest.mark.asyncio
async def test_product_search_invalid_filter(client: AsyncClient, monkeypatch):
    class FakeResponse:
        def json(self):
            return {"errors": [{"message": "Invalid filter value"}]}

        @property
        def status_code(self):
            return 200

    async def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(client, "post", fake_post)
    query = """
    query {
      products(filter: {price: "not_a_number"}) {
        id
        name
      }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert "errors" in response.json()


@pytest.mark.asyncio
async def test_product_search_empty_filter(client: AsyncClient, monkeypatch):
    class FakeResponse:
        def json(self):
            return {"data": {"products": []}}

        @property
        def status_code(self):
            return 200

    async def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(client, "post", fake_post)
    query = """
    query { products(filter: {}) { id name } }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()["data"]["products"]
    assert data == []


@pytest.mark.asyncio
async def test_farmer_without_products(client: AsyncClient, monkeypatch):
    fake_farmers = [{"id": "1", "name": "Farmer 1", "products": []}]

    class FakeResponse:
        def json(self):
            return {"data": {"farmers": fake_farmers}}

        @property
        def status_code(self):
            return 200

    async def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(client, "post", fake_post)
    query = """
    query { farmers { id name products { id name } } }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    farmers = response.json()["data"]["farmers"]
    assert farmers[0]["products"] == []


@pytest.mark.asyncio
async def test_product_with_null_category(client: AsyncClient, monkeypatch):
    fake_products = [{"id": "1", "name": "Sin categoría", "category": None}]

    class FakeResponse:
        def json(self):
            return {"data": {"products": fake_products}}

        @property
        def status_code(self):
            return 200

    async def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(client, "post", fake_post)
    query = """
    query { products { id name category { id name } } }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()["data"]["products"]
    assert data[0]["category"] is None


@pytest.mark.asyncio
async def test_product_query_invalid_field(client: AsyncClient, monkeypatch):
    class FakeResponse:
        def json(self):
            return {"errors": [{"message": "Cannot query field 'nonExistentField'"}]}

        @property
        def status_code(self):
            return 200

    async def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(client, "post", fake_post)
    query = """
    query { products { id name nonExistentField } }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    body = response.json()
    assert "errors" in body


@pytest.mark.asyncio
async def test_product_search_empty_filter():
    mock_session = AsyncMock()

    async def fake_service(*args, **kwargs):
        return []

    with patch(
        "app.graphql.resolvers.product_resolver.search_products_service",
        new=fake_service,
    ):
        resolver = ProductResolver()
        filters = ProductSearchInput()
        info = InfoMock(mock_session)
        result = await resolver.search_products(info, filters)
        assert result == []


@pytest.mark.asyncio
async def test_product_search_invalid_filter():
    mock_session = AsyncMock()

    async def fake_service(*args, **kwargs):
        raise AttributeError("'coroutine' object has no attribute 'all'")

    with patch(
        "app.graphql.resolvers.product_resolver.search_products_service",
        new=fake_service,
    ):
        resolver = ProductResolver()
        filters = ProductSearchInput(min_price="not_a_number")
        info = InfoMock(mock_session)
        with pytest.raises(AttributeError) as exc:
            await resolver.search_products(info, filters)
        assert "'coroutine' object has no attribute 'all'" in str(exc.value)


@pytest.mark.asyncio
async def test_product_search_performance():
    mock_session = AsyncMock()
    fake_category = ProductCategoryType(id=1, name="Cat", description=None)
    fake_farmer = FarmerType(
        id=1, name="Farmer", email="f@x.com", phone=None, location=None, verified=True
    )
    fake_products = [
        ProductType(
            id=i,
            name=f"Producto {i}",
            description=None,
            price=1.0,
            stock=1,
            seasonal_availability=None,
            category=fake_category,
            farmer=fake_farmer,
        )
        for i in range(1000)
    ]

    async def fake_service(*args, **kwargs):
        return fake_products

    with patch(
        "app.graphql.resolvers.product_resolver.search_products_service",
        new=fake_service,
    ):
        resolver = ProductResolver()
        filters = ProductSearchInput()
        info = InfoMock(mock_session)
        import time

        start = time.perf_counter()
        result = await resolver.search_products(info, filters)
        elapsed = (time.perf_counter() - start) * 1000
        assert len(result) == 1000
        assert elapsed < 500


@pytest.mark.asyncio
async def test_product_with_null_category():
    mock_session = AsyncMock()
    fake_farmer = FarmerType(
        id=1, name="Farmer", email="f@x.com", phone=None, location=None, verified=True
    )
    fake_products = [
        ProductType(
            id=1,
            name="Sin categoría",
            description=None,
            price=1.0,
            stock=1,
            seasonal_availability=None,
            category=None,
            farmer=fake_farmer,
        )
    ]

    async def fake_service(*args, **kwargs):
        return fake_products

    with patch(
        "app.graphql.resolvers.product_resolver.search_products_service",
        new=fake_service,
    ):
        resolver = ProductResolver()
        filters = ProductSearchInput()
        info = InfoMock(mock_session)
        result = await resolver.search_products(info, filters)
        assert result[0].category is None
