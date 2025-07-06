import pytest
from unittest.mock import AsyncMock
from app.services.search_service import (
    search_products_service,
    get_product_category,
    get_farmer,
)
from app.graphql.types.product_type import (
    ProductType,
    ProductCategoryType,
    ProductSearchInput,
)
from app.graphql.types.farmer_type import FarmerType


def make_session_with_products(products):
    class ScalarsMock:
        def all(self):
            return products

    class ResultMock:
        def scalars(self):
            return ScalarsMock()

    session = AsyncMock()
    session.execute.return_value = ResultMock()
    return session


@pytest.mark.asyncio
async def test_search_products_service_no_filters(monkeypatch):
    class Product:
        id = 1
        name = "Tomate"
        description = "desc"
        price = 10
        stock = 5
        seasonal_availability = "Verano"
        category_id = 1
        farmer_id = 1

    session = make_session_with_products([Product()])
    monkeypatch.setattr(
        "app.services.search_service.get_product_category",
        AsyncMock(
            return_value=ProductCategoryType(id=1, name="Verduras", description="desc")
        ),
    )
    monkeypatch.setattr(
        "app.services.search_service.get_farmer",
        AsyncMock(
            return_value=FarmerType(
                id=1,
                name="Juan",
                email="j@x.com",
                phone="123",
                location="Norte",
                verified=True,
            )
        ),
    )
    result = await search_products_service(session)
    assert len(result) == 1
    assert isinstance(result[0], ProductType)


@pytest.mark.asyncio
async def test_search_products_service_with_name_filter(monkeypatch):
    filters = ProductSearchInput(name="Tomate")
    session = make_session_with_products([])
    result = await search_products_service(session, filters)
    assert result == []


@pytest.mark.asyncio
async def test_search_products_service_with_category_filter(monkeypatch):
    filters = ProductSearchInput(category_id=2)
    session = make_session_with_products([])
    result = await search_products_service(session, filters)
    assert result == []


@pytest.mark.asyncio
async def test_search_products_service_with_farmer_filter(monkeypatch):
    filters = ProductSearchInput(farmer_id=3)
    session = make_session_with_products([])
    result = await search_products_service(session, filters)
    assert result == []


@pytest.mark.asyncio
async def test_search_products_service_with_min_max_price(monkeypatch):
    filters = ProductSearchInput(min_price=5, max_price=20)
    session = make_session_with_products([])
    result = await search_products_service(session, filters)
    assert result == []


@pytest.mark.asyncio
async def test_search_products_service_with_available(monkeypatch):
    filters = ProductSearchInput(available=True)
    session = make_session_with_products([])
    result = await search_products_service(session, filters)
    assert result == []
    filters = ProductSearchInput(available=False)
    result = await search_products_service(session, filters)
    assert result == []


@pytest.mark.asyncio
async def test_search_products_service_with_seasonal(monkeypatch):
    filters = ProductSearchInput(seasonal="Verano")
    session = make_session_with_products([])
    result = await search_products_service(session, filters)
    assert result == []


@pytest.mark.asyncio
async def test_search_products_service_no_products(monkeypatch):
    session = make_session_with_products([])
    result = await search_products_service(session)
    assert result == []


@pytest.mark.asyncio
async def test_search_products_service_product_with_missing_category_farmer(
    monkeypatch,
):
    class Product:
        id = 1
        name = "Tomate"
        description = "desc"
        price = 10
        stock = 5
        seasonal_availability = "Verano"
        category_id = 1
        farmer_id = 1

    session = make_session_with_products([Product()])
    monkeypatch.setattr(
        "app.services.search_service.get_product_category", AsyncMock(return_value=None)
    )
    monkeypatch.setattr(
        "app.services.search_service.get_farmer", AsyncMock(return_value=None)
    )
    with pytest.raises(ValueError) as exc:
        await search_products_service(session)
    assert "Category with id 1 not found" in str(exc.value)


@pytest.mark.asyncio
async def test_get_product_category_exists(monkeypatch):
    class Cat:
        id = 1
        name = "Verduras"
        description = "desc"

    session = AsyncMock()
    session.get.return_value = Cat()
    result = await get_product_category(session, 1)
    assert isinstance(result, ProductCategoryType)
    assert result.name == "Verduras"


@pytest.mark.asyncio
async def test_get_product_category_not_exists(monkeypatch):
    session = AsyncMock()
    session.get.return_value = None
    result = await get_product_category(session, 1)
    assert result is None


@pytest.mark.asyncio
async def test_get_farmer_exists(monkeypatch):
    class Farmer:
        id = 1
        name = "Juan"
        email = "j@x.com"
        phone = "123"
        location = "Norte"
        verified = True

    session = AsyncMock()
    session.get.return_value = Farmer()
    result = await get_farmer(session, 1)
    assert isinstance(result, FarmerType)
    assert result.name == "Juan"


@pytest.mark.asyncio
async def test_get_farmer_not_exists(monkeypatch):
    session = AsyncMock()
    session.get.return_value = None
    result = await get_farmer(session, 1)
    assert result is None
