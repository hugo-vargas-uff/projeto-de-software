import pytest

from airline.adapters.orm import Base
from airline.entrypoints.flask_app import app, engine, SessionFactory

@pytest.fixture
def client():
    #limpa antes de cada teste
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    app.config["TESTING"] = True
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def session_factory():
    return SessionFactory
