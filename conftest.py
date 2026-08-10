import pytest
from sqlmodel import SQLModel
from database.session import engine

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)
