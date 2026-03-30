import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import Base, engine

os.environ["ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis(mocker):
    mocker.patch("app.api.routes.redis_client.get", return_value=None)
    mocker.patch("app.api.routes.redis_client.set", return_value=True)