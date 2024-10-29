from contextlib import asynccontextmanager
import datetime
import pytest
from fastapi.testclient import TestClient
from app.main import app, get_session
from sqlmodel import Session, create_engine, SQLModel

from app.dbmodels import Product

# Create an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)


def session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = session


@pytest.fixture(scope="module")
def client():
    app.router.lifespan_context = lifespan

    with TestClient(app) as test_client:
        yield test_client
    SQLModel.metadata.drop_all(engine)


@asynccontextmanager
async def lifespan(app):
    SQLModel.metadata.create_all(engine)
    s = Session(engine)
    test_product = Product(
        web_id="P-001",
        name="ProductA Name",
        brand="Brand",
        image_url="http://example.com/image.jpg",
        description="Test description",
        price=1000.55,
        supermarket="carrefour",
        last_updated=datetime.datetime.now(),
    )
    test_product = Product(
        web_id="P-002",
        name="ProductB Name",
        brand="Brand",
        image_url="http://example.com/image.jpg",
        description="Test description",
        price=1000.55,
        supermarket="carrefour",
        last_updated=datetime.datetime.now(),
    )

    s.add(test_product)
    s.commit()
    yield
    SQLModel.metadata.drop_all(engine)
