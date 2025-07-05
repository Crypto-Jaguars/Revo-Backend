import pytest
from unittest.mock import AsyncMock
from app.graphql.resolvers.product_resolver import (
    ProductResolver,
    get_product_category,
    get_farmer,
)
from app.graphql.types.product_type import ProductCategoryType
from app.graphql.types.farmer_type import FarmerType


class InfoMock:
    def __init__(self, db):
        self.context = {"db": db}


def make_session_with_items(items):
    class ScalarsMock:
        def all(self):
            return items

    class ResultMock:
        def scalars(self):
            return ScalarsMock()

    session = AsyncMock()
    session.execute.return_value = ResultMock()
    return session


@pytest.mark.asyncio
async def test_products_by_category_empty(monkeypatch):
    session = make_session_with_items([])
    info = InfoMock(session)
    pq = ProductResolver()
    result = await pq.products_by_category(info)
    assert result == []


@pytest.mark.asyncio
async def test_products_by_category_with_data(monkeypatch):
    class Cat:
        def __init__(self, id, name, description):
            self.id = id
            self.name = name
            self.description = description

    cats = [Cat(1, "Verduras", "desc1"), Cat(2, "Frutas", "desc2")]
    session = make_session_with_items(cats)
    info = InfoMock(session)
    pq = ProductResolver()
    result = await pq.products_by_category(info)
    assert len(result) == 2
    assert isinstance(result[0], ProductCategoryType)


@pytest.mark.asyncio
async def test_farmers_by_region_empty(monkeypatch):
    session = make_session_with_items([])
    info = InfoMock(session)
    pq = ProductResolver()
    result = await pq.farmers_by_region(info, region="Norte")
    assert result == []


@pytest.mark.asyncio
async def test_farmers_by_region_with_data(monkeypatch):
    class Farmer:
        def __init__(self, id, name, email, phone, location, verified):
            self.id = id
            self.name = name
            self.email = email
            self.phone = phone
            self.location = location
            self.verified = verified

    farmers = [Farmer(1, "Juan", "j@x.com", "123", "Norte", True)]
    session = make_session_with_items(farmers)
    info = InfoMock(session)
    pq = ProductResolver()
    result = await pq.farmers_by_region(info, region="Norte")
    assert len(result) == 1
    assert isinstance(result[0], FarmerType)


@pytest.mark.asyncio
async def test_farmers_by_region_none(monkeypatch):
    class ScalarsMock:
        def all(self):
            return None

    class ResultMock:
        def scalars(self):
            return ScalarsMock()

    session = AsyncMock()
    session.execute.return_value = ResultMock()
    info = InfoMock(session)
    pq = ProductResolver()
    result = await pq.farmers_by_region(info, region="Norte")
    assert result == []


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


@pytest.mark.asyncio
async def test_products_by_category_none(monkeypatch):
    class ScalarsMock:
        def all(self):
            return None

    class ResultMock:
        def scalars(self):
            return ScalarsMock()

    session = AsyncMock()
    session.execute.return_value = ResultMock()
    info = InfoMock(session)
    pq = ProductResolver()
    result = await pq.products_by_category(info)
    assert result == []
