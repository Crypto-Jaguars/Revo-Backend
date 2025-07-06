import pytest
from unittest.mock import AsyncMock
from app.graphql.resolvers.product_resolver import (
    ProductResolver,
)
from app.graphql.types.product_type import ProductCategoryType
from app.graphql.types.farmer_type import FarmerType
from app.services.helpers import get_product_category, get_farmer


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
async def test_product_categories_empty(monkeypatch):
    session = make_session_with_items([])
    info = InfoMock(session)
    pq = ProductResolver()
    result = await pq.product_categories(info)
    assert result == []


@pytest.mark.asyncio
async def test_product_categories_with_data(monkeypatch):
    class Cat:
        def __init__(self, id, name, description):
            self.id = id
            self.name = name
            self.description = description

    cats = [Cat(1, "Verduras", "desc1"), Cat(2, "Frutas", "desc2")]
    session = make_session_with_items(cats)
    info = InfoMock(session)
    pq = ProductResolver()
    result = await pq.product_categories(info)
    assert len(result) == 2
    assert isinstance(result[0], ProductCategoryType)


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
async def test_product_categories_none(monkeypatch):
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
    result = await pq.product_categories(info)
    assert result == []
