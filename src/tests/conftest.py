"""
Sets up the test modules and configuration
"""
import pytest

# Starlette test client
from fastapi.testclient import TestClient

# Fetch App
from app.main import app
from app.db import metadata, engine

@pytest.fixture(scope="module")
def test_app():
    # WARNING! This should not be used in production environment. 
    # In case of real world application use a separate database (even full separate enviroment) for testing
    metadata.drop_all(engine)
    metadata.create_all(engine)

    with TestClient(app) as client:
        yield client  # testing happens here